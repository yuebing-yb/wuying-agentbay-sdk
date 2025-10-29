package integration

import (
	"os"
	"testing"

	"github.com/aliyun/wuying-agentbay-sdk/golang/pkg/agentbay"
	"github.com/aliyun/wuying-agentbay-sdk/golang/pkg/agentbay/browser"
	"github.com/stretchr/testify/assert"
	"github.com/stretchr/testify/require"
)

func TestBrowser_Initialize_Integration(t *testing.T) {
	// Skip if no API key
	apiKey := os.Getenv("AGENTBAY_API_KEY")
	if apiKey == "" {
		t.Skip("Skipping integration test: AGENTBAY_API_KEY not set")
	}

	// Create AgentBay client
	agentBay, err := agentbay.NewAgentBay(apiKey)
	require.NoError(t, err)
	require.NotNil(t, agentBay)

	// Create session with browser image
	params := &agentbay.CreateSessionParams{
		ImageId: "browser_latest",
	}

	sessionResult, err := agentBay.Create(params)
	require.NoError(t, err)
	require.NotNil(t, sessionResult)
	require.True(t, sessionResult.Success)
	require.NotNil(t, sessionResult.Session)

	session := sessionResult.Session
	defer func() {
		// Clean up session
		_, err := agentBay.Delete(session, false)
		if err != nil {
			t.Logf("Warning: Failed to delete session: %v", err)
		}
	}()

	t.Run("Initialize with default options", func(t *testing.T) {
		option := browser.NewBrowserOption()
		success, err := session.Browser.Initialize(option)

		assert.NoError(t, err)
		assert.True(t, success)
		assert.True(t, session.Browser.IsInitialized())

		// Verify option was saved
		savedOption := session.Browser.GetOption()
		assert.NotNil(t, savedOption)
		assert.Equal(t, "chromium", savedOption.BrowserType)
	})

	t.Run("Get endpoint URL after initialization", func(t *testing.T) {
		endpointURL, err := session.Browser.GetEndpointURL()

		assert.NoError(t, err)
		assert.NotEmpty(t, endpointURL)
		t.Logf("Browser endpoint URL: %s", endpointURL)
	})
}

func TestBrowser_InitializeWithChrome_Integration(t *testing.T) {
	// Skip if no API key
	apiKey := os.Getenv("AGENTBAY_API_KEY")
	if apiKey == "" {
		t.Skip("Skipping integration test: AGENTBAY_API_KEY not set")
	}

	// Create AgentBay client
	agentBay, err := agentbay.NewAgentBay(apiKey)
	require.NoError(t, err)
	require.NotNil(t, agentBay)

	// Create session with computer use image (required for chrome/chromium selection)
	params := &agentbay.CreateSessionParams{
		ImageId: "linux_latest",
	}

	sessionResult, err := agentBay.Create(params)
	require.NoError(t, err)
	require.NotNil(t, sessionResult)
	require.True(t, sessionResult.Success)
	require.NotNil(t, sessionResult.Session)

	session := sessionResult.Session
	defer func() {
		// Clean up session
		_, err := agentBay.Delete(session, false)
		if err != nil {
			t.Logf("Warning: Failed to delete session: %v", err)
		}
	}()

	t.Run("Initialize with Chrome browser type", func(t *testing.T) {
		option := browser.NewBrowserOption()
		browserType := "chrome"
		option.BrowserType = &browserType

		success, err := session.Browser.Initialize(option)

		assert.NoError(t, err)
		assert.True(t, success)
		assert.True(t, session.Browser.IsInitialized())

		// Verify Chrome was selected
		savedOption := session.Browser.GetOption()
		assert.NotNil(t, savedOption)
		assert.Equal(t, "chrome", savedOption.BrowserType)
	})
}

func TestBrowser_InitializeWithCustomOptions_Integration(t *testing.T) {
	// Skip if no API key
	apiKey := os.Getenv("AGENTBAY_API_KEY")
	if apiKey == "" {
		t.Skip("Skipping integration test: AGENTBAY_API_KEY not set")
	}

	// Create AgentBay client
	agentBay, err := agentbay.NewAgentBay(apiKey)
	require.NoError(t, err)
	require.NotNil(t, agentBay)

	// Create session with browser image
	params := &agentbay.CreateSessionParams{
		ImageId: "browser_latest",
	}

	sessionResult, err := agentBay.Create(params)
	require.NoError(t, err)
	require.NotNil(t, sessionResult)
	require.True(t, sessionResult.Success)
	require.NotNil(t, sessionResult.Session)

	session := sessionResult.Session
	defer func() {
		// Clean up session
		_, err := agentBay.Delete(session, false)
		if err != nil {
			t.Logf("Warning: Failed to delete session: %v", err)
		}
	}()

	t.Run("Initialize with custom viewport and user agent", func(t *testing.T) {
		userAgent := "Mozilla/5.0 (Test) AppleWebKit/537.36"
		browserType := "chromium"
		option := &browser.BrowserOption{
			BrowserType: &browserType,
			UserAgent:   &userAgent,
			Viewport: &browser.BrowserViewport{
				Width:  1366,
				Height: 768,
			},
			Screen: &browser.BrowserScreen{
				Width:  1366,
				Height: 768,
			},
		}

		success, err := session.Browser.Initialize(option)

		assert.NoError(t, err)
		assert.True(t, success)
		assert.True(t, session.Browser.IsInitialized())

		// Verify options were saved
		savedOption := session.Browser.GetOption()
		assert.NotNil(t, savedOption)
		assert.Equal(t, userAgent, *savedOption.UserAgent)
		assert.Equal(t, 1366, savedOption.Viewport.Width)
		assert.Equal(t, 768, savedOption.Viewport.Height)
	})
}

func TestBrowser_InitializeAlreadyInitialized_Integration(t *testing.T) {
	// Skip if no API key
	apiKey := os.Getenv("AGENTBAY_API_KEY")
	if apiKey == "" {
		t.Skip("Skipping integration test: AGENTBAY_API_KEY not set")
	}

	// Create AgentBay client
	agentBay, err := agentbay.NewAgentBay(apiKey)
	require.NoError(t, err)
	require.NotNil(t, agentBay)

	// Create session with browser image
	params := &agentbay.CreateSessionParams{
		ImageId: "browser_latest",
	}

	sessionResult, err := agentBay.Create(params)
	require.NoError(t, err)
	require.NotNil(t, sessionResult)
	require.True(t, sessionResult.Success)
	require.NotNil(t, sessionResult.Session)

	session := sessionResult.Session
	defer func() {
		// Clean up session
		_, err := agentBay.Delete(session, false)
		if err != nil {
			t.Logf("Warning: Failed to delete session: %v", err)
		}
	}()

	// Initialize browser first time
	option1 := browser.NewBrowserOption()
	success1, err1 := session.Browser.Initialize(option1)
	require.NoError(t, err1)
	require.True(t, success1)

	// Try to initialize again
	option2 := browser.NewBrowserOption()
	browserType2 := "chrome"
	option2.BrowserType = &browserType2
	success2, err2 := session.Browser.Initialize(option2)

	// Should return true without error (already initialized)
	assert.NoError(t, err2)
	assert.True(t, success2)

	// Should still have the original option
	savedOption := session.Browser.GetOption()
	assert.NotNil(t, savedOption)
	assert.Equal(t, "chromium", savedOption.BrowserType) // Original value
}

func TestBrowser_GetEndpointURLBeforeInitialization_Integration(t *testing.T) {
	// Skip if no API key
	apiKey := os.Getenv("AGENTBAY_API_KEY")
	if apiKey == "" {
		t.Skip("Skipping integration test: AGENTBAY_API_KEY not set")
	}

	// Create AgentBay client
	agentBay, err := agentbay.NewAgentBay(apiKey)
	require.NoError(t, err)
	require.NotNil(t, agentBay)

	// Create session with browser image
	params := &agentbay.CreateSessionParams{
		ImageId: "browser_latest",
	}

	sessionResult, err := agentBay.Create(params)
	require.NoError(t, err)
	require.NotNil(t, sessionResult)
	require.True(t, sessionResult.Success)
	require.NotNil(t, sessionResult.Session)

	session := sessionResult.Session
	defer func() {
		// Clean up session
		_, err := agentBay.Delete(session, false)
		if err != nil {
			t.Logf("Warning: Failed to delete session: %v", err)
		}
	}()

	// Try to get endpoint URL before initialization
	endpointURL, err := session.Browser.GetEndpointURL()

	// Should return error
	assert.Error(t, err)
	assert.Empty(t, endpointURL)
	assert.Contains(t, err.Error(), "browser is not initialized")
}

func TestBrowser_VPCMode_Integration(t *testing.T) {
	// Skip if no API key or VPC not configured
	apiKey := os.Getenv("AGENTBAY_API_KEY")
	if apiKey == "" {
		t.Skip("Skipping integration test: AGENTBAY_API_KEY not set")
	}

	// This test requires VPC setup - skip if not available
	vpcEnabled := os.Getenv("AGENTBAY_VPC_ENABLED")
	if vpcEnabled != "true" {
		t.Skip("Skipping VPC test: AGENTBAY_VPC_ENABLED not set to true")
	}

	// Create AgentBay client
	agentBay, err := agentbay.NewAgentBay(apiKey)
	require.NoError(t, err)
	require.NotNil(t, agentBay)

	// Create VPC session with browser image
	params := &agentbay.CreateSessionParams{
		ImageId: "browser_latest",
		// VPC-specific parameters would go here
	}

	sessionResult, err := agentBay.Create(params)
	require.NoError(t, err)
	require.NotNil(t, sessionResult)
	require.True(t, sessionResult.Success)
	require.NotNil(t, sessionResult.Session)

	session := sessionResult.Session
	defer func() {
		// Clean up session
		_, err := agentBay.Delete(session, false)
		if err != nil {
			t.Logf("Warning: Failed to delete session: %v", err)
		}
	}()

	// Initialize browser
	option := browser.NewBrowserOption()
	success, err := session.Browser.Initialize(option)
	require.NoError(t, err)
	require.True(t, success)

	// Get endpoint URL (should use VPC IP and port format)
	endpointURL, err := session.Browser.GetEndpointURL()
	assert.NoError(t, err)
	assert.NotEmpty(t, endpointURL)

	// VPC endpoints should start with ws://
	assert.Contains(t, endpointURL, "ws://")
	t.Logf("VPC Browser endpoint URL: %s", endpointURL)
}
