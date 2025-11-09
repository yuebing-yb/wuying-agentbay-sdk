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
	params := agentbay.NewCreateSessionParams().WithImageId("mobile_latest")
	result, err := client.Create(params)
	if err != nil {
		fmt.Printf("Error: %v\n", err)
		os.Exit(1)
	}
	session := result.Session

	// Read ADB public key from file (typically ~/.android/adbkey.pub)

	adbPubKey, err := os.ReadFile(os.Getenv("HOME") + "/.android/adbkey.pub")
	if err != nil {
		fmt.Printf("Error reading ADB key: %v\n", err)
		os.Exit(1)
	}

	// Get ADB URL

	adbResult := session.Mobile.GetAdbUrl(string(adbPubKey))
	if adbResult.Success {
		fmt.Printf("ADB URL: %s\n", adbResult.URL)

		// Output: ADB URL: adb connect xx.xx.xx.xx:xxxxx

	} else {
		fmt.Printf("Error: %s\n", adbResult.ErrorMessage)
	}
	session.Delete()
}
```

#### GetAllUIElements

```go
func (m *Mobile) GetAllUIElements(timeoutMs int) *UIElementsResult
```

GetAllUIElements retrieves all UI elements within the specified timeout

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
	params := &agentbay.CreateSessionParams{
		ImageId: "mobile_latest",
	}
	result, err := client.Create(params)
	if err != nil {
		fmt.Printf("Error: %v\n", err)
		os.Exit(1)
	}
	session := result.Session
	elementsResult := session.Mobile.GetAllUIElements(5000)
	if elementsResult.ErrorMessage == "" {
		fmt.Printf("Found %d total elements\n", len(elementsResult.Elements))
		for _, elem := range elementsResult.Elements {
			if elem.Bounds != nil {
				fmt.Printf("  - Element: %s at (%d, %d, %d, %d)\n",
					elem.ClassName,
					elem.Bounds.Left, elem.Bounds.Top,
					elem.Bounds.Right, elem.Bounds.Bottom)
			}
		}
	}
	session.Delete()
}
```

#### GetClickableUIElements

```go
func (m *Mobile) GetClickableUIElements(timeoutMs int) *UIElementsResult
```

GetClickableUIElements retrieves all clickable UI elements within the specified timeout

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
	params := &agentbay.CreateSessionParams{
		ImageId: "mobile_latest",
	}
	result, err := client.Create(params)
	if err != nil {
		fmt.Printf("Error: %v\n", err)
		os.Exit(1)
	}
	session := result.Session
	elementsResult := session.Mobile.GetClickableUIElements(5000)
	if elementsResult.ErrorMessage == "" {
		fmt.Printf("Found %d clickable elements\n", len(elementsResult.Elements))
		for _, elem := range elementsResult.Elements {
			fmt.Printf("  - Text: %s, ResourceID: %s\n", elem.Text, elem.ResourceID)
		}
	}
	session.Delete()
}
```

#### GetInstalledApps

```go
func (m *Mobile) GetInstalledApps(startMenu, desktop, ignoreSystemApps bool) *InstalledAppListResult
```

GetInstalledApps retrieves a list of installed applications

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
	params := &agentbay.CreateSessionParams{
		ImageId: "mobile_latest",
	}
	result, err := client.Create(params)
	if err != nil {
		fmt.Printf("Error: %v\n", err)
		os.Exit(1)
	}
	session := result.Session

	// Get all user-installed apps (excluding system apps)

	appsResult := session.Mobile.GetInstalledApps(true, true, true)
	if appsResult.ErrorMessage == "" {
		fmt.Printf("Found %d installed apps\n", len(appsResult.Apps))
		for _, app := range appsResult.Apps {
			fmt.Printf("  - %s: %s\n", app.Name, app.StartCmd)
		}
	}
	session.Delete()
}
```

#### InputText

```go
func (m *Mobile) InputText(text string) *BoolResult
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
	params := &agentbay.CreateSessionParams{
		ImageId: "mobile_latest",
	}
	result, err := client.Create(params)
	if err != nil {
		fmt.Printf("Error: %v\n", err)
		os.Exit(1)
	}
	session := result.Session
	inputResult := session.Mobile.InputText("Hello Mobile")
	if inputResult.Success {
		fmt.Println("Text input successful")
	}
	session.Delete()
}
```

#### Screenshot

```go
func (m *Mobile) Screenshot() *ScreenshotResult
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
	params := &agentbay.CreateSessionParams{
		ImageId: "mobile_latest",
	}
	result, err := client.Create(params)
	if err != nil {
		fmt.Printf("Error: %v\n", err)
		os.Exit(1)
	}
	session := result.Session
	screenshot := session.Mobile.Screenshot()
	if screenshot.ErrorMessage == "" {
		fmt.Printf("Screenshot URL: %s\n", screenshot.Data)
	}
	session.Delete()
}
```

#### SendKey

```go
func (m *Mobile) SendKey(key int) *BoolResult
```

SendKey sends a key press event

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
	params := &agentbay.CreateSessionParams{
		ImageId: "mobile_latest",
	}
	result, err := client.Create(params)
	if err != nil {
		fmt.Printf("Error: %v\n", err)
		os.Exit(1)
	}
	session := result.Session

	// Send BACK key (keycode 4)

	keyResult := session.Mobile.SendKey(4)
	if keyResult.Success {
		fmt.Println("Key press successful")
	}
	session.Delete()
}
```

#### SetAppBlacklist

```go
func (m *Mobile) SetAppBlacklist(packageNames []string) error
```

SetAppBlacklist sets app blacklist for mobile devices

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
	params := agentbay.NewCreateSessionParams().WithImageId("mobile_latest")
	result, err := client.Create(params)
	if err != nil {
		fmt.Printf("Error: %v\n", err)
		os.Exit(1)
	}
	session := result.Session

	// Block specific apps from running

	blockedApps := []string{
		"com.facebook.katana",
		"com.instagram.android",
		"com.snapchat.android",
	}
	err = session.Mobile.SetAppBlacklist(blockedApps)
	if err != nil {
		fmt.Printf("Error setting app blacklist: %v\n", err)
		os.Exit(1)
	}
	fmt.Printf("Blocked %d apps from running\n", len(blockedApps))
	session.Delete()
}
```

#### SetAppWhitelist

```go
func (m *Mobile) SetAppWhitelist(packageNames []string) error
```

SetAppWhitelist sets app whitelist for mobile devices

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
	params := agentbay.NewCreateSessionParams().WithImageId("mobile_latest")
	result, err := client.Create(params)
	if err != nil {
		fmt.Printf("Error: %v\n", err)
		os.Exit(1)
	}
	session := result.Session

	// Only allow specific apps to run (kiosk mode)

	allowedApps := []string{
		"com.example.kiosk",
		"com.android.settings",
	}
	err = session.Mobile.SetAppWhitelist(allowedApps)
	if err != nil {
		fmt.Printf("Error setting app whitelist: %v\n", err)
		os.Exit(1)
	}
	fmt.Printf("Restricted device to %d allowed apps\n", len(allowedApps))
	session.Delete()
}
```

#### SetNavigationBarVisibility

```go
func (m *Mobile) SetNavigationBarVisibility(hide bool) error
```

SetNavigationBarVisibility sets navigation bar visibility for mobile devices

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
	params := agentbay.NewCreateSessionParams().WithImageId("mobile_latest")
	result, err := client.Create(params)
	if err != nil {
		fmt.Printf("Error: %v\n", err)
		os.Exit(1)
	}
	session := result.Session

	// Hide navigation bar for full-screen experience

	err = session.Mobile.SetNavigationBarVisibility(true)
	if err != nil {
		fmt.Printf("Error hiding navigation bar: %v\n", err)
		os.Exit(1)
	}
	fmt.Println("Navigation bar hidden successfully")

	// Show navigation bar again

	err = session.Mobile.SetNavigationBarVisibility(false)
	if err != nil {
		fmt.Printf("Error showing navigation bar: %v\n", err)
		os.Exit(1)
	}
	fmt.Println("Navigation bar shown successfully")
	session.Delete()
}
```

#### SetResolutionLock

```go
func (m *Mobile) SetResolutionLock(enable bool) error
```

SetResolutionLock sets display resolution lock for mobile devices

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
	params := agentbay.NewCreateSessionParams().WithImageId("mobile_latest")
	result, err := client.Create(params)
	if err != nil {
		fmt.Printf("Error: %v\n", err)
		os.Exit(1)
	}
	session := result.Session

	// Enable resolution lock to prevent automatic resolution changes

	err = session.Mobile.SetResolutionLock(true)
	if err != nil {
		fmt.Printf("Error setting resolution lock: %v\n", err)
		os.Exit(1)
	}
	fmt.Println("Resolution lock enabled successfully")

	// Disable resolution lock to allow automatic resolution changes

	err = session.Mobile.SetResolutionLock(false)
	if err != nil {
		fmt.Printf("Error disabling resolution lock: %v\n", err)
		os.Exit(1)
	}
	fmt.Println("Resolution lock disabled successfully")
	session.Delete()
}
```

#### SetUninstallBlacklist

```go
func (m *Mobile) SetUninstallBlacklist(packageNames []string) error
```

SetUninstallBlacklist sets uninstall protection blacklist for mobile devices

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
	params := agentbay.NewCreateSessionParams().WithImageId("mobile_latest")
	result, err := client.Create(params)
	if err != nil {
		fmt.Printf("Error: %v\n", err)
		os.Exit(1)
	}
	session := result.Session

	// Protect critical apps from being uninstalled

	protectedApps := []string{
		"com.android.chrome",
		"com.google.android.gms",
		"com.android.vending",
	}
	err = session.Mobile.SetUninstallBlacklist(protectedApps)
	if err != nil {
		fmt.Printf("Error setting uninstall blacklist: %v\n", err)
		os.Exit(1)
	}
	fmt.Printf("Protected %d apps from uninstallation\n", len(protectedApps))
	session.Delete()
}
```

#### StartApp

```go
func (m *Mobile) StartApp(startCmd, workDirectory, activity string) *ProcessListResult
```

StartApp starts a specified application

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
	params := &agentbay.CreateSessionParams{
		ImageId: "mobile_latest",
	}
	result, err := client.Create(params)
	if err != nil {
		fmt.Printf("Error: %v\n", err)
		os.Exit(1)
	}
	session := result.Session

	// Start an Android app (example: Calculator)

	processResult := session.Mobile.StartApp("com.android.calculator2", "", "com.android.calculator2.Calculator")
	if processResult.ErrorMessage == "" {
		fmt.Printf("App started, %d processes found\n", len(processResult.Processes))
		for _, proc := range processResult.Processes {
			fmt.Printf("  - Process: %s (PID: %d)\n", proc.PName, proc.PID)
		}
	}
	session.Delete()
}
```

#### StopAppByCmd

```go
func (m *Mobile) StopAppByCmd(stopCmd string) *BoolResult
```

StopAppByCmd stops an application using the provided stop command

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
	params := &agentbay.CreateSessionParams{
		ImageId: "mobile_latest",
	}
	result, err := client.Create(params)
	if err != nil {
		fmt.Printf("Error: %v\n", err)
		os.Exit(1)
	}
	session := result.Session

	// Stop an Android app by package name

	stopResult := session.Mobile.StopAppByCmd("com.android.calculator2")
	if stopResult.Success {
		fmt.Println("App stopped successfully")
	}
	session.Delete()
}
```

#### Swipe

```go
func (m *Mobile) Swipe(startX, startY, endX, endY, durationMs int) *BoolResult
```

Swipe performs a swipe gesture on the screen

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
	params := &agentbay.CreateSessionParams{
		ImageId: "mobile_latest",
	}
	result, err := client.Create(params)
	if err != nil {
		fmt.Printf("Error: %v\n", err)
		os.Exit(1)
	}
	session := result.Session
	swipeResult := session.Mobile.Swipe(100, 500, 900, 500, 300)
	if swipeResult.Success {
		fmt.Println("Swipe successful")
	}
	session.Delete()
}
```

#### Tap

```go
func (m *Mobile) Tap(x, y int) *BoolResult
```

Tap taps on the screen at specific coordinates

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
	params := &agentbay.CreateSessionParams{
		ImageId: "mobile_latest",
	}
	result, err := client.Create(params)
	if err != nil {
		fmt.Printf("Error: %v\n", err)
		os.Exit(1)
	}
	session := result.Session
	tapResult := session.Mobile.Tap(500, 500)
	if tapResult.Success {
		fmt.Println("Tap successful")
	}
	session.Delete()
}
```

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
