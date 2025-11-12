# Computer Use Examples

This directory contains examples demonstrating Windows desktop automation capabilities in AgentBay SDK.

## Overview

Computer Use environment (`windows_latest` image) provides cloud-based Windows desktop automation with:
- Application management (start, stop, list)
- Window operations (maximize, minimize, resize, close)
- Focus management
- Desktop UI automation workflows
- Process monitoring

## Examples

### windows_app_management_example.py

Comprehensive Windows application management example demonstrating:

1. **Finding Installed Applications**
   - Discover all applications in Windows start menu
   - Filter system applications
   - Search for specific applications

2. **Launching Applications**
   - Start applications by command
   - Monitor spawned processes
   - Track process IDs

3. **Monitoring Running Applications**
   - List currently visible applications
   - Get application window information
   - Track application states

4. **Stopping Applications**
   - Stop by process ID (PID)
   - Stop by process name
   - Graceful termination

## Prerequisites

- Python 3.8 or later
- AgentBay SDK installed: `pip install wuying-agentbay-sdk`
- Valid `AGENTBAY_API_KEY` environment variable

## Quick Start

```bash
# Set your API key
export AGENTBAY_API_KEY=your_api_key_here

# Run the example
cd computer
python windows_app_management_example.py
```

## Usage Examples

### Basic Application Management

```python
from agentbay import AgentBay
from agentbay.session_params import CreateSessionParams

# Create Windows session
agent_bay = AgentBay(api_key="your_api_key")
params = CreateSessionParams(image_id="windows_latest")
result = agent_bay.create(params)
session = result.session

# Get installed applications
apps_result = session.computer.get_installed_apps(
    start_menu=True,
    desktop=False,
    ignore_system_apps=True
)

if apps_result.success:
    for app in apps_result.data:
        print(f"App: {app.name}")
        print(f"Command: {app.start_cmd}")

# Start an application
start_result = session.computer.start_app("C:\\Windows\\System32\\notepad.exe")
if start_result.success:
    for process in start_result.data:
        print(f"Started: {process.pname} (PID: {process.pid})")

# List visible applications
visible_result = session.computer.list_visible_apps()
if visible_result.success:
    for app in visible_result.data:
        print(f"Visible: {app.pname} (PID: {app.pid})")

# Stop application by PID
stop_result = session.computer.stop_app_by_pid(process.pid)

# Stop application by name
stop_result = session.computer.stop_app_by_pname("notepad.exe")

# Cleanup
agent_bay.delete(session)
```

### Window Management

```python
# List all windows
windows_result = session.window.list_windows()
if windows_result.success:
    for window in windows_result.data:
        print(f"Window: {window.title}")
        print(f"Handle: {window.handle}")

# Focus a window
focus_result = session.window.focus_window(window_handle)

# Maximize window
maximize_result = session.window.maximize_window(window_handle)

# Minimize window
minimize_result = session.window.minimize_window(window_handle)

# Close window
close_result = session.window.close_window(window_handle)
```

### UI Automation

```python
# Take screenshot
screenshot_result = session.ui.screenshot()
if screenshot_result.success:
    with open("screenshot.png", "wb") as f:
        f.write(screenshot_result.data)

# Click at coordinates
click_result = session.ui.click(x=100, y=200)

# Type text
type_result = session.ui.type("Hello, World!")

# Send key
from agentbay.mobile import KeyCode
key_result = session.ui.key(KeyCode.ENTER)
```

## Features Demonstrated

### Application Discovery
- Find installed applications in start menu
- Filter system applications
- Search by application name
- Get application start commands

### Process Management
- Start applications by command
- Monitor process creation
- Track process IDs and names
- List visible applications with windows

### Application Control
- Stop applications by PID
- Stop applications by process name
- Graceful vs forceful termination
- Error handling for process operations

### Window Operations
- List all windows
- Focus specific windows
- Maximize/minimize windows
- Close windows
- Get window information

## API Methods Used

| Method | Purpose |
|--------|---------|
| `session.computer.get_installed_apps()` | Get list of installed applications |
| `session.computer.start_app()` | Start an application |
| `session.computer.list_visible_apps()` | List currently visible applications |
| `session.computer.stop_app_by_pid()` | Stop application by process ID |
| `session.computer.stop_app_by_pname()` | Stop application by process name |
| `session.window.list_windows()` | List all windows |
| `session.window.focus_window()` | Focus a specific window |
| `session.window.maximize_window()` | Maximize a window |
| `session.window.minimize_window()` | Minimize a window |
| `session.window.close_window()` | Close a window |
| `session.ui.screenshot()` | Take a screenshot |
| `session.ui.click()` | Click at coordinates |
| `session.ui.type()` | Type text |
| `session.ui.key()` | Send keyboard key |

## Common Use Cases

### 1. Automated Testing
```python
# Start application
session.computer.start_app("C:\\MyApp\\app.exe")

# Wait for window
import time
time.sleep(2)

# Interact with UI
session.ui.click(x=200, y=300)
session.ui.type("test data")
session.ui.key(KeyCode.ENTER)

# Verify results
screenshot = session.ui.screenshot()
```

### 2. Application Monitoring
```python
# Monitor running applications
while True:
    visible_apps = session.computer.list_visible_apps()
    if visible_apps.success:
        print(f"Running apps: {len(visible_apps.data)}")
    time.sleep(60)
```

### 3. Automated Workflows
```python
# Open Excel
session.computer.start_app("excel.exe")
time.sleep(3)

# Type data
session.ui.type("=SUM(A1:A10)")
session.ui.key(KeyCode.ENTER)

# Save
session.ui.key(KeyCode.CTRL, KeyCode.S)
```

## Best Practices

1. **Wait for Application Load**: Add delays after starting applications
2. **Error Handling**: Always check `result.success` before proceeding
3. **Resource Cleanup**: Stop applications and delete sessions when done
4. **Process Identification**: Use PIDs for reliable process management
5. **Retry Logic**: Implement retries for resource creation delays
6. **Window Focus**: Ensure window has focus before UI interactions
7. **Screenshot Verification**: Use screenshots to verify UI state

## Related Documentation

- [Computer Use Guide](../../../../docs/guides/computer-use/README.md)
- [Computer Application Management](../../../../docs/guides/computer-use/computer-application-management.md)
- [Computer UI Automation](../../../../docs/guides/computer-use/computer-ui-automation.md)
- [Window Management](../../../../docs/guides/computer-use/window-management.md)

## Troubleshooting

### Resource Creation Delay

If you see "Resource creation in progress" message:
- Wait 90 seconds and retry
- This is normal for Windows session initialization
- Consider session pooling for production

### Application Not Found

If application is not in the list:
- Check application is installed in start menu
- Try using full path to executable
- Verify application name spelling

### Application Won't Start

If application fails to start:
- Verify start command is correct
- Check application permissions
- Ensure application is compatible with Windows version
- Review application dependencies

### Window Operations Fail

If window operations don't work:
- Verify window handle is valid
- Check window still exists
- Ensure window is not minimized (for some operations)
- Wait for window to be ready

### UI Automation Issues

If UI interactions fail:
- Take screenshot to verify UI state
- Ensure window has focus
- Add delays between actions
- Verify coordinates are correct
- Check for popup dialogs blocking interaction

