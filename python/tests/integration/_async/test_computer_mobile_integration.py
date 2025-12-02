"""
Integration tests for Computer and Mobile modules.
Tests the integration with Session and actual usage patterns.
"""

from unittest.mock import Mock, patch

import pytest

from agentbay import AsyncAgentBay, AsyncSession
from agentbay import Computer
from agentbay import Mobile


class TestComputerMobileIntegration:
    """Integration tests for Computer and Mobile modules."""

    def setup_method(self):
        """Set up test fixtures."""
        self.api_key = "test-api-key"

    def test_session_has_computer_and_mobile_modules(self):
        """Test that Session includes Computer and Mobile modules."""
        # Arrange - Create a mock AsyncAgentBay instance
        mock_agent_bay = Mock()

        # Act - Create a Session directly
        session = AsyncSession(mock_agent_bay, "test-session-123")

        # Assert
        assert hasattr(session, "computer")
        assert hasattr(session, "mobile")
        assert isinstance(session.computer, Computer)
        assert isinstance(session.mobile, Mobile)

    def test_computer_module_usage_in_session(self):
        """Test Computer module usage through Session."""
        # Arrange
        mock_agent_bay = Mock()
        session = AsyncSession(mock_agent_bay, "test-session-123")

        # Mock the call_mcp_tool method at the session level
        with patch.object(session, "call_mcp_tool") as mock_mcp:
            mock_mcp_result = Mock()
            mock_mcp_result.success = True
            mock_mcp_result.request_id = "test-123"
            mock_mcp_result.content = ""
            mock_mcp.return_value = mock_mcp_result

            # Act
            result = session.computer.click_mouse(100, 200)

            # Assert
            assert result.success is True
            mock_mcp.assert_called_once_with(
                "click_mouse", {"x": 100, "y": 200, "button": "left"}
            )

    def test_mobile_module_usage_in_session(self):
        """Test Mobile module usage through Session."""
        # Arrange
        mock_agent_bay = Mock()
        session = AsyncSession(mock_agent_bay, "test-session-123")

        # Mock the call_mcp_tool method at the session level
        with patch.object(session, "call_mcp_tool") as mock_mcp:
            mock_mcp_result = Mock()
            mock_mcp_result.success = True
            mock_mcp_result.request_id = "test-123"
            mock_mcp_result.content = ""
            mock_mcp.return_value = mock_mcp_result

            # Act
            result = session.mobile.tap(150, 250)

            # Assert
            assert result.success is True
            mock_mcp.assert_called_once_with("tap", {"x": 150, "y": 250})

    def test_computer_get_installed_apps(self):
        """Test that Computer module can call get_installed_apps."""
        # Arrange
        mock_agent_bay = Mock()
        session = AsyncSession(mock_agent_bay, "test-session-123")

        # Mock the call_mcp_tool method at the session level
        with patch.object(session, "call_mcp_tool") as mock_mcp:
            mock_mcp_result = Mock()
            mock_mcp_result.success = True
            mock_mcp_result.request_id = "test-123"
            mock_mcp_result.data = "[]"  # get_installed_apps uses result.data
            mock_mcp.return_value = mock_mcp_result

            # Act
            result = session.computer.get_installed_apps()

            # Assert
            assert result.success is True

    def test_mobile_get_installed_apps(self):
        """Test that Mobile module can call get_installed_apps."""
        # Arrange
        mock_agent_bay = Mock()
        session = AsyncSession(mock_agent_bay, "test-session-123")

        # Mock the call_mcp_tool method at the session level
        with patch.object(session, "call_mcp_tool") as mock_mcp:
            mock_mcp_result = Mock()
            mock_mcp_result.success = True
            mock_mcp_result.request_id = "test-123"
            mock_mcp_result.data = "[]"  # get_installed_apps uses result.data
            mock_mcp.return_value = mock_mcp_result

            # Act - Mobile requires all three parameters
            result = session.mobile.get_installed_apps(True, False, True)

            # Assert
            assert result.success is True
