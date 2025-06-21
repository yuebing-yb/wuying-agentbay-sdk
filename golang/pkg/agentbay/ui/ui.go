package ui

import (
	"encoding/json"
	"fmt"
	"strings"

	"github.com/alibabacloud-go/tea/tea"
	mcp "github.com/aliyun/wuying-agentbay-sdk/golang/api/client"
)

// UIElement represents a UI element in the UI hierarchy
type UIElement struct {
	Bounds     string       `json:"bounds"`
	ClassName  string       `json:"className"`
	Text       string       `json:"text"`
	Type       string       `json:"type"`
	ResourceId string       `json:"resourceId"`
	Index      int          `json:"index"`
	IsParent   bool         `json:"isParent"`
	Children   []*UIElement `json:"children,omitempty"`
}

// KeyCode constants for mobile device input
var KeyCode = struct {
	HOME        int
	BACK        int
	VOLUME_UP   int
	VOLUME_DOWN int
	POWER       int
	MENU        int
}{
	HOME:        3,
	BACK:        4,
	VOLUME_UP:   24,
	VOLUME_DOWN: 25,
	POWER:       26,
	MENU:        82,
}

// UI handles UI operations in the AgentBay cloud environment
type UI struct {
	Session interface {
		GetAPIKey() string
		GetClient() *mcp.Client
		GetSessionId() string
	}
}

// NewUI creates a new UI object
func NewUI(session interface {
	GetAPIKey() string
	GetClient() *mcp.Client
	GetSessionId() string
}) *UI {
	return &UI{
		Session: session,
	}
}

// callMcpTool is an internal helper to call MCP tool and handle errors
func (u *UI) callMcpTool(name string, args interface{}) (string, error) {
	argsJSON, err := json.Marshal(args)
	if err != nil {
		return "", fmt.Errorf("failed to marshal args: %w", err)
	}

	callToolRequest := &mcp.CallMcpToolRequest{
		Authorization: tea.String("Bearer " + u.Session.GetAPIKey()),
		SessionId:     tea.String(u.Session.GetSessionId()),
		Name:          tea.String(name),
		Args:          tea.String(string(argsJSON)),
	}

	// Log API request
	fmt.Println("API Call: CallMcpTool -", name)
	fmt.Printf("Request: SessionId=%s, Args=%s\n", *callToolRequest.SessionId, *callToolRequest.Args)

	response, err := u.Session.GetClient().CallMcpTool(callToolRequest)

	// Log API response
	if err != nil {
		fmt.Println("Error calling CallMcpTool -", name, ":", err)
		return "", fmt.Errorf("failed to call MCP tool %s: %w", name, err)
	}
	if response != nil && response.Body != nil {
		fmt.Println("Response from CallMcpTool -", name, ":", response.Body)
	}

	// Parse the response
	data, ok := response.Body.Data.(map[string]interface{})
	if !ok {
		return "", fmt.Errorf("invalid response data format")
	}

	// Check if there's an error in the response
	isError, ok := data["isError"].(bool)
	if ok && isError {
		// Try to extract the error message from the content field
		contentArray, ok := data["content"].([]interface{})
		if ok && len(contentArray) > 0 {
			var errorMessages []string
			for _, item := range contentArray {
				contentItem, ok := item.(map[string]interface{})
				if ok {
					text, ok := contentItem["text"].(string)
					if ok {
						errorMessages = append(errorMessages, text)
					}
				}
			}
			if len(errorMessages) > 0 {
				return "", fmt.Errorf("error in response: %s", strings.Join(errorMessages, "; "))
			}
		}
		return "", fmt.Errorf("error in response")
	}

	// Extract content array
	content, ok := data["content"].([]interface{})
	if !ok || len(content) == 0 {
		return "", fmt.Errorf("no content found in response")
	}

	// Extract text field from the first content item
	contentItem, ok := content[0].(map[string]interface{})
	if !ok {
		return "", fmt.Errorf("invalid content item format")
	}

	jsonText, ok := contentItem["text"].(string)
	if !ok {
		return "", fmt.Errorf("text field not found or not a string")
	}

	return jsonText, nil
}

// GetClickableUIElements retrieves all clickable UI elements within the specified timeout
func (u *UI) GetClickableUIElements(timeoutMs int) ([]*UIElement, error) {
	if timeoutMs <= 0 {
		timeoutMs = 2000 // Default timeout
	}

	args := map[string]interface{}{
		"timeout_ms": timeoutMs,
	}

	result, err := u.callMcpTool("get_clickable_ui_elements", args)
	if err != nil {
		return nil, fmt.Errorf("failed to get clickable UI elements: %w", err)
	}

	// Parse the JSON string into a slice of UIElement structs
	var elements []*UIElement
	if err := json.Unmarshal([]byte(result), &elements); err != nil {
		return nil, fmt.Errorf("failed to parse UI elements: %w", err)
	}

	return elements, nil
}

// GetAllUIElements retrieves all UI elements within the specified timeout
func (u *UI) GetAllUIElements(timeoutMs int) ([]*UIElement, error) {
	if timeoutMs <= 0 {
		timeoutMs = 2000 // Default timeout
	}

	args := map[string]interface{}{
		"timeout_ms": timeoutMs,
	}

	result, err := u.callMcpTool("get_all_ui_elements", args)
	if err != nil {
		return nil, fmt.Errorf("failed to get all UI elements: %w", err)
	}

	// Parse the JSON string into a slice of UIElement structs
	var elements []*UIElement
	if err := json.Unmarshal([]byte(result), &elements); err != nil {
		return nil, fmt.Errorf("failed to parse UI elements: %w", err)
	}

	return elements, nil
}

// SendKey sends a key press event
func (u *UI) SendKey(key int) (string, error) {
	args := map[string]interface{}{
		"key": key,
	}

	result, err := u.callMcpTool("send_key", args)
	if err != nil {
		return "", fmt.Errorf("failed to send key: %w", err)
	}

	return result, nil
}

// InputText inputs text into the active field
func (u *UI) InputText(text string) (string, error) {
	args := map[string]interface{}{
		"text": text,
	}

	result, err := u.callMcpTool("input_text", args)
	if err != nil {
		return "", fmt.Errorf("failed to input text: %w", err)
	}

	return result, nil
}

// Swipe performs a swipe gesture from start to end coordinates
func (u *UI) Swipe(startX, startY, endX, endY, durationMs int) (string, error) {
	args := map[string]interface{}{
		"start_x":     startX,
		"start_y":     startY,
		"end_x":       endX,
		"end_y":       endY,
		"duration_ms": durationMs,
	}

	result, err := u.callMcpTool("swipe", args)
	if err != nil {
		return "", fmt.Errorf("failed to perform swipe: %w", err)
	}

	return result, nil
}

// Click performs a click at the specified coordinates
func (u *UI) Click(x, y int, button string) (string, error) {
	args := map[string]interface{}{
		"x":      x,
		"y":      y,
		"button": button,
	}

	result, err := u.callMcpTool("click", args)
	if err != nil {
		return "", fmt.Errorf("failed to perform click: %w", err)
	}

	return result, nil
}

// Screenshot takes a screenshot and returns the base64 encoded image
func (u *UI) Screenshot() (string, error) {
	args := map[string]interface{}{}

	result, err := u.callMcpTool("system_screenshot", args)
	if err != nil {
		return "", fmt.Errorf("failed to take screenshot: %w", err)
	}

	return result, nil
}
