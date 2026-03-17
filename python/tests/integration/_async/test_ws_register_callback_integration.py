# -*- coding: utf-8 -*-
import asyncio
import os

import pytest

from agentbay import AsyncAgentBay, BrowserOption, CreateSessionParams


@pytest.mark.integration
@pytest.mark.asyncio
class TestWsRegisterCallbackIntegration:
    @pytest.fixture
    def agentbay(self):
        api_key = os.getenv("AGENTBAY_API_KEY")
        if not api_key:
            pytest.skip("AGENTBAY_API_KEY environment variable not set")
        return AsyncAgentBay(api_key=api_key)

    async def test_ws_register_callback_should_receive_captcha_push(self, agentbay) -> None:
        playwright = pytest.importorskip("playwright.async_api")

        created = await agentbay.create(CreateSessionParams())
        assert created.success is True, created.error_message
        assert created.session is not None
        session = created.session

        ws_client = None
        try:
            ws_client = await session._get_ws_client()
            push_signal = asyncio.Event()
            received: list[dict] = []

            def on_push(payload: dict) -> None:
                received.append(payload)
                push_signal.set()

            ws_client.register_callback("wuying_cdp_mcp_server", on_push)
            await ws_client.connect()

            browser_option = BrowserOption(use_stealth=True, solve_captchas=True)
            assert await session.browser.initialize(browser_option)
            endpoint_url = await session.browser.get_endpoint_url()
            assert endpoint_url

            async with playwright.async_playwright() as p:
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

                await asyncio.wait_for(push_signal.wait(), timeout=180.0)

            assert received, "Expected at least 1 push callback invocation"
            first = received[0]
            assert first.get("target") == "wuying_cdp_mcp_server"
            data = first.get("data")
            assert isinstance(data, dict)
            assert data.get("code") in (201, 202), f"unexpected push data: {data!r}"
        finally:
            if ws_client is not None:
                try:
                    await ws_client.close()
                except Exception:
                    pass
            await session.delete()

