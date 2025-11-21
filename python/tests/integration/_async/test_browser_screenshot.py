"""Integration tests for browser screenshots."""
import os
import pytest
import pytest_asyncio
from playwright.async_api import async_playwright

from agentbay import AsyncAgentBay
from agentbay.browser import BrowserOption
from agentbay.session_params import CreateSessionParams


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
async def test_browser_take_screenshot(browser_session):
    """Test taking a screenshot."""
    browser = browser_session.browser
    await browser.initialize(BrowserOption())
    
    endpoint_url = await browser.get_endpoint_url_async()
    p = await async_playwright().start()
    playwright_browser = await p.chromium.connect_over_cdp(endpoint_url)
    page = await playwright_browser.new_page()
    
    await page.goto("https://www.example.com")
    screenshot = await page.screenshot()
    
    assert screenshot is not None
    assert len(screenshot) > 0
    print(f"Screenshot size: {len(screenshot)} bytes")
    
    await page.close()
    await playwright_browser.close()
    await p.stop()


@pytest.mark.asyncio
async def test_browser_screenshot_fullpage(browser_session):
    """Test taking a full page screenshot."""
    browser = browser_session.browser
    await browser.initialize(BrowserOption())
    
    endpoint_url = await browser.get_endpoint_url_async()
    p = await async_playwright().start()
    playwright_browser = await p.chromium.connect_over_cdp(endpoint_url)
    page = await playwright_browser.new_page()
    
    await page.goto("https://www.example.com")
    screenshot = await page.screenshot(full_page=True)
    
    assert screenshot is not None
    print(f"Full page screenshot size: {len(screenshot)} bytes")
    
    await page.close()
    await playwright_browser.close()
    await p.stop()


