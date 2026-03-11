import { useState, useEffect } from 'react'
import SessionForm from './components/SessionForm'
import DingtalkSetupPanel from './components/DingtalkSetupPanel'

const SESSION_ID_PARAM = 'sessionId'

/** 从 URL 读取 sessionId */
function getSessionIdFromUrl(): string | null {
  const params = new URLSearchParams(window.location.search)
  return params.get(SESSION_ID_PARAM)
}

/** 更新 URL，添加或移除 sessionId */
function updateUrlSessionId(sessionId: string | null) {
  const url = new URL(window.location.href)
  if (sessionId) {
    url.searchParams.set(SESSION_ID_PARAM, sessionId)
  } else {
    url.searchParams.delete(SESSION_ID_PARAM)
  }
  window.history.replaceState({}, '', url.toString())
}

/** 会话响应类型 */
interface SessionData {
  sessionId: string
  resourceUrl: string
  openclawUrl: string
  username: string
  createdAt: string
  status: string
}

type AppState = 'idle' | 'creating' | 'running' | 'destroying' | 'restoring'

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
        const res = await fetch(`/api/sessions/${sid}`)
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
    } catch (e: unknown) {
      setError(e instanceof Error ? e.message : '创建会话失败')
      setState('idle')
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
      setSession(null)
      setState('idle')
      updateUrlSessionId(null)
    } catch (e: unknown) {
      setError(e instanceof Error ? e.message : '销毁会话失败')
      setState('running')
    }
  }

  const isSessionActive = (state === 'running' || state === 'destroying' || state === 'restoring') && session

  return (
    <div className={`app ${isSessionActive ? 'session-active' : ''}`}>
      <header className="app-header">
        <h1>OpenClaw in AgentBay</h1>
        <p className="subtitle">一键创建 OpenClaw 沙箱环境</p>
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

        {(state === 'running' || state === 'destroying') && session && (
          <div className="session-layout">
            <aside className="session-sidebar">
              <div className="card session-card">
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
                  <div className="info-row">
                    <span className="info-label">创建时间</span>
                    <span className="info-value">{session.createdAt}</span>
                  </div>
                  <div className="info-row">
                    <span className="info-label">状态</span>
                    <span className="info-value status-running">{session.status}</span>
                  </div>
                </div>

                <DingtalkSetupPanel sessionId={session.sessionId} />

                {session.openclawUrl && (
                  <a
                    href={session.openclawUrl}
                    target="_blank"
                    rel="noopener noreferrer"
                    className="btn btn-primary resource-link"
                  >
                    打开 OpenClaw UI
                  </a>
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
  )
}

export default App
