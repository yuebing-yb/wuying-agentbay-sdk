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
//
// Example:
//
//	package main
//	import (
//		"fmt"
//		"os"
//		"github.com/aliyun/wuying-agentbay-sdk/golang/pkg/agentbay"
//		"github.com/aliyun/wuying-agentbay-sdk/golang/pkg/agentbay/computer"
//	)
//	func main() {
//		client, err := agentbay.NewAgentBay(os.Getenv("AGENTBAY_API_KEY"), nil)
//		if err != nil {
//			fmt.Printf("Error: %v\n", err)
//			os.Exit(1)
//		}
//		params := agentbay.NewCreateSessionParams().WithImageId("windows_latest")
//		result, err := client.Create(params)
//		if err != nil {
//			fmt.Printf("Error: %v\n", err)
//			os.Exit(1)
//		}
//		session := result.Session
//
//		// Click at coordinates (500, 300) with left mouse button
//
//		clickResult := session.Computer.ClickMouse(500, 300, computer.MouseButtonLeft)
//		if clickResult.Success {
//			fmt.Println("Mouse clicked successfully")
//		} else {
//			fmt.Printf("Error: %s\n", clickResult.ErrorMessage)
//		}
//
//		// Double click
//
//		doubleClickResult := session.Computer.ClickMouse(500, 300, computer.MouseButtonDoubleLeft)
//		if doubleClickResult.Success {
//			fmt.Println("Double click successful")
//		}
//
//		session.Delete()
//	}
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
//
// Example:
//
//	package main
//	import (
//		"fmt"
//		"os"
//		"github.com/aliyun/wuying-agentbay-sdk/golang/pkg/agentbay"
//	)
//	func main() {
//		client, err := agentbay.NewAgentBay(os.Getenv("AGENTBAY_API_KEY"), nil)
//		if err != nil {
//			fmt.Printf("Error: %v\n", err)
//			os.Exit(1)
//		}
//		params := agentbay.NewCreateSessionParams().WithImageId("windows_latest")
//		result, err := client.Create(params)
//		if err != nil {
//			fmt.Printf("Error: %v\n", err)
//			os.Exit(1)
//		}
//		session := result.Session
//
//		// Move mouse to coordinates (300, 200)
//
//		moveResult := session.Computer.MoveMouse(300, 200)
//		if moveResult.Success {
//			fmt.Println("Mouse moved successfully")
//		} else {
//			fmt.Printf("Error: %s\n", moveResult.ErrorMessage)
//		}
//		session.Delete()
//	}
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
//
// Example:
//
//	package main
//	import (
//		"fmt"
//		"os"
//		"github.com/aliyun/wuying-agentbay-sdk/golang/pkg/agentbay"
//		"github.com/aliyun/wuying-agentbay-sdk/golang/pkg/agentbay/computer"
//	)
//	func main() {
//		client, err := agentbay.NewAgentBay(os.Getenv("AGENTBAY_API_KEY"), nil)
//		if err != nil {
//			fmt.Printf("Error: %v\n", err)
//			os.Exit(1)
//		}
//		params := agentbay.NewCreateSessionParams().WithImageId("windows_latest")
//		result, err := client.Create(params)
//		if err != nil {
//			fmt.Printf("Error: %v\n", err)
//			os.Exit(1)
//		}
//		session := result.Session
//
//		// Drag from (100, 100) to (300, 300) with left button
//
//		dragResult := session.Computer.DragMouse(100, 100, 300, 300, computer.MouseButtonLeft)
//		if dragResult.Success {
//			fmt.Println("Drag operation successful")
//		} else {
//			fmt.Printf("Error: %s\n", dragResult.ErrorMessage)
//		}
//		session.Delete()
//	}
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
//
// Example:
//
//	package main
//	import (
//		"fmt"
//		"os"
//		"github.com/aliyun/wuying-agentbay-sdk/golang/pkg/agentbay"
//		"github.com/aliyun/wuying-agentbay-sdk/golang/pkg/agentbay/computer"
//	)
//	func main() {
//		client, err := agentbay.NewAgentBay(os.Getenv("AGENTBAY_API_KEY"), nil)
//		if err != nil {
//			fmt.Printf("Error: %v\n", err)
//			os.Exit(1)
//		}
//		params := agentbay.NewCreateSessionParams().WithImageId("windows_latest")
//		result, err := client.Create(params)
//		if err != nil {
//			fmt.Printf("Error: %v\n", err)
//			os.Exit(1)
//		}
//		session := result.Session
//
//		// Scroll down 5 units at coordinates (400, 300)
//
//		scrollResult := session.Computer.Scroll(400, 300, computer.ScrollDirectionDown, 5)
//		if scrollResult.Success {
//			fmt.Println("Scroll operation successful")
//		} else {
//			fmt.Printf("Error: %s\n", scrollResult.ErrorMessage)
//		}
//		session.Delete()
//	}
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
//
// Example:
//
//	package main
//	import (
//		"fmt"
//		"os"
//		"github.com/aliyun/wuying-agentbay-sdk/golang/pkg/agentbay"
//	)
//	func main() {
//		client, err := agentbay.NewAgentBay(os.Getenv("AGENTBAY_API_KEY"), nil)
//		if err != nil {
//			fmt.Printf("Error: %v\n", err)
//			os.Exit(1)
//		}
//		params := agentbay.NewCreateSessionParams().WithImageId("windows_latest")
//		result, err := client.Create(params)
//		if err != nil {
//			fmt.Printf("Error: %v\n", err)
//			os.Exit(1)
//		}
//		session := result.Session
//
//		// Get the current cursor position
//
//		position := session.Computer.GetCursorPosition()
//		if position.ErrorMessage == "" {
//			fmt.Printf("Cursor position: (%d, %d)\n", position.X, position.Y)
//		} else {
//			fmt.Printf("Error: %s\n", position.ErrorMessage)
//		}
//		session.Delete()
//	}
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
//
// Example:
//
//	package main
//	import (
//		"fmt"
//		"os"
//		"github.com/aliyun/wuying-agentbay-sdk/golang/pkg/agentbay"
//	)
//	func main() {
//		client, err := agentbay.NewAgentBay(os.Getenv("AGENTBAY_API_KEY"), nil)
//		if err != nil {
//			fmt.Printf("Error: %v\n", err)
//			os.Exit(1)
//		}
//		params := agentbay.NewCreateSessionParams().WithImageId("windows_latest")
//		result, err := client.Create(params)
//		if err != nil {
//			fmt.Printf("Error: %v\n", err)
//			os.Exit(1)
//		}
//		session := result.Session
//
//		// Input text into the active field
//
//		inputResult := session.Computer.InputText("Hello World")
//		if inputResult.Success {
//			fmt.Println("Text input successful")
//		} else {
//			fmt.Printf("Error: %s\n", inputResult.ErrorMessage)
//		}
//
//		session.Delete()
//	}
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
//
// Example:
//
//	package main
//	import (
//		"fmt"
//		"os"
//		"github.com/aliyun/wuying-agentbay-sdk/golang/pkg/agentbay"
//	)
//	func main() {
//		client, err := agentbay.NewAgentBay(os.Getenv("AGENTBAY_API_KEY"), nil)
//		if err != nil {
//			fmt.Printf("Error: %v\n", err)
//			os.Exit(1)
//		}
//		params := agentbay.NewCreateSessionParams().WithImageId("windows_latest")
//		result, err := client.Create(params)
//		if err != nil {
//			fmt.Printf("Error: %v\n", err)
//			os.Exit(1)
//		}
//		session := result.Session
//
//		// Press Ctrl+C (copy)
//
//		pressResult := session.Computer.PressKeys([]string{"Ctrl", "c"}, false)
//		if pressResult.Success {
//			fmt.Println("Keys pressed successfully")
//		} else {
//			fmt.Printf("Error: %s\n", pressResult.ErrorMessage)
//		}
//		session.Delete()
//	}
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
//
// Example:
//
//	package main
//	import (
//		"fmt"
//		"os"
//		"github.com/aliyun/wuying-agentbay-sdk/golang/pkg/agentbay"
//	)
//	func main() {
//		client, err := agentbay.NewAgentBay(os.Getenv("AGENTBAY_API_KEY"), nil)
//		if err != nil {
//			fmt.Printf("Error: %v\n", err)
//			os.Exit(1)
//		}
//		params := agentbay.NewCreateSessionParams().WithImageId("windows_latest")
//		result, err := client.Create(params)
//		if err != nil {
//			fmt.Printf("Error: %v\n", err)
//			os.Exit(1)
//		}
//		session := result.Session
//
//		// Hold Shift key first
//
//		session.Computer.PressKeys([]string{"Shift"}, true)
//
//		// Release Shift key
//
//		releaseResult := session.Computer.ReleaseKeys([]string{"Shift"})
//		if releaseResult.Success {
//			fmt.Println("Keys released successfully")
//		} else {
//			fmt.Printf("Error: %s\n", releaseResult.ErrorMessage)
//		}
//		session.Delete()
//	}
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
//
// Example:
//
//	package main
//	import (
//		"fmt"
//		"os"
//		"github.com/aliyun/wuying-agentbay-sdk/golang/pkg/agentbay"
//	)
//	func main() {
//		client, err := agentbay.NewAgentBay(os.Getenv("AGENTBAY_API_KEY"), nil)
//		if err != nil {
//			fmt.Printf("Error: %v\n", err)
//			os.Exit(1)
//		}
//		params := agentbay.NewCreateSessionParams().WithImageId("windows_latest")
//		result, err := client.Create(params)
//		if err != nil {
//			fmt.Printf("Error: %v\n", err)
//			os.Exit(1)
//		}
//		session := result.Session
//
//		// Get the screen size
//
//		screenSize := session.Computer.GetScreenSize()
//		if screenSize.ErrorMessage == "" {
//			fmt.Printf("Screen size: %dx%d\n", screenSize.Width, screenSize.Height)
//			fmt.Printf("DPI scaling factor: %.2f\n", screenSize.DpiScalingFactor)
//		} else {
//			fmt.Printf("Error: %s\n", screenSize.ErrorMessage)
//		}
//
//		session.Delete()
//	}
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
//
// Example:
//
//	package main
//	import (
//		"fmt"
//		"os"
//		"github.com/aliyun/wuying-agentbay-sdk/golang/pkg/agentbay"
//	)
//	func main() {
//		client, err := agentbay.NewAgentBay(os.Getenv("AGENTBAY_API_KEY"), nil)
//		if err != nil {
//			fmt.Printf("Error: %v\n", err)
//			os.Exit(1)
//		}
//		params := agentbay.NewCreateSessionParams().WithImageId("windows_latest")
//		result, err := client.Create(params)
//		if err != nil {
//			fmt.Printf("Error: %v\n", err)
//			os.Exit(1)
//		}
//		session := result.Session
//
//		// Take a screenshot of the current screen
//
//		screenshot := session.Computer.Screenshot()
//		if screenshot.ErrorMessage == "" {
//			fmt.Printf("Screenshot URL: %s\n", screenshot.Data)
//		} else {
//			fmt.Printf("Error: %s\n", screenshot.ErrorMessage)
//		}
//
//		session.Delete()
//	}
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
//
// Example:
//
//	package main
//	import (
//		"fmt"
//		"os"
//		"github.com/aliyun/wuying-agentbay-sdk/golang/pkg/agentbay"
//	)
//	func main() {
//		client, err := agentbay.NewAgentBay(os.Getenv("AGENTBAY_API_KEY"), nil)
//		if err != nil {
//			fmt.Printf("Error: %v\n", err)
//			os.Exit(1)
//		}
//		params := agentbay.NewCreateSessionParams().WithImageId("windows_latest")
//		result, err := client.Create(params)
//		if err != nil {
//			fmt.Printf("Error: %v\n", err)
//			os.Exit(1)
//		}
//		session := result.Session
//
//		// Get the currently active window
//
//		windowResult, err := session.Computer.GetActiveWindow()
//		if err != nil {
//			fmt.Printf("Error: %v\n", err)
//			os.Exit(1)
//		}
//		if windowResult.Window != nil {
//			fmt.Printf("Active Window ID: %d\n", windowResult.Window.WindowID)
//			fmt.Printf("Window Title: %s\n", windowResult.Window.Title)
//			fmt.Printf("Process Name: %s\n", windowResult.Window.PName)
//		}
//
//		session.Delete()
//	}
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
//
// Example:
//
//	package main
//	import (
//		"fmt"
//		"os"
//		"github.com/aliyun/wuying-agentbay-sdk/golang/pkg/agentbay"
//	)
//	func main() {
//		client, err := agentbay.NewAgentBay(os.Getenv("AGENTBAY_API_KEY"), nil)
//		if err != nil {
//			fmt.Printf("Error: %v\n", err)
//			os.Exit(1)
//		}
//		params := agentbay.NewCreateSessionParams().WithImageId("windows_latest")
//		result, err := client.Create(params)
//		if err != nil {
//			fmt.Printf("Error: %v\n", err)
//			os.Exit(1)
//		}
//		session := result.Session
//
//		// List all root windows
//
//		windowList, err := session.Computer.ListRootWindows()
//		if err != nil {
//			fmt.Printf("Error: %v\n", err)
//			os.Exit(1)
//		}
//		if len(windowList.Windows) > 0 {
//			targetWindow := windowList.Windows[0]
//			fmt.Printf("Activating window: %s (ID: %d)\n", targetWindow.Title, targetWindow.WindowID)
//
//			// Activate the first window
//
//			activateResult, err := session.Computer.ActivateWindow(targetWindow.WindowID)
//			if err != nil {
//				fmt.Printf("Error: %v\n", err)
//				os.Exit(1)
//			}
//			if activateResult.Success {
//				fmt.Println("Window activated successfully")
//			}
//		}
//
//		session.Delete()
//	}
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
//
// Example:
//
//	package main
//	import (
//		"fmt"
//		"os"
//		"github.com/aliyun/wuying-agentbay-sdk/golang/pkg/agentbay"
//	)
//	func main() {
//		client, err := agentbay.NewAgentBay(os.Getenv("AGENTBAY_API_KEY"), nil)
//		if err != nil {
//			fmt.Printf("Error: %v\n", err)
//			os.Exit(1)
//		}
//		params := agentbay.NewCreateSessionParams().WithImageId("windows_latest")
//		result, err := client.Create(params)
//		if err != nil {
//			fmt.Printf("Error: %v\n", err)
//			os.Exit(1)
//		}
//		session := result.Session
//
//		// List all root windows
//		windowList, err := session.Computer.ListRootWindows()
//		if err != nil {
//			fmt.Printf("Error: %v\n", err)
//			os.Exit(1)
//		}
//		if len(windowList.Windows) > 0 {
//			targetWindow := windowList.Windows[0]
//			fmt.Printf("Closing window: %s (ID: %d)\n", targetWindow.Title, targetWindow.WindowID)
//
//			// Close the window
//			closeResult, err := session.Computer.CloseWindow(targetWindow.WindowID)
//			if err != nil {
//				fmt.Printf("Error: %v\n", err)
//				os.Exit(1)
//			}
//			if closeResult.Success {
//				fmt.Println("Window closed successfully")
//			}
//		}
//		session.Delete()
//	}
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
//
// Example:
//
//	package main
//	import (
//		"fmt"
//		"os"
//		"github.com/aliyun/wuying-agentbay-sdk/golang/pkg/agentbay"
//	)
//	func main() {
//		client, err := agentbay.NewAgentBay(os.Getenv("AGENTBAY_API_KEY"), nil)
//		if err != nil {
//			fmt.Printf("Error: %v\n", err)
//			os.Exit(1)
//		}
//		params := agentbay.NewCreateSessionParams().WithImageId("windows_latest")
//		result, err := client.Create(params)
//		if err != nil {
//			fmt.Printf("Error: %v\n", err)
//			os.Exit(1)
//		}
//		session := result.Session
//
//		// List all root windows
//		windowList, err := session.Computer.ListRootWindows()
//		if err != nil {
//			fmt.Printf("Error: %v\n", err)
//			os.Exit(1)
//		}
//		if len(windowList.Windows) > 0 {
//			targetWindow := windowList.Windows[0]
//			fmt.Printf("Maximizing window: %s (ID: %d)\n", targetWindow.Title, targetWindow.WindowID)
//
//			// Maximize the window
//			maxResult, err := session.Computer.MaximizeWindow(targetWindow.WindowID)
//			if err != nil {
//				fmt.Printf("Error: %v\n", err)
//				os.Exit(1)
//			}
//			if maxResult.Success {
//				fmt.Println("Window maximized successfully")
//			}
//		}
//		session.Delete()
//	}
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
//
// Example:
//
//	package main
//	import (
//		"fmt"
//		"os"
//		"github.com/aliyun/wuying-agentbay-sdk/golang/pkg/agentbay"
//	)
//	func main() {
//		client, err := agentbay.NewAgentBay(os.Getenv("AGENTBAY_API_KEY"), nil)
//		if err != nil {
//			fmt.Printf("Error: %v\n", err)
//			os.Exit(1)
//		}
//		params := agentbay.NewCreateSessionParams().WithImageId("windows_latest")
//		result, err := client.Create(params)
//		if err != nil {
//			fmt.Printf("Error: %v\n", err)
//			os.Exit(1)
//		}
//		session := result.Session
//
//		// List all root windows
//		windowList, err := session.Computer.ListRootWindows()
//		if err != nil {
//			fmt.Printf("Error: %v\n", err)
//			os.Exit(1)
//		}
//		if len(windowList.Windows) > 0 {
//			targetWindow := windowList.Windows[0]
//			fmt.Printf("Minimizing window: %s (ID: %d)\n", targetWindow.Title, targetWindow.WindowID)
//
//			// Minimize the window
//			minResult, err := session.Computer.MinimizeWindow(targetWindow.WindowID)
//			if err != nil {
//				fmt.Printf("Error: %v\n", err)
//				os.Exit(1)
//			}
//			if minResult.Success {
//				fmt.Println("Window minimized successfully")
//			}
//		}
//		session.Delete()
//	}
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
//
// Example:
//
//	package main
//	import (
//		"fmt"
//		"os"
//		"github.com/aliyun/wuying-agentbay-sdk/golang/pkg/agentbay"
//	)
//	func main() {
//		client, err := agentbay.NewAgentBay(os.Getenv("AGENTBAY_API_KEY"), nil)
//		if err != nil {
//			fmt.Printf("Error: %v\n", err)
//			os.Exit(1)
//		}
//		params := agentbay.NewCreateSessionParams().WithImageId("windows_latest")
//		result, err := client.Create(params)
//		if err != nil {
//			fmt.Printf("Error: %v\n", err)
//			os.Exit(1)
//		}
//		session := result.Session
//
//		// Enable focus mode
//
//		focusResult, err := session.Computer.FocusMode(true)
//		if err != nil {
//			fmt.Printf("Error: %v\n", err)
//			os.Exit(1)
//		}
//		if focusResult.Success {
//			fmt.Println("Focus mode enabled")
//		}
//
//		// Disable focus mode
//
//		unfocusResult, err := session.Computer.FocusMode(false)
//		if err != nil {
//			fmt.Printf("Error: %v\n", err)
//			os.Exit(1)
//		}
//		if unfocusResult.Success {
//			fmt.Println("Focus mode disabled")
//		}
//
//		session.Delete()
//	}
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
