package integration

import (
	"fmt"
	"os"
	"testing"

	"github.com/aliyun/wuying-agentbay-sdk/golang/pkg/agentbay"
)

// TestGetSessionAPI integration test for GetSession API
func TestGetSessionAPI(t *testing.T) {
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

	// Test GetSession API
	fmt.Println("Testing GetSession API...")
	getSessionResult, err := client.GetSession(sessionID)
	if err != nil {
		t.Fatalf("Failed to call GetSession API: %v", err)
	}

	// Validate response
	if getSessionResult.RequestID == "" {
		t.Error("RequestID should not be empty")
	}
	t.Logf("GetSession RequestID: %s", getSessionResult.RequestID)

	if getSessionResult.HttpStatusCode != 200 {
		t.Errorf("Expected HttpStatusCode 200, got %d", getSessionResult.HttpStatusCode)
	}

	if getSessionResult.Code != "ok" {
		t.Errorf("Expected Code 'ok', got '%s'", getSessionResult.Code)
	}

	if !getSessionResult.Success {
		t.Error("Expected Success to be true")
	}

	// Validate Data field
	if getSessionResult.Data == nil {
		t.Fatal("Data field should not be nil")
	}

	if getSessionResult.Data.SessionID != sessionID {
		t.Errorf("Expected SessionID %s, got %s", sessionID, getSessionResult.Data.SessionID)
	}

	// Note: Data.Success field is not always populated by the API
	// The presence of AppInstanceID and ResourceID indicates a successful query

	if getSessionResult.Data.AppInstanceID == "" {
		t.Error("AppInstanceID should not be empty")
	}
	t.Logf("AppInstanceID: %s", getSessionResult.Data.AppInstanceID)

	if getSessionResult.Data.ResourceID == "" {
		t.Error("ResourceID should not be empty")
	}
	t.Logf("ResourceID: %s", getSessionResult.Data.ResourceID)

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
