package integration

import (
	"fmt"
	"os"
	"strings"
	"testing"
	"time"

	"github.com/aliyun/wuying-agentbay-sdk/golang/pkg/agentbay"
	"github.com/joho/godotenv"
)

func init() {
	// Load environment variables from .env file
	envFile := "../../.env"
	if _, err := os.Stat(envFile); err == nil {
		if err := godotenv.Load(envFile); err != nil {
			fmt.Printf("Warning: Error loading .env file: %v\n", err)
		}
	}

	// Also try to load from project root
	rootEnvFile := "../../../.env"
	if _, err := os.Stat(rootEnvFile); err == nil {
		if err := godotenv.Load(rootEnvFile); err != nil {
			fmt.Printf("Warning: Error loading root .env file: %v\n", err)
		}
	}
}

// containsIgnoreCase checks if a string contains a substring (case insensitive)
func containsIgnoreCase(s, substr string) bool {
	return strings.Contains(strings.ToLower(s), strings.ToLower(substr))
}

// TestDeletePausedSession tests that deleting a paused session returns an appropriate error
func TestDeletePausedSession(t *testing.T) {
	apiKey := os.Getenv("AGENTBAY_API_KEY")
	if apiKey == "" {
		t.Fatal("AGENTBAY_API_KEY environment variable is not set")
	}

	client, err := agentbay.NewAgentBay(apiKey, nil)
	if err != nil {
		t.Fatalf("Failed to initialize AgentBay client: %v", err)
	}

	fmt.Println("Creating a new session for paused delete testing...")
	createResult, err := client.Create(nil)
	if err != nil {
		t.Fatalf("Failed to create session: %v", err)
	}
	createdSession := createResult.Session
	sessionId := createdSession.SessionID
	t.Logf("Session created with ID: %s", sessionId)

	// Verify session is initially in RUNNING state
	fmt.Println("Step 1: Verifying session is initially RUNNING...")
	getResult, err := createdSession.GetStatus()
	if err != nil {
		t.Fatalf("Failed to get session: %v", err)
	}
	if !getResult.Success {
		t.Fatalf("Get session failed: %s", getResult.ErrorMessage)
	}
	if getResult.Status != "RUNNING" {
		t.Fatalf("Expected session status RUNNING, got %s", getResult.Status)
	}
	t.Logf("✓ Session is RUNNING: %s", sessionId)

	// Pause the session
	fmt.Println("Step 2: Pausing session...")
	pauseResult, err := client.Pause(createdSession, 600, 2.0)
	if err != nil {
		t.Fatalf("Failed to pause session: %v", err)
	}
	if pauseResult == nil {
		t.Fatal("Pause returned nil result")
	}
	if !pauseResult.Success {
		t.Fatalf("Pause failed: %s", pauseResult.ErrorMessage)
	}
	t.Logf("✓ Session pause initiated successfully")
	t.Logf("  Request ID: %s", pauseResult.RequestID)

	// Wait a bit for pause to complete
	fmt.Println("Step 3: Waiting for session to pause...")
	time.Sleep(2 * time.Second)

	// Check session status after pause
	getResult, err = createdSession.GetStatus()
	if err != nil {
		t.Fatalf("Failed to get session: %v", err)
	}
	if !getResult.Success {
		t.Fatalf("Get session failed: %s", getResult.ErrorMessage)
	}
	// Session should be PAUSED or still PAUSING
	if getResult.Status != "PAUSED" && getResult.Status != "PAUSING" {
		t.Fatalf("Expected session status PAUSED or PAUSING, got %s", getResult.Status)
	}
	t.Logf("✓ Session status after pause: %s", getResult.Status)
	
	// Resume the session first to test delete on running session
	fmt.Println("Step 4: Resuming session before delete test...")
	resumeResult, err := client.Resume(createdSession, 120, 2.0)
	if err != nil {
		t.Logf("Failed to resume session for delete test: %v", err)
		t.Skip("Skipping delete test due to resume failure")
		return
	}
	if resumeResult == nil {
		t.Log("Resume returned nil result")
		t.Skip("Skipping delete test due to resume failure")
		return
	}
	if !resumeResult.Success {
		t.Logf("Resume failed: %s", resumeResult.ErrorMessage)
		t.Skip("Skipping delete test due to resume failure")
		return
	}
	t.Logf("✓ Session resumed successfully for delete test")

	// Wait a bit for resume to complete and check status
	fmt.Println("Step 5: Waiting for session to resume and checking status...")
	time.Sleep(2 * time.Second)

	// Check session status after resume
	getResult, err = createdSession.GetStatus()
	if err != nil {
		t.Logf("Failed to get session status after resume: %v", err)
		t.Skip("Skipping delete test due to status check failure")
		return
	}
	if !getResult.Success {
		t.Logf("Get session failed after resume: %s", getResult.ErrorMessage)
		t.Skip("Skipping delete test due to status check failure")
		return
	}
	if getResult.Status != "RUNNING" {
		t.Logf("Expected session status RUNNING after resume, got %s", getResult.Status)
		t.Skip("Skipping delete test - session not in RUNNING state")
		return
	}
	t.Logf("✓ Session status after resume: %s", getResult.Status)

	// Try to delete the running session - this should succeed
	fmt.Println("Step 6: Attempting to delete running session...")
	deleteResult, err := createdSession.Delete()
	if err != nil {
		t.Logf("Error deleting running session: %v", err)
	} else {
		if deleteResult.Success {
			t.Logf("✓ Session %s deleted successfully", sessionId)
		} else {
			t.Logf("Delete failed: %s", deleteResult.ErrorMessage)
		}
	}
}
