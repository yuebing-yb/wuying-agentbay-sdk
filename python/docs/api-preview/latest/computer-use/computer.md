# Computer API Reference

## 🖥️ Related Tutorial

- [Computer Use Guide](../../../../../docs/guides/computer-use/README.md) - Automate desktop applications

## Overview

The Computer module provides comprehensive desktop automation capabilities including mouse operations,
keyboard input, screen capture, and window management. It enables automated UI testing and RPA workflows.


## Requirements

- Requires `windows_latest` image for computer use features

## Data Types

### MouseButton

Mouse button constants: Left, Right, Middle

### ScrollDirection

Scroll direction constants: Up, Down, Left, Right

### KeyModifier

Keyboard modifier keys: Ctrl, Alt, Shift, Win

## Important Notes

- Key names in PressKeys and ReleaseKeys are case-sensitive
- Coordinate validation: x and y must be non-negative integers
- Drag operation requires valid start and end coordinates
- Screenshot operations may have size limitations



Computer module for desktop UI automation.
Handles mouse operations, keyboard operations, window management, 
application management, and screen operations.

## MouseButton Objects

```python
class MouseButton(str, Enum)
```

Mouse button types for click and drag operations.

#### LEFT

```python
LEFT = "left"
```

#### RIGHT

```python
RIGHT = "right"
```

#### MIDDLE

```python
MIDDLE = "middle"
```

#### DOUBLE\_LEFT

```python
DOUBLE_LEFT = "double_left"
```

## ScrollDirection Objects

```python
class ScrollDirection(str, Enum)
```

Scroll direction for scroll operations.

#### UP

```python
UP = "up"
```

#### DOWN

```python
DOWN = "down"
```

#### LEFT

```python
LEFT = "left"
```

#### RIGHT

```python
RIGHT = "right"
```

## InstalledApp Objects

```python
class InstalledApp()
```

Represents an installed application.

#### from\_dict

```python
@classmethod
def from_dict(cls, data: Dict[str, Any]) -> "InstalledApp"
```

## Process Objects

```python
class Process()
```

Represents a running process.

#### from\_dict

```python
@classmethod
def from_dict(cls, data: Dict[str, Any]) -> "Process"
```

## Window Objects

```python
class Window()
```

Represents a window in the system.

#### from\_dict

```python
@classmethod
def from_dict(cls, data: Dict[str, Any]) -> "Window"
```

## InstalledAppListResult Objects

```python
class InstalledAppListResult(ApiResponse)
```

Result of operations returning a list of InstalledApps.

## ProcessListResult Objects

```python
class ProcessListResult(ApiResponse)
```

Result of operations returning a list of Processes.

## AppOperationResult Objects

```python
class AppOperationResult(ApiResponse)
```

Result of application operations like start/stop.

## WindowListResult Objects

```python
class WindowListResult(ApiResponse)
```

Result of window listing operations.

## WindowInfoResult Objects

```python
class WindowInfoResult(ApiResponse)
```

Result of window info operations.

## Computer Objects

```python
class Computer(BaseService)
```

Handles computer UI automation operations in the AgentBay cloud environment.
Provides comprehensive desktop automation capabilities including mouse, keyboard,
window management, application management, and screen operations.

#### click\_mouse

```python
def click_mouse(
        x: int,
        y: int,
        button: Union[MouseButton, str] = MouseButton.LEFT) -> BoolResult
```

Clicks the mouse at the specified screen coordinates.

**Arguments**:

- `x` _int_ - X coordinate in pixels (0 is left edge of screen).
- `y` _int_ - Y coordinate in pixels (0 is top edge of screen).
- `button` _Union[MouseButton, str], optional_ - Mouse button to click. Options:
  - MouseButton.LEFT or "left": Single left click
  - MouseButton.RIGHT or "right": Right click (context menu)
  - MouseButton.MIDDLE or "middle": Middle click (scroll wheel)
  - MouseButton.DOUBLE_LEFT or "double_left": Double left click
  Defaults to MouseButton.LEFT.
  

**Returns**:

- `BoolResult` - Object containing:
  - success (bool): Whether the click succeeded
  - data (bool): True if successful, None otherwise
  - error_message (str): Error description if failed
  

**Raises**:

- `ValueError` - If button is not one of the valid options.
  
  Behavior:
  - Clicks at the exact pixel coordinates provided
  - Does not move the mouse cursor before clicking
  - For double-click, use MouseButton.DOUBLE_LEFT
  - Right-click typically opens context menus
  

**Example**:

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
  

**Notes**:

  - Coordinates are absolute screen positions, not relative to windows
  - Use `get_screen_size()` to determine valid coordinate ranges
  - Consider using `move_mouse()` first if you need to see cursor movement
  - For UI automation, consider using higher-level methods from `ui` module
  

**See Also**:

  move_mouse, drag_mouse, get_cursor_position, get_screen_size

#### move\_mouse

```python
def move_mouse(x: int, y: int) -> BoolResult
```

Moves the mouse to the specified coordinates.

**Arguments**:

- `x` _int_ - X coordinate.
- `y` _int_ - Y coordinate.
  

**Returns**:

- `BoolResult` - Result object containing success status and error message if any.

#### drag\_mouse

```python
def drag_mouse(
        from_x: int,
        from_y: int,
        to_x: int,
        to_y: int,
        button: Union[MouseButton, str] = MouseButton.LEFT) -> BoolResult
```

Drags the mouse from one point to another.

**Arguments**:

- `from_x` _int_ - Starting X coordinate.
- `from_y` _int_ - Starting Y coordinate.
- `to_x` _int_ - Ending X coordinate.
- `to_y` _int_ - Ending Y coordinate.
- `button` _Union[MouseButton, str], optional_ - Button type. Can be MouseButton enum or string.
  Valid values: MouseButton.LEFT, MouseButton.RIGHT, MouseButton.MIDDLE
  or their string equivalents. Defaults to MouseButton.LEFT.
- `Note` - DOUBLE_LEFT is not supported for drag operations.
  

**Returns**:

- `BoolResult` - Result object containing success status and error message if any.
  

**Raises**:

- `ValueError` - If button is not a valid option.

#### scroll

```python
def scroll(x: int,
           y: int,
           direction: Union[ScrollDirection, str] = ScrollDirection.UP,
           amount: int = 1) -> BoolResult
```

Scrolls the mouse wheel at the specified coordinates.

**Arguments**:

- `x` _int_ - X coordinate.
- `y` _int_ - Y coordinate.
- `direction` _Union[ScrollDirection, str], optional_ - Scroll direction. Can be ScrollDirection enum or string.
  Valid values: ScrollDirection.UP, ScrollDirection.DOWN, ScrollDirection.LEFT, ScrollDirection.RIGHT
  or their string equivalents. Defaults to ScrollDirection.UP.
- `amount` _int, optional_ - Scroll amount. Defaults to 1.
  

**Returns**:

- `BoolResult` - Result object containing success status and error message if any.
  

**Raises**:

- `ValueError` - If direction is not a valid option.

#### get\_cursor\_position

```python
def get_cursor_position() -> OperationResult
```

Gets the current cursor position.

**Returns**:

- `OperationResult` - Result object containing cursor position data
  with keys 'x' and 'y', and error message if any.

#### input\_text

```python
def input_text(text: str) -> BoolResult
```

Types text into the currently focused input field.

**Arguments**:

- `text` _str_ - The text to input. Supports Unicode characters.
  

**Returns**:

- `BoolResult` - Object with success status and error message if any.
  

**Example**:

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
  

**Notes**:

  - Requires an input field to be focused first
  - Use click_mouse() or UI automation to focus the field
  - Supports special characters and Unicode
  

**See Also**:

  press_keys, click_mouse

#### press\_keys

```python
def press_keys(keys: List[str], hold: bool = False) -> BoolResult
```

Presses the specified keys.

**Arguments**:

- `keys` _List[str]_ - List of keys to press (e.g., ["Ctrl", "a"]).
- `hold` _bool, optional_ - Whether to hold the keys. Defaults to False.
  

**Returns**:

- `BoolResult` - Result object containing success status and error message if any.

#### release\_keys

```python
def release_keys(keys: List[str]) -> BoolResult
```

Releases the specified keys.

**Arguments**:

- `keys` _List[str]_ - List of keys to release (e.g., ["Ctrl", "a"]).
  

**Returns**:

- `BoolResult` - Result object containing success status and error message if any.

#### get\_screen\_size

```python
def get_screen_size() -> OperationResult
```

Gets the screen size and DPI scaling factor.

**Returns**:

- `OperationResult` - Result object containing screen size data
  with keys 'width', 'height', and 'dpiScalingFactor',
  and error message if any.

#### screenshot

```python
def screenshot() -> OperationResult
```

Takes a screenshot of the current screen.

**Returns**:

- `OperationResult` - Result object containing the path to the screenshot
  and error message if any.

#### list\_root\_windows

```python
def list_root_windows(timeout_ms: int = 3000) -> WindowListResult
```

Lists all root windows.

**Arguments**:

- `timeout_ms` _int, optional_ - Timeout in milliseconds. Defaults to 3000.

**Returns**:

- `WindowListResult` - Result object containing list of windows and error message if any.

#### get\_active\_window

```python
def get_active_window(timeout_ms: int = 3000) -> WindowInfoResult
```

Gets the currently active window.

**Arguments**:

- `timeout_ms` _int, optional_ - Timeout in milliseconds. Defaults to 3000.

**Returns**:

- `WindowInfoResult` - Result object containing active window info and error message if any.

#### activate\_window

```python
def activate_window(window_id: int) -> BoolResult
```

Activates the specified window.

**Arguments**:

- `window_id` _int_ - The ID of the window to activate.
  

**Returns**:

- `BoolResult` - Result object containing success status and error message if any.

#### close\_window

```python
def close_window(window_id: int) -> BoolResult
```

Closes the specified window.

**Arguments**:

- `window_id` _int_ - The ID of the window to close.
  

**Returns**:

- `BoolResult` - Result object containing success status and error message if any.

#### maximize\_window

```python
def maximize_window(window_id: int) -> BoolResult
```

Maximizes the specified window.

**Arguments**:

- `window_id` _int_ - The ID of the window to maximize.
  

**Returns**:

- `BoolResult` - Result object containing success status and error message if any.

#### minimize\_window

```python
def minimize_window(window_id: int) -> BoolResult
```

Minimizes the specified window.

**Arguments**:

- `window_id` _int_ - The ID of the window to minimize.
  

**Returns**:

- `BoolResult` - Result object containing success status and error message if any.

#### restore\_window

```python
def restore_window(window_id: int) -> BoolResult
```

Restores the specified window.

**Arguments**:

- `window_id` _int_ - The ID of the window to restore.
  

**Returns**:

- `BoolResult` - Result object containing success status and error message if any.

#### resize\_window

```python
def resize_window(window_id: int, width: int, height: int) -> BoolResult
```

Resizes the specified window.

**Arguments**:

- `window_id` _int_ - The ID of the window to resize.
- `width` _int_ - New width of the window.
- `height` _int_ - New height of the window.
  

**Returns**:

- `BoolResult` - Result object containing success status and error message if any.

#### fullscreen\_window

```python
def fullscreen_window(window_id: int) -> BoolResult
```

Makes the specified window fullscreen.

**Arguments**:

- `window_id` _int_ - The ID of the window to make fullscreen.
  

**Returns**:

- `BoolResult` - Result object containing success status and error message if any.

#### focus\_mode

```python
def focus_mode(on: bool) -> BoolResult
```

Toggles focus mode on or off.

**Arguments**:

- `on` _bool_ - True to enable focus mode, False to disable it.
  

**Returns**:

- `BoolResult` - Result object containing success status and error message if any.

#### get\_installed\_apps

```python
def get_installed_apps(
        start_menu: bool = True,
        desktop: bool = False,
        ignore_system_apps: bool = True) -> InstalledAppListResult
```

Gets the list of installed applications.

**Arguments**:

- `start_menu` _bool, optional_ - Whether to include start menu applications. Defaults to True.
- `desktop` _bool, optional_ - Whether to include desktop applications. Defaults to False.
- `ignore_system_apps` _bool, optional_ - Whether to ignore system applications. Defaults to True.
  

**Returns**:

- `InstalledAppListResult` - Result object containing list of installed apps and error message if any.

#### start\_app

```python
def start_app(start_cmd: str,
              work_directory: str = "",
              activity: str = "") -> ProcessListResult
```

Starts the specified application.

**Arguments**:

- `start_cmd` _str_ - The command to start the application.
- `work_directory` _str, optional_ - Working directory for the application. Defaults to "".
- `activity` _str, optional_ - Activity name to launch (for mobile apps). Defaults to "".
  

**Returns**:

- `ProcessListResult` - Result object containing list of processes started and error message if any.

#### list\_visible\_apps

```python
def list_visible_apps() -> ProcessListResult
```

Lists all applications with visible windows.

Returns detailed process information for applications that have visible windows,
including process ID, name, command line, and other system information.
This is useful for system monitoring and process management tasks.

**Returns**:

- `ProcessListResult` - Result object containing list of visible applications
  with detailed process information.

#### stop\_app\_by\_pname

```python
def stop_app_by_pname(pname: str) -> AppOperationResult
```

Stops an application by process name.

**Arguments**:

- `pname` _str_ - The process name of the application to stop.
  

**Returns**:

- `AppOperationResult` - Result object containing success status and error message if any.

#### stop\_app\_by\_pid

```python
def stop_app_by_pid(pid: int) -> AppOperationResult
```

Stops an application by process ID.

**Arguments**:

- `pid` _int_ - The process ID of the application to stop.
  

**Returns**:

- `AppOperationResult` - Result object containing success status and error message if any.

#### stop\_app\_by\_cmd

```python
def stop_app_by_cmd(stop_cmd: str) -> AppOperationResult
```

Stops an application by stop command.

**Arguments**:

- `stop_cmd` _str_ - The command to stop the application.
  

**Returns**:

- `AppOperationResult` - Result object containing success status and error message if any.

## Best Practices

1. Verify screen coordinates before mouse operations
2. Use appropriate delays between UI interactions
3. Handle window focus changes properly
4. Take screenshots for verification and debugging
5. Use keyboard shortcuts for efficient automation
6. Clean up windows and applications after automation

## Related Resources

- [Application API Reference](application.md)
- [UI API Reference](ui.md)
- [Window API Reference](window.md)

---

*Documentation generated automatically from source code using pydoc-markdown.*
