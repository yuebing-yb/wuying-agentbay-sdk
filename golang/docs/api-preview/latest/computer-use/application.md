# Application API Reference

## Type AppOperationResult

```go
type AppOperationResult struct {
	models.ApiResponse
	Success	bool
}
```

AppOperationResult wraps application operation result and RequestID

## Type Application

```go
type Application struct {
	ID	string	`json:"id"`
	Name	string	`json:"name"`
	CmdLine	string	`json:"cmdline,omitempty"`
}
```

Application represents an application

## Type ApplicationListResult

```go
type ApplicationListResult struct {
	models.ApiResponse
	Applications	[]Application
}
```

ApplicationListResult wraps application list and RequestID

## Type ApplicationManager

```go
type ApplicationManager struct {
	Session interface {
		GetAPIKey() string
		GetClient() *mcp.Client
		GetSessionId() string
		IsVpc() bool
		NetworkInterfaceIp() string
		HttpPort() string
		FindServerForTool(toolName string) string
		CallMcpTool(toolName string, args interface{}, autoGenSession ...bool) (*models.McpToolResult, error)
	}
}
```

ApplicationManager handles application management operations in the AgentBay cloud environment.

### Methods

#### GetInstalledApps

```go
func (am *ApplicationManager) GetInstalledApps(startMenu bool, desktop bool, ignoreSystemApps bool) (*ApplicationListResult, error)
```

GetInstalledApps retrieves a list of installed applications.

#### ListVisibleApps

```go
func (am *ApplicationManager) ListVisibleApps() (*ProcessListResult, error)
```

ListVisibleApps returns a list of currently visible applications.

#### StartApp

```go
func (am *ApplicationManager) StartApp(startCmd string, workDirectory string, activity string) (*ProcessListResult, error)
```

StartApp starts an application with the given command, optional working directory, and optional
activity.

#### StopAppByCmd

```go
func (am *ApplicationManager) StopAppByCmd(stopCmd string) (*AppOperationResult, error)
```

StopAppByCmd stops an application by stop command.

#### StopAppByPID

```go
func (am *ApplicationManager) StopAppByPID(pid int) (*AppOperationResult, error)
```

StopAppByPID stops an application by its process ID.

#### StopAppByPName

```go
func (am *ApplicationManager) StopAppByPName(pname string) (*AppOperationResult, error)
```

StopAppByPName stops an application by process name.

### Related Functions

#### NewApplicationManager

```go
func NewApplicationManager(session interface {
	GetAPIKey() string
	GetClient() *mcp.Client
	GetSessionId() string
	IsVpc() bool
	NetworkInterfaceIp() string
	HttpPort() string
	FindServerForTool(toolName string) string
	CallMcpTool(toolName string, args interface{}, autoGenSession ...bool) (*models.McpToolResult, error)
}) *ApplicationManager
```

NewApplicationManager creates a new ApplicationManager object.

## Type InstalledApp

```go
type InstalledApp struct {
	Name		string	`json:"name"`
	StartCmd	string	`json:"start_cmd"`
	StopCmd		string	`json:"stop_cmd,omitempty"`
	WorkDirectory	string	`json:"work_directory,omitempty"`
}
```

InstalledApp represents an installed application

### Related Functions

#### parseInstalledAppsFromJSON

```go
func parseInstalledAppsFromJSON(jsonStr string) ([]InstalledApp, error)
```

parseInstalledAppsFromJSON parses JSON string into array of InstalledApp objects

## Type Process

```go
type Process struct {
	PName	string	`json:"pname"`
	PID	int	`json:"pid"`
	CmdLine	string	`json:"cmdline,omitempty"`
}
```

Process represents a running process

### Related Functions

#### parseProcessesFromJSON

```go
func parseProcessesFromJSON(jsonStr string) ([]Process, error)
```

parseProcessesFromJSON parses JSON string into array of Process objects

## Type ProcessListResult

```go
type ProcessListResult struct {
	models.ApiResponse
	Processes	[]Process
}
```

ProcessListResult wraps process list and RequestID

---

*Documentation generated automatically from Go source code.*
