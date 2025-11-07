package computer

import (
	"encoding/json"
	"fmt"

	mcp "github.com/aliyun/wuying-agentbay-sdk/golang/api/client"
	"github.com/aliyun/wuying-agentbay-sdk/golang/pkg/agentbay/models"
)

// MouseButton represents mouse button types
type MouseButton string

const (
	MouseButtonLeft       MouseButton = "left"
	MouseButtonRight      MouseButton = "right"
	MouseButtonMiddle     MouseButton = "middle"
	MouseButtonDoubleLeft MouseButton = "double_left"
)

// ScrollDirection represents scroll directions
type ScrollDirection string

const (
	ScrollDirectionUp    ScrollDirection = "up"
	ScrollDirectionDown  ScrollDirection = "down"
	ScrollDirectionLeft  ScrollDirection = "left"
	ScrollDirectionRight ScrollDirection = "right"
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

// WindowInfo represents window information
type WindowInfo struct {
	WindowID int    `json:"window_id"`
	Title    string `json:"title"`
	PID      int    `json:"pid"`
	PName    string `json:"pname"`
}

// WindowListResult represents the result of listing windows
type WindowListResult struct {
	models.ApiResponse
	Windows []*WindowInfo
}

// WindowDetailResult represents the result of getting window details
type WindowDetailResult struct {
	models.ApiResponse
	Window *Window
}

// WindowResult represents the result of a window action
type WindowResult struct {
	models.ApiResponse
	Success bool
}

// CursorPosition represents the cursor position on screen
type CursorPosition struct {
	models.ApiResponse
	X            int    `json:"x"`
	Y            int    `json:"y"`
	ErrorMessage string `json:"error_message"`
}

// ScreenSize represents the screen dimensions
type ScreenSize struct {
	models.ApiResponse
	Width            int     `json:"width"`
	Height           int     `json:"height"`
	DpiScalingFactor float64 `json:"dpiScalingFactor"`
	ErrorMessage     string  `json:"error_message"`
}

// ScreenshotResult represents the result of a screenshot operation
type ScreenshotResult struct {
	models.ApiResponse
	Data         string `json:"data"`
	ErrorMessage string `json:"error_message"`
}

// BoolResult represents a boolean operation result
type BoolResult struct {
	models.ApiResponse
	Success      bool   `json:"success"`
	ErrorMessage string `json:"error_message"`
}

// Computer handles computer UI automation operations in the AgentBay cloud environment.
// Provides comprehensive desktop automation capabilities including mouse, keyboard,
// window management, application management, and screen operations.
type Computer struct {
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

// NewComputer creates a new Computer instance
func NewComputer(session interface {
	GetAPIKey() string
	GetClient() *mcp.Client
	GetSessionId() string
	IsVpc() bool
	NetworkInterfaceIp() string
	HttpPort() string
	FindServerForTool(toolName string) string
	CallMcpTool(toolName string, args interface{}, autoGenSession ...bool) (*models.McpToolResult, error)
}) *Computer {
	return &Computer{Session: session}
}

// ClickMouse clicks the mouse at the specified coordinates
func (c *Computer) ClickMouse(x, y int, button MouseButton) *BoolResult {
	// Validate button parameter
	validButtons := []MouseButton{MouseButtonLeft, MouseButtonRight, MouseButtonMiddle, MouseButtonDoubleLeft}
	isValid := false
	for _, validButton := range validButtons {
		if button == validButton {
			isValid = true
			break
		}
	}
	if !isValid {
		return &BoolResult{
			ApiResponse: models.ApiResponse{
				RequestID: "",
			},
			Success:      false,
			ErrorMessage: fmt.Sprintf("invalid button: %s. Valid options: %v", button, validButtons),
		}
	}

	args := map[string]interface{}{
		"x":      x,
		"y":      y,
		"button": string(button),
	}

	result, err := c.Session.CallMcpTool("click_mouse", args)
	if err != nil {
		return &BoolResult{
			ApiResponse: models.ApiResponse{
				RequestID: "",
			},
			Success:      false,
			ErrorMessage: fmt.Sprintf("failed to call click_mouse: %v", err),
		}
	}

	return &BoolResult{
		ApiResponse: models.ApiResponse{
			RequestID: result.RequestID,
		},
		Success:      result.Success,
		ErrorMessage: result.ErrorMessage,
	}
}

// MoveMouse moves the mouse cursor to specific coordinates
func (c *Computer) MoveMouse(x, y int) *BoolResult {
	args := map[string]interface{}{
		"x": x,
		"y": y,
	}

	result, err := c.Session.CallMcpTool("move_mouse", args)
	if err != nil {
		return &BoolResult{
			ApiResponse: models.ApiResponse{
				RequestID: "",
			},
			Success:      false,
			ErrorMessage: fmt.Sprintf("failed to call move_mouse: %v", err),
		}
	}

	return &BoolResult{
		ApiResponse: models.ApiResponse{
			RequestID: result.RequestID,
		},
		Success:      result.Success,
		ErrorMessage: result.ErrorMessage,
	}
}

// DragMouse drags the mouse from one point to another
func (c *Computer) DragMouse(fromX, fromY, toX, toY int, button MouseButton) *BoolResult {
	// Validate button parameter
	validButtons := []MouseButton{MouseButtonLeft, MouseButtonRight, MouseButtonMiddle}
	isValid := false
	for _, validButton := range validButtons {
		if button == validButton {
			isValid = true
			break
		}
	}
	if !isValid {
		return &BoolResult{
			ApiResponse: models.ApiResponse{
				RequestID: "",
			},
			Success:      false,
			ErrorMessage: fmt.Sprintf("invalid button: %s. Valid options: %v", button, validButtons),
		}
	}

	args := map[string]interface{}{
		"from_x": fromX,
		"from_y": fromY,
		"to_x":   toX,
		"to_y":   toY,
		"button": string(button),
	}

	result, err := c.Session.CallMcpTool("drag_mouse", args)
	if err != nil {
		return &BoolResult{
			ApiResponse: models.ApiResponse{
				RequestID: "",
			},
			Success:      false,
			ErrorMessage: fmt.Sprintf("failed to call drag_mouse: %v", err),
		}
	}

	return &BoolResult{
		ApiResponse: models.ApiResponse{
			RequestID: result.RequestID,
		},
		Success:      result.Success,
		ErrorMessage: result.ErrorMessage,
	}
}

// Scroll scrolls the mouse wheel at specific coordinates
func (c *Computer) Scroll(x, y int, direction ScrollDirection, amount int) *BoolResult {
	// Validate direction parameter
	validDirections := []ScrollDirection{ScrollDirectionUp, ScrollDirectionDown, ScrollDirectionLeft, ScrollDirectionRight}
	isValid := false
	for _, validDirection := range validDirections {
		if direction == validDirection {
			isValid = true
			break
		}
	}
	if !isValid {
		return &BoolResult{
			ApiResponse: models.ApiResponse{
				RequestID: "",
			},
			Success:      false,
			ErrorMessage: fmt.Sprintf("invalid direction: %s. Valid options: %v", direction, validDirections),
		}
	}

	args := map[string]interface{}{
		"x":         x,
		"y":         y,
		"direction": string(direction),
		"amount":    amount,
	}

	result, err := c.Session.CallMcpTool("scroll", args)
	if err != nil {
		return &BoolResult{
			ApiResponse: models.ApiResponse{
				RequestID: "",
			},
			Success:      false,
			ErrorMessage: fmt.Sprintf("failed to call scroll: %v", err),
		}
	}

	return &BoolResult{
		ApiResponse: models.ApiResponse{
			RequestID: result.RequestID,
		},
		Success:      result.Success,
		ErrorMessage: result.ErrorMessage,
	}
}

// GetCursorPosition gets the current cursor position
func (c *Computer) GetCursorPosition() *CursorPosition {
	args := map[string]interface{}{}

	result, err := c.Session.CallMcpTool("get_cursor_position", args)
	if err != nil {
		return &CursorPosition{
			ApiResponse: models.ApiResponse{
				RequestID: "",
			},
			ErrorMessage: fmt.Sprintf("failed to call get_cursor_position: %v", err),
		}
	}

	if !result.Success {
		return &CursorPosition{
			ApiResponse: models.ApiResponse{
				RequestID: result.RequestID,
			},
			ErrorMessage: result.ErrorMessage,
		}
	}

	// Parse cursor position from JSON
	var position struct {
		X int `json:"x"`
		Y int `json:"y"`
	}
	if err := json.Unmarshal([]byte(result.Data), &position); err != nil {
		return &CursorPosition{
			ApiResponse: models.ApiResponse{
				RequestID: result.RequestID,
			},
			ErrorMessage: fmt.Sprintf("failed to parse cursor position: %v", err),
		}
	}

	return &CursorPosition{
		ApiResponse: models.ApiResponse{
			RequestID: result.RequestID,
		},
		X:            position.X,
		Y:            position.Y,
		ErrorMessage: result.ErrorMessage,
	}
}

// InputText inputs text into the active field
func (c *Computer) InputText(text string) *BoolResult {
	args := map[string]interface{}{
		"text": text,
	}

	result, err := c.Session.CallMcpTool("input_text", args)
	if err != nil {
		return &BoolResult{
			ApiResponse: models.ApiResponse{
				RequestID: "",
			},
			Success:      false,
			ErrorMessage: fmt.Sprintf("failed to call input_text: %v", err),
		}
	}

	return &BoolResult{
		ApiResponse: models.ApiResponse{
			RequestID: result.RequestID,
		},
		Success:      result.Success,
		ErrorMessage: result.ErrorMessage,
	}
}

// PressKeys presses multiple keyboard keys simultaneously
func (c *Computer) PressKeys(keys []string, hold bool) *BoolResult {
	args := map[string]interface{}{
		"keys": keys,
		"hold": hold,
	}

	result, err := c.Session.CallMcpTool("press_keys", args)
	if err != nil {
		return &BoolResult{
			ApiResponse: models.ApiResponse{
				RequestID: "",
			},
			Success:      false,
			ErrorMessage: fmt.Sprintf("failed to call press_keys: %v", err),
		}
	}

	return &BoolResult{
		ApiResponse: models.ApiResponse{
			RequestID: result.RequestID,
		},
		Success:      result.Success,
		ErrorMessage: result.ErrorMessage,
	}
}

// ReleaseKeys releases multiple keyboard keys
func (c *Computer) ReleaseKeys(keys []string) *BoolResult {
	args := map[string]interface{}{
		"keys": keys,
	}

	result, err := c.Session.CallMcpTool("release_keys", args)
	if err != nil {
		return &BoolResult{
			ApiResponse: models.ApiResponse{
				RequestID: "",
			},
			Success:      false,
			ErrorMessage: fmt.Sprintf("failed to call release_keys: %v", err),
		}
	}

	return &BoolResult{
		ApiResponse: models.ApiResponse{
			RequestID: result.RequestID,
		},
		Success:      result.Success,
		ErrorMessage: result.ErrorMessage,
	}
}

// GetScreenSize gets the size of the primary screen
func (c *Computer) GetScreenSize() *ScreenSize {
	args := map[string]interface{}{}

	result, err := c.Session.CallMcpTool("get_screen_size", args)
	if err != nil {
		return &ScreenSize{
			ApiResponse: models.ApiResponse{
				RequestID: "",
			},
			ErrorMessage: fmt.Sprintf("failed to call get_screen_size: %v", err),
		}
	}

	if !result.Success {
		return &ScreenSize{
			ApiResponse: models.ApiResponse{
				RequestID: result.RequestID,
			},
			ErrorMessage: result.ErrorMessage,
		}
	}

	// Parse screen size from JSON
	var size struct {
		Width            int     `json:"width"`
		Height           int     `json:"height"`
		DpiScalingFactor float64 `json:"dpiScalingFactor"`
	}
	if err := json.Unmarshal([]byte(result.Data), &size); err != nil {
		return &ScreenSize{
			ApiResponse: models.ApiResponse{
				RequestID: result.RequestID,
			},
			ErrorMessage: fmt.Sprintf("failed to parse screen size: %v", err),
		}
	}

	return &ScreenSize{
		ApiResponse: models.ApiResponse{
			RequestID: result.RequestID,
		},
		Width:            size.Width,
		Height:           size.Height,
		DpiScalingFactor: size.DpiScalingFactor,
		ErrorMessage:     result.ErrorMessage,
	}
}

// Screenshot takes a screenshot of the current screen
func (c *Computer) Screenshot() *ScreenshotResult {
	args := map[string]interface{}{}

	result, err := c.Session.CallMcpTool("system_screenshot", args)
	if err != nil {
		return &ScreenshotResult{
			ApiResponse: models.ApiResponse{
				RequestID: "",
			},
			ErrorMessage: fmt.Sprintf("failed to call system_screenshot: %v", err),
		}
	}

	return &ScreenshotResult{
		ApiResponse: models.ApiResponse{
			RequestID: result.RequestID,
		},
		Data:         result.Data,
		ErrorMessage: result.ErrorMessage,
	}
}

// ListRootWindows lists all root windows
func (c *Computer) ListRootWindows(timeoutMs ...int) (*WindowListResult, error) {
	args := map[string]interface{}{}

	result, err := c.Session.CallMcpTool("list_root_windows", args)
	if err != nil {
		return nil, fmt.Errorf("error listing root windows: %w", err)
	}

	if !result.Success {
		return nil, fmt.Errorf("error listing root windows: %s", result.ErrorMessage)
	}

	var windows []*WindowInfo
	if err := json.Unmarshal([]byte(result.Data), &windows); err != nil {
		return nil, fmt.Errorf("failed to parse window information: %w", err)
	}

	return &WindowListResult{
		ApiResponse: models.ApiResponse{
			RequestID: result.RequestID,
		},
		Windows: windows,
	}, nil
}

// GetActiveWindow gets the currently active window
func (c *Computer) GetActiveWindow(timeoutMs ...int) (*WindowDetailResult, error) {
	args := map[string]interface{}{}

	result, err := c.Session.CallMcpTool("get_active_window", args)
	if err != nil {
		return nil, fmt.Errorf("error getting active window: %w", err)
	}

	if !result.Success {
		return nil, fmt.Errorf("error getting active window: %s", result.ErrorMessage)
	}

	var window Window
	if err := json.Unmarshal([]byte(result.Data), &window); err != nil {
		return nil, fmt.Errorf("failed to parse window information: %w", err)
	}

	return &WindowDetailResult{
		ApiResponse: models.ApiResponse{
			RequestID: result.RequestID,
		},
		Window: &window,
	}, nil
}

// ActivateWindow activates the specified window
func (c *Computer) ActivateWindow(windowID int) (*WindowResult, error) {
	args := map[string]interface{}{
		"window_id": windowID,
	}

	result, err := c.Session.CallMcpTool("activate_window", args)
	if err != nil {
		return nil, fmt.Errorf("error activating window: %w", err)
	}

	return &WindowResult{
		ApiResponse: models.ApiResponse{
			RequestID: result.RequestID,
		},
		Success: result.Success,
	}, nil
}

// CloseWindow closes the specified window
func (c *Computer) CloseWindow(windowID int) (*WindowResult, error) {
	args := map[string]interface{}{
		"window_id": windowID,
	}

	result, err := c.Session.CallMcpTool("close_window", args)
	if err != nil {
		return nil, fmt.Errorf("error closing window: %w", err)
	}

	return &WindowResult{
		ApiResponse: models.ApiResponse{
			RequestID: result.RequestID,
		},
		Success: result.Success,
	}, nil
}

// MaximizeWindow maximizes the specified window
func (c *Computer) MaximizeWindow(windowID int) (*WindowResult, error) {
	args := map[string]interface{}{
		"window_id": windowID,
	}

	result, err := c.Session.CallMcpTool("maximize_window", args)
	if err != nil {
		return nil, fmt.Errorf("error maximizing window: %w", err)
	}

	return &WindowResult{
		ApiResponse: models.ApiResponse{
			RequestID: result.RequestID,
		},
		Success: result.Success,
	}, nil
}

// MinimizeWindow minimizes the specified window
func (c *Computer) MinimizeWindow(windowID int) (*WindowResult, error) {
	args := map[string]interface{}{
		"window_id": windowID,
	}

	result, err := c.Session.CallMcpTool("minimize_window", args)
	if err != nil {
		return nil, fmt.Errorf("error minimizing window: %w", err)
	}

	return &WindowResult{
		ApiResponse: models.ApiResponse{
			RequestID: result.RequestID,
		},
		Success: result.Success,
	}, nil
}

// RestoreWindow restores the specified window
func (c *Computer) RestoreWindow(windowID int) (*WindowResult, error) {
	args := map[string]interface{}{
		"window_id": windowID,
	}

	result, err := c.Session.CallMcpTool("restore_window", args)
	if err != nil {
		return nil, fmt.Errorf("error restoring window: %w", err)
	}

	return &WindowResult{
		ApiResponse: models.ApiResponse{
			RequestID: result.RequestID,
		},
		Success: result.Success,
	}, nil
}

// ResizeWindow resizes the specified window
func (c *Computer) ResizeWindow(windowID int, width int, height int) (*WindowResult, error) {
	args := map[string]interface{}{
		"window_id": windowID,
		"width":     width,
		"height":    height,
	}

	result, err := c.Session.CallMcpTool("resize_window", args)
	if err != nil {
		return nil, fmt.Errorf("error resizing window: %w", err)
	}

	return &WindowResult{
		ApiResponse: models.ApiResponse{
			RequestID: result.RequestID,
		},
		Success: result.Success,
	}, nil
}

// FullscreenWindow makes the specified window fullscreen
func (c *Computer) FullscreenWindow(windowID int) (*WindowResult, error) {
	args := map[string]interface{}{
		"window_id": windowID,
	}

	result, err := c.Session.CallMcpTool("fullscreen_window", args)
	if err != nil {
		return nil, fmt.Errorf("error making window fullscreen: %w", err)
	}

	return &WindowResult{
		ApiResponse: models.ApiResponse{
			RequestID: result.RequestID,
		},
		Success: result.Success,
	}, nil
}

// FocusMode toggles focus mode on or off
func (c *Computer) FocusMode(on bool) (*WindowResult, error) {
	args := map[string]interface{}{
		"on": on,
	}

	result, err := c.Session.CallMcpTool("focus_mode", args)
	if err != nil {
		return nil, fmt.Errorf("error toggling focus mode: %w", err)
	}

	return &WindowResult{
		ApiResponse: models.ApiResponse{
			RequestID: result.RequestID,
		},
		Success: result.Success,
	}, nil
}
