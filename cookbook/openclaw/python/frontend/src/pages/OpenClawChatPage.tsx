/**
 * OpenClaw 对话 - 独立页面
 * 通过 URL 参数 sessionId 连接并实现与 OpenClaw 的对话功能
 */

import { useState, useEffect, useLayoutEffect, useRef, useCallback } from 'react'
import { Link, useSearchParams } from 'react-router-dom'
import ReactMarkdown from 'react-markdown'

/** Build proxy WebSocket URL */
function buildProxyWssUrl(sessionId: string): string {
  const proto = window.location.protocol === 'https:' ? 'wss:' : 'ws:'
  return `${proto}//${window.location.host}/api/sessions/${sessionId}/openclaw-wss`
}

type AssistantRevealType = 'instant' | 'streaming' | 'typewriter'

interface ChatMessage {
  id: string
  role: 'user' | 'assistant'
  content: string
  timestamp: Date
  streaming?: boolean
  /** 助手气泡展示方式：历史/流式块即时；一次性整段回复用打字机 */
  revealType?: AssistantRevealType
}

/** 助手 Markdown：即时、流式（可选光标）、打字机逐字 */
function AssistantMarkdownBody({
  content,
  revealType,
  onContentLayout,
}: {
  content: string
  revealType: AssistantRevealType
  /** 打字机/流式高度变化时让列表贴底 */
  onContentLayout?: () => void
}) {
  const [typedLen, setTypedLen] = useState(() => (revealType === 'typewriter' ? 0 : content.length))

  useEffect(() => {
    if (revealType !== 'typewriter') {
      setTypedLen(content.length)
      return
    }
    setTypedLen(0)
    if (!content) return
    let cancelled = false
    let i = 0
    const step = 2
    const tickMs = 16
    const id = window.setInterval(() => {
      if (cancelled) return
      i = Math.min(content.length, i + step)
      setTypedLen(i)
      if (i >= content.length) clearInterval(id)
    }, tickMs)
    return () => {
      cancelled = true
      clearInterval(id)
    }
  }, [content, revealType])

  useLayoutEffect(() => {
    if (revealType === 'typewriter') onContentLayout?.()
  }, [typedLen, revealType, onContentLayout])

  if (revealType === 'instant' || revealType === 'streaming') {
    const display =
      content || (revealType === 'streaming' ? '思考中...' : '')
    const showCaret =
      revealType === 'streaming' &&
      !!content &&
      content !== '思考中...'
    return (
      <div className="chat-im-content chat-im-content-markdown">
        <ReactMarkdown>{display}</ReactMarkdown>
        {showCaret ? <span className="chat-im-typewriter-caret" aria-hidden /> : null}
      </div>
    )
  }

  const slice = content.slice(0, typedLen)
  return (
    <div className="chat-im-content chat-im-content-markdown">
      <ReactMarkdown>{slice}</ReactMarkdown>
      {typedLen < content.length ? (
        <span className="chat-im-typewriter-caret" aria-hidden />
      ) : null}
    </div>
  )
}

function OpenClawChatPage() {
  const [searchParams] = useSearchParams()
  const sessionIdFromUrl = searchParams.get('sessionId') || ''
  const [sessionId, setSessionId] = useState(sessionIdFromUrl)
  const [error, setError] = useState<string | null>(null)
  const [connected, setConnected] = useState(false)
  const [loadingHistory, setLoadingHistory] = useState(false)
  const [messages, setMessages] = useState<ChatMessage[]>([])
  const [inputText, setInputText] = useState('')
  const [sending, setSending] = useState(false)
  const wsRef = useRef<WebSocket | null>(null)
  const messagesScrollRef = useRef<HTMLDivElement | null>(null)
  const msgIdRef = useRef(0)
  const fallbackTimerRef = useRef<ReturnType<typeof setTimeout> | null>(null)
  const chatHistoryReqIdRef = useRef<string | null>(null)
  /** 当前等待回复的 send msgId；收到助手回复时置空，用于 HTTP fallback 判断（不能用 DOM，历史消息会误判） */
  const pendingSendMsgIdRef = useRef<string | null>(null)

  const wssUrl = sessionId ? buildProxyWssUrl(sessionId) : ''

  /** Extract text from OpenClaw transcript message content (array of {type,text}, or string, or {text}) */
  function extractTextFromContent(content: unknown): string {
    if (typeof content === 'string') return content
    if (content && typeof content === 'object' && 'text' in content) return String((content as { text?: unknown }).text ?? '')
    if (Array.isArray(content)) {
      return content
        .map((block) => (block && typeof block === 'object' && 'text' in block ? String((block as { text?: unknown }).text ?? '') : ''))
        .join('')
    }
    return ''
  }

  /**
   * Gateway 有时把正文放在 message.content（或数组）、message.text，或拼写错误的 conten；统一抽取。
   */
  function extractAssistantFromMessageObj(msgObj: unknown): string {
    if (!msgObj || typeof msgObj !== 'object') return ''
    const o = msgObj as Record<string, unknown>
    const raw = o.content ?? o.text ?? o.conten ?? o.delta ?? ''
    if (typeof raw === 'string') return raw
    return extractTextFromContent(raw)
  }

  useEffect(() => {
    if (sessionIdFromUrl) setSessionId(sessionIdFromUrl)
  }, [sessionIdFromUrl])

  const scrollMessagesToBottom = useCallback(() => {
    const el = messagesScrollRef.current
    if (!el) return
    el.scrollTop = el.scrollHeight
  }, [])

  useLayoutEffect(() => {
    if (!sessionId) return
    scrollMessagesToBottom()
  }, [sessionId, messages, loadingHistory, scrollMessagesToBottom])

  const clearFallbackTimer = useCallback(() => {
    if (fallbackTimerRef.current) {
      clearTimeout(fallbackTimerRef.current)
      fallbackTimerRef.current = null
    }
  }, [])

  const handleGatewayMessage = useCallback((msg: Record<string, unknown>) => {
    const type = msg.type as string

    if (type === 'error') {
      setLoadingHistory(false)
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
      pendingSendMsgIdRef.current = null
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
                  return [
                    ...prev.slice(0, -1),
                    { ...last, content: last.content + text, streaming: false, revealType: 'instant' },
                  ]
                }
                return [
                  ...prev,
                  {
                    id: `a-${Date.now()}`,
                    role: 'assistant',
                    content: text,
                    timestamp: new Date(),
                    revealType: 'instant',
                  },
                ]
              })
            }
          }
        }
      }
      return
    }

    if (type === 'response') {
      clearFallbackTimer()
      pendingSendMsgIdRef.current = null
      const payload = msg.payload as { text?: string } | undefined
      const text = payload?.text ?? ''
        setMessages((prev) => {
          const last = prev[prev.length - 1]
          if (last?.role === 'assistant' && (last.streaming || last.content === '思考中...')) {
            return [
              ...prev.slice(0, -1),
              { ...last, content: text, streaming: false, revealType: 'typewriter' },
            ]
          }
          return [
            ...prev,
            {
              id: `a-${Date.now()}`,
              role: 'assistant',
              content: text,
              timestamp: new Date(),
              revealType: 'typewriter',
            },
          ]
        })
      return
    }

    // event=chat: OpenClaw Gateway（含 state=delta / final；message 可能为 content 数组或 conten 拼写）
    if (type === 'event' && msg.event === 'chat') {
      const payload = msg.payload ?? msg.data ?? {}
      const data = payload as Record<string, unknown>
      const state = String(data.state ?? '')
      const msgObj = (data.message ?? (payload as { message?: unknown }).message) as Record<string, unknown> | undefined

      const topLine = String(data.text ?? data.delta ?? '').trim()
      const fromMessage = extractAssistantFromMessageObj(msgObj)
      const text = topLine || fromMessage

      if (state === 'delta' && text) {
        setMessages((prev) => {
          const last = prev[prev.length - 1]
          if (last?.role === 'assistant' && (last.streaming || last.content === '思考中...')) {
            const base = last.content === '思考中...' ? '' : last.content
            return [
              ...prev.slice(0, -1),
              { ...last, content: base + text, streaming: true, revealType: 'streaming' },
            ]
          }
          return [
            ...prev,
            {
              id: `a-${Date.now()}`,
              role: 'assistant',
              content: text,
              timestamp: new Date(),
              streaming: true,
              revealType: 'streaming',
            },
          ]
        })
        return
      }

      if (state === 'final' || text) {
        const reply =
          text ||
          extractAssistantFromMessageObj(msgObj) ||
          '我可以帮你执行命令、浏览网页或回答问题。你想做什么？'
        setMessages((prev) => {
          const last = prev[prev.length - 1]
          const canFill =
            last?.role === 'assistant' &&
            (last.content === '思考中...' || last.streaming || last.content === '')
          if (canFill) {
            if (state === 'final') {
              queueMicrotask(() => {
                clearFallbackTimer()
                pendingSendMsgIdRef.current = null
              })
            }
            const useTypewriter =
              last.content === '思考中...' || last.content === ''
            return [
              ...prev.slice(0, -1),
              {
                ...last,
                content: reply,
                streaming: false,
                revealType: useTypewriter ? 'typewriter' : 'instant',
              },
            ]
          }
          return prev
        })
      }
      return
    }

    const chatDelta = type === 'chat.delta' || (type === 'event' && msg.event === 'chat.delta')
    if (chatDelta) {
      clearFallbackTimer()
      pendingSendMsgIdRef.current = null
      const data = (msg.data ?? msg.payload) as { delta?: string } | undefined
      const delta = data?.delta ?? ''
        setMessages((prev) => {
          const last = prev[prev.length - 1]
          if (last?.role === 'assistant' && (last.streaming || last.content === '思考中...')) {
            return [
              ...prev.slice(0, -1),
              {
                ...last,
                content: last.content === '思考中...' ? delta : last.content + delta,
                streaming: true,
                revealType: 'streaming',
              },
            ]
          }
          return [
            ...prev,
            {
              id: `a-${Date.now()}`,
              role: 'assistant',
              content: delta,
              timestamp: new Date(),
              streaming: true,
              revealType: 'streaming',
            },
          ]
        })
      return
    }

    const chatDone = type === 'chat.done' || (type === 'event' && msg.event === 'chat.done')
    if (chatDone) {
      setMessages((prev) => {
        const last = prev[prev.length - 1]
        if (last?.role === 'assistant' && (last.streaming || last.content === '思考中...')) {
          // 绝不能把「思考中...」直接清空为 ''，否则后续 chat.final 无法匹配，界面会只剩空气泡
          if (last.content === '思考中...') return prev
          return [...prev.slice(0, -1), { ...last, streaming: false, revealType: 'instant' }]
        }
        return prev
      })
      return
    }

    if (type === 'res') {
      const payload = msg.payload as Record<string, unknown> | undefined
      const reqId = msg.id as string | undefined
      const errRaw = msg.error
      if (errRaw) {
        setLoadingHistory(false)
        const errStr = typeof errRaw === 'string' ? errRaw : (errRaw && typeof errRaw === 'object' && 'message' in errRaw ? String((errRaw as { message?: unknown }).message) : JSON.stringify(errRaw))
        // Ignore "unknown method: sessions.messages.subscribe" - may come from Control UI or older Gateway
        if (errStr.includes('sessions.messages.subscribe')) return
        setError(errStr)
        return
      }
      // chat.history response: payload.messages = transcript array (OpenClaw native format)
      if (reqId === chatHistoryReqIdRef.current) {
        chatHistoryReqIdRef.current = null
        setLoadingHistory(false)
        if (payload?.messages && Array.isArray(payload.messages)) {
          const transcript = payload.messages as Array<{ role?: string; content?: unknown; text?: string }>
          const loaded: ChatMessage[] = []
          for (let i = 0; i < transcript.length; i++) {
            const m = transcript[i]
            const role = m?.role
            if (role === 'user' || role === 'assistant') {
              const text =
                extractTextFromContent(m?.content) ||
                extractTextFromContent((m as { conten?: unknown }).conten) ||
                (m?.text as string) ||
                ''
              if (text || role === 'user') {
                loaded.push({
                  id: `hist-${i}-${Date.now()}`,
                  role: role as 'user' | 'assistant',
                  content: text,
                  timestamp: new Date(),
                  ...(role === 'assistant' ? { revealType: 'instant' as const } : {}),
                })
              }
            }
          }
          if (loaded.length > 0) setMessages(loaded)
        }
        return
      }
      if (payload?.type === 'chat.done' || payload?.text || payload?.delta) {
        clearFallbackTimer()
        pendingSendMsgIdRef.current = null
        const text = (payload.text as string) ?? (payload.delta as string) ?? ''
        if (text) {
          setMessages((prev) => {
            const last = prev[prev.length - 1]
            if (last?.role === 'assistant' && (last.streaming || last.content === '思考中...')) {
              return [
                ...prev.slice(0, -1),
                { ...last, content: text, streaming: false, revealType: 'typewriter' },
              ]
            }
            return [
              ...prev,
              {
                id: `a-${Date.now()}`,
                role: 'assistant',
                content: text,
                timestamp: new Date(),
                revealType: 'typewriter',
              },
            ]
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
        setLoadingHistory(true)
        // Load chat history from OpenClaw (same as native Control UI)
        const reqId = `chat-history-${Date.now()}`
        chatHistoryReqIdRef.current = reqId
        const historyReq = {
          type: 'req',
          id: reqId,
          method: 'chat.history',
          params: { sessionKey: 'main', limit: 100 },
        }
        console.log('[WSS 发送]', historyReq)
        ws.send(JSON.stringify(historyReq))
        // Fallback: stop loading after 10s if no response
        setTimeout(() => {
          if (chatHistoryReqIdRef.current === reqId) {
            chatHistoryReqIdRef.current = null
            setLoadingHistory(false)
          }
        }, 10000)
      }

      ws.onmessage = (event) => {
        try {
          const msg = JSON.parse(event.data)
          const t = msg.type as string
          const ev = msg.event as string
          if (t === 'res' || t === 'event' || t === 'chat.delta' || ev === 'chat.delta' || ev === 'chat' || ev === 'session.message') {
            const pl = msg.payload ?? msg.data
            const keys = pl && typeof pl === 'object' ? Object.keys(pl as object) : []
            console.log('[WSS 收到]', t, ev || '-', msg.id || '-', keys.length ? keys : '(无payload)')
          }
          handleGatewayMessage(msg)
        } catch {
          // Ignore non-JSON
        }
      }

      ws.onclose = (ev) => {
        setConnected(false)
        setLoadingHistory(false)
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

    // Immediately show user message and assistant loading state for better UX (as per phase 7 requirement)
    setMessages((prev) => [
      ...prev,
      { id: msgId, role: 'user', content: text, timestamp: new Date() },
      {
        id: `loading-${Date.now()}`,
        role: 'assistant',
        content: '思考中...',
        timestamp: new Date(),
        streaming: true,
        revealType: 'streaming',
      },
    ])

    try {
      // 1. Try WebSocket chat.send if connected
      if (wsRef.current?.readyState === WebSocket.OPEN) {
        const sendReq = {
          type: 'req',
          id: msgId,
          method: 'chat.send',
          params: { sessionKey: 'main', message: text, idempotencyKey: msgId },
        }
        console.log('[WSS 发送]', sendReq)
        wsRef.current.send(JSON.stringify(sendReq))
        pendingSendMsgIdRef.current = msgId
        // 2. HTTP fallback: if no assistant reply in 20s, call HTTP API (older Gateway may not send chat.delta)
        if (fallbackTimerRef.current) clearTimeout(fallbackTimerRef.current)
        fallbackTimerRef.current = setTimeout(async () => {
          fallbackTimerRef.current = null
          // 用 ref 判断是否已收到本次发送的回复，不能用 DOM（历史消息会误判为已有回复）
          if (pendingSendMsgIdRef.current !== msgId) return
          pendingSendMsgIdRef.current = null
          try {
            const res = await fetch(`/api/sessions/${sessionId}/openclaw-chat`, {
              method: 'POST',
              headers: { 'Content-Type': 'application/json' },
              body: JSON.stringify({ message: text }),
            })
            const data = await res.json()
            if (res.ok && data?.response) {
              // Replace loading state with real response
              setMessages((prev) => {
                const lastIdx = prev.length - 1
                if (lastIdx >= 0 && prev[lastIdx].role === 'assistant' && prev[lastIdx].content === '思考中...') {
                  return [
                    ...prev.slice(0, -1),
                    {
                      id: `a-${Date.now()}`,
                      role: 'assistant',
                      content: data.response,
                      timestamp: new Date(),
                      revealType: 'typewriter',
                    },
                  ]
                }
                return [
                  ...prev,
                  {
                    id: `a-${Date.now()}`,
                    role: 'assistant',
                    content: data.response,
                    timestamp: new Date(),
                    revealType: 'typewriter',
                  },
                ]
              })
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
        // Replace loading state with real response (CLI fallback or HTTP)
        setMessages((prev) => {
          const lastIdx = prev.length - 1
          if (lastIdx >= 0 && prev[lastIdx].role === 'assistant' && prev[lastIdx].content === '思考中...') {
            return [
              ...prev.slice(0, -1),
              {
                id: `a-${Date.now()}`,
                role: 'assistant',
                content: data.response,
                timestamp: new Date(),
                revealType: 'typewriter',
              },
            ]
          }
          return [
            ...prev,
            {
              id: `a-${Date.now()}`,
              role: 'assistant',
              content: data.response,
              timestamp: new Date(),
              revealType: 'typewriter',
            },
          ]
        })
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

  const formatTime = (d: Date) => {
    return d.toLocaleTimeString('zh-CN', { hour: '2-digit', minute: '2-digit' })
  }

  return (
    <div className="openclaw-chat-page openclaw-chat-im">
      {!sessionId ? (
        <>
          <header className="chat-im-header">
            <Link to="/" className="back-link">← 返回管理页</Link>
            <h1>OpenClaw 对话</h1>
          </header>
          <main className="chat-im-main chat-im-session-form">
            <div className="chat-im-welcome-card">
              <div className="chat-im-welcome-icon">💬</div>
              <h2>输入会话 ID</h2>
              <p className="chat-im-hint">请从管理页创建会话后，将 sessionId 填入下方，或直接访问 /chat?sessionId=xxx</p>
              <form onSubmit={handleSessionIdSubmit} className="chat-im-session-form-inner">
                <input
                  type="text"
                  name="sessionId"
                  placeholder="例如: s-04owxw8oxc0icdcfw"
                  className="chat-im-input"
                  autoFocus
                />
                <button type="submit" className="btn btn-primary chat-im-submit">进入对话</button>
              </form>
            </div>
          </main>
        </>
      ) : (
        <>
          <header className="chat-im-header chat-im-header-bar">
            <Link to="/" className="chat-im-back">← 返回</Link>
            <div className="chat-im-header-center">
              <h1>OpenClaw</h1>
              <div className="chat-im-status">
                <span className={`chat-im-status-dot ${connected ? 'connected' : ''}`} />
                <span className="chat-im-status-text">{connected ? '已连接' : '未连接'}</span>
              </div>
            </div>
            <div className="chat-im-header-actions">
              {!connected ? (
                <button type="button" className="btn btn-primary chat-im-connect-btn" onClick={connect} data-testid="openclaw-connect-btn">
                  连接 OpenClaw
                </button>
              ) : (
                <button type="button" className="btn btn-outline chat-im-disconnect-btn" onClick={disconnect}>
                  断开
                </button>
              )}
            </div>
          </header>

          <main className="chat-im-main chat-im-conversation">
            <div className="chat-im-messages" ref={messagesScrollRef}>
              {loadingHistory && (
                <div className="chat-im-loading">
                  <span className="chat-im-loading-spinner" />
                  <p className="chat-im-loading-text">加载对话历史...</p>
                </div>
              )}
              {!loadingHistory && messages.length === 0 && (
                <div className="chat-im-empty">
                  <div className="chat-im-empty-icon">🤖</div>
                  <p className="chat-im-empty-title">开始与 OpenClaw 对话</p>
                  <p className="chat-im-empty-hint">输入消息后按 Enter 发送，Shift+Enter 换行</p>
                  <p className="chat-im-empty-session">会话: {sessionId}</p>
                </div>
              )}
              {messages.map((m) => (
                <div key={m.id} className={`chat-im-bubble chat-im-bubble-${m.role}`}>
                  <div className="chat-im-bubble-inner">
                    {m.role === 'assistant' && (
                      <div className="chat-im-avatar chat-im-avatar-assistant" title="OpenClaw">OC</div>
                    )}
                    <div className="chat-im-bubble-content">
                      <div className="chat-im-bubble-body">
                        {m.role === 'assistant' ? (
                          <AssistantMarkdownBody
                            content={m.content}
                            revealType={
                              m.revealType === 'typewriter'
                                ? 'typewriter'
                                : m.streaming
                                  ? (m.revealType ?? 'streaming')
                                  : 'instant'
                            }
                            onContentLayout={scrollMessagesToBottom}
                          />
                        ) : (
                          <div className="chat-im-content">{m.content}</div>
                        )}
                      </div>
                      <div className="chat-im-bubble-meta">
                        <span className="chat-im-meta-label">{m.role === 'user' ? '我' : 'OpenClaw'}</span>
                        <span className="chat-im-meta-time">{formatTime(m.timestamp)}</span>
                      </div>
                    </div>
                    {m.role === 'user' && (
                      <div className="chat-im-avatar chat-im-avatar-user">我</div>
                    )}
                  </div>
                </div>
              ))}
            </div>

            <div className="chat-im-input-bar">
              {error && (
                <div className="chat-im-error-bar">
                  <span>{error}</span>
                </div>
              )}
              <div className="chat-im-input-wrapper">
                <textarea
                  className="chat-im-textarea"
                  placeholder="输入消息，Enter 发送，Shift+Enter 换行"
                  data-testid="openclaw-chat-input"
                  value={inputText}
                  onChange={(e) => setInputText(e.target.value)}
                  onKeyDown={(e) => e.key === 'Enter' && !e.shiftKey && (e.preventDefault(), sendMessage())}
                  disabled={sending}
                  rows={1}
                />
                <div className="chat-im-input-buttons">
                  <Link to="/" className="chat-im-btn-new">新会话</Link>
                  <button
                    type="button"
                    className="chat-im-btn-send"
                    onClick={sendMessage}
                    disabled={sending || !inputText.trim()}
                    data-testid="openclaw-send-btn"
                  >
                    {sending ? (
                      <span className="chat-im-send-loading">发送中</span>
                    ) : (
                      <>
                        <span className="chat-im-send-icon">发送</span>
                      </>
                    )}
                  </button>
                </div>
              </div>
            </div>
          </main>
        </>
      )}
    </div>
  )
}

export default OpenClawChatPage
