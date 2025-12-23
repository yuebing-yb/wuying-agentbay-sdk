package agent

import (
	"encoding/json"
	"fmt"
	"time"

	"github.com/aliyun/wuying-agentbay-sdk/golang/pkg/agentbay/models"
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

// QueryResult represents the result of query operations
type QueryResult struct {
	models.ApiResponse
	Success      bool   `json:"success"`
	ErrorMessage string `json:"error_message"`
	TaskID       string `json:"task_id"`
	TaskStatus   string `json:"task_status"`
	TaskAction   string `json:"task_action"`
	TaskProduct  string `json:"task_product"`
}

// InitializationResult represents the result of agent initialization
type InitializationResult struct {
	models.ApiResponse
	Success      bool   `json:"success"`
	ErrorMessage string `json:"error_message"`
}

// Options for configuring the agent.
// Args:
// use_vision (bool): Whether to use vision to perform actions.
// output_schema(dict): User-defined output schema for the agent's results.

type AgentOptions struct {
	UseVision    bool
	OutputSchema string
}

// baseTaskAgent provides common functionality for task execution agents
type baseTaskAgent struct {
	Session    McpSession
	ToolPrefix string
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

	taskID, ok := content["taskId"].(string)
	if !ok {
		taskID, ok = content["task_id"].(string)
	}
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

// executeTaskAndWait executes a specific task described in human language synchronously.
// This is a synchronous interface that blocks until the task is completed or
// an error occurs, or timeout happens. The default polling interval is 3 seconds.
func (b *baseTaskAgent) executeTaskAndWait(task string, maxTryTimes int) *ExecutionResult {
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

	taskID, ok := content["taskId"].(string)
	if !ok {
		taskID, ok = content["task_id"].(string)
	}
	if !ok {
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
	triedTime := 0
	for triedTime < maxTryTimes {
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
			return &ExecutionResult{
				ApiResponse:  models.ApiResponse{RequestID: query.RequestID},
				Success:      false,
				ErrorMessage: "Failed to execute task.",
				TaskID:       taskID,
				TaskStatus:   taskStatus,
			}
		case "cancelled":
			return &ExecutionResult{
				ApiResponse:  models.ApiResponse{RequestID: query.RequestID},
				Success:      false,
				ErrorMessage: "Task was cancelled.",
				TaskID:       taskID,
				TaskStatus:   taskStatus,
			}
		case "unsupported":
			return &ExecutionResult{
				ApiResponse:  models.ApiResponse{RequestID: query.RequestID},
				Success:      false,
				ErrorMessage: "Unsupported task.",
				TaskID:       taskID,
				TaskStatus:   taskStatus,
			}
		}

		fmt.Printf("⏳ Task %s running 🚀: %s.\n", taskID, query.TaskAction)
		time.Sleep(3 * time.Second)
		triedTime++
	}

	fmt.Println("⚠️ task execution timeout!")
	return &ExecutionResult{
		ApiResponse:  models.ApiResponse{RequestID: result.RequestID},
		Success:      false,
		ErrorMessage: "Task timeout.",
		TaskStatus:   "failed",
		TaskID:       taskID,
		TaskResult:   "Task timeout.",
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

	// Safely extract fields with defaults
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

	// Mobile Agent returns "result", other agents return "product"
	// Support both for compatibility, prefer "result"
	var product string
	if resultValue, ok := queryResult["result"].(string); ok && resultValue != "" {
		product = resultValue
	} else if productValue, ok := queryResult["product"].(string); ok {
		product = productValue
	} else {
		product = ""
	}

	return &QueryResult{
		ApiResponse: models.ApiResponse{RequestID: result.RequestID},
		Success:     true,
		TaskID:      taskIDFromResult,
		TaskStatus:  status,
		TaskAction:  action,
		TaskProduct: product,
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
type ComputerUseAgent struct {
	*baseTaskAgent
}

// BrowserUseAgent represents an agent to manipulate a browser to complete specific tasks
type BrowserUseAgent struct {
	*baseTaskAgent
}

// MobileUseAgent represents an agent to perform tasks on mobile devices
type MobileUseAgent struct {
	*baseTaskAgent
}

// Agent represents an agent to manipulate applications to complete specific tasks
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
// If maxTryTimes is provided, it will wait for task completion (blocking).
// If maxTryTimes is not provided, it returns immediately with a task ID (non-blocking).
//
// Non-blocking usage (new style):
//
//	result := sessionResult.Session.Agent.Computer.ExecuteTask("Open Chrome browser")
//	status := sessionResult.Session.Agent.Computer.GetTaskStatus(result.TaskID)
//
// Blocking usage (backward compatible):
//
//	result := sessionResult.Session.Agent.Computer.ExecuteTask("Open Chrome browser", 20)
func (a *ComputerUseAgent) ExecuteTask(task string, maxTryTimes ...int) *ExecutionResult {
	if len(maxTryTimes) > 0 {
		// Backward compatible: blocking version
		return a.baseTaskAgent.executeTaskAndWait(task, maxTryTimes[0])
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
//	result := sessionResult.Session.Agent.Computer.ExecuteTaskAndWait("Open Chrome browser", 20)
func (a *ComputerUseAgent) ExecuteTaskAndWait(task string, maxTryTimes int) *ExecutionResult {
	return a.baseTaskAgent.executeTaskAndWait(task, maxTryTimes)
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

// Initialize initializes the browser agent with options.
// If options is nil, default values will be used (use_vision=false, output_schema={}).
func (a *BrowserUseAgent) Initialize(options *AgentOptions) *InitializationResult {
	fmt.Println("Initialize Browser Use Agent...")

	args := map[string]interface{}{
		"use_vision":    false,
		"output_schema": map[string]interface{}{},
	}

	if options != nil {
		args["use_vision"] = options.UseVision
		// Convert string to map if needed, or use empty map if empty string
		if options.OutputSchema != "" {
			var schemaMap map[string]interface{}
			if err := json.Unmarshal([]byte(options.OutputSchema), &schemaMap); err == nil {
				args["output_schema"] = schemaMap
			} else {
				// If not valid JSON, use empty map
				args["output_schema"] = map[string]interface{}{}
			}
		} else {
			args["output_schema"] = map[string]interface{}{}
		}
	}

	result, err := a.baseTaskAgent.Session.CallMcpTool("browser_use_initialize", args)
	if err != nil {
		fmt.Printf("Failed to initialize: %v\n", err)
		return &InitializationResult{
			ApiResponse:  models.ApiResponse{RequestID: ""},
			Success:      false,
			ErrorMessage: fmt.Sprintf("Failed to initialize: %v", err),
		}
	}

	if result.Success {
		return &InitializationResult{
			ApiResponse:  models.ApiResponse{RequestID: result.RequestID},
			Success:      true,
			ErrorMessage: "",
		}
	}

	fmt.Println("Failed to initialize browser use agent")
	errorMessage := result.ErrorMessage
	if errorMessage == "" {
		errorMessage = "Failed to initialize browser use agent"
	}
	return &InitializationResult{
		ApiResponse:  models.ApiResponse{RequestID: result.RequestID},
		Success:      false,
		ErrorMessage: errorMessage,
	}
}

// ExecuteTask executes a task in human language.
// If maxTryTimes is provided, it will wait for task completion (blocking).
// If maxTryTimes is not provided, it returns immediately with a task ID (non-blocking).
//
// Non-blocking usage (new style):
//
//	result := sessionResult.Session.Agent.Browser.ExecuteTask("Open Chrome browser")
//	status := sessionResult.Session.Agent.Browser.GetTaskStatus(result.TaskID)
//
// Blocking usage (backward compatible):
//
//	result := sessionResult.Session.Agent.Browser.ExecuteTask("Open Chrome browser", 20)
func (a *BrowserUseAgent) ExecuteTask(task string, maxTryTimes ...int) *ExecutionResult {
	if len(maxTryTimes) > 0 {
		// Backward compatible: blocking version
		return a.baseTaskAgent.executeTaskAndWait(task, maxTryTimes[0])
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
//	result := sessionResult.Session.Agent.Browser.ExecuteTaskAndWait("Open Chrome browser", 20)
func (a *BrowserUseAgent) ExecuteTaskAndWait(task string, maxTryTimes int) *ExecutionResult {
	return a.baseTaskAgent.executeTaskAndWait(task, maxTryTimes)
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
//	result := sessionResult.Session.Agent.Mobile.ExecuteTask("Open WeChat app", 100, 5)
//	status := sessionResult.Session.Agent.Mobile.GetTaskStatus(result.TaskID)
func (a *MobileUseAgent) ExecuteTask(task string, maxSteps int, maxStepRetries int) *ExecutionResult {
	args := map[string]interface{}{
		"task":      task,
		"max_steps": maxSteps,
	}

	var lastError string
	var lastRequestID string

	for attempt := 0; attempt < maxStepRetries; attempt++ {
		result, err := a.baseTaskAgent.Session.CallMcpTool(
			a.baseTaskAgent.getToolName("execute"), args)
		if err != nil {
			lastError = fmt.Sprintf("Failed to execute: %v", err)
			if attempt < maxStepRetries-1 {
				time.Sleep(1 * time.Second)
				continue
			}
			return &ExecutionResult{
				ApiResponse:  models.ApiResponse{RequestID: lastRequestID},
				Success:      false,
				ErrorMessage: lastError,
				TaskStatus:   "failed",
				TaskID:       "",
			}
		}

		lastRequestID = result.RequestID

		if !result.Success {
			errorMessage := result.ErrorMessage
			if errorMessage == "" {
				errorMessage = "Failed to execute task"
			}
			lastError = errorMessage
			if attempt < maxStepRetries-1 {
				time.Sleep(1 * time.Second)
				continue
			}
			return &ExecutionResult{
				ApiResponse:  models.ApiResponse{RequestID: result.RequestID},
				Success:      false,
				ErrorMessage: lastError,
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

	return &ExecutionResult{
		ApiResponse:  models.ApiResponse{RequestID: lastRequestID},
		Success:      false,
		ErrorMessage: fmt.Sprintf("Failed after %d attempts: %s", maxStepRetries, lastError),
		TaskStatus:   "failed",
		TaskID:       "",
	}
}

// ExecuteTaskAndWait executes a specific task described in human language
// synchronously. This is a synchronous interface that blocks until the task
// is completed or an error occurs, or timeout happens. The default polling
// interval is 3 seconds.
//
// Example:
//
//	result := sessionResult.Session.Agent.Mobile.ExecuteTaskAndWait("Open WeChat app", 100, 3, 200)
func (a *MobileUseAgent) ExecuteTaskAndWait(task string, maxSteps int, maxStepRetries int, maxTryTimes int) *ExecutionResult {
	args := map[string]interface{}{
		"task":      task,
		"max_steps": maxSteps,
	}

	var taskID string
	var lastError string
	var lastRequestID string

	for attempt := 0; attempt < maxStepRetries; attempt++ {
		result, err := a.baseTaskAgent.Session.CallMcpTool(
			a.baseTaskAgent.getToolName("execute"), args)
		if err != nil {
			lastError = fmt.Sprintf("Failed to execute: %v", err)
			if attempt < maxStepRetries-1 {
				time.Sleep(1 * time.Second)
				continue
			}
			return &ExecutionResult{
				ApiResponse:  models.ApiResponse{RequestID: lastRequestID},
				Success:      false,
				ErrorMessage: lastError,
				TaskStatus:   "failed",
				TaskID:       "",
				TaskResult:   "Task Failed",
			}
		}

		lastRequestID = result.RequestID

		if !result.Success {
			errorMessage := result.ErrorMessage
			if errorMessage == "" {
				errorMessage = "Failed to execute task"
			}
			lastError = errorMessage
			if attempt < maxStepRetries-1 {
				time.Sleep(1 * time.Second)
				continue
			}
			return &ExecutionResult{
				ApiResponse:  models.ApiResponse{RequestID: result.RequestID},
				Success:      false,
				ErrorMessage: lastError,
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
		taskID, ok = content["taskId"].(string)
		if !ok {
			taskID, ok = content["task_id"].(string)
		}
		if !ok {
			return &ExecutionResult{
				ApiResponse:  models.ApiResponse{RequestID: result.RequestID},
				Success:      false,
				ErrorMessage: "Task ID not found in response",
				TaskStatus:   "failed",
				TaskID:       "",
				TaskResult:   "Invalid task ID.",
			}
		}
		break
	}

	if taskID == "" {
		return &ExecutionResult{
			ApiResponse:  models.ApiResponse{RequestID: lastRequestID},
			Success:      false,
			ErrorMessage: fmt.Sprintf("Failed to get task_id after %d attempts: %s", maxStepRetries, lastError),
			TaskStatus:   "failed",
			TaskID:       "",
			TaskResult:   "Task Failed",
		}
	}

	triedTime := 0
	for triedTime < maxTryTimes {
		query := a.baseTaskAgent.getTaskStatus(taskID)
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
			return &ExecutionResult{
				ApiResponse:  models.ApiResponse{RequestID: query.RequestID},
				Success:      false,
				ErrorMessage: "Failed to execute task.",
				TaskID:       taskID,
				TaskStatus:   taskStatus,
			}
		case "cancelled":
			return &ExecutionResult{
				ApiResponse:  models.ApiResponse{RequestID: query.RequestID},
				Success:      false,
				ErrorMessage: "Task was cancelled.",
				TaskID:       taskID,
				TaskStatus:   taskStatus,
			}
		case "unsupported":
			return &ExecutionResult{
				ApiResponse:  models.ApiResponse{RequestID: query.RequestID},
				Success:      false,
				ErrorMessage: "Unsupported task.",
				TaskID:       taskID,
				TaskStatus:   taskStatus,
			}
		}

		fmt.Printf("⏳ Task %s running 🚀: %s.\n", taskID, query.TaskAction)
		time.Sleep(3 * time.Second)
		triedTime++
	}

	fmt.Println("⚠️ task execution timeout!")
	return &ExecutionResult{
		ApiResponse:  models.ApiResponse{RequestID: lastRequestID},
		Success:      false,
		ErrorMessage: "Task timeout.",
		TaskStatus:   "failed",
		TaskID:       taskID,
		TaskResult:   "Task timeout.",
	}
}

// GetTaskStatus gets the status of the task with the given task ID
//
// Example:
//
//	statusResult := sessionResult.Session.Agent.Mobile.GetTaskStatus(execResult.TaskID)
func (a *MobileUseAgent) GetTaskStatus(taskID string) *QueryResult {
	return a.baseTaskAgent.getTaskStatus(taskID)
}

// TerminateTask terminates a task with a specified task ID
//
// Example:
//
//	terminateResult := sessionResult.Session.Agent.Mobile.TerminateTask(execResult.TaskID)
func (a *MobileUseAgent) TerminateTask(taskID string) *ExecutionResult {
	return a.baseTaskAgent.terminateTask(taskID)
}
