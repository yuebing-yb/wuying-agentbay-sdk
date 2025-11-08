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

**Example:**

```go
package main
import (
	"fmt"
	"os"
	"github.com/aliyun/wuying-agentbay-sdk/golang/pkg/agentbay"
)
func main() {
	client, err := agentbay.NewAgentBay(os.Getenv("AGENTBAY_API_KEY"), nil)
	if err != nil {
		fmt.Printf("Error: %v\n", err)
		os.Exit(1)
	}
	result, err := client.Create(nil)
	if err != nil {
		fmt.Printf("Error: %v\n", err)
		os.Exit(1)
	}
	session := result.Session

	// Get context synchronization information

	infoResult, err := session.Context.Info()
	if err != nil {
		fmt.Printf("Error: %v\n", err)
		os.Exit(1)
	}
	fmt.Printf("Context status data count: %d\n", len(infoResult.ContextStatusData))
	for _, item := range infoResult.ContextStatusData {
		fmt.Printf("Context %s: Status=%s, Path=%s\n", item.ContextId, item.Status, item.Path)
	}

	// Output: Context status data count: 0

	session.Delete()
}
```

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

Example (Synchronous mode - waits for completion):


package main

import (

	"fmt"

	"os"

	"github.com/aliyun/wuying-agentbay-sdk/golang/pkg/agentbay"

)

func main() {

	client, err := agentbay.NewAgentBay(os.Getenv("AGENTBAY_API_KEY"), nil)

	if err != nil {

		fmt.Printf("Error: %v\n", err)

		os.Exit(1)

	}

	result, err := client.Create(nil)

	if err != nil {

		fmt.Printf("Error: %v\n", err)

		os.Exit(1)

	}

	session := result.Session


	// Get or create a context

	contextResult, err := client.Context.Get("my-context", true)

	if err != nil {

		fmt.Printf("Error: %v\n", err)

		os.Exit(1)

	}


	// Synchronous mode: callback is nil, so it waits for completion

	syncResult, err := session.Context.SyncWithCallback(

		contextResult.ContextID,

		"/mnt/persistent",

		"upload",

		nil,  // No callback - synchronous mode

		10,   // maxRetries

		1000, // retryInterval in milliseconds

	)

	if err != nil {

		fmt.Printf("Error: %v\n", err)

		os.Exit(1)

	}

	fmt.Printf("Sync completed - Success: %v\n", syncResult.Success)


	// Output: No sync tasks found

	// Output: Sync completed - Success: true


	session.Delete()

}

Example (Asynchronous mode - with callback):


package main

import (

	"fmt"

	"os"

	"time"

	"github.com/aliyun/wuying-agentbay-sdk/golang/pkg/agentbay"

)

func main() {

	client, err := agentbay.NewAgentBay(os.Getenv("AGENTBAY_API_KEY"), nil)

	if err != nil {

		fmt.Printf("Error: %v\n", err)

		os.Exit(1)

	}

	result, err := client.Create(nil)

	if err != nil {

		fmt.Printf("Error: %v\n", err)

		os.Exit(1)

	}

	session := result.Session


	// Get or create a context

	contextResult, err := client.Context.Get("my-context", true)

	if err != nil {

		fmt.Printf("Error: %v\n", err)

		os.Exit(1)

	}


	// Asynchronous mode: with callback, returns immediately

	syncResult, err := session.Context.SyncWithCallback(

		contextResult.ContextID,

		"/mnt/persistent",

		"upload",

		func(success bool) {

			if success {

				fmt.Println("Context sync completed successfully")

			} else {

				fmt.Println("Context sync failed or timed out")

			}

		},

		150,  // maxRetries

		1500, // retryInterval in milliseconds

	)

	if err != nil {

		fmt.Printf("Error: %v\n", err)

		os.Exit(1)

	}

	fmt.Printf("Sync triggered - Success: %v\n", syncResult.Success)


	// Wait for callback to complete

	time.Sleep(5 * time.Second)


	// Output: Sync triggered - Success: true

	// Output: Context sync completed successfully


	session.Delete()

}

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

**Example:**

```go
package main
import (
	"fmt"
	"github.com/aliyun/wuying-agentbay-sdk/golang/pkg/agentbay"
)
func main() {

	// Set log level to DEBUG

	agentbay.SetLogLevel(agentbay.LOG_DEBUG)

	// Check current level

	currentLevel := agentbay.GetLogLevel()
	fmt.Printf("Current log level: %d\n", currentLevel)
}
```

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

**Example:**

```go
package main
import (
	"fmt"
	"os"
	"github.com/aliyun/wuying-agentbay-sdk/golang/pkg/agentbay"
)
func main() {

	// Set log level to DEBUG to see API calls

	agentbay.SetLogLevel(agentbay.LOG_DEBUG)
	client, err := agentbay.NewAgentBay(os.Getenv("AGENTBAY_API_KEY"), nil)
	if err != nil {
		fmt.Printf("Error: %v\n", err)
		os.Exit(1)
	}
	result, err := client.Create(nil)
	if err != nil {
		fmt.Printf("Error: %v\n", err)
		os.Exit(1)
	}
	session := result.Session
	defer session.Delete()

	// API calls are automatically logged by the SDK

	// Output: 🔗 API Call: create_session

}
```

### LogAPIResponseWithDetails

```go
func LogAPIResponseWithDetails(apiName, requestID string, success bool, keyFields map[string]interface{}, fullResponse string)
```

LogAPIResponseWithDetails logs a structured API response with key fields

**Example:**

```go
package main
import (
	"fmt"
	"os"
	"github.com/aliyun/wuying-agentbay-sdk/golang/pkg/agentbay"
)
func main() {

	// Set log level to DEBUG to see detailed responses

	agentbay.SetLogLevel(agentbay.LOG_DEBUG)
	client, err := agentbay.NewAgentBay(os.Getenv("AGENTBAY_API_KEY"), nil)
	if err != nil {
		fmt.Printf("Error: %v\n", err)
		os.Exit(1)
	}
	result, err := client.Create(nil)
	if err != nil {
		fmt.Printf("Error: %v\n", err)
		os.Exit(1)
	}
	session := result.Session
	defer session.Delete()

	// API responses are automatically logged by the SDK

	// Output: ✅ API Response: create_session, RequestId=xxx

}
```

### LogCodeExecutionOutput

```go
func LogCodeExecutionOutput(requestID, rawOutput string)
```

LogCodeExecutionOutput extracts and logs the actual code execution output from run_code response

**Example:**

```go
package main
import (
	"fmt"
	"os"
	"github.com/aliyun/wuying-agentbay-sdk/golang/pkg/agentbay"
)
func main() {

	// Set log level to INFO to see code execution output

	agentbay.SetLogLevel(agentbay.LOG_INFO)
	client, err := agentbay.NewAgentBay(os.Getenv("AGENTBAY_API_KEY"), nil)
	if err != nil {
		fmt.Printf("Error: %v\n", err)
		os.Exit(1)
	}
	result, err := client.Create(nil)
	if err != nil {
		fmt.Printf("Error: %v\n", err)
		os.Exit(1)
	}
	session := result.Session
	defer session.Delete()

	// Execute code in the session

	execResult, err := session.Code.RunCode("print('Hello from AgentBay')", "python")
	if err != nil {
		fmt.Printf("Error: %v\n", err)
		os.Exit(1)
	}
	fmt.Printf("Code execution completed: %v\n", execResult.Success)

	// Output: 📋 Code Execution Output (RequestID: xxx):

	// Output:    Hello from AgentBay

}
```

### LogDebug

```go
func LogDebug(message string)
```

LogDebug logs a debug message

**Example:**

```go
package main
import (
	"fmt"
	"os"
	"github.com/aliyun/wuying-agentbay-sdk/golang/pkg/agentbay"
)
func main() {

	// Set log level to DEBUG to see debug messages

	agentbay.SetLogLevel(agentbay.LOG_DEBUG)
	client, err := agentbay.NewAgentBay(os.Getenv("AGENTBAY_API_KEY"), nil)
	if err != nil {
		fmt.Printf("Error: %v\n", err)
		os.Exit(1)
	}
	result, err := client.Create(nil)
	if err != nil {
		fmt.Printf("Error: %v\n", err)
		os.Exit(1)
	}
	session := result.Session
	defer session.Delete()

	// Log debug messages

	agentbay.LogDebug("Debugging session creation process")

	// Output: 🐛 Debugging session creation process

}
```

### LogInfo

```go
func LogInfo(message string)
```

LogInfo logs an informational message

**Example:**

```go
package main
import (
	"fmt"
	"os"
	"github.com/aliyun/wuying-agentbay-sdk/golang/pkg/agentbay"
)
func main() {

	// Set log level to INFO or DEBUG to see info messages

	agentbay.SetLogLevel(agentbay.LOG_INFO)
	client, err := agentbay.NewAgentBay(os.Getenv("AGENTBAY_API_KEY"), nil)
	if err != nil {
		fmt.Printf("Error: %v\n", err)
		os.Exit(1)
	}
	result, err := client.Create(nil)
	if err != nil {
		fmt.Printf("Error: %v\n", err)
		os.Exit(1)
	}
	session := result.Session
	defer session.Delete()

	// Log informational messages

	agentbay.LogInfo("Session created successfully")

	// Output: ℹ️  Session created successfully

}
```

### LogInfoWithColor

```go
func LogInfoWithColor(message string)
```

LogInfoWithColor logs an informational message with custom color

**Example:**

```go
package main
import (
	"fmt"
	"os"
	"github.com/aliyun/wuying-agentbay-sdk/golang/pkg/agentbay"
)
func main() {

	// Set log level to INFO or DEBUG to see colored messages

	agentbay.SetLogLevel(agentbay.LOG_INFO)
	client, err := agentbay.NewAgentBay(os.Getenv("AGENTBAY_API_KEY"), nil)
	if err != nil {
		fmt.Printf("Error: %v\n", err)
		os.Exit(1)
	}
	result, err := client.Create(nil)
	if err != nil {
		fmt.Printf("Error: %v\n", err)
		os.Exit(1)
	}
	session := result.Session
	defer session.Delete()

	// Log informational messages with color emphasis

	agentbay.LogInfoWithColor("Important: Session ready for use")

	// Output: ℹ️  Important: Session ready for use

}
```

### LogOperationError

```go
func LogOperationError(operation, errorMsg string, withStack bool)
```

LogOperationError logs an operation error with optional stack trace

**Example:**

```go
package main
import (
	"fmt"
	"os"
	"github.com/aliyun/wuying-agentbay-sdk/golang/pkg/agentbay"
)
func main() {
	client, err := agentbay.NewAgentBay(os.Getenv("AGENTBAY_API_KEY"), nil)
	if err != nil {
		fmt.Printf("Error: %v\n", err)
		os.Exit(1)
	}
	result, err := client.Create(nil)
	if err != nil {

		// Log operation errors

		agentbay.LogOperationError("Create Session", err.Error(), false)
		os.Exit(1)
	}
	session := result.Session
	defer session.Delete()

	// Output: ❌ Failed: Create Session

	// Output: 💥 Error: session creation failed

}
```

### MaskSensitiveData

```go
func MaskSensitiveData(data interface{}) interface{}
```

MaskSensitiveData recursively masks sensitive information in data structures

**Example:**

```go
package main
import (
	"fmt"
	"github.com/aliyun/wuying-agentbay-sdk/golang/pkg/agentbay"
)
func main() {

	// Create data with sensitive information

	data := map[string]interface{}{
		"api_key":    "sk_live_1234567890",
		"password":   "secret123",
		"auth_token": "Bearer xyz",
		"username":   "john_doe",
	}

	// Mask sensitive data

	masked := agentbay.MaskSensitiveData(data)
	fmt.Printf("Masked data: %v\n", masked)

	// Output: Masked data: map[api_key:sk****90 auth_token:Be****yz password:se****23 username:john_doe]

}
```

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

**Example:**

```go
package main
import (
	"fmt"
	"os"
	"github.com/aliyun/wuying-agentbay-sdk/golang/pkg/agentbay"
)
func main() {

	// Set log level to DEBUG to see all messages

	agentbay.SetLogLevel(agentbay.LOG_DEBUG)
	client, err := agentbay.NewAgentBay(os.Getenv("AGENTBAY_API_KEY"), nil)
	if err != nil {
		fmt.Printf("Error: %v\n", err)
		os.Exit(1)
	}
	result, err := client.Create(nil)
	if err != nil {
		fmt.Printf("Error: %v\n", err)
		os.Exit(1)
	}
	session := result.Session
	defer session.Delete()

	// Change to INFO level to reduce verbosity

	agentbay.SetLogLevel(agentbay.LOG_INFO)

	// Continue with your operations

}
```

### SetupLogger

```go
func SetupLogger(config LoggerConfig)
```

SetupLogger configures the logger with file logging support

**Example:**

```go
package main
import (
	"fmt"
	"os"
	"github.com/aliyun/wuying-agentbay-sdk/golang/pkg/agentbay"
)
func main() {

	// Configure file logging with rotation

	agentbay.SetupLogger(agentbay.LoggerConfig{
		Level:       "DEBUG",
		LogFile:     "/tmp/agentbay.log",
		MaxFileSize: "100 MB",
	})
	client, err := agentbay.NewAgentBay(os.Getenv("AGENTBAY_API_KEY"), nil)
	if err != nil {
		fmt.Printf("Error: %v\n", err)
		os.Exit(1)
	}
	result, err := client.Create(nil)
	if err != nil {
		fmt.Printf("Error: %v\n", err)
		os.Exit(1)
	}
	session := result.Session
	defer session.Delete()

	// All logs will be written to both console and file

}
```

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
