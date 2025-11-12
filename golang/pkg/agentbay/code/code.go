package code

import (
	"fmt"

	mcp "github.com/aliyun/wuying-agentbay-sdk/golang/api/client"
	"github.com/aliyun/wuying-agentbay-sdk/golang/pkg/agentbay/models"
)

// CodeResult represents the result of a code execution
type CodeResult struct {
	models.ApiResponse // Embedded ApiResponse
	Output             string
}

// Code handles code execution operations in the AgentBay cloud environment.
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

// NewCode creates a new Code instance
func NewCode(session interface {
	GetAPIKey() string
	GetClient() *mcp.Client
	GetSessionId() string
	IsVpc() bool
	NetworkInterfaceIp() string
	HttpPort() string
	FindServerForTool(toolName string) string
	CallMcpTool(toolName string, args interface{}, autoGenSession ...bool) (*models.McpToolResult, error)
}) *Code {
	return &Code{
		Session: session,
	}
}

// RunCode executes code in the session environment.
// timeoutS: The timeout for the code execution in seconds. Default is 60s.
// Note: Due to gateway limitations, each request cannot exceed 60 seconds.
//
// Example:
//
//	package main
//
//	import (
//	    "fmt"
//	    "os"
//
//	    "github.com/aliyun/wuying-agentbay-sdk/golang/pkg/agentbay"
//	)
//
//	func main() {
//	    // Initialize AgentBay with API key from environment variable
//	    client, err := agentbay.NewAgentBay(os.Getenv("AGENTBAY_API_KEY"), nil)
//	    if err != nil {
//	        fmt.Printf("Error initializing AgentBay client: %v\n", err)
//	        os.Exit(1)
//	    }
//
//	    // Create a session with code_latest image
//	    params := &agentbay.CreateSessionParams{
//	        ImageId: "code_latest",
//	    }
//	    sessionResult, err := client.Create(params)
//	    if err != nil {
//	        fmt.Printf("Error creating session: %v\n", err)
//	        os.Exit(1)
//	    }
//	    session := sessionResult.Session
//
//	    // Execute Python code
//	    pythonCode := `
//	print("Hello from Python!")
//	result = 2 + 3
//	print(f"Result: {result}")
//	`
//	    codeResult, err := session.Code.RunCode(pythonCode, "python")
//	    if err != nil {
//	        fmt.Printf("Error executing Python code: %v\n", err)
//	    } else {
//	        fmt.Printf("Python code output:\n%s\n", codeResult.Output)
//	        fmt.Printf("Request ID: %s\n", codeResult.RequestID)
//	    }
//
//	    // Execute JavaScript code with custom timeout
//	    jsCode := `
//	console.log("Hello from JavaScript!");
//	const result = 2 + 3;
//	console.log("Result:", result);
//	`
//	    jsResult, err := session.Code.RunCode(jsCode, "javascript", 30)
//	    if err != nil {
//	        fmt.Printf("Error executing JavaScript code: %v\n", err)
//	    } else {
//	        fmt.Printf("JavaScript code output:\n%s\n", jsResult.Output)
//	        fmt.Printf("Request ID: %s\n", jsResult.RequestID)
//	    }
//	}
func (c *Code) RunCode(code string, language string, timeoutS ...int) (*CodeResult, error) {
	// Set default timeout if not provided
	timeout := 60
	if len(timeoutS) > 0 && timeoutS[0] > 0 {
		timeout = timeoutS[0]
	}

	// Validate language
	if language != "python" && language != "javascript" {
		return nil, fmt.Errorf("unsupported language: %s. Supported languages are 'python' and 'javascript'", language)
	}

	args := map[string]interface{}{
		"code":      code,
		"language":  language,
		"timeout_s": timeout,
	}

	// Use Session's CallMcpTool method
	result, err := c.Session.CallMcpTool("run_code", args)
	if err != nil {
		return nil, fmt.Errorf("failed to execute code: %w", err)
	}

	if !result.Success {
		return nil, fmt.Errorf("code execution failed: %s", result.ErrorMessage)
	}

	return &CodeResult{
		ApiResponse: models.ApiResponse{
			RequestID: result.RequestID,
		},
		Output: result.Data,
	}, nil
}
