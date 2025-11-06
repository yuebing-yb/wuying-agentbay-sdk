# Window API Reference

## 🪟 Related Tutorial

- [Window Management Guide](../../../../../docs/guides/computer-use/window-management.md) - Manage application windows

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

## Type WindowActionResult

```go
type WindowActionResult struct {
	models.ApiResponse
	Success	bool
}
```

WindowActionResult represents the result of a window action

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

## Type WindowInfoResult

```go
type WindowInfoResult struct {
	models.ApiResponse
	Window	*WindowInfo
}
```

WindowInfoResult represents the result of getting window information

## Type WindowListResult

```go
type WindowListResult struct {
	models.ApiResponse
	Windows	[]*WindowInfo
}
```

WindowListResult represents the result of listing windows

## Type WindowManager

```go
type WindowManager struct {
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

WindowManager handles window management operations in the AgentBay cloud environment

### Methods

#### ActivateWindow

```go
func (wm *WindowManager) ActivateWindow(windowID int) (*WindowResult, error)
```

ActivateWindow activates a window by ID (original interface)

#### CloseWindow

```go
func (wm *WindowManager) CloseWindow(windowID int) (*WindowResult, error)
```

CloseWindow closes a window by ID (original interface)

#### FocusMode

```go
func (wm *WindowManager) FocusMode(on bool) (*WindowResult, error)
```

FocusMode enables or disables focus mode (original interface)

#### FullscreenWindow

```go
func (wm *WindowManager) FullscreenWindow(windowID int) (*WindowResult, error)
```

FullscreenWindow toggles fullscreen mode for a window by ID (original interface)

#### GetActiveWindow

```go
func (wm *WindowManager) GetActiveWindow() (*WindowDetailResult, error)
```

GetActiveWindow retrieves information about the currently active window (original interface)

#### ListRootWindows

```go
func (wm *WindowManager) ListRootWindows() (*WindowListResult, error)
```

ListRootWindows lists all root windows with their associated information

#### MaximizeWindow

```go
func (wm *WindowManager) MaximizeWindow(windowID int) (*WindowResult, error)
```

MaximizeWindow maximizes a window by ID (original interface)

#### MinimizeWindow

```go
func (wm *WindowManager) MinimizeWindow(windowID int) (*WindowResult, error)
```

MinimizeWindow minimizes a window by ID (original interface)

#### ResizeWindow

```go
func (wm *WindowManager) ResizeWindow(windowID int, width, height int) (*WindowResult, error)
```

ResizeWindow resizes a window by ID (original interface)

#### RestoreWindow

```go
func (wm *WindowManager) RestoreWindow(windowID int) (*WindowResult, error)
```

RestoreWindow restores a window by ID (original interface)

### Related Functions

#### NewWindowManager

```go
func NewWindowManager(session interface {
	GetAPIKey() string
	GetClient() *mcp.Client
	GetSessionId() string
	IsVpc() bool
	NetworkInterfaceIp() string
	HttpPort() string
	FindServerForTool(toolName string) string
	CallMcpTool(toolName string, args interface{}, autoGenSession ...bool) (*models.McpToolResult, error)
}) *WindowManager
```

NewWindowManager creates a new window manager instance

## Type WindowResult

```go
type WindowResult struct {
	models.ApiResponse
	Success	bool
}
```

WindowResult represents the result of a window action

## Related Resources

- [Computer API Reference](computer.md)
- [Application API Reference](application.md)

---

*Documentation generated automatically from Go source code.*
