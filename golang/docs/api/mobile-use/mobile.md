# Mobile API Reference

## 📱 Related Tutorial

- [Mobile Use Guide](../../../../docs/guides/mobile-use/README.md) - Automate mobile applications

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

## Type BetaScreenshotResult

```go
type BetaScreenshotResult struct {
	models.ApiResponse
	Success		bool	`json:"success"`
	Data		[]byte	`json:"data"`
	Format		string	`json:"format"`
	Width		*int	`json:"width,omitempty"`
	Height		*int	`json:"height,omitempty"`
	ErrorMessage	string	`json:"error_message"`
}
```

BetaScreenshotResult represents the result of a beta screenshot operation (binary image bytes).

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
		CallMcpTool(toolName string, args interface{}) (*models.McpToolResult, error)
	}
	command	*command.Command
}
```

Mobile handles mobile UI automation operations and configuration in the AgentBay cloud environment.
Provides touch operations, UI element interactions, application management, screenshot capabilities,
and mobile environment configuration.

> **⚠️ Note**: Currently, for agent services (including ComputerUseAgent, BrowserUseAgent, and
MobileUseAgent), we do not provide services for overseas users registered with **alibabacloud.com**.

### Methods

### BetaTakeLongScreenshot

```go
func (m *Mobile) BetaTakeLongScreenshot(maxScreens int, format string, quality ...int) *BetaScreenshotResult
```

BetaTakeLongScreenshot captures a long screenshot and returns raw image bytes.

Supported formats: - "png" - "jpeg" (or "jpg")

### BetaTakeScreenshot

```go
func (m *Mobile) BetaTakeScreenshot() *BetaScreenshotResult
```

BetaTakeScreenshot captures the current screen as a PNG image and returns raw image bytes.

It calls the MCP tool "screenshot" with format="png".

### Configure

```go
func (m *Mobile) Configure(mobileConfig *models.MobileExtraConfig) error
```

Configure configures mobile settings from MobileExtraConfig

### GetAdbUrl

```go
func (m *Mobile) GetAdbUrl(adbkeyPub string) *AdbUrlResult
```

GetAdbUrl retrieves the ADB connection URL for the mobile environment. This method is only supported
in mobile environments (mobile_latest image). It uses the provided ADB public key to establish the
connection and returns the ADB connect URL.

**Example:**

```go
client, _ := agentbay.NewAgentBay(os.Getenv("AGENTBAY_API_KEY"), nil)
result, _ := client.Create(agentbay.NewCreateSessionParams().WithImageId("mobile_latest"))
defer result.Session.Delete()
adbPubKey, _ := os.ReadFile(os.Getenv("HOME") + "/.android/adbkey.pub")
adbResult := result.Session.Mobile.GetAdbUrl(string(adbPubKey))
```

### GetAllUIElements

```go
func (m *Mobile) GetAllUIElements(timeoutMs int, formats ...string) *UIElementsResult
```

GetAllUIElements retrieves all UI elements within the specified timeout

**Example:**

```go
client, _ := agentbay.NewAgentBay(os.Getenv("AGENTBAY_API_KEY"), nil)
result, _ := client.Create(agentbay.NewCreateSessionParams().WithImageId("mobile_latest"))
defer result.Session.Delete()
elementsResult := result.Session.Mobile.GetAllUIElements(5000)
```

### GetClickableUIElements

```go
func (m *Mobile) GetClickableUIElements(timeoutMs int) *UIElementsResult
```

GetClickableUIElements retrieves all clickable UI elements within the specified timeout

**Example:**

```go
client, _ := agentbay.NewAgentBay(os.Getenv("AGENTBAY_API_KEY"), nil)
result, _ := client.Create(agentbay.NewCreateSessionParams().WithImageId("mobile_latest"))
defer result.Session.Delete()
elementsResult := result.Session.Mobile.GetClickableUIElements(5000)
```

### GetInstalledApps

```go
func (m *Mobile) GetInstalledApps(startMenu, desktop, ignoreSystemApps bool) *InstalledAppListResult
```

GetInstalledApps retrieves a list of installed applications

**Example:**

```go
client, _ := agentbay.NewAgentBay(os.Getenv("AGENTBAY_API_KEY"), nil)
result, _ := client.Create(agentbay.NewCreateSessionParams().WithImageId("mobile_latest"))
defer result.Session.Delete()
appsResult := result.Session.Mobile.GetInstalledApps(true, true, true)
```

### InputText

```go
func (m *Mobile) InputText(text string) *BoolResult
```

InputText inputs text into the active field

**Example:**

```go
client, _ := agentbay.NewAgentBay(os.Getenv("AGENTBAY_API_KEY"), nil)
result, _ := client.Create(agentbay.NewCreateSessionParams().WithImageId("mobile_latest"))
defer result.Session.Delete()
inputResult := result.Session.Mobile.InputText("Hello Mobile")
```

### Screenshot

```go
func (m *Mobile) Screenshot() *ScreenshotResult
```

Screenshot takes a screenshot of the current screen

**Example:**

```go
client, _ := agentbay.NewAgentBay(os.Getenv("AGENTBAY_API_KEY"), nil)
result, _ := client.Create(agentbay.NewCreateSessionParams().WithImageId("mobile_latest"))
defer result.Session.Delete()
screenshot := result.Session.Mobile.Screenshot()
```

### SendKey

```go
func (m *Mobile) SendKey(key int) *BoolResult
```

SendKey sends a key press event

**Example:**

```go
client, _ := agentbay.NewAgentBay(os.Getenv("AGENTBAY_API_KEY"), nil)
result, _ := client.Create(agentbay.NewCreateSessionParams().WithImageId("mobile_latest"))
defer result.Session.Delete()
keyResult := result.Session.Mobile.SendKey(4)
```

### SetAppBlacklist

```go
func (m *Mobile) SetAppBlacklist(packageNames []string) error
```

SetAppBlacklist sets app blacklist for mobile devices

**Example:**

```go
client, _ := agentbay.NewAgentBay(os.Getenv("AGENTBAY_API_KEY"), nil)
result, _ := client.Create(agentbay.NewCreateSessionParams().WithImageId("mobile_latest"))
defer result.Session.Delete()
blockedApps := []string{"com.example.blockedapp"}
err := result.Session.Mobile.SetAppBlacklist(blockedApps)
```

### SetAppWhitelist

```go
func (m *Mobile) SetAppWhitelist(packageNames []string) error
```

SetAppWhitelist sets app whitelist for mobile devices

**Example:**

```go
client, _ := agentbay.NewAgentBay(os.Getenv("AGENTBAY_API_KEY"), nil)
result, _ := client.Create(agentbay.NewCreateSessionParams().WithImageId("mobile_latest"))
defer result.Session.Delete()
allowedApps := []string{"com.android.calculator2"}
err := result.Session.Mobile.SetAppWhitelist(allowedApps)
```

### SetNavigationBarVisibility

```go
func (m *Mobile) SetNavigationBarVisibility(hide bool) error
```

SetNavigationBarVisibility sets navigation bar visibility for mobile devices

**Example:**

```go
client, _ := agentbay.NewAgentBay(os.Getenv("AGENTBAY_API_KEY"), nil)
result, _ := client.Create(agentbay.NewCreateSessionParams().WithImageId("mobile_latest"))
defer result.Session.Delete()
err := result.Session.Mobile.SetNavigationBarVisibility(true)
```

### SetResolutionLock

```go
func (m *Mobile) SetResolutionLock(enable bool) error
```

SetResolutionLock sets display resolution lock for mobile devices

**Example:**

```go
client, _ := agentbay.NewAgentBay(os.Getenv("AGENTBAY_API_KEY"), nil)
result, _ := client.Create(agentbay.NewCreateSessionParams().WithImageId("mobile_latest"))
defer result.Session.Delete()
err := result.Session.Mobile.SetResolutionLock(true)
```

### SetUninstallBlacklist

```go
func (m *Mobile) SetUninstallBlacklist(packageNames []string) error
```

SetUninstallBlacklist sets uninstall protection blacklist for mobile devices

**Example:**

```go
client, _ := agentbay.NewAgentBay(os.Getenv("AGENTBAY_API_KEY"), nil)
result, _ := client.Create(agentbay.NewCreateSessionParams().WithImageId("mobile_latest"))
defer result.Session.Delete()
protectedApps := []string{"com.android.calculator2"}
err := result.Session.Mobile.SetUninstallBlacklist(protectedApps)
```

### StartApp

```go
func (m *Mobile) StartApp(startCmd, workDirectory, activity string) *ProcessListResult
```

StartApp starts a specified application

**Example:**

```go
client, _ := agentbay.NewAgentBay(os.Getenv("AGENTBAY_API_KEY"), nil)
result, _ := client.Create(agentbay.NewCreateSessionParams().WithImageId("mobile_latest"))
defer result.Session.Delete()
processResult := result.Session.Mobile.StartApp("com.android.calculator2", "", "com.android.calculator2.Calculator")
```

### StopAppByCmd

```go
func (m *Mobile) StopAppByCmd(stopCmd string) *BoolResult
```

StopAppByCmd stops an application using the provided stop command

**Example:**

```go
client, _ := agentbay.NewAgentBay(os.Getenv("AGENTBAY_API_KEY"), nil)
result, _ := client.Create(agentbay.NewCreateSessionParams().WithImageId("mobile_latest"))
defer result.Session.Delete()
stopResult := result.Session.Mobile.StopAppByCmd("com.android.calculator2")
```

### Swipe

```go
func (m *Mobile) Swipe(startX, startY, endX, endY, durationMs int) *BoolResult
```

Swipe performs a swipe gesture on the screen

**Example:**

```go
client, _ := agentbay.NewAgentBay(os.Getenv("AGENTBAY_API_KEY"), nil)
result, _ := client.Create(agentbay.NewCreateSessionParams().WithImageId("mobile_latest"))
defer result.Session.Delete()
swipeResult := result.Session.Mobile.Swipe(100, 500, 900, 500, 300)
```

### Tap

```go
func (m *Mobile) Tap(x, y int) *BoolResult
```

Tap taps on the screen at specific coordinates

**Example:**

```go
client, _ := agentbay.NewAgentBay(os.Getenv("AGENTBAY_API_KEY"), nil)
result, _ := client.Create(agentbay.NewCreateSessionParams().WithImageId("mobile_latest"))
defer result.Session.Delete()
tapResult := result.Session.Mobile.Tap(500, 500)
```

### Related Functions

### NewMobile

```go
func NewMobile(session interface {
	GetAPIKey() string
	GetClient() *mcp.Client
	GetSessionId() string
	GetImageID() string
	CallMcpTool(toolName string, args interface{}) (*models.McpToolResult, error)
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
	CallMcpTool(toolName string, args interface{}) (*models.McpToolResult, error)
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

## Type UIElementsResult

```go
type UIElementsResult struct {
	models.ApiResponse
	Elements	[]*UIElement	`json:"elements"`
	Raw		string		`json:"raw"`
	Format		string		`json:"format"`
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

- [Session API Reference](../common-features/basics/session.md)

---

*Documentation generated automatically from Go source code.*
