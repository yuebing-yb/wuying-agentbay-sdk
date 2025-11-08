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
//		"os"
//
//		"github.com/aliyun/wuying-agentbay-sdk/golang/pkg/agentbay"
//	)
//
//	func main() {
//		// Initialize AgentBay client
//		client, err := agentbay.NewAgentBay("", nil)
//		if err != nil {
//			fmt.Printf("Error initializing AgentBay client: %v\n", err)
//			os.Exit(1)
//		}
//
//		// Create a session with code_latest image (supports command execution)
//		params := agentbay.NewCreateSessionParams().WithImageId("code_latest")
//		result, err := client.Create(params)
//		if err != nil {
//			fmt.Printf("Error creating session: %v\n", err)
//			os.Exit(1)
//		}
//
//		session := result.Session
//		fmt.Printf("Session created: %s\n", session.SessionID)
//		// Output: Session created: session-xxxxxxxxxxxxxx
//
//		// Execute a simple command with default timeout (1000ms)
//		cmdResult, err := session.Command.ExecuteCommand("ls -la")
//		if err != nil {
//			fmt.Printf("Error executing command: %v\n", err)
//			os.Exit(1)
//		}
//		fmt.Printf("Command output:\n%s\n", cmdResult.Output)
//		// Output: Directory listing showing files and folders
//		// Sample: total 100\ndrwxr-x--- 16 wuying wuying 4096...
//		fmt.Printf("Request ID: %s\n", cmdResult.RequestID)
//		// Output: Request ID: XXXXXXXX-XXXX-XXXX-XXXX-XXXXXXXXXXXX
//
//		// Execute a command with custom timeout (5000ms)
//		longCmd, err := session.Command.ExecuteCommand("sleep 2 && echo 'Done'", 5000)
//		if err != nil {
//			fmt.Printf("Error executing long command: %v\n", err)
//			os.Exit(1)
//		}
//		fmt.Printf("Long command output: %s\n", longCmd.Output)
//		// Output: Long command output: Done
//		// The command waits 2 seconds then outputs "Done"
//		fmt.Printf("Request ID: %s\n", longCmd.RequestID)
//		// Output: Request ID: XXXXXXXX-XXXX-XXXX-XXXX-XXXXXXXXXXXX
//
//		// Note: If a command exceeds its timeout, it will return an error
//		// Example: session.Command.ExecuteCommand("sleep 3", 1000)
//		// Returns error: "command execution failed: Execution failed. Error code:-1 Error message: [timeout]"
//
//		// Clean up the session
//		deleteResult, err := session.Delete()
//		if err != nil {
//			fmt.Printf("Error deleting session: %v\n", err)
//			os.Exit(1)
//		}
//		if deleteResult.Success {
//			fmt.Println("Session deleted successfully")
//			// Output: Session deleted successfully
//		}
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
