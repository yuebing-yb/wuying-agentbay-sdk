# Code API Reference

## 💻 Related Tutorial

- [Code Execution Guide](../../../../../docs/guides/codespace/code-execution.md) - Execute code in isolated environments

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

## Related Resources

- [Session API Reference](session.md)

---

*Documentation generated automatically from Go source code.*
