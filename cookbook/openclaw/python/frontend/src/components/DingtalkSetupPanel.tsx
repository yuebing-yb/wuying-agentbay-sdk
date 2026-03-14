import { useState, useEffect } from 'react'
import { getCredentialsForSession, updateDingtalkCredentialsForSession } from '../utils/credentials'

interface DingtalkSetupPanelProps {
  sessionId: string
}

type SetupStep = 'idle' | 'login' | 'creating' | 'done' | 'manual' | 'saved' | 'error'

interface SetupStatus {
  step: SetupStep
  clientId?: string
  clientSecret?: string
  error?: string
  applied?: boolean
  applyError?: string
}

function DingtalkSetupPanel({ sessionId }: DingtalkSetupPanelProps) {
  const [status, setStatus] = useState<SetupStatus | null>(null)
  const [loading, setLoading] = useState(false)
  const [clientId, setClientId] = useState('')
  const [clientSecret, setClientSecret] = useState('')
  const [applyLoading, setApplyLoading] = useState(false)
  const [showSecret, setShowSecret] = useState(false)

  const fetchStatus = async () => {
    let apiStatus: SetupStatus | null = null
    try {
      const res = await fetch(`/api/sessions/${sessionId}/dingtalk-setup/status`)
      const data = await res.json()
      apiStatus = data
      setStatus(data)
      if (data.clientId) setClientId(data.clientId)
      if (data.clientSecret) setClientSecret(data.clientSecret)
      if (data.clientId && data.clientSecret) {
        updateDingtalkCredentialsForSession(sessionId, data.clientId, data.clientSecret)
      }
    } catch {
      setStatus(null)
    }
    // 若 sessionStorage 已有钉钉凭证且后端为 idle，展示保存的凭证供用户应用
    const creds = getCredentialsForSession(sessionId)
    if (creds?.dingtalkClientId && creds?.dingtalkClientSecret && (!apiStatus || apiStatus.step === 'idle')) {
      setClientId(creds.dingtalkClientId)
      setClientSecret(creds.dingtalkClientSecret)
      setStatus({ step: 'saved', clientId: creds.dingtalkClientId, clientSecret: creds.dingtalkClientSecret })
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
      setStatus({
        step: 'done',
        clientId: data.clientId,
        clientSecret: data.clientSecret,
        applied: data.applied,
        applyError: data.applyError,
      })
      setClientId(data.clientId || '')
      setClientSecret(data.clientSecret || '')
      if (data.clientId && data.clientSecret) {
        updateDingtalkCredentialsForSession(sessionId, data.clientId, data.clientSecret)
      }
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
      setStatus({ step: 'done', clientId, clientSecret, applied: true })
      updateDingtalkCredentialsForSession(sessionId, clientId.trim(), clientSecret.trim())
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

      {step === 'saved' && (
        <div className="setup-step setup-done">
          <p className="setup-hint">已检测到保存的钉钉凭证，点击下方按钮应用到配置</p>
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
              {applyLoading ? (
                <span className="loading-text">
                  <span className="spinner" />
                  正在应用...
                </span>
              ) : (
                '应用配置'
              )}
            </button>
            <button
              className="btn btn-secondary"
              onClick={() => setStatus({ step: 'idle' })}
              disabled={applyLoading}
            >
              重新配置
            </button>
          </div>
        </div>
      )}

      {step === 'idle' && (
        <div className="setup-step">
          <p className="setup-hint">自动打开钉钉开放平台，创建应用并获取凭证</p>
          <div className="setup-buttons-row">
            <button
              className="btn btn-primary"
              onClick={handleStart}
              disabled={loading}
            >
              {loading ? '正在打开...' : '一键配置'}
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
            {loading ? (
              <span className="loading-text">
                <span className="spinner" />
                正在自动配置...
              </span>
            ) : (
              '我已登录'
            )}
          </button>
        </div>
      )}

      {step === 'creating' && (
        <div className="setup-step">
          <p className="setup-hint">
            <span className="loading-text">
              <span className="spinner" />
              正在自动创建应用并提取凭证...
            </span>
          </p>
        </div>
      )}

      {step === 'done' && (
        <div className="setup-step setup-done">
          <p className="setup-hint">
            {status?.applied
              ? '已获取钉钉应用凭证并已应用到配置，Gateway 已重启'
              : status?.applyError
                ? `已获取凭证，但自动应用失败：${status.applyError}，请点击下方按钮重试`
                : '已获取钉钉应用凭证，确认后点击应用按钮'}
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
          {!status?.applied && (
            <button
              className="btn btn-primary"
              onClick={handleApply}
              disabled={applyLoading || !clientId.trim() || !clientSecret.trim()}
            >
              {applyLoading ? (
                <span className="loading-text">
                  <span className="spinner" />
                  正在应用...
                </span>
              ) : (
                '应用到配置'
              )}
            </button>
          )}
        </div>
      )}

      {step === 'manual' && (
        <div className="setup-step setup-done">
          <p className="setup-hint">
            请前往
            <a
              href="https://open-dev.dingtalk.com"
              target="_blank"
              rel="noopener noreferrer"
            >
              钉钉开放平台
            </a>
            创建应用并获取凭证
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
          <button
            className="btn btn-primary"
            onClick={handleApply}
            disabled={applyLoading || !clientId.trim() || !clientSecret.trim()}
          >
            {applyLoading ? (
              <span className="loading-text">
                <span className="spinner" />
                正在应用...
              </span>
            ) : (
              '应用到配置'
            )}
          </button>
        </div>
      )}

      {step === 'error' && (
        <div className="setup-step setup-error">
          <p className="setup-error-msg">{status?.error || '配置失败'}</p>
          <div className="setup-error-actions">
            <button
              className="btn btn-primary"
              onClick={handleStart}
              disabled={loading}
            >
              重试
            </button>
            <button
              className="btn btn-secondary"
              onClick={() => setStatus({ step: 'manual' })}
            >
              手动配置
            </button>
          </div>
        </div>
      )}
    </div>
  )
}

export default DingtalkSetupPanel
