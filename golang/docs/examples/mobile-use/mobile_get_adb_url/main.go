package main

import (
	"fmt"
	"os"

	"github.com/aliyun/wuying-agentbay-sdk/golang/pkg/agentbay"
)

func main() {
	// Get API key from environment variable
	apiKey := os.Getenv("AGENTBAY_API_KEY")
	if apiKey == "" {
		fmt.Println("Error: AGENTBAY_API_KEY environment variable is not set")
		fmt.Println("Please set it with: export AGENTBAY_API_KEY=your_api_key")
		os.Exit(1)
	}

	// Initialize AgentBay client
	client, err := agentbay.NewAgentBay(apiKey)
	if err != nil {
		fmt.Printf("Failed to create AgentBay client: %v\n", err)
		os.Exit(1)
	}

	fmt.Println("=== Mobile GetAdbUrl Example ===")
	fmt.Println()

	// Create a mobile session
	fmt.Println("Creating mobile session...")
	params := &agentbay.CreateSessionParams{
		ImageId: "mobile_latest", // Must use mobile_latest for ADB functionality
	}

	sessionResult, err := client.Create(params)
	if err != nil {
		fmt.Printf("Failed to create session: %v\n", err)
		os.Exit(1)
	}

	session := sessionResult.Session
	fmt.Printf("✅ Session created successfully\n")
	fmt.Printf("   Session ID: %s\n", session.SessionID)
	fmt.Printf("   Image ID: %s\n", session.ImageId)
	fmt.Println()

	// Ensure session cleanup
	defer func() {
		fmt.Println("Cleaning up session...")
		deleteResult, err := session.Delete()
		if err != nil {
			fmt.Printf("Warning: Failed to delete session: %v\n", err)
		} else if deleteResult.Success {
			fmt.Printf("✅ Session deleted successfully (RequestID: %s)\n", deleteResult.RequestID)
		}
	}()

	// Get ADB URL with public key
	// Note: In production, you should use your actual ADB public key
	// This is a desensitized example key
	adbkeyPub := "QAAAAM0muSn7yQCY...your_adb_public_key...EAAQAA="

	fmt.Println("Getting ADB connection URL...")
	result := session.Mobile.GetAdbUrl(adbkeyPub)

	if result.Success {
		fmt.Printf("✅ ADB URL retrieved successfully\n")
		fmt.Printf("   URL: %s\n", result.URL)
		fmt.Printf("   Request ID: %s\n", result.RequestID)
		fmt.Println()
		fmt.Println("You can now connect to the mobile device using:")
		fmt.Printf("   %s\n", result.URL)
	} else {
		fmt.Printf("❌ Failed to get ADB URL\n")
		fmt.Printf("   Error: %s\n", result.ErrorMessage)
		fmt.Printf("   Request ID: %s\n", result.RequestID)
		os.Exit(1)
	}

	fmt.Println()
	fmt.Println("=== Example completed successfully ===")
}
