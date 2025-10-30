"""
Unit tests for Computer module.
Following TDD principles - tests first, then implementation.
"""

import pytest
from unittest.mock import Mock, patch

from agentbay.computer import Computer, MouseButton, ScrollDirection
from agentbay.model import BoolResult, OperationResult
from agentbay.exceptions import AgentBayError


class TestComputer:
    """Test cases for Computer module."""

    def setup_method(self):
        """Set up test fixtures."""
        self.mock_session = Mock()
        self.session = self.mock_session  # Add session reference
        self.computer = Computer(self.mock_session)

    def test_computer_initialization(self):
        """Test Computer module initialization."""
        assert self.computer.session == self.mock_session

    # Mouse Operations Tests
    def test_click_mouse_success(self):
        """Test successful mouse click."""
        # Arrange
        mock_result = Mock()
        mock_result.success = True
        mock_result.request_id = "test-123"
        mock_result.error_message = ""
        
        self.session.call_mcp_tool = Mock(return_value=mock_result)
        
        # Act
        result = self.computer.click_mouse(100, 200)
        
        # Assert
        assert isinstance(result, BoolResult)
        assert result.success is True
        assert result.data is True
        self.session.call_mcp_tool.assert_called_once_with(
            "click_mouse", {"x": 100, "y": 200, "button": "left"}
        )

    def test_click_mouse_with_button(self):
        """Test mouse click with specific button."""
        # Arrange
        mock_result = Mock()
        mock_result.success = True
        mock_result.request_id = "test-123"
        
        self.session.call_mcp_tool = Mock(return_value=mock_result)
        
        # Act
        result = self.computer.click_mouse(100, 200, button="right")
        
        # Assert
        self.session.call_mcp_tool.assert_called_once_with(
            "click_mouse", {"x": 100, "y": 200, "button": "right"}
        )

    def test_click_mouse_invalid_button(self):
        """Test mouse click with invalid button."""
        # Act & Assert
        with pytest.raises(ValueError, match="Invalid button"):
            self.computer.click_mouse(100, 200, button="invalid")

    def test_click_mouse_with_enum(self):
        """Test mouse click with MouseButton enum."""
        # Arrange
        mock_result = Mock()
        mock_result.success = True
        mock_result.request_id = "test-123"
        
        self.session.call_mcp_tool = Mock(return_value=mock_result)
        
        # Act
        result = self.computer.click_mouse(100, 200, button=MouseButton.RIGHT)
        
        # Assert
        assert result.success is True
        self.session.call_mcp_tool.assert_called_once_with(
            "click_mouse", {"x": 100, "y": 200, "button": "right"}
        )

    def test_click_mouse_with_double_left_enum(self):
        """Test mouse click with MouseButton.DOUBLE_LEFT enum."""
        # Arrange
        mock_result = Mock()
        mock_result.success = True
        mock_result.request_id = "test-123"
        
        self.session.call_mcp_tool = Mock(return_value=mock_result)
        
        # Act
        result = self.computer.click_mouse(100, 200, button=MouseButton.DOUBLE_LEFT)
        
        # Assert
        self.session.call_mcp_tool.assert_called_once_with(
            "click_mouse", {"x": 100, "y": 200, "button": "double_left"}
        )
    def test_move_mouse_success(self):
        """Test successful mouse move."""
        # Arrange
        mock_result = Mock()
        mock_result.success = True
        mock_result.request_id = "test-123"
        
        self.session.call_mcp_tool = Mock(return_value=mock_result)
        
        # Act
        result = self.computer.move_mouse(150, 250)
        
        # Assert
        assert isinstance(result, BoolResult)
        assert result.success is True
        self.session.call_mcp_tool.assert_called_once_with(
            "move_mouse", {"x": 150, "y": 250}
        )

    def test_drag_mouse_success(self):
        """Test successful mouse drag."""
        # Arrange
        mock_result = Mock()
        mock_result.success = True
        mock_result.request_id = "test-123"
        
        self.session.call_mcp_tool = Mock(return_value=mock_result)
        
        # Act
        result = self.computer.drag_mouse(100, 100, 200, 200)
        
        # Assert
        assert isinstance(result, BoolResult)
        assert result.success is True
        self.session.call_mcp_tool.assert_called_once_with(
            "drag_mouse", {
                "from_x": 100, "from_y": 100, 
                "to_x": 200, "to_y": 200, 
                "button": "left"
            }
        )

    def test_scroll_success(self):
        """Test successful scroll."""
        # Arrange
        mock_result = Mock()
        mock_result.success = True
        mock_result.request_id = "test-123"
        
        self.session.call_mcp_tool = Mock(return_value=mock_result)
        
        # Act
        result = self.computer.scroll(300, 300)
        
        # Assert
        assert isinstance(result, BoolResult)
        assert result.success is True
        self.session.call_mcp_tool.assert_called_once_with(
            "scroll", {"x": 300, "y": 300, "direction": "up", "amount": 1}
        )

    def test_scroll_with_params(self):
        """Test scroll with custom parameters."""
        # Arrange
        mock_result = Mock()
        mock_result.success = True
        mock_result.request_id = "test-123"
        
        self.session.call_mcp_tool = Mock(return_value=mock_result)
        
        # Act
        result = self.computer.scroll(300, 300, direction="down", amount=3)
        
        # Assert
        self.session.call_mcp_tool.assert_called_once_with(
            "scroll", {"x": 300, "y": 300, "direction": "down", "amount": 3}
        )

    def test_get_cursor_position_success(self):
        """Test successful cursor position retrieval."""
        # Arrange
        mock_result = Mock()
        mock_result.success = True
        mock_result.request_id = "test-123"
        mock_result.data = {"x": 150, "y": 250}
        
        self.session.call_mcp_tool = Mock(return_value=mock_result)
        
        # Act
        result = self.computer.get_cursor_position()
        
        # Assert
        assert isinstance(result, OperationResult)
        assert result.success is True
        assert result.data == {"x": 150, "y": 250}
        self.session.call_mcp_tool.assert_called_once_with("get_cursor_position", {})

    # Keyboard Operations Tests
    def test_input_text_success(self):
        """Test successful text input."""
        # Arrange
        mock_result = Mock()
        mock_result.success = True
        mock_result.request_id = "test-123"
        
        self.session.call_mcp_tool = Mock(return_value=mock_result)
        
        # Act
        result = self.computer.input_text("Hello World")
        
        # Assert
        assert isinstance(result, BoolResult)
        assert result.success is True
        self.session.call_mcp_tool.assert_called_once_with(
            "input_text", {"text": "Hello World"}
        )

    def test_press_keys_success(self):
        """Test successful key press."""
        # Arrange
        mock_result = Mock()
        mock_result.success = True
        mock_result.request_id = "test-123"
        
        self.session.call_mcp_tool = Mock(return_value=mock_result)
        
        # Act
        result = self.computer.press_keys(["Ctrl", "a"])
        
        # Assert
        assert isinstance(result, BoolResult)
        assert result.success is True
        self.session.call_mcp_tool.assert_called_once_with(
            "press_keys", {"keys": ["Ctrl", "a"], "hold": False}
        )

    def test_press_keys_with_hold(self):
        """Test key press with hold."""
        # Arrange
        mock_result = Mock()
        mock_result.success = True
        mock_result.request_id = "test-123"
        
        self.session.call_mcp_tool = Mock(return_value=mock_result)
        
        # Act
        result = self.computer.press_keys(["Shift"], hold=True)
        
        # Assert
        self.session.call_mcp_tool.assert_called_once_with(
            "press_keys", {"keys": ["Shift"], "hold": True}
        )

    def test_release_keys_success(self):
        """Test successful key release."""
        # Arrange
        mock_result = Mock()
        mock_result.success = True
        mock_result.request_id = "test-123"
        
        self.session.call_mcp_tool = Mock(return_value=mock_result)
        
        # Act
        result = self.computer.release_keys(["Shift"])
        
        # Assert
        assert isinstance(result, BoolResult)
        assert result.success is True
        self.session.call_mcp_tool.assert_called_once_with(
            "release_keys", {"keys": ["Shift"]}
        )

    # Screen Operations Tests
    def test_get_screen_size_success(self):
        """Test successful screen size retrieval."""
        # Arrange
        mock_result = Mock()
        mock_result.success = True
        mock_result.request_id = "test-123"
        mock_result.data = {"width": 1920, "height": 1080, "dpiScalingFactor": 1.0}
        
        self.session.call_mcp_tool = Mock(return_value=mock_result)
        
        # Act
        result = self.computer.get_screen_size()
        
        # Assert
        assert isinstance(result, OperationResult)
        assert result.success is True
        assert result.data["width"] == 1920
        assert result.data["height"] == 1080
        self.session.call_mcp_tool.assert_called_once_with("get_screen_size", {})

    def test_screenshot_success(self):
        """Test successful screenshot."""
        # Arrange
        mock_result = Mock()
        mock_result.success = True
        mock_result.request_id = "test-123"
        mock_result.data = "/path/to/screenshot.png"
        
        self.session.call_mcp_tool = Mock(return_value=mock_result)
        
        # Act
        result = self.computer.screenshot()
        
        # Assert
        assert isinstance(result, OperationResult)
        assert result.success is True
        assert result.data == "/path/to/screenshot.png"
        self.session.call_mcp_tool.assert_called_once_with("system_screenshot", {})

    # Error Handling Tests
    def test_click_mouse_mcp_failure(self):
        """Test mouse click when MCP tool fails."""
        # Arrange
        mock_result = Mock()
        mock_result.success = False
        mock_result.request_id = "test-123"
        mock_result.error_message = "MCP tool failed"
        
        self.session.call_mcp_tool = Mock(return_value=mock_result)
        
        # Act
        result = self.computer.click_mouse(100, 200)
        
        # Assert
        assert isinstance(result, BoolResult)
        assert result.success is False
        assert result.error_message == "MCP tool failed"

    def test_click_mouse_exception(self):
        """Test mouse click when exception occurs."""
        # Arrange
        self.session.call_mcp_tool = Mock(side_effect=Exception("Network error"))
        
        # Act
        result = self.computer.click_mouse(100, 200)
        
        # Assert
        assert isinstance(result, BoolResult)
        assert result.success is False
        assert "Failed to click mouse" in result.error_message

    def test_invalid_scroll_direction(self):
        """Test scroll with invalid direction."""
        # Act & Assert
        with pytest.raises(ValueError, match="Invalid direction"):
            self.computer.scroll(100, 100, direction="invalid")

    def test_scroll_with_enum(self):
        """Test scroll with ScrollDirection enum."""
        # Arrange
        mock_result = Mock()
        mock_result.success = True
        mock_result.request_id = "test-123"
        
        self.session.call_mcp_tool = Mock(return_value=mock_result)
        
        # Act
        result = self.computer.scroll(300, 300, direction=ScrollDirection.DOWN, amount=5)
        
        # Assert
        assert result.success is True
        self.session.call_mcp_tool.assert_called_once_with(
            "scroll", {"x": 300, "y": 300, "direction": "down", "amount": 5}
        )

    def test_drag_mouse_with_enum(self):
        """Test drag mouse with MouseButton enum."""
        # Arrange
        mock_result = Mock()
        mock_result.success = True
        mock_result.request_id = "test-123"
        
        self.session.call_mcp_tool = Mock(return_value=mock_result)
        
        # Act
        result = self.computer.drag_mouse(100, 100, 200, 200, button=MouseButton.MIDDLE)
        
        # Assert
        assert result.success is True
        self.session.call_mcp_tool.assert_called_once_with(
            "drag_mouse", {
                "from_x": 100, "from_y": 100,
                "to_x": 200, "to_y": 200,
                "button": "middle"
            }
        )
    def test_list_visible_apps_success(self):
        """Test list_visible_apps delegates to ApplicationManager."""
        with patch('agentbay.application.ApplicationManager') as mock_app_manager:
            mock_instance = Mock()
            mock_result = Mock(success=True, data=[Mock(pname="Calculator", pid=1234)])
            mock_instance.list_visible_apps.return_value = mock_result
            mock_app_manager.return_value = mock_instance
            
            result = self.computer.list_visible_apps()
            
            assert result.success is True
            assert len(result.data) == 1
            assert result.data[0].pname == "Calculator"
            mock_instance.list_visible_apps.assert_called_once_with()

    # Application Management Operations Tests
    def test_get_installed_apps_success(self):
        """Test get_installed_apps delegates to ApplicationManager."""
        # Arrange
        with patch('agentbay.application.ApplicationManager') as mock_app_manager:
            mock_instance = Mock()
            # Configure mock objects with attributes
            mock_app1 = Mock()
            mock_app1.configure_mock(name='Notepad', start_cmd='notepad.exe')
            mock_app2 = Mock()
            mock_app2.configure_mock(name='Calculator', start_cmd='calc.exe')
            mock_result = Mock(success=True, data=[mock_app1, mock_app2])
            mock_instance.get_installed_apps.return_value = mock_result
            mock_app_manager.return_value = mock_instance

            # Act
            result = self.computer.get_installed_apps()

            # Assert
            assert result.success is True
            assert len(result.data) == 2
            assert result.data[0].name == 'Notepad'
            assert result.data[1].name == 'Calculator'
            mock_instance.get_installed_apps.assert_called_once()

    def test_start_app_success(self):
        """Test start_app delegates to ApplicationManager."""
        # Arrange
        with patch('agentbay.application.ApplicationManager') as mock_app_manager:
            mock_instance = Mock()
            mock_process = Mock(pname='notepad', pid=1234)
            mock_result = Mock(success=True, data=[mock_process])
            mock_instance.start_app.return_value = mock_result
            mock_app_manager.return_value = mock_instance
            
            # Act
            result = self.computer.start_app('notepad.exe')
            
            # Assert
            assert result.success is True
            assert len(result.data) == 1
            assert result.data[0].pname == 'notepad'
            assert result.data[0].pid == 1234
            mock_instance.start_app.assert_called_once_with('notepad.exe', '', '')

    def test_start_app_with_working_directory(self):
        """Test start_app with working directory."""
        # Arrange
        with patch('agentbay.application.ApplicationManager') as mock_app_manager:
            mock_instance = Mock()
            mock_result = Mock(success=True, data=[])
            mock_instance.start_app.return_value = mock_result
            mock_app_manager.return_value = mock_instance
            
            # Act
            result = self.computer.start_app('notepad.exe', '/home/user/documents')
            
            # Assert
            assert result.success is True
            mock_instance.start_app.assert_called_once_with('notepad.exe', '/home/user/documents', '')

    def test_stop_app_by_pname_success(self):
        """Test stop_app_by_pname delegates to ApplicationManager."""
        # Arrange
        with patch('agentbay.application.ApplicationManager') as mock_app_manager:
            mock_instance = Mock()
            mock_result = Mock(success=True)
            mock_instance.stop_app_by_pname.return_value = mock_result
            mock_app_manager.return_value = mock_instance
            
            # Act
            result = self.computer.stop_app_by_pname('notepad')
            
            # Assert
            assert result.success is True
            mock_instance.stop_app_by_pname.assert_called_once_with('notepad')

    def test_stop_app_by_pid_success(self):
        """Test stop_app_by_pid delegates to ApplicationManager."""
        # Arrange
        with patch('agentbay.application.ApplicationManager') as mock_app_manager:
            mock_instance = Mock()
            mock_result = Mock(success=True)
            mock_instance.stop_app_by_pid.return_value = mock_result
            mock_app_manager.return_value = mock_instance
            
            # Act
            result = self.computer.stop_app_by_pid(1234)
            
            # Assert
            assert result.success is True
            mock_instance.stop_app_by_pid.assert_called_once_with(1234)

    def test_stop_app_by_cmd_success(self):
        """Test stop_app_by_cmd delegates to ApplicationManager."""
        # Arrange
        with patch('agentbay.application.ApplicationManager') as mock_app_manager:
            mock_instance = Mock()
            mock_result = Mock(success=True)
            mock_instance.stop_app_by_cmd.return_value = mock_result
            mock_app_manager.return_value = mock_instance
            
            # Act
            result = self.computer.stop_app_by_cmd('pkill notepad')
            
            # Assert
            assert result.success is True
            mock_instance.stop_app_by_cmd.assert_called_once_with('pkill notepad')

    def test_application_management_methods_exist(self):
        """Test that all application management methods exist on Computer class."""
        # Assert
        assert hasattr(self.computer, 'get_installed_apps')
        assert hasattr(self.computer, 'start_app')
        assert hasattr(self.computer, 'stop_app_by_pname')
        assert hasattr(self.computer, 'stop_app_by_pid')
        assert hasattr(self.computer, 'stop_app_by_cmd')
        assert hasattr(self.computer, 'list_visible_apps')
        
        # Verify they are callable
        assert callable(self.computer.get_installed_apps)
        assert callable(self.computer.start_app)
        assert callable(self.computer.stop_app_by_pname)
        assert callable(self.computer.stop_app_by_pid)
        assert callable(self.computer.stop_app_by_cmd)
        assert callable(self.computer.list_visible_apps) 