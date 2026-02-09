package code

import (
	"encoding/json"
	"fmt"
	"strings"

	mcp "github.com/aliyun/wuying-agentbay-sdk/golang/api/client"
	"github.com/aliyun/wuying-agentbay-sdk/golang/pkg/agentbay/internal"
	"github.com/aliyun/wuying-agentbay-sdk/golang/pkg/agentbay/models"
)

// WsStreamClient is a public interface for WebSocket streaming clients.
// It abstracts the internal WsClient to allow external packages (e.g., tests)
// to implement GetWsClient without importing the internal package.
type WsStreamClient interface {
	CallStream(target string, data map[string]interface{},
		onEvent func(string, map[string]interface{}),
		onEnd func(string, map[string]interface{}),
		onError func(string, error),
	) (*internal.WsStreamHandle, error)
}

// CodeExecutionError represents an error during code execution
type CodeExecutionError struct {
	Name      string `json:"name"`
	Value     string `json:"value"`
	Traceback string `json:"traceback"`
}

// CodeExecutionLogs represents stdout and stderr logs
type CodeExecutionLogs struct {
	Stdout []string `json:"stdout"`
	Stderr []string `json:"stderr"`
}

// CodeExecutionResultItem represents a single result item (text, image, etc.)
type CodeExecutionResultItem struct {
	Text         string      `json:"text,omitempty"`
	HTML         string      `json:"html,omitempty"`
	Markdown     string      `json:"markdown,omitempty"`
	PNG          string      `json:"png,omitempty"`
	JPEG         string      `json:"jpeg,omitempty"`
	SVG          string      `json:"svg,omitempty"`
	Latex        string      `json:"latex,omitempty"`
	JSON         interface{} `json:"json,omitempty"`
	Chart        interface{} `json:"chart,omitempty"`
	IsMainResult bool        `json:"is_main_result,omitempty"`
}

// CodeResult represents the result of a code execution
type CodeResult struct {
	models.ApiResponse // Embedded ApiResponse

	// Legacy/Simple output
	Output string

	// Enhanced fields
	Success        bool                      `json:"success"`
	Result         string                    `json:"result"` // Legacy compatible result text
	ErrorMessage   string                    `json:"error_message,omitempty"`
	Logs           *CodeExecutionLogs        `json:"logs,omitempty"`
	Results        []CodeExecutionResultItem `json:"results,omitempty"`
	Error          *CodeExecutionError       `json:"error,omitempty"`
	ExecutionTime  float64                   `json:"execution_time,omitempty"`
	ExecutionCount *int                      `json:"execution_count,omitempty"`
}

// Code handles code execution operations in the AgentBay cloud environment.
type Code struct {
	Session interface {
		GetAPIKey() string
		GetClient() *mcp.Client
		GetSessionId() string
		CallMcpTool(toolName string, args interface{}) (*models.McpToolResult, error)
		GetWsClient() (interface{}, error)
	}
}

// NewCode creates a new Code instance
func NewCode(session interface {
	GetAPIKey() string
	GetClient() *mcp.Client
	GetSessionId() string
	CallMcpTool(toolName string, args interface{}) (*models.McpToolResult, error)
	GetWsClient() (interface{}, error)
}) *Code {
	return &Code{
		Session: session,
	}
}

type RunCodeStreamBetaOptions struct {
	TimeoutS   int
	StreamBeta bool
	OnStdout   func(chunk string)
	OnStderr   func(chunk string)
	OnError    func(err error)
}

func (c *Code) runCodeStreamWs(code string, language string, timeoutS int, opts *RunCodeStreamBetaOptions) (*CodeResult, error) {
	if timeoutS <= 0 {
		timeoutS = 60
	}

	rawLanguage := language
	normalizedLanguage := strings.ToLower(strings.TrimSpace(language))
	aliases := map[string]string{
		"py":      "python",
		"python3": "python",
		"js":      "javascript",
		"node":    "javascript",
		"nodejs":  "javascript",
	}
	if canonical, ok := aliases[normalizedLanguage]; ok {
		normalizedLanguage = canonical
	}

	switch normalizedLanguage {
	case "python", "javascript", "r", "java":
	default:
		return &CodeResult{
			Success:      false,
			ErrorMessage: fmt.Sprintf("Unsupported language: %s. Supported languages are 'python', 'javascript', 'r', and 'java'", rawLanguage),
		}, nil
	}

	wsClientRaw, err := c.Session.GetWsClient()
	if err != nil {
		return &CodeResult{
			Success:      false,
			ErrorMessage: err.Error(),
		}, nil
	}
	wsClient, wsOk := wsClientRaw.(*internal.WsClient)
	if !wsOk || wsClient == nil {
		return &CodeResult{
			Success:      false,
			ErrorMessage: "invalid or nil WsClient returned from session",
		}, nil
	}

	stdoutChunks := []string{}
	stderrChunks := []string{}
	results := []CodeExecutionResultItem{}
	var executionCount *int
	executionTime := float64(0)
	var execErrMsg string

	target := "wuying_codespace"
	handle, err := wsClient.CallStream(
		target,
		map[string]interface{}{
			"method": "run_code",
			"mode":   "stream",
			"params": map[string]interface{}{
				"language": normalizedLanguage,
				"timeoutS": timeoutS,
				"code":     code,
			},
		},
		func(_ string, data map[string]interface{}) {
			eventType, _ := data["eventType"].(string)
			switch eventType {
			case "stdout":
				chunk := fmt.Sprintf("%v", data["chunk"])
				stdoutChunks = append(stdoutChunks, chunk)
				if opts != nil && opts.OnStdout != nil {
					opts.OnStdout(chunk)
				}
			case "stderr":
				chunk := fmt.Sprintf("%v", data["chunk"])
				stderrChunks = append(stderrChunks, chunk)
				if opts != nil && opts.OnStderr != nil {
					opts.OnStderr(chunk)
				}
			case "result":
				if m, ok := data["result"].(map[string]interface{}); ok {
					results = append(results, parseResultItemFromMimeMap(m))
				} else {
					results = append(results, CodeExecutionResultItem{Text: fmt.Sprintf("%v", data["result"])})
				}
			case "error":
				execErrMsg = fmt.Sprintf("%v", data["error"])
				if opts != nil && opts.OnError != nil {
					opts.OnError(fmt.Errorf("%s", execErrMsg))
				}
			}
		},
		func(_ string, data map[string]interface{}) {
			if v, ok := data["executionCount"]; ok {
				if i, ok := toInt(v); ok {
					executionCount = &i
				}
			}
			if v, ok := data["executionTime"]; ok {
				if f, ok := toFloat(v); ok {
					executionTime = f
				}
			}
			if v, ok := data["executionError"]; ok && v != nil && fmt.Sprintf("%v", v) != "" {
				execErrMsg = fmt.Sprintf("%v", v)
			}
		},
		func(_ string, e error) {
			if opts != nil && opts.OnError != nil {
				opts.OnError(e)
			}
			if execErrMsg == "" {
				execErrMsg = e.Error()
			}
		},
	)
	if err != nil {
		return &CodeResult{
			ApiResponse:  models.ApiResponse{RequestID: ""},
			Success:      false,
			ErrorMessage: err.Error(),
		}, nil
	}

	endData, err := handle.WaitEnd()
	if err != nil {
		return &CodeResult{
			ApiResponse:  models.ApiResponse{RequestID: handle.InvocationID},
			Success:      false,
			ErrorMessage: err.Error(),
			Logs:         &CodeExecutionLogs{Stdout: stdoutChunks, Stderr: stderrChunks},
			Results:      results,
		}, nil
	}
	_ = endData

	ok := execErrMsg == ""
	if st, okSt := endData["status"].(string); okSt && st == "failed" {
		ok = false
	}

	res := &CodeResult{
		ApiResponse:    models.ApiResponse{RequestID: handle.InvocationID},
		Success:        ok,
		ErrorMessage:   execErrMsg,
		Logs:           &CodeExecutionLogs{Stdout: stdoutChunks, Stderr: stderrChunks},
		Results:        results,
		ExecutionTime:  executionTime,
		ExecutionCount: executionCount,
	}

	foundText := false
	for _, r := range res.Results {
		if r.IsMainResult && r.Text != "" {
			res.Output = r.Text
			res.Result = r.Text
			foundText = true
			break
		}
	}
	if !foundText && len(res.Results) > 0 && res.Results[0].Text != "" {
		res.Output = res.Results[0].Text
		res.Result = res.Results[0].Text
		foundText = true
	}
	if !foundText && len(stdoutChunks) > 0 {
		res.Output = strings.Join(stdoutChunks, "")
		res.Result = res.Output
	}

	if !res.Success && res.ErrorMessage == "" {
		res.ErrorMessage = "Failed to run code"
	}
	return res, nil
}

func parseResultItemFromMimeMap(itemMap map[string]interface{}) CodeExecutionResultItem {
	item := CodeExecutionResultItem{
		JSON:  itemMap["application/json"],
		Chart: itemMap["chart"],
	}

	if val, ok := itemMap["isMainResult"].(bool); ok {
		item.IsMainResult = val
	}
	if val, ok := itemMap["is_main_result"].(bool); ok {
		item.IsMainResult = val
	}
	if val, ok := itemMap["text/plain"].(string); ok {
		item.Text = val
	}
	if val, ok := itemMap["text/html"].(string); ok {
		item.HTML = val
	}
	if val, ok := itemMap["text/markdown"].(string); ok {
		item.Markdown = val
	}
	if val, ok := itemMap["image/png"].(string); ok {
		item.PNG = val
	}
	if val, ok := itemMap["image/jpeg"].(string); ok {
		item.JPEG = val
	}
	if val, ok := itemMap["image/svg+xml"].(string); ok {
		item.SVG = val
	}
	if val, ok := itemMap["text/latex"].(string); ok {
		item.Latex = val
	}
	if val, ok := itemMap["application/vnd.vegalite.v4+json"]; ok {
		item.Chart = val
	}
	if val, ok := itemMap["application/vnd.vegalite.v5+json"]; ok {
		item.Chart = val
	}
	if val, ok := itemMap["application/vnd.vega.v5+json"]; ok {
		item.Chart = val
	}
	return item
}

func toInt(v interface{}) (int, bool) {
	switch t := v.(type) {
	case float64:
		return int(t), true
	case int:
		return t, true
	case int64:
		return int(t), true
	case json.Number:
		i, err := t.Int64()
		if err != nil {
			return 0, false
		}
		return int(i), true
	default:
		return 0, false
	}
}

func toFloat(v interface{}) (float64, bool) {
	switch t := v.(type) {
	case float64:
		return t, true
	case int:
		return float64(t), true
	case int64:
		return float64(t), true
	case json.Number:
		f, err := t.Float64()
		if err != nil {
			return 0, false
		}
		return f, true
	default:
		return 0, false
	}
}

// backendResponse represents the raw JSON structure returned by the backend tool
type backendResponse struct {
	ExecutionError string   `json:"executionError"`
	Result         []string `json:"result"` // List of JSON strings
	Stdout         []string `json:"stdout"`
	Stderr         []string `json:"stderr"`
	TraceID        string   `json:"traceId"`
	// Try both cases just in case
	ExecutionTime   float64 `json:"executionTime"`
	ExecutionTimeSn float64 `json:"execution_time"`
	ExecutionCount  *int    `json:"executionCount"`
	ExecutionCntSn  *int    `json:"execution_count"`
}

func parseBackendResponse(data string) (*CodeResult, error) {
	var raw backendResponse
	if err := json.Unmarshal([]byte(data), &raw); err != nil {
		return nil, err
	}

	// Check if it's actually the expected structure (e.g. has result or stdout/stderr keys)
	// If unmarshal into empty struct, it might succeed but be empty.
	// But since Result/Stdout are slices, they will be nil or empty.
	// We can check if data looks like JSON object.
	// But let's assume if Unmarshal works and we find keys, it's good.

	logs := &CodeExecutionLogs{
		Stdout: raw.Stdout,
		Stderr: raw.Stderr,
	}
	if logs.Stdout == nil {
		logs.Stdout = []string{}
	}
	if logs.Stderr == nil {
		logs.Stderr = []string{}
	}

	execTime := raw.ExecutionTime
	if execTime == 0 {
		execTime = raw.ExecutionTimeSn
	}

	execCount := raw.ExecutionCount
	if execCount == nil {
		execCount = raw.ExecutionCntSn
	}

	res := &CodeResult{
		Success:        true,
		Logs:           logs,
		ExecutionTime:  execTime,
		ExecutionCount: execCount,
	}

	// Parse Results
	for _, resultStr := range raw.Result {
		var itemMap map[string]interface{}
		if err := json.Unmarshal([]byte(resultStr), &itemMap); err != nil {
			continue
		}

		item := CodeExecutionResultItem{
			JSON:  itemMap["json"],
			Chart: itemMap["chart"],
		}

		if val, ok := itemMap["isMainResult"].(bool); ok {
			item.IsMainResult = val
		}

		// Map MIME types to fields
		if val, ok := itemMap["text/plain"].(string); ok {
			item.Text = val
		}
		if val, ok := itemMap["text/html"].(string); ok {
			item.HTML = val
		}
		if val, ok := itemMap["text/markdown"].(string); ok {
			item.Markdown = val
		}
		if val, ok := itemMap["image/png"].(string); ok {
			item.PNG = val
		}
		if val, ok := itemMap["image/jpeg"].(string); ok {
			item.JPEG = val
		}
		if val, ok := itemMap["image/svg+xml"].(string); ok {
			item.SVG = val
		}
		if val, ok := itemMap["text/latex"].(string); ok {
			item.Latex = val
		}
		// Handle JSON and Chart mime types
		if val, ok := itemMap["application/json"]; ok {
			item.JSON = val
		}
		if val, ok := itemMap["application/vnd.vegalite.v4+json"]; ok {
			item.Chart = val
		}
		if val, ok := itemMap["application/vnd.vegalite.v5+json"]; ok {
			item.Chart = val
		}
		if val, ok := itemMap["application/vnd.vega.v5+json"]; ok {
			item.Chart = val
		}

		res.Results = append(res.Results, item)
	}
	if res.Results == nil {
		res.Results = []CodeExecutionResultItem{}
	}

	// Handle Error
	if raw.ExecutionError != "" {
		res.Success = false
		res.Error = &CodeExecutionError{
			Value: raw.ExecutionError,
			// Name and Traceback might not be parsed from simple string
		}
		res.ErrorMessage = raw.ExecutionError
	}

	// Construct Result/Output string for backward compatibility
	foundText := false
	for _, r := range res.Results {
		if r.IsMainResult && r.Text != "" {
			res.Output = r.Text
			res.Result = r.Text
			foundText = true
			break
		}
	}
	if !foundText && len(res.Results) > 0 && res.Results[0].Text != "" {
		res.Output = res.Results[0].Text
		res.Result = res.Results[0].Text
		foundText = true
	}
	if !foundText && len(res.Logs.Stdout) > 0 {
		res.Output = strings.Join(res.Logs.Stdout, "")
		res.Result = res.Output
	}

	return res, nil
}

// RunCode executes code in the session environment.
// timeoutS: The timeout for the code execution in seconds. Default is 60s.
// Note: Due to gateway limitations, each request cannot exceed 60 seconds.
//
// language is case-insensitive. Supported values: "python", "javascript", "r", "java".
//
// Example:
//
//	client, _ := agentbay.NewAgentBay(os.Getenv("AGENTBAY_API_KEY"), nil)
//	sessionResult, _ := client.Create(agentbay.NewCreateSessionParams().WithImageId("code_latest"))
//	defer sessionResult.Session.Delete()
//	codeResult, _ := sessionResult.Session.Code.RunCode("print('Hello')", "python")
func (c *Code) RunCode(code string, language string, args ...interface{}) (*CodeResult, error) {
	timeout := 60
	var opts *RunCodeStreamBetaOptions
	for _, a := range args {
		if a == nil {
			continue
		}
		switch v := a.(type) {
		case int:
			if v > 0 {
				timeout = v
			}
		case int32:
			if v > 0 {
				timeout = int(v)
			}
		case int64:
			if v > 0 {
				timeout = int(v)
			}
		case RunCodeStreamBetaOptions:
			tmp := v
			opts = &tmp
		case *RunCodeStreamBetaOptions:
			opts = v
		default:
			return nil, fmt.Errorf("unsupported RunCode argument type: %T", a)
		}
	}

	if opts != nil && opts.TimeoutS > 0 {
		timeout = opts.TimeoutS
	}

	useStream := false
	if opts != nil && (opts.StreamBeta || opts.OnStdout != nil || opts.OnStderr != nil || opts.OnError != nil) {
		useStream = true
	}
	if useStream {
		return c.runCodeStreamWs(code, language, timeout, opts)
	}

	// Normalize and validate language (case-insensitive)
	rawLanguage := language
	normalizedLanguage := strings.ToLower(strings.TrimSpace(language))
	aliases := map[string]string{
		"py":      "python",
		"python3": "python",
		"js":      "javascript",
		"node":    "javascript",
		"nodejs":  "javascript",
	}
	if canonical, ok := aliases[normalizedLanguage]; ok {
		normalizedLanguage = canonical
	}

	switch normalizedLanguage {
	case "python", "javascript", "r", "java":
		// supported
	default:
		return nil, fmt.Errorf(
			"unsupported language: %s. Supported languages are 'python', 'javascript', 'r', and 'java'",
			rawLanguage,
		)
	}

	toolArgs := map[string]interface{}{
		"code":      code,
		"language":  normalizedLanguage,
		"timeout_s": timeout,
	}

	// Use Session's CallMcpTool method
	result, err := c.Session.CallMcpTool("run_code", toolArgs)
	if err != nil {
		return nil, fmt.Errorf("failed to execute code: %w", err)
	}

	var codeRes *CodeResult
	var parseErr error

	if result.Success {
		codeRes, parseErr = parseBackendResponse(result.Data)
	} else {
		// Try parsing error message if it looks like JSON
		if strings.HasPrefix(strings.TrimSpace(result.ErrorMessage), "{") {
			codeRes, parseErr = parseBackendResponse(result.ErrorMessage)
			if codeRes != nil {
				codeRes.Success = false
			}
		} else {
			// Not JSON error, real failure
			return nil, fmt.Errorf("code execution failed: %s", result.ErrorMessage)
		}
	}

	// If parsing failed or result was not enhanced
	if parseErr != nil || codeRes == nil {
		if !result.Success {
			return nil, fmt.Errorf("code execution failed: %s", result.ErrorMessage)
		}
		// Legacy fallback
		codeRes = &CodeResult{
			Success: true,
			Output:  result.Data,
			Result:  result.Data,
		}
	}

	codeRes.RequestID = result.RequestID
	codeRes.ApiResponse = models.ApiResponse{RequestID: result.RequestID}

	return codeRes, nil
}

// Run is an alias of RunCode.
func (c *Code) Run(code string, language string, args ...interface{}) (*CodeResult, error) {
	return c.RunCode(code, language, args...)
}

// Execute is an alias of RunCode.
func (c *Code) Execute(code string, language string, args ...interface{}) (*CodeResult, error) {
	return c.RunCode(code, language, args...)
}
