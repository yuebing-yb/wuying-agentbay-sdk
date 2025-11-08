# Browser API Reference

## 🌐 Related Tutorial

- [Browser Use Guide](../../../../../docs/guides/browser-use/README.md) - Complete guide to browser automation

## Overview

The Browser module provides comprehensive browser automation capabilities including navigation, element interaction,
screenshot capture, and content extraction. It enables automated testing and web scraping workflows.

## Requirements

- Requires `browser_latest` image for browser automation features

## Type Browser

```go
type Browser struct {
	session		SessionInterface
	endpointURL	string
	initialized	bool
	option		*BrowserOption
}
```

Browser provides browser-related operations for the session

### Methods

#### Destroy

```go
func (b *Browser) Destroy() error
```

Destroy the browser instance

**Example:**

```go
package main
import (
	"fmt"
	"os"
	"github.com/aliyun/wuying-agentbay-sdk/golang/pkg/agentbay"
	"github.com/aliyun/wuying-agentbay-sdk/golang/pkg/agentbay/browser"
)
func main() {
	client, err := agentbay.NewAgentBay(os.Getenv("AGENTBAY_API_KEY"), nil)
	if err != nil {
		fmt.Printf("Error: %v\n", err)
		os.Exit(1)
	}
	result, err := client.Create(nil)
	if err != nil {
		fmt.Printf("Error: %v\n", err)
		os.Exit(1)
	}
	session := result.Session

	// Initialize browser

	option := browser.NewBrowserOption()
	success, err := session.Browser.Initialize(option)
	if err != nil {
		fmt.Printf("Error: %v\n", err)
		os.Exit(1)
	}
	if !success {
		fmt.Println("Failed to initialize browser")
		os.Exit(1)
	}
	fmt.Println("Browser initialized successfully")

	// Output: Browser initialized successfully

	// Use browser for automation tasks...

	// Destroy browser instance

	err = session.Browser.Destroy()
	if err != nil {
		fmt.Printf("Error: %v\n", err)
		os.Exit(1)
	}
	fmt.Println("Browser destroyed successfully")

	// Output: Browser destroyed successfully

	session.Delete()
}
```

#### GetEndpointURL

```go
func (b *Browser) GetEndpointURL() (string, error)
```

GetEndpointURL returns the endpoint URL if the browser is initialized

**Example:**

```go
endpointURL, err := session.Browser.GetEndpointURL()
if err != nil {
    log.Fatalf("Failed to get endpoint URL: %v", err)
}

// Use with Playwright

pw, err := playwright.Run()
defer pw.Stop()
browser, err := pw.Chromium.ConnectOverCDP(endpointURL)
defer browser.Close()
page, err := browser.Contexts()[0].NewPage()
```

#### GetOption

```go
func (b *Browser) GetOption() *BrowserOption
```

GetOption returns the current BrowserOption used to initialize the browser, or nil if not set

#### Initialize

```go
func (b *Browser) Initialize(option *BrowserOption) (bool, error)
```

Initialize initializes the browser instance with the given options. Returns true and nil error if
successful, false and error otherwise.

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

#### IsInitialized

```go
func (b *Browser) IsInitialized() bool
```

IsInitialized returns true if the browser was initialized, false otherwise

#### Screenshot

```go
func (b *Browser) Screenshot(page interface{}, options *ScreenshotOptions) ([]byte, error)
```

Screenshot takes a screenshot of the specified page with enhanced options and error handling.
This method requires the caller to connect to the browser via Playwright or similar and pass the
page object to this method.

Parameters:
  - page: The Playwright Page object to take a screenshot of. This is a required parameter.
  - options: Screenshot options including:
  - FullPage (bool): Whether to capture the full scrollable page. Defaults to false.
  - Type (string): Image type, either "png" or "jpeg". Defaults to "png".
  - Quality (int): Quality of the image, between 0-100 (jpeg only). Defaults to 0.
  - Timeout (int): Maximum time in milliseconds. Defaults to 60000.

Returns:
  - []byte: Screenshot data as bytes.
  - error: Error if browser is not initialized or screenshot capture fails.

**Example:**

```go
package main
import (
	"fmt"
	"os"
	"github.com/aliyun/wuying-agentbay-sdk/golang/pkg/agentbay"
	"github.com/aliyun/wuying-agentbay-sdk/golang/pkg/agentbay/browser"
	"github.com/playwright-community/playwright-go"
)
func main() {
	client, err := agentbay.NewAgentBay(os.Getenv("AGENTBAY_API_KEY"), nil)
	if err != nil {
		fmt.Printf("Error: %v\n", err)
		os.Exit(1)
	}
	result, err := client.Create(nil)
	if err != nil {
		fmt.Printf("Error: %v\n", err)
		os.Exit(1)
	}
	session := result.Session

	// Initialize browser

	option := browser.NewBrowserOption()
	success, err := session.Browser.Initialize(option)
	if err != nil {
		fmt.Printf("Error: %v\n", err)
		os.Exit(1)
	}
	if !success {
		os.Exit(1)
	}

	// Get endpoint URL and connect with Playwright

	endpointURL, err := session.Browser.GetEndpointURL()
	if err != nil {
		fmt.Printf("Error: %v\n", err)
		os.Exit(1)
	}

	// Connect to browser via Playwright

	pw, err := playwright.Run()
	if err != nil {
		fmt.Printf("Error: %v\n", err)
		os.Exit(1)
	}
	defer pw.Stop()
	browser, err := pw.Chromium.ConnectOverCDP(endpointURL)
	if err != nil {
		fmt.Printf("Error: %v\n", err)
		os.Exit(1)
	}
	defer browser.Close()

	// Get the page

	contexts := browser.Contexts()
	if len(contexts) == 0 {
		fmt.Println("No browser contexts available")
		os.Exit(1)
	}
	page, err := contexts[0].NewPage()
	if err != nil {
		fmt.Printf("Error: %v\n", err)
		os.Exit(1)
	}

	// Navigate to a URL

	_, err = page.Goto("https://example.com")
	if err != nil {
		fmt.Printf("Error: %v\n", err)
		os.Exit(1)
	}

	// Take screenshot with custom options

	screenshotOptions := &browser.ScreenshotOptions{
		FullPage: true,
		Type:     "png",
		Timeout:  60000,
	}
	screenshotData, err := session.Browser.Screenshot(page, screenshotOptions)
	if err != nil {
		fmt.Printf("Error: %v\n", err)
		os.Exit(1)
	}

	// Save screenshot to file

	err = os.WriteFile("/tmp/screenshot.png", screenshotData, 0644)
	if err != nil {
		fmt.Printf("Error: %v\n", err)
		os.Exit(1)
	}
	fmt.Printf("Screenshot saved successfully (%d bytes)\n", len(screenshotData))

	// Output: Screenshot saved successfully (12345 bytes)

	session.Delete()
}
```

#### _scrollToLoadAllContent

```go
func (b *Browser) _scrollToLoadAllContent(page interface {
	Evaluate(expression string, options ...interface{}) (interface{}, error)
	WaitForTimeout(timeout int)
}, maxScrolls int, delayMs int) error
```

_scrollToLoadAllContent scrolls the page to load all content (especially for lazy-loaded elements)

### Related Functions

#### NewBrowser

```go
func NewBrowser(session SessionInterface) *Browser
```

NewBrowser creates a new Browser instance

## Type BrowserFingerprint

```go
type BrowserFingerprint struct {
	Devices			[]string	`json:"devices,omitempty"`		// Device types: "desktop" or "mobile"
	OperatingSystems	[]string	`json:"operatingSystems,omitempty"`	// OS types: "windows", "macos", "linux", "android", "ios"
	Locales			[]string	`json:"locales,omitempty"`		// Locale identifiers
}
```

BrowserFingerprint represents browser fingerprint options

**Example:**

```go
fingerprint := &browser.BrowserFingerprint{
    Devices:          []string{"desktop"},
    OperatingSystems: []string{"windows", "macos"},
    Locales:          []string{"en-US", "en-GB"},
}
```

### Methods

#### ToMap

```go
func (f *BrowserFingerprint) ToMap() map[string]interface{}
```

ToMap converts BrowserFingerprint to map for API request

### Related Functions

#### NewBrowserFingerprint

```go
func NewBrowserFingerprint(devices, operatingSystems, locales []string) (*BrowserFingerprint, error)
```

NewBrowserFingerprint creates a new BrowserFingerprint with validation

## Type BrowserOption

```go
type BrowserOption struct {
	UseStealth		bool			`json:"useStealth,omitempty"`		// Enable stealth mode
	UserAgent		*string			`json:"userAgent,omitempty"`		// Custom user agent
	Viewport		*BrowserViewport	`json:"viewport,omitempty"`		// Viewport configuration
	Screen			*BrowserScreen		`json:"screen,omitempty"`		// Screen configuration
	Fingerprint		*BrowserFingerprint	`json:"fingerprint,omitempty"`		// Fingerprint configuration
	SolveCaptchas		bool			`json:"solveCaptchas,omitempty"`	// Auto-solve captchas
	Proxies			[]*BrowserProxy		`json:"proxies,omitempty"`		// Proxy configurations
	ExtensionPath		*string			`json:"extensionPath,omitempty"`	// Path to extensions directory
	CmdArgs			[]string		`json:"cmdArgs,omitempty"`		// Additional command line arguments
	DefaultNavigateUrl	*string			`json:"defaultNavigateUrl,omitempty"`	// Default URL to navigate to when browser starts
	BrowserType		*string			`json:"browserType,omitempty"`		// Browser type: "chrome" or "chromium"
}
```

BrowserOption represents browser initialization options

**Example:**

```go
option := browser.NewBrowserOption()

// Custom user agent

ua := "Mozilla/5.0 (Windows NT 10.0; Win64; x64) Chrome/120.0.0.0"
option.UserAgent = &ua

// Viewport and screen

option.Viewport = &browser.BrowserViewport{Width: 1920, Height: 1080}
option.Screen = &browser.BrowserScreen{Width: 1920, Height: 1080}

// Stealth mode

option.UseStealth = true

// Validate configuration

if err := option.Validate(); err != nil {
    log.Fatalf("Invalid configuration: %v", err)
}
```

### Methods

#### ToMap

```go
func (o *BrowserOption) ToMap() map[string]interface{}
```

ToMap converts BrowserOption to map for API request

#### Validate

```go
func (o *BrowserOption) Validate() error
```

Validate validates the BrowserOption

### Related Functions

#### NewBrowserOption

```go
func NewBrowserOption() *BrowserOption
```

NewBrowserOption creates a new BrowserOption with default values and validation

## Type BrowserProxy

```go
type BrowserProxy struct {
	Type		string	`json:"type"`			// Type of proxy - "custom" or "wuying"
	Server		*string	`json:"server,omitempty"`	// Proxy server address (required for custom type)
	Username	*string	`json:"username,omitempty"`	// Proxy username (optional for custom type)
	Password	*string	`json:"password,omitempty"`	// Proxy password (optional for custom type)
	Strategy	*string	`json:"strategy,omitempty"`	// Strategy for wuying: "restricted" or "polling"
	PollSize	*int	`json:"pollsize,omitempty"`	// Pool size (optional for wuying with polling strategy)
}
```

BrowserProxy represents browser proxy configuration. Supports two types of proxy: custom proxy and
wuying proxy. Wuying proxy supports two strategies: restricted and polling.

**Example:**

```go
// Custom proxy

server := "proxy.example.com:8080"
username := "user"
password := "pass"
customProxy := &browser.BrowserProxy{
    Type:     "custom",
    Server:   &server,
    Username: &username,
    Password: &password,
}

// WuYing proxy with restricted strategy

strategy := "restricted"
wuyingProxy := &browser.BrowserProxy{
    Type:     "wuying",
    Strategy: &strategy,
}

// WuYing proxy with polling strategy

pollingStrategy := "polling"
pollSize := 10
pollingProxy := &browser.BrowserProxy{
    Type:     "wuying",
    Strategy: &pollingStrategy,
    PollSize: &pollSize,
}
```

### Methods

#### ToMap

```go
func (p *BrowserProxy) ToMap() map[string]interface{}
```

ToMap converts BrowserProxy to map for API request

### Related Functions

#### NewBrowserProxy

```go
func NewBrowserProxy(proxyType string, server, username, password, strategy *string, pollSize *int) (*BrowserProxy, error)
```

NewBrowserProxy creates a new BrowserProxy with validation

## Type BrowserScreen

```go
type BrowserScreen struct {
	Width	int	`json:"width"`	// Screen width
	Height	int	`json:"height"`	// Screen height
}
```

BrowserScreen represents browser screen options

### Methods

#### ToMap

```go
func (s *BrowserScreen) ToMap() map[string]interface{}
```

ToMap converts BrowserScreen to map for API request

## Type BrowserViewport

```go
type BrowserViewport struct {
	Width	int	`json:"width"`	// Viewport width
	Height	int	`json:"height"`	// Viewport height
}
```

BrowserViewport represents browser viewport options

### Methods

#### ToMap

```go
func (v *BrowserViewport) ToMap() map[string]interface{}
```

ToMap converts BrowserViewport to map for API request

## Type LinkResult

```go
type LinkResult struct {
	Link string
}
```

SessionInterface defines a minimal interface for Browser to interact with Session This interface
allows us to avoid circular dependencies while still accessing necessary Session methods LinkResult
represents the result of GetLink call

## Type McpToolResult

```go
type McpToolResult struct {
	Success		bool
	Data		string
	ErrorMessage	string
}
```

McpToolResult represents the result of CallMcpTool call

## Type ScreenshotOptions

```go
type ScreenshotOptions struct {
	FullPage	bool
	Type		string	// "png" or "jpeg"
	Quality		int	// 0-100 for jpeg
	Timeout		int	// timeout in milliseconds
}
```

ScreenshotOptions represents options for taking screenshots

## Type SessionInterface

```go
type SessionInterface interface {
	GetAPIKey() string
	GetSessionID() string
	GetClient() *client.Client
	CallMcpToolForBrowser(toolName string, args interface{}) (*McpToolResult, error)
	GetLinkForBrowser(protocolType *string, port *int32, options *string) (*LinkResult, error)
	IsVPCEnabled() bool
	GetNetworkInterfaceIP() string
	GetHttpPortNumber() string
}
```

SessionInterface defines the interface that Session must implement for Browser

## Functions

### min

```go
func min(a, b int) int
```

Helper function to find minimum of two integers

## Best Practices

1. Wait for page load completion before interacting with elements
2. Use appropriate selectors (CSS, XPath) for reliable element identification
3. Handle navigation timeouts and errors gracefully
4. Take screenshots for debugging and verification
5. Clean up browser resources after automation tasks

## Related Resources

- [Extension API Reference](extension.md)
- [Session API Reference](../../common-features/basics/session.md)

---

*Documentation generated automatically from Go source code.*
