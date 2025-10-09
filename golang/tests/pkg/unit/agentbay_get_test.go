package agentbay_test

import (
	"fmt"
	"testing"

	"github.com/aliyun/wuying-agentbay-sdk/golang/pkg/agentbay"
)

// TestAgentBayGetEmptySessionId tests Get with empty session ID
func TestAgentBayGetEmptySessionId(t *testing.T) {
	ab := &agentbay.AgentBay{
		APIKey: "test-api-key",
	}

	// Test Get method with empty session ID
	_, err := ab.Get("")

	// Assertions
	if err == nil {
		t.Fatal("Expected error for empty session ID, got nil")
	}

	expectedErrMsg := "session_id is required"
	if err.Error() != expectedErrMsg {
		t.Errorf("Expected error message '%s', got '%s'", expectedErrMsg, err.Error())
	}
}

// TestAgentBayGetBasicValidation tests basic validation for Get method
func TestAgentBayGetBasicValidation(t *testing.T) {
	tests := []struct {
		name        string
		sessionID   string
		expectError bool
		errorMsg    string
	}{
		{
			name:        "Empty session ID",
			sessionID:   "",
			expectError: true,
			errorMsg:    "session_id is required",
		},
	}

	for _, tt := range tests {
		t.Run(tt.name, func(t *testing.T) {
			ab := &agentbay.AgentBay{
				APIKey: "test-api-key",
			}

			_, err := ab.Get(tt.sessionID)

			if tt.expectError {
				if err == nil {
					t.Fatalf("Expected error, got nil")
				}
				if err.Error() != tt.errorMsg {
					t.Errorf("Expected error message '%s', got '%s'", tt.errorMsg, err.Error())
				}
			}
		})
	}
}

// TestAgentBayGetInterfaceCompliance tests that Get method signature is correct
func TestAgentBayGetInterfaceCompliance(t *testing.T) {
	// This test ensures the Get method exists with the correct signature
	var _ func(string) (*agentbay.Session, error) = (&agentbay.AgentBay{}).Get

	// If this compiles, the method signature is correct
	t.Log("Get method has correct signature")
}

// TestAgentBayGetErrorMessages tests error message formatting
func TestAgentBayGetErrorMessages(t *testing.T) {
	ab := &agentbay.AgentBay{
		APIKey: "test-api-key",
	}

	tests := []struct {
		name      string
		sessionID string
		wantErr   string
	}{
		{
			name:      "Empty session ID error",
			sessionID: "",
			wantErr:   "session_id is required",
		},
	}

	for _, tt := range tests {
		t.Run(tt.name, func(t *testing.T) {
			_, err := ab.Get(tt.sessionID)
			if err == nil {
				t.Fatal("Expected error, got nil")
			}
			if err.Error() != tt.wantErr {
				t.Errorf("Expected error '%s', got '%s'", tt.wantErr, err.Error())
			}
		})
	}
}

// TestGetMethodDocumentation verifies the Get method is properly exported and documented
func TestGetMethodDocumentation(t *testing.T) {
	// Create a simple test to ensure the method exists and can be called
	defer func() {
		if r := recover(); r != nil {
			t.Errorf("Get method panicked: %v", r)
		}
	}()

	ab := &agentbay.AgentBay{
		APIKey: "test-key",
	}

	// This should return an error (empty session ID) but shouldn't panic
	_, err := ab.Get("")
	if err == nil {
		t.Error("Expected error for empty session ID")
	}

	// Verify error message format
	expectedPrefix := "session_id is required"
	if err.Error() != expectedPrefix {
		t.Errorf("Expected error message to be '%s', got '%s'", expectedPrefix, err.Error())
	}
}

// Example test showing expected usage pattern
func ExampleAgentBay_Get() {
	ab := &agentbay.AgentBay{
		APIKey: "your-api-key",
	}

	session, err := ab.Get("session-id-123")
	if err != nil {
		fmt.Printf("Error: %v\n", err)
		return
	}

	fmt.Printf("Retrieved session: %s\n", session.SessionID)
}
