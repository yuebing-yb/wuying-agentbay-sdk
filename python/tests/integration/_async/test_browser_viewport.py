"""Integration tests for browser viewport."""

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
async def test_browser_viewport_size(browser_session):
    """Test setting browser viewport size."""
    browser = browser_session.browser
    await browser.initialize(BrowserOption())

    endpoint_url = await browser.get_endpoint_url_async()
    p = await async_playwright().start()
    playwright_browser = await p.chromium.connect_over_cdp(endpoint_url)
    page = await playwright_browser.new_page()

    # Set viewport
    await page.set_viewport_size({"width": 1280, "height": 720})

    # Get viewport
    viewport = page.viewport_size
    assert viewport["width"] == 1280
    assert viewport["height"] == 720
    print(f"Viewport set to: {viewport}")

    await page.close()
    await playwright_browser.close()
    await p.stop()


@pytest.mark.asyncio
async def test_browser_mobile_viewport(browser_session):
    """Test mobile viewport."""
    browser = browser_session.browser
    await browser.initialize(BrowserOption())

    endpoint_url = await browser.get_endpoint_url_async()
    p = await async_playwright().start()
    playwright_browser = await p.chromium.connect_over_cdp(endpoint_url)
    page = await playwright_browser.new_page()

    # Set mobile viewport
    await page.set_viewport_size({"width": 375, "height": 667})

    viewport = page.viewport_size
    assert viewport["width"] == 375
    assert viewport["height"] == 667
    print(f"Mobile viewport: {viewport}")

    await page.close()
    await playwright_browser.close()
    await p.stop()
