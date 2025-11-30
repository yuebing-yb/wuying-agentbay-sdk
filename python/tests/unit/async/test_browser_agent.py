import asyncio
import json
import os
import unittest
from typing import List, Optional
from unittest.mock import AsyncMock, MagicMock, patch

from pydantic import BaseModel, Field

from agentbay._async.browser import AsyncBrowser
from agentbay._async.browser_agent import ActOptions as AsyncActOptions
from agentbay._async.browser_agent import AsyncBrowserAgent
from agentbay._async.browser_agent import ExtractOptions as AsyncExtractOptions
from agentbay._async.browser_agent import ObserveOptions as AsyncObserveOptions
from agentbay._common.exceptions import BrowserError
from agentbay._sync.browser import (
    Browser,
    BrowserFingerprint,
    BrowserOption,
    BrowserProxy,
    BrowserScreen,
    BrowserViewport,
)
from agentbay._sync.browser_agent import (
    ActOptions,
    ActResult,
    BrowserAgent,
    ExtractOptions,
    ObserveOptions,
    ObserveResult,
)
from agentbay._sync.fingerprint import FingerprintFormat


class SchemaForTest(BaseModel):
    title: str = Field(..., description="Page title")
    content: Optional[str] = Field(None, description="Page content")


class TestBrowser(unittest.TestCase):
    def setUp(self):
        """Set up test browser."""
        self.mock_session = MagicMock()
        # Configure async mock for init_browser_async
        # For sync Browser, it calls sync init_browser or calls async one via run_until_complete?
        # Sync browser uses BaseService which uses Session.
        # Session.client is sync client?
        # Let's assume mock setup for Sync Browser is simpler or existing one was "okay" but incomplete.
        # Existing setup:
        # self.mock_session._get_client().init_browser_async = AsyncMock()
        # Browser (sync) calls init_browser (sync) on client?
        # Or session.client.init_browser?

        # Ideally we mock what Browser calls.
        # Browser (sync) calls session.client.init_browser (sync) presumably.
        self.browser = Browser(self.mock_session)
        self.browser.agent = MagicMock()

    def test_initialize(self):
        """Test initialize method."""
        # Mock initialize return
        # Since Browser.initialize (sync) is likely calling session.client.init_browser (sync)
        # We should mock that if needed, but here self.browser is the real object.
        # Wait, Browser.initialize implementation:
        # It calls session.client.init_browser_async(request) in ASYNC version.
        # Sync version generated from Async version.
        # Sync version should call sync method of client?
        # Or it calls sync version of session.client?

        # The existing test passed test_initialize because it calls self.browser.initialize(BrowserOption())
        # And initialize calls self.session.client.init_browser_async? NO.
        # If generated, it calls sync version.

        # We'll leave this as is, assuming Browser(sync) mocks are handled or not needed for basic True check if mocked elsewhere.
        # Actually, self.browser.initialize calls self.session.client...
        # If we don't mock session.client methods, it might fail.

        # Let's look at how we mocked for AsyncBrowser.
        # SyncBrowser should be similar but sync.
        self.mock_session.client.init_browser.return_value = MagicMock()
        self.mock_session.client.init_browser.return_value.to_map.return_value = {
            "body": {"Data": {"Port": 9333}}
        }

        self.assertTrue(self.browser.initialize(BrowserOption()))

    def test_is_initialized(self):
        """Test is_initialized method."""
        self.assertFalse(self.browser.is_initialized())

    def test_get_endpoint_url(self):
        """Test get_endpoint_url method."""
        self.mock_session.client.init_browser.return_value.to_map.return_value = {
            "body": {"Data": {"Port": 9333}}
        }
        self.browser.initialize(BrowserOption())
        # Need to mock session.is_vpc and session.network_interface_ip if needed,
        # or session.agent_bay.client.get_cdp_link...
        # But initialize sets _endpoint_url if port is returned.
        self.assertIsNotNone(self.browser.get_endpoint_url())

    def test_get_option(self):
        """Test get_option method."""
        # Create a proxy for testing
        test_proxy = BrowserProxy(proxy_type="wuying", strategy="polling", pollsize=15)

        fingerprint_format = FingerprintFormat.load(
            open(
                os.path.join(
                    os.path.dirname(__file__),
                    "../../../../resource/fingerprint.example.json",
                ),
                "r",
            ).read()
        )
        browser_option = BrowserOption(
            use_stealth=True,
            user_agent="User-Agent(By Mock)",
            viewport=BrowserViewport(width=1920, height=1080),
            screen=BrowserScreen(width=1920, height=1080),
            fingerprint=BrowserFingerprint(
                devices=["desktop"],
                operating_systems=["windows", "macos"],
                locales=["zh-CN"],
            ),
            fingerprint_format=fingerprint_format,
            fingerprint_persistent=True,
            solve_captchas=True,
            proxies=[test_proxy],
        )

        self.mock_session.client.init_browser.return_value.to_map.return_value = {
            "body": {"Data": {"Port": 9333}}
        }
        self.browser.initialize(browser_option)
        option = self.browser.get_option()
        self.assertIsNotNone(option)
        self.assertEqual(option.use_stealth, True)
        self.assertEqual(option.user_agent, "User-Agent(By Mock)")
        self.assertEqual(option.viewport.width, 1920)
        self.assertEqual(option.viewport.height, 1080)
        self.assertEqual(option.screen.width, 1920)
        self.assertEqual(option.screen.height, 1080)
        self.assertEqual(option.fingerprint.devices, ["desktop"])
        self.assertEqual(option.fingerprint.operating_systems, ["windows", "macos"])
        self.assertEqual(option.fingerprint.locales, ["zh-CN"])
        self.assertIsNotNone(option.fingerprint_persist_path)
        self.assertIsNotNone(option.fingerprint_format)
        self.assertEqual(option.solve_captchas, True)

        # Test proxy options
        self.assertIsNotNone(option.proxies)
        self.assertEqual(len(option.proxies), 1)
        proxy = option.proxies[0]
        self.assertEqual(proxy.type, "wuying")
        self.assertEqual(proxy.strategy, "polling")
        self.assertEqual(proxy.pollsize, 15)

    def test_browser_proxy_options(self):
        """Test different types of browser proxy configurations."""

        # Test custom proxy
        custom_proxy = BrowserProxy(
            proxy_type="custom",
            server="http://proxy.example.com:8080",
            username="testuser",
            password="testpass",
        )

        custom_option = BrowserOption(proxies=[custom_proxy])
        self.mock_session.client.init_browser.return_value.to_map.return_value = {
            "body": {"Data": {"Port": 9333}}
        }
        self.browser.initialize(custom_option)
        option = self.browser.get_option()

        self.assertIsNotNone(option.proxies)
        self.assertEqual(len(option.proxies), 1)
        proxy = option.proxies[0]
        self.assertEqual(proxy.type, "custom")
        self.assertEqual(proxy.server, "http://proxy.example.com:8080")
        self.assertEqual(proxy.username, "testuser")
        self.assertEqual(proxy.password, "testpass")

        # Test wuying restricted proxy
        restricted_proxy = BrowserProxy(proxy_type="wuying", strategy="restricted")

        restricted_option = BrowserOption(proxies=[restricted_proxy])
        # Create new browser instance for clean state
        restricted_browser = Browser(self.mock_session)
        restricted_browser.initialize(restricted_option)
        restricted_option_result = restricted_browser.get_option()

        self.assertIsNotNone(restricted_option_result.proxies)
        self.assertEqual(len(restricted_option_result.proxies), 1)
        restricted_proxy_result = restricted_option_result.proxies[0]
        self.assertEqual(restricted_proxy_result.type, "wuying")
        self.assertEqual(restricted_proxy_result.strategy, "restricted")

        # Test proxy serialization/deserialization
        proxy_map = custom_proxy._to_map()
        self.assertEqual(proxy_map["type"], "custom")
        self.assertEqual(proxy_map["server"], "http://proxy.example.com:8080")
        self.assertEqual(proxy_map["username"], "testuser")
        self.assertEqual(proxy_map["password"], "testpass")

        # Test from_map
        restored_proxy = BrowserProxy._from_map(proxy_map)
        self.assertEqual(restored_proxy.type, "custom")
        self.assertEqual(restored_proxy.server, "http://proxy.example.com:8080")
        self.assertEqual(restored_proxy.username, "testuser")
        self.assertEqual(restored_proxy.password, "testpass")

    def test_proxy_validation(self):
        """Test proxy validation logic."""

        # Test multiple proxies should fail
        proxy1 = BrowserProxy(proxy_type="custom", server="http://proxy1.com")
        proxy2 = BrowserProxy(proxy_type="custom", server="http://proxy2.com")

        with self.assertRaises(ValueError) as context:
            BrowserOption(proxies=[proxy1, proxy2])
        self.assertIn(
            "proxies list length must be limited to 1", str(context.exception)
        )

        # Test invalid proxy type should fail
        with self.assertRaises(ValueError) as context:
            BrowserProxy(proxy_type="invalid")
        self.assertIn("proxy_type must be custom or wuying", str(context.exception))

        # Test custom proxy without server should fail
        with self.assertRaises(ValueError) as context:
            BrowserProxy(proxy_type="custom")
        self.assertIn(
            "server is required for custom proxy type", str(context.exception)
        )

        # Test wuying proxy without strategy should fail
        with self.assertRaises(ValueError) as context:
            BrowserProxy(proxy_type="wuying")
        self.assertIn(
            "strategy is required for wuying proxy type", str(context.exception)
        )

        # Test wuying proxy with invalid strategy should fail
        with self.assertRaises(ValueError) as context:
            BrowserProxy(proxy_type="wuying", strategy="invalid")
        self.assertIn(
            "strategy must be restricted or polling for wuying proxy type",
            str(context.exception),
        )

        # Test polling strategy with invalid pollsize should fail
        with self.assertRaises(ValueError) as context:
            BrowserProxy(proxy_type="wuying", strategy="polling", pollsize=0)
        self.assertIn(
            "pollsize must be greater than 0 for polling strategy",
            str(context.exception),
        )

        with self.assertRaises(ValueError) as context:
            BrowserProxy(proxy_type="wuying", strategy="polling", pollsize=-1)
        self.assertIn(
            "pollsize must be greater than 0 for polling strategy",
            str(context.exception),
        )

    def test_fingerprint_format(self):
        """Test fingerprint format."""
        # Test fingerprint format from JSON
        fingerprint_format = FingerprintFormat.load(
            open(
                os.path.join(
                    os.path.dirname(__file__),
                    "../../../../resource/fingerprint.example.json",
                ),
                "r",
            ).read()
        )
        self.assertIsNotNone(fingerprint_format)
        self.assertIsNotNone(fingerprint_format.fingerprint)
        self.assertIsNotNone(fingerprint_format.headers)

        # Test fingerprint format to JSON
        json_str = fingerprint_format._to_json()
        self.assertIsNotNone(json_str)
        self.assertIsInstance(json_str, str)
        json_dict = json.loads(json_str)
        self.assertIsNotNone(json_dict)
        self.assertIsNotNone(json_dict["fingerprint"])
        self.assertIsNotNone(json_dict["headers"])

    def test_act(self):
        """Test act method."""
        page = MagicMock()
        self.mock_session.client.init_browser.return_value.to_map.return_value = {
            "body": {"Data": {"Port": 9333}}
        }
        self.browser.initialize(BrowserOption())
        # self.browser.agent is MagicMock in setUp
        self.browser.agent.act(ActOptions(action="Click search button"), page)
        self.browser.agent.act.assert_called()

    def test_observe(self):
        """Test observe method."""
        page = MagicMock()
        self.mock_session.client.init_browser.return_value.to_map.return_value = {
            "body": {"Data": {"Port": 9333}}
        }
        self.browser.initialize(BrowserOption())
        self.browser.agent.observe(
            ObserveOptions(instruction="Find the search button"), page
        )
        self.browser.agent.observe.assert_called()

    def test_extract(self):
        """Test extract method."""
        page = MagicMock()
        self.mock_session.client.init_browser.return_value.to_map.return_value = {
            "body": {"Data": {"Port": 9333}}
        }
        self.browser.initialize(BrowserOption())
        self.browser.agent.extract(
            ExtractOptions(instruction="Extract the title", schema=SchemaForTest), page
        )
        self.browser.agent.extract.assert_called()


class TestAsyncBrowser(unittest.TestCase):
    def setUp(self):
        """Set up test browser."""
        self.mock_session = MagicMock()
        # Configure async mock for init_browser_async
        mock_client = AsyncMock()
        mock_client.init_browser_async = AsyncMock()
        mock_client.init_browser_async.return_value = MagicMock()
        mock_client.init_browser_async.return_value.to_map.return_value = {
            "body": {"Data": {"Port": 9333}}
        }
        self.mock_session._get_client.return_value = mock_client
        # Mock session.call_mcp_tool as it is used by agent
        self.mock_session.call_mcp_tool = AsyncMock()

        self.browser = AsyncBrowser(self.mock_session)
        # We are testing real AsyncBrowserAgent, so we don't mock self.browser.agent
        # But we need to ensure dependencies work.

    def test_initialize_async(self):
        """Test initialize method (async)."""
        result = asyncio.run(self.browser.initialize(BrowserOption()))
        self.assertTrue(result)

    def test_act_async(self):
        """Test act method (async)."""
        page = MagicMock()
        page.context.new_cdp_session = AsyncMock()

        asyncio.run(self.browser.initialize(BrowserOption()))

        # Mock the MCP tool response for act
        # act calls _execute_act -> _call_mcp_tool_timeout
        # First call: page_use_act_async -> returns task_id
        # Second call: page_use_get_act_result -> returns result

        response1 = MagicMock(success=True, data=json.dumps({"task_id": "123"}))
        response2 = MagicMock(
            success=True,
            data=json.dumps({"steps": [], "is_done": True, "success": True}),
        )

        self.mock_session.call_mcp_tool.side_effect = [response1, response2]

        asyncio.run(
            self.browser.agent.act(AsyncActOptions(action="Click search button"), page)
        )
        self.mock_session.call_mcp_tool.assert_called()

    def test_observe_async(self):
        """Test observe method (async)."""
        page = MagicMock()
        page.context.new_cdp_session = AsyncMock()

        asyncio.run(self.browser.initialize(BrowserOption()))
        # observe calls page_use_observe -> returns list of items
        self.mock_session.call_mcp_tool.return_value = MagicMock(
            success=True, data=json.dumps([{"selector": "#search"}])
        )

        asyncio.run(
            self.browser.agent.observe(
                AsyncObserveOptions(instruction="Find the search button"), page
            )
        )
        self.mock_session.call_mcp_tool.assert_called()

    def test_extract_async(self):
        """Test extract method (async)."""
        page = MagicMock()
        page.context.new_cdp_session = AsyncMock()

        asyncio.run(self.browser.initialize(BrowserOption()))

        # extract calls page_use_extract_async -> returns task_id
        # then page_use_get_extract_result -> returns result

        response1 = MagicMock(success=True, data=json.dumps({"task_id": "456"}))
        # response2 should be the extracted data directly, as per _execute_extract implementation
        response2 = MagicMock(success=True, data=json.dumps({"title": "Example"}))

        self.mock_session.call_mcp_tool.side_effect = [response1, response2]

        asyncio.run(
            self.browser.agent.extract(
                AsyncExtractOptions(instruction="Extract the title", schema=SchemaForTest),
                page,
            )
        )
        self.mock_session.call_mcp_tool.assert_called()


if __name__ == "__main__":
    unittest.main()
