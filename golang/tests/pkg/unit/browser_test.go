package unit

import (
	"testing"

	"github.com/aliyun/wuying-agentbay-sdk/golang/pkg/agentbay/browser"
	"github.com/stretchr/testify/assert"
	"github.com/stretchr/testify/require"
)

func TestBrowserOption_NewBrowserOption(t *testing.T) {
	option := browser.NewBrowserOption()

	assert.NotNil(t, option)
	assert.False(t, option.UseStealth)
	assert.False(t, option.SolveCaptchas)
	assert.Equal(t, "chromium", option.BrowserType) // Default should be chromium
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
				BrowserType: "chromium",
			},
			expectErr: false,
		},
		{
			name: "valid chrome browser type",
			option: &browser.BrowserOption{
				BrowserType: "chrome",
			},
			expectErr: false,
		},
		{
			name: "invalid browser type",
			option: &browser.BrowserOption{
				BrowserType: "firefox",
			},
			expectErr: true,
			errMsg:    "browserType must be 'chrome' or 'chromium'",
		},
		{
			name: "multiple proxies",
			option: &browser.BrowserOption{
				BrowserType: "chromium",
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
				BrowserType:   "chromium",
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

func TestBrowserOption_ToMap(t *testing.T) {
	t.Run("default options", func(t *testing.T) {
		option := browser.NewBrowserOption()
		optionMap := option.ToMap()

		assert.NotNil(t, optionMap)
		assert.Equal(t, false, optionMap["useStealth"])
		assert.Equal(t, false, optionMap["solveCaptchas"])
		assert.Equal(t, "chromium", optionMap["browserType"])
		assert.Equal(t, "/tmp/extensions/", optionMap["extensionPath"])
	})

	t.Run("custom browser type", func(t *testing.T) {
		option := browser.NewBrowserOption()
		option.BrowserType = "chrome"
		optionMap := option.ToMap()

		assert.Equal(t, "chrome", optionMap["browserType"])
	})

	t.Run("with user agent", func(t *testing.T) {
		ua := "Mozilla/5.0 Test"
		option := &browser.BrowserOption{
			BrowserType: "chromium",
			UserAgent:   &ua,
		}
		optionMap := option.ToMap()

		assert.Equal(t, ua, optionMap["userAgent"])
	})

	t.Run("with viewport", func(t *testing.T) {
		option := &browser.BrowserOption{
			BrowserType: "chromium",
			Viewport: &browser.BrowserViewport{
				Width:  1920,
				Height: 1080,
			},
		}
		optionMap := option.ToMap()

		viewport, ok := optionMap["viewport"].(map[string]interface{})
		assert.True(t, ok)
		assert.Equal(t, 1920, viewport["width"])
		assert.Equal(t, 1080, viewport["height"])
	})

	t.Run("with screen", func(t *testing.T) {
		option := &browser.BrowserOption{
			BrowserType: "chromium",
			Screen: &browser.BrowserScreen{
				Width:  1920,
				Height: 1080,
			},
		}
		optionMap := option.ToMap()

		screen, ok := optionMap["screen"].(map[string]interface{})
		assert.True(t, ok)
		assert.Equal(t, 1920, screen["width"])
		assert.Equal(t, 1080, screen["height"])
	})
}

func TestBrowserProxy_NewBrowserProxy(t *testing.T) {
	tests := []struct {
		name      string
		proxyType string
		server    *string
		username  *string
		password  *string
		strategy  *string
		pollSize  *int
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
			name:      "invalid proxy type",
			proxyType: "invalid",
			expectErr: true,
			errMsg:    "proxy_type must be custom or wuying",
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

func (m *mockSessionForBrowser) CallMcpTool(toolName string, args interface{}) (interface{}, error) {
	return nil, nil
}

func (m *mockSessionForBrowser) GetLink(protocolType *string, port *int32) (interface{}, error) {
	return nil, nil
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

