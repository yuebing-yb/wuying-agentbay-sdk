package integration_test

import (
	"os"
	"testing"
	"time"

	"github.com/aliyun/wuying-agentbay-sdk/golang/pkg/agentbay"
	"github.com/aliyun/wuying-agentbay-sdk/golang/pkg/agentbay/agent"
)

func TestMobileAgentStreaming_TypedCallbacks(t *testing.T) {
	apiKey := os.Getenv("AGENTBAY_API_KEY")
	if apiKey == "" {
		t.Skip("AGENTBAY_API_KEY not set")
	}

	client, err := agentbay.NewAgentBay(apiKey, nil)
	if err != nil {
		t.Fatalf("Failed to create AgentBay client: %v", err)
	}

	time.Sleep(3 * time.Second)

	params := agentbay.NewCreateSessionParams().WithImageId("imgc-0ab5takhnmlvhx9gp")
	sessionResult, err := client.Create(params)
	if err != nil {
		t.Fatalf("Failed to create session: %v", err)
	}
	if sessionResult.Session == nil {
		t.Fatal("Session is nil")
	}
	defer func() {
		sessionResult.Session.Delete()
	}()

	t.Logf("Session created: %s", sessionResult.Session.SessionID)

	var reasoningCount, contentCount, toolCallCount, toolResultCount int

	result := sessionResult.Session.Agent.Mobile.ExecuteTaskAndWait(
		"Open Settings app",
		180,
		agent.MobileTaskOptions{
			MaxSteps: 10,
			StreamOptions: agent.StreamOptions{
				OnReasoning: func(evt agent.AgentEvent) {
					reasoningCount++
					t.Logf("[Reasoning] round=%d: %s", evt.Round, truncate(evt.Content, 100))
				},
				OnContent: func(evt agent.AgentEvent) {
					contentCount++
					t.Logf("[Content] round=%d: %s", evt.Round, truncate(evt.Content, 100))
				},
				OnToolCall: func(evt agent.AgentEvent) {
					toolCallCount++
					t.Logf("[ToolCall] round=%d: %s", evt.Round, evt.ToolName)
				},
				OnToolResult: func(evt agent.AgentEvent) {
					toolResultCount++
					t.Logf("[ToolResult] round=%d: %s", evt.Round, evt.ToolName)
				},
			},
		},
	)

	t.Logf("Result: success=%v, status=%s", result.Success, result.TaskStatus)
	t.Logf("Reasoning: %d, Content: %d, ToolCalls: %d, ToolResults: %d",
		reasoningCount, contentCount, toolCallCount, toolResultCount)
}

func truncate(s string, maxLen int) string {
	if len(s) <= maxLen {
		return s
	}
	return s[:maxLen] + "..."
}
