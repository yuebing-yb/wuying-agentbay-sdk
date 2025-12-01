"""Integration tests for browser cookies."""

import os

import pytest
import pytest_asyncio
from playwright.async_api import async_playwright

from agentbay import AsyncAgentBay
from agentbay._common.params.session_params import CreateSessionParams
from agentbay import BrowserOption


@pytest_asyncio.fixture(scope="module")
async def agent_bay():
    """Create AsyncAgentBay instance."""
    api_key = os.environ.get("AGENTBAY_API_KEY")
    if not api_key:
        pytest.skip("AGENTBAY_API_KEY environment variable not set")
    return AsyncAgentBay(api_key=api_key)


@pytest_asyncio.fixture
async def browser_session(agent_bay):
    """Create a browser session."""
    params = CreateSessionParams(image_id="browser_latest")
    result = await agent_bay.create(params)
    assert result.success
    session = result.session
    yield session
    await session.delete()


@pytest.mark.asyncio
async def test_browser_set_cookie(browser_session):
    """Test setting cookies in browser."""
    browser = browser_session.browser
    await browser.initialize(BrowserOption())

    endpoint_url = await browser.get_endpoint_url_async()
    p = await async_playwright().start()
    playwright_browser = await p.chromium.connect_over_cdp(endpoint_url)
    context = playwright_browser.contexts[0]

    # Set cookie
    await context.add_cookies(
        [
            {
                "name": "test_cookie",
                "value": "test_value",
                "domain": ".example.com",
                "path": "/",
            }
        ]
    )

    # Get cookies
    cookies = await context.cookies()
    cookie_names = [c["name"] for c in cookies]

    assert "test_cookie" in cookie_names
    print(f"Set cookie successfully: test_cookie")

    await playwright_browser.close()
    await p.stop()


@pytest.mark.asyncio
async def test_browser_clear_cookies(browser_session):
    """Test clearing cookies."""
    browser = browser_session.browser
    await browser.initialize(BrowserOption())

    endpoint_url = await browser.get_endpoint_url_async()
    p = await async_playwright().start()
    playwright_browser = await p.chromium.connect_over_cdp(endpoint_url)
    context = playwright_browser.contexts[0]

    # Set cookie
    await context.add_cookies(
        [
            {
                "name": "temp_cookie",
                "value": "temp_value",
                "domain": ".example.com",
                "path": "/",
            }
        ]
    )

    # Clear cookies
    await context.clear_cookies()

    # Verify cleared
    cookies = await context.cookies()
    cookie_names = [c["name"] for c in cookies]

    assert "temp_cookie" not in cookie_names
    print("Cookies cleared successfully")

    await playwright_browser.close()
    await p.stop()
