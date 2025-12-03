package main

import (
	"fmt"
	"os"
	"path/filepath"
	"time"

	"github.com/aliyun/wuying-agentbay-sdk/golang/pkg/agentbay"
	"github.com/aliyun/wuying-agentbay-sdk/golang/pkg/agentbay/models"
)

var session *agentbay.Session

func runOnMobileSession(client *agentbay.AgentBay) error {
	fmt.Println("Getting a user specific context...")
	contextResult, err := client.Context.Get("13000000012", true)
	if err != nil {
		return fmt.Errorf("failed to get context: %v", err)
	}
	if !contextResult.Success || contextResult.Context == nil {
		return fmt.Errorf("failed to get context: %s", contextResult.ErrorMessage)
	}

	context := contextResult.Context
	fmt.Printf("context.id = %s, context.name = %s\n", context.ID, context.Name)

	// Create sync policy with white list
	syncPolicy := &agentbay.SyncPolicy{
		BWList: &agentbay.BWList{
			WhiteLists: []*agentbay.WhiteList{
				{
					Path:         "/com.wuying.devinfo",
					ExcludePaths: []string{},
				},
			},
		},
	}

	contextSync := &agentbay.ContextSync{
		ContextID: context.ID,
		Path:      "/data/data",
		Policy:    syncPolicy,
	}

	// Create mobile simulate service and set simulate params
	fmt.Println("Creating mobile simulate service and set simulate params...")
	simulateService, err := agentbay.NewMobileSimulateService(client)
	if err != nil {
		return fmt.Errorf("failed to create mobile simulate service: %v", err)
	}
	simulateService.SetSimulateEnable(true)
	simulateService.SetSimulateMode(models.MobileSimulateModePropertiesOnly)

	fmt.Println("Checking or uploading mobile dev info file...")

	// Check if the mobile dev info file exists in user's specific context
	hasMobileInfo, err := simulateService.HasMobileInfo(contextSync)
	if err != nil {
		return fmt.Errorf("failed to check mobile info: %v", err)
	}
	if !hasMobileInfo {
		// If not, get a mobile dev info file from DumpSDK or real device
		// Get the path to mobile_info_model_a.json
		// Navigate from golang/docs/examples/mobile-use/mobile_simulate_with_ctx to resource/
		mobileInfoFilePath := filepath.Join("..", "..", "..", "..", "..", "resource", "mobile_info_model_a.json")

		// Read the mobile info file
		mobileInfoContent, err := os.ReadFile(mobileInfoFilePath)
		if err != nil {
			return fmt.Errorf("failed to read mobile info file: %v", err)
		}

		uploadResult := simulateService.UploadMobileInfo(string(mobileInfoContent), contextSync)
		if !uploadResult.Success {
			return fmt.Errorf("failed to upload mobile dev info: %s", uploadResult.ErrorMessage)
		}
		fmt.Println("Mobile dev info uploaded successfully")
	} else {
		fmt.Printf("Mobile dev info already exists: %v\n", hasMobileInfo)
	}

	// Create session with mobile simulate configuration and user's specific context
	params := &agentbay.CreateSessionParams{
		ImageId:     "mobile_latest",
		ContextSync: []*agentbay.ContextSync{contextSync},
		ExtraConfigs: &models.ExtraConfigs{
			Mobile: &models.MobileExtraConfig{
				// Set mobile simulate config
				SimulateConfig: simulateService.GetSimulateConfig(),
			},
		},
	}

	fmt.Println("Creating session...")
	sessionResult, err := client.Create(params)
	if err != nil {
		return fmt.Errorf("failed to create session: %v", err)
	}
	if !sessionResult.Success || sessionResult.Session == nil {
		return fmt.Errorf("failed to create session: %s", sessionResult.ErrorMessage)
	}

	session = sessionResult.Session
	fmt.Printf("Session created with ID: %s\n", session.SessionID)
	fmt.Printf("Session: %+v\n", session)

	// Wait for mobile simulate to complete
	fmt.Println("Waiting 5 seconds for mobile simulate to complete...")
	time.Sleep(5 * time.Second)

	// Get device model after mobile simulate
	fmt.Println("Getting device model after mobile simulate...")
	result, err := session.Command.ExecuteCommand("getprop ro.product.model")
	if err != nil {
		return fmt.Errorf("failed to execute command: %v", err)
	}

	productModel := result.Output
	fmt.Printf("Session device model: %s\n", productModel)

	return nil
}

func main() {
	fmt.Println("=== Mobile Simulate with User Specific Context Example ===")
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

	// Run on mobile session
	if err := runOnMobileSession(client); err != nil {
		fmt.Printf("Error during demo: %v\n", err)
		os.Exit(1)
	}

	// Delete session with context sync
	fmt.Println("\nDeleting session...")
	deleteResult, err := client.Delete(session, true)
	if err != nil {
		fmt.Printf("Failed to delete session: %v\n", err)
		os.Exit(1)
	}
	if !deleteResult.Success {
		fmt.Printf("Failed to delete session: %s\n", deleteResult.ErrorMessage)
		os.Exit(1)
	}
	fmt.Printf("Session deleted successfully (RequestID: %s)\n", deleteResult.RequestID)

	fmt.Println("\n=== Example completed successfully ===")
}
