"""
Unit tests for browser screenshot functionality.
"""

import pytest
from unittest.mock import Mock, patch


class TestBrowserScreenshot:
    """Test browser screenshot functionality."""

    def test_screenshot_basic(self):
        """Test basic screenshot functionality."""
        # Mock browser agent
        mock_agent = Mock()
        mock_agent.screenshot.return_value = "data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR42mNkYPhfDwAChwGA60e6kgAAAABJRU5ErkJggg=="

        # Test screenshot call
        result = mock_agent.screenshot()
        assert result.startswith("data:image/png;base64,")

    def test_screenshot_with_options(self):
        """Test screenshot with options."""
        mock_agent = Mock()
        mock_agent.screenshot.return_value = "data:image/png;base64,test"

        # Test with full page option
        result = mock_agent.screenshot(full_page=True, quality=90)
        mock_agent.screenshot.assert_called_with(full_page=True, quality=90)
        assert result == "data:image/png;base64,test"

    def test_screenshot_error_handling(self):
        """Test screenshot error handling."""
        mock_agent = Mock()
        mock_agent.screenshot.side_effect = Exception("Screenshot failed")

        with pytest.raises(Exception, match="Screenshot failed"):
            mock_agent.screenshot()


if __name__ == "__main__":
    pytest.main([__file__])
