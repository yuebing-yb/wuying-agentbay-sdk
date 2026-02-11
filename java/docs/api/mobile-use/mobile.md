# 📱 Mobile API Reference

## Overview

The Mobile module provides mobile device automation capabilities including touch gestures,text input, app management, and screenshot capture. It supports Android device automation.


## 📚 Tutorial

[Mobile Use Guide](../../../../docs/guides/mobile-use/README.md)

Automate mobile applications

## 📋 Requirements

- Requires `mobile_latest` image for mobile automation features

## Mobile

Mobile module for mobile device UI automation and configuration.
Handles touch operations, UI element interactions, application management, screenshot capabilities,and mobile environment configuration operations.

### Constructor

```java
public Mobile(Session session)
```

### Methods

### tap

```java
public BoolResult tap(int x, int y)
```

Taps on the mobile screen at the specified coordinates.

**Parameters:**
- `x` (int): X coordinate in pixels
- `y` (int): Y coordinate in pixels

**Returns:**
- `BoolResult`: BoolResult Object with success status and error message if any

### swipe

```java
public BoolResult swipe(int startX, int startY, int endX, int endY, int durationMs)
```

```java
public BoolResult swipe(int startX, int startY, int endX, int endY)
```

Performs a swipe gesture from one point to another.

**Parameters:**
- `startX` (int): Starting X coordinate
- `startY` (int): Starting Y coordinate
- `endX` (int): Ending X coordinate
- `endY` (int): Ending Y coordinate
- `durationMs` (int): Duration of the swipe in milliseconds. Defaults to 300

**Returns:**
- `BoolResult`: BoolResult Result object containing success status and error message if any

### inputText

```java
public BoolResult inputText(String text)
```

Inputs text into the active field.

**Parameters:**
- `text` (String): The text to input

**Returns:**
- `BoolResult`: BoolResult Result object containing success status and error message if any

### sendKey

```java
public BoolResult sendKey(int key)
```

Sends a key press event.

**Parameters:**
- `key` (int): The key code to send. Supported key codes:
              - 3: HOME
              - 4: BACK
              - 24: VOLUME_UP
              - 25: VOLUME_DOWN
              - 26: POWER
              - 82: MENU

**Returns:**
- `BoolResult`: BoolResult Result object containing success status and error message if any

### getClickableUiElements

```java
public UIElementListResult getClickableUiElements(int timeoutMs)
```

```java
public UIElementListResult getClickableUiElements()
```

Retrieves all clickable UI elements within the specified timeout.

**Parameters:**
- `timeoutMs` (int): Timeout in milliseconds. Defaults to 2000

**Returns:**
- `UIElementListResult`: UIElementListResult containing clickable UI elements and error message if any

<p><strong>Note</strong>: Each returned element may include from backend which is not stable in type.
Use (dict with left/top/right/bottom) instead.</p>

### getAllUiElements

```java
public UIElementListResult getAllUiElements(int timeoutMs)
```

```java
public UIElementListResult getAllUiElements(int timeoutMs, String format)
```

```java
public UIElementListResult getAllUiElements()
```

Retrieves all UI elements within the specified timeout.

Supported formats:
- "json": parse and return elements
- "xml": return raw XML and an empty elements list

**Parameters:**
- `timeoutMs` (int): Timeout in milliseconds. Defaults to 2000.
- `format` (String): Output format of the underlying MCP tool ("json" or "xml"), default to "json"

**Returns:**
- `UIElementListResult`: UIElementListResult containing UI elements or raw XML

### getInstalledApps

```java
public InstalledAppListResult getInstalledApps(boolean startMenu, boolean desktop, boolean ignoreSystemApps)
```

```java
public InstalledAppListResult getInstalledApps()
```

Retrieves a list of installed applications.

**Parameters:**
- `startMenu` (boolean): Whether to include start menu applications
- `desktop` (boolean): Whether to include desktop applications
- `ignoreSystemApps` (boolean): Whether to ignore system applications

**Returns:**
- `InstalledAppListResult`: InstalledAppListResult containing the list of installed applications

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
- `workDirectory` (String): Optional working directory for the application
- `activity` (String): Optional activity name to launch (e.g. ".SettingsActivity" or "com.package/.Activity")

**Returns:**
- `ProcessListResult`: ProcessListResult containing the list of processes started

### stopAppByCmd

```java
public AppOperationResult stopAppByCmd(String stopCmd)
```

Stops an application by stop command.

**Parameters:**
- `stopCmd` (String): The command to stop the application

**Returns:**
- `AppOperationResult`: AppOperationResult containing the result of the operation

### screenshot

```java
public OperationResult screenshot()
```

Takes a screenshot of the current screen.

**Returns:**
- `OperationResult`: OperationResult containing the path/URL to the screenshot and error message if any

### betaTakeScreenshot

```java
public ScreenshotBytesResult betaTakeScreenshot()
```

```java
public ScreenshotBytesResult betaTakeScreenshot(String format)
```

Capture the current screen and return raw image bytes (beta).

Supported formats:
- "png"
- "jpeg" (or "jpg")

**Parameters:**
- `format` (String): Output image format ("png" or "jpeg")

**Returns:**
- `ScreenshotBytesResult`: ScreenshotBytesResult containing image bytes and error message if any

### betaTakeLongScreenshot

```java
public ScreenshotBytesResult betaTakeLongScreenshot(int maxScreens, String format, Integer quality)
```

```java
public ScreenshotBytesResult betaTakeLongScreenshot(int maxScreens, String format)
```

```java
public ScreenshotBytesResult betaTakeLongScreenshot(int maxScreens)
```

Takes a long screenshot (scroll + stitch) of the mobile device (beta).

Supported formats:
- "png"
- "jpeg" (or "jpg")

**Parameters:**
- `maxScreens` (int): Number of screens to stitch (range: [2, 10])
- `format` (String): Output image format ("png" or "jpeg")
- `quality` (Integer): JPEG quality (range: [1, 100]). Only used for jpeg.

**Returns:**
- `ScreenshotBytesResult`: ScreenshotBytesResult Object containing the screenshot image data (bytes) and metadata including `width` and `height` when provided by the backend.

### configure

```java
public void configure(MobileExtraConfig mobileConfig)
```

Configure mobile settings from MobileExtraConfig.
This method is typically called automatically during session creation when MobileExtraConfig is provided in CreateSessionParams. It can also be called manually to reconfigure mobile settings during a session.

**Parameters:**
- `mobileConfig` (MobileExtraConfig): mobile_config (MobileExtraConfig): Mobile configuration object with settings for:
                - lock_resolution (bool): Whether to lock device resolution
                - app_manager_rule (AppManagerRule): App whitelist/blacklist rules
                - hide_navigation_bar (bool): Whether to hide navigation bar
                - uninstall_blacklist (List[str]): Apps protected from uninstallation

### setResolutionLock

```java
public void setResolutionLock(boolean enable)
```

Set display resolution lock for mobile devices.

**Parameters:**
- `enable` (boolean): True to enable, False to disable

### setAppWhitelist

```java
public void setAppWhitelist(List<String> packageNames)
```

Set application whitelist.

**Parameters:**
- `packageNames` (List<String>): List of Android package names to whitelist

### setAppBlacklist

```java
public void setAppBlacklist(List<String> packageNames)
```

Set application blacklist.

**Parameters:**
- `packageNames` (List<String>): List of Android package names to blacklist

### setNavigationBarVisibility

```java
public void setNavigationBarVisibility(boolean hide)
```

Set navigation bar visibility for mobile devices.

**Parameters:**
- `hide` (boolean): True to hide navigation bar, False to show navigation bar

### setUninstallBlacklist

```java
public void setUninstallBlacklist(List<String> packageNames)
```

Set uninstall protection blacklist for mobile devices.

**Parameters:**
- `packageNames` (List<String>): List of Android package names to protect from uninstallation

### getAdbUrl

```java
public AdbUrlResult getAdbUrl(String adbkeyPub)
```

Retrieves the ADB connection URL for the mobile environment.
<p>
This method is only supported in mobile environments (mobile_latest image).
It uses the provided ADB public key to establish the connection and returns
the ADB connect URL.
</p>

**Parameters:**
- `adbkeyPub` (String): The ADB public key for connection authentication

**Returns:**
- `AdbUrlResult`: AdbUrlResult containing the ADB connection URL and request ID.Returns error if not in mobile environment.



## 💡 Best Practices

- Verify element coordinates before tap operations
- Use appropriate swipe durations for smooth gestures
- Wait for UI elements to load before interaction
- Take screenshots for verification and debugging
- Handle app installation and uninstallation properly
- Configure app whitelists/blacklists for security

## 🔗 Related Resources

- [Session API Reference](../../api/common-features/basics/session.md)

