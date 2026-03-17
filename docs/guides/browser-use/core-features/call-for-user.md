# Call For User

The Call For User feature handles scenarios where browser automation encounters situations that require human intervention. This includes authentication challenges, complex verification processes, or security measures that cannot be automatically resolved by the system.

> **Use Cases:** This feature is triggered when the browser encounters user information requests, authentication challenges, or other scenarios that require manual human interaction to proceed.

The interface is unified across BrowserUse, ComputerUse, and MobileUse. Messages are delivered as a structured payload (e.g. JSON) with the following shape:

```ts
interface CallForUserMessage {
  type: string;      // "call-for-user"
  id: number;        // notify id (used for send_takeover_done)
  code: number;      // scenario code
  message: string;   // human-readable message
  action: string;    // "none" | "pause" | "resume" | "takeover" | "takeoverdone"
  extraParams: {};   // optional params, e.g. { max_wait_time: 180 }
}
```

## Call For User Scenarios

Common scenarios and their `type`, `code`, `message`, `action`, and `extraParams` are listed below. This table may be extended as more scenarios are added.

| type           | code | message                 | action       | extraParams            | Notes |
|----------------|------|-------------------------|-------------|------------------------|-------|
| call-for-user  | 0    | "common notice message" | none        | {}                     | Reserved for generic notifications. No action required. |
| call-for-user  | 101  | "captcha request"       | takeover    | {"max_wait_time": 180} | User intervention required; open session URL for user. Max wait 180s. Includes login, payment, or captcha failure. |
| call-for-user  | 102  | "login request"         | takeover    | {"max_wait_time": 180} | Login requires user intervention. Max wait 180s. |
| call-for-user  | 103  | "pay request"           | takeover    | {"max_wait_time": 180} | Payment requires user intervention. Max wait 180s. |
| call-for-user  | 199  | "user handle done"      | takeoverdone| {}                     | Reverse notification: user takeover completed (mirror → SDK). |
| call-for-user  | 201  | "captcha solving start" | pause       | {"max_wait_time": 60}  | Pause business flow; captcha is being solved automatically. Max wait 60s. |
| call-for-user  | 202  | "captcha solving finish"| resume      | {}                     | Resume business flow after captcha solved. |
| call-for-user  | 301  | "auto login start"      | pause       | {"max_wait_time": 100}  | Pause business flow; auto login in progress. Max wait 100s. |
| call-for-user  | 302  | "auto login finish"     | resume      | {}                     | Resume business flow after auto login succeeded. |

## Action Handling

After your app receives a call-for-user message, handle it according to `action`:

| action       | Meaning | What to do |
|-------------|--------|------------|
| **none**    | No operation | Ignore; no response needed. |
| **pause**   | Automation in progress | Pause your business flow and wait. Max wait time is in `extraParams.max_wait_time` (seconds). Resume only after a **resume** message. Example: user is logging in; a captcha appears → you get `pause`; wait until you get `resume` before continuing. |
| **resume**  | Automation done | Leave the pause state and continue your business flow. |
| **takeover**| User must intervene | Have the user complete the task (e.g. open session resource URL in a browser). When done, call `session.browser.send_takeover_done(notify_id)`. If you do not call it, the system will continue after the max wait time. |
| **takeoverdone** | User takeover completed (reverse) | Mirror notifies that user takeover is done; SDK side can continue. |

## SDK Integration

### Browser option: call_for_user

Enable call-for-user (manual user takeover) by setting `call_for_user=True` when initializing the browser. The mirror will then send call-for-user messages when intervention is needed (e.g. captcha, login, payment).

```python
from agentbay import BrowserOption

browser_option = BrowserOption(
    call_for_user=True,  # enable call-for-user notifications
)
await session.browser.initialize(browser_option)
```

### Registering a callback

Use `session.browser.register_callback` to receive call-for-user messages from the mirror:

```python
from agentbay import BrowserNotifyMessage

def on_browser_callback(msg: BrowserNotifyMessage):
    print(f"call-for-user: type={msg.type}, id={msg.id}, code={msg.code}, action={msg.action}, extra={msg.extra_params}")
    if msg.type != "call-for-user":
        return
    action = msg.action
    extra = msg.extra_params or {}
    if action == "pause":
        # Pause business flow, wait up to extra.get("max_wait_time", 60) seconds for resume
        ...
    elif action == "resume":
        # Resume business flow
        ...
    elif action == "takeover":
        # Open session resource URL for user, then call send_takeover_done(msg.id) when done
        webbrowser.open(session.resource_url)
        time.sleep(extra.get("max_wait_time", 180))
        session.browser.send_takeover_done(msg.id)
```

```python
await session.browser.register_callback(on_browser_callback)
```

### Notifying takeover done

When the user has finished the takeover task, notify the mirror so it can continue:

```python
# notify_id is msg.id from the takeover message
await session.browser.send_takeover_done(notify_id)
```

If you do not call this, the mirror will still continue after the `max_wait_time` in `extraParams`.

### Unregistering the callback

When you no longer need to receive call-for-user messages (e.g. before closing the session or switching flows), unregister the callback:

```python
await session.browser.unregister_callback()
```

## Example

The following example uses the new call-for-user interface: register a callback, handle `pause` / `resume` / `takeover` by `action` and `code`, and call `send_takeover_done` when the user finishes. For a full runnable sample, see `browser_captcha_solving.py`.

```python
import asyncio
import os
from agentbay import AsyncAgentBay as AgentBay, AsyncSession as Session, CreateSessionParams, BrowserOption, BrowserNotifyMessage
from playwright.async_api import async_playwright

takeover_notify_id = None
takeover_event = asyncio.Event()
pause_event = asyncio.Event()
resume_event = asyncio.Event()

def on_browser_callback(msg: BrowserNotifyMessage):
    print(f"🔔 call-for-user: type={msg.type}, id={msg.id}, code={msg.code}, action={msg.action}, extra={msg.extra_params}")
    if msg.type != "call-for-user":
        return
    action = msg.action
    code = msg.code
    extra = msg.extra_params or {}
    if action == "pause":
        pause_event.set()
    elif action == "resume":
        resume_event.set()
    elif action == "takeover":
        global takeover_notify_id
        takeover_notify_id = msg.id
        takeover_event.set()

async def main():
    api_key = os.getenv("AGENTBAY_API_KEY")
    agent_bay = AgentBay(api_key=api_key)
    session_result = await agent_bay.create(CreateSessionParams(image_id="browser_latest"))
    assert session_result.success and session_result.session is not None
    session = session_result.session
    takeover_url = session.resource_url

    await session.browser.register_callback(on_browser_callback)

    browser_option = BrowserOption(use_stealth=True, solve_captchas=True, call_for_user=True)
    await session.browser.initialize(browser_option)
    endpoint_url = await session.browser.get_endpoint_url()

    async with async_playwright() as p:
        browser = await p.chromium.connect_over_cdp(endpoint_url)
        page = (await browser.contexts()[0].new_page())
        await page.goto("https://www.jd.com/")

        # Wait for possible takeover (e.g. code 101/102/103)
        try:
            await asyncio.wait_for(takeover_event.wait(), timeout=5.0)
        except asyncio.TimeoutError:
            pass
        else:
            if takeover_notify_id is not None:
                import webbrowser
                webbrowser.open(takeover_url)
                await asyncio.sleep(180)  # or use extraParams["max_wait_time"]
                await session.browser.send_takeover_done(takeover_notify_id)
                print("✅ User takeover completed")

        await session.browser.unregister_callback()
    await agent_bay.delete(session)

if __name__ == "__main__":
    asyncio.run(main())
```

## Usage Tips

- **Use the callback API** — Prefer `session.browser.register_callback(on_browser_callback)` to receive call-for-user messages instead of parsing console output.
- **Branch on `action` and `code`** — Handle `pause` / `resume` / `takeover` by `action`; use `code` to distinguish captcha, login, or takeover.
- **Respect `extraParams.max_wait_time`** — For `pause` and `takeover`, wait at most this many seconds before timing out.
- **Always call `send_takeover_done(notify_id)`** after the user completes a takeover so the mirror can continue; use the `id` from the takeover message.
- **Reference examples** — See `browser_captcha_solving.py`, `browser_captcha_takeover.py`, `browser_auto_login.py`, and `browser_login_takeover.py` for full flows.

## Backward Compatibility

The legacy **wuying-call-for-user** console message format will be supported for a few more versions. New implementations should use the call-for-user callback and the `type` / `code` / `action` / `extraParams` interface above.

## 📚 Related Guides

- [CAPTCHA Resolution](captcha.md) - Automatic CAPTCHA handling
- [Session Management](../../common-features/basics/session-management.md) - Session lifecycle and configuration
- [Browser Use Overview](../README.md) - Complete browser automation features

## 🆘 Getting Help

- [GitHub Issues](https://github.com/agentbay-ai/wuying-agentbay-sdk/issues)
- [Documentation Home](../../README.md)
