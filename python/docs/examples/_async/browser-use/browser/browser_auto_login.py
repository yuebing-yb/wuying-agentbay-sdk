"""
Example: browser_auto_login.py
This example demonstrates auto login and ly.com hotel booking flow
using browser notification callback from sandbox browser.

1. Create a new browser session with AgentBay SDK
2. Use playwright to connect to AIBrowser instance through CDP protocol
3. Set auto_login and solve_captchas, then run the ly.com hotel booking flow
4. Handle call-for-user (pause/resume/takeover) during the flow.
"""

import asyncio
import os
from agentbay import AsyncAgentBay as AgentBay
from agentbay import AsyncSession as Session
from agentbay import CreateSessionParams
from agentbay import BrowserOption
from agentbay import BrowserProxy
from agentbay import BrowserNotifyMessage
from playwright.async_api import async_playwright


should_takeover = False
takeover_notify_id = None
max_autologin_detect_timeout = 5.0
max_autologin_solving_timeout = 60.0
max_takeover_timeout = 180.0
autologin_pause_event = asyncio.Event()
autologin_resume_or_takeover_event = asyncio.Event()

async def wait_for_autologin_solving(
    autologin_pause_event: asyncio.Event,
    autologin_resume_or_takeover_event: asyncio.Event,
    autologin_detect_timeout: float = 2.0,
) -> bool:
    """
    Wait for autologin solving if needed.
    
    Args:
        autologin_pause_event: Event that signals autologin pause notification
        autologin_resume_or_takeover_event: Event that signals autologin resume notification
        autologin_detect_timeout: Timeout in seconds to wait for autologin detect (pause event)
    
    Returns:
        bool
        True: autologin success, False: autologin failed or should takeover
    """
    try:
        print(f"Waiting for autologin pause event, timeout: {autologin_detect_timeout}s")
        await asyncio.wait_for(autologin_pause_event.wait(), timeout=autologin_detect_timeout)
        try:
            # Autologin pause event occurred, wait for autologin resume event
            global max_autologin_solving_timeout
            print(f"Waiting for autologin resume event, timeout: {max_autologin_solving_timeout}s")
            await asyncio.wait_for(autologin_resume_or_takeover_event.wait(), timeout=max_autologin_solving_timeout)
            global should_takeover
            if should_takeover:
                print("Autologin failed, takeover event detected")
                return False
            else:
                return True
        except asyncio.TimeoutError:
            # No resume event within timeout, proceed directly
            print("No autologin resume event detected within timeout, should takeover")
            return False
    except asyncio.TimeoutError:
        # No pause event within timeout, proceed directly
        print("No autologin pause event detected within timeout, proceeding next step")
        return True


def on_browser_callback(msg: BrowserNotifyMessage):
    print(f"🔔 Received browser callback: {msg.type}, {msg.id}, {msg.code}, {msg.message}, {msg.action}, {msg.extra_params}")
    try:
        if msg.type == "call-for-user":
            action = msg.action
            code = msg.code
            extra_params = msg.extra_params
            if action == "pause" and code == 301:
                global max_autologin_solving_timeout
                max_autologin_solving_timeout = extra_params.get("max_wait_time", 60)
                print(f"Autologin pause notification received, max wait time: {max_autologin_solving_timeout}s")
                # Signal that pause has been received
                autologin_pause_event.set()
            elif action == "resume" and code == 302:
                print("Autologin resume notification received")
                # Signal that resume has been received
                autologin_resume_or_takeover_event.set()
            elif action == "takeover":
                global should_takeover
                should_takeover = True
                global takeover_notify_id
                takeover_notify_id = msg.id
                global max_takeover_timeout
                max_takeover_timeout = extra_params.get("max_wait_time", 180)
                print(f"Autologin takeover notification received, notify_id: {takeover_notify_id}, max wait time: {max_takeover_timeout}s")
                # Signal that takeover has been received
                autologin_resume_or_takeover_event.set()
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
            auto_login=True,
            use_stealth=True,
            solve_captchas=True,
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

            # Navigate to ly.com homepage
            print("🌐 Navigating to ly.com homepage...")
            await page.goto("https://www.ly.com/")
            await asyncio.sleep(2)

            # Handle first-time login popup (if present)
            print("🔍 Checking for first-time login popup...")
            try:
                await asyncio.sleep(1)
                mask = page.locator("div.dt-mask.dt-mask-show")
                mask_count = await mask.count()
                if mask_count > 0:
                    print("✅ First-time login popup detected, closing...")
                    close_button = page.locator("img.dt-close-icon.closeDtMask")
                    close_button_count = await close_button.count()
                    if close_button_count > 0:
                        try:
                            await close_button.first.wait_for(state="visible", timeout=3000)
                            await close_button.first.click(timeout=3000)
                            print("✅ Close button clicked")
                            try:
                                await mask.wait_for(state="hidden", timeout=3000)
                                print("✅ Popup closed")
                            except Exception:
                                print("⚠️ Popup may have closed")
                        except Exception as e:
                            print(f"⚠️ Error closing popup: {e}")
                    else:
                        print("⚠️ Close button not found")
                else:
                    print("ℹ️ No first-time login popup detected, continuing")
            except Exception as e:
                print(f"⚠️ Error checking popup: {e}, continuing")

            # Click "Hotel" link
            print('🔍 Looking for "Hotel" link...')
            hotel_link = page.locator("a#top_hotel, a.hotel_at.atop_hotel")
            hotel_link_count = await hotel_link.count()
            if hotel_link_count > 0:
                await hotel_link.first.click()
                await asyncio.sleep(1)
            else:
                print('⚠️ "Hotel" link not found, continuing')

            # Enter "Beijing" in destination
            print("🔍 Looking for destination input...")
            destination_input = page.locator("input#txtHotelCity1")
            destination_count = await destination_input.count()
            if destination_count > 0:
                await destination_input.fill("北京")
            else:
                raise RuntimeError("Destination input not found")
            await asyncio.sleep(1)

            # Enter hotel name input
            print("🔍 Looking for hotel name input...")
            hotel_name_input = page.locator("input#txtHotelInfo")
            hotel_name_count = await hotel_name_input.count()
            if hotel_name_count > 0:
                await hotel_name_input.fill("北京国贸大酒店")
            else:
                raise RuntimeError("Hotel name input not found")
            await asyncio.sleep(1)

            # Press Enter to submit search
            print("⌨️ Pressing Enter to submit search...")
            await hotel_name_input.press("Enter")
            try:
                await page.wait_for_load_state("networkidle", timeout=10000)
                print("✅ Page loaded")
            except Exception:
                print("⚠️ Page load timeout, continuing")
            await asyncio.sleep(5)
            await page.evaluate("() => window.scrollBy(0, 200)")
            await asyncio.sleep(1)

            # Click "View details" button
            print('🔍 Looking for "View details" button...')
            try:
                await page.wait_for_selector(
                    'div:has-text("查看详情")', timeout=10000, state="visible"
                )
            except Exception:
                print('⚠️ Timeout waiting for "View details" button, continuing to search...')

            detail_selector = 'div.flex.items-center.justify-center.w-\\[104px\\].h-\\[40px\\]:has-text("查看详情")'
            detail_button = page.locator(detail_selector)
            detail_count = await detail_button.count()
            clicked = False
            if detail_count > 0:
                try:
                    first_button = detail_button.first
                    await first_button.wait_for(state="visible", timeout=5000)
                    await first_button.scroll_into_view_if_needed()
                    await asyncio.sleep(0.5)
                    await first_button.click(timeout=5000, force=True)
                    clicked = True
                except Exception as e:
                    print(f"❌ click failed: {e}")
            if not clicked:
                print('⚠️ "View details" button not found or not clickable')

            # Wait for autologin solving if needed
            autologin_success = await wait_for_autologin_solving(autologin_pause_event=autologin_pause_event,
                                                                autologin_resume_or_takeover_event=autologin_resume_or_takeover_event,
                                                                autologin_detect_timeout=max_autologin_detect_timeout)
            if not autologin_success:
                import webbrowser
                print("🌍 Opening browser with takeover URL...")
                webbrowser.open(takeover_url)
                await asyncio.sleep(30)
                if takeover_notify_id is not None:
                    await session.browser.send_takeover_done(takeover_notify_id)
                print("✅ User takeover completed...")

            print("🔍 Waiting for page to load...")
            await asyncio.sleep(15)
            try:
                await page.wait_for_load_state("networkidle", timeout=10000)
            except Exception:
                print("⚠️ Page load timeout, continuing")
            await page.evaluate("() => window.scrollBy(0, 2000)")
            await asyncio.sleep(5)

            # Click first "Book" button
            print('🔍 Looking for "Book" button...')
            booking_button = page.locator('div.btn-top:has-text("预订")').first
            booking_count = await booking_button.count()
            if booking_count > 0:
                try:
                    await booking_button.wait_for(state="visible", timeout=5000)
                    await booking_button.scroll_into_view_if_needed()
                    await asyncio.sleep(0.5)
                    await booking_button.click(timeout=5000, force=True)
                except Exception as e:
                    print(f'❌ Failed to click "Book" button: {e}')
            else:
                print('⚠️ "Book" button not found')

            await asyncio.sleep(3)
            await page.evaluate("() => window.scrollBy(0, 300)")

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
