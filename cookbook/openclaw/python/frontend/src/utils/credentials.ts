const CREDENTIALS_STORAGE_KEY = 'openclaw_session_credentials'

/** 按 sessionId 缓存表单数据到 sessionStorage */
export function saveCredentialsForSession(sessionId: string, formData: Record<string, string>) {
  try {
    const raw = sessionStorage.getItem(CREDENTIALS_STORAGE_KEY)
    const creds: Record<string, Record<string, string>> = raw ? JSON.parse(raw) : {}
    creds[sessionId] = formData
    sessionStorage.setItem(CREDENTIALS_STORAGE_KEY, JSON.stringify(creds))
  } catch {
    // ignore
  }
}

/** 从 sessionStorage 读取某 session 的表单数据 */
export function getCredentialsForSession(sessionId: string): Record<string, string> | null {
  try {
    const raw = sessionStorage.getItem(CREDENTIALS_STORAGE_KEY)
    if (!raw) return null
    const creds = JSON.parse(raw) as Record<string, Record<string, string>>
    return creds[sessionId] ?? null
  } catch {
    return null
  }
}

/** 删除某 session 的缓存 */
export function removeCredentialsForSession(sessionId: string) {
  try {
    const raw = sessionStorage.getItem(CREDENTIALS_STORAGE_KEY)
    if (!raw) return
    const creds = JSON.parse(raw) as Record<string, Record<string, string>>
    delete creds[sessionId]
    sessionStorage.setItem(CREDENTIALS_STORAGE_KEY, JSON.stringify(creds))
  } catch {
    // ignore
  }
}

/** 更新某 session 的飞书凭证到 sessionStorage */
export function updateFeishuCredentialsForSession(
  sessionId: string,
  appId: string,
  appSecret: string
) {
  try {
    const raw = sessionStorage.getItem(CREDENTIALS_STORAGE_KEY)
    const creds: Record<string, Record<string, string>> = raw ? JSON.parse(raw) : {}
    const existing = creds[sessionId] ?? {}
    creds[sessionId] = { ...existing, feishuAppId: appId, feishuAppSecret: appSecret }
    sessionStorage.setItem(CREDENTIALS_STORAGE_KEY, JSON.stringify(creds))
  } catch {
    // ignore
  }
}
