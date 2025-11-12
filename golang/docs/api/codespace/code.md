# Code API Reference

## 💻 Related Tutorial

- [Code Execution Guide](../../../../docs/guides/codespace/code-execution.md) - Execute code in isolated environments

## Overview

The Code module provides secure code execution capabilities in isolated environments.
It supports multiple programming languages including Python, JavaScript, and more.

## Requirements

- Requires `code_latest` image for code execution features

## Type Code

```go
type Code struct {
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

Code handles code execution operations in the AgentBay cloud environment.

### Methods

#### RunCode

```go
func (c *Code) RunCode(code string, language string, timeoutS ...int) (*CodeResult, error)
```

RunCode executes code in the session environment. timeoutS: The timeout for the code execution in
seconds. Default is 60s. Note: Due to gateway limitations, each request cannot exceed 60 seconds.

**Example:**

```go
client, _ := agentbay.NewAgentBay(os.Getenv("AGENTBAY_API_KEY"), nil)
sessionResult, _ := client.Create(agentbay.NewCreateSessionParams().WithImageId("code_latest"))
defer sessionResult.Session.Delete()
codeResult, _ := sessionResult.Session.Code.RunCode("print('Hello')", "python")
```

### Related Functions

#### NewCode

```go
func NewCode(session interface {
	GetAPIKey() string
	GetClient() *mcp.Client
	GetSessionId() string
	IsVpc() bool
	NetworkInterfaceIp() string
	HttpPort() string
	FindServerForTool(toolName string) string
	CallMcpTool(toolName string, args interface{}, autoGenSession ...bool) (*models.McpToolResult, error)
}) *Code
```

NewCode creates a new Code instance

## Type CodeResult

```go
type CodeResult struct {
	models.ApiResponse	// Embedded ApiResponse
	Output			string
}
```

CodeResult represents the result of a code execution

## Best Practices

1. Validate code syntax before execution
2. Set appropriate execution timeouts
3. Handle execution errors and exceptions
4. Use proper resource limits to prevent resource exhaustion
5. Clean up temporary files after code execution

## Related Resources

- [Session API Reference](../common-features/basics/session.md)

---

*Documentation generated automatically from Go source code.*
