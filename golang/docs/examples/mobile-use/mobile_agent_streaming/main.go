// Mobile Agent Streaming Example
//
// Demonstrates:
// 1. Mobile Agent task execution with real-time streaming output
// 2. Using typed callbacks (OnReasoning, OnContent, OnToolCall, OnToolResult)
package main

import (
	"fmt"
	"os"
	"strings"

	"github.com/aliyun/wuying-agentbay-sdk/golang/pkg/agentbay"
	"github.com/aliyun/wuying-agentbay-sdk/golang/pkg/agentbay/agent"
)

func exampleTypedCallbacks(client *agentbay.AgentBay) {
	fmt.Println(strings.Repeat("=", 60))
	fmt.Println("Example 1: Mobile Agent Streaming with Typed Callbacks")
	fmt.Println(strings.Repeat("=", 60))

	params := agentbay.NewCreateSessionParams().WithImageId("imgc-0ab5takhnmlvhx9gp")
	sessionResult, err := client.Create(params)
	if err != nil {
		fmt.Printf("Failed to create session: %v\n", err)
		return
	}
	defer sessionResult.Session.Delete()
	fmt.Printf("Session created: %s\n", sessionResult.Session.SessionID)

	result := sessionResult.Session.Agent.Mobile.ExecuteTaskAndWait(
		"Open Settings app",
		180,
		agent.MobileTaskOptions{
			MaxSteps: 10,
			StreamOptions: agent.StreamOptions{
				OnReasoning: func(evt agent.AgentEvent) {
					fmt.Printf("[Reasoning] %s", evt.Content)
				},
				OnContent: func(evt agent.AgentEvent) {
					fmt.Printf("[Content] %s", evt.Content)
				},
				OnToolCall: func(evt agent.AgentEvent) {
					fmt.Printf("\n[ToolCall] %s(%v)\n", evt.ToolName, evt.Args)
				},
				OnToolResult: func(evt agent.AgentEvent) {
					fmt.Printf("[ToolResult] %s -> %v\n", evt.ToolName, evt.Result)
				},
			},
		},
	)

	fmt.Printf("\n\nTask completed:\n")
	fmt.Printf("  Success: %v\n", result.Success)
	fmt.Printf("  Status: %s\n", result.TaskStatus)
	if result.TaskResult != "" {
		fmt.Printf("  Result: %s\n", result.TaskResult)
	}
}

func main() {
	fmt.Println("Mobile Agent Streaming Output Examples\n")

	apiKey := os.Getenv("AGENTBAY_API_KEY")
	client, err := agentbay.NewAgentBay(apiKey, nil)
	if err != nil {
		fmt.Printf("Failed to create AgentBay client: %v\n", err)
		os.Exit(1)
	}

	exampleTypedCallbacks(client)

	fmt.Println("\nAll examples completed!")
}
