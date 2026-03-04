"""
Example: browser_captcha_takeover.py
This example demonstrates how to deal with captcha automatically solving
using browser notification callback from sandbox browser.

1. Create a new browser session with AgentBay SDK
2. Use playwright to connect to AIBrowser instance through CDP protocol
3. Set solve_captchas to be False and goto jd.com website
4. We will encounter a captcha and server will notify us to takeover the task.
"""

import asyncio
import cmd
import os
import webbrowser
from re import A
from agentbay import AsyncAgentBay as AgentBay
from agentbay import AsyncSession as Session
from agentbay import CreateSessionParams
from agentbay import BrowserOption
from agentbay import BrowserNotifyMessage
from playwright.async_api import async_playwright


captcha_solved_success = False
should_takeover = False
takeover_notify_id = None
max_captcha_detect_timeout = 5.0
max_takeover_timeout = 180.0
captcha_detect_event = asyncio.Event()

def on_browser_callback(msg: BrowserNotifyMessage):
    print(f"on_browser_callback: {msg.type}, {msg.id}, {msg.code}, {msg.message}, {msg.action}, {msg.extra_params}")
    try:
        if msg.type == "call-for-user":
            action = msg.action
            extra_params = msg.extra_params
            if action == "takeover":
                global should_takeover
                should_takeover = True
                global takeover_notify_id
                takeover_notify_id = msg.id
                global max_takeover_timeout
                max_takeover_timeout = extra_params.get("max_wait_time", 180)
                print(f"Captcha takeover notification received, notify_id: {takeover_notify_id}, max wait time: {max_takeover_timeout}s")
                # Signal that takeover has been received
                captcha_detect_event.set()
    except Exception as e:
        print(f"Error handling browser callback: {e}")


async def main():
    api_key = os.getenv("AGENTBAY_API_KEY")
    agent_bay = AgentBay(api_key=api_key)
    params = CreateSessionParams(image_id="browser_latest")
    session_result = await agent_bay.create(params)
    assert session_result.success and session_result.session is not None
    session: Session = session_result.session
    takeover_url = session.resource_url

    await session.browser.register_callback(on_browser_callback)

    try:
        browser_option = BrowserOption(
            use_stealth=True,
            solve_captchas=False,
            call_for_user=True,
        )
        assert await session.browser.initialize(browser_option)
        endpoint_url = await session.browser.get_endpoint_url()
        print(f"🌐 Browser endpoint URL: {endpoint_url}")
        assert endpoint_url is not None
        await asyncio.sleep(2)
        async with async_playwright() as p:
            browser = await p.chromium.connect_over_cdp(endpoint_url)
            page = await browser.contexts[0].new_page()
            # Navigate to jd.com and trigger captcha
            print("🚀 Navigating to jd.com...")

            await page.goto('https://aq.jd.com/process/findPwd?s=1')
            print("📱 fill phone number...")
            await page.fill('input.field[placeholder="请输入账号名/邮箱/已验证手机号"]', '13000000000')
            await asyncio.sleep(2)
            
            print("🖱️ click next step button...")
            await page.click('button.btn-check-defaut.btn-xl')
            print("🔑 Captcha triggered, waiting for takeover notification...")

            # Wait for captcha takeover if needed
            await asyncio.wait_for(captcha_detect_event.wait(), timeout=max_captcha_detect_timeout)
            if should_takeover:
                print("⏰ Captcha should takeover...")
                import webbrowser
                print("🌍 Opening browser with takeover URL...")
                webbrowser.open(takeover_url)
                # wait until user task over completed or timeout
                global max_takeover_timeout
                print(f"Waiting for user task over completed or timeout, timeout: {max_takeover_timeout}s")
                await asyncio.sleep(max_takeover_timeout)
                # Send takeoverdone notify message
                if takeover_notify_id is not None:
                    await session.browser.send_takeover_done(takeover_notify_id)
                print("✅ User task over completed...")
            else:
                print("✅ Captcha solved...")
            # Take screenshot for page
            print("📸 Taking screenshot...")
            await page.screenshot(path="captcha.png")
            print("✅ Screenshot taken...")

            # Check for authentication success button
            print("🔍 Checking for authentication success...")
            try:
                success_button = await page.wait_for_selector(
                    'button.btn-check-succ:has-text("认证成功")',
                    timeout=5000
                )
                if success_button:
                    print("✅ Authentication successful - '认证成功' button found!")
                    # Take screenshot of successful state
                    await page.screenshot(path="captcha_solving.png")
                else:
                    print("⚠️ Authentication success button not found")
            except Exception as e:
                print(f"⚠️ Could not find authentication success button: {e}")

            await asyncio.sleep(10)

            await session.browser.unregister_callback()
    except Exception as e:
        print(f"❌ error: {e}")
    finally:
        print("🗑️ Deleting session")
        await agent_bay.delete(session)
if __name__ == "__main__":
    asyncio.run(main())