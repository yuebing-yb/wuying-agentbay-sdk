import { useState, useEffect } from 'react'

interface DingtalkSetupPanelProps {
  sessionId: string
}

type SetupStep = 'idle' | 'login' | 'creating' | 'done' | 'manual' | 'error'

interface SetupStatus {
  step: SetupStep
  clientId?: string
  clientSecret?: string
  error?: string
}

function DingtalkSetupPanel({ sessionId }: DingtalkSetupPanelProps) {
  const [status, setStatus] = useState<SetupStatus | null>(null)
  const [loading, setLoading] = useState(false)
  const [clientId, setClientId] = useState('')
  const [clientSecret, setClientSecret] = useState('')
  const [applyLoading, setApplyLoading] = useState(false)
  const [showSecret, setShowSecret] = useState(false)

  const fetchStatus = async () => {
    try {
      const res = await fetch(`/api/sessions/${sessionId}/dingtalk-setup/status`)
      const data = await res.json()
      setStatus(data)
      if (data.clientId) setClientId(data.clientId)
      if (data.clientSecret) setClientSecret(data.clientSecret)
    } catch {
      setStatus(null)
    }
  }

  useEffect(() => {
    fetchStatus()
  }, [sessionId])

  const handleStart = async () => {
    setLoading(true)
    try {
      const res = await fetch(
        `/api/sessions/${sessionId}/dingtalk-setup/start?backend=playwright`,
        { method: 'POST' }
      )
      const data = await res.json()
      if (!res.ok) throw new Error(data.detail || '启动失败')
      setStatus({ step: 'login' })
    } catch (e) {
      setStatus({ step: 'error', error: e instanceof Error ? e.message : '启动失败' })
    } finally {
      setLoading(false)
    }
  }

  const handleLoggedIn = async () => {
    setLoading(true)
    try {
      const res = await fetch(
        `/api/sessions/${sessionId}/dingtalk-setup/continue?backend=playwright`,
        { method: 'POST' }
      )
      const data = await res.json()
      if (!res.ok) throw new Error(data.detail || '继续失败')
      setStatus({ step: 'done', clientId: data.clientId, clientSecret: data.clientSecret })
      setClientId(data.clientId || '')
      setClientSecret(data.clientSecret || '')
    } catch (e) {
      setStatus({ step: 'error', error: e instanceof Error ? e.message : '自动化失败' })
    } finally {
      setLoading(false)
    }
  }

  const handleApply = async () => {
    if (!clientId.trim() || !clientSecret.trim()) return
    setApplyLoading(true)
    try {
      const res = await fetch(`/api/sessions/${sessionId}/dingtalk-setup/apply`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ clientId: clientId.trim(), clientSecret: clientSecret.trim() }),
      })
      const data = await res.json()
      if (!res.ok) throw new Error(data.detail || '应用失败')
      setStatus({ step: 'done', clientId, clientSecret })
    } catch (e) {
      setStatus({ step: 'error', error: e instanceof Error ? e.message : '应用失败' })
    } finally {
      setApplyLoading(false)
    }
  }

  const step = status?.step ?? 'idle'

  return (
    <div className="dingtalk-setup-panel">
      <h3>一键配置钉钉机器人</h3>

      {step === 'idle' && (
        <div className="setup-step">
          <p className="setup-hint">自动打开钉钉开放平台，创建应用并获取凭证</p>
          <div className="setup-buttons-row">
            <button
              className="btn btn-primary"
              onClick={handleStart}
              disabled={loading}
            >
              {loading ? '启动中...' : '一键配置'}
            </button>
            <button
              className="btn btn-secondary"
              onClick={() => setStatus({ step: 'manual' })}
              disabled={loading}
            >
              手动配置
            </button>
          </div>
        </div>
      )}

      {step === 'login' && (
        <div className="setup-step">
          <p className="setup-hint">
            为了获取机器人权限，请使用钉钉 APP 扫描右侧云机中的二维码进行登录
          </p>
          <p className="setup-tip">小贴士：若页面卡住可刷新，或检查网络/代理</p>
          <button
            className="btn btn-primary"
            onClick={handleLoggedIn}
            disabled={loading}
          >
            {loading ? '正在创建应用...' : '我已登录'}
          </button>
        </div>
      )}

      {step === 'creating' && (
        <div className="setup-step">
          <p className="setup-hint">正在自动创建应用并提取凭证，请稍候...</p>
        </div>
      )}

      {(step === 'done' || step === 'manual') && (
        <div className="setup-step setup-done">
          <p className="setup-hint">
            {step === 'manual' ? '请手动填写钉钉应用凭证' : '已获取钉钉应用凭证，可修改后提交并更新配置'}
          </p>
          <div className="form-group">
            <label>Client ID</label>
            <input
              type="text"
              value={clientId}
              onChange={(e) => setClientId(e.target.value)}
              placeholder="钉钉应用 Client ID"
            />
          </div>
          <div className="form-group">
            <label>Client Secret</label>
            <div className="secret-input-wrapper">
              <input
                type={showSecret ? 'text' : 'password'}
                value={clientSecret}
                onChange={(e) => setClientSecret(e.target.value)}
                placeholder="钉钉应用 Client Secret"
              />
              <button
                type="button"
                className="secret-toggle-btn"
                onClick={() => setShowSecret((v) => !v)}
                title={showSecret ? '隐藏' : '显示'}
                aria-label={showSecret ? '隐藏 Client Secret' : '显示 Client Secret'}
              >
                {showSecret ? (
                  <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
                    <path d="M17.94 17.94A10.07 10.07 0 0 1 12 20c-7 0-11-8-11-8a18.45 18.45 0 0 1 5.06-5.94M9.9 4.24A9.12 9.12 0 0 1 12 4c7 0 11 8 11 8a18.5 18.5 0 0 1-2.16 3.19m-6.72-1.07a3 3 0 1 1-4.24-4.24" />
                    <line x1="1" y1="1" x2="23" y2="23" />
                  </svg>
                ) : (
                  <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
                    <path d="M1 12s4-8 11-8 11 8 11 8-4 8-11 8-11-8-11-8z" />
                    <circle cx="12" cy="12" r="3" />
                  </svg>
                )}
              </button>
            </div>
          </div>
          <div className="setup-buttons-row">
            <button
              className="btn btn-primary"
              onClick={handleApply}
              disabled={applyLoading || !clientId.trim() || !clientSecret.trim()}
            >
              {applyLoading ? '更新中...' : '提交并更新配置'}
            </button>
            {step === 'manual' && (
              <button
                className="btn btn-secondary"
                onClick={() => setStatus({ step: 'idle' })}
                disabled={applyLoading}
              >
                返回
              </button>
            )}
          </div>
        </div>
      )}

      {step === 'error' && (
        <div className="setup-step setup-error">
          <p className="setup-error-msg">{status?.error}</p>
          <div className="setup-error-actions">
            <button className="btn btn-secondary" onClick={() => setStatus({ step: 'idle' })}>
              重新开始
            </button>
            <button
              className="btn btn-secondary"
              onClick={() => setStatus({ step: 'done' })}
            >
              手动填写凭证
            </button>
          </div>
        </div>
      )}
    </div>
  )
}

export default DingtalkSetupPanel
