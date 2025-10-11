# Browser API Reference

The Browser API provides methods for initializing and managing browser instances in the AgentBay cloud environment. It supports both headless and non-headless browsers with extensive configuration options including stealth mode, custom viewports, fingerprinting, proxies, and more.

## Overview

The Browser API is accessed through a session instance and provides methods for browser lifecycle management and connection to automation frameworks via Chrome DevTools Protocol (CDP).

```python
from agentbay import AgentBay
from agentbay.browser.browser import BrowserOption
from agentbay.browser.fingerprint import FingerprintFormat, BrowserFingerprintGenerator

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
        fingerprint_format: Optional[FingerprintFormat] = None,
        fingerprint_persistent: bool = False,
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
- `fingerprint` (BrowserFingerprint | None): Browser fingerprint configuration for random generation. Default: `None`
- `fingerprint_format` (FingerprintFormat | None): Complete fingerprint data to apply directly to the browser. Takes precedence over `fingerprint` parameter. Default: `None`
- `fingerprint_persistent` (bool): Enable fingerprint persistence across sessions using the same fingerprint context. Default: `False`
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

### FingerprintFormat

Complete fingerprint data structure containing detailed browser characteristics and HTTP headers.

```python
class FingerprintFormat:
    def __init__(self, fingerprint: Fingerprint, headers: Dict[str, str]):
        self.fingerprint = fingerprint
        self.headers = headers
```

**Parameters:**
- `fingerprint` (Fingerprint): Detailed browser fingerprint data including navigator, screen, and other properties
- `headers` (Dict[str, str]): HTTP headers to be sent with requests

**Methods:**

#### to_json()
Converts the fingerprint format to JSON string.

```python
def to_json(self, indent: int = 2, ensure_ascii: bool = False) -> str
```

#### from_json()
Creates FingerprintFormat from JSON string.

```python
@classmethod
def from_json(cls, json_str: str) -> FingerprintFormat
```

#### to_dict()
Converts to dictionary format.

```python
def to_dict(self) -> Dict[str, Any]
```

**Usage Examples:**

1. **Loading from file:**
```python
from agentbay.browser.fingerprint import FingerprintFormat

# Load fingerprint from JSON file
with open("fingerprint.json", "r") as f:
    fingerprint_format = FingerprintFormat.from_json(f.read())

option = BrowserOption(fingerprint_format=fingerprint_format)
```

2. **Generating from local browser:**
```python
from agentbay.browser.fingerprint import BrowserFingerprintGenerator

# Generate fingerprint from local Chrome installation
generator = BrowserFingerprintGenerator(headless=False)
fingerprint_format = await generator.generate_fingerprint()

option = BrowserOption(fingerprint_format=fingerprint_format)
```

3. **Saving generated fingerprint:**
```python
# Generate and save fingerprint for reuse
generator = BrowserFingerprintGenerator()
fingerprint_format = await generator.generate_fingerprint()

# Save to file
with open("my_fingerprint.json", "w") as f:
    f.write(fingerprint_format.to_json())
```

**Note:** When both `fingerprint` and `fingerprint_format` are provided, `fingerprint_format` takes precedence.

### BrowserFingerprintGenerator

Utility class for generating browser fingerprints from local Chrome installations.

```python
class BrowserFingerprintGenerator:
    def __init__(self, headless: bool = True, use_chrome_channel: bool = True):
        self.headless = headless
        self.use_chrome_channel = use_chrome_channel
```

**Parameters:**
- `headless` (bool): Whether to run the local browser in headless mode during fingerprint extraction. Default: `True`
- `use_chrome_channel` (bool): Whether to use Chrome channel for browser detection. Default: `True`

**Methods:**

#### generate_fingerprint()
Extracts comprehensive browser fingerprint from local Chrome installation.

```python
async def generate_fingerprint(self) -> Optional[FingerprintFormat]
```

**Returns:**
- `Optional[FingerprintFormat]`: Complete fingerprint data including navigator properties, screen dimensions, and HTTP headers, or `None` if generation failed

**Example:**
```python
import asyncio
from agentbay.browser.fingerprint import BrowserFingerprintGenerator

async def main():
    # Generate fingerprint from local Chrome (visible mode)
    generator = BrowserFingerprintGenerator(headless=False)
    fingerprint_format = await generator.generate_fingerprint()
    
    if fingerprint_format:
        print(f"User Agent: {fingerprint_format.fingerprint.navigator.userAgent}")
        print(f"Screen Size: {fingerprint_format.fingerprint.screen.width}x{fingerprint_format.fingerprint.screen.height}")
    else:
        print("Failed to generate fingerprint")

asyncio.run(main())
```

**Use Cases:**
- **Local-to-Remote Sync**: Capture your local browser's fingerprint and apply it to remote sessions
- **Fingerprint Collection**: Generate multiple fingerprints for testing purposes
- **Custom Fingerprint Creation**: Extract specific characteristics from different browser configurations

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

#### screenshot(page, full_page: bool = False, **options) -> bytes

Takes a screenshot of the specified page with enhanced options and error handling (asynchronous).

This method captures screenshots of web pages with advanced features including:
- Full page screenshots (scrolling to capture entire content)
- Custom image formats (PNG, JPEG)
- Quality control for JPEG images
- Enhanced loading state management
- Lazy-loaded content handling
- Background image loading

```python
async def screenshot(self, page, full_page: bool = False, **options) -> bytes
```

**Parameters:**
- `page` (Page): The Playwright Page object to take a screenshot of. This is a required parameter.
- `full_page` (bool): Whether to capture the full scrollable page. Defaults to `False`.
- `**options`: Additional screenshot options that will override defaults.
  Common options include:
  - `type` (str): Image type, either `'png'` or `'jpeg'` (default: `'png'`)
  - `quality` (int): Quality of the image, between 0-100 (jpeg only)
  - `timeout` (int): Maximum time in milliseconds (default: 60000)
  - `animations` (str): How to handle animations (default: `'disabled'`)
  - `caret` (str): How to handle the caret (default: `'hide'`)
  - `scale` (str): Scale setting (default: `'css'`)

**Returns:**
- `bytes`: Screenshot data as bytes.

**Raises:**
- `BrowserError`: If browser is not initialized.
- `ValueError`: If page is None.
- `RuntimeError`: If screenshot capture fails.

**Example:**
```python
import asyncio
from playwright.async_api import async_playwright

async def capture_screenshots():
    # Get browser endpoint and connect with Playwright
    endpoint_url = session.browser.get_endpoint_url()
    async with async_playwright() as p:
        browser = await p.chromium.connect_over_cdp(endpoint_url)
        context = browser.contexts[0]
        page = await context.new_page()
        
        # Navigate to a page
        await page.goto("https://example.com")
        
        # Take a simple screenshot (viewport only)
        screenshot_data = await session.browser.screenshot(page)
        with open("screenshot.png", "wb") as f:
            f.write(screenshot_data)
        
        # Take a full page screenshot
        full_page_data = await session.browser.screenshot(page, full_page=True)
        with open("full_page.png", "wb") as f:
            f.write(full_page_data)
        
        # Take a screenshot with custom options
        custom_screenshot = await session.browser.screenshot(
            page,
            full_page=False,
            type="jpeg",
            quality=80,
            timeout=30000
        )
        with open("custom_screenshot.jpg", "wb") as f:
            f.write(custom_screenshot)
        
        await browser.close()

asyncio.run(capture_screenshots())
```

**Advanced Usage:**
```python
# Handle errors gracefully
try:
    screenshot_data = await session.browser.screenshot(page)
    # Process screenshot data...
except BrowserError as e:
    print(f"Browser not initialized: {e}")
except RuntimeError as e:
    print(f"Screenshot failed: {e}")
except Exception as e:
    print(f"Unexpected error: {e}")
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
    
    # Fingerprint randomization (generates random fingerprint)
    fingerprint=BrowserFingerprint(
        devices=["desktop"],
        operating_systems=["windows", "macos"],
        locales=["en-US"]
    ),
    
    # OR use specific fingerprint format (takes precedence over fingerprint)
    # fingerprint_format=my_fingerprint_format,
    
    # Enable fingerprint persistence across sessions
    fingerprint_persistent=True,
    
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

### Fingerprint Usage Examples

#### 1. Random Fingerprint Generation

```python
from agentbay.browser.browser import BrowserOption, BrowserFingerprint

# Generate random fingerprint based on criteria
option = BrowserOption(
    use_stealth=True,
    fingerprint=BrowserFingerprint(
        devices=["desktop"],
        operating_systems=["windows"],
        locales=["en-US", "en-GB"]
    )
)

success = await session.browser.initialize_async(option)
```

#### 2. Local Browser Fingerprint Sync

```python
import asyncio
from agentbay.browser.fingerprint import BrowserFingerprintGenerator
from agentbay.browser.browser import BrowserOption

async def sync_local_fingerprint():
    # Generate fingerprint from local Chrome
    generator = BrowserFingerprintGenerator(headless=False)
    fingerprint_format = await generator.generate_fingerprint()
    
    if not fingerprint_format:
        raise RuntimeError("Failed to generate local fingerprint")
    
    # Apply local fingerprint to remote browser
    option = BrowserOption(
        use_stealth=True,
        fingerprint_format=fingerprint_format
    )
    
    success = await session.browser.initialize_async(option)
    if success:
        print("Local fingerprint synced to remote browser")

asyncio.run(sync_local_fingerprint())
```

#### 3. Self-Customized Fingerprint Generation

```python
import os
from agentbay.browser.fingerprint import FingerprintFormat
from agentbay.browser.browser import BrowserOption

# Load fingerprint from local JSON file
fingerprint_file = "path/to/fingerprint.json"
with open(fingerprint_file, "r") as f:
    fingerprint_format = FingerprintFormat.from_json(f.read())

# Use loaded fingerprint
option = BrowserOption(
    use_stealth=True,
    fingerprint_format=fingerprint_format
)

success = await session.browser.initialize_async(option)
```

#### 4. Fingerprint Persistence Across Sessions

```python
from agentbay import AgentBay
from agentbay.session_params import CreateSessionParams, BrowserContext
from agentbay.browser.browser import BrowserOption, BrowserFingerprint, BrowserFingerprintContext

# Create contexts for persistence
agent_bay = AgentBay(api_key="your_api_key")

# Create browser context
browser_context_result = agent_bay.context.get("my-browser-context", create_if_not_exists=True)
browser_context = BrowserContext(browser_context_result.context.id)

# Create fingerprint context
fp_context_result = agent_bay.context.get("my-fingerprint-context", create_if_not_exists=True)
fp_context = BrowserFingerprintContext(fp_context_result.context.id)
browser_context.fingerprint_context = fp_context

# First session - generate and persist fingerprint
params1 = CreateSessionParams(
    image_id="browser_latest",
    browser_context=browser_context
)
session1 = agent_bay.create(params1).session

option1 = BrowserOption(
    use_stealth=True,
    fingerprint_persistent=True,
    fingerprint=BrowserFingerprint(
        devices=["desktop"],
        operating_systems=["windows"],
        locales=["en-US"]
    )
)
await session1.browser.initialize_async(option1)
# ... use browser ...
agent_bay.delete(session1, sync_context=True)  # Save fingerprint to context

# Second session - reuse persisted fingerprint
params2 = CreateSessionParams(
    image_id="browser_latest",
    browser_context=browser_context
)
session2 = agent_bay.create(params2).session

option2 = BrowserOption(
    use_stealth=True,
    fingerprint_persistent=True  # Will load previously saved fingerprint
)
await session2.browser.initialize_async(option2)
# Browser will have the same fingerprint as session1
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

- **Fingerprinting**: Minimal performance impact
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
- [Advanced Features](../../../../docs/guides/browser-use/advance-features.md) - Advanced configuration including fingerprinting
- [Browser Fingerprint Examples](../../examples/browser-use/browser/) - Fingerprint usage examples
- [Browser Examples](../../examples/browser-use/browser/README.md) - Runnable example code
- [PageUseAgent API](../../../../docs/guides/browser-use/advance-features/page-use-agent.md) - AI-powered browser automation
- [Session Management](../common-features/basics/session.md) - Session lifecycle and management

