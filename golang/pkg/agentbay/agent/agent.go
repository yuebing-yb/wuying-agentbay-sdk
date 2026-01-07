package agent

import (
	"encoding/json"
	"fmt"
	"strings"
	"time"

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

		fmt.Printf("⏳ Task %s running 🚀: %s.\n", taskID, query.TaskAction)
		time.Sleep(3 * time.Second)
		triedTime++
	}

	fmt.Println("⚠️ task execution timeout!")
	terminateResult := b.terminateTask(taskID)
	if terminateResult.Success {
		fmt.Printf("✅ Terminate request sent for task %s after timeout\n", taskID)
	} else {
		fmt.Printf("⚠️ Failed to terminate task %s after timeout: %s\n", taskID, terminateResult.ErrorMessage)
	}

	fmt.Printf("⏳ Waiting for task %s to be fully terminated...\n", taskID)
	terminatePollInterval := 1
	maxTerminatePollAttempts := 30
	terminateTriedTime := 0
	taskTerminatedConfirmed := false

	for terminateTriedTime < maxTerminatePollAttempts {
		statusQuery := b.getTaskStatus(taskID)
		if !statusQuery.Success {
			errorMsg := statusQuery.ErrorMessage
			if errorMsg != "" && strings.HasPrefix(errorMsg, "Task not found or already finished") {
				fmt.Printf("✅ Task %s confirmed terminated (not found or finished)\n", taskID)
				taskTerminatedConfirmed = true
				break
			}
		}
		time.Sleep(time.Duration(terminatePollInterval) * time.Second)
		terminateTriedTime++
	}

	if !taskTerminatedConfirmed {
		fmt.Printf("⚠️ Timeout waiting for task %s to be fully terminated\n", taskID)
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
		status = "finised"
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
	fmt.Println("Terminating task")

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
		status := "finised"
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
	CallMcpTool(toolName string, args interface{}, autoGenSession ...bool) (*models.McpToolResult, error)
}

func NewBrowserUseAgent(session McpSession) *BrowserUseAgent {
	return &BrowserUseAgent{
		baseTaskAgent: &baseTaskAgent{
			Session:    session,
			ToolPrefix: "browser_use",
		},
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
	args := map[string]interface{}{
		"task": task,
		"use_vision": use_vision,
		"output_schema": generateJsonSchema(output_schema),
	}
	fmt.Println(args)
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

		fmt.Printf("⏳ Task %s running 🚀: %s.\n", taskID, query.TaskAction)
		time.Sleep(3 * time.Second)
		triedTime++
	}

	fmt.Println("⚠️ task execution timeout!")
	// Automatically terminate the task on timeout
	terminateResult := a.terminateTask(taskID)
	if terminateResult.Success {
		fmt.Printf("✅ Task %s terminated successfully after timeout\n", taskID)
	} else {
		fmt.Printf("⚠️ Failed to terminate task %s after timeout: %s\n", taskID, terminateResult.ErrorMessage)
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

// ExecuteTask executes a task in human language without waiting for completion
// (non-blocking). This is a fire-and-return interface that immediately provides
// a task ID. Call GetTaskStatus to check the task status.
//
// Example:
//
//	result := sessionResult.Session.Agent.Mobile.ExecuteTask("Open WeChat app", 100)
//	status := sessionResult.Session.Agent.Mobile.GetTaskStatus(result.TaskID)
func (a *MobileUseAgent) ExecuteTask(task string, maxSteps int) *ExecutionResult {
	args := map[string]interface{}{
		"task":      task,
		"max_steps": maxSteps,
	}

	result, err := a.baseTaskAgent.Session.CallMcpTool(
		a.baseTaskAgent.getToolName("execute"), args)
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

	taskID, ok := content["taskId"].(string)
	if !ok {
		taskID, ok = content["task_id"].(string)
	}
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
		}
	}

	return &ExecutionResult{
		ApiResponse: models.ApiResponse{RequestID: result.RequestID},
		Success:     true,
		TaskID:      taskID,
		TaskStatus:  "running",
	}
}

// ExecuteTaskAndWait executes a specific task described in human language
// synchronously. This is a synchronous interface that blocks until the task
// is completed or an error occurs, or timeout happens. The default polling
// interval is 3 seconds.
//
// Example:
//
//	result := sessionResult.Session.Agent.Mobile.ExecuteTaskAndWait("Open WeChat app", 100, 180)
func (a *MobileUseAgent) ExecuteTaskAndWait(task string, maxSteps int, timeout int) *ExecutionResult {
	args := map[string]interface{}{
		"task":      task,
		"max_steps": maxSteps,
	}

	result, err := a.baseTaskAgent.Session.CallMcpTool(
		a.baseTaskAgent.getToolName("execute"), args)
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

	var ok bool
	taskID, ok := content["taskId"].(string)
	if !ok {
		taskID, ok = content["task_id"].(string)
	}
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
			TaskResult:   "Invalid task ID.",
		}
	}

	pollInterval := 3
	maxPollAttempts := timeout / pollInterval
	triedTime := 0
	processedTimestamps := make(map[int64]bool) // Track processed stream fragments by timestamp_ms
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

		// Process new stream fragments for real-time output
		if len(query.Stream) > 0 {
			for _, streamItem := range query.Stream {
				if streamItem.TimestampMs != nil {
					timestamp := *streamItem.TimestampMs
					// Use timestamp_ms to identify new fragments (handles backend returning snapshots)
					if !processedTimestamps[timestamp] {
						processedTimestamps[timestamp] = true // Mark as processed immediately

						// Output immediately for true streaming effect
						if streamItem.Content != "" {
							// Use fmt.Print for streaming output without automatic newlines
							fmt.Print(streamItem.Content)
						}
						// Note: reasoning can be logged at debug level if needed
					}
				}
			}
		}

		// Check for error field
		if query.Error != "" {
			// Log error if needed
			// logWarning(fmt.Sprintf("⚠️ Task error: %s", query.Error))
		}

		taskStatus := query.TaskStatus
		switch taskStatus {
		case "completed":
			return &ExecutionResult{
				ApiResponse:  models.ApiResponse{RequestID: query.RequestID},
				Success:      true,
				ErrorMessage: "",
				TaskID:       taskID,
				TaskStatus:   taskStatus,
				TaskResult:   query.TaskProduct,
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
				Success:      false,
				ErrorMessage: errorMsg,
				TaskID:       taskID,
				TaskStatus:   taskStatus,
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
				Success:      false,
				ErrorMessage: errorMsg,
				TaskID:       taskID,
				TaskStatus:   taskStatus,
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
				Success:      false,
				ErrorMessage: errorMsg,
				TaskID:       taskID,
				TaskStatus:   taskStatus,
			}
		}

		fmt.Printf("⏳ Task %s running 🚀: %s.\n", taskID, query.TaskAction)
		time.Sleep(3 * time.Second)
		triedTime++
	}

	fmt.Println("⚠️ task execution timeout!")
	terminateResult := a.TerminateTask(taskID)
	if terminateResult.Success {
		fmt.Printf("✅ Terminate request sent for task %s after timeout\n", taskID)
	} else {
		fmt.Printf("⚠️ Failed to terminate task %s after timeout: %s\n", taskID, terminateResult.ErrorMessage)
	}

	fmt.Printf("⏳ Waiting for task %s to be fully terminated...\n", taskID)
	terminatePollInterval := 1
	maxTerminatePollAttempts := 30
	terminateTriedTime := 0
	taskTerminatedConfirmed := false

	for terminateTriedTime < maxTerminatePollAttempts {
		statusQuery := a.GetTaskStatus(taskID)
		if !statusQuery.Success {
			errorMsg := statusQuery.ErrorMessage
			if errorMsg != "" && strings.HasPrefix(errorMsg, "Task not found or already finished") {
				fmt.Printf("✅ Task %s confirmed terminated (not found or finished)\n", taskID)
				taskTerminatedConfirmed = true
				break
			}
		}
		time.Sleep(time.Duration(terminatePollInterval) * time.Second)
		terminateTriedTime++
	}

	if !taskTerminatedConfirmed {
		fmt.Printf("⚠️ Timeout waiting for task %s to be fully terminated\n", taskID)
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
	fmt.Println("Terminating task")
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
