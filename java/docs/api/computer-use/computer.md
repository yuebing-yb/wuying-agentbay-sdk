# 🖥️ Computer API Reference

## Overview

The Computer module provides comprehensive desktop automation capabilities including mouse operations,keyboard input, screen capture, and window management. It enables automated UI testing and RPA workflows.


## 📚 Tutorial

[Computer Use Guide](../../../../docs/guides/computer-use/README.md)

Automate desktop applications

## 📋 Requirements

- Requires `windows_latest` image for computer use features

## Computer

Computer module for desktop UI automation.
Provides comprehensive desktop automation capabilities including mouse, keyboard,window management, application management, and screen operations.

### Constructor

```java
public Computer(Session session)
```

### Methods

### startApp

```java
public ProcessListResult startApp(String startCmd, String workDirectory, String activity)
```

```java
public ProcessListResult startApp(String startCmd, String workDirectory)
```

```java
public ProcessListResult startApp(String startCmd)
```

Starts an application with the given command, optional working directory and optional activity.

**Parameters:**
- `startCmd` (String): The command to start the application
- `workDirectory` (String): working directory for the application
- `activity` (String): activity name to launch (for mobile apps). Defaults to empty string.

**Returns:**
- `ProcessListResult`: ProcessListResult containing the list of processes started and error message if any.

### stopAppByPName

```java
public AppOperationResult stopAppByPName(String pname)
```

Stops an application by process name.

**Parameters:**
- `pname` (String): The process name of the application to stop

**Returns:**
- `AppOperationResult`: AppOperationResult containing success status and error message if any

### stopAppByPID

```java
public AppOperationResult stopAppByPID(int pid)
```

Stops an application by process ID.

**Parameters:**
- `pid` (int): The process ID of the application to stop

**Returns:**
- `AppOperationResult`: AppOperationResult containing success status and error message if any

### stopAppByCmd

```java
public AppOperationResult stopAppByCmd(String stopCmd)
```

Stops an application by stop command.

**Parameters:**
- `stopCmd` (String): The command to stop the application

**Returns:**
- `AppOperationResult`: AppOperationResult containing success status and error message if any

### listVisibleApps

```java
public ProcessListResult listVisibleApps()
```

Lists all applications with visible windows.
Returns detailed process information for applications that have visible windows,including process ID, name, command line, and other system information.
This is useful for system monitoring and process management tasks.

**Returns:**
- `ProcessListResult`: ProcessListResult containing list of visible applications with detailed process information

### getInstalledApps

```java
public InstalledAppListResult getInstalledApps(boolean startMenu, boolean desktop, boolean ignoreSystemApps)
```

```java
public InstalledAppListResult getInstalledApps()
```

Gets the list of installed applications.

**Parameters:**
- `startMenu` (boolean): Whether to include start menu applications. Defaults to true.
- `desktop` (boolean): Whether to include desktop applications. Defaults to false.
- `ignoreSystemApps` (boolean): Whether to ignore system applications. Defaults to true.

**Returns:**
- `InstalledAppListResult`: InstalledAppListResult containing list of installed apps and error message if any

### clickMouse

```java
public BoolResult clickMouse(int x, int y, MouseButton button)
```

```java
public BoolResult clickMouse(int x, int y)
```

```java
public BoolResult clickMouse(int x, int y, String button)
```

Clicks the mouse at the specified screen coordinates.

**Parameters:**
- `x` (int): X coordinate in pixels (0 is left edge of screen)
- `y` (int): Y coordinate in pixels (0 is top edge of screen)
- `button` (MouseButton): Mouse button to click. Options:
              - MouseButton.LEFT: Single left click
              - MouseButton.RIGHT: Right click (context menu)
              - MouseButton.MIDDLE: Middle click (scroll wheel)
              - MouseButton.DOUBLE_LEFT: Double left click
              Defaults to MouseButton.LEFT

**Returns:**
- `BoolResult`: BoolResult Object containing:
        - success (boolean): Whether the click succeeded
        - data (Boolean): True if successful, null otherwise
        - errorMessage (String): Error description if failed

**Throws:**
- `IllegalArgumentException`: If button is not one of the valid options

<p>Behavior:
<ul>
  <li>Clicks at the exact pixel coordinates provided</li>
  <li>Does not move the mouse cursor before clicking</li>
  <li>For double-click, use MouseButton.DOUBLE_LEFT</li>
  <li>Right-click typically opens context menus</li>
</ul>


<p>Note:
<ul>
  <li>Coordinates are absolute screen positions, not relative to windows</li>
  <li>Use getScreenSize() to determine valid coordinate ranges</li>
  <li>Consider using moveMouse() first if you need to see cursor movement</li>
</ul>

### moveMouse

```java
public BoolResult moveMouse(int x, int y)
```

Moves the mouse to the specified coordinates.

**Parameters:**
- `x` (int): X coordinate
- `y` (int): Y coordinate

**Returns:**
- `BoolResult`: BoolResult Result object containing success status and error message if any


<p>Note:
<ul>
  <li>Moves the cursor smoothly to the target position</li>
  <li>Does not click after moving</li>
  <li>Use getCursorPosition() to verify the new position</li>
</ul>

### dragMouse

```java
public BoolResult dragMouse(int fromX, int fromY, int toX, int toY, MouseButton button)
```

```java
public BoolResult dragMouse(int fromX, int fromY, int toX, int toY)
```

```java
public BoolResult dragMouse(int fromX, int fromY, int toX, int toY, String button)
```

Drags the mouse from one point to another.

**Parameters:**
- `fromX` (int): Starting X coordinate
- `fromY` (int): Starting Y coordinate
- `toX` (int): Ending X coordinate
- `toY` (int): Ending Y coordinate
- `button` (MouseButton): Mouse button to use. Defaults to LEFT

**Returns:**
- `BoolResult`: BoolResult containing success status and error message if any

### scroll

```java
public BoolResult scroll(int x, int y, ScrollDirection direction, int amount)
```

```java
public BoolResult scroll(int x, int y)
```

```java
public BoolResult scroll(int x, int y, String direction, int amount)
```

Scrolls the mouse wheel at the specified coordinates.

**Parameters:**
- `x` (int): X coordinate
- `y` (int): Y coordinate
- `direction` (ScrollDirection): Scroll direction. Defaults to UP
- `amount` (int): Scroll amount. Defaults to 1

**Returns:**
- `BoolResult`: BoolResult containing success status and error message if any

### getCursorPosition

```java
public OperationResult getCursorPosition()
```

Gets the current cursor position.

**Returns:**
- `OperationResult`: OperationResult Result object containing cursor position data with keys 'x' and 'y', and error message if any

<p>Note:
<ul>
  <li>Returns the absolute screen coordinates</li>
  <li>Useful for verifying mouse movements</li>
  <li>Position is in pixels from top-left corner (0, 0)</li>
</ul>

### inputText

```java
public BoolResult inputText(String text)
```

Types text into the currently focused input field.

**Parameters:**
- `text` (String): The text to input. Supports Unicode characters

**Returns:**
- `BoolResult`: BoolResult Object with success status and error message if any

<p>Note:
<ul>
  <li>Requires an input field to be focused first</li>
  <li>Use clickMouse() or UI automation to focus the field</li>
  <li>Supports special characters and Unicode</li>
</ul>

### pressKeys

```java
public BoolResult pressKeys(List<String> keys, boolean hold)
```

```java
public BoolResult pressKeys(List<String> keys)
```

Presses the specified keys.

**Parameters:**
- `keys` (List<String>): List of keys to press (e.g., Arrays.asList("Ctrl", "a"))
- `hold` (boolean): Whether to hold the keys. Defaults to false

**Returns:**
- `BoolResult`: BoolResult Result object containing success status and error message if any

<p>Note:
<ul>
  <li>Key names are case-sensitive</li>
  <li>When hold=true, remember to call releaseKeys() afterwards</li>
  <li>Supports modifier keys like Ctrl, Alt, Shift</li>
  <li>Can press multiple keys simultaneously for shortcuts</li>
</ul>

### releaseKeys

```java
public BoolResult releaseKeys(List<String> keys)
```

Releases the specified keys.

**Parameters:**
- `keys` (List<String>): List of keys to release (e.g., Arrays.asList("Ctrl", "a"))

**Returns:**
- `BoolResult`: BoolResult Result object containing success status and error message if any

<p>Note:
<ul>
  <li>Should be used after pressKeys() with hold=true</li>
  <li>Key names are case-sensitive</li>
  <li>Releases all keys specified in the list</li>
</ul>

### getScreenSize

```java
public OperationResult getScreenSize()
```

Gets the screen size and DPI scaling factor.

**Returns:**
- `OperationResult`: OperationResult Result object containing screen size data with keys 'width', 'height', and 'dpiScalingFactor', and error message if any

<p>Note:
<ul>
  <li>Returns the full screen dimensions in pixels</li>
  <li>DPI scaling factor affects coordinate calculations on high-DPI displays</li>
  <li>Use this to determine valid coordinate ranges for mouse operations</li>
</ul>

### screenshot

```java
public OperationResult screenshot()
```

Takes a screenshot of the current screen.

**Returns:**
- `OperationResult`: OperationResult Result object containing the path to the screenshot and error message if any

<p>Note:
<ul>
  <li>Returns an OSS URL to the screenshot image</li>
  <li>Screenshot captures the entire screen</li>
  <li>Useful for debugging and verification</li>
  <li>Image format is typically PNG</li>
</ul>

### betaTakeScreenshot

```java
public ScreenshotBytesResult betaTakeScreenshot(String format)
```

```java
public ScreenshotBytesResult betaTakeScreenshot()
```

Takes a screenshot of the Computer and returns raw binary image data (beta).

<p>This API uses the MCP tool `screenshot` (wuying_capture) and returns raw
binary image data. The backend also returns the captured image dimensions
(width/height in pixels), which are exposed on ScreenshotBytesResult.width
and ScreenshotBytesResult.height. The backend metadata fields `type` and
`mime_type` are exposed on ScreenshotBytesResult.type and ScreenshotBytesResult.mimeType.

**Parameters:**
- `format` (String): The desired image format (default: "png"). Supported: "png", "jpeg", "jpg"

**Returns:**
- `ScreenshotBytesResult`: ScreenshotBytesResult Object containing the screenshot image data (bytes) and metadata
        including `type`, `mimeType`, `width`, and `height` when provided by the backend

**Throws:**
- `IllegalArgumentException`: If format is invalid

<p>Supported formats:
<ul>
  <li>"png"</li>
  <li>"jpeg" (or "jpg")</li>
</ul>

### listRootWindows

```java
public WindowListResult listRootWindows(int timeoutMs)
```

```java
public WindowListResult listRootWindows()
```

Lists all root windows.

**Parameters:**
- `timeoutMs` (int): Timeout in milliseconds. Defaults to 3000

**Returns:**
- `WindowListResult`: WindowListResult Result object containing list of windows and error message if any

### getActiveWindow

```java
public WindowInfoResult getActiveWindow(int timeoutMs)
```

```java
public WindowInfoResult getActiveWindow()
```

Gets the currently active window.

**Parameters:**
- `timeoutMs` (int): Timeout in milliseconds. Defaults to 3000

**Returns:**
- `WindowInfoResult`: WindowInfoResult Result object containing active window info and error message if any

<p><strong>Note</strong>: Java version requires timeoutMs parameter, while Python version does not.

### activateWindow

```java
public BoolResult activateWindow(int windowId)
```

Activates the specified window.

**Parameters:**
- `windowId` (int): The ID of the window to activate

**Returns:**
- `BoolResult`: BoolResult Result object containing success status and error message if any

<p>Note:
<ul>
  <li>The window must exist in the system</li>
  <li>Use listRootWindows() to get available window IDs</li>
  <li>Activating a window brings it to the foreground</li>
</ul>

### closeWindow

```java
public BoolResult closeWindow(int windowId)
```

Closes the specified window.

**Parameters:**
- `windowId` (int): The ID of the window to close

**Returns:**
- `BoolResult`: BoolResult Result object containing success status and error message if any

<p>Note:
<ul>
  <li>The window must exist in the system</li>
  <li>Use listRootWindows() to get available window IDs</li>
  <li>Closing a window terminates it permanently</li>
</ul>

### maximizeWindow

```java
public BoolResult maximizeWindow(int windowId)
```

Maximizes the specified window.

**Parameters:**
- `windowId` (int): The ID of the window to maximize

**Returns:**
- `BoolResult`: BoolResult Result object containing success status and error message if any

<p>Note:
<ul>
  <li>The window must exist in the system</li>
  <li>Maximizing expands the window to fill the screen</li>
  <li>Use restoreWindow() to return to previous size</li>
</ul>

### minimizeWindow

```java
public BoolResult minimizeWindow(int windowId)
```

Minimizes the specified window.

**Parameters:**
- `windowId` (int): The ID of the window to minimize

**Returns:**
- `BoolResult`: BoolResult Result object containing success status and error message if any

<p>Note:
<ul>
  <li>The window must exist in the system</li>
  <li>Minimizing hides the window in the taskbar</li>
  <li>Use restoreWindow() or activateWindow() to bring it back</li>
</ul>

### restoreWindow

```java
public BoolResult restoreWindow(int windowId)
```

Restores the specified window.

**Parameters:**
- `windowId` (int): The ID of the window to restore

**Returns:**
- `BoolResult`: BoolResult Result object containing success status and error message if any

<p>Note:
<ul>
  <li>The window must exist in the system</li>
  <li>Restoring returns a minimized or maximized window to its normal state</li>
  <li>Works for windows that were previously minimized or maximized</li>
</ul>

### resizeWindow

```java
public BoolResult resizeWindow(int windowId, int width, int height)
```

Resizes the specified window.

**Parameters:**
- `windowId` (int): The ID of the window to resize
- `width` (int): New width of the window
- `height` (int): New height of the window

**Returns:**
- `BoolResult`: BoolResult Result object containing success status and error message if any

<p>Note:
<ul>
  <li>The window must exist in the system</li>
  <li>Width and height are in pixels</li>
  <li>Some windows may have minimum or maximum size constraints</li>
</ul>

### fullscreenWindow

```java
public BoolResult fullscreenWindow(int windowId)
```

Makes the specified window fullscreen.

**Parameters:**
- `windowId` (int): The ID of the window to make fullscreen

**Returns:**
- `BoolResult`: BoolResult containing success status and error message if any

<p>Note:
<ul>
  <li>The window must exist in the system</li>
  <li>Fullscreen mode hides window borders and taskbar</li>
  <li>Different from maximizeWindow() which keeps window borders</li>
  <li>Press F11 or ESC to exit fullscreen in most applications</li>
</ul>

### focusMode

```java
public BoolResult focusMode(boolean on)
```

Toggles focus mode on or off.

**Parameters:**
- `on` (boolean): True to enable focus mode, False to disable it

**Returns:**
- `BoolResult`: BoolResult containing success status and error message if any

<p>Note:
<ul>
  <li>Focus mode helps reduce distractions by managing window focus</li>
  <li>When enabled, may prevent background windows from stealing focus</li>
  <li>Behavior depends on the window manager and OS settings</li>
</ul>



## 💡 Best Practices

- Verify screen coordinates before mouse operations
- Use appropriate delays between UI interactions
- Handle window focus changes properly
- Take screenshots for verification and debugging
- Use keyboard shortcuts for efficient automation
- Clean up windows and applications after automation

