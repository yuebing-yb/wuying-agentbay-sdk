# Agent API Reference

## 🤖 Related Tutorial

- [Agent Modules Guide](../../../../../docs/guides/common-features/advanced/agent-modules.md) - Learn about agent modules and custom agents

## Type Agent

```go
type Agent struct {
	Browser		*BrowserUseAgent
	Computer	*ComputerUseAgent
	Mobile		*MobileUseAgent
}
```

Agent represents an agent to manipulate applications to complete specific tasks

> **⚠️ Note**: Currently, for agent services (including ComputerUseAgent, BrowserUseAgent, and
MobileUseAgent), we do not provide services for overseas users registered with **alibabacloud.com**.

### Related Functions

### NewAgent

```go
func NewAgent(session McpSession) *Agent
```

NewAgent creates a new Agent instance

## Type AgentOptions

```go
type AgentOptions struct {
	UseVision	bool
	OutputSchema	string
}
```

## Type BrowserUseAgent

```go
type BrowserUseAgent struct {
	*baseTaskAgent
}
```

BrowserUseAgent represents an agent to manipulate a browser to complete specific tasks

> **⚠️ Note**: Currently, for agent services (including ComputerUseAgent, BrowserUseAgent, and
MobileUseAgent), we do not provide services for overseas users registered with **alibabacloud.com**.

### Methods

### ExecuteTask

```go
func (a *BrowserUseAgent) ExecuteTask(task string, timeout ...int) *ExecutionResult
```

ExecuteTask executes a task in human language. If timeout is provided, it will wait for task
completion (blocking). If timeout is not provided, it returns immediately with a task ID
(non-blocking).

Non-blocking usage (new style):


result := sessionResult.Session.Agent.Browser.ExecuteTask("Open Chrome browser")

status := sessionResult.Session.Agent.Browser.GetTaskStatus(result.TaskID)

Blocking usage (backward compatible):


result := sessionResult.Session.Agent.Browser.ExecuteTask("Open Chrome browser", 20)

### ExecuteTaskAndWait

```go
func (a *BrowserUseAgent) ExecuteTaskAndWait(task string, timeout int) *ExecutionResult
```

ExecuteTaskAndWait executes a specific task described in human language synchronously. This is
a synchronous interface that blocks until the task is completed or an error occurs, or timeout
happens. The default polling interval is 3 seconds.

**Example:**

```go
client, _ := agentbay.NewAgentBay(os.Getenv("AGENTBAY_API_KEY"), nil)
sessionResult, _ := client.Create(agentbay.NewCreateSessionParams().WithImageId("windows_latest"))
defer sessionResult.Session.Delete()
result := sessionResult.Session.Agent.Browser.ExecuteTaskAndWait("Open Chrome browser", 60)
```

### GetTaskStatus

```go
func (a *BrowserUseAgent) GetTaskStatus(taskID string) *QueryResult
```

GetTaskStatus gets the status of the task with the given task ID

**Example:**

```go
client, _ := agentbay.NewAgentBay(os.Getenv("AGENTBAY_API_KEY"), nil)
sessionResult, _ := client.Create(agentbay.NewCreateSessionParams().WithImageId("windows_latest"))
defer sessionResult.Session.Delete()
execResult := sessionResult.Session.Agent.Browser.ExecuteTask("Find weather in NYC", 10)
statusResult := sessionResult.Session.Agent.Browser.GetTaskStatus(execResult.TaskID)
```

### Initialize

```go
func (a *BrowserUseAgent) Initialize(options *AgentOptions) *InitializationResult
```

Initialize initializes the browser agent with options. If options is nil, default values will be
used (use_vision=false, output_schema={}).

### TerminateTask

```go
func (a *BrowserUseAgent) TerminateTask(taskID string) *ExecutionResult
```

TerminateTask terminates a task with a specified task ID

**Example:**

```go
client, _ := agentbay.NewAgentBay(os.Getenv("AGENTBAY_API_KEY"), nil)
sessionResult, _ := client.Create(agentbay.NewCreateSessionParams().WithImageId("windows_latest"))
defer sessionResult.Session.Delete()
execResult := sessionResult.Session.Agent.Browser.ExecuteTask("Find weather in NYC", 10)
terminateResult := sessionResult.Session.Agent.Browser.TerminateTask(execResult.TaskID)
```

### Related Functions

### NewBrowserUseAgent

```go
func NewBrowserUseAgent(session McpSession) *BrowserUseAgent
```

## Type ComputerUseAgent

```go
type ComputerUseAgent struct {
	*baseTaskAgent
}
```

ComputerUseAgent represents an agent to manipulate a browser to complete specific tasks

> **⚠️ Note**: Currently, for agent services (including ComputerUseAgent, BrowserUseAgent, and
MobileUseAgent), we do not provide services for overseas users registered with **alibabacloud.com**.

### Methods

### ExecuteTask

```go
func (a *ComputerUseAgent) ExecuteTask(task string, timeout ...int) *ExecutionResult
```

ExecuteTask executes a task in human language. If timeout is provided, it will wait for task
completion (blocking). If timeout is not provided, it returns immediately with a task ID
(non-blocking).

Non-blocking usage (new style):


result := sessionResult.Session.Agent.Computer.ExecuteTask("Open Chrome browser")

status := sessionResult.Session.Agent.Computer.GetTaskStatus(result.TaskID)

Blocking usage (backward compatible):


result := sessionResult.Session.Agent.Computer.ExecuteTask("Open Chrome browser", 20)

### ExecuteTaskAndWait

```go
func (a *ComputerUseAgent) ExecuteTaskAndWait(task string, timeout int) *ExecutionResult
```

ExecuteTaskAndWait executes a specific task described in human language synchronously. This is
a synchronous interface that blocks until the task is completed or an error occurs, or timeout
happens. The default polling interval is 3 seconds.

**Example:**

```go
client, _ := agentbay.NewAgentBay(os.Getenv("AGENTBAY_API_KEY"), nil)
sessionResult, _ := client.Create(agentbay.NewCreateSessionParams().WithImageId("windows_latest"))
defer sessionResult.Session.Delete()
result := sessionResult.Session.Agent.Computer.ExecuteTaskAndWait("Open Chrome browser", 60)
```

### GetTaskStatus

```go
func (a *ComputerUseAgent) GetTaskStatus(taskID string) *QueryResult
```

GetTaskStatus gets the status of the task with the given task ID

**Example:**

```go
client, _ := agentbay.NewAgentBay(os.Getenv("AGENTBAY_API_KEY"), nil)
sessionResult, _ := client.Create(agentbay.NewCreateSessionParams().WithImageId("windows_latest"))
defer sessionResult.Session.Delete()
execResult := sessionResult.Session.Agent.Computer.ExecuteTask("Find weather in NYC", 10)
statusResult := sessionResult.Session.Agent.Computer.GetTaskStatus(execResult.TaskID)
```

### TerminateTask

```go
func (a *ComputerUseAgent) TerminateTask(taskID string) *ExecutionResult
```

TerminateTask terminates a task with a specified task ID

**Example:**

```go
client, _ := agentbay.NewAgentBay(os.Getenv("AGENTBAY_API_KEY"), nil)
sessionResult, _ := client.Create(agentbay.NewCreateSessionParams().WithImageId("windows_latest"))
defer sessionResult.Session.Delete()
execResult := sessionResult.Session.Agent.Computer.ExecuteTask("Find weather in NYC", 10)
terminateResult := sessionResult.Session.Agent.Computer.TerminateTask(execResult.TaskID)
```

### Related Functions

### NewComputerUseAgent

```go
func NewComputerUseAgent(session McpSession) *ComputerUseAgent
```

## Type ExecutionResult

```go
type ExecutionResult struct {
	models.ApiResponse
	Success		bool	`json:"success"`
	ErrorMessage	string	`json:"error_message"`
	TaskID		string	`json:"task_id"`
	TaskStatus	string	`json:"task_status"`
	TaskResult	string	`json:"task_result"`
}
```

ExecutionResult represents the result of task execution

## Type InitializationResult

```go
type InitializationResult struct {
	models.ApiResponse
	Success		bool	`json:"success"`
	ErrorMessage	string	`json:"error_message"`
}
```

InitializationResult represents the result of agent initialization

## Type McpSession

```go
type McpSession interface {
	GetAPIKey() string
	GetSessionId() string
	CallMcpTool(toolName string, args interface{}, autoGenSession ...bool) (*models.McpToolResult, error)
}
```

McpSession interface defines the methods needed by Agent

## Type MobileUseAgent

```go
type MobileUseAgent struct {
	*baseTaskAgent
}
```

MobileUseAgent represents an agent to perform tasks on mobile devices

> **⚠️ Note**: Currently, for agent services (including ComputerUseAgent, BrowserUseAgent, and
MobileUseAgent), we do not provide services for overseas users registered with **alibabacloud.com**.

### Methods

### ExecuteTask

```go
func (a *MobileUseAgent) ExecuteTask(task string, maxSteps int) *ExecutionResult
```

ExecuteTask executes a task in human language without waiting for completion (non-blocking).
This is a fire-and-return interface that immediately provides a task ID. Call GetTaskStatus to check
the task status.

**Example:**

```go
result := sessionResult.Session.Agent.Mobile.ExecuteTask("Open WeChat app", 100)
status := sessionResult.Session.Agent.Mobile.GetTaskStatus(result.TaskID)
```

### ExecuteTaskAndWait

```go
func (a *MobileUseAgent) ExecuteTaskAndWait(task string, maxSteps int, timeout int) *ExecutionResult
```

ExecuteTaskAndWait executes a specific task described in human language synchronously. This is
a synchronous interface that blocks until the task is completed or an error occurs, or timeout
happens. The default polling interval is 3 seconds.

**Example:**

```go
result := sessionResult.Session.Agent.Mobile.ExecuteTaskAndWait("Open WeChat app", 100, 180)
```

### GetTaskStatus

```go
func (a *MobileUseAgent) GetTaskStatus(taskID string) *QueryResult
```

GetTaskStatus gets the status of the task with the given task ID

**Example:**

```go
statusResult := sessionResult.Session.Agent.Mobile.GetTaskStatus(execResult.TaskID)
```

### TerminateTask

```go
func (a *MobileUseAgent) TerminateTask(taskID string) *ExecutionResult
```

TerminateTask terminates a task with a specified task ID

**Example:**

```go
terminateResult := sessionResult.Session.Agent.Mobile.TerminateTask(execResult.TaskID)
```

### Related Functions

### NewMobileUseAgent

```go
func NewMobileUseAgent(session McpSession) *MobileUseAgent
```

## Type QueryResult

```go
type QueryResult struct {
	models.ApiResponse
	Success		bool		`json:"success"`
	ErrorMessage	string		`json:"error_message"`
	TaskID		string		`json:"task_id"`
	TaskStatus	string		`json:"task_status"`
	TaskAction	string		`json:"task_action"`
	TaskProduct	string		`json:"task_product"`
	Stream		[]StreamItem	`json:"stream,omitempty"`
	Error		string		`json:"error,omitempty"`
}
```

QueryResult represents the result of query operations

## Type StreamItem

```go
type StreamItem struct {
	Content		string	`json:"content,omitempty"`
	Reasoning	string	`json:"reasoning,omitempty"`
	TimestampMs	*int64	`json:"timestamp_ms,omitempty"`
}
```

StreamItem represents a single stream fragment

## Type baseTaskAgent

```go
type baseTaskAgent struct {
	Session		McpSession
	ToolPrefix	string
}
```

baseTaskAgent provides common functionality for task execution agents

## Related Resources

- [Session API Reference](../basics/session.md)

---

*Documentation generated automatically from Go source code.*
