# Mobile API Reference

## 📱 Related Tutorial

- [Mobile Use Guide](../../../../../docs/guides/mobile-use/README.md) - Automate mobile applications

## Overview

The Mobile module provides mobile device automation capabilities including touch gestures,
text input, app management, and screenshot capture. It supports Android device automation.

## Requirements

- Requires `mobile_latest` image for mobile automation features

## Type AdbUrlResult

```go
type AdbUrlResult struct {
	models.ApiResponse
	URL		string	`json:"url"`
	Success		bool	`json:"success"`
	ErrorMessage	string	`json:"error_message"`
}
```

AdbUrlResult represents the result of ADB URL retrieval operation

## Type BoolResult

```go
type BoolResult struct {
	models.ApiResponse
	Success		bool	`json:"success"`
	ErrorMessage	string	`json:"error_message"`
}
```

BoolResult represents a boolean operation result

## Type InstalledApp

```go
type InstalledApp struct {
	Name		string	`json:"name"`
	StartCmd	string	`json:"start_cmd"`
	StopCmd		string	`json:"stop_cmd,omitempty"`
	WorkDirectory	string	`json:"work_directory,omitempty"`
}
```

InstalledApp represents an installed application

## Type InstalledAppListResult

```go
type InstalledAppListResult struct {
	models.ApiResponse
	Apps		[]InstalledApp	`json:"apps"`
	ErrorMessage	string		`json:"error_message"`
}
```

InstalledAppListResult wraps installed app list and RequestID

## Type Mobile

```go
type Mobile struct {
	Session	interface {
		GetAPIKey() string
		GetClient() *mcp.Client
		GetSessionId() string
		GetImageID() string
		IsVpc() bool
		NetworkInterfaceIp() string
		HttpPort() string
		FindServerForTool(toolName string) string
		CallMcpTool(toolName string, args interface{}, autoGenSession ...bool) (*models.McpToolResult, error)
	}
	command	*command.Command
}
```

Mobile handles mobile UI automation operations and configuration in the AgentBay cloud environment.
Provides touch operations, UI element interactions, application management, screenshot capabilities,
and mobile environment configuration.

### Methods

#### Configure

```go
func (m *Mobile) Configure(mobileConfig *models.MobileExtraConfig) error
```

Configure configures mobile settings from MobileExtraConfig

#### GetAdbUrl

```go
func (m *Mobile) GetAdbUrl(adbkeyPub string) *AdbUrlResult
```

GetAdbUrl retrieves the ADB connection URL for the mobile environment. This method is only supported
in mobile environments (mobile_latest image). It uses the provided ADB public key to establish the
connection and returns the ADB connect URL.

#### GetAllUIElements

```go
func (m *Mobile) GetAllUIElements(timeoutMs int) *UIElementsResult
```

GetAllUIElements retrieves all UI elements within the specified timeout

#### GetClickableUIElements

```go
func (m *Mobile) GetClickableUIElements(timeoutMs int) *UIElementsResult
```

GetClickableUIElements retrieves all clickable UI elements within the specified timeout

#### GetInstalledApps

```go
func (m *Mobile) GetInstalledApps(startMenu, desktop, ignoreSystemApps bool) *InstalledAppListResult
```

GetInstalledApps retrieves a list of installed applications

#### InputText

```go
func (m *Mobile) InputText(text string) *BoolResult
```

InputText inputs text into the active field

#### Screenshot

```go
func (m *Mobile) Screenshot() *ScreenshotResult
```

Screenshot takes a screenshot of the current screen

#### SendKey

```go
func (m *Mobile) SendKey(key int) *BoolResult
```

SendKey sends a key press event

#### SetAppBlacklist

```go
func (m *Mobile) SetAppBlacklist(packageNames []string) error
```

SetAppBlacklist sets app blacklist for mobile devices

#### SetAppWhitelist

```go
func (m *Mobile) SetAppWhitelist(packageNames []string) error
```

SetAppWhitelist sets app whitelist for mobile devices

#### SetNavigationBarVisibility

```go
func (m *Mobile) SetNavigationBarVisibility(hide bool) error
```

SetNavigationBarVisibility sets navigation bar visibility for mobile devices

#### SetResolutionLock

```go
func (m *Mobile) SetResolutionLock(enable bool) error
```

SetResolutionLock sets display resolution lock for mobile devices

#### SetUninstallBlacklist

```go
func (m *Mobile) SetUninstallBlacklist(packageNames []string) error
```

SetUninstallBlacklist sets uninstall protection blacklist for mobile devices

#### StartApp

```go
func (m *Mobile) StartApp(startCmd, workDirectory, activity string) *ProcessListResult
```

StartApp starts a specified application

#### StopAppByCmd

```go
func (m *Mobile) StopAppByCmd(stopCmd string) *BoolResult
```

StopAppByCmd stops an application using the provided stop command

#### Swipe

```go
func (m *Mobile) Swipe(startX, startY, endX, endY, durationMs int) *BoolResult
```

Swipe performs a swipe gesture on the screen

#### Tap

```go
func (m *Mobile) Tap(x, y int) *BoolResult
```

Tap taps on the screen at specific coordinates

#### executeTemplateCommand

```go
func (m *Mobile) executeTemplateCommand(commandTemplate, description string) error
```

executeTemplateCommand executes a mobile command template

#### setAppBlacklist

```go
func (m *Mobile) setAppBlacklist(packageNames []string) error
```

setAppBlacklist sets app blacklist configuration

#### setAppWhitelist

```go
func (m *Mobile) setAppWhitelist(packageNames []string) error
```

setAppWhitelist sets app whitelist configuration

#### setNavigationBarVisibility

```go
func (m *Mobile) setNavigationBarVisibility(hide bool) error
```

setNavigationBarVisibility sets navigation bar visibility

#### setResolutionLock

```go
func (m *Mobile) setResolutionLock(enable bool) error
```

setResolutionLock internal method to set resolution lock

#### setUninstallBlacklist

```go
func (m *Mobile) setUninstallBlacklist(packageNames []string) error
```

setUninstallBlacklist sets uninstall protection blacklist

### Related Functions

#### NewMobile

```go
func NewMobile(session interface {
	GetAPIKey() string
	GetClient() *mcp.Client
	GetSessionId() string
	GetImageID() string
	IsVpc() bool
	NetworkInterfaceIp() string
	HttpPort() string
	FindServerForTool(toolName string) string
	CallMcpTool(toolName string, args interface{}, autoGenSession ...bool) (*models.McpToolResult, error)
}) *Mobile
```

NewMobile creates a new Mobile instance for UI automation

## Type Process

```go
type Process struct {
	PName	string	`json:"pname"`
	PID	int	`json:"pid"`
	CmdLine	string	`json:"cmdline,omitempty"`
}
```

Process represents a running process

## Type ProcessListResult

```go
type ProcessListResult struct {
	models.ApiResponse
	Processes	[]Process	`json:"processes"`
	ErrorMessage	string		`json:"error_message"`
}
```

ProcessListResult wraps process list and RequestID

## Type ScreenshotResult

```go
type ScreenshotResult struct {
	models.ApiResponse
	Data		string	`json:"data"`
	ErrorMessage	string	`json:"error_message"`
}
```

ScreenshotResult represents the result of a screenshot operation

## Type SessionWithCommand

```go
type SessionWithCommand interface {
	GetAPIKey() string
	GetClient() *mcp.Client
	GetSessionId() string
	IsVpc() bool
	NetworkInterfaceIp() string
	HttpPort() string
	FindServerForTool(toolName string) string
	CallMcpTool(toolName string, args interface{}, autoGenSession ...bool) (*models.McpToolResult, error)
	GetCommand() *command.Command
}
```

SessionWithCommand extends the basic session interface to include Command access

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

### Related Functions

#### parseBoundsString

```go
func parseBoundsString(s string) *UIBounds
```

parseBoundsString parses bounds string format "left,top,right,bottom"

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
	Children	[]*UIElement	`json:"children,omitempty"`
}
```

UIElement represents a UI element structure

### Methods

#### UnmarshalJSON

```go
func (e *UIElement) UnmarshalJSON(data []byte) error
```

UnmarshalJSON custom unmarshaler to handle string format bounds

## Type UIElementsResult

```go
type UIElementsResult struct {
	models.ApiResponse
	Elements	[]*UIElement	`json:"elements"`
	ErrorMessage	string		`json:"error_message"`
}
```

UIElementsResult represents the result containing UI elements

## Best Practices

1. Verify element coordinates before tap operations
2. Use appropriate swipe durations for smooth gestures
3. Wait for UI elements to load before interaction
4. Take screenshots for verification and debugging
5. Handle app installation and uninstallation properly
6. Configure app whitelists/blacklists for security

## Related Resources

- [Session API Reference](../../common-features/basics/session.md)

---

*Documentation generated automatically from Go source code.*
