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

#### GetTaskStatus

```go
func (a *Agent) GetTaskStatus(taskID string) *QueryResult
```

GetTaskStatus gets the status of the task with the given task ID

#### TerminateTask

```go
func (a *Agent) TerminateTask(taskID string) *ExecutionResult
```

TerminateTask terminates a task with a specified task ID

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

- [Session API Reference](session.md)

---

*Documentation generated automatically from Go source code.*
