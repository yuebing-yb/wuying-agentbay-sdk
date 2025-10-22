package integration

import (
	"os"
	"strings"
	"testing"
	"time"

	"github.com/aliyun/wuying-agentbay-sdk/golang/pkg/agentbay"
	"github.com/stretchr/testify/assert"
	"github.com/stretchr/testify/require"
)

// TestMobileGetAdbUrl_E2E tests Mobile.GetAdbUrl with real AgentBay session
// This test requires:
// 1. AGENTBAY_API_KEY environment variable
// 2. Real AgentBay session (mobile_latest image)
// 3. Manual execution (not suitable for CI/CD)
func TestMobileGetAdbUrl_E2E(t *testing.T) {
	// Skip if no API key provided
	apiKey := os.Getenv("AGENTBAY_API_KEY")
	if apiKey == "" {
		t.Skip("Skipping real E2E test: AGENTBAY_API_KEY not set")
	}

	// Create AgentBay client
	agentBay, err := agentbay.NewAgentBay(apiKey)
	require.NoError(t, err, "Failed to create AgentBay client")

	// Create session with mobile image
	sessionParams := &agentbay.CreateSessionParams{
		ImageId: "mobile_latest", // Use mobile_latest for mobile automation
	}

	sessionResult, err := agentBay.Create(sessionParams)
	require.NoError(t, err, "Failed to create session")
	require.NotNil(t, sessionResult.Session, "Session should be created")

	session := sessionResult.Session
	defer func() {
		// Cleanup: Delete session after test
		deleteResult, _ := session.Delete()
		if deleteResult != nil && deleteResult.RequestID != "" {
			t.Logf("Session %s deleted successfully", session.SessionID)
		}
	}()

	t.Logf("Created mobile session: %s", session.SessionID)

	// Wait for session to be ready
	time.Sleep(15 * time.Second) // Mobile sessions may take longer to start

	t.Run("GetAdbUrl_WithValidKey", func(t *testing.T) {
		// Use a valid ADB public key
		adbkeyPub := "test_adb_key_123"

		result := session.Mobile.GetAdbUrl(adbkeyPub)

		// Verify result structure
		assert.NotNil(t, result, "Result should not be nil")
		assert.True(t, result.Success, "GetAdbUrl should succeed: %s", result.ErrorMessage)
		assert.NotEmpty(t, result.RequestID, "Should have request ID")
		assert.NotEmpty(t, result.URL, "Should have ADB URL")
		assert.Empty(t, result.ErrorMessage, "Should not have error message on success")

		// Log the result
		t.Logf("ADB URL: %s", result.URL)
		t.Logf("Request ID: %s", result.RequestID)

		// Verify URL format: "adb connect <IP>:<Port>"
		assert.True(t, strings.HasPrefix(result.URL, "adb connect"),
			"URL should start with 'adb connect', got: %s", result.URL)
	})

	t.Run("GetAdbUrl_ReturnsValidFormat", func(t *testing.T) {
		// Use a simple test key
		adbkeyPub := "test_key_123"

		result := session.Mobile.GetAdbUrl(adbkeyPub)

		assert.True(t, result.Success, "GetAdbUrl should succeed")
		assert.NotEmpty(t, result.URL, "Should have ADB URL")

		// Parse URL format: "adb connect <IP>:<Port>"
		parts := strings.Split(result.URL, " ")
		assert.Equal(t, 3, len(parts), "URL should have format 'adb connect <address>', got: %s", result.URL)
		assert.Equal(t, "adb", parts[0])
		assert.Equal(t, "connect", parts[1])

		// Verify IP:Port format
		addressParts := strings.Split(parts[2], ":")
		assert.Equal(t, 2, len(addressParts), "Address should be <IP>:<Port>, got: %s", parts[2])

		t.Logf("Parsed ADB URL - IP: %s, Port: %s", addressParts[0], addressParts[1])
	})

	t.Run("GetAdbUrl_RequestIdExists", func(t *testing.T) {
		adbkeyPub := "test_key_xyz"

		result := session.Mobile.GetAdbUrl(adbkeyPub)

		assert.True(t, result.Success, "GetAdbUrl should succeed")
		assert.NotEmpty(t, result.RequestID, "Request ID should not be empty")
		assert.Greater(t, len(result.RequestID), 0, "Request ID should have length > 0")

		t.Logf("Request ID: %s", result.RequestID)
	})
}

// TestMobileGetAdbUrl_NonMobileImage tests GetAdbUrl fails on non-mobile image
func TestMobileGetAdbUrl_NonMobileImage(t *testing.T) {
	// Skip if no API key provided
	apiKey := os.Getenv("AGENTBAY_API_KEY")
	if apiKey == "" {
		t.Skip("Skipping real E2E test: AGENTBAY_API_KEY not set")
	}

	// Create AgentBay client
	agentBay, err := agentbay.NewAgentBay(apiKey)
	require.NoError(t, err, "Failed to create AgentBay client")

	// Create session with browser image (non-mobile)
	sessionParams := &agentbay.CreateSessionParams{
		ImageId: "browser_latest", // Use browser_latest (not mobile)
	}

	sessionResult, err := agentBay.Create(sessionParams)
	require.NoError(t, err, "Failed to create session")
	require.NotNil(t, sessionResult.Session, "Session should be created")

	session := sessionResult.Session
	defer func() {
		// Cleanup: Delete session after test
		deleteResult, _ := session.Delete()
		if deleteResult != nil && deleteResult.RequestID != "" {
			t.Logf("Browser session %s deleted successfully", session.SessionID)
		}
	}()

	t.Logf("Created browser session: %s", session.SessionID)

	// Wait for session to be ready
	time.Sleep(10 * time.Second)

	t.Run("GetAdbUrl_FailsOnBrowserImage", func(t *testing.T) {
		adbkeyPub := "test_key_456"

		result := session.Mobile.GetAdbUrl(adbkeyPub)

		// Should fail because this is not a mobile environment
		assert.NotNil(t, result, "Result should not be nil")
		assert.False(t, result.Success, "GetAdbUrl should fail on non-mobile image")
		assert.NotEmpty(t, result.ErrorMessage, "Should have error message")
		assert.Contains(t, strings.ToLower(result.ErrorMessage), "mobile",
			"Error message should mention mobile environment")

		t.Logf("Expected error: %s", result.ErrorMessage)
	})
}
