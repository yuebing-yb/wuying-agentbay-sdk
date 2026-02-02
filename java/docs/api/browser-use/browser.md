# 🌐 Browser API Reference

## Overview

The Browser module provides comprehensive browser automation capabilities including navigation, element interaction,
screenshot capture, and content extraction. It enables automated testing and web scraping workflows.


## 📚 Tutorial

[Browser Use Guide](../../../../docs/guides/browser-use/README.md)

Complete guide to browser automation

## 📋 Requirements

- Requires `browser_latest` image for browser automation features

## Browser

Browser provides browser-related operations for the session.

### Constructor

```java
public Browser(Session session)
```

### Methods

### initialize

```java
public boolean initialize(BrowserOption option)
```

Initialize the browser instance with the given options.

**Parameters:**
- `option` (BrowserOption): Browser initialization options

**Returns:**
- `boolean`: true if successful, false otherwise

### init

```java
public boolean init(BrowserOption option)
```

Alias for initialize method.

**Parameters:**
- `option` (BrowserOption): Browser initialization options

**Returns:**
- `boolean`: true if successful, false otherwise

### destroy

```java
public void destroy()
```

Destroy the browser instance.

### screenshot

```java
public byte[] screenshot(com.microsoft.playwright.Page page, boolean fullPage, Map<String, Object> options) throws BrowserException
```

Takes a screenshot of the specified page with enhanced options and error handling.

**Parameters:**
- `page` (com.microsoft.playwright.Page): The Playwright Page object to take a screenshot of
- `fullPage` (boolean): Whether to capture the full scrollable page
- `options` (Map<String,Object>): Additional screenshot options

**Returns:**
- `byte[]`: Screenshot data as bytes

**Throws:**
- `BrowserException`: if browser is not initialized

### stopBrowser

```java
public void stopBrowser() throws BrowserException
```

Stop the browser instance (internal use only).

### getEndpointUrl

```java
public String getEndpointUrl() throws BrowserException
```

Get the endpoint URL for browser connection.
When initialized, always fetches the latest CDP url from getCdpLink API.

**Returns:**
- `String`: Browser endpoint URL

**Throws:**
- `BrowserException`: if browser is not initialized or endpoint URL cannot be retrieved

### getOption

```java
public BrowserOption getOption()
```

Get the current BrowserOption used to initialize the browser.

**Returns:**
- `BrowserOption`: BrowserOption or null if not set

### isInitialized

```java
public boolean isInitialized()
```

Check if the browser is initialized.

**Returns:**
- `boolean`: true if initialized, false otherwise

### getOperator

```java
public BrowserOperator getOperator()
```

Get the browser operator for browser operations (recommended).

<p>Example usage:</p>
<pre>{@code
BrowserOperator operator = browser.getOperator();
operator.navigate("https://example.com");
operator.screenshot(null, true, null);
}</pre>

**Returns:**
- `BrowserOperator`: BrowserOperator instance

### getAgent

```java
public BrowserAgent getAgent()
```

Get the browser agent for advanced browser operations.

**Returns:**
- `BrowserAgent`: BrowserAgent instance

### getEndpointRouterPort

```java
public Integer getEndpointRouterPort()
```

Get the endpoint router port.

**Returns:**
- `Integer`: Port number or null if not set



## 💡 Best Practices

- Wait for page load completion before interacting with elements
- Use appropriate selectors (CSS, XPath) for reliable element identification
- Handle navigation timeouts and errors gracefully
- Take screenshots for debugging and verification
- Clean up browser resources after automation tasks

## 🔗 Related Resources

- [Session API Reference](../../api/common-features/basics/session.md)

