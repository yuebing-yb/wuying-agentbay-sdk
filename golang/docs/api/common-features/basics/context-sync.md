# Context Sync API Reference

## 🚀 Related Tutorial

- [First Session Tutorial](../../../../../docs/quickstart/first-session.md) - Get started with creating your first AgentBay session

## Type ContextSync

```go
type ContextSync struct {
	// ContextID is the ID of the context to synchronize
	ContextID	string	`json:"contextId"`
	// Path is the path where the context should be mounted
	Path	string	`json:"path"`
	// Policy defines the synchronization policy
	Policy	*SyncPolicy	`json:"policy,omitempty"`
}
```

ContextSync defines the context synchronization configuration

### Methods

#### WithPolicy

```go
func (cs *ContextSync) WithPolicy(policy *SyncPolicy) (*ContextSync, error)
```

WithPolicy sets the policy and returns the context sync for chaining

### Related Functions

#### NewContextSync

```go
func NewContextSync(contextID, path string, policy *SyncPolicy) (*ContextSync, error)
```

NewContextSync creates a new context sync configuration

## Type SyncPolicy

```go
type SyncPolicy struct {
	// UploadPolicy defines the upload policy
	UploadPolicy	*UploadPolicy	`json:"uploadPolicy,omitempty"`
	// DownloadPolicy defines the download policy
	DownloadPolicy	*DownloadPolicy	`json:"downloadPolicy,omitempty"`
	// DeletePolicy defines the delete policy
	DeletePolicy	*DeletePolicy	`json:"deletePolicy,omitempty"`
	// ExtractPolicy defines the extract policy
	ExtractPolicy	*ExtractPolicy	`json:"extractPolicy,omitempty"`
	// RecyclePolicy defines the recycle policy
	RecyclePolicy	*RecyclePolicy	`json:"recyclePolicy,omitempty"`
	// BWList defines the black and white list
	BWList	*BWList	`json:"bwList,omitempty"`
	// MappingPolicy defines the mapping policy for cross-platform context synchronization
	MappingPolicy	*MappingPolicy	`json:"mappingPolicy,omitempty"`
}
```

SyncPolicy defines the synchronization policy

### Related Functions

#### NewSyncPolicy

```go
func NewSyncPolicy() *SyncPolicy
```

NewSyncPolicy creates a new sync policy with default values

## Type UploadPolicy

```go
type UploadPolicy struct {
	// AutoUpload enables automatic upload
	AutoUpload	bool	`json:"autoUpload"`
	// UploadStrategy defines the upload strategy
	UploadStrategy	UploadStrategy	`json:"uploadStrategy"`
	// UploadMode defines the upload mode
	UploadMode	UploadMode	`json:"uploadMode"`
}
```

UploadPolicy defines the upload policy for context synchronization

### Related Functions

#### NewUploadPolicy

```go
func NewUploadPolicy() *UploadPolicy
```

NewUploadPolicy creates a new upload policy with default values

## Type DownloadPolicy

```go
type DownloadPolicy struct {
	// AutoDownload enables automatic download
	AutoDownload	bool	`json:"autoDownload"`
	// DownloadStrategy defines the download strategy
	DownloadStrategy	DownloadStrategy	`json:"downloadStrategy"`
}
```

DownloadPolicy defines the download policy for context synchronization

### Related Functions

#### NewDownloadPolicy

```go
func NewDownloadPolicy() *DownloadPolicy
```

NewDownloadPolicy creates a new download policy with default values

## Type DeletePolicy

```go
type DeletePolicy struct {
	// SyncLocalFile enables synchronization of local file deletions
	SyncLocalFile bool `json:"syncLocalFile"`
}
```

DeletePolicy defines the delete policy for context synchronization

### Related Functions

#### NewDeletePolicy

```go
func NewDeletePolicy() *DeletePolicy
```

NewDeletePolicy creates a new delete policy with default values

## Type ExtractPolicy

```go
type ExtractPolicy struct {
	// Extract enables file extraction
	Extract	bool	`json:"extract"`
	// DeleteSrcFile enables deletion of source file after extraction
	DeleteSrcFile	bool	`json:"deleteSrcFile"`
	// ExtractToCurrentFolder enables extraction to current folder
	ExtractToCurrentFolder	bool	`json:"extractToCurrentFolder"`
}
```

ExtractPolicy defines the extract policy for context synchronization

### Related Functions

#### NewExtractPolicy

```go
func NewExtractPolicy() *ExtractPolicy
```

NewExtractPolicy creates a new extract policy with default values

## Type RecyclePolicy

```go
type RecyclePolicy struct {
	// Lifecycle defines how long the context data should be retained
	Lifecycle	Lifecycle	`json:"lifecycle"`
	// Paths specifies which directories or files should be subject to the recycle policy
	Paths	[]string	`json:"paths"`
}
```

RecyclePolicy defines the recycle policy for context synchronization

The RecyclePolicy determines how long context data should be retained and which paths are subject to
the policy.

Lifecycle field determines the data retention period:
  - Lifecycle1Day: Keep data for 1 day
  - Lifecycle3Days: Keep data for 3 days
  - Lifecycle5Days: Keep data for 5 days
  - Lifecycle10Days: Keep data for 10 days
  - Lifecycle15Days: Keep data for 15 days
  - Lifecycle30Days: Keep data for 30 days
  - Lifecycle90Days: Keep data for 90 days
  - Lifecycle180Days: Keep data for 180 days
  - Lifecycle360Days: Keep data for 360 days
  - LifecycleForever: Keep data permanently (default)

Paths field specifies which directories or files should be subject to the recycle policy:
  - Must use exact directory/file paths
  - Wildcard patterns (* ? [ ]) are NOT supported
  - Empty string "" means apply to all paths in the context
  - Multiple paths can be specified as a slice
  - Default: []string{""} (applies to all paths)

### Related Functions

#### NewRecyclePolicy

```go
func NewRecyclePolicy() *RecyclePolicy
```

NewRecyclePolicy creates a new recycle policy with default values

## Type WhiteList

```go
type WhiteList struct {
	// Path is the path to include in the white list
	Path	string	`json:"path"`
	// ExcludePaths are the paths to exclude from the white list
	ExcludePaths	[]string	`json:"excludePaths,omitempty"`
}
```

WhiteList defines the white list configuration

## Type BWList

```go
type BWList struct {
	// WhiteLists defines the white lists
	WhiteLists []*WhiteList `json:"whiteLists,omitempty"`
}
```

BWList defines the black and white list configuration

## Type MappingPolicy

```go
type MappingPolicy struct {
	// Path is the original path from a different OS that should be mapped to the current context path
	Path string `json:"path"`
}
```

MappingPolicy defines the mapping policy for cross-platform context synchronization

### Related Functions

#### NewMappingPolicy

```go
func NewMappingPolicy() *MappingPolicy
```

NewMappingPolicy creates a new mapping policy with default values

## Type UploadStrategy

```go
type UploadStrategy string
```

UploadStrategy defines the upload strategy for context synchronization

## Type DownloadStrategy

```go
type DownloadStrategy string
```

DownloadStrategy defines the download strategy for context synchronization

## Type UploadMode

```go
type UploadMode string
```

UploadMode defines the upload mode for context synchronization

## Type Lifecycle

```go
type Lifecycle string
```

Lifecycle defines the lifecycle options for recycle policy

## Functions

### Deprecated

```go
func Deprecated(reason, replacement, version string)
```

Deprecated marks a function or method as deprecated and emits a warning

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

## Related Resources

- [Session API Reference](session.md)
- [Context API Reference](context.md)

---

*Documentation generated automatically from Go source code.*
