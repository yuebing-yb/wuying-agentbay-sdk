import { useState } from 'react'

const STORAGE_KEY = 'openclaw_session_form'

const DEFAULT_VALUES = {
  username: '',
  agentbayApiKey: '',
  bailianApiKey: '',
  modelBaseUrl: 'https://dashscope.aliyuncs.com/compatible-mode/v1',
  modelId: 'qwen3-max-2026-01-23',
} as const

function loadFromStorage(): Record<string, string> {
  try {
    const raw = sessionStorage.getItem(STORAGE_KEY)
    if (!raw) return { ...DEFAULT_VALUES }
    const parsed = JSON.parse(raw) as Record<string, string>
    return { ...DEFAULT_VALUES, ...parsed }
  } catch {
    return { ...DEFAULT_VALUES }
  }
}

function saveToStorage(data: Record<string, string>) {
  try {
    sessionStorage.setItem(STORAGE_KEY, JSON.stringify(data))
  } catch {
    // ignore quota / privacy errors
  }
}

interface SessionFormProps {
  onSubmit: (data: Record<string, string>) => void
  loading: boolean
}

function SessionForm({ onSubmit, loading }: SessionFormProps) {
  const [values, setValues] = useState<Record<string, string>>(loadFromStorage)

  const updateField = (name: string, value: string) => {
    setValues((prev: Record<string, string>) => {
      const next = { ...prev, [name]: value }
      saveToStorage(next)
      return next
    })
  }

  const handleSubmit = (e: React.FormEvent<HTMLFormElement>) => {
    e.preventDefault()
    const fd = new FormData(e.currentTarget)
    const data: Record<string, string> = {}
    fd.forEach((v, k) => {
      const val = v.toString().trim()
      if (val) data[k] = val
    })
    const merged = { ...values, ...data }
    saveToStorage(merged)
    onSubmit(merged)
  }

  return (
    <form className="card session-form" onSubmit={handleSubmit}>
      <h2>创建 OpenClaw 会话</h2>

      {/* 必填字段 */}
      <div className="form-group">
        <label htmlFor="username">用户名称</label>
        <input
          id="username"
          name="username"
          type="text"
          required
          placeholder="输入您的名称"
          value={values.username}
          onChange={(e) => updateField('username', e.target.value)}
          disabled={loading}
        />
      </div>

      <div className="form-group">
        <label htmlFor="agentbayApiKey">
          AgentBay API Key
          <a href="https://agentbay.console.aliyun.com" target="_blank" rel="noopener noreferrer" className="console-link">前往控制台 ↗</a>
        </label>
        <input
          id="agentbayApiKey"
          name="agentbayApiKey"
          type="password"
          required
          placeholder="输入 AgentBay API Key"
          value={values.agentbayApiKey}
          onChange={(e) => updateField('agentbayApiKey', e.target.value)}
          disabled={loading}
        />
      </div>

      <div className="form-group">
        <label htmlFor="bailianApiKey">
          百炼 API Key
          <a href="https://bailian.console.aliyun.com" target="_blank" rel="noopener noreferrer" className="console-link">前往控制台 ↗</a>
        </label>
        <input
          id="bailianApiKey"
          name="bailianApiKey"
          type="password"
          required
          placeholder="输入百炼 (DashScope) API Key"
          value={values.bailianApiKey}
          onChange={(e) => updateField('bailianApiKey', e.target.value)}
          disabled={loading}
        />
      </div>

      <div className="form-group">
        <label htmlFor="modelBaseUrl">模型 Base URL</label>
        <input
          id="modelBaseUrl"
          name="modelBaseUrl"
          type="text"
          placeholder="模型服务 Base URL"
          value={values.modelBaseUrl}
          onChange={(e) => updateField('modelBaseUrl', e.target.value)}
          disabled={loading}
        />
      </div>

      <div className="form-group">
        <label htmlFor="modelId">模型 ID</label>
        <input
          id="modelId"
          name="modelId"
          type="text"
          placeholder="模型名称，如 qwen3-max-2026-01-23"
          value={values.modelId}
          onChange={(e) => updateField('modelId', e.target.value)}
          disabled={loading}
        />
      </div>

      <button type="submit" className="btn btn-primary" disabled={loading}>
        {loading ? (
          <span className="loading-text">
            <span className="spinner" />
            正在创建会话，请稍候（约 1-2 分钟）...
          </span>
        ) : (
          '启动会话'
        )}
      </button>
    </form>
  )
}

export default SessionForm
