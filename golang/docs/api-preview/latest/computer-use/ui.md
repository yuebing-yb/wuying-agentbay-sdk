# UI API Reference

## 🎨 Related Tutorial

- [UI Automation Guide](../../../../../docs/guides/computer-use/computer-ui-automation.md) - Automate UI interactions

## Type KeyActionResult

```go
type KeyActionResult struct {
	models.ApiResponse
	Success	bool
}
```

KeyActionResult represents the result of a key action

## Type KeyCode

```go
type KeyCode int
```

KeyCode represents Android UI key codes

## Type ScreenshotResult

```go
type ScreenshotResult struct {
	models.ApiResponse
	ScreenshotURL	string
}
```

ScreenshotResult represents the result of a screenshot operation

## Type SwipeDirection

```go
type SwipeDirection string
```

SwipeDirection represents swipe directions

## Type SwipeResult

```go
type SwipeResult struct {
	models.ApiResponse
	Success	bool
}
```

SwipeResult represents the result of a swipe action

## Type TextInputResult

```go
type TextInputResult struct {
	models.ApiResponse
	Text	string
}
```

TextInputResult represents the result of a text input action

## Type UIActionResult

```go
type UIActionResult struct {
	models.ApiResponse
	Success	bool
}
```

UIActionResult represents the result of a UI action

## Type UIBounds

```go
type UIBounds struct {
	Bottom	int	`json:"bottom"`
	Left	int	`json:"left"`
	Right	int	`json:"right"`
	Top	int	`json:"top"`
}
```

UIBounds represents the bounds of a UI element

## Type UIElement

```go
type UIElement struct {
	Bounds		*UIBounds	`json:"bounds,omitempty"`
	ClassName	string		`json:"className,omitempty"`
	ContentDesc	string		`json:"contentDesc,omitempty"`
	ElementID	string		`json:"elementId,omitempty"`
	Package		string		`json:"package,omitempty"`
	ResourceID	string		`json:"resourceId,omitempty"`
	Text		string		`json:"text,omitempty"`
	Type		string		`json:"type,omitempty"`
}
```

UIElement represents a UI element structure

## Type UIElementsResult

```go
type UIElementsResult struct {
	models.ApiResponse
	Elements	[]*UIElement
}
```

UIElementsResult represents the result containing UI elements

## Type UIManager

```go
type UIManager struct {
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

UIManager manages UI interactions with the session environment

### Methods

#### Click

```go
func (u *UIManager) Click(x, y int, button string) (*UIResult, error)
```

Click performs a click action on the screen (original interface) Deprecated: UI operations have
been moved to platform-specific modules. Use session.Computer.ClickMouse() or session.Mobile.Tap()
instead.

#### GetAllUIElements

```go
func (u *UIManager) GetAllUIElements(timeoutMs int) (*UIElementsResult, error)
```

GetAllUIElements retrieves all UI elements regardless of their clickable status Deprecated:
UI operations have been moved to platform-specific modules. Use session.Mobile.GetAllUIElements()
instead.

#### GetClickableUIElements

```go
func (u *UIManager) GetClickableUIElements(timeoutMs int) (*UIElementsResult, error)
```

GetClickableUIElements retrieves all clickable UI elements Deprecated: UI operations have been moved
to platform-specific modules. Use session.Mobile.GetClickableUIElements() instead.

#### InputText

```go
func (u *UIManager) InputText(text string) (*TextInputResult, error)
```

InputText inputs text into the currently focused UI element (original interface) Deprecated:
UI operations have been moved to platform-specific modules. Use session.Computer.InputText() or
session.Mobile.InputText() instead.

#### Screenshot

```go
func (u *UIManager) Screenshot() (*UIResult, error)
```

Screenshot captures a screenshot of the current screen (original interface) Deprecated:
UI operations have been moved to platform-specific modules. Use session.Computer.Screenshot() or
session.Mobile.Screenshot() instead.

#### SendKey

```go
func (u *UIManager) SendKey(key int) (*KeyActionResult, error)
```

SendKey sends a key event to the UI (original interface) Deprecated: UI operations have been moved
to platform-specific modules. Use session.Mobile.SendKey() instead.

#### Swipe

```go
func (u *UIManager) Swipe(startX, startY, endX, endY, durationMs int) (*SwipeResult, error)
```

Swipe performs a swipe gesture on the screen (original interface) Deprecated: UI operations have
been moved to platform-specific modules. Use session.Mobile.Swipe() instead.

### Related Functions

#### NewUI

```go
func NewUI(session interface {
	GetAPIKey() string
	GetClient() *mcp.Client
	GetSessionId() string
	IsVpc() bool
	NetworkInterfaceIp() string
	HttpPort() string
	FindServerForTool(toolName string) string
	CallMcpTool(toolName string, args interface{}, autoGenSession ...bool) (*models.McpToolResult, error)
}) *UIManager
```

NewUI creates a new UI object

## Type UIResult

```go
type UIResult struct {
	models.ApiResponse
	ComponentID	string
	Success		bool
}
```

UIResult represents the result of a UI action

## Related Resources

- [Computer API Reference](../../computer-use/computer.md)

---

*Documentation generated automatically from Go source code.*
