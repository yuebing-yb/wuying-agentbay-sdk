# Browser API Reference

The Browser API provides methods for initializing and managing browser instances in the AgentBay cloud environment. It supports both headless and non-headless browsers with extensive configuration options including stealth mode, custom viewports, fingerprinting, proxies, and more.

## Overview

The Browser API is accessed through a session instance and provides methods for browser lifecycle management and connection to automation frameworks via Chrome DevTools Protocol (CDP).

```python
from agentbay import AgentBay
from agentbay.browser.browser import BrowserOption

# Access browser through session
session = result.session
browser_api = session.browser
```

## Classes

### BrowserOption

Configuration options for initializing a browser instance.

```python
class BrowserOption:
    def __init__(
        self,
        use_stealth: bool = False,
        user_agent: str = None,
        viewport: BrowserViewport = None,
        screen: BrowserScreen = None,
        fingerprint: BrowserFingerprint = None,
        solve_captchas: bool = False,
        proxies: Optional[list[BrowserProxy]] = None,
        extension_path: Optional[str] = "/tmp/extensions/",
        browser_type: Optional[Literal["chrome", "chromium"]] = None,
        cmd_args: Optional[list[str]] = None,
        default_navigate_url: Optional[str] = None,
    )
```

**Parameters:**

- `use_stealth` (bool): Enable stealth mode to avoid detection by anti-bot systems. Default: `False`
- `user_agent` (str | None): Custom user agent string for the browser. Default: `None`
- `viewport` (BrowserViewport | None): Browser viewport dimensions. Default: `None`
- `screen` (BrowserScreen | None): Screen dimensions. Default: `None`
- `fingerprint` (BrowserFingerprint | None): Browser fingerprint configuration. Default: `None`
- `solve_captchas` (bool): Automatically solve captchas during browsing. Default: `False`
- `proxies` (list[BrowserProxy] | None): List of proxy configurations (max 1). Default: `None`
- `extension_path` (str | None): Path to directory containing browser extensions. Default: `"/tmp/extensions/"`
- `browser_type` (Literal["chrome", "chromium"] | None): Browser type selection (computer use images only). Default: `None`
- `cmd_args` (list[str] | None): List of Chrome/Chromium command-line arguments to customize browser behavior. Default: `None`
- `default_navigate_url` (str | None): URL that the browser automatically navigates to after initialization. Recommended to use Chrome internal pages (e.g., `chrome://version/`) to avoid timeout issues. Default: `None`

**Methods:**

#### to_map()

Converts BrowserOption to a dictionary for API requests.

```python
def to_map(self) -> dict
```

**Returns:**
- `dict`: Dictionary representation of the browser options

**Example:**
```python
option = BrowserOption(use_stealth=True)
option_map = option.to_map()
```

#### from_map()

Creates BrowserOption from a dictionary.

```python
def from_map(self, m: dict = None) -> BrowserOption
```

**Parameters:**
- `m` (dict): Dictionary containing browser option data

**Returns:**
- `BrowserOption`: Self (for method chaining)

**Example:**
```python
option = BrowserOption()
option.from_map({"useStealth": True, "browserType": "chrome"})
```

### BrowserViewport

Defines the browser viewport dimensions.

```python
class BrowserViewport:
    def __init__(self, width: int, height: int):
        self.width = width
        self.height = height
```

**Parameters:**
- `width` (int): Viewport width in pixels
- `height` (int): Viewport height in pixels

**Common Viewport Sizes:**
```python
# Desktop
BrowserViewport(1920, 1080)
BrowserViewport(1366, 768)

# Laptop
BrowserViewport(1440, 900)

# Tablet
BrowserViewport(1024, 768)

# Mobile
BrowserViewport(375, 667)
BrowserViewport(414, 896)
```

### BrowserScreen

Defines the screen dimensions (usually same or larger than viewport).

```python
class BrowserScreen:
    def __init__(self, width: int, height: int):
        self.width = width
        self.height = height
```

**Parameters:**
- `width` (int): Screen width in pixels
- `height` (int): Screen height in pixels

### BrowserFingerprint

Configuration for browser fingerprint randomization.

```python
class BrowserFingerprint:
    def __init__(
        self,
        devices: list[str] = None,
        operating_systems: list[str] = None,
        locales: list[str] = None,
    ):
        self.devices = devices
        self.operating_systems = operating_systems
        self.locales = locales
```

**Parameters:**
- `devices` (list[str]): Device types - `["desktop", "mobile"]`
- `operating_systems` (list[str]): OS types - `["windows", "macos", "linux", "android", "ios"]`
- `locales` (list[str]): Locale strings - e.g., `["en-US", "zh-CN", "ja-JP"]`

**Example:**
```python
fingerprint = BrowserFingerprint(
    devices=["desktop"],
    operating_systems=["windows", "macos"],
    locales=["en-US", "en-GB"]
)
```

### BrowserProxy

Configuration for browser proxy settings.

```python
class BrowserProxy:
    def __init__(
        self,
        proxy_type: str,
        server: str = None,
        username: str = None,
        password: str = None,
        strategy: str = None,
        poll_size: int = None,
    ):
        self.proxy_type = proxy_type
        self.server = server
        self.username = username
        self.password = password
        self.strategy = strategy
        self.poll_size = poll_size
```

**Proxy Types:**

1. **Custom Proxy** (`proxy_type="custom"`):
   ```python
   proxy = BrowserProxy(
       proxy_type="custom",
       server="proxy.example.com:8080",
       username="user",
       password="pass"
   )
   ```

2. **WuYing Proxy** (`proxy_type="wuying"`):
   - **Restricted Strategy**: Single dedicated IP
     ```python
     proxy = BrowserProxy(
         proxy_type="wuying",
         strategy="restricted"
     )
     ```
   
   - **Polling Strategy**: Rotating IP pool
     ```python
     proxy = BrowserProxy(
         proxy_type="wuying",
         strategy="polling",
         poll_size=10
     )
     ```

**Validation Rules:**
- Maximum 1 proxy allowed in the `proxies` list
- `server` is required for `custom` type
- `strategy` is required for `wuying` type
- `poll_size` must be > 0 for `polling` strategy

## Browser Class

### Methods

#### initialize(option: BrowserOption) -> bool

Initializes the browser with the given options (synchronous).

```python
def initialize(self, option: BrowserOption) -> bool
```

**Parameters:**
- `option` (BrowserOption): Browser configuration options

**Returns:**
- `bool`: `True` if initialization was successful, `False` otherwise

**Raises:**
- `ValueError`: If browser option validation fails

**Example:**
```python
option = BrowserOption(
    use_stealth=True,
    user_agent="Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7)",
    viewport=BrowserViewport(1920, 1080)
)

success = session.browser.initialize(option)
if not success:
    raise RuntimeError("Browser initialization failed")
```

#### initialize_async(option: BrowserOption) -> bool

Initializes the browser with the given options (asynchronous).

```python
async def initialize_async(self, option: BrowserOption) -> bool
```

**Parameters:**
- `option` (BrowserOption): Browser configuration options

**Returns:**
- `bool`: `True` if initialization was successful, `False` otherwise

**Raises:**
- `ValueError`: If browser option validation fails

**Example:**
```python
import asyncio

async def main():
    option = BrowserOption(browser_type="chrome")
    success = await session.browser.initialize_async(option)
    if not success:
        raise RuntimeError("Browser initialization failed")

asyncio.run(main())
```

#### get_endpoint_url() -> str

Retrieves the CDP (Chrome DevTools Protocol) endpoint URL for connecting automation tools.

```python
def get_endpoint_url(self) -> str
```

**Returns:**
- `str`: The CDP WebSocket endpoint URL (e.g., `ws://host:port/devtools/browser/...`)

**Raises:**
- `RuntimeError`: If browser is not initialized

**Example:**
```python
endpoint_url = session.browser.get_endpoint_url()

# Use with Playwright
from playwright.async_api import async_playwright

async with async_playwright() as p:
    browser = await p.chromium.connect_over_cdp(endpoint_url)
```

#### is_initialized() -> bool

Checks if the browser has been initialized.

```python
def is_initialized(self) -> bool
```

**Returns:**
- `bool`: `True` if the browser is initialized, `False` otherwise

**Example:**
```python
if session.browser.is_initialized():
    print("Browser is ready")
else:
    print("Browser needs initialization")
```

#### get_option() -> BrowserOption

Retrieves the current browser configuration.

```python
def get_option(self) -> BrowserOption | None
```

**Returns:**
- `BrowserOption | None`: The current browser configuration, or `None` if not initialized

**Example:**
```python
option = session.browser.get_option()
if option:
    print(f"Browser type: {option.browser_type}")
```

## Complete Usage Example

### Basic Usage

```python
import os
import asyncio
from agentbay import AgentBay
from agentbay.session_params import CreateSessionParams
from agentbay.browser.browser import BrowserOption
from playwright.async_api import async_playwright

async def main():
    # Initialize AgentBay
    api_key = os.getenv("AGENTBAY_API_KEY")
    agent_bay = AgentBay(api_key=api_key)

    # Create session
    params = CreateSessionParams(image_id="browser_latest")
    result = agent_bay.create(params)
    if not result.success:
        raise RuntimeError(f"Failed to create session: {result.error_message}")

    session = result.session

    try:
        # Initialize browser with default options
        option = BrowserOption()
        ok = await session.browser.initialize_async(option)
        if not ok:
            raise RuntimeError("Browser initialization failed")

        # Get CDP endpoint
        endpoint_url = session.browser.get_endpoint_url()

        # Connect with Playwright
        async with async_playwright() as p:
            browser = await p.chromium.connect_over_cdp(endpoint_url)
            context = browser.contexts[0]
            page = await context.new_page()

            # Navigate and interact
            await page.goto("https://example.com")
            title = await page.title()
            print(f"Page title: {title}")

            await browser.close()

    finally:
        session.delete()

if __name__ == "__main__":
    asyncio.run(main())
```

### Advanced Configuration

```python
from agentbay.browser.browser import (
    BrowserOption,
    BrowserViewport,
    BrowserScreen,
    BrowserFingerprint,
    BrowserProxy
)

# Create custom browser configuration
option = BrowserOption(
    # Custom user agent
    user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) Chrome/120.0.0.0",
    
    # Viewport and screen
    viewport=BrowserViewport(width=1920, height=1080),
    screen=BrowserScreen(width=1920, height=1080),
    
    # Browser type (for computer use images)
    browser_type="chrome",
    
    # Stealth mode
    use_stealth=True,
    
    # Command-line arguments
    cmd_args=[
        "--disable-features=PrivacySandboxSettings4",
        "--disable-background-timer-throttling",
    ],
    
    # Default navigation URL (recommended: Chrome internal pages)
    default_navigate_url="chrome://version/",
    
    # Fingerprint randomization
    fingerprint=BrowserFingerprint(
        devices=["desktop"],
        operating_systems=["windows", "macos"],
        locales=["en-US"]
    ),
    
    # Proxy configuration
    proxies=[BrowserProxy(
        proxy_type="custom",
        server="proxy.example.com:8080",
        username="username",
        password="password"
    )]
)

# Initialize with custom options
success = await session.browser.initialize_async(option)
if not success:
    raise RuntimeError("Failed to initialize browser")
```

## Error Handling

### Common Errors

1. **Browser Not Initialized**
   ```python
   try:
       endpoint = session.browser.get_endpoint_url()
   except RuntimeError as e:
       # Error: "Browser not initialized"
       print("Initialize browser before getting endpoint")
   ```

2. **Invalid Configuration**
   ```python
   try:
       option = BrowserOption(browser_type="firefox")  # Invalid
       await session.browser.initialize_async(option)
   except ValueError as e:
       # Error: "browser_type must be 'chrome' or 'chromium'"
       print(f"Configuration error: {e}")
   ```

3. **Multiple Proxies**
   ```python
   try:
       option = BrowserOption(proxies=[proxy1, proxy2])
   except ValueError as e:
       # Error: "proxies list length must be limited to 1"
       print(f"Too many proxies: {e}")
   ```

### Best Practices

```python
# Check initialization status
if not session.browser.is_initialized():
    print("Browser not initialized")

# Always use try-finally for cleanup
try:
    ok = await session.browser.initialize_async(option)
    if not ok:
        raise RuntimeError("Initialization failed")
    
    # Use the browser...
    
finally:
    session.delete()

# Validate options if needed
try:
    option = BrowserOption(browser_type="chrome")
    # Validation happens in __init__
except ValueError as e:
    print(f"Invalid option: {e}")
```

## Browser Type Selection

> **Note:** The `browser_type` parameter is only available for **computer use images**. For standard browser images, the browser type is determined by the image.

### Choosing Browser Type

```python
# Use Chrome (Google Chrome)
option = BrowserOption(browser_type="chrome")

# Use Chromium (open-source)
option = BrowserOption(browser_type="chromium")

# Use default (None - let browser image decide)
option = BrowserOption()  # browser_type is None by default
```

### When to Use Each Type

**Chrome** (`"chrome"`):
- Need specific Chrome-only features
- Testing against actual Chrome browser
- Matching production Chrome environment

**Chromium** (`"chromium"`):
- Open-source preference
- Lighter resource usage
- Standard web automation

**Default** (`None`):
- Let the platform choose optimal browser
- Maximum compatibility
- Recommended for most use cases

## Integration with Automation Tools

### Playwright (Async)

```python
from playwright.async_api import async_playwright

# Get endpoint
endpoint_url = session.browser.get_endpoint_url()

# Connect Playwright
async with async_playwright() as p:
    browser = await p.chromium.connect_over_cdp(endpoint_url)
    context = browser.contexts[0]
    page = await context.new_page()
    
    # Use page...
    
    await browser.close()
```

### Playwright (Sync)

```python
from playwright.sync_api import sync_playwright

# Get endpoint
endpoint_url = session.browser.get_endpoint_url()

# Connect Playwright
with sync_playwright() as p:
    browser = p.chromium.connect_over_cdp(endpoint_url)
    context = browser.contexts[0]
    page = context.new_page()
    
    # Use page...
    
    browser.close()
```

### Puppeteer (via Node.js)

```python
# Get endpoint in Python
endpoint_url = session.browser.get_endpoint_url()
print(f"Use this endpoint in Node.js: {endpoint_url}")
```

```javascript
// In Node.js
const puppeteer = require('puppeteer-core');
const browser = await puppeteer.connect({
    browserWSEndpoint: 'ws://...' // endpoint from Python
});
```

## PageUseAgent Integration

The Browser class includes an `agent` property for AI-powered browser automation.

```python
from agentbay.browser.browser_agent import ActOptions

# Use PageUseAgent for natural language actions
act_result = await session.browser.agent.act_async(
    ActOptions(action="Click the sign in button"),
    page
)

if act_result.success:
    print(f"Action completed: {act_result.message}")
else:
    print(f"Action failed: {act_result.message}")
```

See the [PageUseAgent documentation](../../../../docs/guides/browser-use/advance-features/page-use-agent.md) for more details.

## Performance Considerations

### Resource Usage

- **Stealth Mode**: Adds overhead for anti-detection measures
- **Fingerprinting**: Randomization has minimal performance impact
- **Proxies**: May add latency depending on proxy location
- **Extensions**: Each extension increases memory usage

### Optimization Tips

1. **Reuse Sessions**: Keep sessions alive for multiple operations
2. **Appropriate Viewport**: Use actual target viewport size
3. **Minimal Extensions**: Only load necessary extensions
4. **Async Operations**: Use `initialize_async` for better concurrency

## Troubleshooting

### Browser Won't Initialize

```python
# Check session status
if not result.success:
    print(f"Session creation failed: {result.error_message}")

# Verify image supports browser
params = CreateSessionParams(image_id="browser_latest")

# Check initialization
success = await session.browser.initialize_async(option)
print(f"Initialization success: {success}")
```

### CDP Connection Fails

```python
# Ensure browser is initialized
if not session.browser.is_initialized():
    raise RuntimeError("Browser not initialized")

# Get and verify endpoint
endpoint_url = session.browser.get_endpoint_url()
print(f"Endpoint: {endpoint_url}")
```

### Configuration Issues

```python
# Check option values
option = BrowserOption(browser_type="chrome")
print(f"Browser type: {option.browser_type}")
print(f"Use stealth: {option.use_stealth}")

# Validate through initialization (validation happens in __init__)
try:
    option = BrowserOption(browser_type="firefox")  # Will raise ValueError
except ValueError as e:
    print(f"Invalid configuration: {e}")
```

## See Also

- [Browser Use Guide](../../../../docs/guides/browser-use/README.md) - Complete guide with examples
- [Core Features](../../../../docs/guides/browser-use/core-features.md) - Essential browser features
- [Advanced Features](../../../../docs/guides/browser-use/advance-features.md) - Advanced configuration
- [Browser Examples](../../examples/browser-use/browser/README.md) - Runnable example code
- [PageUseAgent API](../../../../docs/guides/browser-use/advance-features/page-use-agent.md) - AI-powered browser automation
- [Session Management](../common-features/basics/session.md) - Session lifecycle and management

