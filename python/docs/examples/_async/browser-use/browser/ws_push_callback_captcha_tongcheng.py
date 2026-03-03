"""
Example demonstrating how to receive backend push notifications via Session WS.

This example shows how to:
- Create a browser session
- Connect to the session WS endpoint
- Register a push callback for target: wuying_cdp_mcp_server
- Trigger a captcha flow on Tongcheng and wait for backend push
"""

import asyncio
import os

from playwright.async_api import async_playwright

from agentbay import AsyncAgentBay, BrowserOption, CreateSessionParams


async def main() -> None:
    api_key = os.getenv("AGENTBAY_API_KEY")
    if not api_key:
        raise RuntimeError("AGENTBAY_API_KEY environment variable not set")

    image_id = os.getenv("AGENTBAY_WS_IMAGE_ID") or "imgc-0ab5ta4kuo0x3pa70"
    agent_bay = AsyncAgentBay(api_key=api_key)
    created = await agent_bay.create(CreateSessionParams(image_id=image_id))
    if not created.success or created.session is None:
        raise RuntimeError(f"Failed to create session: {created.error_message}")
    session = created.session

    ws_client = None
    try:
        ws_client = await session._get_ws_client()
        push_signal = asyncio.Event()

        def on_push(payload: dict) -> None:
            print(f"WS PUSH: {payload}")
            push_signal.set()

        ws_client.register_callback("wuying_cdp_mcp_server", on_push)
        await ws_client.connect()

        browser_option = BrowserOption(use_stealth=True, solve_captchas=True)
        ok = await session.browser.initialize(browser_option)
        if not ok:
            raise RuntimeError("Failed to initialize browser")

        endpoint_url = await session.browser.get_endpoint_url()
        if not endpoint_url:
            raise RuntimeError("Empty browser endpoint URL")

        async with async_playwright() as p:
            browser = await p.chromium.connect_over_cdp(endpoint_url)
            page = await browser.contexts[0].new_page()
            await page.goto(
                "https://passport.ly.com/Passport/GetPassword",
                wait_until="domcontentloaded",
            )
            input_element = await page.wait_for_selector("#name_in", timeout=10000)
            await input_element.click()
            await input_element.fill("")
            await input_element.type("13000000000")
            await page.wait_for_timeout(1000)
            await page.click("#next_step1")

            print("Waiting for backend push...")
            await asyncio.wait_for(push_signal.wait(), timeout=180.0)
            print("Received backend push.")
    finally:
        if ws_client is not None:
            try:
                await ws_client.close()
            except Exception:
                pass
        await session.delete()


if __name__ == "__main__":
    asyncio.run(main())

