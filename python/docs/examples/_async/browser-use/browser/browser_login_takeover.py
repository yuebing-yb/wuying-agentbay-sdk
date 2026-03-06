"""
Example: browser_login_takeover.py
This example demonstrates the call-for-user (login takeover) flow
on JD.com using browser notification callback from sandbox browser.

1. Create a new browser session with AgentBay SDK
2. Use playwright to connect to AIBrowser instance through CDP protocol
3. Set auto_login, solve_captchas and call_for_user, then run the JD search flow
4. Handle call-for-user (pause/resume/takeover) during login/captcha
"""

import asyncio
import os
import webbrowser
from agentbay import AsyncAgentBay as AgentBay
from agentbay import AsyncSession as Session
from agentbay import CreateSessionParams
from agentbay import BrowserOption
from agentbay import BrowserProxy
from agentbay import BrowserNotifyMessage
from playwright.async_api import async_playwright


should_takeover = False
takeover_notify_id = None
max_login_detect_timeout = 5.0
max_login_takeover_timeout = 180.0
takeover_event = asyncio.Event()


def on_browser_callback(msg: BrowserNotifyMessage):
    print(f"on_browser_callback: {msg.type}, {msg.id}, {msg.code}, {msg.message}, {msg.action}, {msg.extra_params}")
    try:
        if msg.type == "call-for-user":
            action = msg.action
            code = msg.code
            extra_params = msg.extra_params
            if action == "takeover" and code == 102:
                global should_takeover
                should_takeover = True
                global takeover_notify_id
                takeover_notify_id = msg.id
                global max_login_takeover_timeout
                max_login_takeover_timeout = extra_params.get("max_wait_time", 180)
                print(f"Call-for-user takeover received, notify_id: {takeover_notify_id}, max wait time: {max_login_takeover_timeout}s")
                # Signal that takeover has been received
                takeover_event.set()
    except Exception as e:
        print(f"Error handling browser callback: {e}")


async def wait_and_do_takeover_if_needed(session: Session, takeover_url: str):
    """Wait for takeover event, then open browser and send takeover done if should_takeover."""
    # Wait for login takeover if needed
    try:
        await asyncio.wait_for(takeover_event.wait(), timeout=max_login_detect_timeout)
    except asyncio.TimeoutError:
        print("ℹ️ No takeover event within timeout, proceeding...")
        return
    if should_takeover:
        print("⏰ Login should takeover...")
        import webbrowser
        webbrowser.open(takeover_url)
        print(f"Waiting for user takeover completed or timeout, timeout: {max_login_takeover_timeout}s")
        await asyncio.sleep(max_login_takeover_timeout)
        if takeover_notify_id is not None:
            await session.browser.send_takeover_done(takeover_notify_id)
        print("✅ User takeover completed...")
    else:
        print("ℹ️ No takeover event within timeout, proceeding...")


async def run_jd_homepage_flow(page):
    """
    JD homepage flow: close login popup if needed, search, wait for results.
    """
    # Close login popup if present
    print("🔍 Checking for login popup...")
    try:
        close_button = page.locator("#login2025-dialog-close")
        await close_button.wait_for(state="visible", timeout=2000)
        await close_button.click(timeout=3000)
        print("✅ Login popup closed")
        await asyncio.sleep(0.5)
    except Exception:
        # Popup not present, continue
        pass

    # Search (ref: login_jingdong.test.js)
    print("🔍 Entering search keyword...")
    search_input = page.locator("input#key")
    await search_input.fill("iphone 17价格京东自营")
    await page.locator('button[aria-label="搜索"]').click()

    # Wait for search results to load
    print("⏳ Waiting for search results to load...")
    try:
        await page.wait_for_load_state("networkidle", timeout=15000)
        print("✅ Search results loaded")
    except Exception:
        pass
    await asyncio.sleep(2)


async def run_post_login_flow(page):
    """
    Post-login flow: scroll, add to cart, open cart. Ref: login_jingdong.js
    """
    print("📜 Scrolling down 500px so products are visible...")
    await page.evaluate("() => window.scrollBy(0, 500)")
    await asyncio.sleep(1)

    try:
        first_card = page.locator("div.plugin_goodsCardWrapper").first
        await first_card.wait_for(state="visible", timeout=8000)
        await first_card.scroll_into_view_if_needed()
        await first_card.locator("button._addCart_d0rf6_71").click(timeout=5000, force=True)
        print("✅ Clicked add to cart")
        await asyncio.sleep(3)
        cart_link = page.locator("li#Cart a.Cart").first
        await cart_link.scroll_into_view_if_needed()
        await cart_link.click(timeout=5000, force=True)
        print("✅ Clicked cart")
        await asyncio.sleep(2)
    except Exception as e:
        print(f"⚠️ Add to cart or open cart failed: {e}")


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
            auto_login=False,
            call_for_user=True,
            proxies=[BrowserProxy(proxy_type="wuying", strategy="restricted")],
        )
        assert await session.browser.initialize(browser_option)
        endpoint_url = await session.browser.get_endpoint_url()
        print(f"🌐 Browser endpoint URL: {endpoint_url}")
        assert endpoint_url is not None
        await asyncio.sleep(2)

        async with async_playwright() as p:
            browser = await p.chromium.connect_over_cdp(endpoint_url)
            context = browser.contexts[0] if browser.contexts else await browser.new_context()
            page = await context.new_page()

            # Navigate to JD homepage
            print("🌐 Navigating to JD homepage...")
            await page.goto("https://www.jd.com/")
            await asyncio.sleep(2)

            # Check current URL to decide which flow to run
            current_url = page.url

            if "passport.jd.com" in current_url:
                # Already on login page, wait for takeover
                print("🔐 Detected passport.jd.com login page, waiting for takeover...")
                await asyncio.sleep(5)
                await wait_and_do_takeover_if_needed(session, takeover_url)

                await run_jd_homepage_flow(page)
            else:
                await asyncio.sleep(10)
                # On homepage, run homepage flow
                await run_jd_homepage_flow(page)

                # After homepage flow, wait for possible takeover (short timeout)
                print("⏳ Waiting for takeover event (user may log in manually)...")
                await wait_and_do_takeover_if_needed(session, takeover_url)

            # Run post-login flow
            await run_post_login_flow(page)

            print("✅ Test completed")
            await asyncio.sleep(10)

            await session.browser.unregister_callback()
    except Exception as e:
        print(f"❌ error: {e}")
    finally:
        print("🗑️ Deleting session")
        await agent_bay.delete(session)


if __name__ == "__main__":
    asyncio.run(main())
