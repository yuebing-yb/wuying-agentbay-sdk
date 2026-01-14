package integration_test

import (
	"strings"
	"testing"

	"github.com/aliyun/wuying-agentbay-sdk/golang/pkg/agentbay"
	"github.com/aliyun/wuying-agentbay-sdk/golang/tests/pkg/agentbay/testutil"
)

// TestLinkUrlSessionMcpToolsAndCallTool verifies that when CreateSession returns LinkUrl,
// the SDK can expose LinkUrl/Token, and call tools through the LinkUrl route.
func TestLinkUrlSessionMcpToolsAndCallTool(t *testing.T) {
	apiKey := testutil.GetTestAPIKey(t)

	client, err := agentbay.NewAgentBay(apiKey)
	if err != nil {
		t.Fatalf("Error initializing AgentBay client: %v", err)
	}

	params := agentbay.NewCreateSessionParams().
		WithImageId("imgc-0ab5takhjgjky7htu").
		WithLabels(map[string]string{
			"test-type": "link-url-integration",
		})

	createResult, err := client.Create(params)
	if err != nil {
		t.Fatalf("Error creating session: %v", err)
	}
	session := createResult.Session

	defer func() {
		_, _ = client.Delete(session)
	}()

	if session.GetToken() == "" || session.GetLinkUrl() == "" {
		t.Skip("LinkUrl/token not provided by CreateSession response in this environment")
	}

	if session.Command == nil {
		t.Fatalf("session.Command is nil")
	}

	cmdResult, err := session.Command.ExecuteCommand("echo link-url-route-ok")
	if err != nil {
		t.Fatalf("ExecuteCommand failed: %v", err)
	}
	if !strings.Contains(cmdResult.Output, "link-url-route-ok") {
		t.Fatalf("unexpected command output: %q", cmdResult.Output)
	}

	direct, err := session.CallMcpTool("shell", map[string]interface{}{
		"command": "echo direct-link-url-route-ok",
	}, "wuying_shell")
	if err != nil {
		t.Fatalf("CallMcpTool failed: %v", err)
	}
	if !direct.Success || !strings.Contains(direct.Data, "direct-link-url-route-ok") {
		t.Fatalf("unexpected direct tool result: success=%v data=%q err=%q", direct.Success, direct.Data, direct.ErrorMessage)
	}
}

