# AsyncBrowser API Reference

> **💡 Sync Version**: This documentation covers the asynchronous API. For synchronous operations, see [`Browser`](../sync/browser.md).
>
> ⚡ **Performance Advantage**: Async API enables concurrent operations with 4-6x performance improvements for parallel tasks.

## 🌐 Related Tutorial

- [Browser Use Guide](../../../../docs/guides/browser-use/README.md) - Complete guide to browser automation

## Overview

The Browser module provides comprehensive browser automation capabilities including navigation, element interaction,screenshot capture, and content extraction. It enables automated testing and web scraping workflows.


## Requirements

- Requires `browser_latest` image for browser automation features



## AsyncBrowser

```python
class AsyncBrowser(AsyncBaseService)
```

Browser provides browser-related operations for the session.

### __init__

```python
def __init__(self, session: "AsyncSession")
```

### agent

```python
@property
def agent()
```

**Deprecated**: Use `operator` instead. This property will be removed in a future version.

**Example**:

```python
# Old way (deprecated):
# await session.browser.operator.navigate(url)

# New way (recommended):
await session.browser.operator.navigate(url)
```

### initialize

```python
async def initialize(option: Optional["BrowserOption"] = None) -> bool
```

Initialize the browser instance with the given options asynchronously.
Returns True if successful, False otherwise.

**Arguments**:

- `option` _BrowserOption, optional_ - Browser configuration options. If None, default options are used.
  

**Returns**:

    bool: True if initialization was successful, False otherwise.
  

**Example**:

```python
create_result = await agent_bay.create()
session = create_result.session
# Use default options
await session.browser.initialize()
# Or with specific options
browser_option = BrowserOption(use_stealth=True)
await session.browser.initialize(browser_option)
await session.delete()
```

### init

```python
async def init(option: Optional["BrowserOption"] = None) -> bool
```

Alias for initialize.

### destroy

```python
async def destroy()
```

Destroy the browser instance manually.

### screenshot

```python
async def screenshot(page, full_page: bool = False, **options) -> bytes
```

Takes a screenshot of the specified page with enhanced options and error handling.

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

### register_callback

```python
async def register_callback(callback: BrowserCallback) -> bool
```

Register a callback function to handle browser-related push notifications from sandbox.

**Arguments**:

- `callback` _Callable[[BrowserNotifyMessage], None]_ - Callback function that receives
  a BrowserNotifyMessage object containing notification details such as type, code,
  message, action, and extra_params.
  

**Returns**:

    bool: True if the callback was successfully registered.
  

**Example**:

```python
def on_browser_callback(notify_msg: BrowserNotifyMessage):
  print(f"Type: {notify_msg.type}")
  print(f"Code: {notify_msg.code}")
  print(f"Message: {notify_msg.message}")
  print(f"Action: {notify_msg.action}")
  print(f"Extra params: {notify_msg.extra_params}")

create_result = await agent_bay.create()
session = create_result.session

# Initialize browser
await session.browser.initialize()

# Register callback
success = await session.browser.register_callback(on_browser_callback)

# ... do work ...

# Unregister when done
await session.browser.unregister_callback()
await session.delete()
```

### unregister_callback

```python
async def unregister_callback() -> None
```

Unregister the previously registered callback function.

**Example**:

```python
def on_browser_callback(notify_msg: BrowserNotifyMessage):
  print(f"Notification - Type: {notify_msg.type}, Message: {notify_msg.message}")

create_result = await agent_bay.create()
session = create_result.session

await session.browser.initialize()

await session.browser.register_callback(on_browser_callback)

# ... do work ...

# Unregister callback
await session.browser.unregister_callback()

await session.delete()
```

### send_notify_message

```python
async def send_notify_message(notify_message: BrowserNotifyMessage) -> bool
```

Send a BrowserNotifyMessage to sandbox.

**Arguments**:

- `notify_message` _BrowserNotifyMessage_ - The notify message to send.
  

**Returns**:

    bool: True if the notify message was successfully sent, False otherwise.
  

**Example**:

```python
def on_browser_callback(notify_msg: BrowserNotifyMessage):
  print(f"Type: {notify_msg.type}")
  print(f"Code: {notify_msg.code}")
  print(f"Message: {notify_msg.message}")
  print(f"Action: {notify_msg.action}")
  print(f"Extra params: {notify_msg.extra_params}")

create_result = await agent_bay.create()
session = create_result.session

# Initialize browser
await session.browser.initialize()

# Register callback
success = await session.browser.register_callback(on_browser_callback)

# ... do work ...

# Send notify message
notify_message = BrowserNotifyMessage(
  type="call-for-user",
  id=3,
  code=199,
  message="user handle done",
  action="takeoverdone",
  extra_params={}
)
await session.browser.send_notify_message(notify_message)

# Unregister when done
await session.browser.unregister_callback()
await session.delete()
```

### send_takeover_done

```python
async def send_takeover_done(notify_id: int) -> bool
```

Send a takeoverdone notify message to sandbox.

**Arguments**:

- `notify_id` _int_ - The notification ID associated with the takeover request message.
  

**Returns**:

    bool: True if the takeoverdone notify message was successfully sent, False otherwise.
  

**Example**:

```python
def on_browser_callback(notify_msg: BrowserNotifyMessage):
  # receive call-for-user "takeover" action
  if notify_msg.action == "takeover":
      takeover_notify_id = notify_msg.id

      ## ... do work in other thread...
      # send takeoverdone notify message
      await session.browser.send_takeover_done(takeover_notify_id)
      ## ... end...

create_result = await agent_bay.create()
session = create_result.session

# Initialize browser
await session.browser.initialize()

# Register callback
success = await session.browser.register_callback(on_browser_callback)

# ... do work ...

# Unregister when done
await session.browser.unregister_callback()
await session.delete()
```

### get_endpoint_url

```python
async def get_endpoint_url() -> str
```

Returns the endpoint URL if the browser is initialized, otherwise raises an exception.
When initialized, always fetches the latest CDP url from session.get_link().

**Returns**:

    str: The browser CDP endpoint URL.
  

**Raises**:

    BrowserError: If browser is not initialized or endpoint URL cannot be retrieved.
  

**Example**:

```python
create_result = await agent_bay.create()
session = create_result.session
browser_option = BrowserOption()
await session.browser.initialize(browser_option)
endpoint_url = await session.browser.get_endpoint_url()
print(f"CDP Endpoint: {endpoint_url}")
await session.delete()
```

### get_option

```python
def get_option() -> Optional["BrowserOption"]
```

Returns the current BrowserOption used to initialize the browser, or None if not set.

**Returns**:

    Optional[BrowserOption]: The browser options if initialized, None otherwise.
  

**Example**:

```python
create_result = await agent_bay.create()
session = create_result.session
browser_option = BrowserOption(use_stealth=True)
await session.browser.initialize(browser_option)
current_options = session.browser.get_option()
print(f"Stealth mode: {current_options.use_stealth}")
await session.delete()
```

### is_initialized

```python
def is_initialized() -> bool
```

Returns True if the browser was initialized, False otherwise.

**Returns**:

    bool: True if browser is initialized, False otherwise.
  

**Example**:

```python
create_result = await agent_bay.create()
session = create_result.session
print(f"Initialized: {session.browser.is_initialized()}")
browser_option = BrowserOption()
await session.browser.initialize(browser_option)
print(f"Initialized: {session.browser.is_initialized()}")
await session.delete()
```

## Best Practices

1. Wait for page load completion before interacting with elements
2. Use appropriate selectors (CSS, XPath) for reliable element identification
3. Handle navigation timeouts and errors gracefully
4. Take screenshots for debugging and verification
5. Clean up browser resources after automation tasks

## See Also

- [Synchronous vs Asynchronous API](../../../docs/guides/async-programming/sync-vs-async.md)

**Related APIs:**
- [Session API Reference](./async-session.md)

---

*Documentation generated automatically from source code using pydoc-markdown.*
