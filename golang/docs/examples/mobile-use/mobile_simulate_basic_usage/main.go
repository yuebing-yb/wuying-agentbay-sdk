package main

import (
	"fmt"
	"os"
	"path/filepath"
	"time"

	"github.com/aliyun/wuying-agentbay-sdk/golang/pkg/agentbay"
	"github.com/aliyun/wuying-agentbay-sdk/golang/pkg/agentbay/models"
)

var (
	session1           *agentbay.Session
	session2           *agentbay.Session
	mobileSimContextID string
)

func runOnFirstMobileSession(client *agentbay.AgentBay) error {
	fmt.Println("=== First Mobile Session ===")

	// Upload mobile info file for first time
	// How to get the mobile info file please contact the support team.
	fmt.Println("Uploading mobile info file for first time...")

	// Get the path to mobile_info_model_a.json
	// Navigate from golang/docs/examples/mobile-use/mobile_simulate_example to resource/
	mobileInfoFilePath := filepath.Join("..", "..", "..", "..", "..", "resource", "mobile_info_model_a.json")

	// Read the mobile info file
	mobileInfoContent, err := os.ReadFile(mobileInfoFilePath)
	if err != nil {
		return fmt.Errorf("failed to read mobile info file: %v", err)
	}

	// Create mobile simulate service and set simulate params
	fmt.Println("Creating mobile simulate service and set simulate params...")
	simulateService, err := agentbay.NewMobileSimulateService(client)
	if err != nil {
		return fmt.Errorf("failed to create mobile simulate service: %v", err)
	}
	simulateService.SetSimulateEnable(true)
	simulateService.SetSimulateMode(models.MobileSimulateModePropertiesOnly)

	// Upload mobile info
	uploadResult := simulateService.UploadMobileInfo(string(mobileInfoContent), nil)
	if !uploadResult.Success {
		return fmt.Errorf("failed to upload mobile info file: %s", uploadResult.ErrorMessage)
	}

	mobileSimContextID = uploadResult.MobileSimulateContextID
	fmt.Printf("Mobile simulate context id uploaded successfully: %s\n", mobileSimContextID)

	// Create session with mobile simulate configuration
	params := &agentbay.CreateSessionParams{
		ImageId: "mobile_latest",
		ExtraConfigs: &models.ExtraConfigs{
			Mobile: &models.MobileExtraConfig{
				// Set mobile simulate config
				SimulateConfig: simulateService.GetSimulateConfig(),
			},
		},
	}

	fmt.Println("Creating first session...")
	sessionResult, err := client.Create(params)
	if err != nil {
		return fmt.Errorf("failed to create session: %v", err)
	}
	if !sessionResult.Success || sessionResult.Session == nil {
		return fmt.Errorf("failed to create session: %s", sessionResult.ErrorMessage)
	}

	session1 = sessionResult.Session
	fmt.Printf("Session created with ID: %s\n", session1.SessionID)
	fmt.Printf("Session: %+v\n", session1)

	// Wait for mobile simulate to complete
	fmt.Println("Waiting 5 seconds for mobile simulate to complete...")
	time.Sleep(5 * time.Second)

	// Get device model after mobile simulate
	fmt.Println("Getting device model after mobile simulate...")
	result, err := session1.Command.ExecuteCommand("getprop ro.product.model")
	if err != nil {
		return fmt.Errorf("failed to execute command: %v", err)
	}

	productModel := result.Output
	fmt.Printf("First session device model: %s\n", productModel)

	return nil
}

func runOnSecondMobileSession(client *agentbay.AgentBay) error {
	fmt.Println("\n=== Second Mobile Session ===")

	// Create mobile simulate service and set simulate params
	fmt.Println("Creating mobile simulate service and set simulate params...")
	simulateService, err := agentbay.NewMobileSimulateService(client)
	if err != nil {
		return fmt.Errorf("failed to create mobile simulate service: %v", err)
	}
	simulateService.SetSimulateEnable(true)
	simulateService.SetSimulateMode(models.MobileSimulateModePropertiesOnly)
	simulateService.SetSimulateContextID(mobileSimContextID)

	// Use the same mobile simulate context id as the first session
	params := &agentbay.CreateSessionParams{
		ImageId: "mobile_latest",
		ExtraConfigs: &models.ExtraConfigs{
			Mobile: &models.MobileExtraConfig{
				// Set mobile simulate config
				SimulateConfig: simulateService.GetSimulateConfig(),
			},
		},
	}

	fmt.Println("Creating second session...")
	sessionResult, err := client.Create(params)
	if err != nil {
		return fmt.Errorf("failed to create session: %v", err)
	}
	if !sessionResult.Success || sessionResult.Session == nil {
		return fmt.Errorf("failed to create session: %s", sessionResult.ErrorMessage)
	}

	session2 = sessionResult.Session
	fmt.Printf("Session created with ID: %s\n", session2.SessionID)
	fmt.Printf("Session: %+v\n", session2)

	// Wait for mobile simulate to complete
	fmt.Println("Waiting 5 seconds for mobile simulate to complete...")
	time.Sleep(5 * time.Second)

	// Get device model after mobile simulate
	fmt.Println("Getting device model after mobile simulate...")
	result, err := session2.Command.ExecuteCommand("getprop ro.product.model")
	if err != nil {
		return fmt.Errorf("failed to execute command: %v", err)
	}

	productModel := result.Output
	fmt.Printf("Second session device model: %s\n", productModel)

	return nil
}

func main() {
	fmt.Println("=== Mobile Simulate Example ===")
	fmt.Println()

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
	fmt.Println("AgentBay client initialized")

	// Run on first mobile session
	if err := runOnFirstMobileSession(client); err != nil {
		fmt.Printf("Error during first mobile session: %v\n", err)
		os.Exit(1)
	}

	// Delete first session
	fmt.Println("\nDeleting first session...")
	deleteResult, err := session1.Delete()
	if err != nil {
		fmt.Printf("Failed to delete first session: %v\n", err)
		os.Exit(1)
	}
	if !deleteResult.Success {
		fmt.Printf("Failed to delete first session: %s\n", deleteResult.ErrorMessage)
		os.Exit(1)
	}
	fmt.Printf("First session deleted successfully (RequestID: %s)\n", deleteResult.RequestID)

	// Run on second mobile session
	if err := runOnSecondMobileSession(client); err != nil {
		fmt.Printf("Error during second mobile session: %v\n", err)
		os.Exit(1)
	}

	// Delete second session
	fmt.Println("\nDeleting second session...")
	deleteResult, err = session2.Delete()
	if err != nil {
		fmt.Printf("Failed to delete second session: %v\n", err)
		os.Exit(1)
	}
	if !deleteResult.Success {
		fmt.Printf("Failed to delete second session: %s\n", deleteResult.ErrorMessage)
		os.Exit(1)
	}
	fmt.Printf("Second session deleted successfully (RequestID: %s)\n", deleteResult.RequestID)

	fmt.Println("\n=== Example completed successfully ===")
}
