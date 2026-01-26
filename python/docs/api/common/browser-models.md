# Browser Models API Reference

> **💡 Async Version**: This documentation covers the synchronous API. For async/await support, see [`AsyncBrowser`](../async/async-browser.md) which provides the same functionality with async methods.

## 🌐 Related Tutorial

- [Browser Use Guide](../../../../docs/guides/browser-use/README.md) - Complete guide to browser automation

## Overview

The Browser module provides comprehensive browser automation capabilities including navigation, element interaction,
screenshot capture, and content extraction. It enables automated testing and web scraping workflows.


## Requirements

- Requires `browser_latest` image for browser automation features



Browser module data models.

## BrowserFingerprintContext

```python
class BrowserFingerprintContext()
```

Browser fingerprint context configuration.

### __init__

```python
def __init__(self, fingerprint_context_id: str)
```

Initialize FingerprintContext with context id.

**Arguments**:

- `fingerprint_context_id` _str_ - ID of the fingerprint context for browser fingerprint.
  

**Raises**:

    ValueError: If fingerprint_context_id is empty.

## BrowserProxy

```python
class BrowserProxy()
```

Browser proxy configuration.
Supports three types of proxy: custom proxy, wuying proxy, and managed proxy.

- **custom proxy**: User-provided proxy server
- **wuying proxy**: Wuying built-in proxy service
  * restricted: Fixed IP per session
  * polling: Allocates multiple proxies per session (size controlled by pollsize)
- **managed proxy**: Client-provided proxies managed by Wuying platform (requires setup - contact us)
  * polling: Allocates one proxy per session from pool (round-robin)
  * sticky: Keep same IP for specific user
  * rotating: Force different IP for specific user
  * matched: Filter proxies by ISP/country/province/city attributes

> **Note**: To use managed proxy, please contact us or your account manager to set up your proxy pool first.

### __init__

```python
def __init__(self, proxy_type: Literal["custom", "wuying", "managed"],
             server: Optional[str] = None,
             username: Optional[str] = None,
             password: Optional[str] = None,
             strategy: Optional[Literal["restricted", "polling", "sticky", "rotating", "matched"]] = None,
             pollsize: int = 10,
             user_id: Optional[str] = None,
             isp: Optional[str] = None,
             country: Optional[str] = None,
             province: Optional[str] = None,
             city: Optional[str] = None)
```

Initialize a BrowserProxy.

**Arguments**:

    proxy_type: Type of proxy - "custom", "wuying", or "managed"
    server: Proxy server address (required for custom type)
    username: Proxy username (optional for custom type)
    password: Proxy password (optional for custom type)
    strategy: Proxy allocation strategy:
        - For wuying: "restricted" (fixed IP) or "polling" (allocates multiple proxies per session)
        - For managed: "polling" (allocates one proxy per session from pool), 
                       "sticky" (keep same IP for user), 
                       "rotating" (force different IP for user), 
                       "matched" (filter by ISP/country/province/city attributes)
    pollsize: Pool size for wuying polling strategy (default: 10). Not used for managed type.
    user_id: Custom user identifier for tracking proxy allocation records (required for managed type).
             - sticky/rotating strategies: Associates with historical allocations to maintain or rotate IPs per user
             - polling/matched strategies: Each session gets an independent allocation
    isp: ISP filter for managed matched strategy (e.g., "China Telecom", "China Unicom")
    country: Country filter for managed matched strategy (e.g., "China", "United States")
    province: Province filter for managed matched strategy (e.g., "Beijing", "Guangdong")
    city: City filter for managed matched strategy (e.g., "Beijing", "Shenzhen")
  
**Examples**:

```python
# Custom proxy
proxy_type: custom
server: "127.0.0.1:9090"
username: "username"
password: "password"

# Wuying proxy with polling strategy
proxy_type: wuying
strategy: "polling"
pollsize: 10

# Wuying proxy with restricted strategy
proxy_type: wuying
strategy: "restricted"

# Managed proxy with polling strategy
proxy_type: managed
strategy: "polling"
user_id: "user123"

# Managed proxy with sticky strategy
proxy_type: managed
strategy: "sticky"
user_id: "user123"

# Managed proxy with rotating strategy
proxy_type: managed
strategy: "rotating"
user_id: "user123"

# Managed proxy with matched strategy
proxy_type: managed
strategy: "matched"
user_id: "user123"
isp: "China Telecom"
country: "China"
province: "Beijing"
city: "Beijing"
```

## BrowserViewport

```python
class BrowserViewport()
```

Browser viewport options.

### __init__

```python
def __init__(self, width: int = 1920, height: int = 1080)
```

## BrowserScreen

```python
class BrowserScreen()
```

Browser screen options.

### __init__

```python
def __init__(self, width: int = 1920, height: int = 1080)
```

## BrowserFingerprint

```python
class BrowserFingerprint()
```

Browser fingerprint options.

### __init__

```python
def __init__(self, devices: list[Literal["desktop", "mobile"]] = None,
             operating_systems: list[Literal["windows", "macos", "linux",
                                             "android", "ios"]] = None,
             locales: list[str] = None)
```

## BrowserOption

```python
class BrowserOption()
```

browser initialization options.

### __init__

```python
def __init__(self, use_stealth: bool = False,
             user_agent: str = None,
             viewport: BrowserViewport = None,
             screen: BrowserScreen = None,
             fingerprint: BrowserFingerprint = None,
             fingerprint_format: Optional["FingerprintFormat"] = None,
             fingerprint_persistent: bool = False,
             solve_captchas: bool = False,
             proxies: Optional[list[BrowserProxy]] = None,
             extension_path: Optional[str] = "/tmp/extensions/",
             cmd_args: Optional[list[str]] = None,
             default_navigate_url: Optional[str] = None,
             browser_type: Optional[Literal["chrome", "chromium"]] = None)
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
- [Session API Reference](../sync/session.md)

---

*Documentation generated automatically from source code using pydoc-markdown.*
