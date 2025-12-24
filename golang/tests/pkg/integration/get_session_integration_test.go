package integration

import (
	"fmt"
	"os"
	"testing"

	"github.com/aliyun/wuying-agentbay-sdk/golang/pkg/agentbay"
)

// TestGetStatusAPI integration test for GetSessionDetail (GetStatus) API
func TestGetStatusAPI(t *testing.T) {
	// Get API Key
	apiKey := os.Getenv("AGENTBAY_API_KEY")
	if apiKey == "" {
		t.Fatal("AGENTBAY_API_KEY environment variable is not set")
	}

	// Initialize AgentBay client
	client, err := agentbay.NewAgentBay(apiKey, nil)
	if err != nil {
		t.Fatalf("Failed to initialize AgentBay client: %v", err)
	}

	// Create a session first
	fmt.Println("Creating a new session for GetSession testing...")
	createResult, err := client.Create(nil)
	if err != nil {
		t.Fatalf("Failed to create session: %v", err)
	}
	session := createResult.Session
	sessionID := session.SessionID
	t.Logf("Session created with ID: %s", sessionID)

	// Test GetStatus API
	fmt.Println("Testing GetStatus API...")
	getStatusResult, err := session.GetStatus()
	if err != nil {
		t.Fatalf("Failed to call GetStatus API: %v", err)
	}

	// Validate response
	if getStatusResult.RequestID == "" {
		t.Error("RequestID should not be empty")
	}
	t.Logf("GetStatus RequestID: %s", getStatusResult.RequestID)

	if getStatusResult.HttpStatusCode != 200 {
		t.Errorf("Expected HttpStatusCode 200, got %d", getStatusResult.HttpStatusCode)
	}

	if getStatusResult.Code != "ok" {
		t.Errorf("Expected Code 'ok', got '%s'", getStatusResult.Code)
	}

	if !getStatusResult.Success {
		t.Error("Expected Success to be true")
	}

	if getStatusResult.Status == "" {
		t.Error("Status should not be empty")
	}
	t.Logf("Status: %s", getStatusResult.Status)

	// TODO: Don't support file transfer context yet
	// Validate contexts field
	// if getSessionResult.Data.Contexts == nil {
	// 	t.Error("Contexts field should not be nil")
	// }
	// if len(getSessionResult.Data.Contexts) == 0 {
	// 	t.Error("Contexts list should not be empty")
	// }
	// t.Logf("Contexts count: %d", len(getSessionResult.Data.Contexts))
	// for i, ctx := range getSessionResult.Data.Contexts {
	// 	if ctx.Name == "" {
	// 		t.Errorf("Context %d should have a non-empty Name field", i)
	// 	}
	// 	if ctx.ID == "" {
	// 		t.Errorf("Context %d should have a non-empty ID field", i)
	// 	}
	// 	t.Logf("Context %d: name=%s, id=%s", i, ctx.Name, ctx.ID)
	// }

	// Clean up: Delete the session
	fmt.Println("Cleaning up: Deleting the session...")
	_, err = session.Delete()
	if err != nil {
		t.Logf("Warning: Failed to delete session: %v", err)
	} else {
		t.Logf("Session %s deleted successfully", sessionID)
	}
}
