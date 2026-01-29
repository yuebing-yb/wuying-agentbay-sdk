# 🖥️ Computer API Reference

## Overview

The Computer module provides comprehensive desktop automation capabilities including mouse operations,
keyboard input, screen capture, and window management. It enables automated UI testing and RPA workflows.


## 📚 Tutorial

[Computer Use Guide](../../../../docs/guides/computer-use/README.md)

Automate desktop applications

## 📋 Requirements

- Requires `windows_latest` image for computer use features

## Computer

Computer module for desktop UI automation.
Provides comprehensive desktop automation capabilities including mouse, keyboard,
window management, application management, and screen operations.

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
- `startCmd` (String): The command to start the application (e.g., "npm run dev", "notepad.exe")
- `workDirectory` (String): Optional working directory for the application (e.g., "/tmp/app/react-site-demo-1")
- `activity` (String): Optional activity name to launch (for mobile apps). Defaults to empty string.

**Returns:**
- `ProcessListResult`: ProcessListResult containing the list of processes started

### stopAppByPName

```java
public AppOperationResult stopAppByPName(String pname)
```

Stops an application by process name.

**Parameters:**
- `pname` (String): The process name of the application to stop (e.g., "notepad.exe", "chrome.exe")

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
- `stopCmd` (String): The command to stop the application (e.g., "taskkill /IM notepad.exe /F")

**Returns:**
- `AppOperationResult`: AppOperationResult containing success status and error message if any

### listVisibleApps

```java
public ProcessListResult listVisibleApps()
```

Lists all applications with visible windows.

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
- `button` (MouseButton): Mouse button to click. Defaults to LEFT

**Returns:**
- `BoolResult`: BoolResult containing success status and error message if any

### moveMouse

```java
public BoolResult moveMouse(int x, int y)
```

Moves the mouse to the specified coordinates.

**Parameters:**
- `x` (int): X coordinate
- `y` (int): Y coordinate

**Returns:**
- `BoolResult`: BoolResult containing success status and error message if any

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
- `OperationResult`: OperationResult containing cursor position data with keys 'x' and 'y', and error message if any

### inputText

```java
public BoolResult inputText(String text)
```

Types text into the currently focused input field.

**Parameters:**
- `text` (String): The text to input. Supports Unicode characters.

**Returns:**
- `BoolResult`: BoolResult containing success status and error message if any

### pressKeys

```java
public BoolResult pressKeys(List<String> keys, boolean hold)
```

```java
public BoolResult pressKeys(List<String> keys)
```

Presses the specified keys.

**Parameters:**
- `keys` (List<String>): List of keys to press (e.g., ["Ctrl", "a"])
- `hold` (boolean): Whether to hold the keys. Defaults to false

**Returns:**
- `BoolResult`: BoolResult containing success status and error message if any

### releaseKeys

```java
public BoolResult releaseKeys(List<String> keys)
```

Releases the specified keys.

**Parameters:**
- `keys` (List<String>): List of keys to release (e.g., ["Ctrl", "a"])

**Returns:**
- `BoolResult`: BoolResult containing success status and error message if any

### getScreenSize

```java
public OperationResult getScreenSize()
```

Gets the screen size and DPI scaling factor.

**Returns:**
- `OperationResult`: OperationResult containing screen size data with keys 'width', 'height', and 'dpiScalingFactor',
        and error message if any

### screenshot

```java
public OperationResult screenshot()
```

Takes a screenshot of the current screen.

**Returns:**
- `OperationResult`: OperationResult containing the path/URL to the screenshot and error message if any

### betaTakeScreenshot

```java
public ScreenshotBytesResult betaTakeScreenshot(String format)
```

```java
public ScreenshotBytesResult betaTakeScreenshot()
```

Capture the current screen and return raw image bytes (beta).

This API uses the MCP tool `screenshot` (wuying_capture) and expects the backend to return
a JSON string with top-level field `data` containing base64.

Supported formats:
- "png"
- "jpeg" (or "jpg")

**Parameters:**
- `format` (String): Output image format ("png", "jpeg", or "jpg")

**Returns:**
- `ScreenshotBytesResult`: ScreenshotBytesResult containing image bytes and error message if any

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
- `WindowListResult`: WindowListResult containing list of windows and error message if any

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
- `WindowInfoResult`: WindowInfoResult containing active window info and error message if any

### activateWindow

```java
public BoolResult activateWindow(int windowId)
```

Activates the specified window.

**Parameters:**
- `windowId` (int): The ID of the window to activate

**Returns:**
- `BoolResult`: BoolResult containing success status and error message if any

### closeWindow

```java
public BoolResult closeWindow(int windowId)
```

Closes the specified window.

**Parameters:**
- `windowId` (int): The ID of the window to close

**Returns:**
- `BoolResult`: BoolResult containing success status and error message if any

### maximizeWindow

```java
public BoolResult maximizeWindow(int windowId)
```

Maximizes the specified window.

**Parameters:**
- `windowId` (int): The ID of the window to maximize

**Returns:**
- `BoolResult`: BoolResult containing success status and error message if any

### minimizeWindow

```java
public BoolResult minimizeWindow(int windowId)
```

Minimizes the specified window.

**Parameters:**
- `windowId` (int): The ID of the window to minimize

**Returns:**
- `BoolResult`: BoolResult containing success status and error message if any

### restoreWindow

```java
public BoolResult restoreWindow(int windowId)
```

Restores the specified window.

**Parameters:**
- `windowId` (int): The ID of the window to restore

**Returns:**
- `BoolResult`: BoolResult containing success status and error message if any

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
- `BoolResult`: BoolResult containing success status and error message if any

### fullscreenWindow

```java
public BoolResult fullscreenWindow(int windowId)
```

Makes the specified window fullscreen.

**Parameters:**
- `windowId` (int): The ID of the window to make fullscreen

**Returns:**
- `BoolResult`: BoolResult containing success status and error message if any

### focusMode

```java
public BoolResult focusMode(boolean on)
```

Toggles focus mode on or off.

**Parameters:**
- `on` (boolean): True to enable focus mode, False to disable it

**Returns:**
- `BoolResult`: BoolResult containing success status and error message if any



## 💡 Best Practices

- Verify screen coordinates before mouse operations
- Use appropriate delays between UI interactions
- Handle window focus changes properly
- Take screenshots for verification and debugging
- Use keyboard shortcuts for efficient automation
- Clean up windows and applications after automation

