# Mobile Use Examples

This directory contains examples demonstrating mobile UI automation capabilities in AgentBay SDK.

## Overview

Mobile Use environment (`mobile_latest` image) provides cloud-based Android mobile automation with:
- UI element detection and interaction
- Touch gestures (tap, swipe, scroll)
- Text input and key events
- Screenshot capture
- Mobile application management
- ADB (Android Debug Bridge) integration

## Examples

### mobile_system/main.py

Comprehensive mobile automation example demonstrating:

1. **Application Management**
   - Get installed applications
   - Start applications
   - Stop applications
   - Application state monitoring

2. **UI Element Detection**
   - Get clickable UI elements
   - Get all UI elements (tree structure)
   - Element property inspection

3. **Touch Interactions**
   - Tap at coordinates
   - Swipe gestures
   - Multi-touch operations

4. **Text Input**
   - Input text to focused elements
   - Send key events
   - Keyboard operations

5. **Screenshot Capture**
   - Capture mobile screen
   - Save screenshots locally

### mobile_get_adb_url_example.py

ADB URL retrieval example:
- Get ADB connection URL
- Connect external tools to mobile session
- Remote debugging setup

## Prerequisites

- Python 3.8 or later
- AgentBay SDK installed: `pip install wuying-agentbay-sdk`
- Valid `AGENTBAY_API_KEY` environment variable

## Quick Start

```bash
# Set your API key
export AGENTBAY_API_KEY=your_api_key_here

# Run the main example
cd mobile_system
python main.py

# Run ADB URL example
cd ..
python mobile_get_adb_url_example.py
```

## Usage Examples

### Basic Mobile Automation

```python
from agentbay import AgentBay
from agentbay.session_params import CreateSessionParams
from agentbay.mobile import KeyCode

# Create mobile session
agent_bay = AgentBay(api_key="your_api_key")
params = CreateSessionParams(image_id="mobile_latest")
result = agent_bay.create(params)
session = result.session

# Get installed applications
apps_result = session.mobile.get_installed_apps(
    start_menu=True,
    desktop=False,
    ignore_system_apps=True
)

if apps_result.success:
    print(f"Found {len(apps_result.data)} applications")

# Start an application
start_result = session.mobile.start_app(
    "monkey -p com.android.settings -c android.intent.category.LAUNCHER 1"
)

# Get clickable UI elements
elements_result = session.mobile.get_clickable_ui_elements()
if elements_result.success:
    for element in elements_result.elements:
        print(f"Element: {element['text']}")

# Tap on screen
tap_result = session.mobile.tap(x=500, y=800)

# Swipe gesture
swipe_result = session.mobile.swipe(
    start_x=100,
    start_y=800,
    end_x=900,
    end_y=200,
    duration_ms=500
)

# Input text
input_result = session.mobile.input_text("Hello, AgentBay!")

# Send key event
key_result = session.mobile.send_key(KeyCode.HOME)

# Take screenshot
screenshot_result = session.mobile.screenshot()
if screenshot_result.success:
    with open("screenshot.png", "wb") as f:
        f.write(screenshot_result.data)

# Stop application
stop_result = session.mobile.stop_app_by_cmd(
    "am force-stop com.android.settings"
)

# Cleanup
agent_bay.delete(session)
```

### UI Element Tree Navigation

```python
# Get all UI elements
all_elements_result = session.mobile.get_all_ui_elements(timeout_ms=3000)

if all_elements_result.success:
    import json
    elements = json.loads(all_elements_result.elements)
    
    def print_element(element, indent=0):
        prefix = "  " * indent
        print(f"{prefix}- {element['className']}")
        print(f"{prefix}  text: '{element['text']}'")
        print(f"{prefix}  resourceId: '{element['resourceId']}'")
        
        for child in element.get('children', []):
            print_element(child, indent + 1)
    
    for element in elements:
        print_element(element)
```

### Application with Specific Activity

```python
# Start app with specific activity
app_package = "com.example.app"
app_activity = "com.example.app.MainActivity"
start_cmd = f"monkey -p {app_package} -c android.intent.category.LAUNCHER 1"

start_result = session.mobile.start_app(
    start_cmd=start_cmd,
    activity=app_activity
)

if start_result.success:
    for process in start_result.data:
        print(f"Started: {process.pname} (PID: {process.pid})")
```

### ADB Connection

```python
# Get ADB URL for external tools
adb_url_result = session.mobile.get_adb_url()
if adb_url_result.success:
    adb_url = adb_url_result.data
    print(f"ADB URL: {adb_url}")
    
    # Use with adb command line:
    # adb connect {adb_url}
```

## Features Demonstrated

### Application Management
- List installed applications
- Filter system applications
- Start applications with monkey command
- Start with specific activity
- Stop applications by command
- Monitor application processes

### UI Element Detection
- Get clickable elements only
- Get complete UI element tree
- Element property inspection
- Resource ID and text extraction
- Hierarchical element structure

### Touch Interactions
- Single tap at coordinates
- Long press
- Swipe gestures with duration
- Multi-point touch
- Drag and drop

### Text Input
- Input text to focused elements
- Send individual key events
- Special keys (HOME, BACK, etc.)
- Keyboard shortcuts

### Screenshot Operations
- Capture full screen
- Save to local file
- Base64 encoding support
- Image format handling

## API Methods Used

| Method | Purpose |
|--------|---------|
| `session.mobile.get_installed_apps()` | Get list of installed applications |
| `session.mobile.start_app()` | Start an application |
| `session.mobile.stop_app_by_cmd()` | Stop application by command |
| `session.mobile.get_clickable_ui_elements()` | Get clickable UI elements |
| `session.mobile.get_all_ui_elements()` | Get complete UI element tree |
| `session.mobile.tap()` | Tap at coordinates |
| `session.mobile.swipe()` | Perform swipe gesture |
| `session.mobile.input_text()` | Input text |
| `session.mobile.send_key()` | Send key event |
| `session.mobile.screenshot()` | Take screenshot |
| `session.mobile.get_adb_url()` | Get ADB connection URL |

## Common Use Cases

### 1. App Testing Automation

```python
# Start app
session.mobile.start_app("monkey -p com.myapp -c android.intent.category.LAUNCHER 1")

# Wait for app to load
import time
time.sleep(3)

# Get UI elements
elements = session.mobile.get_clickable_ui_elements()

# Find and tap login button
for element in elements.elements:
    if element['text'] == 'Login':
        session.mobile.tap(x=element['x'], y=element['y'])
        break

# Input credentials
session.mobile.input_text("user@example.com")
session.mobile.send_key(KeyCode.TAB)
session.mobile.input_text("password123")

# Submit
session.mobile.send_key(KeyCode.ENTER)

# Verify with screenshot
screenshot = session.mobile.screenshot()
```

### 2. UI Element Inspection

```python
# Get all elements
all_elements = session.mobile.get_all_ui_elements()

# Find specific element by text
def find_element_by_text(elements, text):
    for element in elements:
        if element['text'] == text:
            return element
        if 'children' in element:
            result = find_element_by_text(element['children'], text)
            if result:
                return result
    return None

target = find_element_by_text(all_elements.elements, "Settings")
if target:
    session.mobile.tap(x=target['x'], y=target['y'])
```

### 3. Gesture Automation

```python
# Swipe up (scroll down)
session.mobile.swipe(
    start_x=500,
    start_y=1500,
    end_x=500,
    end_y=500,
    duration_ms=300
)

# Swipe right (navigate)
session.mobile.swipe(
    start_x=100,
    start_y=800,
    end_x=900,
    end_y=800,
    duration_ms=200
)

# Long press
session.mobile.tap(x=500, y=800)  # Hold for long press
```

## Best Practices

1. **Wait for UI Load**: Add delays after starting apps or navigation
2. **Element Verification**: Verify elements exist before interaction
3. **Error Handling**: Check `result.success` for all operations
4. **Resource Cleanup**: Stop apps and delete sessions when done
5. **Screenshot Verification**: Use screenshots to verify UI state
6. **Coordinate Accuracy**: Use element coordinates from UI tree
7. **Gesture Timing**: Adjust swipe duration for different effects
8. **Key Events**: Use appropriate key codes for device buttons

## Related Documentation

- [Mobile Use Guide](../../../../docs/guides/mobile-use/README.md)
- [Mobile Application Management](../../../../docs/guides/mobile-use/mobile-application-management.md)
- [Mobile UI Automation](../../../../docs/guides/mobile-use/mobile-ui-automation.md)

## Troubleshooting

### Application Not Starting

If application fails to start:
- Verify package name is correct
- Check application is installed
- Ensure monkey command syntax is correct
- Try with specific activity

### UI Elements Not Found

If UI elements are missing:
- Wait longer for UI to load
- Check timeout parameter
- Verify app is in correct state
- Take screenshot to inspect UI

### Touch Interactions Not Working

If taps/swipes don't work:
- Verify coordinates are within screen bounds
- Check element is visible and enabled
- Ensure no overlay blocking interaction
- Add delay before interaction

### ADB Connection Issues

If ADB URL doesn't work:
- Verify session is mobile_latest image
- Check network connectivity
- Ensure ADB is installed locally
- Try reconnecting: `adb disconnect` then `adb connect`

### Screenshot Issues

If screenshots fail or are corrupted:
- Check session is active
- Verify sufficient memory
- Try smaller screen resolution
- Handle base64 decoding correctly

