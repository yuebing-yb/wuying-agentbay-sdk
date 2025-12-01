"""Integration tests for browser storage."""

import os

import pytest
import pytest_asyncio
from playwright.async_api import async_playwright

from agentbay import AsyncAgentBay
from agentbay._common.params.session_params import CreateSessionParams
from agentbay import BrowserOption


@pytest_asyncio.fixture(scope="module")
async def agent_bay():
    api_key = os.environ.get("AGENTBAY_API_KEY")
    if not api_key:
        pytest.skip("AGENTBAY_API_KEY environment variable not set")
    return AsyncAgentBay(api_key=api_key)


@pytest_asyncio.fixture
async def browser_session(agent_bay):
    params = CreateSessionParams(image_id="browser_latest")
    result = await agent_bay.create(params)
    assert result.success
    yield result.session
    await result.session.delete()


@pytest.mark.asyncio
async def test_browser_local_storage(browser_session):
    """Test browser localStorage operations."""
    browser = browser_session.browser
    await browser.initialize(BrowserOption())

    endpoint_url = await browser.get_endpoint_url_async()
    p = await async_playwright().start()
    playwright_browser = await p.chromium.connect_over_cdp(endpoint_url)
    page = await playwright_browser.new_page()

    await page.goto("https://www.example.com")

    # Set localStorage
    await page.evaluate("localStorage.setItem('test_key', 'test_value')")

    # Get localStorage
    value = await page.evaluate("localStorage.getItem('test_key')")
    assert value == "test_value"
    print("localStorage operations successful")

    await page.close()
    await playwright_browser.close()
    await p.stop()


@pytest.mark.asyncio
async def test_browser_session_storage(browser_session):
    """Test browser sessionStorage operations."""
    browser = browser_session.browser
    await browser.initialize(BrowserOption())

    endpoint_url = await browser.get_endpoint_url_async()
    p = await async_playwright().start()
    playwright_browser = await p.chromium.connect_over_cdp(endpoint_url)
    page = await playwright_browser.new_page()

    await page.goto("https://www.example.com")

    # Set sessionStorage
    await page.evaluate("sessionStorage.setItem('session_key', 'session_value')")

    # Get sessionStorage
    value = await page.evaluate("sessionStorage.getItem('session_key')")
    assert value == "session_value"
    print("sessionStorage operations successful")

    await page.close()
    await playwright_browser.close()
    await p.stop()
