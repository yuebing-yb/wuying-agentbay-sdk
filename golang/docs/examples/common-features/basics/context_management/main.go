package main

import (
	"fmt"
	"os"

	"github.com/aliyun/wuying-agentbay-sdk/golang/pkg/agentbay"
)

func main() {
	// Initialize the AgentBay client
	// You can provide the API key as a parameter or set the AGENTBAY_API_KEY environment variable
	apiKey := os.Getenv("AGENTBAY_API_KEY")
	if apiKey == "" {
		apiKey = "akm-xxx" // Replace with your actual API key
	}

	ab, err := agentbay.NewAgentBay(apiKey)
	if err != nil {
		fmt.Printf("Error initializing AgentBay: %v\n", err)
		return
	}

	// Example 1: List all contexts
	fmt.Println("\nExample 1: Listing all contexts...")
	listResult, err := ab.Context.List(agentbay.NewContextListParams())
	if err != nil {
		fmt.Printf("Error listing contexts: %v\n", err)
	} else {
		fmt.Printf("Found %d contexts (RequestID: %s):\n", len(listResult.Contexts), listResult.RequestID)
		for _, ctx := range listResult.Contexts {
			fmt.Printf("- %s (%s): state=%s, os=%s\n",
				ctx.Name, ctx.ID)
		}
	}

	// Example 2: Get a context (create if it doesn't exist)
	fmt.Println("\nExample 2: Getting a context (creating if it doesn't exist)...")
	contextName := "my-test-context"
	getResult, err := ab.Context.Get(contextName, true)
	if err != nil {
		fmt.Printf("Error getting context: %v\n", err)
		return
	}
	if getResult.ContextID == "" {
		fmt.Println("Context not found and could not be created")
		return
	}

	fmt.Printf("Got context: %s (%s) with RequestID: %s\n",
		getResult.Context.Name,
		getResult.ContextID,
		getResult.RequestID)

	// Use the Context object directly
	context := getResult.Context

	// Example 3: Create a session with the context
	fmt.Println("\nExample 3: Creating a session with the context...")
	params := agentbay.NewCreateSessionParams().
		AddContextSync(context.ID, "/workspace", nil).
		WithLabels(map[string]string{
			"username": "alice",
			"project":  "my-project",
		})

	sessionResult, err := ab.Create(params)
	if err != nil {
		fmt.Printf("Error creating session: %v\n", err)
		return
	}
	fmt.Printf("Session created with ID: %s (RequestID: %s)\n",
		sessionResult.Session.SessionID, sessionResult.RequestID)

	session := sessionResult.Session

	// Example 4: Update the context
	fmt.Println("\nExample 4: Updating the context...")
	context.Name = "renamed-test-context"
	updateResult, err := ab.Context.Update(context)
	if err != nil {
		fmt.Printf("Error updating context: %v\n", err)
	} else if !updateResult.Success {
		fmt.Println("Context update was not successful")
	} else {
		fmt.Printf("Context updated successfully to: %s (RequestID: %s)\n",
			context.Name, updateResult.RequestID)
	}

	// Example 5: Clear context data
	fmt.Println("\nExample 5: Clearing context data...")
	fmt.Println("Starting synchronous context clear (recommended approach)...")

	// Synchronous clear (blocking until completion) - Recommended approach
	clearResult, err := ab.Context.Clear(context.ID, 30, 2.0)
	if err != nil {
		fmt.Printf("❌ Error during context clear: %v\n", err)
	} else {
		fmt.Printf("Clear result: Success=%t, Status=%s, RequestID=%s\n",
			clearResult.Success, clearResult.Status, clearResult.RequestID)

		if clearResult.Success {
			fmt.Println("✅ Context data cleared successfully")
			fmt.Printf("   Context ID: %s\n", clearResult.ContextID)
			fmt.Printf("   Final Status: %s\n", clearResult.Status)
		} else {
			fmt.Printf("❌ Context data clearing failed: %s\n", clearResult.ErrorMessage)
		}
	}

	// Clean up
	fmt.Println("\nCleaning up...")
	fmt.Println("Note: Context data has been cleared, but the context itself still exists.")

	// Delete the session
	deleteSessionResult, err := ab.Delete(session)
	if err != nil {
		fmt.Printf("Error deleting session: %v\n", err)
	} else {
		fmt.Printf("Session deleted successfully (RequestID: %s)\n", deleteSessionResult.RequestID)
	}

	// Delete the context
	fmt.Println("Deleting the context...")
	deleteContextResult, err := ab.Context.Delete(context)
	if err != nil {
		fmt.Printf("Error deleting context: %v\n", err)
	} else {
		fmt.Printf("Context deleted successfully (RequestID: %s)\n", deleteContextResult.RequestID)
	}
}
