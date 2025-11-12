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
