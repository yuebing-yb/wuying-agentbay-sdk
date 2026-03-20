package agentbay_test

import (
	"testing"

	"github.com/aliyun/wuying-agentbay-sdk/golang/pkg/agentbay/agent"
)

func TestAgentEvent_Fields(t *testing.T) {
	evt := agent.AgentEvent{
		Type:    "reasoning",
		Seq:     1,
		Round:   1,
		Content: "thinking...",
	}
	if evt.Type != "reasoning" {
		t.Errorf("expected type 'reasoning', got '%s'", evt.Type)
	}
	if evt.Seq != 1 {
		t.Errorf("expected seq 1, got %d", evt.Seq)
	}
	if evt.Content != "thinking..." {
		t.Errorf("expected content 'thinking...', got '%s'", evt.Content)
	}

	toolEvt := agent.AgentEvent{
		Type:       "tool_call",
		Seq:        2,
		Round:      1,
		ToolCallID: "call_001",
		ToolName:   "click",
		Args:       map[string]interface{}{"x": 100.0},
	}
	if toolEvt.ToolName != "click" {
		t.Errorf("expected tool name 'click', got '%s'", toolEvt.ToolName)
	}
	if toolEvt.Args["x"] != 100.0 {
		t.Errorf("expected args x=100, got %v", toolEvt.Args["x"])
	}

	errEvt := agent.AgentEvent{
		Type:  "error",
		Seq:   3,
		Round: 1,
		Error: map[string]interface{}{"message": "something went wrong"},
	}
	if errEvt.Error["message"] != "something went wrong" {
		t.Errorf("expected error message 'something went wrong', got %v", errEvt.Error["message"])
	}
}

func TestStreamOptions_OnError(t *testing.T) {
	opts := agent.StreamOptions{
		OnError: func(e agent.AgentEvent) {},
	}
	if opts.OnError == nil {
		t.Error("expected OnError to be set")
	}
}

func TestMobileTaskOptions_Defaults(t *testing.T) {
	opts := agent.MobileTaskOptions{}
	if opts.MaxSteps != 0 {
		t.Errorf("expected default MaxSteps 0, got %d", opts.MaxSteps)
	}
	if opts.OnReasoning != nil {
		t.Error("expected OnReasoning to be nil by default")
	}
	if opts.OnCallForUser != nil {
		t.Error("expected OnCallForUser to be nil by default")
	}
}

func TestMobileTaskOptions_WithCallbacks(t *testing.T) {
	called := false
	opts := agent.MobileTaskOptions{
		MaxSteps: 50,
		StreamOptions: agent.StreamOptions{
			OnReasoning: func(e agent.AgentEvent) { called = true },
			OnContent:   func(e agent.AgentEvent) {},
		},
		OnCallForUser: func(e agent.AgentEvent) string { return "user reply" },
	}
	if opts.MaxSteps != 50 {
		t.Errorf("expected MaxSteps 50, got %d", opts.MaxSteps)
	}
	opts.OnReasoning(agent.AgentEvent{})
	if !called {
		t.Error("expected OnReasoning callback to be invoked")
	}
	reply := opts.OnCallForUser(agent.AgentEvent{})
	if reply != "user reply" {
		t.Errorf("expected OnCallForUser to return 'user reply', got '%s'", reply)
	}
}

func TestTaskExecution_WaitWithError(t *testing.T) {
	execution := &agent.TaskExecution{
		TaskID: "test-123",
	}
	if execution.TaskID != "test-123" {
		t.Errorf("expected TaskID 'test-123', got '%s'", execution.TaskID)
	}
}

func TestWsTarget_Resolution(t *testing.T) {
	mobileAgent := agent.NewMobileUseAgent(nil)
	computerAgent := agent.NewComputerUseAgent(nil)
	browserAgent := agent.NewBrowserUseAgent(nil)

	_ = mobileAgent
	_ = computerAgent
	_ = browserAgent
}
