# Context API Reference

## 🚀 Related Tutorial

- [First Session Tutorial](../../../../../docs/quickstart/first-session.md) - Get started with creating your first AgentBay session

## Type Context

```go
type Context struct {
	// ID is the unique identifier of the context.
	ID	string

	// Name is the name of the context.
	Name	string

	// State is deprecated and will be removed in a future version.
	// Deprecated: This field is no longer used.
	State	string

	// CreatedAt is the date and time when the Context was created.
	CreatedAt	string

	// LastUsedAt is the date and time when the Context was last used.
	LastUsedAt	string

	// OSType is deprecated and will be removed in a future version.
	// Deprecated: This field is no longer used.
	OSType	string
}
```

Context represents a persistent storage context in the AgentBay cloud environment.

## Type ContextResult

```go
type ContextResult struct {
	models.ApiResponse
	Success		bool
	ContextID	string
	Context		*Context
	ErrorMessage	string
}
```

ContextResult wraps context operation result and RequestID

## Type ContextListResult

```go
type ContextListResult struct {
	models.ApiResponse
	Success		bool
	Contexts	[]*Context
	NextToken	string
	MaxResults	int32
	TotalCount	int32
	ErrorMessage	string
}
```

ContextListResult wraps context list and RequestID

## Type ContextCreateResult

```go
type ContextCreateResult struct {
	models.ApiResponse
	ContextID	string
}
```

ContextCreateResult wraps context creation result and RequestID

## Type ContextModifyResult

```go
type ContextModifyResult struct {
	models.ApiResponse
	Success		bool
	ErrorMessage	string
}
```

ContextModifyResult wraps context modification result and RequestID

## Type ContextDeleteResult

```go
type ContextDeleteResult struct {
	models.ApiResponse
	Success		bool
	ErrorMessage	string
}
```

ContextDeleteResult wraps context deletion result and RequestID

## Type ContextClearResult

```go
type ContextClearResult struct {
	models.ApiResponse
	Success		bool
	Status		string	// Current status of the clearing task ("clearing", "available", etc.)
	ContextID	string
	ErrorMessage	string
}
```

ContextClearResult wraps context clear operation result and RequestID

## Type ContextService

```go
type ContextService struct {
	// AgentBay is the AgentBay instance.
	AgentBay *AgentBay
}
```

ContextService provides methods to manage persistent contexts in the AgentBay cloud environment.

### Methods

#### Clear

```go
func (cs *ContextService) Clear(contextID string, timeoutSeconds int, pollIntervalSeconds float64) (*ContextClearResult, error)
```

Clear synchronously clears the context's persistent data and waits for the final result. This method
wraps the ClearAsync and GetClearStatus polling logic.

The clearing process transitions through the following states: - "clearing": Data clearing is in
progress - "available": Clearing completed successfully (final success state)

Parameters:
  - contextID: Unique ID of the context to clear
  - timeout: Timeout in seconds to wait for task completion (default: 60)
  - pollInterval: Interval in seconds between status polls (default: 2)

Returns a ContextClearResult object containing the final task result. The status field will be
"available" on success, or other states if interrupted.

#### ClearAsync

```go
func (cs *ContextService) ClearAsync(contextID string) (*ContextClearResult, error)
```

ClearAsync asynchronously initiates a task to clear the context's persistent data. This is a
non-blocking method that returns immediately after initiating the clearing task. The context's state
will transition to "clearing" while the operation is in progress.

#### Create

```go
func (cs *ContextService) Create(name string) (*ContextCreateResult, error)
```

Create creates a new context with the given name.

#### Delete

```go
func (cs *ContextService) Delete(context *Context) (*ContextDeleteResult, error)
```

Delete deletes the specified context.

#### DeleteFile

```go
func (cs *ContextService) DeleteFile(contextID string, filePath string) (*ContextFileDeleteResult, error)
```

DeleteFile deletes a file in a context.

#### Get

```go
func (cs *ContextService) Get(name string, create bool) (*ContextResult, error)
```

Get gets a context by name. Optionally creates it if it doesn't exist.

#### GetClearStatus

```go
func (cs *ContextService) GetClearStatus(contextID string) (*ContextClearResult, error)
```

GetClearStatus queries the status of the clearing task. This method calls GetContext API directly
with contextID and parses the raw response to extract the state field, which indicates the current
clearing status.

#### GetFileDownloadUrl

```go
func (cs *ContextService) GetFileDownloadUrl(contextID string, filePath string) (*ContextFileUrlResult, error)
```

GetFileDownloadUrl gets a presigned download URL for a file in a context.

#### GetFileUploadUrl

```go
func (cs *ContextService) GetFileUploadUrl(contextID string, filePath string) (*ContextFileUrlResult, error)
```

GetFileUploadUrl gets a presigned upload URL for a file in a context.

#### List

```go
func (cs *ContextService) List(params *ContextListParams) (*ContextListResult, error)
```

List lists all available contexts with pagination support.

#### ListFiles

```go
func (cs *ContextService) ListFiles(contextID string, parentFolderPath string, pageNumber int32, pageSize int32) (*ContextFileListResult, error)
```

ListFiles lists files under a specific folder path in a context.

#### Update

```go
func (cs *ContextService) Update(context *Context) (*ContextModifyResult, error)
```

Update updates the specified context. Returns a result with success status.

## Type ContextListParams

```go
type ContextListParams struct {
	MaxResults	int32	// Number of results per page
	NextToken	string	// Token for the next page
}
```

ContextListParams contains parameters for listing contexts

### Related Functions

#### NewContextListParams

```go
func NewContextListParams() *ContextListParams
```

NewContextListParams creates a new ContextListParams with default values

## Type ContextFileUrlResult

```go
type ContextFileUrlResult struct {
	models.ApiResponse
	Success		bool
	Url		string
	ExpireTime	*int64
	ErrorMessage	string
}
```

ContextFileUrlResult represents a presigned URL operation result.

## Type ContextFileEntry

```go
type ContextFileEntry struct {
	FileID		string
	FileName	string
	FilePath	string
	FileType	string
	GmtCreate	string
	GmtModified	string
	Size		int64
	Status		string
}
```

ContextFileEntry represents a file item in a context.

## Type ContextFileListResult

```go
type ContextFileListResult struct {
	models.ApiResponse
	Success		bool
	Entries		[]*ContextFileEntry
	Count		*int32
	ErrorMessage	string
}
```

ContextFileListResult represents the result of listing files under a context path.

## Type ContextFileDeleteResult

```go
type ContextFileDeleteResult struct {
	models.ApiResponse
	Success		bool
	ErrorMessage	string
}
```

ContextFileDeleteResult represents the result of deleting a file in a context.

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
