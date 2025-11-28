package integration

import (
	"os"
	"path/filepath"
	"strings"
	"testing"
	"time"

	"github.com/aliyun/wuying-agentbay-sdk/golang/pkg/agentbay"
	"github.com/aliyun/wuying-agentbay-sdk/golang/pkg/agentbay/models"
)

const (
	MobileInfoModelA = "SM-A505F"
	MobileInfoModelB = "moto g stylus 5G - 2024"
)

var mobileSimPersistenceContextID string

// TestMobileSimulateForModelAIntegration test mobile simulate feature by model_a prop file
// and check product model is "SM-A505F" after session created
func TestMobileSimulateForModelAIntegration(t *testing.T) {
	if testing.Short() {
		t.Skip("Skipping integration test in short mode")
	}

	apiKey := os.Getenv("AGENTBAY_API_KEY")
	if apiKey == "" {
		t.Skip("AGENTBAY_API_KEY not set, skipping integration test")
	}

	client, err := agentbay.NewAgentBay(apiKey, nil)
	if err != nil {
		t.Fatalf("Failed to create AgentBay client: %v", err)
	}

	t.Log("Upload mobile dev info file for model A...")
	mobileInfoFilePath := filepath.Join("..", "..", "..", "..", "resource", "mobile_info_model_a.json")
	mobileInfoContent, err := os.ReadFile(mobileInfoFilePath)
	if err != nil {
		t.Fatalf("Failed to read mobile info file: %v", err)
	}

	// Create mobile simulate service and set simulate params
	t.Log("Creating mobile simulate service and set simulate params...")
	simulateService, err := agentbay.NewMobileSimulateService(client)
	if err != nil {
		t.Fatalf("Failed to create mobile simulate service: %v", err)
	}
	simulateService.SetSimulateEnable(true)
	simulateService.SetSimulateMode(models.MobileSimulateModePropertiesOnly)

	uploadResult := simulateService.UploadMobileInfo(string(mobileInfoContent), nil)
	if !uploadResult.Success {
		t.Fatalf("Failed to upload mobile dev info file: %s", uploadResult.ErrorMessage)
	}
	if uploadResult.MobileSimulateContextID == "" {
		t.Fatal("Expected non-empty MobileSimulateContextID")
	}
	mobileSimContextID := uploadResult.MobileSimulateContextID
	mobileSimPersistenceContextID = mobileSimContextID
	t.Logf("Mobile dev info uploaded successfully: %s", mobileSimContextID)

	params := agentbay.NewCreateSessionParams().
		WithImageId("mobile_latest").
		WithExtraConfigs(&models.ExtraConfigs{
			Mobile: &models.MobileExtraConfig{
				SimulateConfig: simulateService.GetSimulateConfig(),
			},
		})

	result, err := client.Create(params)
	if err != nil {
		t.Fatalf("Failed to create session: %v", err)
	}
	if !result.Success {
		t.Fatal("Create session returned Success=false")
	}
	if result.Session == nil {
		t.Fatal("Session is nil")
	}
	session := result.Session
	t.Logf("Session created successfully: %s", session.GetSessionId())

	defer func() {
		t.Log("Deleting session...")
		deleteResult, err := client.Delete(session)
		if err != nil {
			t.Errorf("Failed to delete session: %v", err)
		}
		if deleteResult != nil && deleteResult.Success {
			t.Logf("Session deleted successfully (RequestID: %s)", deleteResult.RequestID)
		}
	}()

	time.Sleep(5 * time.Second)
	t.Log("Getting device model after mobile simulate for model A...")
	cmdResult, err := session.GetCommand().ExecuteCommand("getprop ro.product.model")
	if err != nil {
		t.Fatalf("Failed to execute command: %v", err)
	}
	if cmdResult == nil {
		t.Fatal("Command result is nil")
	}

	modelAProductModel := strings.TrimSpace(cmdResult.Output)
	t.Logf("Simulated model A mobile product model: %s", modelAProductModel)
	if modelAProductModel != MobileInfoModelA {
		t.Errorf("Expected device model %s, got %s", MobileInfoModelA, modelAProductModel)
	}
}

// TestMobileSimulateForModelAIntegration test mobile simulate feature by model_b prop file
// and check product model is "moto g stylus 5G - 2024" after session created
func TestMobileSimulateForModelBIntegration(t *testing.T) {
	if testing.Short() {
		t.Skip("Skipping integration test in short mode")
	}

	apiKey := os.Getenv("AGENTBAY_API_KEY")
	if apiKey == "" {
		t.Skip("AGENTBAY_API_KEY not set, skipping integration test")
	}

	client, err := agentbay.NewAgentBay(apiKey, nil)
	if err != nil {
		t.Fatalf("Failed to create AgentBay client: %v", err)
	}

	t.Log("Upload mobile dev info file for model B...")
	mobileInfoFilePath := filepath.Join("..", "..", "..", "..", "resource", "mobile_info_model_b.json")
	mobileInfoContent, err := os.ReadFile(mobileInfoFilePath)
	if err != nil {
		t.Fatalf("Failed to read mobile info file: %v", err)
	}

	// Create mobile simulate service and set simulate params
	t.Log("Creating mobile simulate service and set simulate params...")
	simulateService, err := agentbay.NewMobileSimulateService(client)
	if err != nil {
		t.Fatalf("Failed to create mobile simulate service: %v", err)
	}
	simulateService.SetSimulateEnable(true)
	simulateService.SetSimulateMode(models.MobileSimulateModePropertiesOnly)

	uploadResult := simulateService.UploadMobileInfo(string(mobileInfoContent), nil)
	if !uploadResult.Success {
		t.Fatalf("Failed to upload mobile dev info file: %s", uploadResult.ErrorMessage)
	}
	if uploadResult.MobileSimulateContextID == "" {
		t.Fatal("Expected non-empty MobileSimulateContextID")
	}
	mobileSimContextID := uploadResult.MobileSimulateContextID
	t.Logf("Mobile dev info uploaded successfully: %s", mobileSimContextID)

	params := agentbay.NewCreateSessionParams().
		WithImageId("mobile_latest").
		WithExtraConfigs(&models.ExtraConfigs{
			Mobile: &models.MobileExtraConfig{
				SimulateConfig: simulateService.GetSimulateConfig(),
			},
		})

	result, err := client.Create(params)
	if err != nil {
		t.Fatalf("Failed to create session: %v", err)
	}
	if !result.Success {
		t.Fatal("Create session returned Success=false")
	}
	if result.Session == nil {
		t.Fatal("Session is nil")
	}
	session := result.Session
	t.Logf("Session created successfully: %s", session.GetSessionId())

	defer func() {
		t.Log("Deleting session...")
		deleteResult, err := client.Delete(session)
		if err != nil {
			t.Errorf("Failed to delete session: %v", err)
		}
		if deleteResult != nil && deleteResult.Success {
			t.Logf("Session deleted successfully (RequestID: %s)", deleteResult.RequestID)
		}
	}()

	time.Sleep(5 * time.Second)
	t.Log("Getting device model after mobile simulate for model B...")
	cmdResult, err := session.GetCommand().ExecuteCommand("getprop ro.product.model")
	if err != nil {
		t.Fatalf("Failed to execute command: %v", err)
	}
	if cmdResult == nil {
		t.Fatal("Command result is nil")
	}

	modelBProductModel := strings.TrimSpace(cmdResult.Output)
	t.Logf("Simulated model B mobile product model: %s", modelBProductModel)
	if modelBProductModel != MobileInfoModelB {
		t.Errorf("Expected device model %s, got %s", MobileInfoModelB, modelBProductModel)
	}
}

// TestMobileSimulateForModelAIntegration test mobile simulate persistence feature
// by using a exist mobile simulate context id, and check product model is
// "SM-A505F" after session created
func TestMobileSimulatePersistenceIntegration(t *testing.T) {
	if testing.Short() {
		t.Skip("Skipping integration test in short mode")
	}

	apiKey := os.Getenv("AGENTBAY_API_KEY")
	if apiKey == "" {
		t.Skip("AGENTBAY_API_KEY not set, skipping integration test")
	}

	client, err := agentbay.NewAgentBay(apiKey, nil)
	if err != nil {
		t.Fatalf("Failed to create AgentBay client: %v", err)
	}

	t.Logf("Using a persistent mobild simulate context id: %s", mobileSimPersistenceContextID)

	// Create mobile simulate service and set simulate params
	t.Log("Creating mobile simulate service and set simulate params...")
	simulateService, err := agentbay.NewMobileSimulateService(client)
	if err != nil {
		t.Fatalf("Failed to create mobile simulate service: %v", err)
	}
	simulateService.SetSimulateEnable(true)
	simulateService.SetSimulateMode(models.MobileSimulateModePropertiesOnly)
	simulateService.SetSimulateContextID(mobileSimPersistenceContextID)

	params := agentbay.NewCreateSessionParams().
		WithImageId("mobile_latest").
		WithExtraConfigs(&models.ExtraConfigs{
			Mobile: &models.MobileExtraConfig{
				SimulateConfig: simulateService.GetSimulateConfig(),
			},
		})

	result, err := client.Create(params)
	if err != nil {
		t.Fatalf("Failed to create session: %v", err)
	}
	if !result.Success {
		t.Fatal("Create session returned Success=false")
	}
	if result.Session == nil {
		t.Fatal("Session is nil")
	}
	session := result.Session
	t.Logf("Session created successfully: %s", session.GetSessionId())

	defer func() {
		t.Log("Deleting session...")
		deleteResult, err := client.Delete(session)
		if err != nil {
			t.Errorf("Failed to delete session: %v", err)
		}
		if deleteResult != nil && deleteResult.Success {
			t.Logf("Session deleted successfully (RequestID: %s)", deleteResult.RequestID)
		}
	}()

	time.Sleep(5 * time.Second)
	t.Log("Getting device model after mobile simulate with user context...")
	cmdResult, err := session.GetCommand().ExecuteCommand("getprop ro.product.model")
	if err != nil {
		t.Fatalf("Failed to execute command: %v", err)
	}
	if cmdResult == nil {
		t.Fatal("Command result is nil")
	}

	productModel := strings.TrimSpace(cmdResult.Output)
	t.Logf("Persistence simulated mobile product model: %s", productModel)
	if productModel != MobileInfoModelA {
		t.Errorf("Expected device model %s, got %s", MobileInfoModelA, productModel)
	}
}
