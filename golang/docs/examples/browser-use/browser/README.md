# Golang Browser Examples

This directory contains Golang examples demonstrating how to use the AgentBay Browser API.

## Prerequisites

1. **Install Golang SDK**:
   ```bash
   go get github.com/aliyun/wuying-agentbay-sdk/golang
   ```

2. **Install Playwright for Go**:
   ```bash
   go get github.com/playwright-community/playwright-go
   ```

3. **Install Playwright browsers**:
   ```bash
   go run github.com/playwright-community/playwright-go/cmd/playwright@latest install chromium
   ```

4. **Set API Key**:
   ```bash
   export AGENTBAY_API_KEY=your_api_key_here
   ```

## Examples

### 1. visit_aliyun.go

A basic example showing how to:
- Create a session with a browser-enabled image
- Initialize the browser with default options
- Connect to the browser using Playwright over CDP
- Navigate to a website and interact with it
- Take a screenshot

**Run:**
```bash
go run visit_aliyun.go
```

**Expected Output:**
```
Creating session...
Session created: sess-xxxxx
Initializing browser...
Browser CDP endpoint: ws://...
Starting Playwright...
Connecting to browser over CDP...
Navigating to https://www.aliyun.com...
Page title: 阿里云-计算，为了无法计算的价值
Taking screenshot...
Screenshot saved to aliyun_screenshot.png
Browser automation completed successfully!
Deleting session...
```

### 2. custom_browser_config.go

An advanced example demonstrating:
- Custom user agent configuration
- Custom viewport and screen dimensions
- Browser type selection (Chrome vs Chromium)
- Verification of browser configuration

**Run:**
```bash
go run custom_browser_config.go
```

**Expected Output:**
```
Creating session...
Session created: sess-xxxxx
Initializing browser with custom configuration...
Connecting to browser over CDP...
Navigating to user agent detection site...

Verifying browser configuration:
Effective UA: Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36...
Viewport: 1366 x 768
Screen: 1366 x 768

Browser configuration verified successfully!
Deleting session...
```

## Key Browser APIs

### Browser Initialization

```go
// Create browser option with defaults
option := browser.NewBrowserOption()

// Initialize browser
success, err := session.Browser.Initialize(option)
if err != nil || !success {
    log.Fatalf("Browser initialization failed: %v", err)
}
```

### Custom Configuration

```go
option := browser.NewBrowserOption()

// Set custom user agent
customUA := "Mozilla/5.0 ..."
option.UserAgent = &customUA

// Set viewport
option.Viewport = &browser.BrowserViewport{
    Width:  1366,
    Height: 768,
}

// Set screen dimensions
option.Screen = &browser.BrowserScreen{
    Width:  1366,
    Height: 768,
}

// Choose browser type (for computer use images only)
chromeType := "chrome"
option.BrowserType = &chromeType  // "chrome" or "chromium"
```

### Getting CDP Endpoint

```go
endpointURL, err := session.Browser.GetEndpointURL()
if err != nil {
    log.Fatalf("Failed to get endpoint URL: %v", err)
}
```

### Connecting Playwright

```go
pw, err := playwright.Run()
if err != nil {
    log.Fatalf("Failed to start Playwright: %v", err)
}
defer pw.Stop()

browserInstance, err := pw.Chromium.ConnectOverCDP(endpointURL)
if err != nil {
    log.Fatalf("Failed to connect over CDP: %v", err)
}
defer browserInstance.Close()

context := browserInstance.Contexts()[0]
page, err := context.NewPage()
```

## Common Patterns

### Error Handling

Always check both error and success return values:

```go
success, err := session.Browser.Initialize(option)
if err != nil {
    log.Fatalf("Error: %v", err)
}
if !success {
    log.Fatal("Operation failed without error")
}
```

### Resource Cleanup

Use `defer` for proper resource cleanup:

```go
session := result.Session
defer session.Delete()  // Always clean up session

pw, err := playwright.Run()
defer pw.Stop()  // Always stop Playwright

browserInstance, err := pw.Chromium.ConnectOverCDP(endpointURL)
defer browserInstance.Close()  // Always close browser
```

### Pointer Values

Many BrowserOption fields use pointers to allow optional values:

```go
// String pointer
ua := "custom user agent"
option.UserAgent = &ua

// Struct pointer
option.Viewport = &browser.BrowserViewport{
    Width: 1920,
    Height: 1080,
}

// BrowserType uses pointer for optional selection
chromeType := "chrome"
option.BrowserType = &chromeType
```

## Troubleshooting

### "AGENTBAY_API_KEY environment variable not set"

Set your API key:
```bash
export AGENTBAY_API_KEY=your_api_key_here
```

### "Failed to connect over CDP"

Ensure the browser is initialized before connecting:
```go
success, err := session.Browser.Initialize(option)
if err != nil || !success {
    log.Fatal("Browser must be initialized first")
}
```

### "No browser contexts available"

The browser may not have started properly. Check initialization logs and ensure the browser image is available.

## Additional Resources

- [Browser Use Guide](../../../../../docs/guides/browser-use/README.md)
- [Core Features](../../../../../docs/guides/browser-use/core-features.md)
- [Advanced Features](../../../../../docs/guides/browser-use/advance-features.md)
- [Playwright Go Documentation](https://playwright.dev/docs/intro)

