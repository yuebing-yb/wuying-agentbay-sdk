# Context Manager API Reference

## 🚀 Related Tutorial

- [First Session Tutorial](../../../../../docs/quickstart/first-session.md) - Get started with creating your first AgentBay session

## Type ContextStatusData

```go
type ContextStatusData struct {
	ContextId	string	`json:"contextId"`
	Path		string	`json:"path"`
	ErrorMessage	string	`json:"errorMessage"`
	Status		string	`json:"status"`
	StartTime	int64	`json:"startTime"`
	FinishTime	int64	`json:"finishTime"`
	TaskType	string	`json:"taskType"`
}
```

ContextStatusData represents the parsed context status data

## Type ContextStatusItem

```go
type ContextStatusItem struct {
	Type	string	`json:"type"`
	Data	string	`json:"data"`
}
```

ContextStatusItem represents an item in the context status response

## Type ContextInfoResult

```go
type ContextInfoResult struct {
	models.ApiResponse
	Success			bool
	ContextStatusData	[]ContextStatusData	// Parsed context status data
	ErrorMessage		string
}
```

ContextInfoResult wraps context info result and RequestID

## Type ContextSyncResult

```go
type ContextSyncResult struct {
	models.ApiResponse
	Success		bool
	ErrorMessage	string
}
```

ContextSyncResult wraps context sync result and RequestID

## Type ContextManager

```go
type ContextManager struct {
	Session interface {
		GetAPIKey() string
		GetClient() *mcp.Client
		GetSessionId() string
	}
}
```

ContextManager handles context operations for a specific session.

### Methods

#### Info

```go
func (cm *ContextManager) Info() (*ContextInfoResult, error)
```

Info retrieves context information for the current session.

#### InfoWithParams

```go
func (cm *ContextManager) InfoWithParams(contextId, path, taskType string) (*ContextInfoResult, error)
```

InfoWithParams retrieves context information for the current session with optional parameters.

#### Sync

```go
func (cm *ContextManager) Sync() (*ContextSyncResult, error)
```

Sync synchronizes the context for the current session.

#### SyncWithCallback

```go
func (cm *ContextManager) SyncWithCallback(contextId, path, mode string, callback SyncCallback, maxRetries int, retryInterval int) (*ContextSyncResult, error)
```

SyncWithCallback synchronizes the context with callback support (dual-mode). If callback is
provided, it runs in background and calls callback when complete. If callback is nil, it waits for
completion before returning.

#### SyncWithParams

```go
func (cm *ContextManager) SyncWithParams(contextId, path, mode string) (*ContextSyncResult, error)
```

SyncWithParams synchronizes the context for the current session with optional parameters.

#### pollForCompletion

```go
func (cm *ContextManager) pollForCompletion(callback SyncCallback, contextId, path string, maxRetries, retryInterval int)
```

pollForCompletion polls the info interface to check if sync is completed and calls callback.

#### pollForCompletionSync

```go
func (cm *ContextManager) pollForCompletionSync(contextId, path string, maxRetries, retryInterval int) (bool, error)
```

pollForCompletionSync is the synchronous version of polling for sync completion.

### Related Functions

#### NewContextManager

```go
func NewContextManager(session interface {
	GetAPIKey() string
	GetClient() *mcp.Client
	GetSessionId() string
}) *ContextManager
```

NewContextManager creates a new ContextManager object.

## Functions

### Deprecated

```go
func Deprecated(reason, replacement, version string)
```

Deprecated marks a function or method as deprecated and emits a warning

### DeprecatedFunc

```go
func DeprecatedFunc(reason, replacement, version string) func()
```

DeprecatedFunc is a helper function to mark functions as deprecated Usage: defer
DeprecatedFunc("reason", "replacement", "version")()

### DeprecatedMethod

```go
func DeprecatedMethod(methodName, reason, replacement, version string) func()
```

DeprecatedMethod is a helper function to mark methods as deprecated Usage: defer
DeprecatedMethod("MethodName", "reason", "replacement", "version")()

### FindDotEnvFile

```go
func FindDotEnvFile(startPath string) string
```

FindDotEnvFile searches for .env file upward from startPath. Search order: 1. Current working
directory 2. Parent directories (up to root) 3. Git repository root (if found)

Args:


startPath: Starting directory for search (empty string means current directory)

Returns:


Path to .env file if found, empty string otherwise

### GetLogLevel

```go
func GetLogLevel() int
```

GetLogLevel returns the current global log level

### LoadDotEnvWithFallback

```go
func LoadDotEnvWithFallback(customEnvPath string)
```

LoadDotEnvWithFallback loads .env file with improved search strategy.

Args:


customEnvPath: Custom path to .env file (empty string means search upward)

### LogAPICall

```go
func LogAPICall(apiName, requestParams string)
```

LogAPICall logs an API call with request parameters

### LogAPIResponseWithDetails

```go
func LogAPIResponseWithDetails(apiName, requestID string, success bool, keyFields map[string]interface{}, fullResponse string)
```

LogAPIResponseWithDetails logs a structured API response with key fields

### LogCodeExecutionOutput

```go
func LogCodeExecutionOutput(requestID, rawOutput string)
```

LogCodeExecutionOutput extracts and logs the actual code execution output from run_code response

### LogDebug

```go
func LogDebug(message string)
```

LogDebug logs a debug message

### LogInfo

```go
func LogInfo(message string)
```

LogInfo logs an informational message

### LogInfoWithColor

```go
func LogInfoWithColor(message string)
```

LogInfoWithColor logs an informational message with custom color

### LogOperationError

```go
func LogOperationError(operation, errorMsg string, withStack bool)
```

LogOperationError logs an operation error with optional stack trace

### MaskSensitiveData

```go
func MaskSensitiveData(data interface{}) interface{}
```

MaskSensitiveData recursively masks sensitive information in data structures

### SetDeprecationConfig

```go
func SetDeprecationConfig(config *DeprecationConfig)
```

SetDeprecationConfig sets the global deprecation configuration

### SetLogLevel

```go
func SetLogLevel(level int)
```

SetLogLevel sets the global log level

### SetupLogger

```go
func SetupLogger(config LoggerConfig)
```

SetupLogger configures the logger with file logging support

### containsWildcard

```go
func containsWildcard(path string) bool
```

### getColorCodes

```go
func getColorCodes() (reset, green, red, yellow, blue string)
```

getColorCodes returns ANSI color codes based on environment detection

### getVersion

```go
func getVersion() string
```

getVersion attempts to read version from Go module info Returns the version from go.mod or a default
fallback

### init

```go
func init()
```

Initialize log level from environment variable

### isIDEEnvironment

```go
func isIDEEnvironment() bool
```

isIDEEnvironment detects if running in an IDE that supports ANSI colors

### isReleaseVersion

```go
func isReleaseVersion() bool
```

isReleaseVersion checks if this is a release build Returns true only if the SDK is installed from
GitHub (github.com/aliyun/wuying-agentbay-sdk/golang) Returns false if: 1. Developing the SDK
locally (main module) 2. Installed via go.mod replace from internal source (code.alibaba-inc.com) 3.
Installed from a pseudo-version

### isSensitiveField

```go
func isSensitiveField(fieldName string, sensitiveFields []string) bool
```

### isValidLifecycle

```go
func isValidLifecycle(lifecycle Lifecycle) bool
```

isValidLifecycle checks if the given lifecycle value is valid

### isValidUploadMode

```go
func isValidUploadMode(uploadMode UploadMode) bool
```

isValidUploadMode checks if the given uploadMode value is valid

### maskSensitiveDataInternal

```go
func maskSensitiveDataInternal(data interface{}, fields []string) interface{}
```

### maskSensitiveDataString

```go
func maskSensitiveDataString(jsonStr string) string
```

maskSensitiveDataString masks sensitive information in a JSON string

### maskSensitiveDataWithRegex

```go
func maskSensitiveDataWithRegex(str string) string
```

maskSensitiveDataWithRegex masks sensitive data using regex patterns

### parseFileSize

```go
func parseFileSize(sizeStr string) int64
```

parseFileSize parses size string like "10 MB" to bytes

### parseLogLevel

```go
func parseLogLevel(levelStr string) int
```

parseLogLevel converts string to log level constant

### validateSyncPolicy

```go
func validateSyncPolicy(policy *SyncPolicy) error
```

### writeToFile

```go
func writeToFile(message string)
```

writeToFile writes a message to the log file with rotation

## Related Resources

- [Session API Reference](session.md)
- [Context API Reference](context.md)

---

*Documentation generated automatically from Go source code.*
