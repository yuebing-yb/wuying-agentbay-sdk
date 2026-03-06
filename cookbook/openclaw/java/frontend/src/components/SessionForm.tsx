import { useState } from 'react'

interface SessionFormProps {
  onSubmit: (data: Record<string, string>) => void
  loading: boolean
}

function SessionForm({ onSubmit, loading }: SessionFormProps) {
  const [showOptional, setShowOptional] = useState(false)

  const handleSubmit = (e: React.FormEvent<HTMLFormElement>) => {
    e.preventDefault()
    const fd = new FormData(e.currentTarget)
    const data: Record<string, string> = {}
    fd.forEach((v, k) => {
      const val = v.toString().trim()
      if (val) data[k] = val
    })
    onSubmit(data)
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
          disabled={loading}
        />
      </div>

      <div className="form-group">
        <label htmlFor="modelBaseUrl">模型 Base URL</label>
        <input
          id="modelBaseUrl"
          name="modelBaseUrl"
          type="text"
          defaultValue="https://dashscope.aliyuncs.com/compatible-mode/v1"
          placeholder="模型服务 Base URL"
          disabled={loading}
        />
      </div>

      <div className="form-group">
        <label htmlFor="modelId">模型 ID</label>
        <input
          id="modelId"
          name="modelId"
          type="text"
          defaultValue="qwen3-max-2026-01-23"
          placeholder="模型名称，如 qwen3-max-2026-01-23"
          disabled={loading}
        />
      </div>

      {/* 可选字段折叠区域 */}
      <div className="optional-section">
        <button
          type="button"
          className="toggle-btn"
          onClick={() => setShowOptional(!showOptional)}
        >
          {showOptional ? '收起' : '展开'} 可选配置（钉钉 / 飞书）
        </button>

        {showOptional && (
          <div className="optional-fields">
            <fieldset>
              <legend>钉钉配置</legend>
              <div className="form-group">
                <label htmlFor="dingtalkClientId">Client ID</label>
                <input
                  id="dingtalkClientId"
                  name="dingtalkClientId"
                  type="text"
                  placeholder="钉钉 Client ID"
                  disabled={loading}
                />
              </div>
              <div className="form-group">
                <label htmlFor="dingtalkClientSecret">Client Secret</label>
                <input
                  id="dingtalkClientSecret"
                  name="dingtalkClientSecret"
                  type="password"
                  placeholder="钉钉 Client Secret"
                  disabled={loading}
                />
              </div>
            </fieldset>

            <fieldset>
              <legend>飞书配置</legend>
              <div className="form-group">
                <label htmlFor="feishuAppId">App ID</label>
                <input
                  id="feishuAppId"
                  name="feishuAppId"
                  type="text"
                  placeholder="飞书 App ID"
                  disabled={loading}
                />
              </div>
              <div className="form-group">
                <label htmlFor="feishuAppSecret">App Secret</label>
                <input
                  id="feishuAppSecret"
                  name="feishuAppSecret"
                  type="password"
                  placeholder="飞书 App Secret"
                  disabled={loading}
                />
              </div>
            </fieldset>
          </div>
        )}
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
