/**
 * OpenClaw Chat Panel - Connect to OpenClaw Gateway via get_link WSS proxy.
 * Implements chat/dialogue with OpenClaw using the proxied WebSocket connection.
 */

import { useState, useEffect, useRef, useCallback } from 'react'

interface OpenClawChatPanelProps {
  sessionId: string
}

/** Build proxy WebSocket URL (same origin, avoids cross-origin connection errors) */
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

function OpenClawChatPanel({ sessionId }: OpenClawChatPanelProps) {
  const wssUrl = buildProxyWssUrl(sessionId)
  const [error, setError] = useState<string | null>(null)
  const [connected, setConnected] = useState(false)
  const [messages, setMessages] = useState<ChatMessage[]>([])
  const [inputText, setInputText] = useState('')
  const [sending, setSending] = useState(false)
  const wsRef = useRef<WebSocket | null>(null)
  const msgIdRef = useRef(0)
  const pendingResolveRef = useRef<((text: string) => void) | null>(null)

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
          // Ignore non-JSON messages
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
  }, [wssUrl])

  const handleGatewayMessage = useCallback((msg: Record<string, unknown>) => {
    const type = msg.type as string

    // Proxy error from backend
    if (type === 'error') {
      const msgText = (msg.message as string) || '连接失败'
      setError(msgText)
      return
    }

    // Protocol v3: connect.challenge - proxy should handle this; if client sees it, proxy may have failed
    if (type === 'event' && msg.event === 'connect.challenge') {
      setError('Gateway 需要设备认证。请确认 WSS 链接已正确附加 token（与「打开 OpenClaw UI」一致）')
      return
    }

    // clawdocs format: type "response"
    if (type === 'response') {
      const payload = msg.payload as { text?: string } | undefined
      const text = payload?.text ?? ''
      setMessages((prev) => {
        const last = prev[prev.length - 1]
        if (last?.role === 'assistant' && last.streaming) {
          return [...prev.slice(0, -1), { ...last, content: text, streaming: false }]
        }
        return [...prev, { id: `a-${Date.now()}`, role: 'assistant', content: text, timestamp: new Date() }]
      })
      pendingResolveRef.current?.(text)
      pendingResolveRef.current = null
      return
    }

    // opencodedocs format: chat.delta (streaming)
    if (type === 'chat.delta') {
      const data = msg.data as { delta?: string } | undefined
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

    // opencodedocs format: chat.done
    if (type === 'chat.done') {
      setMessages((prev) => {
        const last = prev[prev.length - 1]
        if (last?.role === 'assistant' && last.streaming) {
          return [...prev.slice(0, -1), { ...last, streaming: false }]
        }
        return prev
      })
      return
    }

    // Protocol v3: res (response to req)
    if (type === 'res') {
      const payload = msg.payload as Record<string, unknown> | undefined
      const errRaw = msg.error
      if (errRaw) {
        const errStr = typeof errRaw === 'string' ? errRaw : (errRaw && typeof errRaw === 'object' && 'message' in errRaw ? String((errRaw as { message?: unknown }).message) : JSON.stringify(errRaw))
        setError(errStr)
        return
      }
      // chat.send response might be in payload
      if (payload?.type === 'chat.done' || payload?.text || payload?.delta) {
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
        pendingResolveRef.current?.(text)
        pendingResolveRef.current = null
      }
    }
  }, [])

  const sendMessage = useCallback(async () => {
    const text = inputText.trim()
    if (!text || !wsRef.current || wsRef.current.readyState !== WebSocket.OPEN || sending) return

    setSending(true)
    setInputText('')
    const msgId = `msg-${++msgIdRef.current}`

    setMessages((prev) => [...prev, { id: msgId, role: 'user', content: text, timestamp: new Date() }])

    try {
      // Protocol v3: type=req, method, params (schema: sessionKey, message, idempotencyKey)
      const reqMsg = {
        type: 'req',
        id: msgId,
        method: 'chat.send',
        params: {
          sessionKey: 'main',
          message: text,
          idempotencyKey: msgId,
        },
      }
      wsRef.current.send(JSON.stringify(reqMsg))
    } catch (e) {
      setError(e instanceof Error ? e.message : '发送失败')
      setMessages((prev) => prev.slice(0, -1))
      setInputText(text)
    } finally {
      setSending(false)
    }
  }, [inputText, sending])

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

  return (
    <div className="openclaw-chat-panel">
      <h3>OpenClaw 对话</h3>
      <p className="hint">通过同源 WebSocket 代理连接 OpenClaw Gateway</p>

      {!connected ? (
        <button type="button" className="btn btn-primary" onClick={connect} data-testid="openclaw-connect-btn">
          连接 OpenClaw
        </button>
      ) : (
        <>
          <button type="button" className="btn btn-outline btn-sm" onClick={disconnect}>
            断开连接
          </button>
          <div className="chat-messages">
            {messages.map((m) => (
              <div key={m.id} className={`chat-msg chat-msg-${m.role}`}>
                <span className="chat-role">{m.role === 'user' ? '我' : 'OpenClaw'}</span>
                <div className="chat-content">
                  {m.content || (m.streaming ? '...' : '')}
                </div>
              </div>
            ))}
          </div>
          <div className="chat-input-row">
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
        </>
      )}

      {error && <p className="error-text">{error}</p>}
    </div>
  )
}

export default OpenClawChatPanel
