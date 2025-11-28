package agentbay_test

import (
	"testing"

	"github.com/aliyun/wuying-agentbay-sdk/golang/pkg/agentbay"
	"github.com/aliyun/wuying-agentbay-sdk/golang/pkg/agentbay/models"
)

// TestMobileSimulateUploadResult tests the MobileSimulateUploadResult struct
func TestMobileSimulateUploadResult(t *testing.T) {
	t.Run("SuccessResult", func(t *testing.T) {
		result := &agentbay.MobileSimulateUploadResult{
			Success:                 true,
			MobileSimulateContextID: "context-123",
		}
		if !result.Success {
			t.Error("Expected Success to be true")
		}
		if result.MobileSimulateContextID != "context-123" {
			t.Errorf("Expected MobileSimulateContextID=context-123, got %s", result.MobileSimulateContextID)
		}
		if result.ErrorMessage != "" {
			t.Errorf("Expected empty ErrorMessage, got %s", result.ErrorMessage)
		}
	})

	t.Run("FailureResult", func(t *testing.T) {
		result := &agentbay.MobileSimulateUploadResult{
			Success:      false,
			ErrorMessage: "Upload failed",
		}
		if result.Success {
			t.Error("Expected Success to be false")
		}
		if result.MobileSimulateContextID != "" {
			t.Errorf("Expected empty MobileSimulateContextID, got %s", result.MobileSimulateContextID)
		}
		if result.ErrorMessage != "Upload failed" {
			t.Errorf("Expected ErrorMessage='Upload failed', got %s", result.ErrorMessage)
		}
	})
}

// TestMobileSimulateServiceInitialization tests the NewMobileSimulateService function
func TestMobileSimulateServiceInitialization(t *testing.T) {
	t.Run("ValidInitialization", func(t *testing.T) {
		agentBayClient := &agentbay.AgentBay{
			Context: &agentbay.ContextService{},
		}
		service, err := agentbay.NewMobileSimulateService(agentBayClient)
		if err != nil {
			t.Fatalf("Expected no error, got %v", err)
		}
		if service == nil {
			t.Fatal("Expected non-nil service")
		}
		// Check default values
		if service.GetSimulateEnable() {
			t.Error("Expected SimulateEnable to be false by default")
		}
		if service.GetSimulateMode() != models.MobileSimulateModePropertiesOnly {
			t.Errorf("Expected default SimulateMode to be PropertiesOnly, got %s", service.GetSimulateMode())
		}
	})

	t.Run("NilAgentBay", func(t *testing.T) {
		service, err := agentbay.NewMobileSimulateService(nil)
		if err == nil {
			t.Error("Expected error for nil AgentBay")
		}
		if service != nil {
			t.Error("Expected nil service")
		}
		if err != nil && err.Error() != "agentBay is required" {
			t.Errorf("Expected 'agentBay is required' error, got %v", err)
		}
	})

	t.Run("NilContext", func(t *testing.T) {
		agentBayClient := &agentbay.AgentBay{
			Context: nil,
		}
		service, err := agentbay.NewMobileSimulateService(agentBayClient)
		if err == nil {
			t.Error("Expected error for nil Context")
		}
		if service != nil {
			t.Error("Expected nil service")
		}
		if err != nil && err.Error() != "agentBay.Context is required" {
			t.Errorf("Expected 'agentBay.Context is required' error, got %v", err)
		}
	})
}

// TestSetAndGetSimulateEnable tests the SetSimulateEnable and GetSimulateEnable methods
func TestSetAndGetSimulateEnable(t *testing.T) {
	agentBayClient := &agentbay.AgentBay{
		Context: &agentbay.ContextService{},
	}
	service, err := agentbay.NewMobileSimulateService(agentBayClient)
	if err != nil {
		t.Fatalf("Failed to create service: %v", err)
	}

	t.Run("DefaultValue", func(t *testing.T) {
		if service.GetSimulateEnable() {
			t.Error("Expected default SimulateEnable to be false")
		}
	})

	t.Run("SetEnableTrue", func(t *testing.T) {
		service.SetSimulateEnable(true)
		if !service.GetSimulateEnable() {
			t.Error("Expected SimulateEnable to be true")
		}
	})

	t.Run("SetEnableFalse", func(t *testing.T) {
		service.SetSimulateEnable(false)
		if service.GetSimulateEnable() {
			t.Error("Expected SimulateEnable to be false")
		}
	})
}

// TestSetAndGetSimulateMode tests the SetSimulateMode and GetSimulateMode methods
func TestSetAndGetSimulateMode(t *testing.T) {
	agentBayClient := &agentbay.AgentBay{
		Context: &agentbay.ContextService{},
	}
	service, err := agentbay.NewMobileSimulateService(agentBayClient)
	if err != nil {
		t.Fatalf("Failed to create service: %v", err)
	}

	t.Run("DefaultMode", func(t *testing.T) {
		if service.GetSimulateMode() != models.MobileSimulateModePropertiesOnly {
			t.Errorf("Expected default SimulateMode to be PropertiesOnly, got %s", service.GetSimulateMode())
		}
	})

	t.Run("SetModeAll", func(t *testing.T) {
		service.SetSimulateMode(models.MobileSimulateModeAll)
		if service.GetSimulateMode() != models.MobileSimulateModeAll {
			t.Errorf("Expected SimulateMode=All, got %s", service.GetSimulateMode())
		}
	})

	t.Run("SetModeSensorsOnly", func(t *testing.T) {
		service.SetSimulateMode(models.MobileSimulateModeSensorsOnly)
		if service.GetSimulateMode() != models.MobileSimulateModeSensorsOnly {
			t.Errorf("Expected SimulateMode=SensorsOnly, got %s", service.GetSimulateMode())
		}
	})

	t.Run("SetModePackagesOnly", func(t *testing.T) {
		service.SetSimulateMode(models.MobileSimulateModePackagesOnly)
		if service.GetSimulateMode() != models.MobileSimulateModePackagesOnly {
			t.Errorf("Expected SimulateMode=PackagesOnly, got %s", service.GetSimulateMode())
		}
	})

	t.Run("SetModeServicesOnly", func(t *testing.T) {
		service.SetSimulateMode(models.MobileSimulateModeServicesOnly)
		if service.GetSimulateMode() != models.MobileSimulateModeServicesOnly {
			t.Errorf("Expected SimulateMode=ServicesOnly, got %s", service.GetSimulateMode())
		}
	})
}

// TestSetAndGetSimulateContextID tests the SetSimulateContextID and GetSimulateContextID methods
func TestSetAndGetSimulateContextID(t *testing.T) {
	agentBayClient := &agentbay.AgentBay{
		Context: &agentbay.ContextService{},
	}
	service, err := agentbay.NewMobileSimulateService(agentBayClient)
	if err != nil {
		t.Fatalf("Failed to create service: %v", err)
	}

	t.Run("DefaultContextID", func(t *testing.T) {
		if service.GetSimulateContextID() != "" {
			t.Errorf("Expected empty default ContextID, got %s", service.GetSimulateContextID())
		}
	})

	t.Run("SetContextID", func(t *testing.T) {
		contextID := "test-context-123"
		service.SetSimulateContextID(contextID)
		if service.GetSimulateContextID() != contextID {
			t.Errorf("Expected ContextID=%s, got %s", contextID, service.GetSimulateContextID())
		}
	})

	t.Run("SetEmptyContextID", func(t *testing.T) {
		service.SetSimulateContextID("")
		if service.GetSimulateContextID() != "" {
			t.Errorf("Expected empty ContextID, got %s", service.GetSimulateContextID())
		}
	})
}

// TestGetSimulateConfig tests the GetSimulateConfig method
func TestGetSimulateConfig(t *testing.T) {
	agentBayClient := &agentbay.AgentBay{
		Context: &agentbay.ContextService{},
	}
	service, err := agentbay.NewMobileSimulateService(agentBayClient)
	if err != nil {
		t.Fatalf("Failed to create service: %v", err)
	}

	t.Run("DefaultConfig", func(t *testing.T) {
		config := service.GetSimulateConfig()
		if config == nil {
			t.Fatal("Expected non-nil config")
		}
		if config.Simulate {
			t.Error("Expected Simulate to be false by default")
		}
		if config.SimulateMode != models.MobileSimulateModePropertiesOnly {
			t.Errorf("Expected default SimulateMode to be PropertiesOnly, got %s", config.SimulateMode)
		}
	})

	t.Run("ConfigWithInternalContext", func(t *testing.T) {
		service.SetSimulateEnable(true)
		service.SetSimulateMode(models.MobileSimulateModeAll)
		service.SetSimulateContextID("internal-ctx-123")

		config := service.GetSimulateConfig()
		if config == nil {
			t.Fatal("Expected non-nil config")
		}
		if !config.Simulate {
			t.Error("Expected Simulate to be true")
		}
		if config.SimulateMode != models.MobileSimulateModeAll {
			t.Errorf("Expected SimulateMode=All, got %s", config.SimulateMode)
		}
		if config.SimulatedContextID != "internal-ctx-123" {
			t.Errorf("Expected SimulatedContextID=internal-ctx-123, got %s", config.SimulatedContextID)
		}
		if config.SimulatePath == "" {
			t.Error("Expected non-empty SimulatePath")
		}
	})

	t.Run("ConfigWithAllModes", func(t *testing.T) {
		modes := []models.MobileSimulateMode{
			models.MobileSimulateModePropertiesOnly,
			models.MobileSimulateModeSensorsOnly,
			models.MobileSimulateModePackagesOnly,
			models.MobileSimulateModeServicesOnly,
			models.MobileSimulateModeAll,
		}

		for _, mode := range modes {
			service.SetSimulateMode(mode)
			config := service.GetSimulateConfig()
			if config.SimulateMode != mode {
				t.Errorf("Expected SimulateMode=%s, got %s", mode, config.SimulateMode)
			}
		}
	})
}

// TestMobileSimulateConfig tests the MobileSimulateConfig model
func TestMobileSimulateConfig(t *testing.T) {
	t.Run("DefaultConfig", func(t *testing.T) {
		config := &models.MobileSimulateConfig{}
		if config.Simulate {
			t.Error("Expected Simulate to be false by default")
		}
		if config.SimulateMode != "" {
			t.Errorf("Expected empty SimulateMode, got %s", config.SimulateMode)
		}
		if config.SimulatedContextID != "" {
			t.Errorf("Expected empty SimulatedContextID, got %s", config.SimulatedContextID)
		}
		if config.SimulatePath != "" {
			t.Errorf("Expected empty SimulatePath, got %s", config.SimulatePath)
		}
	})

	t.Run("ConfigWithAllFields", func(t *testing.T) {
		config := &models.MobileSimulateConfig{
			Simulate:           true,
			SimulatePath:       "/data/agentbay_mobile_info",
			SimulateMode:       models.MobileSimulateModeAll,
			SimulatedContextID: "ctx-123",
		}
		if !config.Simulate {
			t.Error("Expected Simulate to be true")
		}
		if config.SimulatePath != "/data/agentbay_mobile_info" {
			t.Errorf("Expected SimulatePath=/data/agentbay_mobile_info, got %s", config.SimulatePath)
		}
		if config.SimulateMode != models.MobileSimulateModeAll {
			t.Errorf("Expected SimulateMode=All, got %s", config.SimulateMode)
		}
		if config.SimulatedContextID != "ctx-123" {
			t.Errorf("Expected SimulatedContextID=ctx-123, got %s", config.SimulatedContextID)
		}
	})

	t.Run("AllSimulateModes", func(t *testing.T) {
		modes := []models.MobileSimulateMode{
			models.MobileSimulateModePropertiesOnly,
			models.MobileSimulateModeSensorsOnly,
			models.MobileSimulateModePackagesOnly,
			models.MobileSimulateModeServicesOnly,
			models.MobileSimulateModeAll,
		}

		expectedValues := []string{
			"PropertiesOnly",
			"SensorsOnly",
			"PackagesOnly",
			"ServicesOnly",
			"All",
		}

		for i, mode := range modes {
			if string(mode) != expectedValues[i] {
				t.Errorf("Expected mode %s, got %s", expectedValues[i], string(mode))
			}
		}
	})
}

// TestMobileExtraConfigWithSimulate tests MobileExtraConfig with SimulateConfig
func TestMobileExtraConfigWithSimulate(t *testing.T) {
	t.Run("WithSimulateConfig", func(t *testing.T) {
		simulateConfig := &models.MobileSimulateConfig{
			Simulate:           true,
			SimulateMode:       models.MobileSimulateModeAll,
			SimulatedContextID: "ctx-456",
			SimulatePath:       "/data/agentbay_mobile_info",
		}

		mobileConfig := &models.MobileExtraConfig{
			LockResolution: true,
			SimulateConfig: simulateConfig,
		}

		if mobileConfig.SimulateConfig == nil {
			t.Fatal("Expected non-nil SimulateConfig")
		}
		if !mobileConfig.SimulateConfig.Simulate {
			t.Error("Expected Simulate to be true")
		}
		if mobileConfig.SimulateConfig.SimulateMode != models.MobileSimulateModeAll {
			t.Errorf("Expected SimulateMode=All, got %s", mobileConfig.SimulateConfig.SimulateMode)
		}
		if mobileConfig.SimulateConfig.SimulatedContextID != "ctx-456" {
			t.Errorf("Expected SimulatedContextID=ctx-456, got %s", mobileConfig.SimulateConfig.SimulatedContextID)
		}
	})

	t.Run("WithoutSimulateConfig", func(t *testing.T) {
		mobileConfig := &models.MobileExtraConfig{
			LockResolution: true,
		}

		if mobileConfig.SimulateConfig != nil {
			t.Error("Expected nil SimulateConfig")
		}
	})
}

// TestMobileSimulateConstants tests the mobile simulate constants
func TestMobileSimulateConstants(t *testing.T) {
	t.Run("PathConstants", func(t *testing.T) {
		// Check that constants are defined (values from config.go)
		if agentbay.MobileInfoSubPath != "/agentbay_mobile_info/" {
			t.Errorf("Expected MobileInfoSubPath=/agentbay_mobile_info/, got %s", agentbay.MobileInfoSubPath)
		}
		if agentbay.MobileInfoFileName != "dev_info.json" {
			t.Errorf("Expected MobileInfoFileName=dev_info.json, got %s", agentbay.MobileInfoFileName)
		}
		if agentbay.MobileInfoDefaultPath != "/data/agentbay_mobile_info" {
			t.Errorf("Expected MobileInfoDefaultPath=/data/agentbay_mobile_info, got %s", agentbay.MobileInfoDefaultPath)
		}
	})
}

// TestUploadMobileInfoValidation tests the UploadMobileInfo validation
func TestUploadMobileInfoValidation(t *testing.T) {
	agentBayClient := &agentbay.AgentBay{
		Context: &agentbay.ContextService{},
	}
	service, err := agentbay.NewMobileSimulateService(agentBayClient)
	if err != nil {
		t.Fatalf("Failed to create service: %v", err)
	}

	t.Run("EmptyContent", func(t *testing.T) {
		result := service.UploadMobileInfo("", nil)
		if result.Success {
			t.Error("Expected upload to fail with empty content")
		}
		if result.ErrorMessage == "" {
			t.Error("Expected error message")
		}
		if result.ErrorMessage != "mobileDevInfoContent is required" {
			t.Errorf("Expected 'mobileDevInfoContent is required', got %s", result.ErrorMessage)
		}
	})

	t.Run("InvalidJSON", func(t *testing.T) {
		result := service.UploadMobileInfo("not a json", nil)
		if result.Success {
			t.Error("Expected upload to fail with invalid JSON")
		}
		if result.ErrorMessage == "" {
			t.Error("Expected error message")
		}
		if !contains(result.ErrorMessage, "not a valid JSON string") {
			t.Errorf("Expected error message to contain 'not a valid JSON string', got %s", result.ErrorMessage)
		}
	})

	t.Run("MissingContextIDInContextSync", func(t *testing.T) {
		contextSync := &agentbay.ContextSync{
			ContextID: "",
			Path:      "/data",
		}
		result := service.UploadMobileInfo(`{"test":"data"}`, contextSync)
		if result.Success {
			t.Error("Expected upload to fail with empty ContextID")
		}
		if result.ErrorMessage != "contextSync.ContextID is required" {
			t.Errorf("Expected 'contextSync.ContextID is required', got %s", result.ErrorMessage)
		}
	})
}

// TestHasMobileInfoValidation tests the HasMobileInfo validation
func TestHasMobileInfoValidation(t *testing.T) {
	agentBayClient := &agentbay.AgentBay{
		Context: &agentbay.ContextService{},
	}
	service, err := agentbay.NewMobileSimulateService(agentBayClient)
	if err != nil {
		t.Fatalf("Failed to create service: %v", err)
	}

	t.Run("NilContextSync", func(t *testing.T) {
		_, err := service.HasMobileInfo(nil)
		if err == nil {
			t.Error("Expected error for nil ContextSync")
		}
		if err.Error() != "contextSync is required" {
			t.Errorf("Expected 'contextSync is required', got %v", err)
		}
	})

	t.Run("EmptyContextID", func(t *testing.T) {
		contextSync := &agentbay.ContextSync{
			ContextID: "",
			Path:      "/data",
		}
		_, err := service.HasMobileInfo(contextSync)
		if err == nil {
			t.Error("Expected error for empty ContextID")
		}
		if err.Error() != "contextSync.ContextID is required" {
			t.Errorf("Expected 'contextSync.ContextID is required', got %v", err)
		}
	})

	t.Run("EmptyPath", func(t *testing.T) {
		contextSync := &agentbay.ContextSync{
			ContextID: "ctx-123",
			Path:      "",
		}
		_, err := service.HasMobileInfo(contextSync)
		if err == nil {
			t.Error("Expected error for empty Path")
		}
		if err.Error() != "contextSync.Path is required" {
			t.Errorf("Expected 'contextSync.Path is required', got %v", err)
		}
	})
}

// Helper function to check if a string contains a substring
func contains(s, substr string) bool {
	return len(s) >= len(substr) && (s == substr || len(substr) == 0 ||
		(len(s) > 0 && len(substr) > 0 && findSubstring(s, substr)))
}

func findSubstring(s, substr string) bool {
	for i := 0; i <= len(s)-len(substr); i++ {
		if s[i:i+len(substr)] == substr {
			return true
		}
	}
	return false
}
