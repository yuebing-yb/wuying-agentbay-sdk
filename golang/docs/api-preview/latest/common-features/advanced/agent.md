# Agent API Reference

## 🤖 Related Tutorial

- [Agent Modules Guide](../../../../../docs/guides/common-features/advanced/agent-modules.md) - Learn about agent modules and custom agents

## Type Agent

```go
type Agent struct {
	Session McpSession
}
```

Agent represents an agent to manipulate applications to complete specific tasks

### Methods

#### ExecuteTask

```go
func (a *Agent) ExecuteTask(task string, maxTryTimes int) *ExecutionResult
```

ExecuteTask executes a specific task described in human language

**Example:**

```go
package main
import (
	"fmt"
	"os"
	"github.com/aliyun/wuying-agentbay-sdk/golang/pkg/agentbay"
)
func main() {

	// Initialize the SDK

	client, err := agentbay.NewAgentBay(os.Getenv("AGENTBAY_API_KEY"), nil)
	if err != nil {
		fmt.Printf("Error initializing AgentBay client: %v\n", err)
		os.Exit(1)
	}

	// Create a session with Windows image (required for Agent functionality)

	params := agentbay.NewCreateSessionParams().WithImageId("windows_latest")
	sessionResult, err := client.Create(params)
	if err != nil {
		fmt.Printf("Error creating session: %v\n", err)
		os.Exit(1)
	}
	session := sessionResult.Session

	// Execute a task using the Agent

	taskDescription := "Find the current weather in New York City"
	executionResult := session.Agent.ExecuteTask(taskDescription, 10)
	if executionResult.Success {
		fmt.Printf("Task completed successfully with status: %s\n", executionResult.TaskStatus)
		fmt.Printf("Task ID: %s\n", executionResult.TaskID)
	} else {
		fmt.Printf("Task failed: %s\n", executionResult.ErrorMessage)
	}
}
```

#### GetTaskStatus

```go
func (a *Agent) GetTaskStatus(taskID string) *QueryResult
```

GetTaskStatus gets the status of the task with the given task ID

**Example:**

```go
// Get the status of a specific task

taskID := "task-12345"
statusResult := session.Agent.GetTaskStatus(taskID)
if statusResult.Success {
	fmt.Printf("Task output: %s\n", statusResult.Output)
} else {
	fmt.Printf("Failed to get task status: %s\n", statusResult.ErrorMessage)
}
```

#### TerminateTask

```go
func (a *Agent) TerminateTask(taskID string) *ExecutionResult
```

TerminateTask terminates a task with a specified task ID

**Example:**

```go
// Terminate a running task

taskID := "task-12345"
terminateResult := session.Agent.TerminateTask(taskID)
if terminateResult.Success {
	fmt.Printf("Task terminated successfully with status: %s\n", terminateResult.TaskStatus)
} else {
	fmt.Printf("Failed to terminate task: %s\n", terminateResult.ErrorMessage)
}
```

### Related Functions

#### NewAgent

```go
func NewAgent(session McpSession) *Agent
```

NewAgent creates a new Agent instance

## Type ExecutionResult

```go
type ExecutionResult struct {
	models.ApiResponse
	Success		bool	`json:"success"`
	ErrorMessage	string	`json:"error_message"`
	TaskID		string	`json:"task_id"`
	TaskStatus	string	`json:"task_status"`
}
```

ExecutionResult represents the result of task execution

## Type McpSession

```go
type McpSession interface {
	GetAPIKey() string
	GetSessionId() string
	CallMcpTool(toolName string, args interface{}, autoGenSession ...bool) (*models.McpToolResult, error)
}
```

McpSession interface defines the methods needed by Agent

## Type QueryResult

```go
type QueryResult struct {
	models.ApiResponse
	Success		bool	`json:"success"`
	Output		string	`json:"output"`
	ErrorMessage	string	`json:"error_message"`
}
```

QueryResult represents the result of query operations

## Related Resources

- [Session API Reference](../basics/session.md)

---

*Documentation generated automatically from Go source code.*
