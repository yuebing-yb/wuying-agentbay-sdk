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
		CallMcpTool(toolName string, args interface{}) (*models.McpToolResult, error)
		GetWsClient() (interface{}, error)
	}
}
```

Code handles code execution operations in the AgentBay cloud environment.

### Methods

### Execute

```go
func (c *Code) Execute(code string, language string, args ...interface{}) (*CodeResult, error)
```

Execute is an alias of RunCode.

### Run

```go
func (c *Code) Run(code string, language string, args ...interface{}) (*CodeResult, error)
```

Run is an alias of RunCode.

### RunCode

```go
func (c *Code) RunCode(code string, language string, args ...interface{}) (*CodeResult, error)
```

RunCode executes code in the session environment. timeoutS: The timeout for the code execution in
seconds. Default is 60s. Note: Due to gateway limitations, each request cannot exceed 60 seconds.

language is case-insensitive. Supported values: "python", "javascript", "r", "java".

**Example:**

```go
client, _ := agentbay.NewAgentBay(os.Getenv("AGENTBAY_API_KEY"), nil)
sessionResult, _ := client.Create(agentbay.NewCreateSessionParams().WithImageId("code_latest"))
defer sessionResult.Session.Delete()
codeResult, _ := sessionResult.Session.Code.RunCode("print('Hello')", "python")
```

### Related Functions

### NewCode

```go
func NewCode(session interface {
	GetAPIKey() string
	GetClient() *mcp.Client
	GetSessionId() string
	CallMcpTool(toolName string, args interface{}) (*models.McpToolResult, error)
	GetWsClient() (interface{}, error)
}) *Code
```

NewCode creates a new Code instance

## Type CodeExecutionError

```go
type CodeExecutionError struct {
	Name		string	`json:"name"`
	Value		string	`json:"value"`
	Traceback	string	`json:"traceback"`
}
```

CodeExecutionError represents an error during code execution

## Type CodeExecutionLogs

```go
type CodeExecutionLogs struct {
	Stdout	[]string	`json:"stdout"`
	Stderr	[]string	`json:"stderr"`
}
```

CodeExecutionLogs represents stdout and stderr logs

## Type CodeExecutionResultItem

```go
type CodeExecutionResultItem struct {
	Text		string		`json:"text,omitempty"`
	HTML		string		`json:"html,omitempty"`
	Markdown	string		`json:"markdown,omitempty"`
	PNG		string		`json:"png,omitempty"`
	JPEG		string		`json:"jpeg,omitempty"`
	SVG		string		`json:"svg,omitempty"`
	Latex		string		`json:"latex,omitempty"`
	JSON		interface{}	`json:"json,omitempty"`
	Chart		interface{}	`json:"chart,omitempty"`
	IsMainResult	bool		`json:"is_main_result,omitempty"`
}
```

CodeExecutionResultItem represents a single result item (text, image, etc.)

## Type CodeResult

```go
type CodeResult struct {
	models.ApiResponse	// Embedded ApiResponse

	// Legacy/Simple output
	Output	string

	// Enhanced fields
	Success		bool				`json:"success"`
	Result		string				`json:"result"`	// Legacy compatible result text
	ErrorMessage	string				`json:"error_message,omitempty"`
	Logs		*CodeExecutionLogs		`json:"logs,omitempty"`
	Results		[]CodeExecutionResultItem	`json:"results,omitempty"`
	Error		*CodeExecutionError		`json:"error,omitempty"`
	ExecutionTime	float64				`json:"execution_time,omitempty"`
	ExecutionCount	*int				`json:"execution_count,omitempty"`
}
```

CodeResult represents the result of a code execution

## Type WsStreamClient

```go
type WsStreamClient interface {
	CallStream(target string, data map[string]interface{},
		onEvent func(string, map[string]interface{}),
		onEnd func(string, map[string]interface{}),
		onError func(string, error),
	) (*internal.WsStreamHandle, error)
}
```

WsStreamClient is a public interface for WebSocket streaming clients. It abstracts the internal
WsClient to allow external packages (e.g., tests) to implement GetWsClient without importing the
internal package.

## Type backendResponse

```go
type backendResponse struct {
	ExecutionError	string		`json:"executionError"`
	Result		[]string	`json:"result"`	// List of JSON strings
	Stdout		[]string	`json:"stdout"`
	Stderr		[]string	`json:"stderr"`
	TraceID		string		`json:"traceId"`
	// Try both cases just in case
	ExecutionTime	float64	`json:"executionTime"`
	ExecutionTimeSn	float64	`json:"execution_time"`
	ExecutionCount	*int	`json:"executionCount"`
	ExecutionCntSn	*int	`json:"execution_count"`
}
```

backendResponse represents the raw JSON structure returned by the backend tool

## Type runCodeStreamBetaOptions

```go
type runCodeStreamBetaOptions struct {
	TimeoutS	int
	StreamBeta	bool
	OnStdout	func(chunk string)
	OnStderr	func(chunk string)
	OnError		func(err error)
}
```

RunCodeStreamBetaOptions holds streaming callback options for run_code. Temporarily unexported while
streaming API is disabled in this release. Will be re-exported in a future release.

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
