// ci-stable
// Integration tests for BetaSkills.GetMetadata() via GetSkillMetaData POP action.
//
// Note: This test calls the real backend. Do not run concurrently.
package integration_test

import (
	"testing"

	"github.com/aliyun/wuying-agentbay-sdk/golang/pkg/agentbay"
	"github.com/aliyun/wuying-agentbay-sdk/golang/tests/pkg/agentbay/testutil"
)

func TestBetaSkillsGetMetadata_ReturnsSkillsRootPathAndSkills(t *testing.T) {
	apiKey := testutil.GetTestAPIKey(t)
	agentBay, err := agentbay.NewAgentBay(apiKey)
	if err != nil {
		t.Fatalf("Error initializing AgentBay client: %v", err)
	}

	result, err := agentBay.BetaSkills.GetMetadata()
	if err != nil {
		t.Fatalf("GetMetadata failed: %v", err)
	}

	if result == nil {
		t.Fatal("Expected non-nil result")
	}
	if len(result.SkillsRootPath) == 0 {
		t.Error("Expected non-empty skillsRootPath")
	}
	if result.Skills == nil {
		t.Error("Expected non-nil skills slice")
	}
}

func TestBetaSkillsGetMetadata_WithSkillNamesFilter(t *testing.T) {
	apiKey := testutil.GetTestAPIKey(t)
	agentBay, err := agentbay.NewAgentBay(apiKey)
	if err != nil {
		t.Fatalf("Error initializing AgentBay client: %v", err)
	}

	result, err := agentBay.BetaSkills.GetMetadata(agentbay.GetMetadataOptions{
		SkillNames: []string{"5kvAvffm"},
	})
	if err != nil {
		t.Fatalf("GetMetadata with skillNames failed: %v", err)
	}

	if result == nil {
		t.Fatal("Expected non-nil result")
	}
	if result.Skills == nil {
		t.Error("Expected non-nil skills slice")
	}
	if len(result.SkillsRootPath) == 0 {
		t.Error("Expected non-empty skillsRootPath")
	}
}

func TestBetaSkillsGetMetadata_WithImageId(t *testing.T) {
	apiKey := testutil.GetTestAPIKey(t)
	agentBay, err := agentbay.NewAgentBay(apiKey)
	if err != nil {
		t.Fatalf("Error initializing AgentBay client: %v", err)
	}

	result, err := agentBay.BetaSkills.GetMetadata(agentbay.GetMetadataOptions{
		ImageID: "linux_latest",
	})
	if err != nil {
		t.Fatalf("GetMetadata with imageId failed: %v", err)
	}

	if result == nil {
		t.Fatal("Expected non-nil result")
	}
	if len(result.SkillsRootPath) == 0 {
		t.Error("Expected non-empty skillsRootPath")
	}
}
