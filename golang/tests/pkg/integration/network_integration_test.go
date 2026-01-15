package integration_test

import (
	"testing"

	"github.com/aliyun/wuying-agentbay-sdk/golang/pkg/agentbay"
	"github.com/aliyun/wuying-agentbay-sdk/golang/tests/pkg/agentbay/testutil"
)

func TestNetworkCreateDescribeAndBindSession(t *testing.T) {
	apiKey := testutil.GetTestAPIKey(t)

	client, err := agentbay.NewAgentBay(apiKey)
	if err != nil {
		t.Fatalf("Error initializing AgentBay client: %v", err)
	}

	if client.BetaNetwork == nil {
		t.Fatalf("client.BetaNetwork is nil")
	}

	networkResult, err := client.BetaNetwork.BetaGetNetworkBindToken("")
	if err != nil {
		t.Fatalf("BetaGetNetworkBindToken failed: %v", err)
	}
	if !networkResult.Success {
		t.Fatalf("BetaGetNetworkBindToken returned success=false: %s", networkResult.ErrorMessage)
	}
	if networkResult.NetworkId == "" {
		t.Fatalf("expected non-empty networkId")
	}
	if networkResult.NetworkToken == "" {
		t.Fatalf("expected non-empty networkToken")
	}
}
