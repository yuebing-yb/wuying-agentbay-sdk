package mobile

import (
	"bytes"
	"encoding/base64"
	"encoding/json"
	"fmt"
	"strings"
	"time"

	"github.com/alibabacloud-go/tea/tea"
	mcp "github.com/aliyun/wuying-agentbay-sdk/golang/api/client"
	"github.com/aliyun/wuying-agentbay-sdk/golang/pkg/agentbay/command"
	"github.com/aliyun/wuying-agentbay-sdk/golang/pkg/agentbay/models"
)

// UIElement represents a UI element structure
type UIElement struct {
	Bounds      *UIBounds    `json:"bounds,omitempty"`
	ClassName   string       `json:"className,omitempty"`
	ContentDesc string       `json:"contentDesc,omitempty"`
	ElementID   string       `json:"elementId,omitempty"`
	Package     string       `json:"package,omitempty"`
	ResourceID  string       `json:"resourceId,omitempty"`
	Text        string       `json:"text,omitempty"`
	Type        string       `json:"type,omitempty"`
	Children    []*UIElement `json:"children,omitempty"`
}

// UnmarshalJSON custom unmarshaler to handle string format bounds
func (e *UIElement) UnmarshalJSON(data []byte) error {
	// Define an auxiliary type to avoid recursion
	type Alias UIElement
	aux := &struct {
		BoundsRaw interface{} `json:"bounds"`
		*Alias
	}{
		Alias: (*Alias)(e),
	}

	if err := json.Unmarshal(data, &aux); err != nil {
		return err
	}

	// Handle bounds field which can be either string or object
	if aux.BoundsRaw != nil {
		switch v := aux.BoundsRaw.(type) {
		case string:
			// Parse string format: "left,top,right,bottom"
			e.Bounds = parseBoundsString(v)
		case map[string]interface{}:
			// Parse object format
			if boundsJSON, err := json.Marshal(v); err == nil {
				var bounds UIBounds
				if err := json.Unmarshal(boundsJSON, &bounds); err == nil {
					e.Bounds = &bounds
				}
			}
		}
	}

	return nil
}

// parseBoundsString parses bounds string format "left,top,right,bottom"
func parseBoundsString(s string) *UIBounds {
	parts := strings.Split(s, ",")
	if len(parts) != 4 {
		return nil
	}

	var left, top, right, bottom int
	if _, err := fmt.Sscanf(s, "%d,%d,%d,%d", &left, &top, &right, &bottom); err != nil {
		return nil
	}

	return &UIBounds{
		Left:   left,
		Top:    top,
		Right:  right,
		Bottom: bottom,
	}
}

// UIBounds represents the bounds of a UI element
type UIBounds struct {
	Bottom int `json:"bottom"`
	Left   int `json:"left"`
	Right  int `json:"right"`
	Top    int `json:"top"`
}

// UIElementsResult represents the result containing UI elements
type UIElementsResult struct {
	models.ApiResponse
	Elements     []*UIElement `json:"elements"`
	Raw          string       `json:"raw"`
	Format       string       `json:"format"`
	ErrorMessage string       `json:"error_message"`
}

// AdbUrlResult represents the result of ADB URL retrieval operation
type AdbUrlResult struct {
	models.ApiResponse
	URL          string `json:"url"`
	Success      bool   `json:"success"`
	ErrorMessage string `json:"error_message"`
}

// InstalledApp represents an installed application
type InstalledApp struct {
	Name          string `json:"name"`
	StartCmd      string `json:"start_cmd"`
	StopCmd       string `json:"stop_cmd,omitempty"`
	WorkDirectory string `json:"work_directory,omitempty"`
}

// Process represents a running process
type Process struct {
	PName   string `json:"pname"`
	PID     int    `json:"pid"`
	CmdLine string `json:"cmdline,omitempty"`
}

// InstalledAppListResult wraps installed app list and RequestID
type InstalledAppListResult struct {
	models.ApiResponse
	Apps         []InstalledApp `json:"apps"`
	ErrorMessage string         `json:"error_message"`
}

// ProcessListResult wraps process list and RequestID
type ProcessListResult struct {
	models.ApiResponse
	Processes    []Process `json:"processes"`
	ErrorMessage string    `json:"error_message"`
}

// BoolResult represents a boolean operation result
type BoolResult struct {
	models.ApiResponse
	Success      bool   `json:"success"`
	ErrorMessage string `json:"error_message"`
}

// ScreenshotResult represents the result of a screenshot operation
type ScreenshotResult struct {
	models.ApiResponse
	Data         string `json:"data"`
	ErrorMessage string `json:"error_message"`
}

// BetaScreenshotResult represents the result of a beta screenshot operation (binary image bytes).
type BetaScreenshotResult struct {
	models.ApiResponse
	Success      bool   `json:"success"`
	Data         []byte `json:"data"`
	Format       string `json:"format"`
	Width        *int   `json:"width,omitempty"`
	Height       *int   `json:"height,omitempty"`
	ErrorMessage string `json:"error_message"`
}

// Mobile handles mobile UI automation operations and configuration in the AgentBay cloud environment.
// Provides touch operations, UI element interactions, application management, screenshot capabilities,
// and mobile environment configuration.
//
// > **⚠️ Note**: Currently, for agent services (including ComputerUseAgent, BrowserUseAgent, and MobileUseAgent), we do not provide services for overseas users registered with **alibabacloud.com**.
type Mobile struct {
	Session interface {
		GetAPIKey() string
		GetClient() *mcp.Client
		GetSessionId() string
		GetImageID() string
		CallMcpTool(toolName string, args interface{}) (*models.McpToolResult, error)
	}
	command *command.Command
}

// SessionWithCommand extends the basic session interface to include Command access
type SessionWithCommand interface {
	GetAPIKey() string
	GetClient() *mcp.Client
	GetSessionId() string
	CallMcpTool(toolName string, args interface{}) (*models.McpToolResult, error)
	GetCommand() *command.Command
}

// NewMobile creates a new Mobile instance for UI automation
func NewMobile(session interface {
	GetAPIKey() string
	GetClient() *mcp.Client
	GetSessionId() string
	GetImageID() string
	CallMcpTool(toolName string, args interface{}) (*models.McpToolResult, error)
}) *Mobile {
	mobile := &Mobile{
		Session: session,
	}

	// Try to get command from session if it implements SessionWithCommand interface
	if sessionWithCmd, ok := session.(SessionWithCommand); ok {
		mobile.command = sessionWithCmd.GetCommand()
	}

	return mobile
}

// Tap taps on the screen at specific coordinates
//
// Example:
//
//	client, _ := agentbay.NewAgentBay(os.Getenv("AGENTBAY_API_KEY"), nil)
//	result, _ := client.Create(agentbay.NewCreateSessionParams().WithImageId("mobile_latest"))
//	defer result.Session.Delete()
//	tapResult := result.Session.Mobile.Tap(500, 500)
func (m *Mobile) Tap(x, y int) *BoolResult {
	args := map[string]interface{}{
		"x": x,
		"y": y,
	}

	result, err := m.Session.CallMcpTool("tap", args)
	if err != nil {
		return &BoolResult{
			ApiResponse: models.ApiResponse{
				RequestID: "",
			},
			Success:      false,
			ErrorMessage: fmt.Sprintf("failed to call tap: %v", err),
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

// Swipe performs a swipe gesture on the screen
//
// Example:
//
//	client, _ := agentbay.NewAgentBay(os.Getenv("AGENTBAY_API_KEY"), nil)
//	result, _ := client.Create(agentbay.NewCreateSessionParams().WithImageId("mobile_latest"))
//	defer result.Session.Delete()
//	swipeResult := result.Session.Mobile.Swipe(100, 500, 900, 500, 300)
func (m *Mobile) Swipe(startX, startY, endX, endY, durationMs int) *BoolResult {
	args := map[string]interface{}{
		"start_x":     startX,
		"start_y":     startY,
		"end_x":       endX,
		"end_y":       endY,
		"duration_ms": durationMs,
	}

	result, err := m.Session.CallMcpTool("swipe", args)
	if err != nil {
		return &BoolResult{
			ApiResponse: models.ApiResponse{
				RequestID: "",
			},
			Success:      false,
			ErrorMessage: fmt.Sprintf("failed to call swipe: %v", err),
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

// InputText inputs text into the active field
//
// Example:
//
//	client, _ := agentbay.NewAgentBay(os.Getenv("AGENTBAY_API_KEY"), nil)
//	result, _ := client.Create(agentbay.NewCreateSessionParams().WithImageId("mobile_latest"))
//	defer result.Session.Delete()
//	inputResult := result.Session.Mobile.InputText("Hello Mobile")
func (m *Mobile) InputText(text string) *BoolResult {
	args := map[string]interface{}{
		"text": text,
	}

	result, err := m.Session.CallMcpTool("input_text", args)
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

// SendKey sends a key press event
//
// Example:
//
//	client, _ := agentbay.NewAgentBay(os.Getenv("AGENTBAY_API_KEY"), nil)
//	result, _ := client.Create(agentbay.NewCreateSessionParams().WithImageId("mobile_latest"))
//	defer result.Session.Delete()
//	keyResult := result.Session.Mobile.SendKey(4)
func (m *Mobile) SendKey(key int) *BoolResult {
	args := map[string]interface{}{
		"key": key,
	}

	result, err := m.Session.CallMcpTool("send_key", args)
	if err != nil {
		return &BoolResult{
			ApiResponse: models.ApiResponse{
				RequestID: "",
			},
			Success:      false,
			ErrorMessage: fmt.Sprintf("failed to call send_key: %v", err),
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

// GetClickableUIElements retrieves all clickable UI elements within the specified timeout
//
// Example:
//
//	client, _ := agentbay.NewAgentBay(os.Getenv("AGENTBAY_API_KEY"), nil)
//	result, _ := client.Create(agentbay.NewCreateSessionParams().WithImageId("mobile_latest"))
//	defer result.Session.Delete()
//	elementsResult := result.Session.Mobile.GetClickableUIElements(5000)
func (m *Mobile) GetClickableUIElements(timeoutMs int) *UIElementsResult {
	args := map[string]interface{}{
		"timeout_ms": timeoutMs,
	}

	result, err := m.Session.CallMcpTool("get_clickable_ui_elements", args)
	if err != nil {
		return &UIElementsResult{
			ApiResponse: models.ApiResponse{
				RequestID: "",
			},
			ErrorMessage: fmt.Sprintf("failed to call get_clickable_ui_elements: %v", err),
		}
	}

	if !result.Success {
		return &UIElementsResult{
			ApiResponse: models.ApiResponse{
				RequestID: result.RequestID,
			},
			ErrorMessage: result.ErrorMessage,
		}
	}

	// Parse UI elements from JSON
	var elements []*UIElement
	if err := json.Unmarshal([]byte(result.Data), &elements); err != nil {
		return &UIElementsResult{
			ApiResponse: models.ApiResponse{
				RequestID: result.RequestID,
			},
			ErrorMessage: fmt.Sprintf("failed to parse UI elements: %v", err),
		}
	}

	return &UIElementsResult{
		ApiResponse: models.ApiResponse{
			RequestID: result.RequestID,
		},
		Elements:     elements,
		ErrorMessage: result.ErrorMessage,
	}
}

// GetAllUIElements retrieves all UI elements within the specified timeout
//
// Example:
//
//	client, _ := agentbay.NewAgentBay(os.Getenv("AGENTBAY_API_KEY"), nil)
//	result, _ := client.Create(agentbay.NewCreateSessionParams().WithImageId("mobile_latest"))
//	defer result.Session.Delete()
//	elementsResult := result.Session.Mobile.GetAllUIElements(5000)
func (m *Mobile) GetAllUIElements(timeoutMs int, formats ...string) *UIElementsResult {
	formatNorm := "json"
	formatArg := ""
	if len(formats) > 0 {
		formatArg = formats[0]
		formatNorm = strings.TrimSpace(strings.ToLower(formatArg))
	}
	if formatNorm == "" {
		formatNorm = "json"
	}

	args := map[string]interface{}{
		"timeout_ms": timeoutMs,
		"format":     formatNorm,
	}

	result, err := m.Session.CallMcpTool("get_all_ui_elements", args)
	if err != nil {
		return &UIElementsResult{
			ApiResponse: models.ApiResponse{
				RequestID: "",
			},
			Raw:          "",
			Format:       formatNorm,
			ErrorMessage: fmt.Sprintf("failed to call get_all_ui_elements: %v", err),
		}
	}

	if !result.Success {
		return &UIElementsResult{
			ApiResponse: models.ApiResponse{
				RequestID: result.RequestID,
			},
			Raw:          result.Data,
			Format:       formatNorm,
			ErrorMessage: result.ErrorMessage,
		}
	}

	if formatNorm == "xml" {
		return &UIElementsResult{
			ApiResponse: models.ApiResponse{
				RequestID: result.RequestID,
			},
			Elements:     []*UIElement{},
			Raw:          result.Data,
			Format:       "xml",
			ErrorMessage: "",
		}
	}

	if formatNorm != "json" {
		return &UIElementsResult{
			ApiResponse: models.ApiResponse{
				RequestID: result.RequestID,
			},
			Elements:     []*UIElement{},
			Raw:          result.Data,
			Format:       formatNorm,
			ErrorMessage: fmt.Sprintf("unsupported UI elements format: %q. Supported values: \"json\", \"xml\".", formatArg),
		}
	}

	// Parse UI elements from JSON
	var elements []*UIElement
	if err := json.Unmarshal([]byte(result.Data), &elements); err != nil {
		return &UIElementsResult{
			ApiResponse: models.ApiResponse{
				RequestID: result.RequestID,
			},
			Raw:          result.Data,
			Format:       "json",
			ErrorMessage: fmt.Sprintf("failed to parse UI elements: %v", err),
		}
	}

	return &UIElementsResult{
		ApiResponse: models.ApiResponse{
			RequestID: result.RequestID,
		},
		Elements:     elements,
		Raw:          result.Data,
		Format:       "json",
		ErrorMessage: result.ErrorMessage,
	}
}

// GetInstalledApps retrieves a list of installed applications
//
// Example:
//
//	client, _ := agentbay.NewAgentBay(os.Getenv("AGENTBAY_API_KEY"), nil)
//	result, _ := client.Create(agentbay.NewCreateSessionParams().WithImageId("mobile_latest"))
//	defer result.Session.Delete()
//	appsResult := result.Session.Mobile.GetInstalledApps(true, true, true)
func (m *Mobile) GetInstalledApps(startMenu, desktop, ignoreSystemApps bool) *InstalledAppListResult {
	args := map[string]interface{}{
		"start_menu":         startMenu,
		"desktop":            desktop,
		"ignore_system_apps": ignoreSystemApps,
	}

	result, err := m.Session.CallMcpTool("get_installed_apps", args)
	if err != nil {
		return &InstalledAppListResult{
			ApiResponse: models.ApiResponse{
				RequestID: "",
			},
			ErrorMessage: fmt.Sprintf("failed to call get_installed_apps: %v", err),
		}
	}

	if !result.Success {
		return &InstalledAppListResult{
			ApiResponse: models.ApiResponse{
				RequestID: result.RequestID,
			},
			ErrorMessage: result.ErrorMessage,
		}
	}

	// Parse installed apps from JSON
	var apps []InstalledApp
	if err := json.Unmarshal([]byte(result.Data), &apps); err != nil {
		return &InstalledAppListResult{
			ApiResponse: models.ApiResponse{
				RequestID: result.RequestID,
			},
			ErrorMessage: fmt.Sprintf("failed to parse installed apps: %v", err),
		}
	}

	return &InstalledAppListResult{
		ApiResponse: models.ApiResponse{
			RequestID: result.RequestID,
		},
		Apps:         apps,
		ErrorMessage: result.ErrorMessage,
	}
}

// StartApp starts a specified application
//
// Example:
//
//	client, _ := agentbay.NewAgentBay(os.Getenv("AGENTBAY_API_KEY"), nil)
//	result, _ := client.Create(agentbay.NewCreateSessionParams().WithImageId("mobile_latest"))
//	defer result.Session.Delete()
//	processResult := result.Session.Mobile.StartApp("com.android.calculator2", "", "com.android.calculator2.Calculator")
func (m *Mobile) StartApp(startCmd, workDirectory, activity string) *ProcessListResult {
	args := map[string]interface{}{
		"start_cmd":      startCmd,
		"work_directory": workDirectory,
		"activity":       activity,
	}

	result, err := m.Session.CallMcpTool("start_app", args)
	if err != nil {
		return &ProcessListResult{
			ApiResponse: models.ApiResponse{
				RequestID: "",
			},
			ErrorMessage: fmt.Sprintf("failed to call start_app: %v", err),
		}
	}

	if !result.Success {
		return &ProcessListResult{
			ApiResponse: models.ApiResponse{
				RequestID: result.RequestID,
			},
			ErrorMessage: result.ErrorMessage,
		}
	}

	// Parse processes from JSON
	var processes []Process
	if err := json.Unmarshal([]byte(result.Data), &processes); err != nil {
		return &ProcessListResult{
			ApiResponse: models.ApiResponse{
				RequestID: result.RequestID,
			},
			ErrorMessage: fmt.Sprintf("failed to parse processes: %v", err),
		}
	}

	return &ProcessListResult{
		ApiResponse: models.ApiResponse{
			RequestID: result.RequestID,
		},
		Processes:    processes,
		ErrorMessage: result.ErrorMessage,
	}
}

// StopAppByCmd stops an application using the provided stop command
//
// Example:
//
//	client, _ := agentbay.NewAgentBay(os.Getenv("AGENTBAY_API_KEY"), nil)
//	result, _ := client.Create(agentbay.NewCreateSessionParams().WithImageId("mobile_latest"))
//	defer result.Session.Delete()
//	stopResult := result.Session.Mobile.StopAppByCmd("com.android.calculator2")
func (m *Mobile) StopAppByCmd(stopCmd string) *BoolResult {
	args := map[string]interface{}{
		"stop_cmd": stopCmd,
	}

	result, err := m.Session.CallMcpTool("stop_app_by_cmd", args)
	if err != nil {
		return &BoolResult{
			ApiResponse: models.ApiResponse{
				RequestID: "",
			},
			Success:      false,
			ErrorMessage: fmt.Sprintf("failed to call stop_app_by_cmd: %v", err),
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

// Screenshot takes a screenshot of the current screen
//
// Example:
//
//	client, _ := agentbay.NewAgentBay(os.Getenv("AGENTBAY_API_KEY"), nil)
//	result, _ := client.Create(agentbay.NewCreateSessionParams().WithImageId("mobile_latest"))
//	defer result.Session.Delete()
//	screenshot := result.Session.Mobile.Screenshot()
func (m *Mobile) Screenshot() *ScreenshotResult {
	args := map[string]interface{}{}

	result, err := m.Session.CallMcpTool("system_screenshot", args)
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

// BetaTakeScreenshot captures the current screen as a PNG image and returns raw image bytes.
//
// It calls the MCP tool "screenshot" with format="png".
func (m *Mobile) BetaTakeScreenshot() *BetaScreenshotResult {
	args := map[string]interface{}{
		"format": "png",
	}

	result, err := m.Session.CallMcpTool("screenshot", args)
	if err != nil {
		return &BetaScreenshotResult{
			ApiResponse:  models.ApiResponse{RequestID: ""},
			Success:      false,
			Data:         nil,
			Format:       "png",
			ErrorMessage: fmt.Sprintf("failed to call screenshot: %v", err),
		}
	}

	if !result.Success {
		return &BetaScreenshotResult{
			ApiResponse:  models.ApiResponse{RequestID: result.RequestID},
			Success:      false,
			Data:         nil,
			Format:       "png",
			ErrorMessage: result.ErrorMessage,
		}
	}

	img, fmtNorm, width, height, err := decodeBase64Image(result.Data, "png")
	if err != nil {
		return &BetaScreenshotResult{
			ApiResponse:  models.ApiResponse{RequestID: result.RequestID},
			Success:      false,
			Data:         nil,
			Format:       "png",
			ErrorMessage: fmt.Sprintf("failed to decode screenshot data: %v", err),
		}
	}

	return &BetaScreenshotResult{
		ApiResponse:  models.ApiResponse{RequestID: result.RequestID},
		Success:      true,
		Data:         img,
		Format:       fmtNorm,
		Width:        width,
		Height:       height,
		ErrorMessage: "",
	}
}

// BetaTakeLongScreenshot captures a long screenshot and returns raw image bytes.
//
// Supported formats:
// - "png"
// - "jpeg" (or "jpg")
func (m *Mobile) BetaTakeLongScreenshot(maxScreens int, format string, quality ...int) *BetaScreenshotResult {
	if maxScreens < 2 || maxScreens > 10 {
		return &BetaScreenshotResult{
			ApiResponse:  models.ApiResponse{RequestID: ""},
			Success:      false,
			Data:         nil,
			Format:       "",
			ErrorMessage: "invalid maxScreens: must be in range [2, 10]",
		}
	}

	formatNorm := normalizeImageFormat(format, "png")
	if formatNorm != "png" && formatNorm != "jpeg" {
		return &BetaScreenshotResult{
			ApiResponse:  models.ApiResponse{RequestID: ""},
			Success:      false,
			Data:         nil,
			Format:       formatNorm,
			ErrorMessage: fmt.Sprintf("unsupported format: %q. Supported values: \"png\", \"jpeg\".", format),
		}
	}

	args := map[string]interface{}{
		"max_screens": maxScreens,
		"format":      formatNorm,
	}
	if len(quality) > 0 {
		q := quality[0]
		if q < 1 || q > 100 {
			return &BetaScreenshotResult{
				ApiResponse:  models.ApiResponse{RequestID: ""},
				Success:      false,
				Data:         nil,
				Format:       formatNorm,
				ErrorMessage: "invalid quality: must be in range [1, 100]",
			}
		}
		args["quality"] = q
	}

	result, err := m.Session.CallMcpTool("long_screenshot", args)
	if err != nil {
		return &BetaScreenshotResult{
			ApiResponse:  models.ApiResponse{RequestID: ""},
			Success:      false,
			Data:         nil,
			Format:       formatNorm,
			ErrorMessage: fmt.Sprintf("failed to call long_screenshot: %v", err),
		}
	}

	if !result.Success {
		return &BetaScreenshotResult{
			ApiResponse:  models.ApiResponse{RequestID: result.RequestID},
			Success:      false,
			Data:         nil,
			Format:       formatNorm,
			ErrorMessage: result.ErrorMessage,
		}
	}

	img, fmtDetected, width, height, err := decodeBase64Image(result.Data, formatNorm)
	if err != nil {
		return &BetaScreenshotResult{
			ApiResponse:  models.ApiResponse{RequestID: result.RequestID},
			Success:      false,
			Data:         nil,
			Format:       formatNorm,
			ErrorMessage: fmt.Sprintf("failed to decode long screenshot data: %v", err),
		}
	}

	return &BetaScreenshotResult{
		ApiResponse:  models.ApiResponse{RequestID: result.RequestID},
		Success:      true,
		Data:         img,
		Format:       fmtDetected,
		Width:        width,
		Height:       height,
		ErrorMessage: "",
	}
}

var (
	pngMagic  = []byte{0x89, 0x50, 0x4e, 0x47, 0x0d, 0x0a, 0x1a, 0x0a}
	jpegMagic = []byte{0xff, 0xd8, 0xff}
)

func normalizeImageFormat(format string, defaultValue string) string {
	f := strings.TrimSpace(strings.ToLower(format))
	if f == "" {
		return defaultValue
	}
	if f == "jpg" {
		return "jpeg"
	}
	return f
}

func decodeBase64Image(text string, expectedFormat string) ([]byte, string, *int, *int, error) {
	s := strings.TrimSpace(text)
	if s == "" {
		return nil, expectedFormat, nil, nil, fmt.Errorf("empty image data")
	}

	// Backend contract: screenshot tool returns a JSON object string with
	// top-level field "data" containing base64.
	if !strings.HasPrefix(s, "{") {
		return nil, expectedFormat, nil, nil, fmt.Errorf("screenshot tool returned non-JSON data")
	}
	type screenshotJSON struct {
		Data   string `json:"data"`
		Width  *int   `json:"width"`
		Height *int   `json:"height"`
	}
	var payload screenshotJSON
	if err := json.Unmarshal([]byte(s), &payload); err != nil {
		return nil, expectedFormat, nil, nil, fmt.Errorf("invalid screenshot JSON: %w", err)
	}
	b64 := strings.TrimSpace(payload.Data)
	if b64 == "" {
		return nil, expectedFormat, nil, nil, fmt.Errorf("screenshot JSON missing base64 field")
	}

	b, err := base64.StdEncoding.DecodeString(b64)
	if err != nil {
		return nil, expectedFormat, nil, nil, err
	}

	exp := normalizeImageFormat(expectedFormat, expectedFormat)
	if exp == "png" {
		if !bytes.HasPrefix(b, pngMagic) {
			return nil, expectedFormat, nil, nil, fmt.Errorf("decoded image does not match expected format")
		}
		return b, "png", payload.Width, payload.Height, nil
	}
	if exp == "jpeg" {
		if !bytes.HasPrefix(b, jpegMagic) {
			return nil, expectedFormat, nil, nil, fmt.Errorf("decoded image does not match expected format")
		}
		return b, "jpeg", payload.Width, payload.Height, nil
	}

	if bytes.HasPrefix(b, pngMagic) {
		return b, "png", payload.Width, payload.Height, nil
	}
	if bytes.HasPrefix(b, jpegMagic) {
		return b, "jpeg", payload.Width, payload.Height, nil
	}
	return nil, expectedFormat, nil, nil, fmt.Errorf("decoded image does not match expected format")
}

// Configure configures mobile settings from MobileExtraConfig
func (m *Mobile) Configure(mobileConfig *models.MobileExtraConfig) error {
	if mobileConfig == nil {
		return fmt.Errorf("no mobile configuration provided")
	}

	// Configure resolution lock
	if err := m.setResolutionLock(mobileConfig.LockResolution); err != nil {
		return fmt.Errorf("failed to set resolution lock: %v", err)
	}

	// Configure app management rules
	if mobileConfig.AppManagerRule != nil && mobileConfig.AppManagerRule.RuleType != "" {
		appRule := mobileConfig.AppManagerRule
		packageNames := appRule.AppPackageNameList

		if len(packageNames) > 0 && (appRule.RuleType == "White" || appRule.RuleType == "Black") {
			if appRule.RuleType == "White" {
				if err := m.setAppWhitelist(packageNames); err != nil {
					return fmt.Errorf("failed to set app whitelist: %v", err)
				}
			} else {
				if err := m.setAppBlacklist(packageNames); err != nil {
					return fmt.Errorf("failed to set app blacklist: %v", err)
				}
			}
		} else if len(packageNames) == 0 {
			return fmt.Errorf("no package names provided for %s list", appRule.RuleType)
		}
	}

	// Configure navigation bar visibility
	if err := m.setNavigationBarVisibility(mobileConfig.HideNavigationBar); err != nil {
		return fmt.Errorf("failed to set navigation bar visibility: %v", err)
	}

	// Configure uninstall blacklist
	if len(mobileConfig.UninstallBlacklist) > 0 {
		if err := m.setUninstallBlacklist(mobileConfig.UninstallBlacklist); err != nil {
			return fmt.Errorf("failed to set uninstall blacklist: %v", err)
		}
	}

	return nil
}

// SetResolutionLock sets display resolution lock for mobile devices
//
// Example:
//
//	client, _ := agentbay.NewAgentBay(os.Getenv("AGENTBAY_API_KEY"), nil)
//	result, _ := client.Create(agentbay.NewCreateSessionParams().WithImageId("mobile_latest"))
//	defer result.Session.Delete()
//	err := result.Session.Mobile.SetResolutionLock(true)
func (m *Mobile) SetResolutionLock(enable bool) error {
	return m.setResolutionLock(enable)
}

// setResolutionLock internal method to set resolution lock
func (m *Mobile) setResolutionLock(enable bool) error {
	var templateName string
	if enable {
		templateName = "resolution_lock_enable"
	} else {
		templateName = "resolution_lock_disable"
	}

	template, exists := command.GetMobileCommandTemplate(templateName)
	if !exists {
		return fmt.Errorf("resolution lock template not found: %s", templateName)
	}

	return m.executeTemplateCommand(template, templateName)
}

// setAppWhitelist sets app whitelist configuration
func (m *Mobile) setAppWhitelist(packageNames []string) error {
	template, exists := command.GetMobileCommandTemplate("app_whitelist")
	if !exists {
		return fmt.Errorf("app whitelist template not found")
	}

	// Replace placeholder with actual package names (newline-separated for file content)
	packageList := strings.Join(packageNames, "\n")
	command := strings.ReplaceAll(template, "{package_list}", packageList)

	return m.executeTemplateCommand(command, fmt.Sprintf("App whitelist configuration (%d packages)", len(packageNames)))
}

// setAppBlacklist sets app blacklist configuration
func (m *Mobile) setAppBlacklist(packageNames []string) error {
	template, exists := command.GetMobileCommandTemplate("app_blacklist")
	if !exists {
		return fmt.Errorf("app blacklist template not found")
	}

	// Replace placeholder with actual package names (newline-separated for file content)
	packageList := strings.Join(packageNames, "\n")
	command := strings.ReplaceAll(template, "{package_list}", packageList)

	return m.executeTemplateCommand(command, fmt.Sprintf("App blacklist configuration (%d packages)", len(packageNames)))
}

// setNavigationBarVisibility sets navigation bar visibility
func (m *Mobile) setNavigationBarVisibility(hide bool) error {
	var templateName string
	if hide {
		templateName = "hide_navigation_bar"
	} else {
		templateName = "show_navigation_bar"
	}

	template, exists := command.GetMobileCommandTemplate(templateName)
	if !exists {
		return fmt.Errorf("navigation bar template not found: %s", templateName)
	}

	description := fmt.Sprintf("Navigation bar visibility (hide: %t)", hide)
	return m.executeTemplateCommand(template, description)
}

// setUninstallBlacklist sets uninstall protection blacklist
func (m *Mobile) setUninstallBlacklist(packageNames []string) error {
	template, exists := command.GetMobileCommandTemplate("uninstall_blacklist")
	if !exists {
		return fmt.Errorf("uninstall blacklist template not found")
	}

	// Replace placeholder with actual package names (newline-separated for file content)
	packageList := strings.Join(packageNames, "\n")
	command := strings.ReplaceAll(template, "{package_list}", packageList)

	// Replace timestamp placeholder with current timestamp
	timestamp := fmt.Sprintf("%d", time.Now().Unix())
	command = strings.ReplaceAll(command, "{timestamp}", timestamp)

	description := fmt.Sprintf("Uninstall blacklist configuration (%d packages)", len(packageNames))
	return m.executeTemplateCommand(command, description)
}

// SetNavigationBarVisibility sets navigation bar visibility for mobile devices
//
// Example:
//
//	client, _ := agentbay.NewAgentBay(os.Getenv("AGENTBAY_API_KEY"), nil)
//	result, _ := client.Create(agentbay.NewCreateSessionParams().WithImageId("mobile_latest"))
//	defer result.Session.Delete()
//	err := result.Session.Mobile.SetNavigationBarVisibility(true)
func (m *Mobile) SetNavigationBarVisibility(hide bool) error {
	return m.setNavigationBarVisibility(hide)
}

// SetUninstallBlacklist sets uninstall protection blacklist for mobile devices
//
// Example:
//
//	client, _ := agentbay.NewAgentBay(os.Getenv("AGENTBAY_API_KEY"), nil)
//	result, _ := client.Create(agentbay.NewCreateSessionParams().WithImageId("mobile_latest"))
//	defer result.Session.Delete()
//	protectedApps := []string{"com.android.calculator2"}
//	err := result.Session.Mobile.SetUninstallBlacklist(protectedApps)
func (m *Mobile) SetUninstallBlacklist(packageNames []string) error {
	return m.setUninstallBlacklist(packageNames)
}

// SetAppWhitelist sets app whitelist for mobile devices
//
// Example:
//
//	client, _ := agentbay.NewAgentBay(os.Getenv("AGENTBAY_API_KEY"), nil)
//	result, _ := client.Create(agentbay.NewCreateSessionParams().WithImageId("mobile_latest"))
//	defer result.Session.Delete()
//	allowedApps := []string{"com.android.calculator2"}
//	err := result.Session.Mobile.SetAppWhitelist(allowedApps)
func (m *Mobile) SetAppWhitelist(packageNames []string) error {
	return m.setAppWhitelist(packageNames)
}

// SetAppBlacklist sets app blacklist for mobile devices
//
// Example:
//
//	client, _ := agentbay.NewAgentBay(os.Getenv("AGENTBAY_API_KEY"), nil)
//	result, _ := client.Create(agentbay.NewCreateSessionParams().WithImageId("mobile_latest"))
//	defer result.Session.Delete()
//	blockedApps := []string{"com.example.blockedapp"}
//	err := result.Session.Mobile.SetAppBlacklist(blockedApps)
func (m *Mobile) SetAppBlacklist(packageNames []string) error {
	return m.setAppBlacklist(packageNames)
}

// executeTemplateCommand executes a mobile command template
func (m *Mobile) executeTemplateCommand(commandTemplate, description string) error {
	if m.command == nil {
		return fmt.Errorf("command service not available")
	}

	fmt.Printf("Executing %s\n", description)

	result, err := m.command.ExecuteCommand(commandTemplate)
	if err != nil {
		return fmt.Errorf("failed to execute %s: %v", description, err)
	}

	if result != nil && result.Output != "" {
		fmt.Printf("✅ %s completed successfully\n", description)
	}

	return nil
}

// GetAdbUrl retrieves the ADB connection URL for the mobile environment.
// This method is only supported in mobile environments (mobile_latest image).
// It uses the provided ADB public key to establish the connection and returns
// the ADB connect URL.
//
// Example:
//
//	client, _ := agentbay.NewAgentBay(os.Getenv("AGENTBAY_API_KEY"), nil)
//	result, _ := client.Create(agentbay.NewCreateSessionParams().WithImageId("mobile_latest"))
//	defer result.Session.Delete()
//	adbPubKey, _ := os.ReadFile(os.Getenv("HOME") + "/.android/adbkey.pub")
//	adbResult := result.Session.Mobile.GetAdbUrl(string(adbPubKey))
func (m *Mobile) GetAdbUrl(adbkeyPub string) *AdbUrlResult {
	// Build options JSON with adbkey_pub
	optionsMap := map[string]string{"adbkey_pub": adbkeyPub}
	optionsJSON, err := json.Marshal(optionsMap)
	if err != nil {
		errorMsg := fmt.Sprintf("Failed to marshal options: %v", err)
		return &AdbUrlResult{
			ApiResponse:  models.ApiResponse{RequestID: ""},
			URL:          "",
			Success:      false,
			ErrorMessage: errorMsg,
		}
	}

	// Call GetAdbLink API with authorization, session_id and options
	optionsStr := string(optionsJSON)

	getAdbLinkRequest := &mcp.GetAdbLinkRequest{
		Authorization: tea.String("Bearer " + m.Session.GetAPIKey()),
		SessionId:     tea.String(m.Session.GetSessionId()),
		Option:        tea.String(optionsStr),
	}

	// Log the API call (blue color)
	fmt.Printf("\033[34m🔗 API Call: GetAdbLink\033[0m\n")
	fmt.Printf("   └─ SessionId=%s, Options=provided\n", m.Session.GetSessionId())

	response, err := m.Session.GetClient().GetAdbLink(getAdbLinkRequest)
	if err != nil {
		errorMsg := fmt.Sprintf("Failed to get ADB URL: %v", err)
		fmt.Printf("\033[31m❌ API Response Failed: GetAdbLink\033[0m\n")
		fmt.Printf("   └─ Error: %s\n", errorMsg)
		return &AdbUrlResult{
			ApiResponse:  models.ApiResponse{RequestID: ""},
			URL:          "",
			Success:      false,
			ErrorMessage: errorMsg,
		}
	}

	// Extract request ID from response
	requestID := ""
	if response.Body != nil && response.Body.RequestId != nil {
		requestID = tea.StringValue(response.Body.RequestId)
	}

	// Check if response is successful
	if response.Body == nil || response.Body.Success == nil || !*response.Body.Success {
		errorMsg := "Unknown error"
		if response.Body != nil && response.Body.Message != nil {
			errorMsg = *response.Body.Message
		}
		fmt.Printf("\033[31m❌ Failed to get ADB URL: %s\033[0m\n", errorMsg)
		return &AdbUrlResult{
			ApiResponse:  models.ApiResponse{RequestID: requestID},
			URL:          "",
			Success:      false,
			ErrorMessage: errorMsg,
		}
	}

	// Extract URL from response
	url := ""
	if response.Body.Data != nil && response.Body.Data.Url != nil {
		url = tea.StringValue(response.Body.Data.Url)
	}

	// Log the successful response (green color, no masking for user convenience)
	fmt.Printf("\033[32m✅ API Response: GetAdbLink, RequestId=%s\033[0m\n", requestID)
	if url != "" {
		fmt.Printf("\033[32m   └─ url=%s\033[0m\n", url)
	}

	return &AdbUrlResult{
		ApiResponse:  models.ApiResponse{RequestID: requestID},
		URL:          url,
		Success:      true,
		ErrorMessage: "",
	}
}
