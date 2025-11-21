"""Integration tests for Browser Agent functionality."""
import asyncio
import os
import pytest
import pytest_asyncio
from playwright.async_api import async_playwright
from pydantic import BaseModel

from agentbay import AsyncAgentBay
from agentbay.browser import BrowserOption, BrowserFingerprint, BrowserProxy
from agentbay._async.browser_agent import ActOptions, ExtractOptions, ObserveOptions
from agentbay.session_params import CreateSessionParams


class DummySchema(BaseModel):
    """Schema for extract test."""
    title: str


def _mask_secret(secret: str, visible: int = 4) -> str:
    """Mask a secret value, keeping only the last `visible` characters."""
    if not secret:
        return ""
    if len(secret) <= visible:
        return "*" * len(secret)
    return ("*" * (len(secret) - visible)) + secret[-visible:]


def is_windows_user_agent(user_agent: str) -> bool:
    """Check if user agent indicates Windows OS."""
    if not user_agent:
        return False
    user_agent_lower = user_agent.lower()
    windows_indicators = [
        'windows nt',
        'win32',
        'win64',
        'windows',
        'wow64'
    ]
    return any(indicator in user_agent_lower for indicator in windows_indicators)


@pytest_asyncio.fixture(scope="module")
async def agent_bay():
    """Create AsyncAgentBay instance."""
    api_key = os.environ.get("AGENTBAY_API_KEY")
    if not api_key:
        pytest.skip("AGENTBAY_API_KEY environment variable not set")
    print(f"\napi_key = {_mask_secret(api_key)}")
    return AsyncAgentBay(api_key=api_key)


@pytest_asyncio.fixture
async def browser_session(agent_bay):
    """Create a session with browser_latest image."""
    print("\nCreating a new session for browser agent testing...")
    session_param = CreateSessionParams(image_id="browser_latest")
    result = await agent_bay.create(session_param)
    assert result.success, f"Failed to create session: {result.error_message}"
    session = result.session
    print(f"Session created with ID: {session.session_id}")
    yield session
    print("\nCleaning up: Deleting the session...")
    await session.delete()


@pytest.mark.asyncio
async def test_initialize_browser(browser_session):
    """Test basic browser initialization."""
    browser = browser_session.browser
    assert browser is not None

    init_result = await browser.initialize(BrowserOption())
    assert init_result is True

    # FIX: Use get_endpoint_url_async() instead of get_endpoint_url()
    endpoint_url = await browser.get_endpoint_url_async()
    print(f"endpoint_url = {endpoint_url}")
    assert endpoint_url is not None

    await asyncio.sleep(10)

    p = await async_playwright().start()
    playwright_browser = await p.chromium.connect_over_cdp(endpoint_url)
    assert playwright_browser is not None

    page = await playwright_browser.new_page()
    await page.goto("http://www.baidu.com")
    title = await page.title()
    print(f"page.title() = {title}")

    assert title is not None
    await page.close()
    await playwright_browser.close()
    await p.stop()


@pytest.mark.asyncio
async def test_initialize_browser_with_fingerprint(browser_session):
    """Test browser initialization with fingerprint."""
    browser = browser_session.browser
    assert browser is not None

    option = BrowserOption(
        use_stealth=True,
        fingerprint=BrowserFingerprint(
            devices=["desktop"],
            operating_systems=["windows"],
            locales=["zh-CN"],
        )
    )
    init_result = await browser.initialize(option)
    assert init_result is True

    # FIX: Use get_endpoint_url_async() instead of get_endpoint_url()
    endpoint_url = await browser.get_endpoint_url_async()
    print(f"endpoint_url = {endpoint_url}")
    assert endpoint_url is not None

    await asyncio.sleep(10)

    p = await async_playwright().start()
    playwright_browser = await p.chromium.connect_over_cdp(endpoint_url)
    assert playwright_browser is not None
    default_context = playwright_browser.contexts[0]
    assert default_context is not None

    page = await default_context.new_page()
    await page.goto("https://httpbin.org/user-agent", timeout=60000)
    response = await page.evaluate("() => JSON.parse(document.body.textContent)")
    user_agent = response["user-agent"]
    print(f"user_agent = {user_agent}")
    assert user_agent is not None
    is_windows = is_windows_user_agent(user_agent)
    assert is_windows is True

    await page.close()
    await playwright_browser.close()
    await p.stop()


@pytest.mark.asyncio
async def test_act_success(browser_session):
    """Test browser agent act operation."""
    browser = browser_session.browser
    assert browser is not None

    init_result = await browser.initialize(BrowserOption())
    assert init_result is True

    # FIX: Use get_endpoint_url_async() instead of get_endpoint_url()
    endpoint_url = await browser.get_endpoint_url_async()
    print(f"endpoint_url = {endpoint_url}")
    assert endpoint_url is not None

    p = await async_playwright().start()
    playwright_browser = await p.chromium.connect_over_cdp(endpoint_url)
    assert playwright_browser is not None

    page = await playwright_browser.new_page()
    await page.goto("http://www.baidu.com")
    title = await page.title()
    assert title is not None

    result = await browser.agent.act(ActOptions(action="Click search button"), page)
    print(f"result = {result}")

    assert result.success is True
    assert hasattr(result, 'action')

    await page.close()
    await playwright_browser.close()
    await p.stop()


@pytest.mark.asyncio
async def test_observe_success(browser_session):
    """Test browser agent observe operation."""
    browser = browser_session.browser
    assert browser is not None

    init_result = await browser.initialize(BrowserOption())
    assert init_result is True

    # FIX: Use get_endpoint_url_async() instead of get_endpoint_url()
    endpoint_url = await browser.get_endpoint_url_async()
    print(f"endpoint_url = {endpoint_url}")
    assert endpoint_url is not None

    p = await async_playwright().start()
    playwright_browser = await p.chromium.connect_over_cdp(endpoint_url)
    assert playwright_browser is not None

    page = await playwright_browser.new_page()
    await page.goto("http://www.baidu.com")
    title = await page.title()
    assert title is not None

    result, observe_results = await browser.agent.observe(
        ObserveOptions(instruction="Find the search button"),
        page
    )
    print(f"result = {result}")
    print(f"observe_results = {observe_results}")

    assert result is True
    assert len(observe_results) > 0
    assert hasattr(observe_results[0], 'description')

    await page.close()
    await playwright_browser.close()
    await p.stop()


@pytest.mark.asyncio
async def test_extract_success(browser_session):
    """Test browser agent extract operation."""
    browser = browser_session.browser
    assert browser is not None

    init_result = await browser.initialize(BrowserOption())
    assert init_result is True

    # FIX: Use get_endpoint_url_async() instead of get_endpoint_url()
    endpoint_url = await browser.get_endpoint_url_async()
    print(f"endpoint_url = {endpoint_url}")
    assert endpoint_url is not None

    p = await async_playwright().start()
    playwright_browser = await p.chromium.connect_over_cdp(endpoint_url)
    assert playwright_browser is not None

    page = await playwright_browser.new_page()
    await page.goto("http://www.baidu.com")
    title = await page.title()
    assert title is not None

    result, obj = await browser.agent.extract(
        ExtractOptions(instruction="Extract the title", schema=DummySchema),
        page
    )
    print(f"result = {result}")
    print(f"obj = {obj}")
    assert result is True
    assert obj is not None
    assert hasattr(obj, 'title')

    await page.close()
    await playwright_browser.close()
    await p.stop()


@pytest.mark.asyncio
async def test_restricted_proxy_ip_comparison(agent_bay):
    """Test restricted proxy by comparing IP addresses before and after proxy setup."""
    print("\n=== test restricted proxy IP comparison ===")

    # Phase 1: Initialize browser without proxy and get original IP
    print("phase 1: initialize browser without proxy...")
    session_param1 = CreateSessionParams(image_id="browser_latest")
    result1 = await agent_bay.create(session_param1)
    assert result1.success
    session1 = result1.session

    browser1 = session1.browser
    no_proxy_option = BrowserOption()
    init_result1 = await browser1.initialize(no_proxy_option)
    assert init_result1 is True

    # FIX: Use get_endpoint_url_async() instead of get_endpoint_url()
    endpoint_url1 = await browser1.get_endpoint_url_async()
    print(f"endpoint_url = {endpoint_url1}")
    assert endpoint_url1 is not None

    await asyncio.sleep(5)

    # Get original IP
    p1 = await async_playwright().start()
    playwright_browser1 = await p1.chromium.connect_over_cdp(endpoint_url1)
    assert playwright_browser1 is not None

    context1 = playwright_browser1.contexts[0]
    page1 = await context1.new_page()
    await page1.goto("https://httpbin.org/ip")

    try:
        response = await page1.evaluate("() => JSON.parse(document.body.textContent)")
        original_ip = response.get("origin", "").strip()
        print(f"original IP: {original_ip}")
    except Exception as e:
        print(f"get original IP failed: {e}")
        original_ip = None

    await page1.close()
    await playwright_browser1.close()
    await p1.stop()

    # Delete current session
    await session1.delete()

    await asyncio.sleep(3)

    # Phase 2: Create new session with restricted proxy
    print("phase 2: create new session with restricted proxy...")
    restricted_proxy = BrowserProxy(
        proxy_type="wuying",
        strategy="restricted"
    )

    proxy_option = BrowserOption(proxies=[restricted_proxy])
    session_param2 = CreateSessionParams(image_id="browser_latest")
    result2 = await agent_bay.create(session_param2)
    assert result2.success
    session2 = result2.session

    browser2 = session2.browser
    init_result2 = await browser2.initialize(proxy_option)
    assert init_result2 is True

    # Verify proxy configuration
    saved_option = browser2.get_option()
    assert saved_option.proxies is not None
    assert len(saved_option.proxies) == 1
    assert saved_option.proxies[0].type == "wuying"
    assert saved_option.proxies[0].strategy == "restricted"
    print("✓ proxy config validation success")

    # FIX: Use get_endpoint_url_async() instead of get_endpoint_url()
    endpoint_url2 = await browser2.get_endpoint_url_async()
    print(f"proxy mode endpoint_url = {endpoint_url2}")

    await asyncio.sleep(5)

    # Get proxy IP
    p2 = await async_playwright().start()
    playwright_browser2 = await p2.chromium.connect_over_cdp(endpoint_url2)
    assert playwright_browser2 is not None

    context2 = playwright_browser2.contexts[0]
    page2 = await context2.new_page()
    await page2.goto("https://httpbin.org/ip")

    try:
        response2 = await page2.evaluate("() => JSON.parse(document.body.textContent)")
        proxy_ip = response2.get("origin", "").strip()
        print(f"proxy IP: {proxy_ip}")
    except Exception as e:
        print(f"get proxy IP failed: {e}")
        proxy_ip = None

    await page2.close()
    await playwright_browser2.close()
    await p2.stop()

    # Clean up session2
    await session2.delete()

    # Compare IPs
    if original_ip and proxy_ip:
        if original_ip != proxy_ip:
            print(f"✅ static proxy test success! IP changed: {original_ip} -> {proxy_ip}")
        else:
            print(f"⚠️  warning: proxy IP is the same, maybe proxy not working: {original_ip}")
            pytest.fail("proxy IP is the same, maybe proxy not working")
    else:
        print("⚠️  failed to compare IP, but proxy config applied")

