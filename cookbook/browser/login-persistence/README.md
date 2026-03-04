# Browser Login Persistence

Keep your web login sessions alive across AgentBay cloud browser environments — no need to re-login every time you create a new session.

## What You'll Build

```
Session 1                          Session 2
┌─────────────────────┐            ┌─────────────────────┐
│  Login to website    │            │  Open same website   │
│  Set cookies         │  Context   │  Already logged in!  │
│  Close session  ─────┼──► Sync ──►│  Cookies restored    │
│  (data saved)        │            │  No re-login needed  │
└─────────────────────┘            └─────────────────────┘
```

After completing this example you will be able to:

1. Create a persistent browser Context that survives across sessions
2. Save browser data (cookies, localStorage, etc.) when a session ends
3. Restore the saved data in a new session automatically

## Use Cases

- **AI Agent Workflows** — avoid wasting tokens and time on login flows every session
- **Batch Automation** — maintain consistent account state across multiple browser sessions
- **Development & Testing** — persist your debug session state between runs

## Prerequisites

1. **AgentBay API Key** — [Get one here](https://agentbay.console.aliyun.com/service-management)
2. **Python 3.8+**
3. **Dependencies**:
   ```bash
   pip install wuying-agentbay-sdk playwright
   playwright install chromium
   ```

## Quick Start

```bash
export AGENTBAY_API_KEY=your_api_key_here
cd cookbook/browser/login-persistence
python main.py
```

### Expected Output

```
============================================================
Step 1: Create a persistent Context for browser data
============================================================
Context created: SdkCtx-xxxxx (name: browser-login-demo-xxxxx)

============================================================
Step 2: First session — set test cookies
============================================================
Session 1 created: s-xxxxx
Browser initialized
Navigated to https://www.aliyun.com
Set 2 test cookies:
  - demo_session_token = persist_test_abc123
  - demo_user_id = user_42
  [OK] Cookie 'demo_session_token' verified in browser
  [OK] Cookie 'demo_user_id' verified in browser

============================================================
Step 3: Delete session — save browser data to Context
============================================================
Session 1 deleted with sync_context=True
Waiting for context sync to complete...

============================================================
Step 4: Second session — verify cookie persistence
============================================================
Session 2 created: s-yyyyy
Browser initialized

Total cookies in session 2: 6
Checking test cookie persistence:
  [OK] 'demo_session_token' persisted: persist_test_abc123
  [OK] 'demo_user_id' persisted: user_42

All cookies persisted across sessions!
```

## How It Works

### BrowserContext

`BrowserContext` is the SDK's mechanism for binding a persistent storage Context to a browser session. When the session ends, the browser's profile data (cookies, localStorage, IndexedDB, etc.) is uploaded to the Context. When a new session starts with the same Context, the data is downloaded and restored.

```python
from agentbay import BrowserContext

browser_context = BrowserContext(
    context_id="your_context_id",
    auto_upload=True  # save browser data when session ends
)
```

### Sync Modes

`BrowserSyncMode` controls how much browser data is synchronized:

| Mode | What's Synced | Best For |
|---|---|---|
| **STANDARD** (default) | Cookies, Local State, localStorage, IndexedDB, Session Storage, saved passwords, preferences, HSTS, GPU cache | Most scenarios — comprehensive login persistence with anti-detection consistency |
| **MINIMAL** | Cookies + Local State only | Lightweight use cases where only cookie-based auth is needed |

```python
from agentbay import BrowserContext, BrowserSyncMode

# Default: STANDARD mode (recommended)
browser_context = BrowserContext(context_id="ctx_id", auto_upload=True)

# Explicit MINIMAL mode
browser_context = BrowserContext(
    context_id="ctx_id",
    auto_upload=True,
    sync_mode=BrowserSyncMode.MINIMAL
)
```

### What STANDARD Mode Syncs

| Category | Files | Purpose |
|---|---|---|
| **Auth Core** | Cookies, Local State | Session tokens, auth cookies |
| **Client Storage** | localStorage, IndexedDB, Session Storage | App state, cached user data |
| **Credentials** | Login Data, Web Data | Saved passwords, form autofill |
| **Preferences** | Preferences, Secure Preferences | Browser and site settings |
| **Network** | TransportSecurity, Network Persistent State | HSTS pins, QUIC config |
| **Rendering** | GPUCache | WebGL fingerprint consistency |

> **Why does this matter?** Many websites use more than just cookies for authentication. They store tokens in localStorage, track device fingerprints via IndexedDB, and use HSTS to enforce security. STANDARD mode preserves all of these, reducing the chance of being flagged as a "new device" on your next session.

## Code Walkthrough

### 1. Create a Persistent Context

```python
ctx_result = await agent_bay.context.get("my-browser-profile", create=True)
context = ctx_result.context

browser_context = BrowserContext(context.id, auto_upload=True)
params = CreateSessionParams(
    image_id="browser_latest",
    browser_context=browser_context,
)
```

### 2. First Session — Login or Set Cookies

```python
result = await agent_bay.create(params)
session = result.session

await session.browser.initialize(BrowserOption())
endpoint_url = await session.browser.get_endpoint_url()

async with async_playwright() as p:
    browser = await p.chromium.connect_over_cdp(endpoint_url)
    ctx = browser.contexts[0]
    page = await ctx.new_page()
    await page.goto("https://example.com")
    # ... login or set cookies ...
```

### 3. Save Browser Data (Critical Step)

```python
# sync_context=True triggers browser data upload before deletion
await agent_bay.delete(session, sync_context=True)
```

> **Important**: If you omit `sync_context=True`, the browser data will **not** be saved to the Context. This is the most common mistake.

### 4. Second Session — Data Restored Automatically

```python
# Same params with the same browser_context
result2 = await agent_bay.create(params)
session2 = result2.session

await session2.browser.initialize(BrowserOption())
# Cookies and other browser data are already restored!
```

## Important Notes

- **Always pass `sync_context=True`** when deleting a session if you want to persist browser data. Without it, changes are lost.
- **Website-side expiry still applies.** If a website's cookies or tokens expire on the server side, persistence won't help — the server will reject the old tokens regardless.
- **Context storage has limits.** Browser profiles are typically small (a few MB), but avoid storing large caches unnecessarily. Use MINIMAL mode if you only need cookies.

## What's Next

- **[Form-Filling Agent](../form-filling-agent/)** — automate form filling with AI-powered browser control
- **[E-commerce Inspector](../e-commerce-inspector/)** — extract product data from e-commerce sites
- **[Browser Context API Reference](../../../python/docs/api/async/async-session-params.md)** — full BrowserContext and BrowserSyncMode documentation
- **[App Login Persistence (Mobile)](../../mobile/app-login-persistence/)** — similar persistence for mobile app login states
