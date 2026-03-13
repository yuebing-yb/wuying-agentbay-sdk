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

## Type AgentEvent

```go
type AgentEvent struct {
	Type		string			`json:"type"`
	Seq		int			`json:"seq"`
	Round		int			`json:"round"`
	Content		string			`json:"content,omitempty"`
	ToolCallID	string			`json:"toolCallId,omitempty"`
	ToolName	string			`json:"toolName,omitempty"`
	Args		map[string]interface{}	`json:"args,omitempty"`
	Result		map[string]interface{}	`json:"result,omitempty"`
	Error		map[string]interface{}	`json:"error,omitempty"`
}
```

AgentEvent represents a streaming event from an Agent execution.

Event types: "reasoning", "content", "tool_call", "tool_result", "error".

The Result field in tool_result events carries an agent-defined structure that the SDK passes
through without parsing. Typical fields include "isError" (bool), "output" (string), and optionally
"screenshot" (base64). The final task outcome is delivered via the ExecutionResult return value of
ExecuteTaskAndWait.

## Type AgentEventCallback

```go
type AgentEventCallback func(event AgentEvent)
```

AgentEventCallback is a function type for handling agent streaming events.

## Type BrowserUseAgent

```go
type BrowserUseAgent struct {
	*baseTaskAgent
	initialized	bool
}
```

BrowserUseAgent represents an agent to manipulate a browser to complete specific tasks

> **⚠️ Note**: Currently, for agent services (including ComputerUseAgent, BrowserUseAgent, and
MobileUseAgent), we do not provide services for overseas users registered with **alibabacloud.com**.

### Methods

### ExecuteTask

```go
func (a *BrowserUseAgent) ExecuteTask(task string, use_vision bool, output_schema interface{}) *ExecutionResult
```

Execute a task described in human language on a browser without waiting for completion
(non-blocking).

This is a fire-and-return interface that immediately provides a task ID. Call get_task_status to
check the task status. You can control the timeout of the task execution in your own code by setting
the frequency of calling get_task_status.

Args: task: Task description in human language. use_vision: Whether to use vision to performe the
task. output_schema: The schema of the structured output.

Returns: ExecutionResult: Result object containing success status, task ID,


task status, and error message if any.

Example: ```typescript client, err := agentbay.NewAgentBay(apiKey)


if err != nil {

	fmt.Printf("Error initializing AgentBay client: %v\n", err)

	return

}

sessionParams := agentbay.NewCreateSessionParams().WithImageId("windows_latest") sessionResult,
err := client.Create(sessionParams)


if err != nil {

	fmt.Printf("Error creating session: %v\n", err)

	return

}

session := sessionResult.Session


type OutputSchema struct {

	City string `json:"City" jsonschema:"required"`

	Weather string `json:"Weather" jsonschema:"required"`

}

result = await session.Agent.Browser.ExecuteTask(task="Query the weather in Shanghai",false,
&OutputSchema{}) fmt.Printf(


f"Task ID: {result.task_id}, Status: {result.task_status}")

status = await session.Agent.Browser.GetTaskStatus(result.task_id) fmt.Printf(f"Task status:
{status.task_status}") await session.delete() ```

### ExecuteTaskAndWait

```go
func (a *BrowserUseAgent) ExecuteTaskAndWait(task string, timeout int, use_vision bool, output_schema interface{}) *ExecutionResult
```

Execute a task described in human language on a browser synchronously.

This is a synchronous interface that blocks until the task is completed or an error occurs,
or timeout happens. The default polling interval is 3 seconds.

Args:


task: Task description in human language.

timeout: Maximum time to wait for task completion in seconds.

	Used to control how long to wait for task completion.

use_vision: Whether to use vision to performe the task.

output_schema: The schema of the structured output.

Returns:


ExecutionResult: Result object containing success status, task ID,

	task status, and error message if any.

Example: ```typescript client, err := agentbay.NewAgentBay(apiKey)


if err != nil {

	fmt.Printf("Error initializing AgentBay client: %v\n", err)

	return

}

sessionParams := agentbay.NewCreateSessionParams().WithImageId("windows_latest") sessionResult,
err := client.Create(sessionParams)


if err != nil {

	fmt.Printf("Error creating session: %v\n", err)

	return

}

session := sessionResult.Session


type OutputSchema struct {

	City string `json:"City" jsonschema:"required"`

	Weather string `json:"Weather" jsonschema:"required"`

}

result = await session.Agent.Browser.ExecuteTaskAndWait(task="Query the weather in Shanghai",180,
false, &OutputSchema{}) fmt.Printf("Task status: %s\n", executionResult.TaskStatus) ```

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
func (a *BrowserUseAgent) Initialize(option *browser.BrowserOption) (bool, error)
```

* * Initialize the browser on which the agent performs tasks. * You are supposed to call this API
before executeTask is called, but is't optional. * @param option Browser option * @return True if
the browser is successfully initialized, False otherwise.

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

## Type DefaultSchema

```go
type DefaultSchema struct {
	Result string `json:"Result" jsonschema:"required"`
}
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

## Type McpSession

```go
type McpSession interface {
	GetAPIKey() string
	GetSessionId() string
	CallMcpTool(toolName string, args interface{}) (*models.McpToolResult, error)
	GetBrowser() *browser.Browser
	GetWsClient() (interface{}, error)
}
```

McpSession interface defines the methods needed by Agent

## Type MobileTaskOptions

```go
type MobileTaskOptions struct {
	StreamOptions
	MaxSteps	int
	OnCallForUser	func(event AgentEvent) string
}
```

MobileTaskOptions holds options for mobile task execution, including streaming callbacks inherited
from StreamOptions.

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
func (a *MobileUseAgent) ExecuteTask(task string, opts ...MobileTaskOptions) *TaskExecution
```

ExecuteTask starts a mobile task and returns a TaskExecution handle immediately (non-blocking).
Use TaskExecution.Wait(timeout) to block until the task completes.

When streaming callbacks are provided in MobileTaskOptions, real-time events are delivered via
WebSocket. Otherwise the task is started via MCP and the handle supports polling-based Wait().

Example (non-blocking):


execution := session.Agent.Mobile.ExecuteTask("Open WeChat app")

result := execution.Wait(180)

Example (with streaming):


execution := session.Agent.Mobile.ExecuteTask("Open Settings", agent.MobileTaskOptions{

    MaxSteps: 50,

    StreamOptions: agent.StreamOptions{

        OnReasoning: func(e agent.AgentEvent) { fmt.Println(e.Content) },

    },

})

result := execution.Wait(180)

### ExecuteTaskAndWait

```go
func (a *MobileUseAgent) ExecuteTaskAndWait(task string, timeout int, opts ...MobileTaskOptions) *ExecutionResult
```

ExecuteTaskAndWait is a convenience wrapper that starts a task via ExecuteTask and immediately
blocks until it completes or times out.

Example (simple):


result := session.Agent.Mobile.ExecuteTaskAndWait("Open WeChat app", 180)

Example (with streaming):


result := session.Agent.Mobile.ExecuteTaskAndWait("Open Settings", 180, agent.MobileTaskOptions{

    MaxSteps: 50,

    StreamOptions: agent.StreamOptions{

        OnReasoning: func(e agent.AgentEvent) { fmt.Println(e.Content) },

    },

})

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

## Type StreamOptions

```go
type StreamOptions struct {
	OnReasoning	AgentEventCallback
	OnContent	AgentEventCallback
	OnToolCall	AgentEventCallback
	OnToolResult	AgentEventCallback
	OnError		AgentEventCallback
}
```

StreamOptions holds streaming callback options.

## Type TaskExecution

```go
type TaskExecution struct {
	TaskID	string
	waitFn	func(timeout int) *ExecutionResult
}
```

TaskExecution represents a running task that can be waited on for its final result. Returned by
MobileUseAgent.ExecuteTask when the task is started.

### Methods

### Wait

```go
func (te *TaskExecution) Wait(timeout int) *ExecutionResult
```

Wait blocks until the task finishes or the timeout (in seconds) is reached. A timeout of 0 means
wait indefinitely (until the task finishes or fails).

## Type baseTaskAgent

```go
type baseTaskAgent struct {
	Session		McpSession
	ToolPrefix	string
}
```

baseTaskAgent provides common functionality for task execution agents

## Type streamContext

```go
type streamContext struct {
	contentParts	[]string
	lastError	map[string]interface{}
	streamErr	error
}
```

streamContext holds mutable state shared between WS callbacks and TaskExecution.Wait().

## Related Resources

- [Session API Reference](../basics/session.md)

---

*Documentation generated automatically from Go source code.*
