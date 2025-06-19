package command

import (
	"encoding/json"
	"fmt"

	"github.com/alibabacloud-go/tea/tea"
	mcp "github.com/aliyun/wuying-agentbay-sdk/golang/api/client"
)

// Command handles command execution operations in the AgentBay cloud environment.
type Command struct {
	Session interface {
		GetAPIKey() string
		GetClient() *mcp.Client
		GetSessionId() string
	}
}

// callMcpToolResult represents the result of a CallMcpTool operation
type callMcpToolResult struct {
	Data       map[string]interface{}
	Content    []map[string]interface{}
	IsError    bool
	ErrorMsg   string
	StatusCode int32
}

// callMcpTool calls the MCP tool and checks for errors in the response
func (c *Command) callMcpTool(toolName string, args interface{}, defaultErrorMsg string) (*callMcpToolResult, error) {
	// Marshal arguments to JSON
	argsJSON, err := json.Marshal(args)
	if err != nil {
		return nil, fmt.Errorf("failed to marshal args: %w", err)
	}

	// Create the request
	callToolRequest := &mcp.CallMcpToolRequest{
		Authorization: tea.String("Bearer " + c.Session.GetAPIKey()),
		SessionId:     tea.String(c.Session.GetSessionId()),
		Name:          tea.String(toolName),
		Args:          tea.String(string(argsJSON)),
	}

	// Log API request
	fmt.Println("API Call: CallMcpTool -", toolName)
	fmt.Printf("Request: SessionId=%s, Args=%s\n", *callToolRequest.SessionId, *callToolRequest.Args)

	// Call the MCP tool
	response, err := c.Session.GetClient().CallMcpTool(callToolRequest)

	// Log API response
	if err != nil {
		fmt.Println("Error calling CallMcpTool -", toolName, ":", err)
		return nil, fmt.Errorf("failed to call %s: %w", toolName, err)
	}
	if response != nil && response.Body != nil {
		fmt.Println("Response from CallMcpTool -", toolName, ":", response.Body)
	}

	// Extract data from response
	data, ok := response.Body.Data.(map[string]interface{})
	if !ok {
		return nil, fmt.Errorf("invalid response data format")
	}

	// Create result object
	result := &callMcpToolResult{
		Data:       data,
		StatusCode: *response.StatusCode,
	}

	// Check if there's an error in the response
	isError, ok := data["isError"].(bool)
	if ok && isError {
		result.IsError = true

		// Try to extract the error message from the content field
		contentArray, ok := data["content"].([]interface{})
		if ok && len(contentArray) > 0 {
			// Convert content array to a more usable format
			result.Content = make([]map[string]interface{}, 0, len(contentArray))
			for _, item := range contentArray {
				contentItem, ok := item.(map[string]interface{})
				if !ok {
					continue
				}
				result.Content = append(result.Content, contentItem)
			}

			// Extract error message from the first content item
			if len(result.Content) > 0 {
				text, ok := result.Content[0]["text"].(string)
				if ok {
					result.ErrorMsg = text
					return result, fmt.Errorf("%s", text)
				}
			}
		}
		return result, fmt.Errorf("%s", defaultErrorMsg)
	}

	// Extract content array if it exists
	contentArray, ok := data["content"].([]interface{})
	if ok {
		result.Content = make([]map[string]interface{}, 0, len(contentArray))
		for _, item := range contentArray {
			contentItem, ok := item.(map[string]interface{})
			if !ok {
				continue
			}
			result.Content = append(result.Content, contentItem)
		}
	}

	return result, nil
}

// NewCommand creates a new Command object.
func NewCommand(session interface {
	GetAPIKey() string
	GetClient() *mcp.Client
	GetSessionId() string
}) *Command {
	return &Command{
		Session: session,
	}
}

// ExecuteCommand executes a command in the cloud environment with a specified timeout.
// If timeoutMs is not provided or is 0, the default timeout of 1000ms will be used.
func (c *Command) ExecuteCommand(command string, timeoutMs ...int) (interface{}, error) {
	// Set default timeout if not provided
	timeout := 1000
	if len(timeoutMs) > 0 && timeoutMs[0] > 0 {
		timeout = timeoutMs[0]
	}

	// Prepare arguments for the shell tool
	args := map[string]interface{}{
		"command":    command,
		"timeout_ms": timeout,
	}

	// Use the helper method to call MCP tool and check for errors
	mcpResult, err := c.callMcpTool("shell", args, "error executing command")
	if err != nil {
		return nil, err
	}

	// Return the raw content field for the caller to parse
	return mcpResult.Data["content"], nil
}

// RunCode executes code in the specified language with a timeout.
// If timeoutS is not provided or is 0, the default timeout of 300 seconds will be used.
func (c *Command) RunCode(code string, language string, timeoutS ...int) (interface{}, error) {
	// Set default timeout if not provided
	timeout := 300
	if len(timeoutS) > 0 && timeoutS[0] > 0 {
		timeout = timeoutS[0]
	}

	// Validate language
	if language != "python" && language != "javascript" {
		return "", fmt.Errorf("unsupported language: %s. Supported languages are 'python' and 'javascript'", language)
	}

	// Prepare arguments for the run_code tool
	args := map[string]interface{}{
		"code":      code,
		"language":  language,
		"timeout_s": timeout,
	}

	// Use the helper method to call MCP tool and check for errors
	mcpResult, err := c.callMcpTool("run_code", args, "error executing code")
	if err != nil {
		return nil, err
	}

	// Return the raw content field for the caller to parse
	return mcpResult.Data["content"], nil
}
