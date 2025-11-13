# Browser API Reference

## 🌐 Related Tutorial

- [Browser Use Guide](../../../../docs/guides/browser-use/README.md) - Complete guide to browser automation

## Overview

The Browser module provides comprehensive browser automation capabilities including navigation, element interaction,
screenshot capture, and content extraction. It enables automated testing and web scraping workflows.


## Requirements

- Requires `browser_latest` image for browser automation features



## BrowserFingerprintContext

```python
class BrowserFingerprintContext()
```

Browser fingerprint context configuration.

## BrowserProxy

```python
class BrowserProxy()
```

Browser proxy configuration.
Supports two types of proxy: custom proxy, wuying proxy.
wuying proxy support two strategies: restricted and polling.

## BrowserViewport

```python
class BrowserViewport()
```

Browser viewport options.

## BrowserScreen

```python
class BrowserScreen()
```

Browser screen options.

## BrowserFingerprint

```python
class BrowserFingerprint()
```

Browser fingerprint options.

## BrowserOption

```python
class BrowserOption()
```

browser initialization options.

## Browser

```python
class Browser(BaseService)
```

Browser provides browser-related operations for the session.

### initialize

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
session = agent_bay.create().session
browser_option = BrowserOption(use_stealth=True)
success = session.browser.initialize(browser_option)
print(f"Browser initialized: {success}")
session.delete()
```

### initialize\_async

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
session = agent_bay.create().session
browser_option = BrowserOption(use_stealth=True)
success = await session.browser.initialize_async(browser_option)
print(f"Browser initialized: {success}")
session.delete()
```

### destroy

```python
def destroy()
```

Destroy the browser instance.

**Example**:

```python
session = agent_bay.create().session
browser_option = BrowserOption()
session.browser.initialize(browser_option)
session.browser.destroy()
session.delete()
```

### screenshot

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

### get\_endpoint\_url

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
session = agent_bay.create().session
browser_option = BrowserOption()
session.browser.initialize(browser_option)
endpoint_url = session.browser.get_endpoint_url()
print(f"CDP Endpoint: {endpoint_url}")
session.delete()
```

### get\_option

```python
def get_option() -> Optional["BrowserOption"]
```

Returns the current BrowserOption used to initialize the browser, or None if not set.

**Returns**:

    Optional[BrowserOption]: The browser options if initialized, None otherwise.
  

**Example**:

```python
session = agent_bay.create().session
browser_option = BrowserOption(use_stealth=True)
session.browser.initialize(browser_option)
current_options = session.browser.get_option()
print(f"Stealth mode: {current_options.use_stealth}")
session.delete()
```

### is\_initialized

```python
def is_initialized() -> bool
```

Returns True if the browser was initialized, False otherwise.

**Returns**:

    bool: True if browser is initialized, False otherwise.
  

**Example**:

```python
session = agent_bay.create().session
print(f"Initialized: {session.browser.is_initialized()}")
browser_option = BrowserOption()
session.browser.initialize(browser_option)
print(f"Initialized: {session.browser.is_initialized()}")
session.delete()
```

#### T

```python
T = TypeVar("T", bound=BaseModel)
```

## ActOptions

```python
class ActOptions()
```

Options for configuring the behavior of the act method.

## ActResult

```python
class ActResult()
```

Result of the act method.

## ObserveOptions

```python
class ObserveOptions()
```

Options for configuring the behavior of the observe method.

## ObserveResult

```python
class ObserveResult()
```

Result of the observe method.

## ExtractOptions

```python
class ExtractOptions(Generic[T])
```

Options for configuring the behavior of the extract method.

## BrowserAgent

```python
class BrowserAgent(BaseService)
```

BrowserAgent handles browser automation and agent logic.

### navigate\_async

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
session = agent_bay.create(image="browser_latest").session
await session.browser.agent.navigate_async("https://example.com")
session.delete()
```


**Notes**:

- The browser must be initialized before calling this method
- This is an async method and must be awaited or run with `asyncio.run()`
- For synchronous usage, consider using browser automation frameworks directly


**See Also**:

screenshot, act, observe

### screenshot

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
session = agent_bay.create(image="browser_latest").session
screenshot_data = session.browser.agent.screenshot()
print(f"Screenshot captured: {len(screenshot_data)} bytes")
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

### screenshot\_async

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

### close\_async

```python
async def close_async() -> bool
```

Asynchronously closes the remote browser agent session.
This will terminate the browser process managed by the agent.

### act

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
from agentbay.browser.browser_agent import ActOptions
session = agent_bay.create(image="browser_latest").session
action = ActOptions(action="Click the login button")
result = session.browser.agent.act(action)
session.delete()
```


**Notes**:

- The browser must be initialized before calling this method
- Using `observe()` + `act()` is recommended for reliable element interaction
- Custom ActOptions requires knowledge of element selectors
- Actions are performed with automatic retry and waiting for elements


**See Also**:

observe, navigate_async, screenshot

### act\_async

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

### observe

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
from agentbay.browser.browser_agent import ObserveOptions
session = agent_bay.create(image="browser_latest").session
options = ObserveOptions(instruction="Find the search input field")
success, results = session.browser.agent.observe(options)
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

### observe\_async

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

### extract

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
from pydantic import BaseModel
from agentbay.browser.browser_agent import ExtractOptions
class ProductInfo(BaseModel):
  name: str
  price: float
session = agent_bay.create(image="browser_latest").session
options = ExtractOptions(instruction="Extract product details", schema=ProductInfo)
success, data = session.browser.agent.extract(options)
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

### extract\_async

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
