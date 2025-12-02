import time
import unittest
from unittest.mock import MagicMock, MagicMock, patch

from agentbay import SyncBrowser, BrowserOption
from agentbay import BrowserError


class TestBrowserScreenshot(unittest.TestCase):
    """Unit tests for browser screenshot functionality."""

    def setUp(self):
        """Set up test browser with mocked session."""
        self.mock_session = MagicMock()
        self.browser = SyncBrowser(self.mock_session)

        # Mock the session methods that would be called
        mock_client = MagicMock()
        mock_client.init_browser_async = MagicMock()
        mock_client.init_browser_async.return_value = MagicMock()
        mock_client.init_browser_async.return_value.to_map.return_value = {
            "body": {"Data": {"Port": 9333}}
        }
        self.mock_session._get_client.return_value = mock_client

        # Initialize the browser for tests
        time.run(self.browser.initialize(BrowserOption()))

    def test_screenshot_async_with_uninitialized_browser_raises_error(self):
        """Test that screenshot_async raises BrowserError when browser is not initialized."""
        # Create a new browser instance that is not initialized
        uninitialized_browser = SyncBrowser(self.mock_session)

        # Create a mock page
        mock_page = MagicMock()

        # Test that calling screenshot_async on uninitialized browser raises error
        with self.assertRaises(BrowserError) as context:
            time.run(uninitialized_browser.screenshot(mock_page))

        self.assertIn("Browser must be initialized", str(context.exception))

    def test_screenshot_async_with_none_page_raises_error(self):
        """Test that screenshot_async raises ValueError when page is None."""
        with self.assertRaises(ValueError) as context:
            time.run(self.browser.screenshot(None))

        self.assertIn("Page cannot be None", str(context.exception))

    @patch("agentbay._async.browser._logger")
    def test_screenshot_async_success(self, mock_logger):
        """Test successful screenshot capture."""
        # Create a mock page with async methods
        mock_page = MagicMock()
        mock_page.wait_for_load_state = MagicMock()
        mock_page.evaluate = MagicMock()
        mock_page.evaluate.return_value = 1000  # Return a fake height as integer
        mock_page.wait_for_timeout = MagicMock()
        mock_page.set_viewport_size = MagicMock()
        mock_page.screenshot = MagicMock(return_value=b"fake_screenshot_data")

        # Call the screenshot method
        result = time.run(self.browser.screenshot(mock_page))

        # Assertions
        self.assertIsInstance(result, bytes)
        self.assertEqual(result, b"fake_screenshot_data")

        # Verify that the page methods were called
        mock_page.wait_for_load_state.assert_called()
        mock_page.evaluate.assert_called()
        mock_page.screenshot.assert_called()

        # Verify logging
        mock_logger.info.assert_called_with("Screenshot captured successfully.")

    @patch("agentbay._async.browser._logger")
    def test_screenshot_async_with_full_page_option(self, mock_logger):
        """Test screenshot capture with full_page=True option."""
        # Create a mock page with async methods
        mock_page = MagicMock()
        mock_page.wait_for_load_state = MagicMock()
        mock_page.evaluate = MagicMock()
        mock_page.evaluate.return_value = 1000  # Return a fake height as integer
        mock_page.wait_for_timeout = MagicMock()
        mock_page.set_viewport_size = MagicMock()
        mock_page.screenshot = MagicMock(return_value=b"fake_full_page_screenshot_data")

        # Call the screenshot method with full_page=True
        result = time.run(self.browser.screenshot(mock_page, full_page=True))

        # Assertions
        self.assertIsInstance(result, bytes)
        self.assertEqual(result, b"fake_full_page_screenshot_data")

        # Verify that the page methods were called
        mock_page.wait_for_load_state.assert_called()
        mock_page.evaluate.assert_called()
        mock_page.screenshot.assert_called()

        # Verify that full_page option was passed to screenshot method
        mock_page.screenshot.assert_called_with(
            animations="disabled",
            caret="hide",
            scale="css",
            timeout=60000,
            full_page=True,
            type="png",
        )

    @patch("agentbay._async.browser._logger")
    def test_screenshot_async_with_custom_options(self, mock_logger):
        """Test screenshot capture with custom options."""
        # Create a mock page with async methods
        mock_page = MagicMock()
        mock_page.wait_for_load_state = MagicMock()
        mock_page.evaluate = MagicMock()
        mock_page.evaluate.return_value = 1000  # Return a fake height as integer
        mock_page.wait_for_timeout = MagicMock()
        mock_page.set_viewport_size = MagicMock()
        mock_page.screenshot = MagicMock(return_value=b"fake_custom_screenshot_data")

        # Call the screenshot method with custom options
        result = time.run(
            self.browser.screenshot(
                mock_page, full_page=False, type="jpeg", quality=80, timeout=30000
            )
        )

        # Assertions
        self.assertIsInstance(result, bytes)
        self.assertEqual(result, b"fake_custom_screenshot_data")

        # Verify that custom options were passed to screenshot method
        mock_page.screenshot.assert_called_with(
            animations="disabled",
            caret="hide",
            scale="css",
            timeout=30000,
            full_page=False,
            type="jpeg",
            quality=80,
        )

    @patch("agentbay._async.browser._logger")
    def test_screenshot_async_handles_exception(self, mock_logger):
        """Test that screenshot_async handles exceptions properly."""
        # Create a mock page that raises an exception
        mock_page = MagicMock()
        mock_page.wait_for_load_state = MagicMock()
        mock_page.evaluate = MagicMock()
        mock_page.evaluate.return_value = 1000  # Return a fake height as integer
        mock_page.wait_for_timeout = MagicMock()
        mock_page.set_viewport_size = MagicMock()
        mock_page.screenshot = MagicMock(side_effect=Exception("Screenshot failed"))

        # Call the screenshot method and expect it to raise RuntimeError
        with self.assertRaises(RuntimeError) as context:
            time.run(self.browser.screenshot(mock_page))

        # Verify the error message
        self.assertIn("Failed to capture screenshot", str(context.exception))
        self.assertIn("Screenshot failed", str(context.exception))

        # Verify logging
        mock_logger.error.assert_called()

    @patch("agentbay._async.browser._logger")
    def test_screenshot_async_handles_coroutine_exception(self, mock_logger):
        """Test that screenshot_async handles exceptions that can't be converted to string."""
        # Create a mock page that raises an exception that can't be converted to string
        mock_page = MagicMock()
        mock_page.wait_for_load_state = MagicMock()
        mock_page.evaluate = MagicMock()
        mock_page.evaluate.return_value = 1000  # Return a fake height as integer
        mock_page.wait_for_timeout = MagicMock()
        mock_page.set_viewport_size = MagicMock()

        # Create a mock exception that raises an error when converted to string
        class UnconvertibleException(Exception):
            def __str__(self):
                raise RuntimeError("Cannot convert to string")

        mock_page.screenshot = MagicMock(
            side_effect=UnconvertibleException("Original error")
        )

        # Call the screenshot method and expect it to raise RuntimeError
        with self.assertRaises(RuntimeError) as context:
            time.run(self.browser.screenshot(mock_page))

        # Verify the error message contains the fallback text
        self.assertIn("Failed to capture screenshot", str(context.exception))
        self.assertIn("Unknown error occurred", str(context.exception))


if __name__ == "__main__":
    unittest.main()
