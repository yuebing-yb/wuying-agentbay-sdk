# Browser API Reference

## 🌐 Related Tutorial

- [Browser Use Guide](../../../../docs/guides/browser-use/README.md) - Complete guide to browser automation

## Overview

The Browser module provides comprehensive browser automation capabilities including navigation, element interaction,
screenshot capture, and content extraction. It enables automated testing and web scraping workflows.


## Requirements

- Requires `browser_latest` image for browser automation features



```python
class BrowserFingerprintContext()
```

Browser fingerprint context configuration.

## BrowserProxy Objects

```python
class BrowserProxy()
```

Browser proxy configuration.
Supports two types of proxy: custom proxy, wuying proxy.
wuying proxy support two strategies: restricted and polling.

## BrowserViewport Objects

```python
class BrowserViewport()
```

Browser viewport options.

## BrowserScreen Objects

```python
class BrowserScreen()
```

Browser screen options.

## BrowserFingerprint Objects

```python
class BrowserFingerprint()
```

Browser fingerprint options.

## BrowserOption Objects

```python
class BrowserOption()
```

browser initialization options.

## Browser Objects

```python
class Browser(BaseService)
```

Browser provides browser-related operations for the session.

#### initialize

```python
def initialize(option: "BrowserOption") -> bool
```

Initialize the browser instance with the given options.
Returns True if successful, False otherwise.

**Arguments**:

- `option` _BrowserOption_ - Browser configuration options.
  

**Returns**:

    bool: True if initialization was successful, False otherwise.
  

**Example**:

```python
from agentbay import AgentBay
from agentbay.browser.browser import BrowserOption, BrowserViewport

agent_bay = AgentBay(api_key="your_api_key")

def initialize_browser():
    try:
        result = agent_bay.create()
        if result.success:
            session = result.session

            # Initialize browser with default options
            browser_option = BrowserOption()
            success = session.browser.initialize(browser_option)
            if success:
                print("Browser initialized successfully")
                # Output: Browser initialized successfully
            else:
                print("Browser initialization failed")

            # Initialize with custom viewport
            browser_option = BrowserOption(
                use_stealth=True,
                viewport=BrowserViewport(width=1920, height=1080)
            )
            success = session.browser.initialize(browser_option)
            if success:
                print("Browser initialized with custom viewport")
                # Output: Browser initialized with custom viewport

            session.delete()
    except Exception as e:
        print(f"Error: {e}")

initialize_browser()
```

#### initialize\_async

```python
async def initialize_async(option: "BrowserOption") -> bool
```

Initialize the browser instance with the given options asynchronously.
Returns True if successful, False otherwise.

**Arguments**:

- `option` _BrowserOption_ - Browser configuration options.
  

**Returns**:

    bool: True if initialization was successful, False otherwise.
  

**Example**:

```python
from agentbay import AgentBay
from agentbay.browser.browser import BrowserOption, BrowserViewport
import asyncio

agent_bay = AgentBay(api_key="your_api_key")

async def initialize_browser_async():
    try:
        result = agent_bay.create()
        if result.success:
            session = result.session

            # Initialize browser asynchronously with default options
            browser_option = BrowserOption()
            success = await session.browser.initialize_async(browser_option)
            if success:
                print("Browser initialized successfully")
                # Output: Browser initialized successfully
            else:
                print("Browser initialization failed")

            session.delete()
    except Exception as e:
        print(f"Error: {e}")

asyncio.run(initialize_browser_async())
```

#### destroy

```python
def destroy()
```

Destroy the browser instance.

**Example**:

```python
from agentbay import AgentBay
from agentbay.browser.browser import BrowserOption

agent_bay = AgentBay(api_key="your_api_key")

def demonstrate_browser_destroy():
    try:
        result = agent_bay.create()
        if result.success:
            session = result.session

            # Initialize the browser
            browser_option = BrowserOption(use_stealth=True)
            success = session.browser.initialize(browser_option)

            if success:
                print("Browser initialized successfully")
                # Output: Browser initialized successfully

                # Check if browser is initialized
                if session.browser.is_initialized():
                    print("Browser is active")
                    # Output: Browser is active

                # Destroy the browser instance
                session.browser.destroy()
                print("Browser destroyed")
                # Output: Browser destroyed

            session.delete()
    except Exception as e:
        print(f"Error: {e}")

demonstrate_browser_destroy()
```

#### screenshot

```python
async def screenshot(page, full_page: bool = False, **options) -> bytes
```

Takes a screenshot of the specified page with enhanced options and error handling.
This is the async version of the screenshot method.

**Arguments**:

- `page` _Page_ - The Playwright Page object to take a screenshot of. This is a required parameter.
- `full_page` _bool_ - Whether to capture the full scrollable page. Defaults to False.
    **options: Additional screenshot options that will override defaults.
  Common options include:
  - type (str): Image type, either 'png' or 'jpeg' (default: 'png')
  - quality (int): Quality of the image, between 0-100 (jpeg only)
  - timeout (int): Maximum time in milliseconds (default: 60000)
  - animations (str): How to handle animations (default: 'disabled')
  - caret (str): How to handle the caret (default: 'hide')
  - scale (str): Scale setting (default: 'css')
  

**Returns**:

    bytes: Screenshot data as bytes.
  

**Raises**:

    BrowserError: If browser is not initialized.
    RuntimeError: If screenshot capture fails.

#### get\_endpoint\_url

```python
def get_endpoint_url() -> str
```

Returns the endpoint URL if the browser is initialized, otherwise raises an exception.
When initialized, always fetches the latest CDP url from session.get_link().

**Returns**:

    str: The browser CDP endpoint URL.
  

**Raises**:

    BrowserError: If browser is not initialized or endpoint URL cannot be retrieved.
  

**Example**:

```python
from agentbay import AgentBay
from agentbay.browser.browser import BrowserOption

agent_bay = AgentBay(api_key="your_api_key")

def get_browser_endpoint():
    try:
        result = agent_bay.create()
        if result.success:
            session = result.session

            # Initialize the browser
            browser_option = BrowserOption()
            success = session.browser.initialize(browser_option)

            if success:
                # Get the browser endpoint URL
                endpoint_url = session.browser.get_endpoint_url()
                print(f"Browser endpoint URL: {endpoint_url}")
                # Output: Browser endpoint URL: ws://127.0.0.1:9222/devtools/browser/...

                # Use this URL to connect with Playwright or other automation tools
                print("You can now connect to this browser using Playwright")
                # Output: You can now connect to this browser using Playwright

            session.delete()
    except Exception as e:
        print(f"Error: {e}")

get_browser_endpoint()
```

#### get\_option

```python
def get_option() -> Optional["BrowserOption"]
```

Returns the current BrowserOption used to initialize the browser, or None if not set.

**Returns**:

    Optional[BrowserOption]: The browser options if initialized, None otherwise.
  

**Example**:

```python
from agentbay import AgentBay
from agentbay.browser.browser import BrowserOption, BrowserViewport

agent_bay = AgentBay(api_key="your_api_key")

def get_browser_options():
    try:
        result = agent_bay.create()
        if result.success:
            session = result.session

            # Get options before initialization (should be None)
            options = session.browser.get_option()
            if options is None:
                print("No browser options set yet")
                # Output: No browser options set yet

            # Initialize with specific options
            browser_option = BrowserOption(
                use_stealth=True,
                viewport=BrowserViewport(width=1920, height=1080)
            )
            session.browser.initialize(browser_option)

            # Get options after initialization
            current_options = session.browser.get_option()
            if current_options:
                print(f"Browser initialized with stealth mode: {current_options.use_stealth}")
                # Output: Browser initialized with stealth mode: True
                print(f"Viewport size: {current_options.viewport.width}x{current_options.viewport.height}")
                # Output: Viewport size: 1920x1080

            session.delete()
    except Exception as e:
        print(f"Error: {e}")

get_browser_options()
```

#### is\_initialized

```python
def is_initialized() -> bool
```

Returns True if the browser was initialized, False otherwise.

**Returns**:

    bool: True if browser is initialized, False otherwise.
  

**Example**:

```python
from agentbay import AgentBay
from agentbay.browser.browser import BrowserOption

agent_bay = AgentBay(api_key="your_api_key")

def check_browser_initialization():
    try:
        result = agent_bay.create()
        if result.success:
            session = result.session

            # Check if browser is initialized before initialization
            if not session.browser.is_initialized():
                print("Browser not initialized yet")
                # Output: Browser not initialized yet

                # Initialize the browser
                browser_option = BrowserOption(use_stealth=True)
                success = session.browser.initialize(browser_option)

                if success:
                    # Check again after initialization
                    if session.browser.is_initialized():
                        print("Browser is now initialized")
                        # Output: Browser is now initialized

            session.delete()
    except Exception as e:
        print(f"Error: {e}")

check_browser_initialization()
```

#### T

```python
T = TypeVar("T", bound=BaseModel)
```

## ActOptions Objects

```python
class ActOptions()
```

Options for configuring the behavior of the act method.

## ActResult Objects

```python
class ActResult()
```

Result of the act method.

## ObserveOptions Objects

```python
class ObserveOptions()
```

Options for configuring the behavior of the observe method.

## ObserveResult Objects

```python
class ObserveResult()
```

Result of the observe method.

## ExtractOptions Objects

```python
class ExtractOptions(Generic[T])
```

Options for configuring the behavior of the extract method.

## BrowserAgent Objects

```python
class BrowserAgent(BaseService)
```

BrowserAgent handles browser automation and agent logic.

#### navigate\_async

```python
async def navigate_async(url: str) -> str
```

Navigates the browser to the specified URL.

**Arguments**:

- `url` _str_ - The URL to navigate to. Must be a valid HTTP/HTTPS URL.
  

**Returns**:

    str: A success message if navigation succeeds, or an error message if it fails.
  

**Raises**:

    BrowserError: If the browser is not initialized or navigation fails.
  
  Behavior:
  - Calls the MCP tool `page_use_navigate` with the specified URL
  - Waits for the page to load before returning
  - Returns an error message if navigation fails (e.g., invalid URL, network error)
  

**Example**:

  
```python
from agentbay import AgentBay

# Initialize and create a session with browser
agent_bay = AgentBay(api_key="your_api_key")
result = agent_bay.create(enable_browser=True)

if result.success:
    session = result.session
    browser = session.browser

    # Initialize the browser
    browser.init()

    # Navigate to a URL
    import asyncio
    nav_result = asyncio.run(browser.agent.navigate_async("https://www.example.com"))
    print(nav_result)
    # Output: Successfully navigated to https://www.example.com

    # Take a screenshot to verify
    screenshot_data = browser.agent.screenshot()
    print(f"Screenshot captured: {len(screenshot_data)} characters")
    # Output: Screenshot captured: 50000 characters

    # Clean up
    session.delete()
```
  

**Notes**:

  - The browser must be initialized before calling this method
  - This is an async method and must be awaited or run with `asyncio.run()`
  - For synchronous usage, consider using browser automation frameworks directly
  

**See Also**:

  screenshot, act, observe

#### screenshot

```python
def screenshot(page=None,
               full_page: bool = True,
               quality: int = 80,
               clip: Optional[Dict[str, float]] = None,
               timeout: Optional[int] = None) -> str
```

Captures a screenshot of the current browser page.

**Arguments**:

- `page` _Optional[Page]_ - The Playwright Page object to screenshot. If None,
  uses the currently focused page. Defaults to None.
- `full_page` _bool_ - Whether to capture the full scrollable page or just the viewport.
  Defaults to True.
- `quality` _int_ - Image quality for JPEG format (0-100). Higher values mean better quality
  but larger file size. Defaults to 80.
- `clip` _Optional[Dict[str, float]]_ - Clipping region with keys: x, y, width, height (in pixels).
  If specified, only this region is captured. Defaults to None.
- `timeout` _Optional[int]_ - Maximum time to wait for screenshot in milliseconds.
  Defaults to None (uses default timeout).
  

**Returns**:

    str: Base64-encoded data URL of the screenshot (format: `data:image/png;base64,...`),
  or an error message string if the operation fails.
  

**Raises**:

    BrowserError: If the browser is not initialized or screenshot operation fails.
  
  Behavior:
  - Captures the entire scrollable page if `full_page=True`
  - Captures only the visible viewport if `full_page=False`
  - Uses PNG format by default for lossless quality
  - Automatically scrolls the page when capturing full page
  - Returns base64-encoded data URL that can be saved or displayed
  

**Example**:

  
```python
from agentbay import AgentBay
import base64
import asyncio

# Initialize and create a session with browser
agent_bay = AgentBay(api_key="your_api_key")
result = agent_bay.create(enable_browser=True)

if result.success:
    session = result.session
    browser = session.browser

    # Initialize the browser
    browser.init()

    # Navigate to a page
    asyncio.run(browser.agent.navigate_async("https://www.example.com"))

    # Take a full-page screenshot
    screenshot_data = browser.agent.screenshot(full_page=True, quality=90)
    print(f"Full page screenshot: {len(screenshot_data)} characters")
    # Output: Full page screenshot: 75000 characters

    # Save the screenshot to a file
    if screenshot_data.startswith("data:image"):
        # Extract base64 data
        base64_data = screenshot_data.split(",")[1]
        image_bytes = base64.b64decode(base64_data)
        with open("screenshot.png", "wb") as f:
            f.write(image_bytes)
        print("Screenshot saved to screenshot.png")
        # Output: Screenshot saved to screenshot.png

    # Take a viewport-only screenshot with custom quality
    viewport_screenshot = browser.agent.screenshot(full_page=False, quality=60)
    print(f"Viewport screenshot: {len(viewport_screenshot)} characters")
    # Output: Viewport screenshot: 30000 characters

    # Take a screenshot of a specific region
    clipped_screenshot = browser.agent.screenshot(
        clip={"x": 0, "y": 0, "width": 800, "height": 600}
    )
    print(f"Clipped screenshot: {len(clipped_screenshot)} characters")
    # Output: Clipped screenshot: 25000 characters

    # Clean up
    session.delete()
```
  

**Notes**:

  - The browser must be initialized before calling this method
  - Full-page screenshots may take longer for very long pages
  - Higher quality values result in larger data sizes
  - The returned data URL can be directly used in HTML `<img>` tags
  - For large screenshots, consider using `clip` to capture specific regions
  

**See Also**:

  navigate_async, act, observe

#### screenshot\_async

```python
async def screenshot_async(page=None,
                           full_page: bool = True,
                           quality: int = 80,
                           clip: Optional[Dict[str, float]] = None,
                           timeout: Optional[int] = None) -> str
```

Asynchronously takes a screenshot of the specified page.

**Arguments**:

- `page` _Optional[Page]_ - The Playwright Page object to take a screenshot of. If None,
  the agent's currently focused page will be used.
- `full_page` _bool_ - Whether to capture the full scrollable page.
- `quality` _int_ - The quality of the image (0-100), for JPEG format.
- `clip` _Optional[Dict[str, float]]_ - An object specifying the clipping region {x, y, width, height}.
- `timeout` _Optional[int]_ - Custom timeout for the operation in milliseconds.
  

**Returns**:

    str: A base64 encoded data URL of the screenshot, or an error message.

#### close\_async

```python
async def close_async() -> bool
```

Asynchronously closes the remote browser agent session.
This will terminate the browser process managed by the agent.

#### act

```python
def act(action_input: Union[ObserveResult, ActOptions],
        page=None) -> "ActResult"
```

Performs an action on a web page element (click, type, select, etc.).

**Arguments**:

- `action_input` _Union[ObserveResult, ActOptions]_ - The action to perform. Can be:
  - ObserveResult: Result from `observe()` method containing element selector
  - ActOptions: Custom action configuration with selector and action type
- `page` _Optional[Page]_ - The Playwright Page object to act on. If None,
  uses the currently focused page. Defaults to None.
  

**Returns**:

    ActResult: Object containing:
  - success (bool): Whether the action succeeded
  - message (str): Description of the result or error message
  

**Raises**:

    BrowserError: If the browser is not initialized or the action fails.
  
  Behavior:
  - Supports actions: click, type, select, hover, scroll, etc.
  - Automatically waits for elements to be actionable
  - Uses element selectors from observe results or custom selectors
  - Calls the MCP tool `page_use_act` to perform the action
  

**Example**:

  
```python
from agentbay import AgentBay
from agentbay.browser.browser_agent import ObserveOptions, ActOptions
import asyncio

# Initialize and create a session with browser
agent_bay = AgentBay(api_key="your_api_key")
result = agent_bay.create(enable_browser=True)

if result.success:
    session = result.session
    browser = session.browser

    # Initialize the browser
    browser.init()

    # Navigate to a page
    asyncio.run(browser.agent.navigate_async("https://www.example.com"))

    # Method 1: Use observe + act (recommended)
    # First, observe elements on the page
    observe_options = ObserveOptions(
        instruction="Find the search button"
    )
    success, observe_results = browser.agent.observe(observe_options)

    if success and observe_results:
        # Act on the first observed element
        act_result = browser.agent.act(observe_results[0])
        print(f"Action result: {act_result.message}")
        # Output: Action result: Successfully clicked element

    # Method 2: Use custom ActOptions
    # Directly specify the action
    act_options = ActOptions(
        selector="`search`-input",
        description="Search input field",
        method="fill",
        arguments={"text": "AgentBay SDK"}
    )
    act_result = browser.agent.act(act_options)
    print(f"Action result: {act_result.message}")
    # Output: Action result: Successfully filled text

    # Clean up
    session.delete()
```
  

**Notes**:

  - The browser must be initialized before calling this method
  - Using `observe()` + `act()` is recommended for reliable element interaction
  - Custom ActOptions requires knowledge of element selectors
  - Actions are performed with automatic retry and waiting for elements
  

**See Also**:

  observe, navigate_async, screenshot

#### act\_async

```python
async def act_async(action_input: Union[ObserveResult, ActOptions],
                    page=None) -> "ActResult"
```

Asynchronously perform an action on a web page.

**Arguments**:

- `page` _Optional[Page]_ - The Playwright Page object to act on. If None, the agent's
  currently focused page will be used automatically.
- `action_input` _Union[ObserveResult, ActOptions]_ - The action to perform.
  

**Returns**:

    ActResult: The result of the action.

#### observe

```python
def observe(options: ObserveOptions,
            page=None) -> Tuple[bool, List[ObserveResult]]
```

Observes and identifies interactive elements on a web page using natural language instructions.

**Arguments**:

- `options` _ObserveOptions_ - Configuration for observation with fields:
  - instruction (str): Natural language description of elements to find
  - iframes (bool, optional): Whether to search within iframes. Defaults to False.
  - dom_settle_timeout_ms (int, optional): Time to wait for DOM to settle (ms)
  - use_vision (bool, optional): Whether to use vision-based element detection
- `page` _Optional[Page]_ - The Playwright Page object to observe. If None,
  uses the currently focused page. Defaults to None.
  

**Returns**:

  Tuple[bool, List[ObserveResult]]: A tuple containing:
  - success (bool): Whether observation succeeded
  - results (List[ObserveResult]): List of found elements, each with:
  - selector (str): CSS selector for the element
  - description (str): Description of the element
  - method (str): Suggested action method (click, fill, etc.)
  - arguments (dict): Suggested arguments for the action
  

**Raises**:

    BrowserError: If the browser is not initialized or observation fails.
  
  Behavior:
  - Uses AI to interpret natural language instructions
  - Identifies matching elements on the page
  - Returns actionable element information (selectors, methods)
  - Can search within iframes if specified
  - Optionally uses vision-based detection for better accuracy
  

**Example**:

  
```python
from agentbay import AgentBay
from agentbay.browser.browser_agent import ObserveOptions
import asyncio

# Initialize and create a session with browser
agent_bay = AgentBay(api_key="your_api_key")
result = agent_bay.create(enable_browser=True)

if result.success:
    session = result.session
    browser = session.browser

    # Initialize the browser
    browser.init()

    # Navigate to a page
    asyncio.run(browser.agent.navigate_async("https://www.example.com"))

    # Observe elements using natural language
    observe_options = ObserveOptions(
        instruction="Find all clickable buttons on the page"
    )
    success, results = browser.agent.observe(observe_options)

    if success:
        print(f"Found {len(results)} elements")
        # Output: Found 5 elements

        for i, result in enumerate(results):
            print(f"Element {i+1}:")
            print(f"  Selector: {result.selector}")
            print(f"  Description: {result.description}")
            print(f"  Suggested method: {result.method}")
            # Output:
            # Element 1:
            #   Selector: `submit`-button
            #   Description: Submit button
            #   Suggested method: click

    # Observe with vision-based detection
    observe_options_vision = ObserveOptions(
        instruction="Find the login form",
        use_vision=True
    )
    success, results = browser.agent.observe(observe_options_vision)

    if success and results:
        # Use the observed element with act()
        act_result = browser.agent.act(results[0])
        print(f"Action: {act_result.message}")
        # Output: Action: Successfully clicked element

    # Clean up
    session.delete()
```
  

**Notes**:

  - The browser must be initialized before calling this method
  - Natural language instructions should be clear and specific
  - Vision-based detection (`use_vision=True`) provides better accuracy but is slower
  - Results can be directly passed to `act()` method
  - Empty results list indicates no matching elements found
  

**See Also**:

  act, extract, navigate_async

#### observe\_async

```python
async def observe_async(options: ObserveOptions,
                        page=None) -> Tuple[bool, List[ObserveResult]]
```

Asynchronously observe elements or state on a web page.

**Arguments**:

- `page` _Optional[Page]_ - The Playwright Page object to observe. If None, the agent's
  currently focused page will be used.
- `options` _ObserveOptions_ - Options to configure the observation behavior.
  

**Returns**:

  Tuple[bool, List[ObserveResult]]: A tuple containing a success boolean and a list
  of observation results.

#### extract

```python
def extract(options: ExtractOptions, page=None) -> Tuple[bool, T]
```

Extracts structured data from a web page using a Pydantic schema.

**Arguments**:

- `options` _ExtractOptions_ - Configuration for extraction with fields:
  - schema (Type[BaseModel]): Pydantic model defining the data structure to extract
  - instruction (str, optional): Natural language instruction for extraction
  - use_vision (bool, optional): Whether to use vision-based extraction
- `page` _Optional[Page]_ - The Playwright Page object to extract from. If None,
  uses the currently focused page. Defaults to None.
  

**Returns**:

  Tuple[bool, T]: A tuple containing:
  - success (bool): Whether extraction succeeded
  - data (T): Extracted data as an instance of the provided Pydantic model,
  or None if extraction failed
  

**Raises**:

    BrowserError: If the browser is not initialized or extraction fails.
  
  Behavior:
  - Uses AI to extract data matching the provided Pydantic schema
  - Automatically identifies relevant data on the page
  - Returns structured data validated against the schema
  - Can use vision-based extraction for better accuracy
  - Handles complex nested data structures
  

**Example**:

  
```python
from agentbay import AgentBay
from agentbay.browser.browser_agent import ExtractOptions
from pydantic import BaseModel
from typing import List
import asyncio

# Define the data schema
class ProductInfo(BaseModel):
    name: str
    price: float
    description: str
    in_stock: bool

class ProductList(BaseModel):
    products: List[ProductInfo]
    total_count: int

# Initialize and create a session with browser
agent_bay = AgentBay(api_key="your_api_key")
result = agent_bay.create(enable_browser=True)

if result.success:
    session = result.session
    browser = session.browser

    # Initialize the browser
    browser.init()

    # Navigate to a product page
    asyncio.run(browser.agent.navigate_async("https://www.example.com/products"))

    # Extract product information
    extract_options = ExtractOptions(
        schema=ProductList,
        instruction="Extract all product information from the page"
    )
    success, data = browser.agent.extract(extract_options)

    if success and data:
        print(f"Total products: {data.total_count}")
        # Output: Total products: 10

        for product in data.products:
            print(f"Product: {product.name}")
            print(f"  Price: ${product.price}")
            print(f"  In stock: {product.in_stock}")
            # Output:
            # Product: AgentBay SDK
            #   Price: $99.99
            #   In stock: True

    # Extract with vision-based detection
    extract_options_vision = ExtractOptions(
        schema=ProductInfo,
        instruction="Extract the featured product details",
        use_vision=True
    )
    success, product_data = browser.agent.extract(extract_options_vision)

    if success and product_data:
        print(f"Featured product: {product_data.name}")
        print(f"Description: {product_data.description}")
        # Output:
        # Featured product: Premium Plan
        # Description: Full access to all features

    # Clean up
    session.delete()
```
  

**Notes**:

  - The browser must be initialized before calling this method
  - The Pydantic schema must accurately represent the data structure
  - Vision-based extraction (`use_vision=True`) provides better accuracy
  - Complex nested schemas are supported
  - Extraction may fail if the page structure doesn't match the schema
  

**See Also**:

  observe, act, navigate_async

#### extract\_async

```python
async def extract_async(options: ExtractOptions, page=None) -> Tuple[bool, T]
```

Asynchronously extract information from a web page.

**Arguments**:

- `page` _Optional[Page]_ - The Playwright Page object to extract from. If None, the agent's
  currently focused page will be used.
- `options` _ExtractOptions_ - Options to configure the extraction, including schema.
  

**Returns**:

  Tuple[bool, T]: A tuple containing a success boolean and the extracted data as a
  Pydantic model instance, or None on failure.

## Best Practices

1. Wait for page load completion before interacting with elements
2. Use appropriate selectors (CSS, XPath) for reliable element identification
3. Handle navigation timeouts and errors gracefully
4. Take screenshots for debugging and verification
5. Clean up browser resources after automation tasks

## Related Resources

- [Session API Reference](../common-features/basics/session.md)

---

*Documentation generated automatically from source code using pydoc-markdown.*
