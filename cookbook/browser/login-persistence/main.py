"""
Browser Login Persistence Example

Demonstrates how to use BrowserContext to persist browser login state
(cookies, localStorage, etc.) across multiple cloud sessions.

Steps:
1. Create a persistent Context for browser data
2. First session: set test cookies via Playwright
3. Delete session with sync_context=True to save browser data
4. Second session: verify cookies persisted automatically
"""

import asyncio
import os
import sys
import time

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "../../../python"))

from agentbay import AsyncAgentBay, CreateSessionParams, BrowserContext
from agentbay import BrowserOption
from playwright.async_api import async_playwright


CONTEXT_NAME = f"browser-login-demo-{int(time.time())}"
TEST_URL = "https://www.aliyun.com"
TEST_DOMAIN = "aliyun.com"

TEST_COOKIES = [
    {
        "name": "demo_session_token",
        "value": "persist_test_abc123",
        "domain": TEST_DOMAIN,
        "path": "/",
        "httpOnly": False,
        "secure": False,
        "expires": int(time.time()) + 3600,
    },
    {
        "name": "demo_user_id",
        "value": "user_42",
        "domain": TEST_DOMAIN,
        "path": "/",
        "httpOnly": False,
        "secure": False,
        "expires": int(time.time()) + 3600,
    },
]


async def main():
    api_key = os.environ.get("AGENTBAY_API_KEY")
    if not api_key:
        print("Error: AGENTBAY_API_KEY environment variable not set")
        return

    agent_bay = AsyncAgentBay(api_key)
    print("AgentBay client initialized\n")

    context = None

    try:
        # ── Step 1: Create a persistent Context ──────────────────────────
        print("=" * 60)
        print("Step 1: Create a persistent Context for browser data")
        print("=" * 60)

        ctx_result = await agent_bay.context.get(CONTEXT_NAME, create=True)
        if not ctx_result.success or not ctx_result.context:
            print(f"Failed to create context: {ctx_result.error_message}")
            return

        context = ctx_result.context
        print(f"Context created: {context.id} (name: {CONTEXT_NAME})\n")

        browser_context = BrowserContext(context.id, auto_upload=True)
        params = CreateSessionParams(
            image_id="browser_latest",
            browser_context=browser_context,
        )

        # ── Step 2: First session — set cookies ─────────────────────────
        print("=" * 60)
        print("Step 2: First session — set test cookies")
        print("=" * 60)

        result1 = await agent_bay.create(params)
        if not result1.success or not result1.session:
            print(f"Failed to create session 1: {result1.error_message}")
            return

        session1 = result1.session
        print(f"Session 1 created: {session1.session_id}")

        init_ok = await session1.browser.initialize(BrowserOption())
        if not init_ok:
            print("Failed to initialize browser")
            return
        print("Browser initialized")

        endpoint_url = await session1.browser.get_endpoint_url()
        if not endpoint_url:
            print("Failed to get browser endpoint URL")
            return

        async with async_playwright() as p:
            browser = await p.chromium.connect_over_cdp(endpoint_url)
            ctx_pw = browser.contexts[0] if browser.contexts else await browser.new_context()
            page = await ctx_pw.new_page()

            await page.goto(TEST_URL)
            print(f"Navigated to {TEST_URL}")
            await page.wait_for_timeout(2000)

            await ctx_pw.add_cookies(TEST_COOKIES)  # type: ignore
            print(f"Set {len(TEST_COOKIES)} test cookies:")
            for c in TEST_COOKIES:
                print(f"  - {c['name']} = {c['value']}")

            cookies = await ctx_pw.cookies()
            cookie_names = {c.get("name", "") for c in cookies}
            for tc in TEST_COOKIES:
                status = "OK" if tc["name"] in cookie_names else "MISSING"
                print(f"  [{status}] Cookie '{tc['name']}' verified in browser")

            cdp_session = await browser.new_browser_cdp_session()
            await cdp_session.send("Browser.close")
            await asyncio.sleep(2)
            await browser.close()

        print()

        # ── Step 3: Delete session 1 with context sync ───────────────────
        print("=" * 60)
        print("Step 3: Delete session — save browser data to Context")
        print("=" * 60)

        delete_result = await agent_bay.delete(session1, sync_context=True)
        if not delete_result.success:
            print(f"Failed to delete session 1: {delete_result.error_message}")
            return
        print("Session 1 deleted with sync_context=True")
        print("Waiting for context sync to complete...")
        await asyncio.sleep(3)
        print()

        # ── Step 4: Second session — verify persistence ──────────────────
        print("=" * 60)
        print("Step 4: Second session — verify cookie persistence")
        print("=" * 60)

        result2 = await agent_bay.create(params)
        if not result2.success or not result2.session:
            print(f"Failed to create session 2: {result2.error_message}")
            return

        session2 = result2.session
        print(f"Session 2 created: {session2.session_id}")

        init_ok2 = await session2.browser.initialize(BrowserOption())
        if not init_ok2:
            print("Failed to initialize browser in session 2")
            return
        print("Browser initialized")

        endpoint_url2 = await session2.browser.get_endpoint_url()
        if not endpoint_url2:
            print("Failed to get endpoint URL for session 2")
            return

        async with async_playwright() as p:
            browser2 = await p.chromium.connect_over_cdp(endpoint_url2)
            ctx2 = browser2.contexts[0] if browser2.contexts else await browser2.new_context()

            cookies2 = await ctx2.cookies()
            cookie_dict2 = {c.get("name", ""): c.get("value", "") for c in cookies2}

            print(f"\nTotal cookies in session 2: {len(cookies2)}")
            print("Checking test cookie persistence:")

            all_persisted = True
            for tc in TEST_COOKIES:
                name = tc["name"]
                expected = tc["value"]
                actual = cookie_dict2.get(name)
                if actual == expected:
                    print(f"  [OK] '{name}' persisted: {actual}")
                elif actual is not None:
                    print(f"  [MISMATCH] '{name}': expected={expected}, actual={actual}")
                    all_persisted = False
                else:
                    print(f"  [MISSING] '{name}' NOT found in session 2")
                    all_persisted = False

            await browser2.close()

        print()
        if all_persisted:
            print("All cookies persisted across sessions!")
        else:
            print("WARNING: Some cookies did not persist.")

        print("\nCleaning up session 2...")
        await agent_bay.delete(session2)
        print("Session 2 deleted.")

    except Exception as e:
        print(f"\nError: {e}")
        raise

    finally:
        if context:
            try:
                await agent_bay.context.delete(context)
                print(f"Context '{CONTEXT_NAME}' deleted.")
            except Exception as e:
                print(f"Warning: Failed to delete context: {e}")

    print("\nExample completed.")


if __name__ == "__main__":
    asyncio.run(main())
