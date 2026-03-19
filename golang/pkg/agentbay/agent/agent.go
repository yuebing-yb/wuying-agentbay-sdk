package agent

import (
	"encoding/json"
	"fmt"
	"strings"
	"time"

	"github.com/aliyun/wuying-agentbay-sdk/golang/pkg/agentbay/browser"
	"github.com/aliyun/wuying-agentbay-sdk/golang/pkg/agentbay/internal"
	"github.com/aliyun/wuying-agentbay-sdk/golang/pkg/agentbay/models"
	"github.com/invopop/jsonschema"
)

// ExecutionResult represents the result of task execution
type ExecutionResult struct {
	models.ApiResponse
	Success      bool   `json:"success"`
	ErrorMessage string `json:"error_message"`
	TaskID       string `json:"task_id"`
	TaskStatus   string `json:"task_status"`
	TaskResult   string `json:"task_result"`
}

// StreamItem represents a single stream fragment
type StreamItem struct {
	Content     string `json:"content,omitempty"`
	Reasoning   string `json:"reasoning,omitempty"`
	TimestampMs *int64 `json:"timestamp_ms,omitempty"`
}

// AgentEvent represents a streaming event from an Agent execution.
//
// Event types: "reasoning", "content", "tool_call", "tool_result", "error".
//
// The Result field in tool_result events carries an agent-defined structure
// that the SDK passes through without parsing. Typical fields include
// "isError" (bool), "output" (string), and optionally "screenshot" (base64).
// The final task outcome is delivered via the ExecutionResult return value
// of ExecuteTaskAndWait.
type AgentEvent struct {
	Type       string                 `json:"type"`
	Seq        int                    `json:"seq"`
	Round      int                    `json:"round"`
	Content    string                 `json:"content,omitempty"`
	ToolCallID string                 `json:"toolCallId,omitempty"`
	ToolName   string                 `json:"toolName,omitempty"`
	Args       map[string]interface{} `json:"args,omitempty"`
	Result     map[string]interface{} `json:"result,omitempty"`
	Error      map[string]interface{} `json:"error,omitempty"`
}

// AgentEventCallback is a function type for handling agent streaming events.
type AgentEventCallback func(event AgentEvent)

// StreamOptions holds streaming callback options.
type StreamOptions struct {
	OnReasoning  AgentEventCallback
	OnContent    AgentEventCallback
	OnToolCall   AgentEventCallback
	OnToolResult AgentEventCallback
	OnError      AgentEventCallback
}

// MobileTaskOptions holds options for mobile task execution, including
// streaming callbacks inherited from StreamOptions.
type MobileTaskOptions struct {
	StreamOptions
	MaxSteps      int
	OnCallForUser func(event AgentEvent) string
}

// streamContext holds mutable state shared between WS callbacks and TaskExecution.Wait().
type streamContext struct {
	contentParts []string
	lastError    map[string]interface{}
	streamErr    error
}

// TaskExecution represents a running task that can be waited on for its final result.
// Returned by MobileUseAgent.ExecuteTask when the task is started.
type TaskExecution struct {
	TaskID string
	waitFn func(timeout int) *ExecutionResult
}

// Wait blocks until the task finishes or the timeout (in seconds) is reached.
// A timeout of 0 means wait indefinitely (until the task finishes or fails).
func (te *TaskExecution) Wait(timeout int) *ExecutionResult {
	return te.waitFn(timeout)
}

// QueryResult represents the result of query operations
type QueryResult struct {
	models.ApiResponse
	Success      bool         `json:"success"`
	ErrorMessage string       `json:"error_message"`
	TaskID       string       `json:"task_id"`
	TaskStatus   string       `json:"task_status"`
	TaskAction   string       `json:"task_action"`
	TaskProduct  string       `json:"task_product"`
	Stream       []StreamItem `json:"stream,omitempty"`
	Error        string       `json:"error,omitempty"`
}

type DefaultSchema struct {
	Result string `json:"Result" jsonschema:"required"`
}

// baseTaskAgent provides common functionality for task execution agents
type baseTaskAgent struct {
	Session    McpSession
	ToolPrefix string
}

// GenerateJsonSchema generates a JSON schema for the given struct
func generateJsonSchema(schema interface{}) string {
	if schema == nil {
		schema = &DefaultSchema{}
	}
	reflector := jsonschema.Reflector{
		DoNotReference:            true,  // Disable $ref
		AllowAdditionalProperties: false, // Disable additional properties
	}
	output_schema := reflector.Reflect(schema)

	schemaMap := make(map[string]interface{})
	schemaBytes, _ := json.Marshal(output_schema)
	json.Unmarshal(schemaBytes, &schemaMap)

	prettyJSON, _ := json.MarshalIndent(schemaMap, "", "  ")
	return string(prettyJSON)
}

// getToolName returns the full MCP tool name based on prefix and action
func (b *baseTaskAgent) getToolName(action string) string {
	toolMap := map[string]string{
		"execute":    "execute_task",
		"get_status": "get_task_status",
		"terminate":  "terminate_task",
	}
	baseName, ok := toolMap[action]
	if !ok {
		baseName = action
	}
	if b.ToolPrefix != "" {
		return b.ToolPrefix + "_" + baseName
	}
	return baseName
}

// getWsTarget returns the WebSocket target for agent streaming.
// browser_use -> wuying_browseruse, flux -> wuying_computer_agent, empty -> wuying_mobile_agent
func (b *baseTaskAgent) getWsTarget() string {
	if b.ToolPrefix == "browser_use" {
		return "wuying_browseruse"
	}
	if b.ToolPrefix == "flux" {
		return "wuying_computer_agent"
	}
	return "wuying_mobile_agent"
}

// executeTask executes a task in human language without waiting for completion (non-blocking).
// This is a fire-and-return interface that immediately provides a task ID.
// Call getTaskStatus to check the task status.
func (b *baseTaskAgent) executeTask(task string) *ExecutionResult {
	args := map[string]interface{}{
		"task": task,
	}

	result, err := b.Session.CallMcpTool(b.getToolName("execute"), args)
	if err != nil {
		return &ExecutionResult{
			ApiResponse:  models.ApiResponse{RequestID: ""},
			Success:      false,
			ErrorMessage: fmt.Sprintf("Failed to execute: %v", err),
			TaskStatus:   "failed",
			TaskID:       "",
		}
	}

	if !result.Success {
		errorMessage := result.ErrorMessage
		if errorMessage == "" {
			errorMessage = "Failed to execute task"
		}
		return &ExecutionResult{
			ApiResponse:  models.ApiResponse{RequestID: result.RequestID},
			Success:      false,
			ErrorMessage: errorMessage,
			TaskStatus:   "failed",
			TaskID:       "",
		}
	}

	// Parse task ID from response
	var content map[string]interface{}
	if err := json.Unmarshal([]byte(result.Data), &content); err != nil {
		return &ExecutionResult{
			ApiResponse:  models.ApiResponse{RequestID: result.RequestID},
			Success:      false,
			ErrorMessage: fmt.Sprintf("Failed to parse response: %v", err),
			TaskStatus:   "failed",
			TaskID:       "",
		}
	}

	taskID, ok := content["task_id"].(string)
	if !ok {
		errorMessage := "Task ID not found in response"
		if errorVal, exists := content["error"]; exists {
			if errorStr, ok := errorVal.(string); ok {
				errorMessage = errorStr
			}
		}
		return &ExecutionResult{
			ApiResponse:  models.ApiResponse{RequestID: result.RequestID},
			Success:      false,
			ErrorMessage: errorMessage,
			TaskStatus:   "failed",
			TaskID:       "",
		}
	}

	return &ExecutionResult{
		ApiResponse: models.ApiResponse{RequestID: result.RequestID},
		Success:     true,
		TaskID:      taskID,
		TaskStatus:  "running",
	}
}

// executeTaskAndWait executes a specific task described in human language synchronously.
// This is a synchronous interface that blocks until the task is completed or
// an error occurs, or timeout happens. The default polling interval is 3 seconds.
func (b *baseTaskAgent) executeTaskAndWait(task string, timeout int) *ExecutionResult {
	args := map[string]interface{}{
		"task": task,
	}

	result, err := b.Session.CallMcpTool(b.getToolName("execute"), args)
	if err != nil {
		return &ExecutionResult{
			ApiResponse:  models.ApiResponse{RequestID: ""},
			Success:      false,
			ErrorMessage: fmt.Sprintf("Failed to execute: %v", err),
			TaskStatus:   "failed",
			TaskID:       "",
			TaskResult:   "Task Failed",
		}
	}

	if !result.Success {
		errorMessage := result.ErrorMessage
		if errorMessage == "" {
			errorMessage = "Failed to execute task"
		}
		return &ExecutionResult{
			ApiResponse:  models.ApiResponse{RequestID: result.RequestID},
			Success:      false,
			ErrorMessage: errorMessage,
			TaskStatus:   "failed",
			TaskID:       "",
			TaskResult:   "Task Failed",
		}
	}

	// Parse task ID from response
	var content map[string]interface{}
	if err := json.Unmarshal([]byte(result.Data), &content); err != nil {
		return &ExecutionResult{
			ApiResponse:  models.ApiResponse{RequestID: result.RequestID},
			Success:      false,
			ErrorMessage: fmt.Sprintf("Failed to parse response: %v", err),
			TaskStatus:   "failed",
			TaskID:       "",
			TaskResult:   "Invalid execution response.",
		}
	}

	taskID, ok := content["task_id"].(string)
	if !ok {
		// 从后端返回的content中提取error信息
		errorMessage := "Task ID not found in response"
		if errorVal, exists := content["error"]; exists {
			if errorStr, ok := errorVal.(string); ok {
				errorMessage = errorStr
			}
		}
		return &ExecutionResult{
			ApiResponse:  models.ApiResponse{RequestID: result.RequestID},
			Success:      false,
			ErrorMessage: errorMessage,
			TaskStatus:   "failed",
			TaskID:       "",
			TaskResult:   "Invalid task ID.",
		}
	}

	// Poll for task completion
	pollInterval := 3
	maxPollAttempts := timeout / pollInterval
	triedTime := 0
	for triedTime < maxPollAttempts {
		query := b.getTaskStatus(taskID)
		if !query.Success {
			return &ExecutionResult{
				ApiResponse:  models.ApiResponse{RequestID: query.RequestID},
				Success:      false,
				ErrorMessage: query.ErrorMessage,
				TaskStatus:   "failed",
				TaskID:       taskID,
			}
		}

		taskStatus := query.TaskStatus
		switch taskStatus {
		case "finished":
			return &ExecutionResult{
				ApiResponse:  models.ApiResponse{RequestID: query.RequestID},
				Success:      true,
				ErrorMessage: "",
				TaskID:       taskID,
				TaskStatus:   taskStatus,
				TaskResult:   query.TaskProduct,
			}
		case "failed":
			errorMsg := query.ErrorMessage
			if errorMsg == "" {
				errorMsg = "Failed to execute task."
			}
			return &ExecutionResult{
				ApiResponse:  models.ApiResponse{RequestID: query.RequestID},
				Success:      false,
				ErrorMessage: errorMsg,
				TaskID:       taskID,
				TaskStatus:   taskStatus,
			}
		case "unsupported":
			errorMsg := query.ErrorMessage
			if errorMsg == "" {
				errorMsg = "Unsupported task."
			}
			return &ExecutionResult{
				ApiResponse:  models.ApiResponse{RequestID: query.RequestID},
				Success:      false,
				ErrorMessage: errorMsg,
				TaskID:       taskID,
				TaskStatus:   taskStatus,
			}
		}

		b.logInfo(fmt.Sprintf("⏳ Task %s running 🚀: %s.", taskID, query.TaskAction))
		time.Sleep(3 * time.Second)
		triedTime++
	}

	b.logWarn("task execution timeout!")
	terminateResult := b.terminateTask(taskID)
	if terminateResult.Success {
		b.logInfo(fmt.Sprintf("✅ Terminate request sent for task %s after timeout", taskID))
	} else {
		b.logWarn(fmt.Sprintf("Failed to terminate task %s after timeout: %s", taskID, terminateResult.ErrorMessage))
	}

	b.logInfo(fmt.Sprintf("⏳ Waiting for task %s to be fully terminated...", taskID))
	terminatePollInterval := 1
	maxTerminatePollAttempts := 30
	terminateTriedTime := 0
	taskTerminatedConfirmed := false

	for terminateTriedTime < maxTerminatePollAttempts {
		statusQuery := b.getTaskStatus(taskID)
		if !statusQuery.Success {
			errorMsg := statusQuery.ErrorMessage
			if errorMsg != "" && strings.HasPrefix(errorMsg, "Task not found or already finished") {
				b.logInfo(fmt.Sprintf("✅ Task %s confirmed terminated (not found or finished)", taskID))
				taskTerminatedConfirmed = true
				break
			}
		}
		time.Sleep(time.Duration(terminatePollInterval) * time.Second)
		terminateTriedTime++
	}

	if !taskTerminatedConfirmed {
		b.logWarn(fmt.Sprintf("Timeout waiting for task %s to be fully terminated", taskID))
	}

	timeoutErrorMsg := fmt.Sprintf("Task execution timed out after %d seconds. Task ID: %s. Polled %d times (max: %d).", timeout, taskID, triedTime, maxPollAttempts)
	return &ExecutionResult{
		ApiResponse:  models.ApiResponse{RequestID: result.RequestID},
		Success:      false,
		ErrorMessage: timeoutErrorMsg,
		TaskStatus:   "failed",
		TaskID:       taskID,
		TaskResult:   fmt.Sprintf("Task execution timed out after %d seconds.", timeout),
	}
}

// executeTaskStreamWs executes a task via WebSocket streaming channel.
func (b *baseTaskAgent) executeTaskStreamWs(taskParams map[string]interface{}, timeout int, opts StreamOptions) *ExecutionResult {
	wsClientRaw, err := b.Session.GetWsClient()
	if err != nil {
		return &ExecutionResult{
			ApiResponse:  models.ApiResponse{RequestID: ""},
			Success:      false,
			ErrorMessage: err.Error(),
			TaskStatus:   "failed",
			TaskID:       "",
			TaskResult:   "Task Failed",
		}
	}
	wsClient, wsOk := wsClientRaw.(*internal.WsClient)
	if !wsOk || wsClient == nil {
		return &ExecutionResult{
			ApiResponse:  models.ApiResponse{RequestID: ""},
			Success:      false,
			ErrorMessage: "invalid or nil WsClient returned from session",
			TaskStatus:   "failed",
			TaskID:       "",
			TaskResult:   "Task Failed",
		}
	}

	target := b.getWsTarget()
	var contentParts []string
	var lastError map[string]interface{}
	var streamErr error

	handle, err := wsClient.CallStream(
		target,
		map[string]interface{}{
			"method": "exec_task",
			"params": taskParams,
		},
		func(_ string, data map[string]interface{}) {
			eventType, _ := data["eventType"].(string)
			seq, _ := toIntAgent(data["seq"])
			round, _ := toIntAgent(data["round"])

			evt := AgentEvent{Type: eventType, Seq: seq, Round: round}

			switch eventType {
			case "reasoning":
				evt.Content, _ = data["content"].(string)
			case "content":
				contentText, _ := data["content"].(string)
				contentParts = append(contentParts, contentText)
				evt.Content = contentText
			case "tool_call":
				evt.ToolCallID, _ = data["toolCallId"].(string)
				evt.ToolName, _ = data["toolName"].(string)
				if args, ok := data["args"].(map[string]interface{}); ok {
					evt.Args = args
				}
			case "tool_result":
				evt.ToolCallID, _ = data["toolCallId"].(string)
				evt.ToolName, _ = data["toolName"].(string)
				if res, ok := data["result"].(map[string]interface{}); ok {
					evt.Result = res
				}
			case "error":
				if e, ok := data["error"].(map[string]interface{}); ok {
					lastError = e
				} else {
					lastError = data
				}
				evt.Error = lastError
			}

			typedCb := map[string]AgentEventCallback{
				"reasoning":   opts.OnReasoning,
				"content":     opts.OnContent,
				"tool_call":   opts.OnToolCall,
				"tool_result": opts.OnToolResult,
				"error":       opts.OnError,
			}
			if cb, ok := typedCb[eventType]; ok && cb != nil {
				cb(evt)
			}
		},
		func(_ string, _ map[string]interface{}) {},
		func(_ string, e error) {
			streamErr = e
		},
	)
	if err != nil {
		return &ExecutionResult{
			ApiResponse:  models.ApiResponse{RequestID: ""},
			Success:      false,
			ErrorMessage: err.Error(),
			TaskStatus:   "failed",
			TaskID:       "",
			TaskResult:   "Task Failed",
		}
	}

	endData, err := handle.WaitEnd()
	if err != nil {
		return &ExecutionResult{
			ApiResponse:  models.ApiResponse{RequestID: handle.InvocationID},
			Success:      false,
			ErrorMessage: err.Error(),
			TaskStatus:   "failed",
			TaskID:       "",
			TaskResult:   strings.Join(contentParts, ""),
		}
	}

	if streamErr != nil {
		return &ExecutionResult{
			ApiResponse:  models.ApiResponse{RequestID: handle.InvocationID},
			Success:      false,
			ErrorMessage: streamErr.Error(),
			TaskStatus:   "failed",
			TaskID:       "",
			TaskResult:   strings.Join(contentParts, ""),
		}
	}

	if lastError != nil {
		return &ExecutionResult{
			ApiResponse:  models.ApiResponse{RequestID: handle.InvocationID},
			Success:      false,
			ErrorMessage: fmt.Sprintf("%v", lastError),
			TaskStatus:   "failed",
			TaskID:       "",
			TaskResult:   strings.Join(contentParts, ""),
		}
	}

	status, _ := endData["status"].(string)
	if status == "" {
		status = "finished"
	}
	taskResult, _ := endData["taskResult"].(string)
	if taskResult == "" {
		taskResult = strings.Join(contentParts, "")
	}

	return &ExecutionResult{
		ApiResponse: models.ApiResponse{RequestID: handle.InvocationID},
		Success:     status == "finished",
		ErrorMessage: func() string {
			if status == "finished" {
				return ""
			}
			return fmt.Sprintf("Task ended with status: %s", status)
		}(),
		TaskStatus: status,
		TaskResult: taskResult,
	}
}

// startTaskStreamWs sets up a WS streaming connection and returns immediately
// with a TaskExecution handle and a shared streamContext. The WS events are
// dispatched to the provided opts callbacks in the background.
func (b *baseTaskAgent) startTaskStreamWs(taskParams map[string]interface{}, opts MobileTaskOptions) (*TaskExecution, *streamContext, error) {
	wsClientRaw, err := b.Session.GetWsClient()
	if err != nil {
		return nil, nil, fmt.Errorf("failed to get WS client: %w", err)
	}
	wsClient, wsOk := wsClientRaw.(*internal.WsClient)
	if !wsOk || wsClient == nil {
		return nil, nil, fmt.Errorf("invalid or nil WsClient returned from session")
	}

	target := b.getWsTarget()
	ctx := &streamContext{}
	var handleRef *internal.WsStreamHandle

	handle, err := wsClient.CallStream(
		target,
		map[string]interface{}{
			"method": "exec_task",
			"params": taskParams,
		},
		func(_ string, data map[string]interface{}) {
			eventType, _ := data["eventType"].(string)
			seq, _ := toIntAgent(data["seq"])
			round, _ := toIntAgent(data["round"])

			evt := AgentEvent{Type: eventType, Seq: seq, Round: round}

			switch eventType {
			case "reasoning":
				evt.Content, _ = data["content"].(string)
			case "content":
				contentText, _ := data["content"].(string)
				ctx.contentParts = append(ctx.contentParts, contentText)
				evt.Content = contentText
			case "tool_call":
				evt.ToolCallID, _ = data["toolCallId"].(string)
				evt.ToolName, _ = data["toolName"].(string)
				if args, ok := data["args"].(map[string]interface{}); ok {
					evt.Args = args
				}
				if evt.ToolName == "call_for_user" {
					if prompt, ok := evt.Args["prompt"].(string); ok {
						evt.Content = prompt
					}
				}
			case "tool_result":
				evt.ToolCallID, _ = data["toolCallId"].(string)
				evt.ToolName, _ = data["toolName"].(string)
				if res, ok := data["result"].(map[string]interface{}); ok {
					evt.Result = res
				}
			case "error":
				if e, ok := data["error"].(map[string]interface{}); ok {
					ctx.lastError = e
				} else {
					ctx.lastError = data
				}
				evt.Error = ctx.lastError
			}

			typedCb := map[string]AgentEventCallback{
				"reasoning":   opts.OnReasoning,
				"content":     opts.OnContent,
				"tool_call":   opts.OnToolCall,
				"tool_result": opts.OnToolResult,
				"error":       opts.OnError,
			}
			if cb, ok := typedCb[eventType]; ok && cb != nil {
				cb(evt)
			}
			if evt.ToolName == "call_for_user" {
				evtCopy := evt
				go func() {
					response := ""
					if opts.OnCallForUser != nil {
						response = opts.OnCallForUser(evtCopy)
					} else {
						fmt.Println("[WARN] Received call_for_user but no OnCallForUser callback is set, sending empty response")
					}
					for i := 0; i < 100; i++ {
						if handleRef != nil {
							break
						}
						time.Sleep(10 * time.Millisecond)
					}
					if handleRef != nil {
						_ = handleRef.Write(map[string]interface{}{
							"method": "resume_task",
							"params": map[string]interface{}{
								"toolCallId": evtCopy.ToolCallID,
								"response":   response,
							},
						})
					}
				}()
			}
		},
		func(_ string, _ map[string]interface{}) {},
		func(_ string, e error) {
			ctx.streamErr = e
		},
	)
	if err != nil {
		return nil, nil, fmt.Errorf("failed to start WS stream: %w", err)
	}
	handleRef = handle

	execution := &TaskExecution{
		TaskID: "",
		waitFn: func(timeout int) *ExecutionResult {
			var endData map[string]interface{}
			var err error
			if timeout > 0 {
				endData, err = handle.WaitEndWithTimeout(time.Duration(timeout) * time.Second)
			} else {
				endData, err = handle.WaitEnd()
			}
			if err != nil {
				errMsg := err.Error()
				if _, ok := err.(*internal.WsTimeoutError); ok {
					_ = handle.Cancel()
					errMsg = fmt.Sprintf("Task execution timed out after %d seconds.", timeout)
				}
				taskResult := strings.Join(ctx.contentParts, "")
				if taskResult == "" {
					taskResult = errMsg
				}
				return &ExecutionResult{
					ApiResponse:  models.ApiResponse{RequestID: handle.InvocationID},
					Success:      false,
					ErrorMessage: errMsg,
					TaskStatus:   "failed",
					TaskResult:   taskResult,
				}
			}

			if ctx.streamErr != nil {
				return &ExecutionResult{
					ApiResponse:  models.ApiResponse{RequestID: handle.InvocationID},
					Success:      false,
					ErrorMessage: ctx.streamErr.Error(),
					TaskStatus:   "failed",
					TaskResult:   strings.Join(ctx.contentParts, ""),
				}
			}

			if ctx.lastError != nil {
				return &ExecutionResult{
					ApiResponse:  models.ApiResponse{RequestID: handle.InvocationID},
					Success:      false,
					ErrorMessage: fmt.Sprintf("%v", ctx.lastError),
					TaskStatus:   "failed",
					TaskResult:   strings.Join(ctx.contentParts, ""),
				}
			}

			status, _ := endData["status"].(string)
			if status == "" {
				status = "finished"
			}
			taskResult, _ := endData["taskResult"].(string)
			if taskResult == "" {
				taskResult = strings.Join(ctx.contentParts, "")
			}

			return &ExecutionResult{
				ApiResponse: models.ApiResponse{RequestID: handle.InvocationID},
				Success:     status == "finished",
				ErrorMessage: func() string {
					if status == "finished" {
						return ""
					}
					return fmt.Sprintf("Task ended with status: %s", status)
				}(),
				TaskStatus: status,
				TaskResult: taskResult,
			}
		},
	}

	return execution, ctx, nil
}

func toIntAgent(v interface{}) (int, bool) {
	switch t := v.(type) {
	case float64:
		return int(t), true
	case int:
		return t, true
	case int64:
		return int(t), true
	default:
		return 0, false
	}
}

// getTaskStatus gets the status of the task with the given task ID
func (b *baseTaskAgent) getTaskStatus(taskID string) *QueryResult {
	args := map[string]interface{}{
		"task_id": taskID,
	}

	result, err := b.Session.CallMcpTool(b.getToolName("get_status"), args)
	if err != nil {
		return &QueryResult{
			ApiResponse:  models.ApiResponse{RequestID: ""},
			Success:      false,
			ErrorMessage: fmt.Sprintf("Failed to get task status: %v", err),
			TaskID:       taskID,
			TaskStatus:   "failed",
		}
	}

	if !result.Success {
		errorMessage := result.ErrorMessage
		if errorMessage == "" {
			errorMessage = "Failed to get task status"
		}
		return &QueryResult{
			ApiResponse:  models.ApiResponse{RequestID: result.RequestID},
			Success:      false,
			ErrorMessage: errorMessage,
			TaskID:       taskID,
			TaskStatus:   "failed",
		}
	}

	var queryResult map[string]interface{}
	if err := json.Unmarshal([]byte(result.Data), &queryResult); err != nil {
		return &QueryResult{
			ApiResponse:  models.ApiResponse{RequestID: result.RequestID},
			Success:      false,
			ErrorMessage: fmt.Sprintf("Failed to parse response: %v", err),
			TaskID:       taskID,
			TaskStatus:   "failed",
		}
	}

	taskIDFromResult, ok := queryResult["task_id"].(string)
	if !ok {
		taskIDFromResult = taskID
	}

	status, ok := queryResult["status"].(string)
	if !ok {
		status = "finished"
	}

	action, ok := queryResult["action"].(string)
	if !ok {
		action = ""
	}

	product, ok := queryResult["product"].(string)
	if !ok {
		product = ""
	}

	// Extract stream and error fields
	var stream []StreamItem
	if streamValue, ok := queryResult["stream"]; ok {
		if streamArray, ok := streamValue.([]interface{}); ok {
			stream = make([]StreamItem, 0, len(streamArray))
			for _, item := range streamArray {
				if itemMap, ok := item.(map[string]interface{}); ok {
					streamItem := StreamItem{}
					if content, ok := itemMap["content"].(string); ok {
						streamItem.Content = content
					}
					if reasoning, ok := itemMap["reasoning"].(string); ok {
						streamItem.Reasoning = reasoning
					}
					if timestampMs, ok := itemMap["timestamp_ms"].(float64); ok {
						timestampInt := int64(timestampMs)
						streamItem.TimestampMs = &timestampInt
					}
					stream = append(stream, streamItem)
				}
			}
		}
	}

	var errorMsg string
	if errorValue, ok := queryResult["error"].(string); ok {
		errorMsg = errorValue
	}

	return &QueryResult{
		ApiResponse: models.ApiResponse{RequestID: result.RequestID},
		Success:     true,
		TaskID:      taskIDFromResult,
		TaskStatus:  status,
		TaskAction:  action,
		TaskProduct: product,
		Stream:      stream,
		Error:       errorMsg,
	}
}

// terminateTask terminates a task with a specified task ID
func (b *baseTaskAgent) terminateTask(taskID string) *ExecutionResult {
	b.logInfo("Terminating task")

	args := map[string]interface{}{
		"task_id": taskID,
	}

	result, err := b.Session.CallMcpTool(b.getToolName("terminate"), args)
	if err != nil {
		return &ExecutionResult{
			ApiResponse:  models.ApiResponse{RequestID: ""},
			Success:      false,
			ErrorMessage: fmt.Sprintf("Failed to terminate: %v", err),
			TaskID:       taskID,
			TaskStatus:   "failed",
		}
	}

	var content map[string]interface{}
	if result.Data != "" {
		if err := json.Unmarshal([]byte(result.Data), &content); err != nil {
			return &ExecutionResult{
				ApiResponse:  models.ApiResponse{RequestID: result.RequestID},
				Success:      false,
				ErrorMessage: fmt.Sprintf("Failed to parse response: %v", err),
				TaskID:       taskID,
				TaskStatus:   "failed",
			}
		}
	}

	terminatedTaskID := taskID
	if content != nil {
		if tid, ok := content["task_id"].(string); ok {
			terminatedTaskID = tid
		}
	}

	if result.Success {
		status := "finished"
		if content != nil {
			if s, ok := content["status"].(string); ok {
				status = s
			}
		}
		return &ExecutionResult{
			ApiResponse:  models.ApiResponse{RequestID: result.RequestID},
			Success:      true,
			ErrorMessage: "",
			TaskID:       terminatedTaskID,
			TaskStatus:   status,
		}
	}

	// When result.Success is false, still try to parse status from content if available
	status := "failed"
	if content != nil {
		if s, ok := content["status"].(string); ok {
			status = s
		}
	}

	errorMessage := result.ErrorMessage
	if errorMessage == "" {
		errorMessage = "Failed to terminate task"
	}

	return &ExecutionResult{
		ApiResponse:  models.ApiResponse{RequestID: result.RequestID},
		Success:      false,
		ErrorMessage: errorMessage,
		TaskID:       terminatedTaskID,
		TaskStatus:   status,
	}
}

// ComputerUseAgent represents an agent to manipulate a browser to complete specific tasks
//
// > **⚠️ Note**: Currently, for agent services (including ComputerUseAgent, BrowserUseAgent, and MobileUseAgent), we do not provide services for overseas users registered with **alibabacloud.com**.
type ComputerUseAgent struct {
	*baseTaskAgent
}

// BrowserUseAgent represents an agent to manipulate a browser to complete specific tasks
//
// > **⚠️ Note**: Currently, for agent services (including ComputerUseAgent, BrowserUseAgent, and MobileUseAgent), we do not provide services for overseas users registered with **alibabacloud.com**.
type BrowserUseAgent struct {
	*baseTaskAgent
	initialized bool
}

// MobileUseAgent represents an agent to perform tasks on mobile devices
//
// > **⚠️ Note**: Currently, for agent services (including ComputerUseAgent, BrowserUseAgent, and MobileUseAgent), we do not provide services for overseas users registered with **alibabacloud.com**.
type MobileUseAgent struct {
	*baseTaskAgent
}

// Agent represents an agent to manipulate applications to complete specific tasks
//
// > **⚠️ Note**: Currently, for agent services (including ComputerUseAgent, BrowserUseAgent, and MobileUseAgent), we do not provide services for overseas users registered with **alibabacloud.com**.
type Agent struct {
	Browser  *BrowserUseAgent
	Computer *ComputerUseAgent
	Mobile   *MobileUseAgent
}

// McpSession interface defines the methods needed by Agent
type McpSession interface {
	GetAPIKey() string
	GetSessionId() string
	CallMcpTool(toolName string, args interface{}) (*models.McpToolResult, error)
	GetBrowser() *browser.Browser
	GetWsClient() (interface{}, error)
}

// McpSessionLogger is an optional interface for logging. If McpSession implements it,
// the agent will use it for logging instead of fmt.Print.
type McpSessionLogger interface {
	LogDebug(msg string)
	LogInfo(msg string)
	LogWarn(msg string)
	LogError(msg string)
}

func (b *baseTaskAgent) logDebug(msg string) {
	if logger, ok := b.Session.(McpSessionLogger); ok {
		logger.LogDebug(msg)
	}
}

func (b *baseTaskAgent) logInfo(msg string) {
	if logger, ok := b.Session.(McpSessionLogger); ok {
		logger.LogInfo(msg)
	}
}

func (b *baseTaskAgent) logWarn(msg string) {
	if logger, ok := b.Session.(McpSessionLogger); ok {
		logger.LogWarn(msg)
	}
}

func (b *baseTaskAgent) logError(msg string) {
	if logger, ok := b.Session.(McpSessionLogger); ok {
		logger.LogError(msg)
	}
}

func NewBrowserUseAgent(session McpSession) *BrowserUseAgent {
	return &BrowserUseAgent{
		baseTaskAgent: &baseTaskAgent{
			Session:    session,
			ToolPrefix: "browser_use",
		},
		initialized: false,
	}
}

func NewComputerUseAgent(session McpSession) *ComputerUseAgent {
	return &ComputerUseAgent{
		baseTaskAgent: &baseTaskAgent{
			Session:    session,
			ToolPrefix: "flux",
		},
	}
}

func NewMobileUseAgent(session McpSession) *MobileUseAgent {
	return &MobileUseAgent{
		baseTaskAgent: &baseTaskAgent{
			Session:    session,
			ToolPrefix: "",
		},
	}
}

// NewAgent creates a new Agent instance
func NewAgent(session McpSession) *Agent {
	return &Agent{
		Browser:  NewBrowserUseAgent(session),
		Computer: NewComputerUseAgent(session),
		Mobile:   NewMobileUseAgent(session),
	}
}

// ExecuteTask executes a task in human language.
// If timeout is provided, it will wait for task completion (blocking).
// If timeout is not provided, it returns immediately with a task ID (non-blocking).
//
// Non-blocking usage (new style):
//
//	result := sessionResult.Session.Agent.Computer.ExecuteTask("Open Chrome browser")
//	status := sessionResult.Session.Agent.Computer.GetTaskStatus(result.TaskID)
//
// Blocking usage (backward compatible):
//
//	result := sessionResult.Session.Agent.Computer.ExecuteTask("Open Chrome browser", 20)
func (a *ComputerUseAgent) ExecuteTask(task string, timeout ...int) *ExecutionResult {
	if len(timeout) > 0 {
		// Backward compatible: blocking version
		return a.baseTaskAgent.executeTaskAndWait(task, timeout[0])
	}
	// New non-blocking version
	return a.baseTaskAgent.executeTask(task)
}

// ExecuteTaskAndWait executes a specific task described in human language synchronously.
// This is a synchronous interface that blocks until the task is completed or
// an error occurs, or timeout happens. The default polling interval is 3 seconds.
//
// Example:
//
//	client, _ := agentbay.NewAgentBay(os.Getenv("AGENTBAY_API_KEY"), nil)
//	sessionResult, _ := client.Create(agentbay.NewCreateSessionParams().WithImageId("windows_latest"))
//	defer sessionResult.Session.Delete()
//	result := sessionResult.Session.Agent.Computer.ExecuteTaskAndWait("Open Chrome browser", 60)
func (a *ComputerUseAgent) ExecuteTaskAndWait(task string, timeout int) *ExecutionResult {
	return a.baseTaskAgent.executeTaskAndWait(task, timeout)
}

// GetTaskStatus gets the status of the task with the given task ID
//
// Example:
//
//	client, _ := agentbay.NewAgentBay(os.Getenv("AGENTBAY_API_KEY"), nil)
//	sessionResult, _ := client.Create(agentbay.NewCreateSessionParams().WithImageId("windows_latest"))
//	defer sessionResult.Session.Delete()
//	execResult := sessionResult.Session.Agent.Computer.ExecuteTask("Find weather in NYC", 10)
//	statusResult := sessionResult.Session.Agent.Computer.GetTaskStatus(execResult.TaskID)
func (a *ComputerUseAgent) GetTaskStatus(taskID string) *QueryResult {
	return a.baseTaskAgent.getTaskStatus(taskID)
}

// TerminateTask terminates a task with a specified task ID
//
// Example:
//
//	client, _ := agentbay.NewAgentBay(os.Getenv("AGENTBAY_API_KEY"), nil)
//	sessionResult, _ := client.Create(agentbay.NewCreateSessionParams().WithImageId("windows_latest"))
//	defer sessionResult.Session.Delete()
//	execResult := sessionResult.Session.Agent.Computer.ExecuteTask("Find weather in NYC", 10)
//	terminateResult := sessionResult.Session.Agent.Computer.TerminateTask(execResult.TaskID)
func (a *ComputerUseAgent) TerminateTask(taskID string) *ExecutionResult {
	return a.baseTaskAgent.terminateTask(taskID)
}

/**
* Initialize the browser on which the agent performs tasks.
* You are supposed to call this API before executeTask is called, but is't optional.
* @param option Browser option
* @return True if the browser is successfully initialized, False otherwise.
 */
func (a *BrowserUseAgent) Initialize(option *browser.BrowserOption) (bool, error) {
	if a.initialized {
		return true, nil
	}

	success, err := a.Session.GetBrowser().Initialize(option)
	if err != nil {
		return false, err
	}

	if success {
		a.initialized = true
	}

	return success, nil
}

/*
Execute a task described in human language on a browser without waiting for completion (non-blocking).

This is a fire-and-return interface that immediately provides a task ID.
Call get_task_status to check the task status. You can control the timeout
of the task execution in your own code by setting the frequency of calling
get_task_status.

Args:
task: Task description in human language.
use_vision: Whether to use vision to performe the task.
output_schema: The schema of the structured output.

Returns:
ExecutionResult: Result object containing success status, task ID,

	task status, and error message if any.

Example:
```typescript
client, err := agentbay.NewAgentBay(apiKey)

	if err != nil {
		fmt.Printf("Error initializing AgentBay client: %v\n", err)
		return
	}

sessionParams := agentbay.NewCreateSessionParams().WithImageId("windows_latest")
sessionResult, err := client.Create(sessionParams)

	if err != nil {
		fmt.Printf("Error creating session: %v\n", err)
		return
	}

session := sessionResult.Session

	type OutputSchema struct {
		City string `json:"City" jsonschema:"required"`
		Weather string `json:"Weather" jsonschema:"required"`
	}

result = await session.Agent.Browser.ExecuteTask(task="Query the weather in Shanghai",false, &OutputSchema{})
fmt.Printf(

	f"Task ID: {result.task_id}, Status: {result.task_status}")

status = await session.Agent.Browser.GetTaskStatus(result.task_id)
fmt.Printf(f"Task status: {status.task_status}")
await session.delete()
```
*/
func (a *BrowserUseAgent) ExecuteTask(task string, use_vision bool, output_schema interface{}) *ExecutionResult {
	if a.initialized == false {
		a.logInfo("Browser is not initialized yet, initializing now")
		success, err := a.Initialize(&browser.BrowserOption{})
		if err != nil || !success {
			a.logError(fmt.Sprintf("BrowserInitializationFailed: %v", err))
			return &ExecutionResult{
				ApiResponse:  models.ApiResponse{RequestID: ""},
				Success:      false,
				ErrorMessage: "BrowserInitializationFailed",
				TaskStatus:   "failed",
				TaskID:       "",
			}
		}
	}
	args := map[string]interface{}{
		"task":          task,
		"use_vision":    use_vision,
		"output_schema": generateJsonSchema(output_schema),
	}
	a.logDebug(fmt.Sprintf("%v", args))
	result, err := a.Session.CallMcpTool(a.getToolName("execute"), args)
	if err != nil {
		return &ExecutionResult{
			ApiResponse:  models.ApiResponse{RequestID: ""},
			Success:      false,
			ErrorMessage: fmt.Sprintf("Failed to execute: %v", err),
			TaskStatus:   "failed",
			TaskID:       "",
		}
	}

	if !result.Success {
		errorMessage := result.ErrorMessage
		if errorMessage == "" {
			errorMessage = "Failed to execute task"
		}
		return &ExecutionResult{
			ApiResponse:  models.ApiResponse{RequestID: result.RequestID},
			Success:      false,
			ErrorMessage: errorMessage,
			TaskStatus:   "failed",
			TaskID:       "",
		}
	}

	// Parse task ID from response
	var content map[string]interface{}
	if err := json.Unmarshal([]byte(result.Data), &content); err != nil {
		return &ExecutionResult{
			ApiResponse:  models.ApiResponse{RequestID: result.RequestID},
			Success:      false,
			ErrorMessage: fmt.Sprintf("Failed to parse response: %v", err),
			TaskStatus:   "failed",
			TaskID:       "",
		}
	}

	taskID, ok := content["task_id"].(string)
	if !ok {
		return &ExecutionResult{
			ApiResponse:  models.ApiResponse{RequestID: result.RequestID},
			Success:      false,
			ErrorMessage: "Task ID not found in response",
			TaskStatus:   "failed",
			TaskID:       "",
		}
	}

	return &ExecutionResult{
		ApiResponse: models.ApiResponse{RequestID: result.RequestID},
		Success:     true,
		TaskID:      taskID,
		TaskStatus:  "running",
	}
}

/*
Execute a task described in human language on a browser synchronously.

This is a synchronous interface that blocks until the task is completed or
an error occurs, or timeout happens. The default polling interval is 3 seconds.

Args:

	task: Task description in human language.
	timeout: Maximum time to wait for task completion in seconds.
		Used to control how long to wait for task completion.
	use_vision: Whether to use vision to performe the task.
	output_schema: The schema of the structured output.

Returns:

	ExecutionResult: Result object containing success status, task ID,
		task status, and error message if any.

Example:
```typescript
client, err := agentbay.NewAgentBay(apiKey)

	if err != nil {
		fmt.Printf("Error initializing AgentBay client: %v\n", err)
		return
	}

sessionParams := agentbay.NewCreateSessionParams().WithImageId("windows_latest")
sessionResult, err := client.Create(sessionParams)

	if err != nil {
		fmt.Printf("Error creating session: %v\n", err)
		return
	}

session := sessionResult.Session

	type OutputSchema struct {
		City string `json:"City" jsonschema:"required"`
		Weather string `json:"Weather" jsonschema:"required"`
	}

result = await session.Agent.Browser.ExecuteTaskAndWait(task="Query the weather in Shanghai",180, false, &OutputSchema{})
fmt.Printf("Task status: %s\n", executionResult.TaskStatus)
```
*/
func (a *BrowserUseAgent) ExecuteTaskAndWait(task string, timeout int, use_vision bool, output_schema interface{}) *ExecutionResult {
	result := a.ExecuteTask(task, use_vision, output_schema)
	if !result.Success {
		errorMessage := result.ErrorMessage
		if errorMessage == "" {
			errorMessage = "Failed to execute task"
		}
		return &ExecutionResult{
			ApiResponse:  models.ApiResponse{RequestID: result.RequestID},
			Success:      false,
			ErrorMessage: errorMessage,
			TaskStatus:   "failed",
			TaskID:       "",
			TaskResult:   "Task Failed",
		}
	}
	taskID := result.TaskID
	if taskID == "" {
		return &ExecutionResult{
			ApiResponse:  models.ApiResponse{RequestID: result.RequestID},
			Success:      false,
			ErrorMessage: "Task ID not found in response",
			TaskStatus:   "failed",
			TaskID:       "",
			TaskResult:   "Invalid task ID.",
		}
	}

	// Poll for task completion
	pollInterval := 3
	maxPollAttempts := timeout / pollInterval
	triedTime := 0
	for triedTime < maxPollAttempts {
		query := a.getTaskStatus(result.TaskID)
		if !query.Success {
			return &ExecutionResult{
				ApiResponse:  models.ApiResponse{RequestID: query.RequestID},
				Success:      false,
				ErrorMessage: query.ErrorMessage,
				TaskStatus:   "failed",
				TaskID:       taskID,
			}
		}

		taskStatus := query.TaskStatus
		switch taskStatus {
		case "finished":
			return &ExecutionResult{
				ApiResponse:  models.ApiResponse{RequestID: query.RequestID},
				Success:      true,
				ErrorMessage: "",
				TaskID:       taskID,
				TaskStatus:   taskStatus,
				TaskResult:   query.TaskProduct,
			}
		case "failed":
			errorMsg := query.ErrorMessage
			if errorMsg == "" {
				errorMsg = "Failed to execute task."
			}
			return &ExecutionResult{
				ApiResponse:  models.ApiResponse{RequestID: query.RequestID},
				Success:      false,
				ErrorMessage: errorMsg,
				TaskID:       taskID,
				TaskStatus:   taskStatus,
			}
		case "unsupported":
			errorMsg := query.ErrorMessage
			if errorMsg == "" {
				errorMsg = "Unsupported task."
			}
			return &ExecutionResult{
				ApiResponse:  models.ApiResponse{RequestID: query.RequestID},
				Success:      false,
				ErrorMessage: errorMsg,
				TaskID:       taskID,
				TaskStatus:   taskStatus,
			}
		}

		a.logInfo(fmt.Sprintf("⏳ Task %s running 🚀: %s.", taskID, query.TaskAction))
		time.Sleep(3 * time.Second)
		triedTime++
	}

	a.logWarn("task execution timeout!")
	// Automatically terminate the task on timeout
	terminateResult := a.terminateTask(taskID)
	if terminateResult.Success {
		a.logInfo(fmt.Sprintf("✅ Task %s terminated successfully after timeout", taskID))
	} else {
		a.logWarn(fmt.Sprintf("Failed to terminate task %s after timeout: %s", taskID, terminateResult.ErrorMessage))
	}
	timeoutErrorMsg := fmt.Sprintf("Task execution timed out after %d seconds. Task ID: %s. Polled %d times (max: %d).", timeout, taskID, triedTime, maxPollAttempts)
	return &ExecutionResult{
		ApiResponse:  models.ApiResponse{RequestID: result.RequestID},
		Success:      false,
		ErrorMessage: timeoutErrorMsg,
		TaskStatus:   "failed",
		TaskID:       taskID,
		TaskResult:   fmt.Sprintf("Task execution timed out after %d seconds.", timeout),
	}
}

// GetTaskStatus gets the status of the task with the given task ID
//
// Example:
//
//	client, _ := agentbay.NewAgentBay(os.Getenv("AGENTBAY_API_KEY"), nil)
//	sessionResult, _ := client.Create(agentbay.NewCreateSessionParams().WithImageId("windows_latest"))
//	defer sessionResult.Session.Delete()
//	execResult := sessionResult.Session.Agent.Browser.ExecuteTask("Find weather in NYC", 10)
//	statusResult := sessionResult.Session.Agent.Browser.GetTaskStatus(execResult.TaskID)
func (a *BrowserUseAgent) GetTaskStatus(taskID string) *QueryResult {
	return a.baseTaskAgent.getTaskStatus(taskID)
}

// TerminateTask terminates a task with a specified task ID
//
// Example:
//
//	client, _ := agentbay.NewAgentBay(os.Getenv("AGENTBAY_API_KEY"), nil)
//	sessionResult, _ := client.Create(agentbay.NewCreateSessionParams().WithImageId("windows_latest"))
//	defer sessionResult.Session.Delete()
//	execResult := sessionResult.Session.Agent.Browser.ExecuteTask("Find weather in NYC", 10)
//	terminateResult := sessionResult.Session.Agent.Browser.TerminateTask(execResult.TaskID)
func (a *BrowserUseAgent) TerminateTask(taskID string) *ExecutionResult {
	return a.baseTaskAgent.terminateTask(taskID)
}

// ExecuteTask starts a mobile task and returns a TaskExecution handle immediately (non-blocking).
// Use TaskExecution.Wait(timeout) to block until the task completes.
//
// When streaming callbacks are provided in MobileTaskOptions, real-time events
// are delivered via WebSocket. Otherwise the task is started via MCP and the
// handle supports polling-based Wait().
//
// Example (non-blocking):
//
//	execution := session.Agent.Mobile.ExecuteTask("Open WeChat app")
//	result := execution.Wait(180)
//
// Example (with streaming):
//
//	execution := session.Agent.Mobile.ExecuteTask("Open Settings", agent.MobileTaskOptions{
//	    MaxSteps: 50,
//	    StreamOptions: agent.StreamOptions{
//	        OnReasoning: func(e agent.AgentEvent) { fmt.Println(e.Content) },
//	    },
//	})
//	result := execution.Wait(180)
func (a *MobileUseAgent) ExecuteTask(task string, opts ...MobileTaskOptions) *TaskExecution {
	var options MobileTaskOptions
	if len(opts) > 0 {
		options = opts[0]
	}
	maxSteps := options.MaxSteps
	if maxSteps <= 0 {
		maxSteps = 50
	}

	hasCallbacks := options.OnReasoning != nil || options.OnContent != nil ||
		options.OnToolCall != nil || options.OnToolResult != nil ||
		options.OnError != nil || options.OnCallForUser != nil

	if hasCallbacks {
		taskParams := map[string]interface{}{
			"task":      task,
			"max_steps": maxSteps,
		}
		execution, _, err := a.baseTaskAgent.startTaskStreamWs(taskParams, options)
		if err != nil {
			return &TaskExecution{
				TaskID: "",
				waitFn: func(_ int) *ExecutionResult {
					return &ExecutionResult{
						Success:      false,
						ErrorMessage: err.Error(),
						TaskStatus:   "failed",
						TaskResult:   "Task Failed",
					}
				},
			}
		}
		return execution
	}

	args := map[string]interface{}{
		"task":      task,
		"max_steps": maxSteps,
	}

	result, err := a.baseTaskAgent.Session.CallMcpTool(
		a.baseTaskAgent.getToolName("execute"), args)
	if err != nil {
		return &TaskExecution{
			TaskID: "",
			waitFn: func(_ int) *ExecutionResult {
				return &ExecutionResult{
					ApiResponse:  models.ApiResponse{RequestID: ""},
					Success:      false,
					ErrorMessage: fmt.Sprintf("Failed to execute: %v", err),
					TaskStatus:   "failed",
					TaskResult:   "Task Failed",
				}
			},
		}
	}

	if !result.Success {
		errorMessage := result.ErrorMessage
		if errorMessage == "" {
			errorMessage = "Failed to execute task"
		}
		reqID := result.RequestID
		return &TaskExecution{
			TaskID: "",
			waitFn: func(_ int) *ExecutionResult {
				return &ExecutionResult{
					ApiResponse:  models.ApiResponse{RequestID: reqID},
					Success:      false,
					ErrorMessage: errorMessage,
					TaskStatus:   "failed",
					TaskResult:   "Task Failed",
				}
			},
		}
	}

	var content map[string]interface{}
	if err := json.Unmarshal([]byte(result.Data), &content); err != nil {
		// Backend executed the task synchronously and returned
		// the result as plain text instead of JSON with taskId.
		reqID := result.RequestID
		data := result.Data
		return &TaskExecution{
			TaskID: "",
			waitFn: func(_ int) *ExecutionResult {
				return &ExecutionResult{
					ApiResponse:  models.ApiResponse{RequestID: reqID},
					Success:      true,
					TaskStatus:   "completed",
					TaskResult:   data,
				}
			},
		}
	}

	taskID, ok := content["taskId"].(string)
	if !ok {
		taskID, ok = content["task_id"].(string)
	}
	if !ok {
		// No taskId means the backend completed the task synchronously.
		reqID := result.RequestID
		data := result.Data
		return &TaskExecution{
			TaskID: "",
			waitFn: func(_ int) *ExecutionResult {
				return &ExecutionResult{
					ApiResponse:  models.ApiResponse{RequestID: reqID},
					Success:      true,
					TaskStatus:   "completed",
					TaskResult:   data,
				}
			},
		}
	}

	return &TaskExecution{
		TaskID: taskID,
		waitFn: a.buildPollingWait(taskID, result.RequestID),
	}
}

// buildPollingWait returns a wait function that polls GetTaskStatus until
// the task finishes, fails, or the timeout is reached.
func (a *MobileUseAgent) buildPollingWait(taskID string, initialRequestID string) func(timeout int) *ExecutionResult {
	return func(timeout int) *ExecutionResult {
		pollInterval := 3
		maxPollAttempts := timeout / pollInterval
		triedTime := 0
		processedTimestamps := make(map[int64]bool)
		var lastQuery *QueryResult
		for triedTime < maxPollAttempts {
			query := a.GetTaskStatus(taskID)
			if !query.Success {
				return &ExecutionResult{
					ApiResponse:  models.ApiResponse{RequestID: query.RequestID},
					Success:      false,
					ErrorMessage: query.ErrorMessage,
					TaskStatus:   "failed",
					TaskID:       taskID,
				}
			}

			if len(query.Stream) > 0 {
				lastQuery = query
			}

			if len(query.Stream) > 0 {
				for _, streamItem := range query.Stream {
					if streamItem.TimestampMs != nil {
						timestamp := *streamItem.TimestampMs
						if !processedTimestamps[timestamp] {
							processedTimestamps[timestamp] = true
							if streamItem.Content != "" {
								fmt.Print(streamItem.Content)
							}
						}
					}
				}
			}

			taskStatus := query.TaskStatus
			switch taskStatus {
			case "completed":
				return &ExecutionResult{
					ApiResponse:  models.ApiResponse{RequestID: query.RequestID},
					Success:     true,
					ErrorMessage: "",
					TaskID:      taskID,
					TaskStatus:  taskStatus,
					TaskResult:  query.TaskProduct,
				}
			case "failed":
				errorMsg := query.Error
				if errorMsg == "" {
					errorMsg = query.ErrorMessage
				}
				if errorMsg == "" {
					errorMsg = "Failed to execute task."
				}
				return &ExecutionResult{
					ApiResponse:  models.ApiResponse{RequestID: query.RequestID},
					Success:     false,
					ErrorMessage: errorMsg,
					TaskID:      taskID,
					TaskStatus:  taskStatus,
				}
			case "cancelled":
				errorMsg := query.Error
				if errorMsg == "" {
					errorMsg = query.ErrorMessage
				}
				if errorMsg == "" {
					errorMsg = "Task was cancelled."
				}
				return &ExecutionResult{
					ApiResponse:  models.ApiResponse{RequestID: query.RequestID},
					Success:     false,
					ErrorMessage: errorMsg,
					TaskID:      taskID,
					TaskStatus:  taskStatus,
				}
			case "unsupported":
				errorMsg := query.Error
				if errorMsg == "" {
					errorMsg = query.ErrorMessage
				}
				if errorMsg == "" {
					errorMsg = "Unsupported task."
				}
				return &ExecutionResult{
					ApiResponse:  models.ApiResponse{RequestID: query.RequestID},
					Success:     false,
					ErrorMessage: errorMsg,
					TaskID:      taskID,
					TaskStatus:  taskStatus,
				}
			}

			a.logInfo(fmt.Sprintf("⏳ Task %s running 🚀: %s.", taskID, query.TaskAction))
			time.Sleep(3 * time.Second)
			triedTime++
		}

		a.logWarn("task execution timeout!")
		terminateResult := a.TerminateTask(taskID)
		if terminateResult.Success {
			a.logInfo(fmt.Sprintf("✅ Terminate request sent for task %s after timeout", taskID))
		} else {
			a.logWarn(fmt.Sprintf("Failed to terminate task %s after timeout: %s", taskID, terminateResult.ErrorMessage))
		}

		a.logInfo(fmt.Sprintf("⏳ Waiting for task %s to be fully terminated...", taskID))
		terminatePollInterval := 1
		maxTerminatePollAttempts := 30
		terminateTriedTime := 0
		taskTerminatedConfirmed := false

		for terminateTriedTime < maxTerminatePollAttempts {
			statusQuery := a.GetTaskStatus(taskID)
			if !statusQuery.Success {
				errorMsg := statusQuery.ErrorMessage
				if errorMsg != "" && strings.HasPrefix(errorMsg, "Task not found or already finished") {
					a.logInfo(fmt.Sprintf("✅ Task %s confirmed terminated (not found or finished)", taskID))
					taskTerminatedConfirmed = true
					break
				}
			}
			time.Sleep(time.Duration(terminatePollInterval) * time.Second)
			terminateTriedTime++
		}

		if !taskTerminatedConfirmed {
			a.logWarn(fmt.Sprintf("Timeout waiting for task %s to be fully terminated", taskID))
		}

		timeoutErrorMsg := fmt.Sprintf("Task execution timed out after %d seconds. Task ID: %s. Polled %d times (max: %d).", timeout, taskID, triedTime, maxPollAttempts)

		taskResultParts := []string{fmt.Sprintf("Task execution timed out after %d seconds.", timeout)}

		if lastQuery != nil {
			if len(lastQuery.Stream) > 0 {
				var streamContentParts []string
				for _, streamItem := range lastQuery.Stream {
					if streamItem.Content != "" {
						streamContentParts = append(streamContentParts, streamItem.Content)
					}
				}
				if len(streamContentParts) > 0 {
					streamContent := strings.Join(streamContentParts, "")
					taskResultParts = append(taskResultParts, fmt.Sprintf("Last task status output: %s", streamContent))
				}
			}
			if lastQuery.TaskAction != "" {
				taskResultParts = append(taskResultParts, fmt.Sprintf("Last action: %s", lastQuery.TaskAction))
			}
			if lastQuery.TaskProduct != "" {
				taskResultParts = append(taskResultParts, fmt.Sprintf("Last result: %s", lastQuery.TaskProduct))
			}
			if lastQuery.Error != "" {
				taskResultParts = append(taskResultParts, fmt.Sprintf("Last error: %s", lastQuery.Error))
			}
			if lastQuery.TaskStatus != "" {
				taskResultParts = append(taskResultParts, fmt.Sprintf("Last status: %s", lastQuery.TaskStatus))
			}
		}

		taskResult := strings.Join(taskResultParts, " | ")

		return &ExecutionResult{
			ApiResponse:  models.ApiResponse{RequestID: initialRequestID},
			Success:      false,
			ErrorMessage: timeoutErrorMsg,
			TaskStatus:   "failed",
			TaskID:       taskID,
			TaskResult:   taskResult,
		}
	}
}

// ExecuteTaskAndWait is a convenience wrapper that starts a task via ExecuteTask
// and immediately blocks until it completes or times out.
//
// Example (simple):
//
//	result := session.Agent.Mobile.ExecuteTaskAndWait("Open WeChat app", 180)
//
// Example (with streaming):
//
//	result := session.Agent.Mobile.ExecuteTaskAndWait("Open Settings", 180, agent.MobileTaskOptions{
//	    MaxSteps: 50,
//	    StreamOptions: agent.StreamOptions{
//	        OnReasoning: func(e agent.AgentEvent) { fmt.Println(e.Content) },
//	    },
//	})
func (a *MobileUseAgent) ExecuteTaskAndWait(task string, timeout int, opts ...MobileTaskOptions) *ExecutionResult {
	execution := a.ExecuteTask(task, opts...)
	return execution.Wait(timeout)
}

// GetTaskStatus gets the status of the task with the given task ID
//
// Example:
//
//	statusResult := sessionResult.Session.Agent.Mobile.GetTaskStatus(execResult.TaskID)
func (a *MobileUseAgent) GetTaskStatus(taskID string) *QueryResult {
	args := map[string]interface{}{
		"task_id": taskID,
	}

	result, err := a.baseTaskAgent.Session.CallMcpTool(a.baseTaskAgent.getToolName("get_status"), args)
	if err != nil {
		return &QueryResult{
			ApiResponse:  models.ApiResponse{RequestID: ""},
			Success:      false,
			ErrorMessage: fmt.Sprintf("Failed to get task status: %v", err),
			TaskID:       taskID,
			TaskStatus:   "failed",
		}
	}

	if !result.Success {
		errorMessage := result.ErrorMessage
		if errorMessage == "" {
			errorMessage = "Failed to get task status"
		}
		return &QueryResult{
			ApiResponse:  models.ApiResponse{RequestID: result.RequestID},
			Success:      false,
			ErrorMessage: errorMessage,
			TaskID:       taskID,
			TaskStatus:   "failed",
		}
	}

	var queryResult map[string]interface{}
	if err := json.Unmarshal([]byte(result.Data), &queryResult); err != nil {
		return &QueryResult{
			ApiResponse:  models.ApiResponse{RequestID: result.RequestID},
			Success:      false,
			ErrorMessage: fmt.Sprintf("Failed to parse response: %v", err),
			TaskID:       taskID,
			TaskStatus:   "failed",
		}
	}

	taskIDFromResult, ok := queryResult["taskId"].(string)
	if !ok {
		taskIDFromResult, ok = queryResult["task_id"].(string)
	}
	if !ok {
		taskIDFromResult = taskID
	}

	status, ok := queryResult["status"].(string)
	if !ok {
		status = "completed"
	}

	action, ok := queryResult["action"].(string)
	if !ok {
		action = ""
	}

	var product string
	if resultValue, ok := queryResult["result"].(string); ok && resultValue != "" {
		product = resultValue
	} else if productValue, ok := queryResult["product"].(string); ok {
		product = productValue
	} else {
		product = ""
	}

	var stream []StreamItem
	if streamValue, ok := queryResult["stream"]; ok {
		if streamArray, ok := streamValue.([]interface{}); ok {
			stream = make([]StreamItem, 0, len(streamArray))
			for _, item := range streamArray {
				if itemMap, ok := item.(map[string]interface{}); ok {
					streamItem := StreamItem{}
					if content, ok := itemMap["content"].(string); ok {
						streamItem.Content = content
					}
					if reasoning, ok := itemMap["reasoning"].(string); ok {
						streamItem.Reasoning = reasoning
					}
					if timestampMs, ok := itemMap["timestamp_ms"].(float64); ok {
						timestampInt := int64(timestampMs)
						streamItem.TimestampMs = &timestampInt
					}
					stream = append(stream, streamItem)
				}
			}
		}
	}

	var errorStr string
	if errorValue, ok := queryResult["error"].(string); ok {
		errorStr = errorValue
	}

	return &QueryResult{
		ApiResponse:  models.ApiResponse{RequestID: result.RequestID},
		Success:      true,
		ErrorMessage: "",
		TaskID:       taskIDFromResult,
		TaskStatus:   status,
		TaskAction:   action,
		TaskProduct:  product,
		Stream:       stream,
		Error:        errorStr,
	}
}

// TerminateTask terminates a task with a specified task ID
//
// Example:
//
//	terminateResult := sessionResult.Session.Agent.Mobile.TerminateTask(execResult.TaskID)
func (a *MobileUseAgent) TerminateTask(taskID string) *ExecutionResult {
	a.logInfo("Terminating task")
	args := map[string]interface{}{
		"task_id": taskID,
	}

	result, err := a.baseTaskAgent.Session.CallMcpTool(a.baseTaskAgent.getToolName("terminate"), args)
	if err != nil {
		return &ExecutionResult{
			ApiResponse:  models.ApiResponse{RequestID: ""},
			Success:      false,
			ErrorMessage: fmt.Sprintf("Failed to terminate: %v", err),
			TaskID:       taskID,
			TaskStatus:   "failed",
		}
	}

	var content map[string]interface{}
	if result.Data != "" {
		json.Unmarshal([]byte(result.Data), &content)
	}

	terminatedTaskID := taskID
	if content != nil {
		if tid, ok := content["taskId"].(string); ok {
			terminatedTaskID = tid
		} else if tid, ok := content["task_id"].(string); ok {
			terminatedTaskID = tid
		}
	}

	if result.Success {
		status := "cancelling"
		if content != nil {
			if s, ok := content["status"].(string); ok {
				status = s
			}
		}
		return &ExecutionResult{
			ApiResponse:  models.ApiResponse{RequestID: result.RequestID},
			Success:      true,
			ErrorMessage: "",
			TaskID:       terminatedTaskID,
			TaskStatus:   status,
		}
	}

	status := "failed"
	if content != nil {
		if s, ok := content["status"].(string); ok {
			status = s
		}
	}

	errorMessage := result.ErrorMessage
	if errorMessage == "" {
		errorMessage = "Failed to terminate task"
	}

	return &ExecutionResult{
		ApiResponse:  models.ApiResponse{RequestID: result.RequestID},
		Success:      false,
		ErrorMessage: errorMessage,
		TaskID:       terminatedTaskID,
		TaskStatus:   status,
	}
}
