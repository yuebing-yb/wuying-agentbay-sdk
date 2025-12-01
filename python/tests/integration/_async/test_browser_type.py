import json
import os
import sys
import time
import unittest

from agentbay import Browser, BrowserOption

# Add the parent directory to the path so we can import the agentbay package
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from agentbay import AgentBay
from agentbay._common.exceptions import AgentBayError
from agentbay._common.params.session_params import CreateSessionParams


def get_test_api_key():
    """Get API key for testing"""
    api_key = os.environ.get("AGENTBAY_API_KEY")
    if not api_key:
        api_key = "akm-xxx"  # Replace with your test API key
        print(
            "Warning: Using default API key. Set AGENTBAY_API_KEY environment variable for testing."
        )
    return api_key


class TestBrowserTypeIntegration(unittest.TestCase):
    """Integration test for browser type selection (chrome vs chromium)."""

    def setUp(self):
        """Set up test fixtures."""
        api_key = get_test_api_key()
        print("api_key =", api_key)
        self.agent_bay = AgentBay(api_key=api_key)
        print("Creating a new session for browser type testing...")
        self.create_session()

    def create_session(self):
        """Create a session with computer use image (required for browser type selection)."""
        # Create session parameters with computer use image
        session_param = CreateSessionParams()
        session_param.image_id = "linux_latest"  # Required for browser type selection

        print("Creating session with computer use image...")
        result = self.agent_bay.create(session_param)
        self.assertTrue(
            result.success, f"Failed to create session: {result.error_message}"
        )
        self.session = result.session
        if self.session:
            print(f"Session created with ID: {self.session.session_id}")

    def tearDown(self):
        """Clean up test fixtures."""
        if hasattr(self, "session") and self.session:
            try:
                print("Deleting session...")
                result = self.agent_bay.delete(self.session)
                if result.success:
                    print("Session deleted successfully")
                else:
                    print(f"Failed to delete session: {result.error_message}")
            except Exception as e:
                print(f"Error deleting session: {e}")

    def test_browser_type_default_none(self):
        """Test that None is the default browser type."""
        print("\n=== Testing default browser type (None) ===")

        # Create browser option with default settings
        browser_option = BrowserOption()

        # Verify default browser type is None
        self.assertIsNone(browser_option.browser_type)
        print(f"Default browser type: {browser_option.browser_type}")

        # Initialize browser
        print("Initializing browser with default options...")
        success = self.session.browser.initialize_async(browser_option)
        self.assertTrue(success, "Failed to initialize browser")
        print("Browser initialized successfully")

        # Verify browser is initialized
        self.assertTrue(self.session.browser.is_initialized())
        print("Browser is initialized")

        # Get endpoint URL
        endpoint_url = self.session.browser.get_endpoint_url()
        self.assertIsNotNone(endpoint_url)
        print(f"Browser endpoint URL: {endpoint_url}")

    def test_browser_type_chrome(self):
        """Test Chrome browser type selection."""
        print("\n=== Testing Chrome browser type ===")

        # Create browser option with Chrome type
        browser_option = BrowserOption(browser_type="chrome")

        # Verify browser type is set correctly
        self.assertEqual(browser_option.browser_type, "chrome")
        print(f"Browser type set to: {browser_option.browser_type}")

        # Initialize browser
        print("Initializing browser with Chrome type...")
        success = self.session.browser.initialize_async(browser_option)
        self.assertTrue(success, "Failed to initialize browser with Chrome type")
        print("Browser initialized successfully with Chrome")

        # Verify browser is initialized
        self.assertTrue(self.session.browser.is_initialized())
        print("Browser is initialized")

        # Get endpoint URL
        endpoint_url = self.session.browser.get_endpoint_url()
        self.assertIsNotNone(endpoint_url)
        print(f"Browser endpoint URL: {endpoint_url}")

    def test_browser_type_chromium_explicit(self):
        """Test explicit Chromium browser type selection."""
        print("\n=== Testing explicit Chromium browser type ===")

        # Create browser option with explicit Chromium type
        browser_option = BrowserOption(browser_type="chromium")

        # Verify browser type is set correctly
        self.assertEqual(browser_option.browser_type, "chromium")
        print(f"Browser type set to: {browser_option.browser_type}")

        # Initialize browser
        print("Initializing browser with explicit Chromium type...")
        success = self.session.browser.initialize_async(browser_option)
        self.assertTrue(success, "Failed to initialize browser with Chromium type")
        print("Browser initialized successfully with Chromium")

        # Verify browser is initialized
        self.assertTrue(self.session.browser.is_initialized())
        print("Browser is initialized")

        # Get endpoint URL
        endpoint_url = self.session.browser.get_endpoint_url()
        self.assertIsNotNone(endpoint_url)
        print(f"Browser endpoint URL: {endpoint_url}")

    def test_browser_type_invalid(self):
        """Test that invalid browser types raise ValueError."""
        print("\n=== Testing invalid browser type validation ===")

        # Test invalid browser type
        with self.assertRaises(ValueError) as context:
            BrowserOption(browser_type="firefox")

        self.assertIn(
            "browser_type must be 'chrome' or 'chromium'", str(context.exception)
        )
        print("Invalid browser type correctly rejected")

        # Test another invalid browser type
        with self.assertRaises(ValueError) as context:
            BrowserOption(browser_type="edge")

        self.assertIn(
            "browser_type must be 'chrome' or 'chromium'", str(context.exception)
        )
        print("Another invalid browser type correctly rejected")

    def test_browser_type_with_other_options(self):
        """Test browser type with other browser options."""
        print("\n=== Testing browser type with other options ===")

        # Create browser option with Chrome type and other options
        browser_option = BrowserOption(
            browser_type="chrome",
            use_stealth=True,
            user_agent="Mozilla/5.0 (Test) AppleWebKit/537.36",
            solve_captchas=True,
        )

        # Verify all options are set correctly
        self.assertEqual(browser_option.browser_type, "chrome")
        self.assertTrue(browser_option.use_stealth)
        self.assertEqual(
            browser_option.user_agent, "Mozilla/5.0 (Test) AppleWebKit/537.36"
        )
        self.assertTrue(browser_option.solve_captchas)
        print("All browser options set correctly")

        # Initialize browser
        print("Initializing browser with Chrome type and other options...")
        success = self.session.browser.initialize_async(browser_option)
        self.assertTrue(
            success, "Failed to initialize browser with Chrome and other options"
        )
        print("Browser initialized successfully with all options")

        # Verify browser is initialized
        self.assertTrue(self.session.browser.is_initialized())
        print("Browser is initialized")

        # Get endpoint URL
        endpoint_url = self.session.browser.get_endpoint_url()
        self.assertIsNotNone(endpoint_url)
        print(f"Browser endpoint URL: {endpoint_url}")

    def test_browser_type_serialization(self):
        """Test that browser type is properly serialized in _to_map()."""
        print("\n=== Testing browser type serialization ===")

        # Test Chrome browser type serialization
        chrome_option = BrowserOption(browser_type="chrome")
        chrome_map = chrome_option._to_map()

        self.assertIn("browserType", chrome_map)
        self.assertEqual(chrome_map["browserType"], "chrome")
        print("Chrome browser type serialized correctly")

        # Test Chromium browser type serialization
        chromium_option = BrowserOption(browser_type="chromium")
        chromium_map = chromium_option._to_map()

        self.assertIn("browserType", chromium_map)
        self.assertEqual(chromium_map["browserType"], "chromium")
        print("Chromium browser type serialized correctly")

        # Test default browser type serialization (should be None/not in map)
        default_option = BrowserOption()
        default_map = default_option._to_map()

        self.assertNotIn("browserType", default_map)
        print("Default browser type (None) not included in map - correct")

    def test_browser_type_standard_image_fallback(self):
        """Test that browser type works with standard browser images (should fallback to default behavior)."""
        print("\n=== Testing browser type with standard browser image ===")

        # Create a new session with standard browser image
        session_param = CreateSessionParams()
        session_param.image_id = "browser_latest"  # Standard browser image

        print("Creating session with standard browser image...")
        result = self.agent_bay.create(session_param)
        self.assertTrue(
            result.success, f"Failed to create session: {result.error_message}"
        )
        session = result.session

        try:
            # Test Chrome browser type with standard image (should still work)
            browser_option = BrowserOption(browser_type="chrome")
            print("Initializing browser with Chrome type on standard image...")
            success = session.browser.initialize_async(browser_option)
            self.assertTrue(
                success,
                "Failed to initialize browser with Chrome type on standard image",
            )
            print("Browser initialized successfully with Chrome on standard image")

            # Verify browser is initialized
            self.assertTrue(session.browser.is_initialized())
            print("Browser is initialized")

        finally:
            # Clean up the additional session
            try:
                result = self.agent_bay.delete(session)
                if result.success:
                    print("Additional session deleted successfully")
                else:
                    print(
                        f"Failed to delete additional session: {result.error_message}"
                    )
            except Exception as e:
                print(f"Error deleting additional session: {e}")


if __name__ == "__main__":
    unittest.main()
