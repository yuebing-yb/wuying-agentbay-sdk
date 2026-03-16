import { useState, useEffect, useRef } from 'react'
import { saveCredentialsForSession } from '../utils/credentials'

const FORM_STORAGE_KEY = 'openclaw_session_form'

function getAgentBayApiKeyFromStorage(): string {
  try {
    const raw = sessionStorage.getItem(FORM_STORAGE_KEY)
    if (!raw) return ''
    const parsed = JSON.parse(raw) as Record<string, string>
    return parsed.agentbayApiKey || ''
  } catch {
    return ''
  }
}

interface SessionItem {
  sessionId: string
  username?: string
  status?: string
}

interface SessionListPanelProps {
  /** 点击某个 session 时，更新 URL 并跳转 */
  onSelectSession: (sessionId: string) => void
  /** 当前选中的 sessionId，用于高亮 */
  currentSessionId: string | null
}

function SessionListPanel({ onSelectSession, currentSessionId }: SessionListPanelProps) {
  const [open, setOpen] = useState(false)
  const panelRef = useRef<HTMLDivElement>(null)

  /** 点击弹窗以外区域时收起 */
  useEffect(() => {
    if (!open) return
    const handleClickOutside = (e: MouseEvent) => {
      if (panelRef.current && !panelRef.current.contains(e.target as Node)) {
        setOpen(false)
      }
    }
    document.addEventListener('mousedown', handleClickOutside)
    return () => document.removeEventListener('mousedown', handleClickOutside)
  }, [open])
  const [sessions, setSessions] = useState<SessionItem[]>([])
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState<string>('')

  /** 仅在打开弹窗时拉取列表，使用 GET /api/sessions（无需 API Key） */
  const loadSessionList = async () => {
    setLoading(true)
    setError('')
    try {
      const res = await fetch('/api/sessions')
      const data = await res.json()
      if (!res.ok) {
        throw new Error(data.detail || '获取会话列表失败')
      }
      const list = Array.isArray(data) ? data : []
      setSessions(
        list.map(
          (s: {
            sessionId?: string
            session_id?: string
            username?: string
            status?: string
          }) => ({
            sessionId: s.sessionId ?? s.session_id ?? '',
            username: s.username,
            status: s.status ?? 'unknown',
          })
        )
      )
    } catch (e: unknown) {
      setError(e instanceof Error ? e.message : '获取会话列表失败')
      setSessions([])
    } finally {
      setLoading(false)
    }
  }

  const handleOpen = () => {
    const next = !open
    setOpen(next)
    if (next) {
      loadSessionList()
    } else {
      setError('')
    }
  }

  /** 点击列表项：保存凭证、跳转并刷新（此时才获取会话详情） */
  const handleSelect = (sessionId: string) => {
    const apiKey = getAgentBayApiKeyFromStorage()
    if (apiKey) {
      saveCredentialsForSession(sessionId, {
        agentbayApiKey: apiKey,
        username: '未知',
      })
    }
    onSelectSession(sessionId)
    setOpen(false)
  }

  return (
    <div className="session-list-panel" ref={panelRef}>
      <button
        type="button"
        className="btn-session-list-trigger"
        onClick={handleOpen}
        title="查看会话列表"
      >
        {open ? '收起列表' : '会话列表'}
      </button>

      {open && (
        <div className="session-list-popup">
          <div className="session-list-header">
            <span>AgentBay 会话</span>
            <button
              type="button"
              className="session-list-close"
              onClick={() => setOpen(false)}
              aria-label="关闭"
            >
              ×
            </button>
          </div>
          {loading && (
            <div className="session-list-loading">
              <span className="spinner" />
              加载中...
            </div>
          )}
          {error && <div className="session-list-error">{error}</div>}
          {!loading && !error && sessions.length === 0 && (
            <div className="session-list-empty">暂无会话</div>
          )}
          {!loading && sessions.length > 0 && (
            <ul className="session-list-items">
              {sessions.map((s) => (
                <li key={s.sessionId}>
                  <button
                    type="button"
                    className={`session-list-item ${currentSessionId === s.sessionId ? 'active' : ''}`}
                    onClick={() => handleSelect(s.sessionId)}
                  >
                    <span className="session-list-item-id">{s.sessionId}</span>
                    {s.username && (
                      <span className="session-list-item-user"> · {s.username}</span>
                    )}
                    {s.status && (
                      <span
                        className={`session-list-item-status status-${s.status === 'paused' ? 'paused' : s.status === 'running' ? 'running' : 'unknown'}`}
                      >
                        {s.status === 'paused' ? '已休眠' : s.status === 'running' ? '运行中' : s.status}
                      </span>
                    )}
                  </button>
                </li>
              ))}
            </ul>
          )}
        </div>
      )}
    </div>
  )
}

export default SessionListPanel
