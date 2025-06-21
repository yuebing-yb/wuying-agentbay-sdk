package window

import (
	"encoding/json"
	"fmt"
	"strings"

	"github.com/alibabacloud-go/tea/tea"
	mcp "github.com/aliyun/wuying-agentbay-sdk/golang/api/client"
)

// Window represents a window in the system
type Window struct {
	WindowID           int      `json:"window_id"`
	Title              string   `json:"title"`
	AbsoluteUpperLeftX int      `json:"absolute_upper_left_x,omitempty"`
	AbsoluteUpperLeftY int      `json:"absolute_upper_left_y,omitempty"`
	Width              int      `json:"width,omitempty"`
	Height             int      `json:"height,omitempty"`
	PID                int      `json:"pid,omitempty"`
	PName              string   `json:"pname,omitempty"`
	ChildWindows       []Window `json:"child_windows,omitempty"`
}

// WindowManager handles window management operations in the AgentBay cloud environment.
type WindowManager struct {
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
func (wm *WindowManager) callMcpTool(toolName string, args interface{}, defaultErrorMsg string) (*callMcpToolResult, error) {
	// Marshal arguments to JSON
	argsJSON, err := json.Marshal(args)
	if err != nil {
		return nil, fmt.Errorf("failed to marshal args: %w", err)
	}

	// Create the request
	callToolRequest := &mcp.CallMcpToolRequest{
		Authorization: tea.String("Bearer " + wm.Session.GetAPIKey()),
		SessionId:     tea.String(wm.Session.GetSessionId()),
		Name:          tea.String(toolName),
		Args:          tea.String(string(argsJSON)),
	}

	// Log API request
	fmt.Println("API Call: CallMcpTool -", toolName)
	fmt.Printf("Request: SessionId=%s, Args=%s\n", *callToolRequest.SessionId, *callToolRequest.Args)

	// Call the MCP tool
	response, err := wm.Session.GetClient().CallMcpTool(callToolRequest)

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

// NewWindowManager creates a new WindowManager object.
func NewWindowManager(session interface {
	GetAPIKey() string
	GetClient() *mcp.Client
	GetSessionId() string
}) *WindowManager {
	return &WindowManager{
		Session: session,
	}
}

// ListRootWindows lists all root windows in the system.
func (wm *WindowManager) ListRootWindows() ([]Window, error) {
	args := map[string]interface{}{}

	// Use the helper method to call MCP tool and check for errors
	mcpResult, err := wm.callMcpTool("list_root_windows", args, "error listing root windows")
	if err != nil {
		return nil, err
	}

	// Parse the JSON data into Window objects
	var windows []Window
	err = json.Unmarshal([]byte(mcpResult.TextContent), &windows)
	if err != nil {
		return nil, fmt.Errorf("failed to parse window data: %w", err)
	}

	return windows, nil
}

// GetActiveWindow gets the currently active window.
func (wm *WindowManager) GetActiveWindow() (*Window, error) {
	args := map[string]interface{}{}

	// Use the helper method to call MCP tool and check for errors
	mcpResult, err := wm.callMcpTool("get_active_window", args, "error getting active window")
	if err != nil {
		return nil, err
	}

	// Parse the JSON data into Window object
	var window Window
	err = json.Unmarshal([]byte(mcpResult.TextContent), &window)
	if err != nil {
		return nil, fmt.Errorf("failed to parse window data: %w", err)
	}

	return &window, nil
}

// ActivateWindow activates a window by ID.
func (wm *WindowManager) ActivateWindow(windowID int) error {
	args := map[string]int{
		"window_id": windowID,
	}

	// Use the helper method to call MCP tool and check for errors
	_, err := wm.callMcpTool("activate_window", args, "error activating window")
	if err != nil {
		return err
	}

	return nil
}

// MaximizeWindow maximizes a window by ID.
func (wm *WindowManager) MaximizeWindow(windowID int) error {
	args := map[string]int{
		"window_id": windowID,
	}

	// Use the helper method to call MCP tool and check for errors
	_, err := wm.callMcpTool("maximize_window", args, "error maximizing window")
	if err != nil {
		return err
	}

	return nil
}

// MinimizeWindow minimizes a window by ID.
func (wm *WindowManager) MinimizeWindow(windowID int) error {
	args := map[string]int{
		"window_id": windowID,
	}

	// Use the helper method to call MCP tool and check for errors
	_, err := wm.callMcpTool("minimize_window", args, "error minimizing window")
	if err != nil {
		return err
	}

	return nil
}

// RestoreWindow restores a window by ID.
func (wm *WindowManager) RestoreWindow(windowID int) error {
	args := map[string]int{
		"window_id": windowID,
	}

	// Use the helper method to call MCP tool and check for errors
	_, err := wm.callMcpTool("restore_window", args, "error restoring window")
	if err != nil {
		return err
	}

	return nil
}

// CloseWindow closes a window by ID.
func (wm *WindowManager) CloseWindow(windowID int) error {
	args := map[string]int{
		"window_id": windowID,
	}

	// Use the helper method to call MCP tool and check for errors
	_, err := wm.callMcpTool("close_window", args, "error closing window")
	if err != nil {
		return err
	}

	return nil
}

// FullscreenWindow toggles fullscreen mode for a window by ID.
func (wm *WindowManager) FullscreenWindow(windowID int) error {
	args := map[string]int{
		"window_id": windowID,
	}

	// Use the helper method to call MCP tool and check for errors
	_, err := wm.callMcpTool("fullscreen_window", args, "error toggling fullscreen mode")
	if err != nil {
		return err
	}

	return nil
}

// ResizeWindow resizes a window by ID.
func (wm *WindowManager) ResizeWindow(windowID, width, height int) error {
	args := map[string]int{
		"window_id": windowID,
		"width":     width,
		"height":    height,
	}

	// Use the helper method to call MCP tool and check for errors
	_, err := wm.callMcpTool("resize_window", args, "error resizing window")
	if err != nil {
		return err
	}

	return nil
}

// FocusMode enables or disables focus mode.
func (wm *WindowManager) FocusMode(on bool) error {
	args := map[string]bool{
		"on": on,
	}

	// Use the helper method to call MCP tool and check for errors
	_, err := wm.callMcpTool("focus_mode", args, "error setting focus mode")
	if err != nil {
		return err
	}

	return nil
}
