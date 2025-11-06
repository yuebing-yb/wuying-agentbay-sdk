package command

import (
	"fmt"

	mcp "github.com/aliyun/wuying-agentbay-sdk/golang/api/client"
	"github.com/aliyun/wuying-agentbay-sdk/golang/pkg/agentbay/models"
)

// CommandResult represents the result of a command execution
type CommandResult struct {
	// Embed the basic API response structure
	models.ApiResponse
	// Output contains the command execution output
	Output string
}

// Command handles command execution operations in the AgentBay cloud environment.
type Command struct {
	Session interface {
		GetAPIKey() string
		GetClient() *mcp.Client
		GetSessionId() string
		IsVpc() bool
		NetworkInterfaceIp() string
		HttpPort() string
		FindServerForTool(toolName string) string
		CallMcpTool(toolName string, args interface{}, autoGenSession ...bool) (*models.McpToolResult, error)
	}
}

// NewCommand creates a new Command instance
func NewCommand(session interface {
	GetAPIKey() string
	GetClient() *mcp.Client
	GetSessionId() string
	IsVpc() bool
	NetworkInterfaceIp() string
	HttpPort() string
	FindServerForTool(toolName string) string
	CallMcpTool(toolName string, args interface{}, autoGenSession ...bool) (*models.McpToolResult, error)
}) *Command {
	return &Command{
		Session: session,
	}
}

// ExecuteCommand executes a command in the session environment.
// ExecuteCommand executes a shell command in the session environment.
//
// Parameters:
//   - command: The shell command to execute
//   - timeoutMs: Timeout in milliseconds (optional, defaults to 1000ms)
//
// Returns:
//   - *CommandResult: Result containing command output and request ID
//   - error: Error if the operation fails
//
// Behavior:
//
// - Executes in a Linux shell environment
// - Combines stdout and stderr in the output
// - Default timeout is 1000ms (1 second)
// - Command runs with session user permissions
//
// Example:
//
//	package main
//
//	import (
//		"fmt"
//		"github.com/aliyun/wuying-agentbay-sdk/golang/pkg/agentbay"
//	)
//
//	func main() {
//		client, err := agentbay.NewAgentBay("your_api_key")
//		if err != nil {
//			panic(err)
//		}
//
//		result, err := client.Create(nil)
//		if err != nil {
//			panic(err)
//		}
//
//		session := result.Session
//
//		// Execute a simple command
//		cmdResult, err := session.Command.ExecuteCommand("echo 'Hello'")
//		if err != nil {
//			panic(err)
//		}
//
//		fmt.Printf("Output: %s\n", cmdResult.Output)
//		// Output: Output: Hello
//
//		// Execute with custom timeout
//		longCmd, err := session.Command.ExecuteCommand("sleep 2 && echo 'Done'", 3000)
//		if err != nil {
//			panic(err)
//		}
//		fmt.Println(longCmd.Output)
//		// Output: Done
//
//		session.Delete()
//	}
func (c *Command) ExecuteCommand(command string, timeoutMs ...int) (*CommandResult, error) {
	// Set default timeout if not provided
	timeout := 1000
	if len(timeoutMs) > 0 && timeoutMs[0] > 0 {
		timeout = timeoutMs[0]
	}

	args := map[string]interface{}{
		"command":    command,
		"timeout_ms": timeout,
	}

	// Use Session's CallMcpTool method
	result, err := c.Session.CallMcpTool("shell", args)
	if err != nil {
		return nil, fmt.Errorf("failed to execute command: %w", err)
	}

	if !result.Success {
		return nil, fmt.Errorf("command execution failed: %s", result.ErrorMessage)
	}

	return &CommandResult{
		ApiResponse: models.ApiResponse{
			RequestID: result.RequestID,
		},
		Output: result.Data,
	}, nil
}
