"""Integration tests for browser navigation."""

import os

import pytest
import pytest_asyncio
from playwright.async_api import async_playwright

from agentbay import AsyncAgentBay
from agentbay import CreateSessionParams
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
async def test_browser_navigate_to_url(browser_session):
    """Test navigating browser to a URL."""
    browser = browser_session.browser
    await browser.initialize(BrowserOption())

    endpoint_url = await browser.get_endpoint_url_async()
    assert endpoint_url is not None

    p = await async_playwright().start()
    playwright_browser = await p.chromium.connect_over_cdp(endpoint_url)
    page = await playwright_browser.new_page()

    # Navigate to URL
    response = await page.goto("https://www.example.com")
    assert response.status == 200

    # Verify navigation
    assert "example.com" in page.url
    print(f"Navigated to: {page.url}")

    await page.close()
    await playwright_browser.close()
    await p.stop()


@pytest.mark.asyncio
async def test_browser_multiple_pages(browser_session):
    """Test opening multiple pages in browser."""
    browser = browser_session.browser
    await browser.initialize(BrowserOption())

    endpoint_url = await browser.get_endpoint_url_async()
    p = await async_playwright().start()
    playwright_browser = await p.chromium.connect_over_cdp(endpoint_url)

    # Open multiple pages
    page1 = await playwright_browser.new_page()
    page2 = await playwright_browser.new_page()
    page3 = await playwright_browser.new_page()

    await page1.goto("https://www.example.com")
    await page2.goto("https://www.example.org")
    await page3.goto("https://www.example.net")

    # Verify all pages
    assert "example.com" in page1.url
    assert "example.org" in page2.url
    assert "example.net" in page3.url
    print(f"Opened 3 pages successfully")

    await page1.close()
    await page2.close()
    await page3.close()
    await playwright_browser.close()
    await p.stop()


@pytest.mark.asyncio
async def test_browser_page_title(browser_session):
    """Test getting page title."""
    browser = browser_session.browser
    await browser.initialize(BrowserOption())

    endpoint_url = await browser.get_endpoint_url_async()
    p = await async_playwright().start()
    playwright_browser = await p.chromium.connect_over_cdp(endpoint_url)
    page = await playwright_browser.new_page()

    await page.goto("https://www.example.com")
    title = await page.title()

    assert title is not None
    assert len(title) > 0
    print(f"Page title: {title}")

    await page.close()
    await playwright_browser.close()
    await p.stop()
