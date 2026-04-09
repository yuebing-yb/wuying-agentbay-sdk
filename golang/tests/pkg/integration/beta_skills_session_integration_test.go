// ci-stable
// Integration tests for session creation with skills loading.
//
// Note: This test calls the real backend. Do not run concurrently.
package integration_test

import (
	"testing"

	"github.com/aliyun/wuying-agentbay-sdk/golang/pkg/agentbay"
	"github.com/aliyun/wuying-agentbay-sdk/golang/tests/pkg/agentbay/testutil"
)

func TestBetaSkillsSession_CreateWithLoadSkillsSucceeds(t *testing.T) {
	apiKey := testutil.GetTestAPIKey(t)
	agentBay, err := agentbay.NewAgentBay(apiKey)
	if err != nil {
		t.Fatalf("Error initializing AgentBay client: %v", err)
	}

	params := agentbay.NewCreateSessionParams().WithLoadSkills(true)
	result, err := agentBay.Create(params)
	if err != nil {
		t.Fatalf("Create failed: %v", err)
	}

	if !result.Success {
		t.Fatalf("Create returned success=false")
	}
	if result.Session == nil {
		t.Fatal("Expected non-nil session")
	}

	session := result.Session
	defer func() {
		_, _ = agentBay.Delete(session)
	}()
}

func TestBetaSkillsSession_CreateWithoutSkillsSucceeds(t *testing.T) {
	apiKey := testutil.GetTestAPIKey(t)
	agentBay, err := agentbay.NewAgentBay(apiKey)
	if err != nil {
		t.Fatalf("Error initializing AgentBay client: %v", err)
	}

	params := agentbay.NewCreateSessionParams()
	result, err := agentBay.Create(params)
	if err != nil {
		t.Fatalf("Create failed: %v", err)
	}

	if !result.Success {
		t.Fatalf("Create returned success=false")
	}
	if result.Session == nil {
		t.Fatal("Expected non-nil session")
	}

	session := result.Session
	defer func() {
		_, _ = agentBay.Delete(session)
	}()
}
