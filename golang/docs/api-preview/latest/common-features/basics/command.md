# Command API Reference

## ⚡ Related Tutorial

- [Command Execution Guide](../../../../../docs/guides/common-features/basics/command-execution.md) - Learn how to execute commands in sessions

## Overview

The Command module provides methods for executing shell commands within a session in the AgentBay cloud environment.
It supports both synchronous command execution with configurable timeouts.

Command templates for various AgentBay operations.

This module contains shell command templates used by different modules
to execute operations in remote environments.

Template naming convention:
- Use descriptive names that clearly indicate the operation
- Group templates by functionality (mobile, desktop, network, etc.)
- Use consistent parameter naming across similar templates

Parameter conventions:
- Use snake_case for parameter names
- Include descriptive parameter names (e.g., lock_switch, package_list)
- Document expected parameter types and values

## Requirements

- Any session image (browser_latest, code_latest, windows_latest, mobile_latest)

## Type Command

```go
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
```

Command handles command execution operations in the AgentBay cloud environment.

### Methods

#### ExecuteCommand

```go
func (c *Command) ExecuteCommand(command string, timeoutMs ...int) (*CommandResult, error)
```

ExecuteCommand executes a command in the session environment. ExecuteCommand executes a shell
command in the session environment.

Parameters:
  - command: The shell command to execute
  - timeoutMs: Timeout in milliseconds (optional, defaults to 1000ms)

Returns:
  - *CommandResult: Result containing command output and request ID
  - error: Error if the operation fails

Behavior:

- Executes in a Linux shell environment - Combines stdout and stderr in the output - Default timeout
is 1000ms (1 second) - Command runs with session user permissions

**Example:**

```go
package main
import (
	"fmt"
	"github.com/aliyun/wuying-agentbay-sdk/golang/pkg/agentbay"
)
func main() {
	client, err := agentbay.NewAgentBay("your_api_key")
	if err != nil {
		panic(err)
	}
	result, err := client.Create(nil)
	if err != nil {
		panic(err)
	}
	session := result.Session

	// Execute a simple command

	cmdResult, err := session.Command.ExecuteCommand("echo 'Hello'")
	if err != nil {
		panic(err)
	}
	fmt.Printf("Output: %s\n", cmdResult.Output)

	// Output: Output: Hello

	// Execute with custom timeout

	longCmd, err := session.Command.ExecuteCommand("sleep 2 && echo 'Done'", 3000)
	if err != nil {
		panic(err)
	}
	fmt.Println(longCmd.Output)

	// Output: Done

	session.Delete()
}
```

### Related Functions

#### NewCommand

```go
func NewCommand(session interface {
	GetAPIKey() string
	GetClient() *mcp.Client
	GetSessionId() string
	IsVpc() bool
	NetworkInterfaceIp() string
	HttpPort() string
	FindServerForTool(toolName string) string
	CallMcpTool(toolName string, args interface{}, autoGenSession ...bool) (*models.McpToolResult, error)
}) *Command
```

NewCommand creates a new Command instance

## Type CommandResult

```go
type CommandResult struct {
	// Embed the basic API response structure
	models.ApiResponse
	// Output contains the command execution output
	Output	string
}
```

CommandResult represents the result of a command execution

## Functions

### GetMobileCommandTemplate

```go
func GetMobileCommandTemplate(templateName string) (string, bool)
```

GetMobileCommandTemplate returns a mobile command template by name

## Best Practices

1. Always specify appropriate timeout values based on expected command duration
2. Handle command execution errors gracefully
3. Use absolute paths when referencing files in commands
4. Be aware that commands run with session user permissions
5. Clean up temporary files created by commands

## Related Resources

- [Session API Reference](session.md)
- [FileSystem API Reference](filesystem.md)

---

*Documentation generated automatically from Go source code.*
