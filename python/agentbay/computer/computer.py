"""
Computer module for desktop UI automation.
Handles mouse operations, keyboard operations, window management, 
application management, and screen operations.
"""

from enum import Enum
from typing import List, Optional, Dict, Any, Union

from agentbay.api.base_service import BaseService
from agentbay.exceptions import AgentBayError
from agentbay.model import BoolResult, OperationResult, ApiResponse
import json


class MouseButton(str, Enum):
    """Mouse button types for click and drag operations."""
    LEFT = "left"
    RIGHT = "right"
    MIDDLE = "middle"
    DOUBLE_LEFT = "double_left"


class ScrollDirection(str, Enum):
    """Scroll direction for scroll operations."""
    UP = "up"
    DOWN = "down"
    LEFT = "left"
    RIGHT = "right"


class InstalledApp:
    """Represents an installed application."""
    def __init__(self, name: str, start_cmd: str, stop_cmd: Optional[str] = None, work_directory: Optional[str] = None):
        self.name = name
        self.start_cmd = start_cmd
        self.stop_cmd = stop_cmd
        self.work_directory = work_directory

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "InstalledApp":
        return cls(
            name=data.get("name", ""),
            start_cmd=data.get("start_cmd", ""),
            stop_cmd=data.get("stop_cmd"),
            work_directory=data.get("work_directory"),
        )


class Process:
    """Represents a running process."""
    def __init__(self, pname: str, pid: int, cmdline: Optional[str] = None):
        self.pname = pname
        self.pid = pid
        self.cmdline = cmdline

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "Process":
        return cls(
            pname=data.get("pname", ""),
            pid=data.get("pid", 0),
            cmdline=data.get("cmdline"),
        )


class Window:
    """Represents a window in the system."""
    def __init__(
        self,
        window_id: int,
        title: str,
        absolute_upper_left_x: Optional[int] = None,
        absolute_upper_left_y: Optional[int] = None,
        width: Optional[int] = None,
        height: Optional[int] = None,
        pid: Optional[int] = None,
        pname: Optional[str] = None,
        child_windows: Optional[List["Window"]] = None,
    ):
        self.window_id = window_id
        self.title = title
        self.absolute_upper_left_x = absolute_upper_left_x
        self.absolute_upper_left_y = absolute_upper_left_y
        self.width = width
        self.height = height
        self.pid = pid
        self.pname = pname
        self.child_windows = child_windows or []

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "Window":
        child_windows = []
        if "child_windows" in data and data["child_windows"]:
            child_windows = [cls.from_dict(child) for child in data["child_windows"]]
        return cls(
            window_id=data.get("window_id", 0),
            title=data.get("title", ""),
            absolute_upper_left_x=data.get("absolute_upper_left_x"),
            absolute_upper_left_y=data.get("absolute_upper_left_y"),
            width=data.get("width"),
            height=data.get("height"),
            pid=data.get("pid"),
            pname=data.get("pname"),
            child_windows=child_windows,
        )


class InstalledAppListResult(ApiResponse):
    """Result of operations returning a list of InstalledApps."""
    def __init__(
        self,
        request_id: str = "",
        success: bool = False,
        data: Optional[List[InstalledApp]] = None,
        error_message: str = "",
    ):
        super().__init__(request_id)
        self.success = success
        self.data = data if data is not None else []
        self.error_message = error_message


class ProcessListResult(ApiResponse):
    """Result of operations returning a list of Processes."""
    def __init__(
        self,
        request_id: str = "",
        success: bool = False,
        data: Optional[List[Process]] = None,
        error_message: str = "",
    ):
        super().__init__(request_id)
        self.success = success
        self.data = data if data is not None else []
        self.error_message = error_message


class AppOperationResult(ApiResponse):
    """Result of application operations like start/stop."""
    def __init__(
        self,
        request_id: str = "",
        success: bool = False,
        error_message: str = "",
    ):
        super().__init__(request_id)
        self.success = success
        self.error_message = error_message


class WindowListResult(ApiResponse):
    """Result of window listing operations."""
    def __init__(
        self,
        request_id: str = "",
        success: bool = False,
        windows: Optional[List[Any]] = None,
        error_message: str = "",
    ):
        super().__init__(request_id)
        self.success = success
        self.windows = windows or []
        self.error_message = error_message


class WindowInfoResult(ApiResponse):
    """Result of window info operations."""
    def __init__(
        self,
        request_id: str = "",
        success: bool = False,
        window: Any = None,
        error_message: str = "",
    ):
        super().__init__(request_id)
        self.success = success
        self.window = window
        self.error_message = error_message


class Computer(BaseService):
    """
    Handles computer UI automation operations in the AgentBay cloud environment.
    Provides comprehensive desktop automation capabilities including mouse, keyboard,
    window management, application management, and screen operations.
    """

    def __init__(self, session):
        """
        Initialize a Computer object.

        Args:
            session: The session object that provides access to the AgentBay API.
        """
        super().__init__(session)

    # Mouse Operations
    def click_mouse(self, x: int, y: int, button: Union[MouseButton, str] = MouseButton.LEFT) -> BoolResult:
        """
        Clicks the mouse at the specified screen coordinates.

        Args:
            x (int): X coordinate in pixels (0 is left edge of screen).
            y (int): Y coordinate in pixels (0 is top edge of screen).
            button (Union[MouseButton, str], optional): Mouse button to click. Options:
                - MouseButton.LEFT or "left": Single left click
                - MouseButton.RIGHT or "right": Right click (context menu)
                - MouseButton.MIDDLE or "middle": Middle click (scroll wheel)
                - MouseButton.DOUBLE_LEFT or "double_left": Double left click
                Defaults to MouseButton.LEFT.

        Returns:
            BoolResult: Object containing:
                - success (bool): Whether the click succeeded
                - data (bool): True if successful, None otherwise
                - error_message (str): Error description if failed

        Raises:
            ValueError: If button is not one of the valid options.

        Behavior:
            - Clicks at the exact pixel coordinates provided
            - Does not move the mouse cursor before clicking
            - For double-click, use MouseButton.DOUBLE_LEFT
            - Right-click typically opens context menus

        Example:
            ```python
            from agentbay import AgentBay
            from agentbay.computer.computer import MouseButton

            # Initialize and create a session
            agent_bay = AgentBay(api_key="your_api_key")
            result = agent_bay.create()
            
            if result.success:
                session = result.session
                computer = session.computer
                
                # Single left click at coordinates
                click_result = computer.click_mouse(100, 200)
                if click_result.success:
                    print("Left click successful")
                    # Output: Left click successful
                
                # Right click to open context menu
                right_click_result = computer.click_mouse(300, 400, MouseButton.RIGHT)
                if right_click_result.success:
                    print("Right click successful")
                    # Output: Right click successful
                
                # Double click
                double_click_result = computer.click_mouse(500, 600, MouseButton.DOUBLE_LEFT)
                if double_click_result.success:
                    print("Double click successful")
                    # Output: Double click successful
                
                # Clean up
                session.delete()
            ```

        Note:
            - Coordinates are absolute screen positions, not relative to windows
            - Use `get_screen_size()` to determine valid coordinate ranges
            - Consider using `move_mouse()` first if you need to see cursor movement
            - For UI automation, consider using higher-level methods from `ui` module

        See Also:
            move_mouse, drag_mouse, get_cursor_position, get_screen_size
        """
        button_str = button.value if isinstance(button, MouseButton) else button
        valid_buttons = [b.value for b in MouseButton]
        if button_str not in valid_buttons:
            raise ValueError(f"Invalid button '{button_str}'. Must be one of {valid_buttons}")

        args = {"x": x, "y": y, "button": button_str}
        try:
            result = self.session.call_mcp_tool("click_mouse", args)

            if not result.success:
                return BoolResult(
                    request_id=result.request_id,
                    success=False,
                    data=None,
                    error_message=result.error_message,
                )

            return BoolResult(
                request_id=result.request_id,
                success=True,
                data=True,
                error_message="",
            )
        except Exception as e:
            return BoolResult(
                request_id="",
                success=False,
                data=None,
                error_message=f"Failed to click mouse: {str(e)}",
            )

    def move_mouse(self, x: int, y: int) -> BoolResult:
        """
        Moves the mouse to the specified coordinates.

        Args:
            x (int): X coordinate.
            y (int): Y coordinate.

        Returns:
            BoolResult: Result object containing success status and error message if any.

        Example:
            ```python
            from agentbay import AgentBay

            agent_bay = AgentBay(api_key="your_api_key")
            result = agent_bay.create()

            if result.success:
                session = result.session
                computer = session.computer

                # Move mouse to coordinates (300, 400)
                move_result = computer.move_mouse(300, 400)
                if move_result.success:
                    print("Mouse moved successfully")
                    # Output: Mouse moved successfully

                session.delete()
            ```

        Note:
            - Moves the cursor smoothly to the target position
            - Does not click after moving
            - Use get_cursor_position() to verify the new position

        See Also:
            click_mouse, drag_mouse, get_cursor_position
        """
        args = {"x": x, "y": y}
        try:
            result = self.session.call_mcp_tool("move_mouse", args)

            if not result.success:
                return BoolResult(
                    request_id=result.request_id,
                    success=False,
                    data=None,
                    error_message=result.error_message,
                )

            return BoolResult(
                request_id=result.request_id,
                success=True,
                data=True,
                error_message="",
            )
        except Exception as e:
            return BoolResult(
                request_id="",
                success=False,
                data=None,
                error_message=f"Failed to move mouse: {str(e)}",
            )

    def drag_mouse(
        self, from_x: int, from_y: int, to_x: int, to_y: int, button: Union[MouseButton, str] = MouseButton.LEFT
    ) -> BoolResult:
        """
        Drags the mouse from one point to another.

        Args:
            from_x (int): Starting X coordinate.
            from_y (int): Starting Y coordinate.
            to_x (int): Ending X coordinate.
            to_y (int): Ending Y coordinate.
            button (Union[MouseButton, str], optional): Button type. Can be MouseButton enum or string.
                Valid values: MouseButton.LEFT, MouseButton.RIGHT, MouseButton.MIDDLE
                or their string equivalents. Defaults to MouseButton.LEFT.
                Note: DOUBLE_LEFT is not supported for drag operations.

        Returns:
            BoolResult: Result object containing success status and error message if any.

        Raises:
            ValueError: If button is not a valid option.
        """
        button_str = button.value if isinstance(button, MouseButton) else button
        valid_buttons = ["left", "right", "middle"]
        if button_str not in valid_buttons:
            raise ValueError(f"Invalid button '{button_str}'. Must be one of {valid_buttons}")

        args = {
            "from_x": from_x,
            "from_y": from_y,
            "to_x": to_x,
            "to_y": to_y,
            "button": button_str,
        }
        try:
            result = self.session.call_mcp_tool("drag_mouse", args)

            if not result.success:
                return BoolResult(
                    request_id=result.request_id,
                    success=False,
                    data=None,
                    error_message=result.error_message,
                )

            return BoolResult(
                request_id=result.request_id,
                success=True,
                data=True,
                error_message="",
            )
        except Exception as e:
            return BoolResult(
                request_id="",
                success=False,
                data=None,
                error_message=f"Failed to drag mouse: {str(e)}",
            )

    def scroll(
        self, x: int, y: int, direction: Union[ScrollDirection, str] = ScrollDirection.UP, amount: int = 1
    ) -> BoolResult:
        """
        Scrolls the mouse wheel at the specified coordinates.

        Args:
            x (int): X coordinate.
            y (int): Y coordinate.
            direction (Union[ScrollDirection, str], optional): Scroll direction. Can be ScrollDirection enum or string.
                Valid values: ScrollDirection.UP, ScrollDirection.DOWN, ScrollDirection.LEFT, ScrollDirection.RIGHT
                or their string equivalents. Defaults to ScrollDirection.UP.
            amount (int, optional): Scroll amount. Defaults to 1.

        Returns:
            BoolResult: Result object containing success status and error message if any.

        Raises:
            ValueError: If direction is not a valid option.
        """
        direction_str = direction.value if isinstance(direction, ScrollDirection) else direction
        valid_directions = [d.value for d in ScrollDirection]
        if direction_str not in valid_directions:
            raise ValueError(f"Invalid direction '{direction_str}'. Must be one of {valid_directions}")

        args = {"x": x, "y": y, "direction": direction_str, "amount": amount}
        try:
            result = self.session.call_mcp_tool("scroll", args)

            if not result.success:
                return BoolResult(
                    request_id=result.request_id,
                    success=False,
                    data=None,
                    error_message=result.error_message,
                )

            return BoolResult(
                request_id=result.request_id,
                success=True,
                data=True,
                error_message="",
            )
        except Exception as e:
            return BoolResult(
                request_id="",
                success=False,
                data=None,
                error_message=f"Failed to scroll: {str(e)}",
            )

    def get_cursor_position(self) -> OperationResult:
        """
        Gets the current cursor position.

        Returns:
            OperationResult: Result object containing cursor position data
                with keys 'x' and 'y', and error message if any.

        Example:
            ```python
            from agentbay import AgentBay

            agent_bay = AgentBay(api_key="your_api_key")
            result = agent_bay.create()

            if result.success:
                session = result.session
                computer = session.computer

                # Get current cursor position
                position_result = computer.get_cursor_position()
                if position_result.success:
                    x = position_result.data["x"]
                    y = position_result.data["y"]
                    print(f"Cursor is at position ({x}, {y})")
                    # Output: Cursor is at position (512, 384)

                session.delete()
            ```

        Note:
            - Returns the absolute screen coordinates
            - Useful for verifying mouse movements
            - Position is in pixels from top-left corner (0, 0)

        See Also:
            move_mouse, click_mouse, get_screen_size
        """
        args = {}
        try:
            result = self.session.call_mcp_tool("get_cursor_position", args)

            if not result.success:
                return OperationResult(
                    request_id=result.request_id,
                    success=False,
                    data=None,
                    error_message=result.error_message,
                )

            return OperationResult(
                request_id=result.request_id,
                success=True,
                data=result.data,
                error_message="",
            )
        except Exception as e:
            return OperationResult(
                request_id="",
                success=False,
                data=None,
                error_message=f"Failed to get cursor position: {str(e)}",
            )

    # Keyboard Operations
    def input_text(self, text: str) -> BoolResult:
        """
        Types text into the currently focused input field.

        Args:
            text (str): The text to input. Supports Unicode characters.

        Returns:
            BoolResult: Object with success status and error message if any.

        Example:
            ```python
            from agentbay import AgentBay

            agent_bay = AgentBay(api_key="your_api_key")
            result = agent_bay.create()
            
            if result.success:
                session = result.session
                computer = session.computer
                
                # Type text into focused field
                input_result = computer.input_text("Hello, AgentBay!")
                if input_result.success:
                    print("Text input successful")
                
                session.delete()
            ```

        Note:
            - Requires an input field to be focused first
            - Use click_mouse() or UI automation to focus the field
            - Supports special characters and Unicode

        See Also:
            press_keys, click_mouse
        """
        args = {"text": text}
        try:
            result = self.session.call_mcp_tool("input_text", args)

            if not result.success:
                return BoolResult(
                    request_id=result.request_id,
                    success=False,
                    data=None,
                    error_message=result.error_message,
                )

            return BoolResult(
                request_id=result.request_id,
                success=True,
                data=True,
                error_message="",
            )
        except Exception as e:
            return BoolResult(
                request_id="",
                success=False,
                data=None,
                error_message=f"Failed to input text: {str(e)}",
            )

    def press_keys(self, keys: List[str], hold: bool = False) -> BoolResult:
        """
        Presses the specified keys.

        Args:
            keys (List[str]): List of keys to press (e.g., ["Ctrl", "a"]).
            hold (bool, optional): Whether to hold the keys. Defaults to False.

        Returns:
            BoolResult: Result object containing success status and error message if any.

        Example:
            ```python
            from agentbay import AgentBay

            agent_bay = AgentBay(api_key="your_api_key")
            result = agent_bay.create()

            if result.success:
                session = result.session
                computer = session.computer

                # Press Ctrl+A to select all
                press_result = computer.press_keys(["Ctrl", "a"])
                if press_result.success:
                    print("Keys pressed successfully")
                    # Output: Keys pressed successfully

                # Hold Shift key for subsequent operations
                hold_result = computer.press_keys(["Shift"], hold=True)
                if hold_result.success:
                    print("Key held successfully")
                    # Output: Key held successfully

                # Remember to release held keys
                computer.release_keys(["Shift"])

                session.delete()
            ```

        Note:
            - Key names are case-sensitive
            - When hold=True, remember to call release_keys() afterwards
            - Supports modifier keys like Ctrl, Alt, Shift
            - Can press multiple keys simultaneously for shortcuts

        See Also:
            release_keys, input_text
        """
        args = {"keys": keys, "hold": hold}
        try:
            result = self.session.call_mcp_tool("press_keys", args)

            if not result.success:
                return BoolResult(
                    request_id=result.request_id,
                    success=False,
                    data=None,
                    error_message=result.error_message,
                )

            return BoolResult(
                request_id=result.request_id,
                success=True,
                data=True,
                error_message="",
            )
        except Exception as e:
            return BoolResult(
                request_id="",
                success=False,
                data=None,
                error_message=f"Failed to press keys: {str(e)}",
            )

    def release_keys(self, keys: List[str]) -> BoolResult:
        """
        Releases the specified keys.

        Args:
            keys (List[str]): List of keys to release (e.g., ["Ctrl", "a"]).

        Returns:
            BoolResult: Result object containing success status and error message if any.
        """
        args = {"keys": keys}
        try:
            result = self.session.call_mcp_tool("release_keys", args)

            if not result.success:
                return BoolResult(
                    request_id=result.request_id,
                    success=False,
                    data=None,
                    error_message=result.error_message,
                )

            return BoolResult(
                request_id=result.request_id,
                success=True,
                data=True,
                error_message="",
            )
        except Exception as e:
            return BoolResult(
                request_id="",
                success=False,
                data=None,
                error_message=f"Failed to release keys: {str(e)}",
            )

    # Screen Operations
    def get_screen_size(self) -> OperationResult:
        """
        Gets the screen size and DPI scaling factor.

        Returns:
            OperationResult: Result object containing screen size data
                with keys 'width', 'height', and 'dpiScalingFactor',
                and error message if any.

        Example:
            ```python
            from agentbay import AgentBay

            agent_bay = AgentBay(api_key="your_api_key")
            result = agent_bay.create()

            if result.success:
                session = result.session
                computer = session.computer

                # Get screen size information
                size_result = computer.get_screen_size()
                if size_result.success:
                    width = size_result.data["width"]
                    height = size_result.data["height"]
                    dpi_scaling = size_result.data["dpiScalingFactor"]
                    print(f"Screen size: {width}x{height}, DPI scaling: {dpi_scaling}")
                    # Output: Screen size: 1024x768, DPI scaling: 1.0

                session.delete()
            ```

        Note:
            - Returns the full screen dimensions in pixels
            - DPI scaling factor affects coordinate calculations on high-DPI displays
            - Use this to determine valid coordinate ranges for mouse operations

        See Also:
            click_mouse, move_mouse, screenshot
        """
        args = {}
        try:
            result = self.session.call_mcp_tool("get_screen_size", args)

            if not result.success:
                return OperationResult(
                    request_id=result.request_id,
                    success=False,
                    data=None,
                    error_message=result.error_message,
                )

            return OperationResult(
                request_id=result.request_id,
                success=True,
                data=result.data,
                error_message="",
            )
        except Exception as e:
            return OperationResult(
                request_id="",
                success=False,
                data=None,
                error_message=f"Failed to get screen size: {str(e)}",
            )

    def screenshot(self) -> OperationResult:
        """
        Takes a screenshot of the current screen.

        Returns:
            OperationResult: Result object containing the path to the screenshot
                and error message if any.

        Example:
            ```python
            from agentbay import AgentBay

            agent_bay = AgentBay(api_key="your_api_key")
            result = agent_bay.create()

            if result.success:
                session = result.session
                computer = session.computer

                # Take a screenshot
                screenshot_result = computer.screenshot()
                if screenshot_result.success:
                    screenshot_url = screenshot_result.data
                    print(f"Screenshot saved to: {screenshot_url}")
                    # Output: Screenshot saved to: https://wuying-intelligence-service-cn-hangzhou.oss-cn-hangzhou.aliyuncs.com/...

                session.delete()
            ```

        Note:
            - Returns an OSS URL to the screenshot image
            - Screenshot captures the entire screen
            - Useful for debugging and verification
            - Image format is typically PNG

        See Also:
            get_screen_size
        """
        args = {}
        try:
            result = self.session.call_mcp_tool("system_screenshot", args)

            if not result.success:
                return OperationResult(
                    request_id=result.request_id,
                    success=False,
                    data=None,
                    error_message=result.error_message,
                )

            return OperationResult(
                request_id=result.request_id,
                success=True,
                data=result.data,
                error_message="",
            )
        except Exception as e:
            return OperationResult(
                request_id="",
                success=False,
                data=None,
                error_message=f"Failed to take screenshot: {str(e)}",
            )

    # Window Management Operations (delegated to existing window module)
    def list_root_windows(self, timeout_ms: int = 3000) -> WindowListResult:
        """
        Lists all root windows.

        Args:
            timeout_ms (int, optional): Timeout in milliseconds. Defaults to 3000.
        Returns:
            WindowListResult: Result object containing list of windows and error message if any.
        """
        from agentbay.window import WindowManager
        window_manager = WindowManager(self.session)
        return window_manager.list_root_windows(timeout_ms)

    def get_active_window(self, timeout_ms: int = 3000) -> WindowInfoResult:
        """
        Gets the currently active window.

        Args:
            timeout_ms (int, optional): Timeout in milliseconds. Defaults to 3000.
        Returns:
            WindowInfoResult: Result object containing active window info and error message if any.
        """
        from agentbay.window import WindowManager
        window_manager = WindowManager(self.session)
        return window_manager.get_active_window(timeout_ms)

    def activate_window(self, window_id: int) -> BoolResult:
        """
        Activates the specified window.

        Args:
            window_id (int): The ID of the window to activate.

        Returns:
            BoolResult: Result object containing success status and error message if any.
        """
        from agentbay.window import WindowManager
        window_manager = WindowManager(self.session)
        return window_manager.activate_window(window_id)

    def close_window(self, window_id: int) -> BoolResult:
        """
        Closes the specified window.

        Args:
            window_id (int): The ID of the window to close.

        Returns:
            BoolResult: Result object containing success status and error message if any.
        """
        from agentbay.window import WindowManager
        window_manager = WindowManager(self.session)
        return window_manager.close_window(window_id)

    def maximize_window(self, window_id: int) -> BoolResult:
        """
        Maximizes the specified window.

        Args:
            window_id (int): The ID of the window to maximize.

        Returns:
            BoolResult: Result object containing success status and error message if any.
        """
        from agentbay.window import WindowManager
        window_manager = WindowManager(self.session)
        return window_manager.maximize_window(window_id)

    def minimize_window(self, window_id: int) -> BoolResult:
        """
        Minimizes the specified window.

        Args:
            window_id (int): The ID of the window to minimize.

        Returns:
            BoolResult: Result object containing success status and error message if any.
        """
        from agentbay.window import WindowManager
        window_manager = WindowManager(self.session)
        return window_manager.minimize_window(window_id)

    def restore_window(self, window_id: int) -> BoolResult:
        """
        Restores the specified window.

        Args:
            window_id (int): The ID of the window to restore.

        Returns:
            BoolResult: Result object containing success status and error message if any.
        """
        from agentbay.window import WindowManager
        window_manager = WindowManager(self.session)
        return window_manager.restore_window(window_id)

    def resize_window(self, window_id: int, width: int, height: int) -> BoolResult:
        """
        Resizes the specified window.

        Args:
            window_id (int): The ID of the window to resize.
            width (int): New width of the window.
            height (int): New height of the window.

        Returns:
            BoolResult: Result object containing success status and error message if any.
        """
        from agentbay.window import WindowManager
        window_manager = WindowManager(self.session)
        return window_manager.resize_window(window_id, width, height)

    def fullscreen_window(self, window_id: int) -> BoolResult:
        """
        Makes the specified window fullscreen.

        Args:
            window_id (int): The ID of the window to make fullscreen.

        Returns:
            BoolResult: Result object containing success status and error message if any.
        """
        from agentbay.window import WindowManager
        window_manager = WindowManager(self.session)
        return window_manager.fullscreen_window(window_id)

    def focus_mode(self, on: bool) -> BoolResult:
        """
        Toggles focus mode on or off.

        Args:
            on (bool): True to enable focus mode, False to disable it.

        Returns:
            BoolResult: Result object containing success status and error message if any.
        """
        from agentbay.window import WindowManager
        window_manager = WindowManager(self.session)
        return window_manager.focus_mode(on)

    # Application Management Operations
    def get_installed_apps(
        self, start_menu: bool = True, desktop: bool = False, ignore_system_apps: bool = True
    ) -> InstalledAppListResult:
        """
        Gets the list of installed applications.

        Args:
            start_menu (bool, optional): Whether to include start menu applications. Defaults to True.
            desktop (bool, optional): Whether to include desktop applications. Defaults to False.
            ignore_system_apps (bool, optional): Whether to ignore system applications. Defaults to True.

        Returns:
            InstalledAppListResult: Result object containing list of installed apps and error message if any.
        """
        try:
            args = {
                "start_menu": start_menu,
                "desktop": desktop,
                "ignore_system_apps": ignore_system_apps,
            }

            result = self.session.call_mcp_tool("get_installed_apps", args)

            if not result.success:
                return InstalledAppListResult(
                    request_id=result.request_id,
                    success=False,
                    error_message=result.error_message,
                )

            try:
                apps_json = json.loads(result.data)
                installed_apps = []

                for app_data in apps_json:
                    app = InstalledApp.from_dict(app_data)
                    installed_apps.append(app)

                return InstalledAppListResult(
                    request_id=result.request_id,
                    success=True,
                    data=installed_apps,
                )
            except json.JSONDecodeError as e:
                return InstalledAppListResult(
                    request_id=result.request_id,
                    success=False,
                    error_message=f"Failed to parse applications JSON: {e}",
                )
        except Exception as e:
            return InstalledAppListResult(
                success=False, error_message=str(e)
            )

    def start_app(self, start_cmd: str, work_directory: str = "", activity: str = "") -> ProcessListResult:
        """
        Starts the specified application.

        Args:
            start_cmd (str): The command to start the application.
            work_directory (str, optional): Working directory for the application. Defaults to "".
            activity (str, optional): Activity name to launch (for mobile apps). Defaults to "".

        Returns:
            ProcessListResult: Result object containing list of processes started and error message if any.
        """
        try:
            args = {"start_cmd": start_cmd}
            if work_directory:
                args["work_directory"] = work_directory
            if activity:
                args["activity"] = activity

            result = self.session.call_mcp_tool("start_app", args)

            if not result.success:
                return ProcessListResult(
                    request_id=result.request_id,
                    success=False,
                    error_message=result.error_message,
                )

            try:
                processes_json = json.loads(result.data)
                processes = []

                for process_data in processes_json:
                    process = Process.from_dict(process_data)
                    processes.append(process)

                return ProcessListResult(
                    request_id=result.request_id, success=True, data=processes
                )
            except json.JSONDecodeError as e:
                return ProcessListResult(
                    request_id=result.request_id,
                    success=False,
                    error_message=f"Failed to parse processes JSON: {e}",
                )
        except Exception as e:
            return ProcessListResult(success=False, error_message=str(e))

    def list_visible_apps(self) -> ProcessListResult:
        """
        Lists all applications with visible windows.

        Returns detailed process information for applications that have visible windows,
        including process ID, name, command line, and other system information.
        This is useful for system monitoring and process management tasks.

        Returns:
            ProcessListResult: Result object containing list of visible applications
                with detailed process information.
        """
        try:
            result = self.session.call_mcp_tool("list_visible_apps", {})

            if not result.success:
                return ProcessListResult(
                    request_id=result.request_id,
                    success=False,
                    error_message=result.error_message,
                )

            try:
                processes_json = json.loads(result.data)
                processes = []

                for process_data in processes_json:
                    process = Process.from_dict(process_data)
                    processes.append(process)

                return ProcessListResult(
                    request_id=result.request_id, success=True, data=processes
                )
            except json.JSONDecodeError as e:
                return ProcessListResult(
                    request_id=result.request_id,
                    success=False,
                    error_message=f"Failed to parse processes JSON: {e}",
                )
        except Exception as e:
            return ProcessListResult(success=False, error_message=str(e))

    def stop_app_by_pname(self, pname: str) -> AppOperationResult:
        """
        Stops an application by process name.

        Args:
            pname (str): The process name of the application to stop.

        Returns:
            AppOperationResult: Result object containing success status and error message if any.
        """
        try:
            args = {"pname": pname}
            result = self.session.call_mcp_tool("stop_app_by_pname", args)

            return AppOperationResult(
                request_id=result.request_id,
                success=result.success,
                error_message=result.error_message,
            )
        except Exception as e:
            return AppOperationResult(success=False, error_message=str(e))

    def stop_app_by_pid(self, pid: int) -> AppOperationResult:
        """
        Stops an application by process ID.

        Args:
            pid (int): The process ID of the application to stop.

        Returns:
            AppOperationResult: Result object containing success status and error message if any.
        """
        try:
            args = {"pid": pid}
            result = self.session.call_mcp_tool("stop_app_by_pid", args)

            return AppOperationResult(
                request_id=result.request_id,
                success=result.success,
                error_message=result.error_message,
            )
        except Exception as e:
            return AppOperationResult(success=False, error_message=str(e))

    def stop_app_by_cmd(self, stop_cmd: str) -> AppOperationResult:
        """
        Stops an application by stop command.

        Args:
            stop_cmd (str): The command to stop the application.

        Returns:
            AppOperationResult: Result object containing success status and error message if any.
        """
        try:
            args = {"stop_cmd": stop_cmd}
            result = self.session.call_mcp_tool("stop_app_by_cmd", args)

            return AppOperationResult(
                request_id=result.request_id,
                success=result.success,
                error_message=result.error_message,
            )
        except Exception as e:
            return AppOperationResult(success=False, error_message=str(e))