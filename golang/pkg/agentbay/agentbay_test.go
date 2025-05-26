package agentbay

import (
	"fmt"
	"os"
	"strings"
	"testing"
)

// Helper function to check if a string contains "tool not found"
func containsToolNotFound(s string) bool {
	return strings.Contains(strings.ToLower(s), "tool not found")
}

// Get API key for testing
func getTestAPIKey(t *testing.T) string {
	apiKey := os.Getenv("AGENTBAY_API_KEY")
	if apiKey == "" {
		apiKey = "akm-xxx" // Replace with your test API key
		t.Logf("Warning: Using default API key. Set AGENTBAY_API_KEY environment variable for testing.")
	}
	return apiKey
}

func TestNewAgentBay(t *testing.T) {
	// Test with API key provided directly
	testAPIKey := getTestAPIKey(t)
	client, err := NewAgentBay(testAPIKey)
	if err != nil {
		t.Fatalf("Expected no error, got %v", err)
	}
	if client.APIKey != testAPIKey {
		t.Errorf("Expected API key to be '%s', got '%s'", testAPIKey, client.APIKey)
	}

	// Test with API key from environment variable
	os.Setenv("AGENTBAY_API_KEY", "env_api_key")
	defer os.Unsetenv("AGENTBAY_API_KEY")

	client, err = NewAgentBay("")
	if err != nil {
		t.Fatalf("Expected no error, got %v", err)
	}
	if client.APIKey != "env_api_key" {
		t.Errorf("Expected API key to be 'env_api_key', got '%s'", client.APIKey)
	}

	// Test with no API key
	os.Unsetenv("AGENTBAY_API_KEY")
	_, err = NewAgentBay("")
	if err == nil {
		t.Fatal("Expected error for missing API key, got nil")
	}
}

func TestAgentBay_Create_List_Delete(t *testing.T) {
	// Initialize AgentBay client
	apiKey := getTestAPIKey(t)
	agentBay, err := NewAgentBay(apiKey)
	if err != nil {
		t.Fatalf("Error initializing AgentBay client: %v", err)
	}

	// Create a session
	fmt.Println("Creating a new session...")
	session, err := agentBay.Create()
	if err != nil {
		t.Fatalf("Error creating session: %v", err)
	}
	t.Logf("Session created with ID: %s", session.SessionID)

	// Ensure session ID is not empty
	if session.SessionID == "" {
		t.Errorf("Expected non-empty session ID")
	}

	// List all sessions
	fmt.Println("Listing sessions...")
	sessions, err := agentBay.List()
	if err != nil {
		t.Fatalf("Error listing sessions: %v", err)
	}

	// Ensure at least one session (the one we just created)
	if len(sessions) < 1 {
		t.Errorf("Expected at least 1 session, got %d", len(sessions))
	}

	// Check if our created session is in the list
	found := false
	for _, s := range sessions {
		if s.SessionID == session.SessionID {
			found = true
			break
		}
	}
	if !found {
		t.Errorf("Created session with ID %s not found in sessions list", session.SessionID)
	}

	// Delete the session
	fmt.Println("Deleting the session...")
	err = agentBay.Delete(session)
	if err != nil {
		t.Fatalf("Error deleting session: %v", err)
	}

	// List sessions again to ensure it's deleted
	sessions, err = agentBay.List()
	if err != nil {
		t.Fatalf("Error listing sessions after deletion: %v", err)
	}

	// Check if the deleted session is not in the list
	for _, s := range sessions {
		if s.SessionID == session.SessionID {
			t.Errorf("Session with ID %s still exists after deletion", session.SessionID)
		}
	}
}

func TestSession_Properties(t *testing.T) {
	// Initialize AgentBay client
	apiKey := getTestAPIKey(t)
	agentBay, err := NewAgentBay(apiKey)
	if err != nil {
		t.Fatalf("Error initializing AgentBay client: %v", err)
	}

	// Create a session
	fmt.Println("Creating a new session for session testing...")
	session, err := agentBay.Create()
	if err != nil {
		t.Fatalf("Error creating session: %v", err)
	}
	t.Logf("Session created with ID: %s", session.SessionID)
	defer func() {
		// Clean up the session after test
		fmt.Println("Cleaning up: Deleting the session...")
		err := agentBay.Delete(session)
		if err != nil {
			t.Logf("Warning: Error deleting session: %v", err)
		}
	}()

	// Test session properties
	if session.SessionID == "" {
		t.Errorf("Expected non-empty session ID")
	}
	if session.AgentBay != agentBay {
		t.Errorf("Expected AgentBay to be the same instance")
	}

	// Test GetSessionId method
	sessionID := session.GetSessionId()
	if sessionID != session.SessionID {
		t.Errorf("Expected GetSessionId to return '%s', got '%s'", session.SessionID, sessionID)
	}

	// Test GetAPIKey method
	apiKeyFromSession := session.GetAPIKey()
	if apiKeyFromSession != apiKey {
		t.Errorf("Expected GetAPIKey to return '%s', got '%s'", apiKey, apiKeyFromSession)
	}

	// Test GetClient method
	client := session.GetClient()
	if client == nil {
		t.Errorf("Expected GetClient to return a non-nil client")
	}
}

func TestSession_DeleteMethod(t *testing.T) {
	// Initialize AgentBay client
	apiKey := getTestAPIKey(t)
	agentBay, err := NewAgentBay(apiKey)
	if err != nil {
		t.Fatalf("Error initializing AgentBay client: %v", err)
	}

	// Create a session
	fmt.Println("Creating a new session for delete testing...")
	session, err := agentBay.Create()
	if err != nil {
		t.Fatalf("Error creating session: %v", err)
	}
	t.Logf("Session created with ID: %s", session.SessionID)

	// Test Delete method
	fmt.Println("Testing session.Delete method...")
	err = session.Delete()
	if err != nil {
		t.Fatalf("Error deleting session: %v", err)
	}

	// Verify the session was deleted by trying to list sessions
	sessions, err := agentBay.List()
	if err != nil {
		t.Fatalf("Error listing sessions: %v", err)
	}

	// Check if the deleted session is not in the list
	for _, s := range sessions {
		if s.SessionID == session.SessionID {
			t.Errorf("Session with ID %s still exists after deletion", session.SessionID)
		}
	}
}

func TestSession_Command_FileSystem(t *testing.T) {
	// Initialize AgentBay client
	apiKey := getTestAPIKey(t)
	agentBay, err := NewAgentBay(apiKey)
	if err != nil {
		t.Fatalf("Error initializing AgentBay client: %v", err)
	}

	// Create a session
	fmt.Println("Creating a new session for command testing...")
	session, err := agentBay.Create()
	if err != nil {
		t.Fatalf("Error creating session: %v", err)
	}
	t.Logf("Session created with ID: %s", session.SessionID)
	defer func() {
		// Clean up the session after test
		fmt.Println("Cleaning up: Deleting the session...")
		err := agentBay.Delete(session)
		if err != nil {
			t.Logf("Warning: Error deleting session: %v", err)
		}
	}()

	// Test Command execution
	if session.Command != nil {
		fmt.Println("Executing command...")
		response, err := session.Command.ExecuteCommand("ls")
		if err != nil {
			t.Logf("Note: Command execution failed: %v", err)
		} else {
			t.Logf("Command execution result: %s", response)
			// Check if response contains "tool not found"
			if containsToolNotFound(response) {
				t.Errorf("Command.ExecuteCommand returned 'tool not found'")
			}
		}
	} else {
		t.Logf("Note: Command interface is nil, skipping command test")
	}

	// Test FileSystem read operations
	if session.FileSystem != nil {
		fmt.Println("Reading file...")
		content, err := session.FileSystem.ReadFile("/etc/hosts")
		t.Logf("ReadFile result: content='%s', err=%v", content, err)
		if err != nil {
			t.Logf("Note: File read failed: %v", err)
		} else {
			t.Logf("File read successful, content length: %d bytes", len(content))
			// Check if response contains "tool not found"
			if containsToolNotFound(content) {
				t.Errorf("FileSystem.ReadFile returned 'tool not found'")
			}
		}
	} else {
		t.Logf("Note: FileSystem interface is nil, skipping file test")
	}
}

func TestSession_Adb(t *testing.T) {
	// Initialize AgentBay client
	apiKey := getTestAPIKey(t)
	agentBay, err := NewAgentBay(apiKey)
	if err != nil {
		t.Fatalf("Error initializing AgentBay client: %v", err)
	}

	// Create a session
	fmt.Println("Creating a new session for ADB testing...")
	session, err := agentBay.Create()
	if err != nil {
		t.Fatalf("Error creating session: %v", err)
	}
	t.Logf("Session created with ID: %s", session.SessionID)
	defer func() {
		// Clean up the session after test
		fmt.Println("Cleaning up: Deleting the session...")
		err := agentBay.Delete(session)
		if err != nil {
			t.Logf("Warning: Error deleting session: %v", err)
		}
	}()

	// Test Adb shell command execution
	if session.Adb != nil {
		fmt.Println("Executing ADB shell command...")
		response, err := session.Adb.Shell("ls /sdcard")
		if err != nil {
			t.Logf("Note: ADB shell execution failed: %v", err)
		} else {
			t.Logf("ADB shell execution result: %s", response)
			// Check if response contains "tool not found"
			if containsToolNotFound(response) {
				t.Errorf("Adb.Shell returned 'tool not found'")
			}
		}

		// Add more ADB-related tests
		fmt.Println("Executing ADB shell command to check device properties...")
		propResponse, err := session.Adb.Shell("getprop")
		if err != nil {
			t.Logf("Note: ADB getprop execution failed: %v", err)
		} else {
			t.Logf("ADB getprop execution result length: %d bytes", len(propResponse))
			// Check if response contains "tool not found"
			if containsToolNotFound(propResponse) {
				t.Errorf("Adb.Shell returned 'tool not found'")
			}
		}
	} else {
		t.Logf("Note: Adb interface is nil, skipping ADB test")
	}
}
