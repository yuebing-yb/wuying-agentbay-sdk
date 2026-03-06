package browser

import (
	"errors"
	"fmt"
	"os"

	"github.com/alibabacloud-go/tea/dara"
	"github.com/aliyun/wuying-agentbay-sdk/golang/api/client"
	"github.com/aliyun/wuying-agentbay-sdk/golang/pkg/agentbay/internal"
	"github.com/playwright-community/playwright-go"
)

// BrowserProxy represents browser proxy configuration.
// Supports three types of proxy: custom proxy, wuying proxy, and managed proxy.
// - Custom proxy: User-provided proxy servers
// - Wuying proxy: Alibaba Cloud proxy service (strategies: restricted, polling)
// - Managed proxy: Client-provided proxies managed by Wuying platform (strategies: polling, sticky, rotating, matched)
//
// Example:
//
//	// Custom proxy
//	server := "proxy.example.com:8080"
//	username := "user"
//	password := "pass"
//	customProxy := &browser.BrowserProxy{
//	    Type:     "custom",
//	    Server:   &server,
//	    Username: &username,
//	    Password: &password,
//	}
//
//	// WuYing proxy with restricted strategy
//	strategy := "restricted"
//	wuyingProxy := &browser.BrowserProxy{
//	    Type:     "wuying",
//	    Strategy: &strategy,
//	}
//
//	// WuYing proxy with polling strategy
//	pollingStrategy := "polling"
//	pollSize := 10
//	pollingProxy := &browser.BrowserProxy{
//	    Type:     "wuying",
//	    Strategy: &pollingStrategy,
//	    PollSize: &pollSize,
//	}
//
//	// Managed proxy with sticky strategy
//	managedStrategy := "sticky"
//	userID := "user123"
//	managedProxy := &browser.BrowserProxy{
//	    Type:     "managed",
//	    Strategy: &managedStrategy,
//	    UserID:   &userID,
//	}
//
//	// Managed proxy with matched strategy
//	matchedStrategy := "matched"
//	isp := "China Telecom"
//	country := "China"
//	province := "Beijing"
//	matchedProxy := &browser.BrowserProxy{
//	    Type:     "managed",
//	    Strategy: &matchedStrategy,
//	    UserID:   &userID,
//	    ISP:      &isp,
//	    Country:  &country,
//	    Province: &province,
//	}
type BrowserProxy struct {
	Type     string  `json:"type"`               // Type of proxy - "custom", "wuying", or "managed"
	Server   *string `json:"server,omitempty"`   // Proxy server address (required for custom type)
	Username *string `json:"username,omitempty"` // Proxy username (optional for custom type)
	Password *string `json:"password,omitempty"` // Proxy password (optional for custom type)
	Strategy *string `json:"strategy,omitempty"` // Strategy for wuying: "restricted" or "polling"; for managed: "polling", "sticky", "rotating", "matched"
	PollSize *int    `json:"pollsize,omitempty"` // Pool size (optional for wuying with polling strategy)
	UserID   *string `json:"user_id,omitempty"`  // Custom user identifier for tracking proxy allocation records (required for managed type)
	ISP      *string `json:"isp,omitempty"`      // ISP filter (optional for managed matched strategy)
	Country  *string `json:"country,omitempty"`  // Country filter (optional for managed matched strategy)
	Province *string `json:"province,omitempty"` // Province filter (optional for managed matched strategy)
	City     *string `json:"city,omitempty"`     // City filter (optional for managed matched strategy)
}

// NewBrowserProxy creates a new BrowserProxy with validation
func NewBrowserProxy(proxyType string, server, username, password, strategy *string, pollSize *int, userID, isp, country, province, city *string) (*BrowserProxy, error) {
	proxy := &BrowserProxy{
		Type:     proxyType,
		Server:   server,
		Username: username,
		Password: password,
		Strategy: strategy,
		PollSize: pollSize,
		UserID:   userID,
		ISP:      isp,
		Country:  country,
		Province: province,
		City:     city,
	}

	// Validation
	if proxyType != "custom" && proxyType != "wuying" && proxyType != "managed" {
		return nil, errors.New("proxy_type must be custom, wuying, or managed")
	}

	if proxyType == "custom" && (server == nil || *server == "") {
		return nil, errors.New("server is required for custom proxy type")
	}

	if proxyType == "wuying" {
		if strategy == nil || *strategy == "" {
			return nil, errors.New("strategy is required for wuying proxy type")
		}
		if *strategy != "restricted" && *strategy != "polling" {
			return nil, errors.New("strategy must be restricted or polling for wuying proxy type")
		}
		if *strategy == "polling" && pollSize != nil && *pollSize <= 0 {
			return nil, errors.New("pollsize must be greater than 0 for polling strategy")
		}
	}

	if proxyType == "managed" {
		if strategy == nil || *strategy == "" {
			return nil, errors.New("strategy is required for managed proxy type")
		}
		if *strategy != "polling" && *strategy != "sticky" && *strategy != "rotating" && *strategy != "matched" {
			return nil, errors.New("strategy must be polling, sticky, rotating, or matched for managed proxy type")
		}
		if userID == nil || *userID == "" {
			return nil, errors.New("user_id is required for managed proxy type")
		}
		if *strategy == "matched" && (isp == nil || *isp == "") && (country == nil || *country == "") && (province == nil || *province == "") && (city == nil || *city == "") {
			return nil, errors.New("at least one of isp, country, province, or city is required for matched strategy")
		}
	}

	return proxy, nil
}

// toMap converts BrowserProxy to map for API request
func (p *BrowserProxy) toMap() map[string]interface{} {
	proxyMap := map[string]interface{}{
		"type": p.Type,
	}

	if p.Type == "custom" {
		if p.Server != nil {
			proxyMap["server"] = *p.Server
		}
		if p.Username != nil {
			proxyMap["username"] = *p.Username
		}
		if p.Password != nil {
			proxyMap["password"] = *p.Password
		}
	} else if p.Type == "wuying" {
		if p.Strategy != nil {
			proxyMap["strategy"] = *p.Strategy
		}
		if p.Strategy != nil && *p.Strategy == "polling" && p.PollSize != nil {
			proxyMap["pollsize"] = *p.PollSize
		}
	} else if p.Type == "managed" {
		if p.Strategy != nil {
			proxyMap["strategy"] = *p.Strategy
		}
		if p.UserID != nil {
			proxyMap["userId"] = *p.UserID
		}
		if p.ISP != nil {
			proxyMap["isp"] = *p.ISP
		}
		if p.Country != nil {
			proxyMap["country"] = *p.Country
		}
		if p.Province != nil {
			proxyMap["province"] = *p.Province
		}
		if p.City != nil {
			proxyMap["city"] = *p.City
		}
	}

	return proxyMap
}

// BrowserViewport represents browser viewport options
type BrowserViewport struct {
	Width  int `json:"width"`  // Viewport width
	Height int `json:"height"` // Viewport height
}

// toMap converts BrowserViewport to map for API request
func (v *BrowserViewport) toMap() map[string]interface{} {
	return map[string]interface{}{
		"width":  v.Width,
		"height": v.Height,
	}
}

// BrowserScreen represents browser screen options
type BrowserScreen struct {
	Width  int `json:"width"`  // Screen width
	Height int `json:"height"` // Screen height
}

// toMap converts BrowserScreen to map for API request
func (s *BrowserScreen) toMap() map[string]interface{} {
	return map[string]interface{}{
		"width":  s.Width,
		"height": s.Height,
	}
}

// BrowserFingerprint represents browser fingerprint options
//
// Example:
//
//	fingerprint := &browser.BrowserFingerprint{
//	    Devices:          []string{"desktop"},
//	    OperatingSystems: []string{"windows", "macos"},
//	    Locales:          []string{"en-US", "en-GB"},
//	}
type BrowserFingerprint struct {
	Devices          []string `json:"devices,omitempty"`          // Device types: "desktop" or "mobile"
	OperatingSystems []string `json:"operatingSystems,omitempty"` // OS types: "windows", "macos", "linux", "android", "ios"
	Locales          []string `json:"locales,omitempty"`          // Locale identifiers
}

// NewBrowserFingerprint creates a new BrowserFingerprint with validation
func NewBrowserFingerprint(devices, operatingSystems, locales []string) (*BrowserFingerprint, error) {
	// Validate devices
	if devices != nil {
		for _, device := range devices {
			if device != "desktop" && device != "mobile" {
				return nil, errors.New("device must be desktop or mobile")
			}
		}
	}

	// Validate operating systems
	if operatingSystems != nil {
		validOS := map[string]bool{"windows": true, "macos": true, "linux": true, "android": true, "ios": true}
		for _, os := range operatingSystems {
			if !validOS[os] {
				return nil, errors.New("operating_system must be windows, macos, linux, android or ios")
			}
		}
	}

	return &BrowserFingerprint{
		Devices:          devices,
		OperatingSystems: operatingSystems,
		Locales:          locales,
	}, nil
}

// toMap converts BrowserFingerprint to map for API request
func (f *BrowserFingerprint) toMap() map[string]interface{} {
	fpMap := make(map[string]interface{})
	if f.Devices != nil {
		fpMap["devices"] = f.Devices
	}
	if f.OperatingSystems != nil {
		fpMap["operatingSystems"] = f.OperatingSystems
	}
	if f.Locales != nil {
		fpMap["locales"] = f.Locales
	}
	return fpMap
}

// BrowserOption represents browser initialization options
//
// Example:
//
//	option := browser.NewBrowserOption()
//
//	// Custom user agent
//	ua := "Mozilla/5.0 (Windows NT 10.0; Win64; x64) Chrome/120.0.0.0"
//	option.UserAgent = &ua
//
//	// Viewport and screen
//	option.Viewport = &browser.BrowserViewport{Width: 1920, Height: 1080}
//	option.Screen = &browser.BrowserScreen{Width: 1920, Height: 1080}
//
//	// Stealth mode
//	option.UseStealth = true
//
//	// Validate configuration
//	if err := option.Validate(); err != nil {
//	    log.Fatalf("Invalid configuration: %v", err)
//	}
type BrowserOption struct {
	UseStealth         bool                `json:"useStealth,omitempty"`         // Enable stealth mode
	UserAgent          *string             `json:"userAgent,omitempty"`          // Custom user agent
	Viewport           *BrowserViewport    `json:"viewport,omitempty"`           // Viewport configuration
	Screen             *BrowserScreen      `json:"screen,omitempty"`             // Screen configuration
	Fingerprint        *BrowserFingerprint `json:"fingerprint,omitempty"`        // Fingerprint configuration
	SolveCaptchas      bool                `json:"solveCaptchas,omitempty"`      // Auto-solve captchas
	AutoLogin          bool                `json:"autoLogin,omitempty"`          // Enable auto login feature
	CallForUser        bool                `json:"callForUser,omitempty"`        // Enable call for user feature
	Proxies            []*BrowserProxy     `json:"proxies,omitempty"`            // Proxy configurations
	ExtensionPath      *string             `json:"extensionPath,omitempty"`      // Path to extensions directory
	CmdArgs            []string            `json:"cmdArgs,omitempty"`            // Additional command line arguments
	DefaultNavigateUrl *string             `json:"defaultNavigateUrl,omitempty"` // Default URL to navigate to when browser starts
	BrowserType        *string             `json:"browserType,omitempty"`        // Browser type: "chrome" or "chromium"
}

// NewBrowserOption creates a new BrowserOption with default values and validation
//
// Example:
//
//	option := browser.NewBrowserOption()
//	option.UseStealth = true
func NewBrowserOption() *BrowserOption {
	defaultExtPath := "/tmp/extensions/"
	return &BrowserOption{
		UseStealth:    false,
		SolveCaptchas: false,
		AutoLogin:     false,
		CallForUser:   false,
		ExtensionPath: &defaultExtPath,
		BrowserType:   nil, // Default to nil (no browser type specified)
	}
}

// Validate validates the BrowserOption
//
// Example:
//
//	package main
//	import (
//		"fmt"
//		"os"
//		"github.com/aliyun/wuying-agentbay-sdk/golang/pkg/agentbay/browser"
//	)
//	func main() {
//		option := browser.NewBrowserOption()
//
//		// Set custom configuration
//		customUA := "Mozilla/5.0 (Windows NT 10.0; Win64; x64) Chrome/120.0.0.0"
//		option.UserAgent = &customUA
//		option.UseStealth = true
//
//		// Validate before use
//		if err := option.Validate(); err != nil {
//			fmt.Printf("Error: %v\n", err)
//			os.Exit(1)
//		}
//		fmt.Println("Browser option validated successfully")
//
//		// Output: Browser option validated successfully
//	}
func (o *BrowserOption) Validate() error {
	// Validate proxies
	if len(o.Proxies) > 1 {
		return errors.New("proxies list length must be limited to 1")
	}

	// Validate extension path
	if o.ExtensionPath != nil && *o.ExtensionPath == "" {
		return errors.New("extensionPath cannot be empty")
	}

	// Validate browser type
	if o.BrowserType != nil && *o.BrowserType != "chrome" && *o.BrowserType != "chromium" {
		return errors.New("browserType must be 'chrome' or 'chromium'")
	}

	// Validate cmdArgs (no specific validation needed, just ensure it's not nil when empty)
	// CmdArgs can be any slice of strings

	// Validate defaultNavigateUrl (no specific validation needed for URL format)
	// DefaultNavigateUrl can be any string

	return nil
}

// toMap converts BrowserOption to map for API request
func (o *BrowserOption) toMap() map[string]interface{} {
	optionMap := make(map[string]interface{})

	// Check for AGENTBAY_BROWSER_BEHAVIOR_SIMULATE environment variable
	if behaviorSimulate := os.Getenv("AGENTBAY_BROWSER_BEHAVIOR_SIMULATE"); behaviorSimulate != "" {
		optionMap["behaviorSimulate"] = behaviorSimulate != "0"
	}

	optionMap["useStealth"] = o.UseStealth

	if o.UserAgent != nil {
		optionMap["userAgent"] = *o.UserAgent
	}

	if o.Viewport != nil {
		optionMap["viewport"] = o.Viewport.toMap()
	}

	if o.Screen != nil {
		optionMap["screen"] = o.Screen.toMap()
	}

	if o.Fingerprint != nil {
		optionMap["fingerprint"] = o.Fingerprint.toMap()
	}

	optionMap["solveCaptchas"] = o.SolveCaptchas
	optionMap["autoLogin"] = o.AutoLogin
	optionMap["callForUser"] = o.CallForUser

	if len(o.Proxies) > 0 {
		proxies := make([]map[string]interface{}, len(o.Proxies))
		for i, proxy := range o.Proxies {
			proxies[i] = proxy.toMap()
		}
		optionMap["proxies"] = proxies
	}

	if o.ExtensionPath != nil {
		optionMap["extensionPath"] = *o.ExtensionPath
	}

	if len(o.CmdArgs) > 0 {
		optionMap["cmdArgs"] = o.CmdArgs
	}

	if o.DefaultNavigateUrl != nil {
		optionMap["defaultNavigateUrl"] = *o.DefaultNavigateUrl
	}

	if o.BrowserType != nil {
		optionMap["browserType"] = *o.BrowserType
	}

	return optionMap
}

// SessionInterface defines a minimal interface for Browser to interact with Session
// This interface allows us to avoid circular dependencies while still accessing
// necessary Session methods
// LinkResult represents the result of GetLink call
type LinkResult struct {
	Link string
}

// McpToolResult represents the result of CallMcpTool call
type McpToolResult struct {
	Success      bool
	Data         string
	ErrorMessage string
}

// SessionInterface defines the interface that Session must implement for Browser
type SessionInterface interface {
	GetAPIKey() string
	GetSessionID() string
	GetClient() *client.Client
	CallMcpToolForBrowser(toolName string, args interface{}) (*McpToolResult, error)
	GetLinkForBrowser(protocolType *string, port *int32, options *string) (*LinkResult, error)
	GetWsClient() (interface{}, error)
}

// Browser provides browser-related operations for the session
//
// > **⚠️ Note**: Currently, for agent services (including ComputerUseAgent, BrowserUseAgent, and MobileUseAgent), we do not provide services for overseas users registered with **alibabacloud.com**.
// BrowserNotifyMessage represents a browser notify message for SDK and sandbox communication
type BrowserNotifyMessage struct {
	Type        *string                `json:"type,omitempty"`
	ID          *int                   `json:"id,omitempty"`
	Code        *int                   `json:"code,omitempty"`
	Message     *string                `json:"message,omitempty"`
	Action      *string                `json:"action,omitempty"`
	ExtraParams map[string]interface{} `json:"extraParams,omitempty"`
}

// NewBrowserNotifyMessage creates a new BrowserNotifyMessage
func NewBrowserNotifyMessage(msgType *string, id *int, code *int, message *string, action *string, extraParams map[string]interface{}) *BrowserNotifyMessage {
	if extraParams == nil {
		extraParams = make(map[string]interface{})
	}
	return &BrowserNotifyMessage{
		Type:        msgType,
		ID:          id,
		Code:        code,
		Message:     message,
		Action:      action,
		ExtraParams: extraParams,
	}
}

// ToMap converts BrowserNotifyMessage to map format
func (b *BrowserNotifyMessage) ToMap() map[string]interface{} {
	notifyMap := make(map[string]interface{})

	if b.Type != nil {
		notifyMap["type"] = *b.Type
	}
	if b.ID != nil {
		notifyMap["id"] = *b.ID
	}
	if b.Code != nil {
		notifyMap["code"] = *b.Code
	}
	if b.Message != nil {
		notifyMap["message"] = *b.Message
	}
	if b.Action != nil {
		notifyMap["action"] = *b.Action
	}
	if len(b.ExtraParams) > 0 {
		notifyMap["extraParams"] = b.ExtraParams
	}

	return notifyMap
}

// FromMap creates BrowserNotifyMessage from map format
func BrowserNotifyMessageFromMap(m map[string]interface{}) *BrowserNotifyMessage {
	if m == nil {
		return nil
	}

	msg := &BrowserNotifyMessage{}

	if v, ok := m["type"].(string); ok {
		msg.Type = &v
	}
	if v, ok := m["id"].(float64); ok {
		id := int(v)
		msg.ID = &id
	} else if v, ok := m["id"].(int); ok {
		msg.ID = &v
	}
	if v, ok := m["code"].(float64); ok {
		code := int(v)
		msg.Code = &code
	} else if v, ok := m["code"].(int); ok {
		msg.Code = &v
	}
	if v, ok := m["message"].(string); ok {
		msg.Message = &v
	}
	if v, ok := m["action"].(string); ok {
		msg.Action = &v
	}
	if v, ok := m["extraParams"].(map[string]interface{}); ok {
		msg.ExtraParams = v
	}

	return msg
}

// BrowserCallback is a function type for browser notification callbacks
type BrowserCallback func(*BrowserNotifyMessage)

type Browser struct {
	session              SessionInterface
	endpointURL          string
	initialized          bool
	option               *BrowserOption
	userCallback         BrowserCallback
	wsCallbackRegistered bool
}

// NewBrowser creates a new Browser instance
func NewBrowser(session SessionInterface) *Browser {
	return &Browser{
		session:     session,
		initialized: false,
	}
}

// IsInitialized returns true if the browser was initialized, false otherwise
//
// Example:
//
//	if session.Browser.IsInitialized() {
//	    // Browser is ready
//	}
func (b *Browser) IsInitialized() bool {
	return b.initialized
}

// GetOption returns the current BrowserOption used to initialize the browser, or nil if not set
//
// Example:
//
//	currentOption := session.Browser.GetOption()
//	if currentOption != nil && currentOption.UseStealth {
//	    // Stealth mode is enabled
//	}
func (b *Browser) GetOption() *BrowserOption {
	return b.option
}

// GetEndpointURL returns the endpoint URL if the browser is initialized
//
// Example:
//
//	client, _ := agentbay.NewAgentBay(os.Getenv("AGENTBAY_API_KEY"), nil)
//	result, _ := client.Create(agentbay.NewCreateSessionParams().WithImageId("browser_latest"))
//	defer result.Session.Delete()
//	session.Browser.Initialize(browser.NewBrowserOption())
//	endpointURL, _ := session.Browser.GetEndpointURL()
//	pw, _ := playwright.Run()
//	browserConn, _ := pw.Chromium.ConnectOverCDP(endpointURL)
//	defer browserConn.Close()
func (b *Browser) GetEndpointURL() (string, error) {
	if !b.initialized {
		return "", errors.New("browser is not initialized. Cannot access endpoint URL")
	}
	// Use GetCdpLink API
	request := &client.GetCdpLinkRequest{
		Authorization: dara.String(fmt.Sprintf("Bearer %s", b.session.GetAPIKey())),
		SessionId:     dara.String(b.session.GetSessionID()),
	}

	response, err := b.session.GetClient().GetCdpLink(request)
	if err != nil {
		return "", fmt.Errorf("failed to get CDP link: %w", err)
	}

	if response.Body == nil || response.Body.Success == nil || !*response.Body.Success {
		errorMsg := "Unknown error"
		if response.Body != nil && response.Body.Message != nil {
			errorMsg = *response.Body.Message
		}
		return "", fmt.Errorf("failed to get CDP link: %s", errorMsg)
	}

	if response.Body.Data == nil || response.Body.Data.Url == nil {
		return "", errors.New("CDP link URL is empty in response")
	}

	b.endpointURL = *response.Body.Data.Url
	return b.endpointURL, nil
}

// Initialize initializes the browser instance with the given options.
// Returns true and nil error if successful, false and error otherwise.
//
// Example:
//
//	option := browser.NewBrowserOption()
//	option.UseStealth = true
//	success, _ := session.Browser.Initialize(option)
//	if success {
//	    endpoint, _ := session.Browser.GetEndpointURL()
//	    pw, _ := playwright.Run()
//	    remoteBrowser, _ := pw.Chromium.ConnectOverCDP(endpoint)
//	    defer remoteBrowser.Close()
//	}
func (b *Browser) Initialize(option *BrowserOption) (bool, error) {
	if b.initialized {
		return true, nil
	}

	// Validate the option
	if err := option.Validate(); err != nil {
		return false, fmt.Errorf("invalid browser option: %w", err)
	}

	// Convert option to map
	browserOptionMap := option.toMap()

	// Set enableRecord based on session.enableBrowserReplay
	// Check if session implements GetEnableBrowserReplay method
	if enableReplayGetter, ok := b.session.(interface {
		GetEnableBrowserReplay() bool
	}); ok {
		browserOptionMap["enableRecord"] = enableReplayGetter.GetEnableBrowserReplay()
	}

	// Create InitBrowserRequest
	authorization := "Bearer " + b.session.GetAPIKey()
	sessionID := b.session.GetSessionID()
	persistentPath := "/tmp/agentbay_browser" // Match Python BROWSER_DATA_PATH

	request := &client.InitBrowserRequest{
		Authorization:  &authorization,
		SessionId:      &sessionID,
		PersistentPath: &persistentPath,
		BrowserOption:  browserOptionMap,
	}

	// Log API request
	fmt.Printf("🔗 API Call: InitBrowser\n")
	fmt.Printf("   Request: SessionId=%s", *request.SessionId)
	if request.PersistentPath != nil {
		fmt.Printf(", PersistentPath=%s\n", *request.PersistentPath)
	}
	if request.BrowserOption != nil {
		fmt.Printf("BrowserOption: %+v\n", request.BrowserOption)
	}

	// Call the client's InitBrowser method
	response, err := b.session.GetClient().InitBrowser(request)
	if err != nil {
		return false, fmt.Errorf("failed to initialize browser: %w", err)
	}

	// Log API response
	fmt.Printf("📥 API Response: InitBrowser\n")
	if response.Body != nil {
		fmt.Printf("Full Response: %+v\n", response.Body)
	}

	// Check the response
	if response == nil || response.Body == nil || response.Body.Data == nil {
		return false, errors.New("browser initialization failed: invalid response")
	}

	// Check if Port is present in the response data
	if response.Body.Data.Port != nil {
		b.initialized = true
		b.option = option
		return true, nil
	}

	return false, errors.New("browser initialization failed: no port in response")
}

// Destroy the browser instance
//
// Example:
//
//	client, _ := agentbay.NewAgentBay(os.Getenv("AGENTBAY_API_KEY"), nil)
//	result, _ := client.Create(nil)
//	defer result.Session.Delete()
//	session.Browser.Initialize(browser.NewBrowserOption())
//	session.Browser.Destroy()
func (b *Browser) Destroy() error {
	if !b.initialized {
		return errors.New("browser is not initialized. Cannot destroy browser")
	}

	// Call the MCP tool to stop Chrome
	_, err := b.session.CallMcpToolForBrowser("stopChrome", map[string]interface{}{})
	if err != nil {
		return fmt.Errorf("failed to destroy browser: %w", err)
	}

	// Reset browser state
	b.initialized = false
	b.option = nil
	b.endpointURL = ""

	return nil
}

// ScreenshotOptions represents options for taking screenshots
type ScreenshotOptions struct {
	FullPage bool
	Type     string // "png" or "jpeg"
	Quality  int    // 0-100 for jpeg
	Timeout  int    // timeout in milliseconds
}

// Screenshot takes a screenshot of the specified page with enhanced options and error handling.
// This method requires the caller to connect to the browser via Playwright or similar
// and pass the page object to this method.
//
// Parameters:
//   - page: The Playwright Page object to take a screenshot of. This is a required parameter.
//   - options: Screenshot options including:
//   - FullPage (bool): Whether to capture the full scrollable page. Defaults to false.
//   - Type (string): Image type, either "png" or "jpeg". Defaults to "png".
//   - Quality (int): Quality of the image, between 0-100 (jpeg only). Defaults to 0.
//   - Timeout (int): Maximum time in milliseconds. Defaults to 60000.
//
// Returns:
//   - []byte: Screenshot data as bytes.
//   - error: Error if browser is not initialized or screenshot capture fails.
//
// Example:
//
//	// Connect to browser using Playwright
//	// pw, _ := playwright.Run()
//	// browser, _ := pw.Chromium.ConnectOverCDP(endpointURL)
//	// page, _ := browser.NewPage()
//	screenshotData, _ := session.Browser.Screenshot(page, nil)
func (b *Browser) Screenshot(page playwright.Page, options *ScreenshotOptions) ([]byte, error) {
	if !b.initialized {
		return nil, errors.New("browser must be initialized before calling screenshot")
	}

	// Create default options if none provided
	if options == nil {
		options = &ScreenshotOptions{
			FullPage: false,
			Type:     "png",
			Quality:  0,
			Timeout:  60000,
		}
	}

	// Set default enhanced options
	enhancedOptions := map[string]interface{}{
		"animations": "disabled",
		"caret":      "hide",
		"scale":      "css",
		"timeout":    options.Timeout,
		"fullPage":   options.FullPage,
		"type":       options.Type,
	}

	// Add quality if type is jpeg
	if options.Type == "jpeg" && options.Quality > 0 {
		enhancedOptions["quality"] = options.Quality
	}

	// Use the actual Playwright page object
	playwrightPage := page

	try := func() ([]byte, error) {
		// Wait for page to load
		// if err := playwrightPage.WaitForLoadState("networkidle"); err != nil {
		// 	return nil, err
		// }

		if _, err := playwrightPage.Evaluate("window.scrollTo(0, document.body.scrollHeight)"); err != nil {
			return nil, err
		}

		if err := playwrightPage.WaitForLoadState(playwright.PageWaitForLoadStateOptions{
			State: playwright.LoadStateDomcontentloaded,
		}); err != nil {
			return nil, err
		}

		// Scroll to load all content (especially for lazy-loaded elements)
		if err := b._scrollToLoadAllContent(playwrightPage, 8, 1200); err != nil {
			return nil, err
		}

		// Ensure images with data-src attributes are loaded
		_, err := playwrightPage.Evaluate(`
			() => {
				document.querySelectorAll('img[data-src]').forEach(img => {
					if (!img.src && img.dataset.src) {
						img.src = img.dataset.src;
					}
				});
				// Also handle background-image[data-bg]
				document.querySelectorAll('[data-bg]').forEach(el => {
					if (!el.style.backgroundImage) {
						el.style.backgroundImage = 'url(' + el.dataset.bg + ')';
					}
				});
			}
		`)
		if err != nil {
			return nil, err
		}

		// Wait a bit for images to load
		playwrightPage.WaitForTimeout(1500)

		finalHeightResult, err := playwrightPage.Evaluate("document.body.scrollHeight")
		if err != nil {
			return nil, err
		}

		finalHeight, ok := finalHeightResult.(int)
		if !ok {
			// Try to convert from float64 if that's what we got
			if floatHeight, ok := finalHeightResult.(float64); ok {
				finalHeight = int(floatHeight)
			} else {
				finalHeight = 10000
			}
		}

		if err := playwrightPage.SetViewportSize(1920, min(finalHeight, 10000)); err != nil {
			return nil, err
		}

		// Take the screenshot
		timeoutFloat := float64(options.Timeout)
		screenshotOptions := playwright.PageScreenshotOptions{
			FullPage: &options.FullPage,
			Timeout:  &timeoutFloat,
		}
		if options.Type == "jpeg" {
			screenshotOptions.Type = playwright.ScreenshotTypeJpeg
			if options.Quality > 0 {
				quality := options.Quality
				screenshotOptions.Quality = &quality
			}
		} else {
			screenshotOptions.Type = playwright.ScreenshotTypePng
		}
		screenshotBytes, err := playwrightPage.Screenshot(screenshotOptions)
		if err != nil {
			return nil, err
		}

		fmt.Println("Screenshot captured successfully.")
		return screenshotBytes, nil
	}

	screenshotBytes, err := try()
	if err != nil {
		// Convert error to string safely to avoid comparison issues
		errorStr := fmt.Sprintf("%v", err)
		errorMsg := fmt.Sprintf("Failed to capture screenshot: %s", errorStr)
		return nil, errors.New(errorMsg)
	}

	return screenshotBytes, nil
}

// _scrollToLoadAllContent scrolls the page to load all content (especially for lazy-loaded elements)
func (b *Browser) _scrollToLoadAllContent(page interface {
	Evaluate(string, ...interface{}) (interface{}, error)
	WaitForTimeout(float64)
}, maxScrolls int, delayMs int) error {
	if maxScrolls <= 0 {
		maxScrolls = 8
	}
	if delayMs <= 0 {
		delayMs = 1200
	}

	lastHeight := 0
	for i := 0; i < maxScrolls; i++ {
		_, err := page.Evaluate("window.scrollTo(0, document.body.scrollHeight)")
		if err != nil {
			return err
		}

		page.WaitForTimeout(float64(delayMs))

		newHeightResult, err := page.Evaluate("Math.max(document.body.scrollHeight, document.documentElement.scrollHeight)")
		if err != nil {
			return err
		}

		newHeight := 0
		if intHeight, ok := newHeightResult.(int); ok {
			newHeight = intHeight
		} else if floatHeight, ok := newHeightResult.(float64); ok {
			newHeight = int(floatHeight)
		}

		if newHeight == lastHeight {
			break
		}
		lastHeight = newHeight
	}
	return nil
}

// Helper function to find minimum of two integers
func min(a, b int) int {
	if a < b {
		return a
	}
	return b
}

// internalWsCallback is the internal WebSocket callback handler
func (b *Browser) internalWsCallback(payload map[string]interface{}) {
	// Basic validation: data field should exist and not be nil
	data, ok := payload["data"]
	if !ok || data == nil {
		return
	}

	// Dispatch to user callback if set
	if b.userCallback != nil {
		dataMap, ok := data.(map[string]interface{})
		if !ok {
			return
		}

		notifyMsg := BrowserNotifyMessageFromMap(dataMap)
		if notifyMsg != nil {
			b.userCallback(notifyMsg)
		}
	}
}

// RegisterCallback registers a callback function to handle browser-related push notifications from sandbox.
//
// The callback function receives a BrowserNotifyMessage object containing notification details
// such as type, code, message, action, and extra_params.
//
// Returns true if the callback was successfully registered.
//
// Example:
//
//	func onBrowserCallback(notifyMsg *browser.BrowserNotifyMessage) {
//	    fmt.Printf("Type: %s\n", *notifyMsg.Type)
//	    fmt.Printf("Code: %d\n", *notifyMsg.Code)
//	    fmt.Printf("Message: %s\n", *notifyMsg.Message)
//	    fmt.Printf("Action: %s\n", *notifyMsg.Action)
//	    fmt.Printf("Extra params: %v\n", notifyMsg.ExtraParams)
//	}
//
//	client, _ := agentbay.NewAgentBay(os.Getenv("AGENTBAY_API_KEY"), nil)
//	result, _ := client.Create(agentbay.NewCreateSessionParams().WithImageId("browser_latest"))
//	defer result.Session.Delete()
//	session := result.Session
//
//	// Initialize browser
//	session.Browser.Initialize(browser.NewBrowserOption())
//
//	// Register callback
//	success, _ := session.Browser.RegisterCallback(onBrowserCallback)
//
//	// ... do work ...
//
//	// Unregister when done
//	session.Browser.UnregisterCallback()
func (b *Browser) RegisterCallback(callback BrowserCallback) (bool, error) {
	// Set user callback (replaces any existing callback)
	b.userCallback = callback

	// Register internal callback to ws_client only once
	if !b.wsCallbackRegistered {
		wsClientInterface, err := b.session.GetWsClient()
		if err != nil {
			return false, fmt.Errorf("failed to get ws_client: %w", err)
		}

		wsClient, ok := wsClientInterface.(*internal.WsClient)
		if !ok {
			return false, fmt.Errorf("ws_client type assertion failed")
		}

		err = wsClient.Connect()
		if err != nil {
			return false, fmt.Errorf("failed to connect ws_client: %w", err)
		}

		wsClient.RegisterCallback("wuying_cdp_mcp_server", b.internalWsCallback)
		b.wsCallbackRegistered = true
	}

	return true, nil
}

// UnregisterCallback unregisters the previously registered callback function.
//
// Example:
//
//	func onBrowserCallback(notifyMsg *browser.BrowserNotifyMessage) {
//	    fmt.Printf("Notification - Type: %s, Message: %s\n", *notifyMsg.Type, *notifyMsg.Message)
//	}
//
//	client, _ := agentbay.NewAgentBay(os.Getenv("AGENTBAY_API_KEY"), nil)
//	result, _ := client.Create(agentbay.NewCreateSessionParams().WithImageId("browser_latest"))
//	defer result.Session.Delete()
//	session := result.Session
//
//	session.Browser.Initialize(browser.NewBrowserOption())
//
//	session.Browser.RegisterCallback(onBrowserCallback)
//
//	// ... do work ...
//
//	// Unregister callback
//	session.Browser.UnregisterCallback()
func (b *Browser) UnregisterCallback() error {
	// Clear user callback
	b.userCallback = nil

	// Unregister from ws_client
	if b.wsCallbackRegistered {
		wsClientInterface, err := b.session.GetWsClient()
		if err != nil {
			return fmt.Errorf("failed to get ws_client: %w", err)
		}

		wsClient, ok := wsClientInterface.(*internal.WsClient)
		if !ok {
			return fmt.Errorf("ws_client type assertion failed")
		}

		wsClient.UnregisterCallback("wuying_cdp_mcp_server")
		err = wsClient.Close()
		if err != nil {
			return fmt.Errorf("failed to close ws_client: %w", err)
		}

		b.wsCallbackRegistered = false
	}

	return nil
}

// SendNotifyMessage sends a BrowserNotifyMessage to sandbox.
//
// Returns true if the notify message was successfully sent, false otherwise.
//
// Example:
//
//	func onBrowserCallback(notifyMsg *browser.BrowserNotifyMessage) {
//	    fmt.Printf("Type: %s\n", *notifyMsg.Type)
//	    fmt.Printf("Code: %d\n", *notifyMsg.Code)
//	    fmt.Printf("Message: %s\n", *notifyMsg.Message)
//	    fmt.Printf("Action: %s\n", *notifyMsg.Action)
//	    fmt.Printf("Extra params: %v\n", notifyMsg.ExtraParams)
//	}
//
//	client, _ := agentbay.NewAgentBay(os.Getenv("AGENTBAY_API_KEY"), nil)
//	result, _ := client.Create(agentbay.NewCreateSessionParams().WithImageId("browser_latest"))
//	defer result.Session.Delete()
//	session := result.Session
//
//	// Initialize browser
//	session.Browser.Initialize(browser.NewBrowserOption())
//
//	// Register callback
//	session.Browser.RegisterCallback(onBrowserCallback)
//
//	// ... do work ...
//
//	// Send notify message
//	msgType := "call-for-user"
//	id := 3
//	code := 199
//	message := "user handle done"
//	action := "takeoverdone"
//	notifyMessage := browser.NewBrowserNotifyMessage(&msgType, &id, &code, &message, &action, map[string]interface{}{})
//	session.Browser.SendNotifyMessage(notifyMessage)
//
//	// Unregister when done
//	session.Browser.UnregisterCallback()
func (b *Browser) SendNotifyMessage(notifyMessage *BrowserNotifyMessage) (bool, error) {
	wsClientInterface, err := b.session.GetWsClient()
	if err != nil {
		return false, fmt.Errorf("failed to get ws_client: %w", err)
	}

	wsClient, ok := wsClientInterface.(*internal.WsClient)
	if !ok {
		return false, fmt.Errorf("ws_client type assertion failed")
	}

	// Send notify message through ws_client
	err = wsClient.SendMessage("wuying_cdp_mcp_server", notifyMessage.ToMap())
	if err != nil {
		return false, fmt.Errorf("failed to send notify message: %w", err)
	}

	return true, nil
}

// SendTakeoverDone sends a takeoverdone notify message to sandbox.
//
// The notifyId parameter is the notification ID associated with the takeover request message.
//
// Returns true if the takeoverdone notify message was successfully sent, false otherwise.
//
// Example:
//
//	func onBrowserCallback(notifyMsg *browser.BrowserNotifyMessage) {
//	    // receive call-for-user "takeover" action
//	    if notifyMsg.Action != nil && *notifyMsg.Action == "takeover" {
//	        takeoverNotifyId := *notifyMsg.ID
//
//	        // ... do work in other thread...
//	        // send takeoverdone notify message
//	        session.Browser.SendTakeoverDone(takeoverNotifyId)
//	        // ... end...
//	    }
//	}
//
//	client, _ := agentbay.NewAgentBay(os.Getenv("AGENTBAY_API_KEY"), nil)
//	result, _ := client.Create(agentbay.NewCreateSessionParams().WithImageId("browser_latest"))
//	defer result.Session.Delete()
//	session := result.Session
//
//	// Initialize browser
//	session.Browser.Initialize(browser.NewBrowserOption())
//
//	// Register callback
//	session.Browser.RegisterCallback(onBrowserCallback)
//
//	// ... do work ...
//
//	// Unregister when done
//	session.Browser.UnregisterCallback()
func (b *Browser) SendTakeoverDone(notifyId int) (bool, error) {
	// Get ws_client
	wsClientInterface, err := b.session.GetWsClient()
	if err != nil {
		return false, fmt.Errorf("failed to get ws_client: %w", err)
	}

	wsClient, ok := wsClientInterface.(*internal.WsClient)
	if !ok {
		return false, fmt.Errorf("ws_client type assertion failed")
	}

	// Build takeoverdone notify message
	msgType := "call-for-user"
	code := 199
	message := "user handle done"
	action := "takeoverdone"
	notifyMessage := NewBrowserNotifyMessage(&msgType, &notifyId, &code, &message, &action, map[string]interface{}{})
	messageData := notifyMessage.ToMap()

	// Send message through ws_client
	err = wsClient.SendMessage("wuying_cdp_mcp_server", messageData)
	if err != nil {
		return false, fmt.Errorf("failed to send browser notify message: %w", err)
	}

	return true, nil
}
