package agentbay_test

import (
	"testing"

	"github.com/aliyun/wuying-agentbay-sdk/golang/pkg/agentbay"
)

// TestRegionIDSupport tests region_id functionality in AgentBay client
func TestRegionIDSupport(t *testing.T) {
	t.Run("NewAgentBayWithRegionID", func(t *testing.T) {
		// Test creating AgentBay client with region_id using WithRegionID option
		client, err := agentbay.NewAgentBay("test-api-key", agentbay.WithRegionID("cn-hangzhou"))
		if err != nil {
			t.Fatalf("Failed to create AgentBay client: %v", err)
		}

		// Verify region_id is set correctly
		if client.RegionID != "cn-hangzhou" {
			t.Errorf("Expected RegionID to be 'cn-hangzhou', got '%s'", client.RegionID)
		}

		// Verify other fields are set correctly
		if client.APIKey != "test-api-key" {
			t.Errorf("Expected APIKey to be 'test-api-key', got '%s'", client.APIKey)
		}

		if client.Context == nil {
			t.Error("Expected Context service to be initialized")
		}
	})

	t.Run("NewAgentBayWithoutRegionID", func(t *testing.T) {
		// Test creating AgentBay client without region_id
		client, err := agentbay.NewAgentBay("test-api-key")
		if err != nil {
			t.Fatalf("Failed to create AgentBay client: %v", err)
		}

		// Verify region_id is empty when not provided
		if client.RegionID != "" {
			t.Errorf("Expected RegionID to be empty, got '%s'", client.RegionID)
		}

		// Verify other fields are set correctly
		if client.APIKey != "test-api-key" {
			t.Errorf("Expected APIKey to be 'test-api-key', got '%s'", client.APIKey)
		}
	})

	t.Run("NewAgentBayWithMultipleOptions", func(t *testing.T) {
		// Test creating AgentBay client with multiple options including region_id
		config := &agentbay.Config{
			Endpoint:  "https://test.endpoint.com",
			TimeoutMs: 60000,
		}

		client, err := agentbay.NewAgentBay("test-api-key",
			agentbay.WithConfig(config),
			agentbay.WithRegionID("cn-beijing"),
			agentbay.WithEnvFile(".env.test"))
		if err != nil {
			t.Fatalf("Failed to create AgentBay client: %v", err)
		}

		// Verify region_id is set correctly
		if client.RegionID != "cn-beijing" {
			t.Errorf("Expected RegionID to be 'cn-beijing', got '%s'", client.RegionID)
		}

		// Verify API key is set correctly
		if client.APIKey != "test-api-key" {
			t.Errorf("Expected APIKey to be 'test-api-key', got '%s'", client.APIKey)
		}
	})

	t.Run("EmptyRegionID", func(t *testing.T) {
		// Test creating AgentBay client with empty region_id
		client, err := agentbay.NewAgentBay("test-api-key", agentbay.WithRegionID(""))
		if err != nil {
			t.Fatalf("Failed to create AgentBay client: %v", err)
		}

		// Verify region_id is empty
		if client.RegionID != "" {
			t.Errorf("Expected RegionID to be empty, got '%s'", client.RegionID)
		}
	})
}