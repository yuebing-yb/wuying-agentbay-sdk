package integration_test

import (
	"fmt"
	"testing"

	"github.com/aliyun/wuying-agentbay-sdk/golang/pkg/agentbay"
	"github.com/aliyun/wuying-agentbay-sdk/golang/tests/pkg/agentbay/testutil"
)

func TestListMcpTools_WindowsLatest(t *testing.T) {
	// Initialize AgentBay client
	apiKey := testutil.GetTestAPIKey(t)
	agentBay, err := agentbay.NewAgentBay(apiKey)
	if err != nil {
		t.Fatalf("Error initializing AgentBay client: %v", err)
	}

	// Create a session with windows_latest ImageId
	fmt.Println("Creating a new session with windows_latest ImageId...")
	params := agentbay.NewCreateSessionParams().WithImageId("windows_latest")
	sessionResult, err := agentBay.Create(params)
	if err != nil {
		t.Fatalf("Error creating session: %v", err)
	}
	session := sessionResult.Session
	t.Logf("Session created with ID: %s (RequestID: %s)",
		session.SessionID, sessionResult.RequestID)

	// Verify that ImageId is properly set in session
	if session.ImageId != "windows_latest" {
		t.Errorf("Expected session.ImageId to be 'windows_latest', but got '%s'", session.ImageId)
	}

	// IMPORTANT: Ensure cleanup of the session after test
	defer func() {
		fmt.Println("Cleaning up: Deleting the session...")
		deleteResult, err := agentBay.Delete(session)
		if err != nil {
			t.Logf("Warning: Error deleting session: %v", err)
		} else {
			t.Logf("Session successfully deleted (RequestID: %s)",
				deleteResult.RequestID)
		}
	}()

	// Call ListMcpTools API
	fmt.Printf("Calling ListMcpTools with ImageId: %s\n", session.ImageId)
	mcpToolsResult, err := session.ListMcpTools()
	if err != nil {
		t.Fatalf("Error calling ListMcpTools: %v", err)
	}

	// Verify the response
	t.Logf("ListMcpTools response - RequestID: %s", mcpToolsResult.RequestID)
	t.Logf("Number of tools returned: %d", len(mcpToolsResult.Tools))

	if len(mcpToolsResult.Tools) == 0 {
		t.Error("Expected at least one MCP tool for windows_latest, but got none")
		return
	}

	// Print all tools for windows_latest
	fmt.Println("\n=== MCP Tools for windows_latest ===")
	for i, tool := range mcpToolsResult.Tools {
		fmt.Printf("\nTool %d:\n", i+1)
		fmt.Printf("  Name: %s\n", tool.Name)
		fmt.Printf("  Description: %s\n", tool.Description)
		fmt.Printf("  Server: %s\n", tool.Server)
		fmt.Printf("  Tool: %s\n", tool.Tool)
		if tool.InputSchema != nil {
			fmt.Printf("  InputSchema: %v\n", tool.InputSchema)
		}

		// Verify each tool has required fields
		if tool.Name == "" {
			t.Errorf("Tool %d has empty Name", i+1)
		}
		if tool.Server == "" {
			t.Errorf("Tool %d has empty Server", i+1)
		}
		if tool.Tool == "" {
			t.Errorf("Tool %d has empty Tool identifier", i+1)
		}
		// Description and InputSchema can be empty, so we don't check them
	}
	fmt.Println("\n=====================================")

	// NOTE: Session must not store MCP tool lists. Only the API result is validated here.
}
