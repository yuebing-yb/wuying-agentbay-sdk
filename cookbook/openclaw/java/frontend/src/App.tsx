import { useState } from 'react'
import SessionForm from './components/SessionForm'

/** 会话响应类型 */
interface SessionData {
  sessionId: string
  resourceUrl: string
  openclawUrl: string
  username: string
  createdAt: string
  status: string
}

type AppState = 'idle' | 'creating' | 'running' | 'destroying'

function App() {
  const [state, setState] = useState<AppState>('idle')
  const [session, setSession] = useState<SessionData | null>(null)
  const [error, setError] = useState<string>('')

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
    } catch (e: unknown) {
      setError(e instanceof Error ? e.message : '销毁会话失败')
      setState('running')
    }
  }

  return (
    <div className="app">
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

        {(state === 'idle' || state === 'creating') && (
          <SessionForm
            onSubmit={handleCreate}
            loading={state === 'creating'}
          />
        )}

        {(state === 'running' || state === 'destroying') && session && (
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

            {session.resourceUrl && (
              <a
                href={session.resourceUrl}
                target="_blank"
                rel="noopener noreferrer"
                className="btn btn-secondary resource-link"
              >
                打开沙箱远程桌面
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
        )}
      </main>
    </div>
  )
}

export default App
