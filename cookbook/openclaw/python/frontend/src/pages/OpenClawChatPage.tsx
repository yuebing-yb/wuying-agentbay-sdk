/**
 * OpenClaw 对话 - 独立页面
 * 通过 URL 参数 sessionId 连接并实现与 OpenClaw 的对话功能
 */

import { useState, useEffect, useRef, useCallback } from 'react'
import { Link, useSearchParams } from 'react-router-dom'

/** Build proxy WebSocket URL */
function buildProxyWssUrl(sessionId: string): string {
  const proto = window.location.protocol === 'https:' ? 'wss:' : 'ws:'
  return `${proto}//${window.location.host}/api/sessions/${sessionId}/openclaw-wss`
}

interface ChatMessage {
  id: string
  role: 'user' | 'assistant'
  content: string
  timestamp: Date
  streaming?: boolean
}

function OpenClawChatPage() {
  const [searchParams] = useSearchParams()
  const sessionIdFromUrl = searchParams.get('sessionId') || ''
  const [sessionId, setSessionId] = useState(sessionIdFromUrl)
  const [error, setError] = useState<string | null>(null)
  const [connected, setConnected] = useState(false)
  const [messages, setMessages] = useState<ChatMessage[]>([])
  const [inputText, setInputText] = useState('')
  const [sending, setSending] = useState(false)
  const wsRef = useRef<WebSocket | null>(null)
  const msgIdRef = useRef(0)
  const fallbackTimerRef = useRef<ReturnType<typeof setTimeout> | null>(null)

  const wssUrl = sessionId ? buildProxyWssUrl(sessionId) : ''

  useEffect(() => {
    if (sessionIdFromUrl) setSessionId(sessionIdFromUrl)
  }, [sessionIdFromUrl])

  const clearFallbackTimer = useCallback(() => {
    if (fallbackTimerRef.current) {
      clearTimeout(fallbackTimerRef.current)
      fallbackTimerRef.current = null
    }
  }, [])

  const handleGatewayMessage = useCallback((msg: Record<string, unknown>) => {
    const type = msg.type as string

    if (type === 'error') {
      const m = msg.message
      const errStr = typeof m === 'string' ? m : (m && typeof m === 'object' && 'message' in m ? String((m as { message?: unknown }).message) : '连接失败')
      // Ignore "unknown method: sessions.messages.subscribe" - may come from Control UI or older Gateway
      if (errStr.includes('sessions.messages.subscribe')) return
      setError(errStr)
      return
    }

    if (type === 'event' && msg.event === 'connect.challenge') {
      setError('Gateway 需要设备认证。请确认 WSS 链接已正确附加 token')
      return
    }

    if (type === 'event' && msg.event === 'session.message') {
      clearFallbackTimer()
      const payload = msg.payload as { messages?: Array<{ role?: string; text?: string; content?: string }> } | undefined
      const messages = payload?.messages
      if (Array.isArray(messages)) {
        for (const m of messages) {
          if (m?.role === 'assistant') {
            const text = m.text ?? m.content ?? ''
            if (text) {
              setMessages((prev) => {
                const last = prev[prev.length - 1]
                if (last?.role === 'assistant' && last.streaming) {
                  return [...prev.slice(0, -1), { ...last, content: last.content + text, streaming: false }]
                }
                return [...prev, { id: `a-${Date.now()}`, role: 'assistant', content: text, timestamp: new Date() }]
              })
            }
          }
        }
      }
      return
    }

    if (type === 'response') {
      clearFallbackTimer()
      const payload = msg.payload as { text?: string } | undefined
      const text = payload?.text ?? ''
      setMessages((prev) => {
        const last = prev[prev.length - 1]
        if (last?.role === 'assistant' && last.streaming) {
          return [...prev.slice(0, -1), { ...last, content: text, streaming: false }]
        }
        return [...prev, { id: `a-${Date.now()}`, role: 'assistant', content: text, timestamp: new Date() }]
      })
      return
    }

    const chatDelta = type === 'chat.delta' || (type === 'event' && msg.event === 'chat.delta')
    if (chatDelta) {
      clearFallbackTimer()
      const data = (msg.data ?? msg.payload) as { delta?: string } | undefined
      const delta = data?.delta ?? ''
      setMessages((prev) => {
        const last = prev[prev.length - 1]
        if (last?.role === 'assistant' && last.streaming) {
          return [...prev.slice(0, -1), { ...last, content: last.content + delta }]
        }
        return [...prev, { id: `a-${Date.now()}`, role: 'assistant', content: delta, timestamp: new Date(), streaming: true }]
      })
      return
    }

    const chatDone = type === 'chat.done' || (type === 'event' && msg.event === 'chat.done')
    if (chatDone) {
      clearFallbackTimer()
      setMessages((prev) => {
        const last = prev[prev.length - 1]
        if (last?.role === 'assistant' && last.streaming) {
          return [...prev.slice(0, -1), { ...last, streaming: false }]
        }
        return prev
      })
      return
    }

    if (type === 'res') {
      const payload = msg.payload as Record<string, unknown> | undefined
      const errRaw = msg.error
      if (errRaw) {
        const errStr = typeof errRaw === 'string' ? errRaw : (errRaw && typeof errRaw === 'object' && 'message' in errRaw ? String((errRaw as { message?: unknown }).message) : JSON.stringify(errRaw))
        // Ignore "unknown method: sessions.messages.subscribe" - may come from Control UI or older Gateway
        if (errStr.includes('sessions.messages.subscribe')) return
        setError(errStr)
        return
      }
      if (payload?.type === 'chat.done' || payload?.text || payload?.delta) {
        clearFallbackTimer()
        const text = (payload.text as string) ?? (payload.delta as string) ?? ''
        if (text) {
          setMessages((prev) => {
            const last = prev[prev.length - 1]
            if (last?.role === 'assistant' && last.streaming) {
              return [...prev.slice(0, -1), { ...last, content: last.content + text, streaming: false }]
            }
            return [...prev, { id: `a-${Date.now()}`, role: 'assistant', content: text, timestamp: new Date() }]
          })
        }
      }
    }
  }, [clearFallbackTimer])

  const connect = useCallback(() => {
    if (!wssUrl || wsRef.current?.readyState === WebSocket.OPEN) return
    setError(null)
    try {
      const ws = new WebSocket(wssUrl)
      wsRef.current = ws

      ws.onopen = () => {
        setConnected(true)
        setError(null)
      }

      ws.onmessage = (event) => {
        try {
          const msg = JSON.parse(event.data)
          handleGatewayMessage(msg)
        } catch {
          // Ignore non-JSON
        }
      }

      ws.onclose = (ev) => {
        setConnected(false)
        wsRef.current = null
        if (ev.code === 4004) {
          setError('会话不存在或 WSS 链接不可用')
        } else if (ev.code !== 1000 && !ev.wasClean) {
          setError(ev.reason || 'WebSocket 连接已关闭')
        }
      }

      ws.onerror = () => {
        setError('WebSocket 连接错误，请检查网络或会话状态')
      }
    } catch (e) {
      setError(e instanceof Error ? e.message : '连接失败')
    }
  }, [wssUrl, handleGatewayMessage])

  const sendMessage = useCallback(async () => {
    const text = inputText.trim()
    if (!text || sending) return
    if (!sessionId) {
      setError('请先输入会话 ID')
      return
    }

    setSending(true)
    setInputText('')
    const msgId = `msg-${++msgIdRef.current}`

    setMessages((prev) => [...prev, { id: msgId, role: 'user', content: text, timestamp: new Date() }])

    const addAssistantReply = (content: string) => {
      setMessages((prev) => [...prev, { id: `a-${Date.now()}`, role: 'assistant', content, timestamp: new Date() }])
    }

    try {
      // 1. Try WebSocket chat.send if connected
      if (wsRef.current?.readyState === WebSocket.OPEN) {
        wsRef.current.send(JSON.stringify({
          type: 'req',
          id: msgId,
          method: 'chat.send',
          params: { sessionKey: 'main', message: text, idempotencyKey: msgId },
        }))
        // 2. HTTP fallback: if no assistant reply in 20s, call HTTP API (older Gateway may not send chat.delta)
        if (fallbackTimerRef.current) clearTimeout(fallbackTimerRef.current)
        fallbackTimerRef.current = setTimeout(async () => {
          fallbackTimerRef.current = null
          const hasReply = document.querySelector('.chat-msg-assistant .chat-content')
          if (hasReply) return
          try {
            const res = await fetch(`/api/sessions/${sessionId}/openclaw-chat`, {
              method: 'POST',
              headers: { 'Content-Type': 'application/json' },
              body: JSON.stringify({ message: text }),
            })
            const data = await res.json()
            if (res.ok && data?.response) {
              addAssistantReply(data.response)
            }
          } catch {
            // ignore
          }
        }, 20000)
      } else {
        // 3. Not connected: use HTTP directly
        const res = await fetch(`/api/sessions/${sessionId}/openclaw-chat`, {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ message: text }),
        })
        const data = await res.json()
        if (!res.ok) {
          throw new Error(data.detail || '发送失败')
        }
        if (data?.response) {
          addAssistantReply(data.response)
        }
      }
    } catch (e) {
      setError(e instanceof Error ? e.message : '发送失败')
      setMessages((prev) => prev.slice(0, -1))
      setInputText(text)
    } finally {
      setSending(false)
    }
  }, [inputText, sending, sessionId])

  const disconnect = useCallback(() => {
    if (wsRef.current) {
      wsRef.current.close()
      wsRef.current = null
    }
    setConnected(false)
  }, [])

  useEffect(() => {
    return () => disconnect()
  }, [disconnect])

  const handleSessionIdSubmit = (e: React.FormEvent) => {
    e.preventDefault()
    const form = e.target as HTMLFormElement
    const input = form.querySelector('input[name="sessionId"]') as HTMLInputElement
    if (input?.value?.trim()) {
      setSessionId(input.value.trim())
      setError(null)
    }
  }

  return (
    <div className="openclaw-chat-page">
      <header className="chat-page-header">
        <Link to="/" className="back-link">← 返回管理页</Link>
        <h1>OpenClaw 对话</h1>
        <p className="chat-page-subtitle">与 OpenClaw 进行对话</p>
      </header>

      <main className="chat-page-main">
        {!sessionId ? (
          <div className="card chat-session-form">
            <h2>输入会话 ID</h2>
            <p className="hint">请从管理页创建会话后，将 sessionId 填入下方，或直接访问 /chat?sessionId=xxx</p>
            <form onSubmit={handleSessionIdSubmit}>
              <input
                type="text"
                name="sessionId"
                placeholder="例如: s-04owxw8oxc0icdcfw"
                className="chat-input"
                autoFocus
              />
              <button type="submit" className="btn btn-primary">进入对话</button>
            </form>
          </div>
        ) : (
          <div className="chat-page-content">
            <div className="chat-session-bar">
              <span className="session-id-label">会话 ID: {sessionId}</span>
              {!connected ? (
                <button type="button" className="btn btn-primary" onClick={connect} data-testid="openclaw-connect-btn">
                  连接 OpenClaw
                </button>
              ) : (
                <button type="button" className="btn btn-outline btn-sm" onClick={disconnect}>
                  断开连接
                </button>
              )}
            </div>

            <div className="chat-messages chat-messages-full">
              {messages.map((m) => (
                <div key={m.id} className={`chat-msg chat-msg-${m.role}`}>
                  <span className="chat-role">{m.role === 'user' ? '我' : 'OpenClaw'}</span>
                  <div className="chat-content">
                    {m.content || (m.streaming ? '...' : '')}
                  </div>
                </div>
              ))}
            </div>

            <div className="chat-input-row chat-input-row-full">
              <input
                type="text"
                className="chat-input"
                placeholder="输入消息..."
                data-testid="openclaw-chat-input"
                value={inputText}
                onChange={(e) => setInputText(e.target.value)}
                onKeyDown={(e) => e.key === 'Enter' && !e.shiftKey && sendMessage()}
                disabled={sending}
              />
              <button
                type="button"
                className="btn btn-primary"
                onClick={sendMessage}
                disabled={sending || !inputText.trim()}
                data-testid="openclaw-send-btn"
              >
                {sending ? '发送中...' : '发送'}
              </button>
            </div>

            {error && <p className="error-text">{error}</p>}
          </div>
        )}
      </main>
    </div>
  )
}

export default OpenClawChatPage
