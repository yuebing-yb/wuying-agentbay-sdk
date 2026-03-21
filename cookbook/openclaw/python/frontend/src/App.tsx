import { useState, useEffect } from 'react'
import { Routes, Route, Link } from 'react-router-dom'
import SessionForm from './components/SessionForm'
import DingtalkSetupPanel from './components/DingtalkSetupPanel'
import FeishuSetupPanel from './components/FeishuSetupPanel'
import OpenClawChatPage from './pages/OpenClawChatPage'
import {
  getCredentialsForSession,
  removeCredentialsForSession,
  saveCredentialsForSession,
} from './utils/credentials'

const SESSION_ID_PARAM = 'sessionId'

/** 从 URL 读取 sessionId */
function getSessionIdFromUrl(): string | null {
  const params = new URLSearchParams(window.location.search)
  return params.get(SESSION_ID_PARAM)
}

/** 更新 URL，添加或移除 sessionId，并触发导航 */
function updateUrlSessionId(sessionId: string | null) {
  const url = new URL(window.location.href)
  if (sessionId) {
    url.searchParams.set(SESSION_ID_PARAM, sessionId)
  } else {
    url.searchParams.delete(SESSION_ID_PARAM)
  }
  window.history.replaceState({}, '', url.toString())
}

/** 跳转到指定 session（更新 URL 并触发恢复流程）- 供 SessionListPanel 使用，会话列表注释时一并注释 */
// function navigateToSession(sessionId: string) {
//   updateUrlSessionId(sessionId)
//   window.location.reload()
// }

/** 会话响应类型 */
interface SessionData {
  sessionId: string
  resourceUrl: string
  openclawUrl: string
  username: string
  createdAt: string
  status: string
  contextName?: string
  contextId?: string
}

type AppState = 'idle' | 'creating' | 'running' | 'destroying' | 'restoring' | 'pausing' | 'resuming'

function App() {
  const [state, setState] = useState<AppState>('idle')
  const [session, setSession] = useState<SessionData | null>(null)
  const [error, setError] = useState<string>('')

  /** 页面加载时：若 URL 中有 sessionId，则恢复会话 */
  useEffect(() => {
    const sid = getSessionIdFromUrl()
    if (!sid) return

    const restore = async () => {
      setState('restoring')
      setError('')
      try {
        const creds = getCredentialsForSession(sid)
        const headers: Record<string, string> = {}
        if (creds) {
          const encoded = encodeURIComponent(JSON.stringify(creds)).replace(
            /%([0-9A-F]{2})/g,
            (_, p1) => String.fromCharCode(parseInt(p1, 16))
          )
          headers['X-OpenClaw-Form-Data'] = btoa(encoded)
        }
        const res = await fetch(`/api/sessions/${sid}`, { headers })
        const data = await res.json()
        if (!res.ok) {
          throw new Error(data.detail || '会话不存在')
        }
        setSession(data)
        setState('running')
      } catch (e: unknown) {
        setError(e instanceof Error ? e.message : '恢复会话失败')
        updateUrlSessionId(null)
        setState('idle')
      }
    }
    restore()
  }, [])

  const handleCreate = async (formData: Record<string, string>) => {
    setState('creating')
    setError('')
    try {
      const res = await fetch('/api/sessions', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(formData),
      })
      const data = await res.json()
      if (!res.ok) {
        throw new Error(data.detail || '创建会话失败')
      }
      setSession(data)
      setState('running')
      updateUrlSessionId(data.sessionId)
      saveCredentialsForSession(data.sessionId, formData)
    } catch (e: unknown) {
      setError(e instanceof Error ? e.message : '创建会话失败')
      setState('idle')
    }
  }

  const handleResume = async () => {
    if (!session) return
    setState('resuming')
    setError('')
    try {
      const res = await fetch(`/api/sessions/${session.sessionId}/resume`, {
        method: 'POST',
      })
      const data = await res.json()
      if (!res.ok) {
        throw new Error(data.detail || '恢复会话失败')
      }
      // 兼容 snake_case 与 camelCase，确保 resourceUrl 正确更新
      setSession({
        sessionId: data.sessionId ?? data.session_id,
        resourceUrl: data.resourceUrl ?? data.resource_url ?? '',
        openclawUrl: data.openclawUrl ?? data.openclaw_url ?? '',
        username: data.username ?? '',
        createdAt: data.createdAt ?? data.created_at ?? '',
        status: data.status ?? 'running',
        contextName: data.contextName ?? data.context_name ?? undefined,
        contextId: data.contextId ?? data.context_id ?? undefined,
      })
      // 恢复成功后 1 秒刷新页面，确保右侧桌面加载最新 resourceUrl
      setTimeout(() => window.location.reload(), 1000)
    } catch (e: unknown) {
      setError(e instanceof Error ? e.message : '恢复会话失败')
    } finally {
      setState('running')
    }
  }

  const handlePause = async () => {
    if (!session) return
    setState('pausing')
    setError('')
    try {
      const res = await fetch(`/api/sessions/${session.sessionId}/pause`, {
        method: 'POST',
      })
      if (!res.ok) {
        const data = await res.json()
        throw new Error(data.detail || '休眠会话失败')
      }
      setSession((s) => (s ? { ...s, status: 'paused' } : null))
    } catch (e: unknown) {
      setError(e instanceof Error ? e.message : '休眠会话失败')
    } finally {
      setState('running')
    }
  }

  const handleDestroy = async () => {
    if (!session) return
    setState('destroying')
    setError('')
    try {
      const res = await fetch(`/api/sessions/${session.sessionId}`, {
        method: 'DELETE',
      })
      if (!res.ok) {
        const data = await res.json()
        throw new Error(data.detail || '销毁会话失败')
      }
      removeCredentialsForSession(session.sessionId)
      setSession(null)
      setState('idle')
      updateUrlSessionId(null)
    } catch (e: unknown) {
      setError(e instanceof Error ? e.message : '销毁会话失败')
      setState('running')
    }
  }

  const isSessionActive =
    (state === 'running' || state === 'destroying' || state === 'restoring' || state === 'pausing' ||
      state === 'resuming') &&
    session

  return (
    <Routes>
      <Route path="/chat" element={<OpenClawChatPage />} />
      <Route
        path="/*"
        element={(
    <div className={`app ${isSessionActive ? 'session-active' : ''}`}>
      <header className="app-header">
        {/* 会话列表入口（逻辑有 bug，暂时注释）
        <div className="app-header-left">
          <SessionListPanel
            onSelectSession={(sessionId) => navigateToSession(sessionId)}
            currentSessionId={session?.sessionId ?? null}
          />
        </div>
        */}
        <div className="app-header-center">
          <h1>OpenClaw in AgentBay</h1>
          <p className="subtitle">一键创建 OpenClaw 沙箱环境</p>
        </div>
      </header>

      <main className="app-main">
        {error && (
          <div className="error-banner">
            <span>{error}</span>
            <button onClick={() => setError('')} className="error-close">x</button>
          </div>
        )}

        {state === 'restoring' && (
          <div className="card session-form">
            <h2>恢复会话</h2>
            <p className="loading-text">
              <span className="spinner" />
              正在恢复会话...
            </p>
          </div>
        )}

        {(state === 'idle' || state === 'creating') && (
          <SessionForm
            onSubmit={handleCreate}
            loading={state === 'creating'}
          />
        )}

        {(state === 'running' || state === 'destroying' || state === 'pausing' || state === 'resuming') &&
          session && (
          <div className="session-layout">
            <aside className="session-sidebar">
              <div className="card session-card" data-session-id={session.sessionId}>
                <h2>会话已就绪</h2>
                <div className="session-info">
                  <div className="info-row">
                    <span className="info-label">用户</span>
                    <span className="info-value">{session.username}</span>
                  </div>
                  <div className="info-row">
                    <span className="info-label">会话 ID</span>
                    <span className="info-value mono">{session.sessionId}</span>
                  </div>
                  {(session.contextName ?? session.contextId) && (
                    <>
                      {session.contextName && (
                        <div className="info-row">
                          <span className="info-label">Context 名称</span>
                          <span className="info-value">{session.contextName}</span>
                        </div>
                      )}
                      {session.contextId && (
                        <div className="info-row">
                          <span className="info-label">Context ID</span>
                          <span className="info-value mono">{session.contextId}</span>
                        </div>
                      )}
                    </>
                  )}
                  <div className="info-row">
                    <span className="info-label">创建时间</span>
                    <span className="info-value">{session.createdAt}</span>
                  </div>
                  <div className="info-row">
                    <span className="info-label">状态</span>
                    <span
                      className={`info-value ${session.status === 'paused' ? 'status-paused' : 'status-running'}`}
                    >
                      {session.status === 'paused' ? '已休眠' : session.status}
                    </span>
                  </div>
                </div>

                <Link
                  to={`/chat?sessionId=${session.sessionId}`}
                  className="btn btn-outline"
                  target="_blank"
                  rel="noopener noreferrer"
                  data-testid="openclaw-standalone-chat-link"
                >
                  与OpenClaw 对话
                </Link>
                <DingtalkSetupPanel sessionId={session.sessionId} />
                <FeishuSetupPanel sessionId={session.sessionId} />

                {session.openclawUrl && (
                  <button
                    type="button"
                    className="btn btn-primary resource-link"
                    onClick={async () => {
                      try {
                        const res = await fetch(`/api/sessions/${session.sessionId}/restart-dashboard`, {
                          method: 'POST',
                        })
                        if (!res.ok) {
                          const data = await res.json().catch(() => ({}))
                          console.warn('Restart dashboard failed:', data.detail || res.statusText)
                        }
                      } catch (e) {
                        console.warn('Restart dashboard failed:', e)
                      }
                      window.open(session.openclawUrl, '_blank', 'noopener,noreferrer')
                    }}
                  >
                    打开 OpenClaw UI
                  </button>
                )}

                {session.status === 'paused' ? (
                  <button
                    onClick={handleResume}
                    disabled={state === 'resuming'}
                    className="btn btn-primary btn-session-action"
                  >
                    {state === 'resuming' ? '正在恢复...' : '恢复会话'}
                  </button>
                ) : (
                  <button
                    onClick={handlePause}
                    disabled={state === 'pausing'}
                    className="btn btn-outline btn-session-action"
                    title="休眠后可通过恢复会话链接重新唤醒"
                  >
                    {state === 'pausing' ? '正在休眠...' : '会话休眠'}
                  </button>
                )}

                <button
                  onClick={handleDestroy}
                  disabled={state === 'destroying'}
                  className="btn btn-danger"
                >
                  {state === 'destroying' ? '正在销毁...' : '销毁会话'}
                </button>
              </div>
            </aside>

            <section className="desktop-panel">
              {session.resourceUrl ? (
                <iframe
                  key={session.resourceUrl}
                  src={session.resourceUrl}
                  title="远程沙箱桌面"
                  className="desktop-iframe"
                  sandbox="allow-same-origin allow-scripts allow-popups allow-forms"
                  allow="fullscreen"
                />
              ) : (
                <div className="desktop-placeholder">
                  <p>暂无远程桌面链接</p>
                  <p className="placeholder-hint">当前会话可能不支持 resourceUrl</p>
                </div>
              )}
            </section>
          </div>
        )}
      </main>
    </div>
        )}
      />
    </Routes>
  )
}

export default App
