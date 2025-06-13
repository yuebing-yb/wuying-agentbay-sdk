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
func (c *Command) ExecuteCommand(command string, timeoutMs ...int) (string, error) {
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
	argsJSON, err := json.Marshal(args)
	if err != nil {
		return "", fmt.Errorf("failed to marshal args: %w", err)
	}

	callToolRequest := &mcp.CallMcpToolRequest{
		Authorization: tea.String("Bearer " + c.Session.GetAPIKey()),
		SessionId:     tea.String(c.Session.GetSessionId()),
		Name:          tea.String("shell"),
		Args:          tea.String(string(argsJSON)),
	}

	// Log API request
	fmt.Println("API Call: CallMcpTool - shell")
	fmt.Printf("Request: SessionId=%s, Args=%s\n", *callToolRequest.SessionId, *callToolRequest.Args)

	response, err := c.Session.GetClient().CallMcpTool(callToolRequest)

	// Log API response
	if err != nil {
		fmt.Println("Error calling CallMcpTool - shell:", err)
		return "", fmt.Errorf("failed to execute command: %w", err)
	}
	if response != nil && response.Body != nil {
		fmt.Println("Response from CallMcpTool - shell:", response.Body)
	}

	// Convert interface{} to map
	data, ok := response.Body.Data.(map[string]interface{})
	if !ok {
		return "", fmt.Errorf("invalid response data format")
	}

	// Get content field and parse as array
	contentArray, ok := data["content"].([]interface{})
	if !ok {
		return "", fmt.Errorf("content field not found or not an array")
	}

	var fullText string
	for _, item := range contentArray {
		// Assert each element is map[string]interface{}
		contentItem, ok := item.(map[string]interface{})
		if !ok {
			continue
		}

		// Extract text field
		text, ok := contentItem["text"].(string)
		if !ok {
			continue
		}

		fullText += text + "\n" // Concatenate text content
	}
	return fullText, nil
}

// RunCode executes code in the specified language with a timeout.
// If timeoutS is not provided or is 0, the default timeout of 300 seconds will be used.
func (c *Command) RunCode(code string, language string, timeoutS ...int) (string, error) {
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
	argsJSON, err := json.Marshal(args)
	if err != nil {
		return "", fmt.Errorf("failed to marshal args: %w", err)
	}

	callToolRequest := &mcp.CallMcpToolRequest{
		Authorization: tea.String("Bearer " + c.Session.GetAPIKey()),
		SessionId:     tea.String(c.Session.GetSessionId()),
		Name:          tea.String("run_code"),
		Args:          tea.String(string(argsJSON)),
	}

	// Log API request
	fmt.Println("API Call: CallMcpTool - run_code")
	fmt.Printf("Request: SessionId=%s, Language=%s, Timeout=%d\n", *callToolRequest.SessionId, language, timeout)

	response, err := c.Session.GetClient().CallMcpTool(callToolRequest)

	// Log API response
	if err != nil {
		fmt.Println("Error calling CallMcpTool - run_code:", err)
		return "", fmt.Errorf("failed to execute code: %w", err)
	}
	if response != nil && response.Body != nil {
		fmt.Println("Response from CallMcpTool - run_code:", response.Body)
	}

	// Convert interface{} to map
	data, ok := response.Body.Data.(map[string]interface{})
	if !ok {
		return "", fmt.Errorf("invalid response data format")
	}

	// Get output field
	output, ok := data["output"].(string)
	if !ok {
		return "", fmt.Errorf("output field not found or not a string")
	}

	return output, nil
}
