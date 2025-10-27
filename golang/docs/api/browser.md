# Browser API Reference

The Browser API provides methods for initializing and managing browser instances in the AgentBay cloud environment. It supports both headless and non-headless browsers with extensive configuration options including stealth mode, custom viewports, fingerprinting, proxies, and more.

## Overview

The Browser API is accessed through a session instance and provides methods for browser lifecycle management and connection to automation frameworks via Chrome DevTools Protocol (CDP).

```go
import "github.com/aliyun/wuying-agentbay-sdk/golang/pkg/agentbay/browser"

// Access browser through session
session := result.Session
browserAPI := session.Browser
```

## Data Types

### BrowserOption

Configuration options for initializing a browser instance.

```go
type BrowserOption struct {
    UseStealth    bool                `json:"useStealth,omitempty"`    // Enable stealth mode
    UserAgent     *string             `json:"userAgent,omitempty"`     // Custom user agent
    Viewport      *BrowserViewport    `json:"viewport,omitempty"`      // Viewport configuration
    Screen        *BrowserScreen      `json:"screen,omitempty"`        // Screen configuration
    Fingerprint   *BrowserFingerprint `json:"fingerprint,omitempty"`   // Fingerprint configuration
    SolveCaptchas bool                `json:"solveCaptchas,omitempty"` // Auto-solve captchas
    Proxies       []*BrowserProxy     `json:"proxies,omitempty"`       // Proxy configurations
    ExtensionPath *string             `json:"extensionPath,omitempty"` // Path to extensions directory
    BrowserType   *string             `json:"browserType,omitempty"`   // Browser type: "chrome" or "chromium"
}
```

**Field Descriptions:**

- `UseStealth`: Enables stealth mode to avoid detection by anti-bot systems
- `UserAgent`: Custom user agent string for the browser
- `Viewport`: Browser viewport dimensions (affects the visible area)
- `Screen`: Screen dimensions (affects screen properties)
- `Fingerprint`: Browser fingerprint configuration for randomization
- `SolveCaptchas`: Automatically solve captchas during browsing
- `Proxies`: List of proxy configurations (maximum 1 proxy)
- `ExtensionPath`: Path to directory containing browser extensions
- `BrowserType`: Browser type selection - `"chrome"` or `"chromium"` (computer use images only), or `nil` for default

### BrowserViewport

Defines the browser viewport dimensions.

```go
type BrowserViewport struct {
    Width  int `json:"width"`  // Viewport width in pixels
    Height int `json:"height"` // Viewport height in pixels
}
```

**Common Viewport Sizes:**
- Desktop: `1920x1080`, `1366x768`, `1280x720`
- Laptop: `1440x900`, `1366x768`
- Tablet: `1024x768`, `768x1024`
- Mobile: `375x667`, `414x896`

### BrowserScreen

Defines the screen dimensions (usually same or larger than viewport).

```go
type BrowserScreen struct {
    Width  int `json:"width"`  // Screen width in pixels
    Height int `json:"height"` // Screen height in pixels
}
```

### BrowserFingerprint

Configuration for browser fingerprint randomization.

```go
type BrowserFingerprint struct {
    Devices          []string `json:"devices,omitempty"`          // Device types
    OperatingSystems []string `json:"operatingSystems,omitempty"` // Operating systems
    Locales          []string `json:"locales,omitempty"`          // Locale strings
}
```

**Valid Values:**

- **Devices**: `"desktop"`, `"mobile"`
- **Operating Systems**: `"windows"`, `"macos"`, `"linux"`, `"android"`, `"ios"`
- **Locales**: Standard locale strings (e.g., `"en-US"`, `"zh-CN"`, `"ja-JP"`)

**Example:**
```go
fingerprint := &browser.BrowserFingerprint{
    Devices:          []string{"desktop"},
    OperatingSystems: []string{"windows", "macos"},
    Locales:          []string{"en-US", "en-GB"},
}
```

### BrowserProxy

Configuration for browser proxy settings.

```go
type BrowserProxy struct {
    Type         string  `json:"type"`                   // Proxy type: "custom" or "wuying"
    Server       *string `json:"server,omitempty"`       // Proxy server (for custom type)
    Username     *string `json:"username,omitempty"`     // Proxy username (optional)
    Password     *string `json:"password,omitempty"`     // Proxy password (optional)
    Strategy     *string `json:"strategy,omitempty"`     // Proxy strategy (for wuying type)
    PollSize     *int    `json:"pollSize,omitempty"`     // Poll size (for polling strategy)
}
```

**Proxy Types:**

1. **Custom Proxy** (`type: "custom"`):
   ```go
   server := "proxy.example.com:8080"
   username := "user"
   password := "pass"
   
   proxy := &browser.BrowserProxy{
       Type:     "custom",
       Server:   &server,
       Username: &username,
       Password: &password,
   }
   ```

2. **WuYing Proxy** (`type: "wuying"`):
   - **Restricted Strategy**: Uses a single dedicated IP
     ```go
     strategy := "restricted"
     proxy := &browser.BrowserProxy{
         Type:     "wuying",
         Strategy: &strategy,
     }
     ```
   
   - **Polling Strategy**: Rotates through a pool of IPs
     ```go
     strategy := "polling"
     pollSize := 10
     proxy := &browser.BrowserProxy{
         Type:     "wuying",
         Strategy: &strategy,
         PollSize: &pollSize,
     }
     ```

**Validation Rules:**
- Maximum 1 proxy allowed in the `Proxies` list
- `Server` is required for `custom` type
- `Strategy` is required for `wuying` type
- `PollSize` must be > 0 for `polling` strategy

## Methods

### NewBrowserOption

Creates a new BrowserOption with default values.

```go
func NewBrowserOption() *BrowserOption
```

**Returns:**
- `*BrowserOption`: A new BrowserOption instance with default values

**Default Values:**
- `UseStealth`: `false`
- `SolveCaptchas`: `false`
- `ExtensionPath`: `"/tmp/extensions/"`
- `BrowserType`: `nil` (lets browser image decide)

**Example:**
```go
option := browser.NewBrowserOption()
// Customize as needed
customUA := "Mozilla/5.0 ..."
option.UserAgent = &customUA
```

### Validate

Validates the BrowserOption configuration.

```go
func (o *BrowserOption) Validate() error
```

**Returns:**
- `error`: An error if validation fails, `nil` otherwise

**Validation Rules:**
- Maximum 1 proxy in `Proxies` list
- `ExtensionPath` cannot be empty if provided
- `BrowserType` must be `"chrome"`, `"chromium"`, or `nil`

**Example:**
```go
option := browser.NewBrowserOption()
if err := option.Validate(); err != nil {
    log.Fatalf("Invalid browser option: %v", err)
}
```

### ToMap

Converts BrowserOption to a map for API requests.

```go
func (o *BrowserOption) ToMap() map[string]interface{}
```

**Returns:**
- `map[string]interface{}`: A map representation of the browser options

**Example:**
```go
option := browser.NewBrowserOption()
optionMap := option.ToMap()
// optionMap can be used in API requests
```

### Initialize

Initializes the browser with the given options (synchronous).

```go
func (b *Browser) Initialize(option *BrowserOption) (bool, error)
```

**Parameters:**
- `option` (*BrowserOption): Browser configuration options

**Returns:**
- `bool`: `true` if initialization was successful
- `error`: An error if the operation fails

**Example:**
```go
option := browser.NewBrowserOption()

// Add custom configuration
customUA := "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7)"
option.UserAgent = &customUA

option.Viewport = &browser.BrowserViewport{
    Width:  1920,
    Height: 1080,
}

// Initialize browser
success, err := session.Browser.Initialize(option)
if err != nil {
    log.Fatalf("Failed to initialize browser: %v", err)
}
if !success {
    log.Fatal("Browser initialization returned false")
}
```

### GetEndpointURL

Retrieves the CDP (Chrome DevTools Protocol) endpoint URL for connecting automation tools.

```go
func (b *Browser) GetEndpointURL() (string, error)
```

**Returns:**
- `string`: The CDP WebSocket endpoint URL (e.g., `ws://host:port/devtools/browser/...`)
- `error`: An error if the operation fails

**Example:**
```go
endpointURL, err := session.Browser.GetEndpointURL()
if err != nil {
    log.Fatalf("Failed to get endpoint URL: %v", err)
}

// Use with Playwright
browser, err := pw.Chromium.ConnectOverCDP(endpointURL)
```

### IsInitialized

Checks if the browser has been initialized.

```go
func (b *Browser) IsInitialized() bool
```

**Returns:**
- `bool`: `true` if the browser is initialized, `false` otherwise

**Example:**
```go
if session.Browser.IsInitialized() {
    fmt.Println("Browser is ready")
} else {
    fmt.Println("Browser needs initialization")
}
```

### GetOption

Retrieves the current browser configuration.

```go
func (b *Browser) GetOption() *BrowserOption
```

**Returns:**
- `*BrowserOption`: The current browser configuration, or `nil` if not initialized

**Example:**
```go
option := session.Browser.GetOption()
if option != nil {
    fmt.Printf("Browser type: %v\n", option.BrowserType)
}
```

## Complete Usage Example

### Basic Usage

```go
package main

import (
    "fmt"
    "log"
    "os"

    "github.com/aliyun/wuying-agentbay-sdk/golang/pkg/agentbay"
    "github.com/aliyun/wuying-agentbay-sdk/golang/pkg/agentbay/browser"
    "github.com/playwright-community/playwright-go"
)

func main() {
    // Initialize AgentBay
    agentBay := agentbay.NewAgentBay(os.Getenv("AGENTBAY_API_KEY"))

    // Create session
    params := &agentbay.CreateSessionParams{
        ImageId: "browser_latest",
    }
    result, err := agentBay.Create(params)
    if err != nil || !result.Success {
        log.Fatalf("Failed to create session: %v", err)
    }
    defer result.Session.Delete()

    // Initialize browser with default options
    option := browser.NewBrowserOption()
    success, err := result.Session.Browser.Initialize(option)
    if err != nil || !success {
        log.Fatalf("Browser initialization failed: %v", err)
    }

    // Get CDP endpoint
    endpoint, err := result.Session.Browser.GetEndpointURL()
    if err != nil {
        log.Fatalf("Failed to get endpoint: %v", err)
    }

    // Connect with Playwright
    pw, err := playwright.Run()
    if err != nil {
        log.Fatalf("Failed to start Playwright: %v", err)
    }
    defer pw.Stop()

    browserInstance, err := pw.Chromium.ConnectOverCDP(endpoint)
    if err != nil {
        log.Fatalf("Failed to connect: %v", err)
    }
    defer browserInstance.Close()

    // Use the browser
    page, err := browserInstance.Contexts()[0].NewPage()
    if err != nil {
        log.Fatalf("Failed to create page: %v", err)
    }

    _, err = page.Goto("https://example.com")
    if err != nil {
        log.Fatalf("Failed to navigate: %v", err)
    }

    title, _ := page.Title()
    fmt.Printf("Page title: %s\n", title)
}
```

### Advanced Configuration

```go
// Create custom browser configuration
option := browser.NewBrowserOption()

// Custom user agent
ua := "Mozilla/5.0 (Windows NT 10.0; Win64; x64) Chrome/120.0.0.0"
option.UserAgent = &ua

// Viewport and screen
option.Viewport = &browser.BrowserViewport{Width: 1920, Height: 1080}
option.Screen = &browser.BrowserScreen{Width: 1920, Height: 1080}

// Browser type (for computer use images)
chromeType := "chrome"
option.BrowserType = &chromeType

// Stealth mode
option.UseStealth = true

// Fingerprint randomization
option.Fingerprint = &browser.BrowserFingerprint{
    Devices:          []string{"desktop"},
    OperatingSystems: []string{"windows", "macos"},
    Locales:          []string{"en-US"},
}

// Proxy configuration
proxyServer := "proxy.example.com:8080"
proxyUser := "username"
proxyPass := "password"
option.Proxies = []*browser.BrowserProxy{
    {
        Type:     "custom",
        Server:   &proxyServer,
        Username: &proxyUser,
        Password: &proxyPass,
    },
}

// Validate before use
if err := option.Validate(); err != nil {
    log.Fatalf("Invalid configuration: %v", err)
}

// Initialize with custom options
success, err := session.Browser.Initialize(option)
if err != nil || !success {
    log.Fatalf("Failed to initialize: %v", err)
}
```

## Error Handling

### Common Errors

1. **Browser Not Initialized**
   ```go
   endpoint, err := session.Browser.GetEndpointURL()
   if err != nil {
       // Error: "browser not initialized"
       log.Fatal("Initialize browser before getting endpoint")
   }
   ```

2. **Invalid Configuration**
   ```go
   option := browser.NewBrowserOption()
   invalidType := "firefox"
   option.BrowserType = &invalidType
   
   _, err := session.Browser.Initialize(option)
   // Error: "browserType must be 'chrome' or 'chromium'"
   ```

3. **Multiple Proxies**
   ```go
   option.Proxies = []*browser.BrowserProxy{proxy1, proxy2}
   err := option.Validate()
   // Error: "proxies list length must be limited to 1"
   ```

### Best Practices

```go
// Always check both success and error
success, err := session.Browser.Initialize(option)
if err != nil {
    log.Fatalf("Error: %v", err)
}
if !success {
    log.Fatal("Initialization failed without error")
}

// Validate options before initialization
if err := option.Validate(); err != nil {
    log.Fatalf("Invalid options: %v", err)
}

// Check initialization status
if !session.Browser.IsInitialized() {
    log.Fatal("Browser must be initialized first")
}

// Use defer for cleanup
defer session.Delete()
defer pw.Stop()
defer browserInstance.Close()
```

## Browser Type Selection

> **Note:** The `BrowserType` option is only available for **computer use images**. For standard browser images, the browser type is determined by the image.

### Choosing Browser Type

```go
// Use Chrome (Google Chrome)
chromeType := "chrome"
option := browser.NewBrowserOption()
option.BrowserType = &chromeType

// Use Chromium (open-source)
chromiumType := "chromium"
option := browser.NewBrowserOption()
option.BrowserType = &chromiumType

// Use default (nil - let browser image decide)
option := browser.NewBrowserOption()
// option.BrowserType is nil by default
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

**Default** (`nil`):
- Let the platform choose optimal browser
- Maximum compatibility
- Recommended for most use cases

## Integration with Automation Tools

### Playwright

```go
import "github.com/playwright-community/playwright-go"

// Get endpoint
endpoint, err := session.Browser.GetEndpointURL()

// Connect Playwright
pw, err := playwright.Run()
defer pw.Stop()

browser, err := pw.Chromium.ConnectOverCDP(endpoint)
defer browser.Close()

page, err := browser.Contexts()[0].NewPage()
```

### Puppeteer (via Node.js)

```go
// Get endpoint
endpoint, err := session.Browser.GetEndpointURL()
fmt.Printf("Use this endpoint in Node.js: %s\n", endpoint)
```

```javascript
// In Node.js
const puppeteer = require('puppeteer-core');
const browser = await puppeteer.connect({
    browserWSEndpoint: 'ws://...' // endpoint from Go
});
```

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
4. **Connection Pooling**: Maintain persistent CDP connections

## Troubleshooting

### Browser Won't Initialize

```go
// Check session status
if !result.Success {
    log.Printf("Session creation failed: %s", result.ErrorMessage)
}

// Verify image supports browser
params := &agentbay.CreateSessionParams{
    ImageId: "browser_latest", // Ensure browser-enabled image
}

// Check initialization
success, err := session.Browser.Initialize(option)
log.Printf("Success: %v, Error: %v", success, err)
```

### CDP Connection Fails

```go
// Ensure browser is initialized
if !session.Browser.IsInitialized() {
    log.Fatal("Browser not initialized")
}

// Get and verify endpoint
endpoint, err := session.Browser.GetEndpointURL()
if err != nil {
    log.Fatalf("Cannot get endpoint: %v", err)
}
log.Printf("Endpoint: %s", endpoint)
```

### Configuration Issues

```go
// Validate before use
if err := option.Validate(); err != nil {
    log.Fatalf("Configuration error: %v", err)
}

// Check pointer fields
if option.UserAgent != nil {
    log.Printf("Using custom UA: %s", *option.UserAgent)
}

if option.BrowserType != nil {
    log.Printf("Browser type: %s", *option.BrowserType)
}
```

## See Also

- [Browser Use Guide](../../../docs/guides/browser-use/README.md) - Complete guide with examples
- [Core Features](../../../docs/guides/browser-use/core-features.md) - Essential browser features
- [Advanced Features](../../../docs/guides/browser-use/advance-features.md) - Advanced configuration
- [Browser Examples](../examples/browser/README.md) - Runnable example code
- [Session Management](session.md) - Session lifecycle and management

