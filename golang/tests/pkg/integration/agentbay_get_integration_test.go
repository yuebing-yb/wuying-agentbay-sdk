package integration

import (
	"fmt"
	"os"
	"testing"

	"github.com/aliyun/wuying-agentbay-sdk/golang/pkg/agentbay"
)

func TestAgentBayGetAPI(t *testing.T) {
	apiKey := os.Getenv("AGENTBAY_API_KEY")
	if apiKey == "" {
		t.Fatal("AGENTBAY_API_KEY environment variable is not set")
	}

	client, err := agentbay.NewAgentBay(apiKey, nil)
	if err != nil {
		t.Fatalf("Failed to initialize AgentBay client: %v", err)
	}

	fmt.Println("Creating a new session for Get API testing...")
	createResult, err := client.Create(nil)
	if err != nil {
		t.Fatalf("Failed to create session: %v", err)
	}
	createdSession := createResult.Session
	sessionId := createdSession.SessionID
	t.Logf("Session created with ID: %s", sessionId)

	fmt.Println("Testing Get API...")
	session, err := client.Get(sessionId)
	if err != nil {
		t.Fatalf("Failed to get session: %v", err)
	}

	if session == nil {
		t.Fatal("Get returned nil session")
	}

	if session.SessionID != sessionId {
		t.Errorf("Expected SessionID %s, got %s", sessionId, session.SessionID)
	}

	if session.AgentBay == nil {
		t.Error("Session AgentBay reference is nil")
	}

	t.Logf("Successfully retrieved session with ID: %s", session.SessionID)

	fmt.Println("Get API test passed successfully")

	fmt.Println("Cleaning up: Deleting the session...")
	deleteResult, err := session.Delete()
	if err != nil {
		t.Fatalf("Failed to delete session: %v", err)
	}
	t.Logf("Session %s deleted successfully", sessionId)
	if !deleteResult.Success {
		t.Error("Session deletion failed")
	}
}

func TestAgentBayGetNonExistentSession(t *testing.T) {
	apiKey := os.Getenv("AGENTBAY_API_KEY")
	if apiKey == "" {
		t.Fatal("AGENTBAY_API_KEY environment variable is not set")
	}

	client, err := agentbay.NewAgentBay(apiKey, nil)
	if err != nil {
		t.Fatalf("Failed to initialize AgentBay client: %v", err)
	}

	fmt.Println("Testing Get API with non-existent session ID...")
	nonExistentSessionId := "session-nonexistent-12345"
	_, err = client.Get(nonExistentSessionId)

	if err == nil {
		t.Fatal("Expected error for non-existent session, got nil")
	}

	t.Logf("Correctly received error for non-existent session: %v", err)
	fmt.Println("Get API non-existent session test passed successfully")
}

func TestAgentBayGetEmptySessionId(t *testing.T) {
	apiKey := os.Getenv("AGENTBAY_API_KEY")
	if apiKey == "" {
		t.Fatal("AGENTBAY_API_KEY environment variable is not set")
	}

	client, err := agentbay.NewAgentBay(apiKey, nil)
	if err != nil {
		t.Fatalf("Failed to initialize AgentBay client: %v", err)
	}

	fmt.Println("Testing Get API with empty session ID...")
	_, err = client.Get("")

	if err == nil {
		t.Fatal("Expected error for empty session ID, got nil")
	}

	expectedErrMsg := "session_id is required"
	if err.Error() != expectedErrMsg {
		t.Errorf("Expected error message '%s', got '%s'", expectedErrMsg, err.Error())
	}

	t.Logf("Correctly received error for empty session ID: %v", err)
	fmt.Println("Get API empty session ID test passed successfully")
}
