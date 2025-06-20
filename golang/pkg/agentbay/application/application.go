package application

import (
	"encoding/json"
	"fmt"
	"strings"

	"github.com/alibabacloud-go/tea/tea"
	mcp "github.com/aliyun/wuying-agentbay-sdk/golang/api/client"
)

// InstalledApp represents an installed application
type InstalledApp struct {
	Name          string `json:"name"`
	StartCmd      string `json:"start_cmd"`
	StopCmd       string `json:"stop_cmd,omitempty"`
	WorkDirectory string `json:"work_directory,omitempty"`
}

// Process represents a running process
type Process struct {
	PName   string `json:"pname"`
	PID     int    `json:"pid"`
	CmdLine string `json:"cmdline,omitempty"`
}

// ApplicationManager handles application management operations in the AgentBay cloud environment.
type ApplicationManager struct {
	Session interface {
		GetAPIKey() string
		GetClient() *mcp.Client
		GetSessionId() string
	}
}

// callMcpToolResult represents the result of a CallMcpTool operation
type callMcpToolResult struct {
	Data        map[string]interface{}
	Content     []map[string]interface{}
	TextContent string
	IsError     bool
	ErrorMsg    string
	StatusCode  int32
}

// callMcpTool calls the MCP tool and checks for errors in the response
func (am *ApplicationManager) callMcpTool(toolName string, args interface{}, defaultErrorMsg string) (*callMcpToolResult, error) {
	// Marshal arguments to JSON
	argsJSON, err := json.Marshal(args)
	if err != nil {
		return nil, fmt.Errorf("failed to marshal args: %w", err)
	}

	// Create the request
	callToolRequest := &mcp.CallMcpToolRequest{
		Authorization: tea.String("Bearer " + am.Session.GetAPIKey()),
		SessionId:     tea.String(am.Session.GetSessionId()),
		Name:          tea.String(toolName),
		Args:          tea.String(string(argsJSON)),
	}

	// Log API request
	fmt.Println("API Call: CallMcpTool -", toolName)
	fmt.Printf("Request: SessionId=%s, Args=%s\n", *callToolRequest.SessionId, *callToolRequest.Args)

	// Call the MCP tool
	response, err := am.Session.GetClient().CallMcpTool(callToolRequest)

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

		// Extract text content from the content items
		var textBuilder strings.Builder
		for _, item := range result.Content {
			text, ok := item["text"].(string)
			if !ok {
				continue
			}

			if textBuilder.Len() > 0 {
				textBuilder.WriteString("\n")
			}
			textBuilder.WriteString(text)
		}
		result.TextContent = textBuilder.String()
	}

	return result, nil
}

// NewApplicationManager creates a new ApplicationManager object.
func NewApplicationManager(session interface {
	GetAPIKey() string
	GetClient() *mcp.Client
	GetSessionId() string
}) *ApplicationManager {
	return &ApplicationManager{
		Session: session,
	}
}

// GetInstalledApps retrieves a list of installed applications.
func (am *ApplicationManager) GetInstalledApps(startMenu bool, desktop bool, ignoreSystemApps bool) (string, error) {
	args := map[string]interface{}{
		"start_menu":         startMenu,
		"desktop":            desktop,
		"ignore_system_apps": ignoreSystemApps,
	}

	// Use the helper method to call MCP tool and check for errors
	mcpResult, err := am.callMcpTool("get_installed_apps", args, "error getting installed apps")
	if err != nil {
		return "", err
	}

	// Return the extracted text content
	return mcpResult.TextContent, nil
}

// StartApp starts an application with the given command and optional working directory.
func (am *ApplicationManager) StartApp(startCmd string, workDirectory string) (string, error) {
	args := map[string]string{
		"start_cmd": startCmd,
	}
	if workDirectory != "" {
		args["work_directory"] = workDirectory
	}

	// Use the helper method to call MCP tool and check for errors
	mcpResult, err := am.callMcpTool("start_app", args, "error starting app")
	if err != nil {
		return "", err
	}

	// Return the extracted text content
	return mcpResult.TextContent, nil
}

// StopAppByPName stops an application by process name.
func (am *ApplicationManager) StopAppByPName(pname string) (string, error) {
	args := map[string]string{
		"pname": pname,
	}

	// Use the helper method to call MCP tool and check for errors
	mcpResult, err := am.callMcpTool("stop_app_by_pname", args, "error stopping app by process name")
	if err != nil {
		return "", err
	}

	// Return the extracted text content
	return mcpResult.TextContent, nil
}

// StopAppByPID stops an application by process ID.
func (am *ApplicationManager) StopAppByPID(pid int) (string, error) {
	args := map[string]int{
		"pid": pid,
	}

	// Use the helper method to call MCP tool and check for errors
	mcpResult, err := am.callMcpTool("stop_app_by_pid", args, "error stopping app by PID")
	if err != nil {
		return "", err
	}

	// Return the extracted text content
	return mcpResult.TextContent, nil
}

// StopAppByCmd stops an application using a specific command.
func (am *ApplicationManager) StopAppByCmd(stopCmd string) (string, error) {
	args := map[string]string{
		"stop_cmd": stopCmd,
	}

	// Use the helper method to call MCP tool and check for errors
	mcpResult, err := am.callMcpTool("stop_app_by_cmd", args, "error stopping app by command")
	if err != nil {
		return "", err
	}

	// Return the extracted text content
	return mcpResult.TextContent, nil
}

// ListVisibleApps lists currently visible applications.
func (am *ApplicationManager) ListVisibleApps() (string, error) {
	args := map[string]interface{}{}

	// Use the helper method to call MCP tool and check for errors
	mcpResult, err := am.callMcpTool("list_visible_apps", args, "error listing visible apps")
	if err != nil {
		return "", err
	}

	// Return the extracted text content
	return mcpResult.TextContent, nil
}
