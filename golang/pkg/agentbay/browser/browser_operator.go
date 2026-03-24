package browser

import (
	"encoding/json"
	"fmt"
	"time"
)

// ActOptions represents options for configuring the act method.
type ActOptions struct {
	Action    string            // The action to perform
	Variables map[string]string // Optional variables for the action
	UseVision *bool             // Whether to use vision-based capabilities
	Timeout   *int              // Timeout in seconds
}

// ActResult represents the result of the act method.
type ActResult struct {
	Success bool
	Message string
}

// ObserveOptions represents options for configuring the observe method.
type ObserveOptions struct {
	Instruction string  // The observation instruction
	UseVision   *bool   // Whether to use vision-based capabilities
	Selector    *string // Optional CSS selector
	Timeout     *int    // Timeout in seconds
}

// ObserveResult represents a single observation result.
type ObserveResult struct {
	Selector    string
	Description string
	Method      string
	Arguments   map[string]interface{}
}

// ExtractOptions represents options for configuring the extract method.
type ExtractOptions struct {
	Instruction    string                 // The extraction instruction
	Schema         map[string]interface{} // JSON schema for the extraction
	UseTextExtract *bool                  // Whether to use text-based extraction
	UseVision      *bool                  // Whether to use vision-based capabilities
	Selector       *string                // Optional CSS selector
	Timeout        *int                   // Timeout in seconds
	MaxPage        *int                   // Maximum number of pages to process
}

// BrowserOperator handles browser automation via MCP tools.
// It provides act, observe, extract and other operations without requiring a direct Playwright connection.
//
// > **⚠️ Note**: Currently, for agent services (including ComputerUseAgent, BrowserUseAgent, and MobileUseAgent),
// > we do not provide services for overseas users registered with **alibabacloud.com**.
type BrowserOperator struct {
	session SessionInterface
	browser *Browser
}

// NewBrowserOperator creates a new BrowserOperator instance.
func NewBrowserOperator(session SessionInterface, browser *Browser) *BrowserOperator {
	return &BrowserOperator{
		session: session,
		browser: browser,
	}
}

func (o *BrowserOperator) callMcpTool(toolName string, args map[string]interface{}) (*McpToolResult, error) {
	return o.session.CallMcpToolForBrowser(toolName, args)
}

// Navigate navigates the browser to the given URL.
//
// Example:
//
//	result, err := session.Browser.Operator.Navigate("https://example.com")
func (o *BrowserOperator) Navigate(url string) (string, error) {
	if !o.browser.IsInitialized() {
		return "", fmt.Errorf("browser must be initialized before calling Navigate")
	}
	args := map[string]interface{}{"url": url}
	result, err := o.callMcpTool("page_use_navigate", args)
	if err != nil {
		return "", fmt.Errorf("failed to navigate: %w", err)
	}
	if result.Success {
		return result.Data, nil
	}
	return fmt.Sprintf("Navigation failed: %s", result.ErrorMessage), nil
}

// Screenshot takes a screenshot of the current page via MCP tool.
// Returns a base64 encoded data URL of the screenshot.
//
// Example:
//
//	data, err := session.Browser.Operator.Screenshot(true, 80, nil, nil)
func (o *BrowserOperator) Screenshot(fullPage bool, quality int, clip map[string]float64, timeout *int) (string, error) {
	if !o.browser.IsInitialized() {
		return "", fmt.Errorf("browser must be initialized before calling Screenshot")
	}
	args := map[string]interface{}{
		"context_id": 0,
		"full_page":  fullPage,
		"quality":    quality,
	}
	if clip != nil {
		args["clip"] = clip
	}
	if timeout != nil {
		args["timeout"] = *timeout
	}
	result, err := o.callMcpTool("page_use_screenshot", args)
	if err != nil {
		return "", fmt.Errorf("failed to take screenshot: %w", err)
	}
	if result.Success {
		return result.Data, nil
	}
	return fmt.Sprintf("Screenshot failed: %s", result.ErrorMessage), nil
}

// Close closes the remote browser operator session.
//
// Example:
//
//	ok, err := session.Browser.Operator.Close()
func (o *BrowserOperator) Close() (bool, error) {
	result, err := o.callMcpTool("page_use_close_session", map[string]interface{}{})
	if err != nil {
		return false, fmt.Errorf("failed to close browser operator session: %w", err)
	}
	return result.Success, nil
}

// Act performs an action on the current web page using async task polling (3s interval).
// The default timeout is 300 seconds if not specified in options.
//
// Example:
//
//	result, err := session.Browser.Operator.Act(&browser.ActOptions{
//	    Action: "click the login button",
//	})
func (o *BrowserOperator) Act(options *ActOptions) (*ActResult, error) {
	if !o.browser.IsInitialized() {
		return nil, fmt.Errorf("browser must be initialized before calling Act")
	}

	args := map[string]interface{}{
		"context_id": 0,
		"action":     options.Action,
	}
	if options.Variables != nil {
		args["variables"] = options.Variables
	}
	if options.UseVision != nil {
		args["use_vision"] = *options.UseVision
	}
	if options.Timeout != nil {
		args["timeout"] = *options.Timeout
	}

	startResp, err := o.callMcpTool("page_use_act_async", args)
	if err != nil {
		return nil, fmt.Errorf("failed to start act task: %w", err)
	}
	if !startResp.Success {
		return nil, fmt.Errorf("failed to start act task: %s", startResp.ErrorMessage)
	}

	var taskData map[string]interface{}
	if err := json.Unmarshal([]byte(startResp.Data), &taskData); err != nil {
		return nil, fmt.Errorf("failed to parse act response: %w", err)
	}
	taskID, ok := taskData["task_id"].(string)
	if !ok {
		return nil, fmt.Errorf("no task_id in act response")
	}

	timeoutS := 300
	if options.Timeout != nil {
		timeoutS = *options.Timeout
	}
	startTS := time.Now()
	noActionMsg := "No actions have been executed."

	for {
		time.Sleep(3 * time.Second)

		pollResp, pollErr := o.callMcpTool("page_use_get_act_result", map[string]interface{}{"task_id": taskID})
		if pollErr == nil && pollResp.Success && pollResp.Data != "" {
			var data map[string]interface{}
			if err := json.Unmarshal([]byte(pollResp.Data), &data); err == nil {
				isDone, _ := data["is_done"].(bool)
				success, _ := data["success"].(bool)
				steps := data["steps"]

				if isDone {
					msg := noActionMsg
					if steps != nil {
						stepsBytes, _ := json.Marshal(steps)
						msg = string(stepsBytes)
					}
					return &ActResult{Success: success, Message: msg}, nil
				}
			}
		}

		if time.Since(startTS).Seconds() >= float64(timeoutS) {
			return nil, fmt.Errorf("task %s: Act timeout after %ds", taskID, timeoutS)
		}
	}
}

// Observe observes elements or state on the current web page using async task polling (3s interval).
// The default timeout is 300 seconds if not specified in options.
//
// Example:
//
//	ok, results, err := session.Browser.Operator.Observe(&browser.ObserveOptions{
//	    Instruction: "find all clickable buttons",
//	})
func (o *BrowserOperator) Observe(options *ObserveOptions) (bool, []ObserveResult, error) {
	if !o.browser.IsInitialized() {
		return false, nil, fmt.Errorf("browser must be initialized before calling Observe")
	}

	args := map[string]interface{}{
		"context_id":  0,
		"instruction": options.Instruction,
	}
	if options.UseVision != nil {
		args["use_vision"] = *options.UseVision
	}
	if options.Selector != nil {
		args["selector"] = *options.Selector
	}
	if options.Timeout != nil {
		args["timeout"] = *options.Timeout
	}

	startResp, err := o.callMcpTool("page_use_observe_async", args)
	if err != nil {
		return false, nil, fmt.Errorf("failed to start observe task: %w", err)
	}
	if !startResp.Success {
		return false, nil, fmt.Errorf("failed to start observe task: %s", startResp.ErrorMessage)
	}

	var taskData map[string]interface{}
	if err := json.Unmarshal([]byte(startResp.Data), &taskData); err != nil {
		return false, nil, fmt.Errorf("failed to parse observe response: %w", err)
	}
	taskID, ok := taskData["task_id"].(string)
	if !ok {
		return false, nil, fmt.Errorf("no task_id in observe response")
	}

	timeoutS := 300
	if options.Timeout != nil {
		timeoutS = *options.Timeout
	}
	startTS := time.Now()

	for {
		time.Sleep(3 * time.Second)

		pollResp, pollErr := o.callMcpTool("page_use_get_observe_result", map[string]interface{}{"task_id": taskID})
		if pollErr == nil && pollResp.Success && pollResp.Data != "" {
			var items []map[string]interface{}
			if err := json.Unmarshal([]byte(pollResp.Data), &items); err == nil {
				results := make([]ObserveResult, 0, len(items))
				for _, item := range items {
					selector, _ := item["selector"].(string)
					description, _ := item["description"].(string)
					method, _ := item["method"].(string)

					var arguments map[string]interface{}
					if argsStr, ok := item["arguments"].(string); ok {
						json.Unmarshal([]byte(argsStr), &arguments) //nolint:errcheck
					} else if argsMap, ok := item["arguments"].(map[string]interface{}); ok {
						arguments = argsMap
					}

					results = append(results, ObserveResult{
						Selector:    selector,
						Description: description,
						Method:      method,
						Arguments:   arguments,
					})
				}
				return true, results, nil
			}
		}

		if time.Since(startTS).Seconds() >= float64(timeoutS) {
			return false, nil, fmt.Errorf("task %s: Observe timeout after %ds", taskID, timeoutS)
		}
	}
}

// Extract extracts structured data from the current web page using async task polling (3s interval).
// The Schema field should be a map representing a JSON schema.
// The returned data is a map[string]interface{} that can be further decoded by the caller.
// The default timeout is 300 seconds if not specified in options.
//
// Example:
//
//	schema := map[string]interface{}{
//	    "type": "object",
//	    "properties": map[string]interface{}{
//	        "title": map[string]interface{}{"type": "string"},
//	    },
//	}
//	ok, data, err := session.Browser.Operator.Extract(&browser.ExtractOptions{
//	    Instruction: "extract the page title",
//	    Schema:      schema,
//	})
func (o *BrowserOperator) Extract(options *ExtractOptions) (bool, map[string]interface{}, error) {
	if !o.browser.IsInitialized() {
		return false, nil, fmt.Errorf("browser must be initialized before calling Extract")
	}

	args := map[string]interface{}{
		"context_id":  0,
		"instruction": options.Instruction,
	}
	if options.Schema != nil {
		schemaBytes, err := json.Marshal(options.Schema)
		if err == nil {
			args["field_schema"] = "schema: " + string(schemaBytes)
		}
	}
	if options.UseTextExtract != nil {
		args["use_text_extract"] = *options.UseTextExtract
	}
	if options.UseVision != nil {
		args["use_vision"] = *options.UseVision
	}
	if options.Selector != nil {
		args["selector"] = *options.Selector
	}
	if options.Timeout != nil {
		args["timeout"] = *options.Timeout
	}
	if options.MaxPage != nil {
		args["max_page"] = *options.MaxPage
	}

	startResp, err := o.callMcpTool("page_use_extract_async", args)
	if err != nil {
		return false, nil, fmt.Errorf("failed to start extract task: %w", err)
	}
	if !startResp.Success {
		return false, nil, fmt.Errorf("failed to start extract task: %s", startResp.ErrorMessage)
	}

	var taskData map[string]interface{}
	if err := json.Unmarshal([]byte(startResp.Data), &taskData); err != nil {
		return false, nil, fmt.Errorf("failed to parse extract response: %w", err)
	}
	taskID, ok := taskData["task_id"].(string)
	if !ok {
		return false, nil, fmt.Errorf("no task_id in extract response")
	}

	timeoutS := 300
	if options.Timeout != nil {
		timeoutS = *options.Timeout
	}
	startTS := time.Now()

	for {
		time.Sleep(3 * time.Second)

		pollResp, pollErr := o.callMcpTool("page_use_get_extract_result", map[string]interface{}{"task_id": taskID})
		if pollErr == nil && pollResp.Success && pollResp.Data != "" {
			var result map[string]interface{}
			if err := json.Unmarshal([]byte(pollResp.Data), &result); err == nil {
				return true, result, nil
			}
		}

		if time.Since(startTS).Seconds() >= float64(timeoutS) {
			return false, nil, fmt.Errorf("task %s: Extract timeout after %ds", taskID, timeoutS)
		}
	}
}
