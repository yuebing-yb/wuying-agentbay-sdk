# Computer API Reference

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
func (c *Computer) ActivateWindow(windowID int) (*window.WindowResult, error)
```

ActivateWindow activates the specified window

#### ClickMouse

```go
func (c *Computer) ClickMouse(x, y int, button MouseButton) *BoolResult
```

ClickMouse clicks the mouse at the specified coordinates

#### CloseWindow

```go
func (c *Computer) CloseWindow(windowID int) (*window.WindowResult, error)
```

CloseWindow closes the specified window

#### DragMouse

```go
func (c *Computer) DragMouse(fromX, fromY, toX, toY int, button MouseButton) *BoolResult
```

DragMouse drags the mouse from one point to another

#### FocusMode

```go
func (c *Computer) FocusMode(on bool) (*window.WindowResult, error)
```

FocusMode toggles focus mode on or off

#### FullscreenWindow

```go
func (c *Computer) FullscreenWindow(windowID int) (*window.WindowResult, error)
```

FullscreenWindow makes the specified window fullscreen

#### GetActiveWindow

```go
func (c *Computer) GetActiveWindow(timeoutMs ...int) (*window.WindowDetailResult, error)
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

#### InputText

```go
func (c *Computer) InputText(text string) *BoolResult
```

InputText inputs text into the active field

#### ListRootWindows

```go
func (c *Computer) ListRootWindows(timeoutMs ...int) (*window.WindowListResult, error)
```

ListRootWindows lists all root windows

#### MaximizeWindow

```go
func (c *Computer) MaximizeWindow(windowID int) (*window.WindowResult, error)
```

MaximizeWindow maximizes the specified window

#### MinimizeWindow

```go
func (c *Computer) MinimizeWindow(windowID int) (*window.WindowResult, error)
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
func (c *Computer) ResizeWindow(windowID int, width int, height int) (*window.WindowResult, error)
```

ResizeWindow resizes the specified window

#### RestoreWindow

```go
func (c *Computer) RestoreWindow(windowID int) (*window.WindowResult, error)
```

RestoreWindow restores the specified window

#### Screenshot

```go
func (c *Computer) Screenshot() *ScreenshotResult
```

Screenshot takes a screenshot of the current screen

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

---

*Documentation generated automatically from Go source code.*
