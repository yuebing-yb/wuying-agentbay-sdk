# Code API Reference

## 💻 Related Tutorial

- [Code Execution Guide](../../../../../docs/guides/codespace/code-execution.md) - Execute code in isolated environments

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
package main
import (
    "fmt"
    "os"
    "github.com/aliyun/wuying-agentbay-sdk/golang/pkg/agentbay"
)
func main() {

    // Initialize AgentBay with API key from environment variable

    client, err := agentbay.NewAgentBay(os.Getenv("AGENTBAY_API_KEY"), nil)
    if err != nil {
        fmt.Printf("Error initializing AgentBay client: %v\n", err)
        os.Exit(1)
    }

    // Create a session with code_latest image

    params := &agentbay.CreateSessionParams{
        ImageId: "code_latest",
    }
    sessionResult, err := client.Create(params)
    if err != nil {
        fmt.Printf("Error creating session: %v\n", err)
        os.Exit(1)
    }
    session := sessionResult.Session

    // Execute Python code

    pythonCode := `
print("Hello from Python!")
result = 2 + 3
print(f"Result: {result}")
`
    codeResult, err := session.Code.RunCode(pythonCode, "python")
    if err != nil {
        fmt.Printf("Error executing Python code: %v\n", err)
    } else {
        fmt.Printf("Python code output:\n%s\n", codeResult.Output)
        fmt.Printf("Request ID: %s\n", codeResult.RequestID)
    }

    // Execute JavaScript code with custom timeout

    jsCode := `
console.log("Hello from JavaScript!");
const result = 2 + 3;
console.log("Result:", result);
`
    jsResult, err := session.Code.RunCode(jsCode, "javascript", 30)
    if err != nil {
        fmt.Printf("Error executing JavaScript code: %v\n", err)
    } else {
        fmt.Printf("JavaScript code output:\n%s\n", jsResult.Output)
        fmt.Printf("Request ID: %s\n", jsResult.RequestID)
    }
}
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

- [Session API Reference](../../common-features/basics/session.md)

---

*Documentation generated automatically from Go source code.*
