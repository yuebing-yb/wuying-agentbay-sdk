package browser

import (
	"encoding/json"
	"errors"
	"fmt"
	"os"
)

// BrowserProxy represents browser proxy configuration.
// Supports two types of proxy: custom proxy and wuying proxy.
// Wuying proxy supports two strategies: restricted and polling.
type BrowserProxy struct {
	Type     string  `json:"type"`               // Type of proxy - "custom" or "wuying"
	Server   *string `json:"server,omitempty"`   // Proxy server address (required for custom type)
	Username *string `json:"username,omitempty"` // Proxy username (optional for custom type)
	Password *string `json:"password,omitempty"` // Proxy password (optional for custom type)
	Strategy *string `json:"strategy,omitempty"` // Strategy for wuying: "restricted" or "polling"
	PollSize *int    `json:"pollsize,omitempty"` // Pool size (optional for wuying with polling strategy)
}

// NewBrowserProxy creates a new BrowserProxy with validation
func NewBrowserProxy(proxyType string, server, username, password, strategy *string, pollSize *int) (*BrowserProxy, error) {
	proxy := &BrowserProxy{
		Type:     proxyType,
		Server:   server,
		Username: username,
		Password: password,
		Strategy: strategy,
		PollSize: pollSize,
	}

	// Validation
	if proxyType != "custom" && proxyType != "wuying" {
		return nil, errors.New("proxy_type must be custom or wuying")
	}

	if proxyType == "custom" && (server == nil || *server == "") {
		return nil, errors.New("server is required for custom proxy type")
	}

	if proxyType == "wuying" && (strategy == nil || *strategy == "") {
		return nil, errors.New("strategy is required for wuying proxy type")
	}

	if proxyType == "wuying" && strategy != nil && *strategy != "restricted" && *strategy != "polling" {
		return nil, errors.New("strategy must be restricted or polling for wuying proxy type")
	}

	if proxyType == "wuying" && strategy != nil && *strategy == "polling" && pollSize != nil && *pollSize <= 0 {
		return nil, errors.New("pollsize must be greater than 0 for polling strategy")
	}

	return proxy, nil
}

// ToMap converts BrowserProxy to map for API request
func (p *BrowserProxy) ToMap() map[string]interface{} {
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
	}

	return proxyMap
}

// BrowserViewport represents browser viewport options
type BrowserViewport struct {
	Width  int `json:"width"`  // Viewport width
	Height int `json:"height"` // Viewport height
}

// ToMap converts BrowserViewport to map for API request
func (v *BrowserViewport) ToMap() map[string]interface{} {
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

// ToMap converts BrowserScreen to map for API request
func (s *BrowserScreen) ToMap() map[string]interface{} {
	return map[string]interface{}{
		"width":  s.Width,
		"height": s.Height,
	}
}

// BrowserFingerprint represents browser fingerprint options
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

// ToMap converts BrowserFingerprint to map for API request
func (f *BrowserFingerprint) ToMap() map[string]interface{} {
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
type BrowserOption struct {
	UseStealth    bool                `json:"useStealth,omitempty"`    // Enable stealth mode
	UserAgent     *string             `json:"userAgent,omitempty"`     // Custom user agent
	Viewport      *BrowserViewport    `json:"viewport,omitempty"`      // Viewport configuration
	Screen        *BrowserScreen      `json:"screen,omitempty"`        // Screen configuration
	Fingerprint   *BrowserFingerprint `json:"fingerprint,omitempty"`   // Fingerprint configuration
	SolveCaptchas bool                `json:"solveCaptchas,omitempty"` // Auto-solve captchas
	Proxies       []*BrowserProxy     `json:"proxies,omitempty"`       // Proxy configurations
	ExtensionPath *string             `json:"extensionPath,omitempty"` // Path to extensions directory
	BrowserType   string              `json:"browserType,omitempty"`   // Browser type: "chrome" or "chromium"
}

// NewBrowserOption creates a new BrowserOption with default values and validation
func NewBrowserOption() *BrowserOption {
	defaultExtPath := "/tmp/extensions/"
	return &BrowserOption{
		UseStealth:    false,
		SolveCaptchas: false,
		ExtensionPath: &defaultExtPath,
		BrowserType:   "chromium", // Default to chromium
	}
}

// Validate validates the BrowserOption
func (o *BrowserOption) Validate() error {
	// Validate proxies
	if o.Proxies != nil && len(o.Proxies) > 1 {
		return errors.New("proxies list length must be limited to 1")
	}

	// Validate extension path
	if o.ExtensionPath != nil && *o.ExtensionPath == "" {
		return errors.New("extensionPath cannot be empty")
	}

	// Validate browser type
	if o.BrowserType != "" && o.BrowserType != "chrome" && o.BrowserType != "chromium" {
		return errors.New("browserType must be 'chrome' or 'chromium'")
	}

	return nil
}

// ToMap converts BrowserOption to map for API request
func (o *BrowserOption) ToMap() map[string]interface{} {
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
		optionMap["viewport"] = o.Viewport.ToMap()
	}

	if o.Screen != nil {
		optionMap["screen"] = o.Screen.ToMap()
	}

	if o.Fingerprint != nil {
		optionMap["fingerprint"] = o.Fingerprint.ToMap()
	}

	optionMap["solveCaptchas"] = o.SolveCaptchas

	if o.Proxies != nil && len(o.Proxies) > 0 {
		proxies := make([]map[string]interface{}, len(o.Proxies))
		for i, proxy := range o.Proxies {
			proxies[i] = proxy.ToMap()
		}
		optionMap["proxies"] = proxies
	}

	if o.ExtensionPath != nil {
		optionMap["extensionPath"] = *o.ExtensionPath
	}

	if o.BrowserType != "" {
		optionMap["browserType"] = o.BrowserType
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
	CallMcpToolForBrowser(toolName string, args interface{}) (*McpToolResult, error)
	GetLinkForBrowser(protocolType *string, port *int32, options *string) (*LinkResult, error)
	IsVPCEnabled() bool
	GetNetworkInterfaceIP() string
	GetHttpPortNumber() string
}

// Browser provides browser-related operations for the session
type Browser struct {
	session     SessionInterface
	endpointURL string
	initialized bool
	option      *BrowserOption
}

// NewBrowser creates a new Browser instance
func NewBrowser(session SessionInterface) *Browser {
	return &Browser{
		session:     session,
		initialized: false,
	}
}

// IsInitialized returns true if the browser was initialized, false otherwise
func (b *Browser) IsInitialized() bool {
	return b.initialized
}

// GetOption returns the current BrowserOption used to initialize the browser, or nil if not set
func (b *Browser) GetOption() *BrowserOption {
	return b.option
}

// GetEndpointURL returns the endpoint URL if the browser is initialized
func (b *Browser) GetEndpointURL() (string, error) {
	if !b.initialized {
		return "", errors.New("browser is not initialized. Cannot access endpoint URL")
	}

	if b.session.IsVPCEnabled() {
		// For VPC mode, construct endpoint URL from VPC IP and port
		b.endpointURL = fmt.Sprintf("ws://%s:%s", b.session.GetNetworkInterfaceIP(), b.session.GetHttpPortNumber())
		return b.endpointURL, nil
	}

	// For non-VPC mode, fetch the CDP URL
	result, err := b.session.GetLinkForBrowser(nil, nil, nil)
	if err != nil {
		return "", fmt.Errorf("failed to get endpoint URL from session: %w", err)
	}
	
	// Extract the Link from the result
	b.endpointURL = result.Link
	return b.endpointURL, nil
}

// Initialize initializes the browser instance with the given options.
// Returns true and nil error if successful, false and error otherwise.
func (b *Browser) Initialize(option *BrowserOption) (bool, error) {
	if b.initialized {
		return true, nil
	}

	// Validate the option
	if err := option.Validate(); err != nil {
		return false, fmt.Errorf("invalid browser option: %w", err)
	}

	// Convert option to map
	browserOptionMap := option.ToMap()

	// Build the request args
	requestArgs := map[string]interface{}{
		"Authorization":  "Bearer " + b.session.GetAPIKey(),
		"SessionId":      b.session.GetSessionID(),
		"PersistentPath": "/tmp/browser_data",
		"BrowserOption":  browserOptionMap,
	}

	// Call the MCP tool to initialize browser
	result, err := b.session.CallMcpToolForBrowser("initBrowser", requestArgs)
	if err != nil {
		return false, fmt.Errorf("failed to initialize browser: %w", err)
	}

	// Check if the MCP tool call was successful
	if !result.Success {
		return false, fmt.Errorf("browser initialization failed: %s", result.ErrorMessage)
	}

	// Parse the Data field (which is a JSON string) to check for Port
	if result.Data != "" {
		var data map[string]interface{}
		if err := json.Unmarshal([]byte(result.Data), &data); err == nil {
			if _, hasPort := data["Port"]; hasPort {
				b.initialized = true
				b.option = option
				return true, nil
			}
		}
	}

	return false, errors.New("browser initialization failed: no port in response")
}
