# Mobile API Reference

## 📱 Related Tutorial

- [Mobile Use Guide](../../../../../docs/guides/mobile-use/README.md) - Automate mobile applications

## Overview

The Mobile module provides mobile device automation capabilities including touch gestures,
text input, app management, and screenshot capture. It supports Android device automation.


## Requirements

- Requires `mobile_latest` image for mobile automation features



Mobile module for mobile device UI automation and configuration.
Handles touch operations, UI element interactions, application management, screenshot capabilities,
and mobile environment configuration operations.

#### logger

```python
logger = get_logger("mobile")
```

## UIElementListResult Objects

```python
class UIElementListResult(ApiResponse)
```

Result of UI element listing operations.

## KeyCode Objects

```python
class KeyCode()
```

Key codes for mobile device input.

#### HOME

```python
HOME = 3
```

#### BACK

```python
BACK = 4
```

#### VOLUME\_UP

```python
VOLUME_UP = 24
```

#### VOLUME\_DOWN

```python
VOLUME_DOWN = 25
```

#### POWER

```python
POWER = 26
```

#### MENU

```python
MENU = 82
```

## Mobile Objects

```python
class Mobile(BaseService)
```

Handles mobile UI automation operations and configuration in the AgentBay cloud environment.
Provides comprehensive mobile automation capabilities including touch operations,
UI element interactions, application management, screenshot capabilities,
and mobile environment configuration operations.

#### tap

```python
def tap(x: int, y: int) -> BoolResult
```

Taps on the mobile screen at the specified coordinates.

**Arguments**:

- `x` _int_ - X coordinate in pixels.
- `y` _int_ - Y coordinate in pixels.
  

**Returns**:

- `BoolResult` - Object with success status and error message if any.
  

**Example**:

```python
from agentbay import AgentBay

agent_bay = AgentBay(api_key="your_api_key")
result = agent_bay.create()

if result.success:
    session = result.session
    mobile = session.mobile

    # Tap at coordinates
    tap_result = mobile.tap(500, 1000)
    if tap_result.success:
        print("Tap successful")

    session.delete()
```
  

**See Also**:

  swipe, long_press

#### swipe

```python
def swipe(start_x: int,
          start_y: int,
          end_x: int,
          end_y: int,
          duration_ms: int = 300) -> BoolResult
```

Performs a swipe gesture from one point to another.

**Arguments**:

- `start_x` _int_ - Starting X coordinate.
- `start_y` _int_ - Starting Y coordinate.
- `end_x` _int_ - Ending X coordinate.
- `end_y` _int_ - Ending Y coordinate.
- `duration_ms` _int, optional_ - Duration of the swipe in milliseconds.
  Defaults to 300.
  

**Returns**:

- `BoolResult` - Result object containing success status and error message if any.

#### input\_text

```python
def input_text(text: str) -> BoolResult
```

Inputs text into the active field.

**Arguments**:

- `text` _str_ - The text to input.
  

**Returns**:

- `BoolResult` - Result object containing success status and error message if any.

#### send\_key

```python
def send_key(key: int) -> BoolResult
```

Sends a key press event.

**Arguments**:

- `key` _int_ - The key code to send. Supported key codes are:
  - 3 : HOME
  - 4 : BACK
  - 24 : VOLUME UP
  - 25 : VOLUME DOWN
  - 26 : POWER
  - 82 : MENU
  

**Returns**:

- `BoolResult` - Result object containing success status and error message if any.

#### get\_clickable\_ui\_elements

```python
def get_clickable_ui_elements(timeout_ms: int = 2000) -> UIElementListResult
```

Retrieves all clickable UI elements within the specified timeout.

**Arguments**:

- `timeout_ms` _int, optional_ - Timeout in milliseconds. Defaults to 2000.
  

**Returns**:

- `UIElementListResult` - Result object containing clickable UI elements and
  error message if any.

#### get\_all\_ui\_elements

```python
def get_all_ui_elements(timeout_ms: int = 2000) -> UIElementListResult
```

Retrieves all UI elements within the specified timeout.

**Arguments**:

- `timeout_ms` _int, optional_ - Timeout in milliseconds. Defaults to 2000.
  

**Returns**:

- `UIElementListResult` - Result object containing UI elements and error
  message if any.

#### get\_installed\_apps

```python
def get_installed_apps(start_menu: bool, desktop: bool,
                       ignore_system_apps: bool) -> InstalledAppListResult
```

Retrieves a list of installed applications.

**Arguments**:

- `start_menu` _bool_ - Whether to include start menu applications.
- `desktop` _bool_ - Whether to include desktop applications.
- `ignore_system_apps` _bool_ - Whether to ignore system applications.
  

**Returns**:

- `InstalledAppListResult` - The result containing the list of installed
  applications.

#### start\_app

```python
def start_app(start_cmd: str,
              work_directory: str = "",
              activity: str = "") -> ProcessListResult
```

Starts an application with the given command, optional working directory and
optional activity.

**Arguments**:

- `start_cmd` _str_ - The command to start the application.
- `work_directory` _str, optional_ - The working directory for the application.
- `activity` _str, optional_ - Activity name to launch (e.g. ".SettingsActivity"
  or "com.package/.Activity"). Defaults to "".
  

**Returns**:

- `ProcessListResult` - The result containing the list of processes started.

#### stop\_app\_by\_cmd

```python
def stop_app_by_cmd(stop_cmd: str) -> AppOperationResult
```

Stops an application by stop command.

**Arguments**:

- `stop_cmd` _str_ - The command to stop the application.
  

**Returns**:

- `AppOperationResult` - The result of the operation.

#### screenshot

```python
def screenshot() -> OperationResult
```

Takes a screenshot of the current screen.

**Returns**:

- `OperationResult` - Result object containing the path to the screenshot
  and error message if any.

#### configure

```python
def configure(mobile_config)
```

Configure mobile settings from MobileExtraConfig.

**Arguments**:

- `mobile_config` - MobileExtraConfig object containing mobile configuration.

#### set\_resolution\_lock

```python
def set_resolution_lock(enable: bool)
```

Set display resolution lock for mobile devices.

**Arguments**:

- `enable` _bool_ - True to enable, False to disable.

#### set\_app\_whitelist

```python
def set_app_whitelist(package_names: List[str])
```

Set application whitelist.

**Arguments**:

- `package_names` _List[str]_ - List of Android package names to whitelist.

#### set\_app\_blacklist

```python
def set_app_blacklist(package_names: List[str])
```

Set application blacklist.

**Arguments**:

- `package_names` _List[str]_ - List of Android package names to blacklist.

#### set\_navigation\_bar\_visibility

```python
def set_navigation_bar_visibility(hide: bool)
```

Set navigation bar visibility for mobile devices.

**Arguments**:

- `hide` _bool_ - True to hide navigation bar, False to show navigation bar.

#### set\_uninstall\_blacklist

```python
def set_uninstall_blacklist(package_names: List[str])
```

Set uninstall protection blacklist for mobile devices.

**Arguments**:

- `package_names` _List[str]_ - List of Android package names to protect from uninstallation.

#### get\_adb\_url

```python
def get_adb_url(adbkey_pub: str) -> AdbUrlResult
```

Retrieves the ADB connection URL for the mobile environment.

This method is only supported in mobile environments (mobile_latest image).
It uses the provided ADB public key to establish the connection and returns
the ADB connect URL.

**Arguments**:

- `adbkey_pub` _str_ - The ADB public key for connection authentication.
  

**Returns**:

- `AdbUrlResult` - Result object containing the ADB connection URL
- `(format` - "adb connect <IP>:<Port>") and request ID.
  Returns error if not in mobile environment.
  

**Raises**:

- `SessionError` - If the session is not in mobile environment.

## Best Practices

1. Verify element coordinates before tap operations
2. Use appropriate swipe durations for smooth gestures
3. Wait for UI elements to load before interaction
4. Take screenshots for verification and debugging
5. Handle app installation and uninstallation properly
6. Configure app whitelists/blacklists for security

## Related Resources

- [Session API Reference](../common-features/basics/session.md)

---

*Documentation generated automatically from source code using pydoc-markdown.*
