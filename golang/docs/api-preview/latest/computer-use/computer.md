# Computer API Reference

## 🖥️ Related Tutorial

- [Computer Use Guide](../../../../../docs/guides/computer-use/README.md) - Automate desktop applications

## Overview

The Computer module provides comprehensive desktop automation capabilities including mouse operations,
keyboard input, screen capture, and window management. It enables automated UI testing and RPA workflows.

## Requirements

- Requires `windows_latest` image for computer use features

## Data Types

### MouseButton

Mouse button constants: Left, Right, Middle

### ScrollDirection

Scroll direction constants: Up, Down, Left, Right

### KeyModifier

Keyboard modifier keys: Ctrl, Alt, Shift, Win

## Important Notes

- Key names in PressKeys and ReleaseKeys are case-sensitive
- Coordinate validation: x and y must be non-negative integers
- Drag operation requires valid start and end coordinates
- Screenshot operations may have size limitations

## Type BoolResult

```go
type BoolResult struct {
	models.ApiResponse
	Success		bool	`json:"success"`
	ErrorMessage	string	`json:"error_message"`
}
```

BoolResult represents a boolean operation result

## Type Computer

```go
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
```

Computer handles computer UI automation operations in the AgentBay cloud environment. Provides
comprehensive desktop automation capabilities including mouse, keyboard, window management,
application management, and screen operations.

### Methods

#### ActivateWindow

```go
func (c *Computer) ActivateWindow(windowID int) (*WindowResult, error)
```

ActivateWindow activates the specified window

#### ClickMouse

```go
func (c *Computer) ClickMouse(x, y int, button MouseButton) *BoolResult
```

ClickMouse clicks the mouse at the specified coordinates

**Example:**

```go
package main
import (
	"fmt"
	"os"
	"github.com/aliyun/wuying-agentbay-sdk/golang/pkg/agentbay"
	"github.com/aliyun/wuying-agentbay-sdk/golang/pkg/agentbay/computer"
)
func main() {
	client, err := agentbay.NewAgentBay(os.Getenv("AGENTBAY_API_KEY"), nil)
	if err != nil {
		fmt.Printf("Error: %v\n", err)
		os.Exit(1)
	}
	params := agentbay.NewCreateSessionParams().WithImageId("windows_latest")
	result, err := client.Create(params)
	if err != nil {
		fmt.Printf("Error: %v\n", err)
		os.Exit(1)
	}
	session := result.Session

	// Click at coordinates (500, 300) with left mouse button

	clickResult := session.Computer.ClickMouse(500, 300, computer.MouseButtonLeft)
	if clickResult.Success {
		fmt.Println("Mouse clicked successfully")
	} else {
		fmt.Printf("Error: %s\n", clickResult.ErrorMessage)
	}

	// Double click

	doubleClickResult := session.Computer.ClickMouse(500, 300, computer.MouseButtonDoubleLeft)
	if doubleClickResult.Success {
		fmt.Println("Double click successful")
	}
	session.Delete()
}
```

#### CloseWindow

```go
func (c *Computer) CloseWindow(windowID int) (*WindowResult, error)
```

CloseWindow closes the specified window

#### DragMouse

```go
func (c *Computer) DragMouse(fromX, fromY, toX, toY int, button MouseButton) *BoolResult
```

DragMouse drags the mouse from one point to another

#### FocusMode

```go
func (c *Computer) FocusMode(on bool) (*WindowResult, error)
```

FocusMode toggles focus mode on or off

#### FullscreenWindow

```go
func (c *Computer) FullscreenWindow(windowID int) (*WindowResult, error)
```

FullscreenWindow makes the specified window fullscreen

#### GetActiveWindow

```go
func (c *Computer) GetActiveWindow(timeoutMs ...int) (*WindowDetailResult, error)
```

GetActiveWindow gets the currently active window

#### GetCursorPosition

```go
func (c *Computer) GetCursorPosition() *CursorPosition
```

GetCursorPosition gets the current cursor position

#### GetScreenSize

```go
func (c *Computer) GetScreenSize() *ScreenSize
```

GetScreenSize gets the size of the primary screen

**Example:**

```go
package main
import (
	"fmt"
	"os"
	"github.com/aliyun/wuying-agentbay-sdk/golang/pkg/agentbay"
)
func main() {
	client, err := agentbay.NewAgentBay(os.Getenv("AGENTBAY_API_KEY"), nil)
	if err != nil {
		fmt.Printf("Error: %v\n", err)
		os.Exit(1)
	}
	params := agentbay.NewCreateSessionParams().WithImageId("windows_latest")
	result, err := client.Create(params)
	if err != nil {
		fmt.Printf("Error: %v\n", err)
		os.Exit(1)
	}
	session := result.Session

	// Get the screen size

	screenSize := session.Computer.GetScreenSize()
	if screenSize.ErrorMessage == "" {
		fmt.Printf("Screen size: %dx%d\n", screenSize.Width, screenSize.Height)
		fmt.Printf("DPI scaling factor: %.2f\n", screenSize.DpiScalingFactor)
	} else {
		fmt.Printf("Error: %s\n", screenSize.ErrorMessage)
	}
	session.Delete()
}
```

#### InputText

```go
func (c *Computer) InputText(text string) *BoolResult
```

InputText inputs text into the active field

**Example:**

```go
package main
import (
	"fmt"
	"os"
	"github.com/aliyun/wuying-agentbay-sdk/golang/pkg/agentbay"
)
func main() {
	client, err := agentbay.NewAgentBay(os.Getenv("AGENTBAY_API_KEY"), nil)
	if err != nil {
		fmt.Printf("Error: %v\n", err)
		os.Exit(1)
	}
	params := agentbay.NewCreateSessionParams().WithImageId("windows_latest")
	result, err := client.Create(params)
	if err != nil {
		fmt.Printf("Error: %v\n", err)
		os.Exit(1)
	}
	session := result.Session

	// Input text into the active field

	inputResult := session.Computer.InputText("Hello World")
	if inputResult.Success {
		fmt.Println("Text input successful")
	} else {
		fmt.Printf("Error: %s\n", inputResult.ErrorMessage)
	}
	session.Delete()
}
```

#### ListRootWindows

```go
func (c *Computer) ListRootWindows(timeoutMs ...int) (*WindowListResult, error)
```

ListRootWindows lists all root windows

#### MaximizeWindow

```go
func (c *Computer) MaximizeWindow(windowID int) (*WindowResult, error)
```

MaximizeWindow maximizes the specified window

#### MinimizeWindow

```go
func (c *Computer) MinimizeWindow(windowID int) (*WindowResult, error)
```

MinimizeWindow minimizes the specified window

#### MoveMouse

```go
func (c *Computer) MoveMouse(x, y int) *BoolResult
```

MoveMouse moves the mouse cursor to specific coordinates

#### PressKeys

```go
func (c *Computer) PressKeys(keys []string, hold bool) *BoolResult
```

PressKeys presses multiple keyboard keys simultaneously

#### ReleaseKeys

```go
func (c *Computer) ReleaseKeys(keys []string) *BoolResult
```

ReleaseKeys releases multiple keyboard keys

#### ResizeWindow

```go
func (c *Computer) ResizeWindow(windowID int, width int, height int) (*WindowResult, error)
```

ResizeWindow resizes the specified window

#### RestoreWindow

```go
func (c *Computer) RestoreWindow(windowID int) (*WindowResult, error)
```

RestoreWindow restores the specified window

#### Screenshot

```go
func (c *Computer) Screenshot() *ScreenshotResult
```

Screenshot takes a screenshot of the current screen

**Example:**

```go
package main
import (
	"fmt"
	"os"
	"github.com/aliyun/wuying-agentbay-sdk/golang/pkg/agentbay"
)
func main() {
	client, err := agentbay.NewAgentBay(os.Getenv("AGENTBAY_API_KEY"), nil)
	if err != nil {
		fmt.Printf("Error: %v\n", err)
		os.Exit(1)
	}
	params := agentbay.NewCreateSessionParams().WithImageId("windows_latest")
	result, err := client.Create(params)
	if err != nil {
		fmt.Printf("Error: %v\n", err)
		os.Exit(1)
	}
	session := result.Session

	// Take a screenshot of the current screen

	screenshot := session.Computer.Screenshot()
	if screenshot.ErrorMessage == "" {
		fmt.Printf("Screenshot URL: %s\n", screenshot.Data)
	} else {
		fmt.Printf("Error: %s\n", screenshot.ErrorMessage)
	}
	session.Delete()
}
```

#### Scroll

```go
func (c *Computer) Scroll(x, y int, direction ScrollDirection, amount int) *BoolResult
```

Scroll scrolls the mouse wheel at specific coordinates

### Related Functions

#### NewComputer

```go
func NewComputer(session interface {
	GetAPIKey() string
	GetClient() *mcp.Client
	GetSessionId() string
	IsVpc() bool
	NetworkInterfaceIp() string
	HttpPort() string
	FindServerForTool(toolName string) string
	CallMcpTool(toolName string, args interface{}, autoGenSession ...bool) (*models.McpToolResult, error)
}) *Computer
```

NewComputer creates a new Computer instance

## Type CursorPosition

```go
type CursorPosition struct {
	models.ApiResponse
	X		int	`json:"x"`
	Y		int	`json:"y"`
	ErrorMessage	string	`json:"error_message"`
}
```

CursorPosition represents the cursor position on screen

## Type MouseButton

```go
type MouseButton string
```

MouseButton represents mouse button types

## Type ScreenSize

```go
type ScreenSize struct {
	models.ApiResponse
	Width			int	`json:"width"`
	Height			int	`json:"height"`
	DpiScalingFactor	float64	`json:"dpiScalingFactor"`
	ErrorMessage		string	`json:"error_message"`
}
```

ScreenSize represents the screen dimensions

## Type ScreenshotResult

```go
type ScreenshotResult struct {
	models.ApiResponse
	Data		string	`json:"data"`
	ErrorMessage	string	`json:"error_message"`
}
```

ScreenshotResult represents the result of a screenshot operation

## Type ScrollDirection

```go
type ScrollDirection string
```

ScrollDirection represents scroll directions

## Type Window

```go
type Window struct {
	WindowID		int		`json:"window_id"`
	Title			string		`json:"title"`
	AbsoluteUpperLeftX	int		`json:"absolute_upper_left_x,omitempty"`
	AbsoluteUpperLeftY	int		`json:"absolute_upper_left_y,omitempty"`
	Width			int		`json:"width,omitempty"`
	Height			int		`json:"height,omitempty"`
	PID			int		`json:"pid,omitempty"`
	PName			string		`json:"pname,omitempty"`
	ChildWindows		[]Window	`json:"child_windows,omitempty"`
}
```

Window represents a window in the system

## Type WindowDetailResult

```go
type WindowDetailResult struct {
	models.ApiResponse
	Window	*Window
}
```

WindowDetailResult represents the result of getting window details

## Type WindowInfo

```go
type WindowInfo struct {
	WindowID	int	`json:"window_id"`
	Title		string	`json:"title"`
	PID		int	`json:"pid"`
	PName		string	`json:"pname"`
}
```

WindowInfo represents window information

## Type WindowListResult

```go
type WindowListResult struct {
	models.ApiResponse
	Windows	[]*WindowInfo
}
```

WindowListResult represents the result of listing windows

## Type WindowResult

```go
type WindowResult struct {
	models.ApiResponse
	Success	bool
}
```

WindowResult represents the result of a window action

## Best Practices

1. Verify screen coordinates before mouse operations
2. Use appropriate delays between UI interactions
3. Handle window focus changes properly
4. Take screenshots for verification and debugging
5. Use keyboard shortcuts for efficient automation
6. Clean up windows and applications after automation

## Related Resources

- [Application API Reference](application.md)
- [UI API Reference](ui.md)
- [Window API Reference](window.md)

---

*Documentation generated automatically from Go source code.*
