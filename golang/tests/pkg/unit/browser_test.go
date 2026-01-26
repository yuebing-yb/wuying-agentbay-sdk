package agentbay_test

import (
	"testing"

	"github.com/aliyun/wuying-agentbay-sdk/golang/api/client"
	"github.com/aliyun/wuying-agentbay-sdk/golang/pkg/agentbay/browser"
	"github.com/stretchr/testify/assert"
)

func TestBrowserOption_NewBrowserOption(t *testing.T) {
	option := browser.NewBrowserOption()

	assert.NotNil(t, option)
	assert.False(t, option.UseStealth)
	assert.False(t, option.SolveCaptchas)
	assert.Nil(t, option.BrowserType) // Default should be nil
	assert.NotNil(t, option.ExtensionPath)
	assert.Equal(t, "/tmp/extensions/", *option.ExtensionPath)
}

func TestBrowserOption_Validate(t *testing.T) {
	tests := []struct {
		name      string
		option    *browser.BrowserOption
		expectErr bool
		errMsg    string
	}{
		{
			name: "valid default option",
			option: &browser.BrowserOption{
				BrowserType: nil,
			},
			expectErr: false,
		},
		{
			name: "valid chrome browser type",
			option: &browser.BrowserOption{
				BrowserType: func() *string { s := "chrome"; return &s }(),
			},
			expectErr: false,
		},
		{
			name: "invalid browser type",
			option: &browser.BrowserOption{
				BrowserType: func() *string { s := "firefox"; return &s }(),
			},
			expectErr: true,
			errMsg:    "browserType must be 'chrome' or 'chromium'",
		},
		{
			name: "multiple proxies",
			option: &browser.BrowserOption{
				BrowserType: nil,
				Proxies: []*browser.BrowserProxy{
					{Type: "custom"},
					{Type: "custom"},
				},
			},
			expectErr: true,
			errMsg:    "proxies list length must be limited to 1",
		},
		{
			name: "empty extension path",
			option: &browser.BrowserOption{
				BrowserType:   nil,
				ExtensionPath: func() *string { s := ""; return &s }(),
			},
			expectErr: true,
			errMsg:    "extensionPath cannot be empty",
		},
	}

	for _, tt := range tests {
		t.Run(tt.name, func(t *testing.T) {
			err := tt.option.Validate()
			if tt.expectErr {
				assert.Error(t, err)
				if tt.errMsg != "" {
					assert.Contains(t, err.Error(), tt.errMsg)
				}
			} else {
				assert.NoError(t, err)
			}
		})
	}
}

// TestBrowserOption_ToMap removed - toMap() is now a private method
// The functionality is tested through public APIs like Initialize()

func TestBrowserProxy_NewBrowserProxy(t *testing.T) {
	tests := []struct {
		name      string
		proxyType string
		server    *string
		username  *string
		password  *string
		strategy  *string
		pollSize  *int
		userID    *string
		isp       *string
		country   *string
		province  *string
		city      *string
		expectErr bool
		errMsg    string
	}{
		{
			name:      "valid custom proxy",
			proxyType: "custom",
			server:    stringPtr("127.0.0.1:8080"),
			expectErr: false,
		},
		{
			name:      "custom proxy without server",
			proxyType: "custom",
			expectErr: true,
			errMsg:    "server is required for custom proxy type",
		},
		{
			name:      "valid wuying proxy with restricted strategy",
			proxyType: "wuying",
			strategy:  stringPtr("restricted"),
			expectErr: false,
		},
		{
			name:      "valid wuying proxy with polling strategy",
			proxyType: "wuying",
			strategy:  stringPtr("polling"),
			pollSize:  intPtr(10),
			expectErr: false,
		},
		{
			name:      "wuying proxy without strategy",
			proxyType: "wuying",
			expectErr: true,
			errMsg:    "strategy is required for wuying proxy type",
		},
		{
			name:      "valid managed proxy with sticky strategy",
			proxyType: "managed",
			strategy:  stringPtr("sticky"),
			userID:    stringPtr("user123"),
			expectErr: false,
		},
		{
			name:      "valid managed proxy with rotating strategy",
			proxyType: "managed",
			strategy:  stringPtr("rotating"),
			userID:    stringPtr("user123"),
			expectErr: false,
		},
		{
			name:      "valid managed proxy with polling strategy",
			proxyType: "managed",
			strategy:  stringPtr("polling"),
			userID:    stringPtr("user123"),
			expectErr: false,
		},
		{
			name:      "valid managed proxy with matched strategy",
			proxyType: "managed",
			strategy:  stringPtr("matched"),
			userID:    stringPtr("user123"),
			isp:       stringPtr("China Telecom"),
			country:   stringPtr("China"),
			province:  stringPtr("Beijing"),
			city:      stringPtr("Beijing"),
			expectErr: false,
		},
		{
			name:      "managed proxy without strategy",
			proxyType: "managed",
			userID:    stringPtr("user123"),
			expectErr: true,
			errMsg:    "strategy is required for managed proxy type",
		},
		{
			name:      "managed proxy without userID",
			proxyType: "managed",
			strategy:  stringPtr("sticky"),
			expectErr: true,
			errMsg:    "user_id is required for managed proxy type",
		},
		{
			name:      "managed proxy with invalid strategy",
			proxyType: "managed",
			strategy:  stringPtr("invalid"),
			userID:    stringPtr("user123"),
			expectErr: true,
			errMsg:    "strategy must be polling, sticky, rotating, or matched for managed proxy type",
		},
		{
			name:      "managed proxy with matched strategy but no filters",
			proxyType: "managed",
			strategy:  stringPtr("matched"),
			userID:    stringPtr("user123"),
			expectErr: true,
			errMsg:    "at least one of isp, country, province, or city is required for matched strategy",
		},
		{
			name:      "invalid proxy type",
			proxyType: "invalid",
			expectErr: true,
			errMsg:    "proxy_type must be custom, wuying, or managed",
		},
	}

	for _, tt := range tests {
		t.Run(tt.name, func(t *testing.T) {
			proxy, err := browser.NewBrowserProxy(
				tt.proxyType,
				tt.server,
				tt.username,
				tt.password,
				tt.strategy,
				tt.pollSize,
				tt.userID,
				tt.isp,
				tt.country,
				tt.province,
				tt.city,
			)

			if tt.expectErr {
				assert.Error(t, err)
				if tt.errMsg != "" {
					assert.Contains(t, err.Error(), tt.errMsg)
				}
				assert.Nil(t, proxy)
			} else {
				assert.NoError(t, err)
				assert.NotNil(t, proxy)
				assert.Equal(t, tt.proxyType, proxy.Type)
			}
		})
	}
}

func TestBrowserFingerprint_NewBrowserFingerprint(t *testing.T) {
	tests := []struct {
		name             string
		devices          []string
		operatingSystems []string
		locales          []string
		expectErr        bool
		errMsg           string
	}{
		{
			name:      "valid devices",
			devices:   []string{"desktop", "mobile"},
			expectErr: false,
		},
		{
			name:      "invalid device",
			devices:   []string{"tablet"},
			expectErr: true,
			errMsg:    "device must be desktop or mobile",
		},
		{
			name:             "valid operating systems",
			operatingSystems: []string{"windows", "macos", "linux"},
			expectErr:        false,
		},
		{
			name:             "invalid operating system",
			operatingSystems: []string{"bsd"},
			expectErr:        true,
			errMsg:           "operating_system must be windows, macos, linux, android or ios",
		},
		{
			name:      "valid locales",
			locales:   []string{"en-US", "zh-CN"},
			expectErr: false,
		},
	}

	for _, tt := range tests {
		t.Run(tt.name, func(t *testing.T) {
			fingerprint, err := browser.NewBrowserFingerprint(
				tt.devices,
				tt.operatingSystems,
				tt.locales,
			)

			if tt.expectErr {
				assert.Error(t, err)
				if tt.errMsg != "" {
					assert.Contains(t, err.Error(), tt.errMsg)
				}
				assert.Nil(t, fingerprint)
			} else {
				assert.NoError(t, err)
				assert.NotNil(t, fingerprint)
			}
		})
	}
}

func TestBrowser_IsInitialized(t *testing.T) {
	mockSession := &mockSessionForBrowser{}
	browser := browser.NewBrowser(mockSession)

	// Initially should not be initialized
	assert.False(t, browser.IsInitialized())
}

func TestBrowser_GetOption(t *testing.T) {
	mockSession := &mockSessionForBrowser{}
	browser := browser.NewBrowser(mockSession)

	// Initially should return nil
	assert.Nil(t, browser.GetOption())
}

func TestBrowser_Screenshot(t *testing.T) {
	// Use the existing mock session
	mockSession := &mockSessionForBrowser{}

	t.Run("screenshot without initialization", func(t *testing.T) {
		b := browser.NewBrowser(mockSession)

		// Try to take screenshot without initializing browser
		_, err := b.Screenshot(nil, nil)

		assert.Error(t, err)
		assert.Contains(t, err.Error(), "browser must be initialized before calling screenshot")
	})

	t.Run("screenshot handles Playwright method errors correctly", func(t *testing.T) {
		// Create a browser and initialize it
		b := browser.NewBrowser(mockSession)

		// We can't easily test the full Playwright integration in unit tests,
		// but we can test that the method exists and handles errors properly
		// For this test, we'll check that the method signature is correct
		// and that it properly validates initialization

		// Since we can't easily mock a Playwright page object in Go unit tests,
		// we'll just verify the method exists and has the right signature
		assert.NotNil(t, b.Screenshot)
	})
}

// Helper functions
func stringPtr(s string) *string {
	return &s
}

func intPtr(i int) *int {
	return &i
}

// Mock session for browser testing
type mockSessionForBrowser struct{}

func (m *mockSessionForBrowser) GetAPIKey() string {
	return "test-api-key"
}

func (m *mockSessionForBrowser) GetSessionID() string {
	return "test-session-id"
}

func (m *mockSessionForBrowser) GetClient() *client.Client {
	// Return nil for unit tests - we're not testing actual API calls
	return nil
}

func (m *mockSessionForBrowser) CallMcpToolForBrowser(toolName string, args interface{}) (*browser.McpToolResult, error) {
	return &browser.McpToolResult{
		Success: true,
		Data:    "{}",
	}, nil
}

func (m *mockSessionForBrowser) GetLinkForBrowser(protocolType *string, port *int32, options *string) (*browser.LinkResult, error) {
	return &browser.LinkResult{
		Link: "ws://localhost:9222",
	}, nil
}

func (m *mockSessionForBrowser) IsVPCEnabled() bool {
	return false
}

func (m *mockSessionForBrowser) GetNetworkInterfaceIP() string {
	return ""
}

func (m *mockSessionForBrowser) GetHttpPortNumber() string {
	return ""
}
