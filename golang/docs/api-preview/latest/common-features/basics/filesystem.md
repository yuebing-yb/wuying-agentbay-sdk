# File System API Reference

## 📁 Related Tutorial

- [File Operations Guide](../../../../../docs/guides/common-features/basics/file-operations.md) - Complete guide to file system operations

## Type DirectoryEntry

```go
type DirectoryEntry struct {
	Name		string	`json:"name"`
	IsDirectory	bool	`json:"isDirectory"`
}
```

DirectoryEntry represents a directory entry

## Type DirectoryListResult

```go
type DirectoryListResult struct {
	models.ApiResponse
	Entries	[]*DirectoryEntry
}
```

DirectoryListResult wraps directory listing result and RequestID

## Type FileChangeEvent

```go
type FileChangeEvent struct {
	EventType	string	`json:"eventType"`	// "create", "modify", "delete"
	Path		string	`json:"path"`
	PathType	string	`json:"pathType"`	// "file", "directory"
}
```

FileChangeEvent represents a single file change event

### Methods

#### String

```go
func (e *FileChangeEvent) String() string
```

String returns string representation of FileChangeEvent

### Related Functions

#### FileChangeEventFromDict

```go
func FileChangeEventFromDict(data map[string]interface{}) *FileChangeEvent
```

FileChangeEventFromDict creates FileChangeEvent from map

## Type FileChangeResult

```go
type FileChangeResult struct {
	models.ApiResponse
	Events	[]*FileChangeEvent
	RawData	string
}
```

FileChangeResult wraps file change detection result

### Methods

#### GetCreatedFiles

```go
func (r *FileChangeResult) GetCreatedFiles() []string
```

GetCreatedFiles returns list of created file paths

#### GetDeletedFiles

```go
func (r *FileChangeResult) GetDeletedFiles() []string
```

GetDeletedFiles returns list of deleted file paths

#### GetModifiedFiles

```go
func (r *FileChangeResult) GetModifiedFiles() []string
```

GetModifiedFiles returns list of modified file paths

#### HasChanges

```go
func (r *FileChangeResult) HasChanges() bool
```

HasChanges checks if there are any file changes

## Type FileDirectoryResult

```go
type FileDirectoryResult struct {
	models.ApiResponse	// Embedded ApiResponse
	Success			bool
}
```

FileDirectoryResult wraps directory operation result and RequestID

## Type FileExistsResult

```go
type FileExistsResult struct {
	models.ApiResponse
	Exists	bool
}
```

FileExistsResult wraps file existence check result and RequestID

## Type FileInfo

```go
type FileInfo struct {
	Name		string	`json:"name"`
	Path		string	`json:"path"`
	Size		int64	`json:"size"`
	IsDirectory	bool	`json:"isDirectory"`
	ModTime		string	`json:"modTime"`
	Mode		string	`json:"mode"`
	Owner		string	`json:"owner,omitempty"`
	Group		string	`json:"group,omitempty"`
}
```

FileInfo represents file or directory information

## Type FileInfoResult

```go
type FileInfoResult struct {
	models.ApiResponse
	FileInfo	*FileInfo
}
```

FileInfoResult wraps file info result and RequestID

## Type FileReadResult

```go
type FileReadResult struct {
	models.ApiResponse	// Embedded ApiResponse
	Content			string
}
```

FileReadResult wraps file read operation result and RequestID

## Type FileSystem

```go
type FileSystem struct {
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

FileSystem handles file system operations in the AgentBay cloud environment.

### Methods

#### CreateDirectory

```go
func (fs *FileSystem) CreateDirectory(path string) (*FileDirectoryResult, error)
```

CreateDirectory creates a new directory.

Parameters:
  - path: Absolute path to the directory to create

Returns:
  - *FileDirectoryResult: Result containing success status and request ID
  - error: Error if the operation fails

Behavior:

- Creates the directory and any necessary parent directories - Fails if the directory already exists
- Returns success if the directory is created successfully

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

	// Create a directory

	createResult, err := session.FileSystem.CreateDirectory("/tmp/test_directory")
	if err != nil {
		fmt.Printf("Error: %v\n", err)
		os.Exit(1)
	}
	if createResult.Success {
		fmt.Println("Directory created successfully")

		// Output: Directory created successfully

	}
	session.Delete()
}
```

#### EditFile

```go
func (fs *FileSystem) EditFile(path string, edits []map[string]string, dryRun bool) (*FileWriteResult, error)
```

EditFile edits a file with specified changes.

Parameters:
  - path: Absolute path to the file to edit
  - edits: Array of edit operations, each containing "oldText" and "newText" keys
  - dryRun: If true, preview changes without applying them

Returns:
  - *FileWriteResult: Result containing success status and request ID
  - error: Error if the operation fails

Behavior:

- Performs find-and-replace operations on the file content - In dry-run mode, shows what changes
would be made without applying them - All edits are applied sequentially in the order provided

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

	// First write a file

	_, err = session.FileSystem.WriteFile("/tmp/test.txt", "Hello, World!", "overwrite")
	if err != nil {
		fmt.Printf("Error: %v\n", err)
		os.Exit(1)
	}

	// Edit the file

	edits := []map[string]string{
		{"oldText": "World", "newText": "AgentBay"},
	}
	editResult, err := session.FileSystem.EditFile("/tmp/test.txt", edits, false)
	if err != nil {
		fmt.Printf("Error: %v\n", err)
		os.Exit(1)
	}
	if editResult.Success {
		fmt.Println("File edited successfully")

		// Output: File edited successfully

	}
	session.Delete()
}
```

#### GetFileChange

```go
func (fs *FileSystem) GetFileChange(path string) (*FileChangeResult, error)
```

GetFileChange gets file change information for the specified directory path.

Parameters:
  - path: Absolute path to the directory to monitor

Returns:
  - *FileChangeResult: Result containing detected file changes and request ID
  - error: Error if the operation fails

Behavior:

- Detects file changes (create, modify, delete) since the last check - Returns empty Events array if
no changes detected - Automatically tracks the last checked state for the directory

**Example:**

```go
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

	// Create a test directory

	_, err = session.FileSystem.CreateDirectory("/tmp/watch_test")
	if err != nil {
		fmt.Printf("Error: %v\n", err)
		os.Exit(1)
	}

	// Initial check to establish baseline

	_, err = session.FileSystem.GetFileChange("/tmp/watch_test")
	if err != nil {
		fmt.Printf("Error: %v\n", err)
		os.Exit(1)
	}

	// Create a new file

	_, err = session.FileSystem.WriteFile("/tmp/watch_test/test.txt", "content", "overwrite")
	if err != nil {
		fmt.Printf("Error: %v\n", err)
		os.Exit(1)
	}

	// Wait a bit for changes to be detected

	time.Sleep(1 * time.Second)

	// Check for changes

	changeResult, err := session.FileSystem.GetFileChange("/tmp/watch_test")
	if err != nil {
		fmt.Printf("Error: %v\n", err)
		os.Exit(1)
	}
	if changeResult.HasChanges() {
		fmt.Printf("Detected %d changes\n", len(changeResult.Events))
		for _, event := range changeResult.Events {
			fmt.Println(event.String())
		}
	}
	session.Delete()
}
```

#### GetFileInfo

```go
func (fs *FileSystem) GetFileInfo(path string) (*FileInfoResult, error)
```

GetFileInfo gets information about a file or directory.

Parameters:
  - path: Absolute path to the file or directory

Returns:
  - *FileInfoResult: Result containing file information and request ID
  - error: Error if the operation fails

Behavior:

- Returns detailed information including size, permissions, modification time - Works for both files
and directories - Fails if the path doesn't exist

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

	// Get file information

	fileInfo, err := session.FileSystem.GetFileInfo("/etc/hostname")
	if err != nil {
		fmt.Printf("Error: %v\n", err)
		os.Exit(1)
	}
	fmt.Printf("File size: %d bytes\n", fileInfo.FileInfo.Size)
	fmt.Printf("Is directory: %t\n", fileInfo.FileInfo.IsDirectory)

	// Output: File size: 16 bytes

	// Output: Is directory: false

	session.Delete()
}
```

#### ListDirectory

```go
func (fs *FileSystem) ListDirectory(path string) (*DirectoryListResult, error)
```

ListDirectory lists the contents of a directory. ListDirectory lists all files and directories in a
directory.

Parameters:
  - path: Absolute path to the directory to list

Returns:
  - *DirectoryListResult: Result containing list of entries and request ID
  - error: Error if the operation fails

Behavior:

- Returns list of DirectoryEntry objects with name, type, size, and mtime - Entry types: "file" or
"directory" - Fails if path doesn't exist or is not a directory

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

	// List directory contents

	listResult, err := session.FileSystem.ListDirectory("/tmp")
	if err != nil {
		fmt.Printf("Error: %v\n", err)
		os.Exit(1)
	}
	for _, entry := range listResult.Entries {
		entryType := "file"
		if entry.IsDirectory {
			entryType = "directory"
		}
		fmt.Printf("%s (%s)\n", entry.Name, entryType)
	}

	// Output:

	// test.txt (file)

	// subdir (directory)

	session.Delete()
}
```

#### MoveFile

```go
func (fs *FileSystem) MoveFile(source, destination string) (*FileWriteResult, error)
```

MoveFile moves a file or directory from source to destination.

Parameters:
  - source: Absolute path to the source file or directory
  - destination: Absolute path to the destination

Returns:
  - *FileWriteResult: Result containing success status and request ID
  - error: Error if the operation fails

Behavior:

- Moves files or directories to a new location - Can be used to rename files/directories - Fails if
source doesn't exist or destination already exists

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

	// First create a file

	_, err = session.FileSystem.WriteFile("/tmp/old_name.txt", "test content", "overwrite")
	if err != nil {
		fmt.Printf("Error: %v\n", err)
		os.Exit(1)
	}

	// Move/rename the file

	moveResult, err := session.FileSystem.MoveFile("/tmp/old_name.txt", "/tmp/new_name.txt")
	if err != nil {
		fmt.Printf("Error: %v\n", err)
		os.Exit(1)
	}
	if moveResult.Success {
		fmt.Println("File moved successfully")

		// Output: File moved successfully

	}
	session.Delete()
}
```

#### ReadFile

```go
func (fs *FileSystem) ReadFile(path string) (*FileReadResult, error)
```

ReadFile reads the contents of a file. Automatically handles large files by chunking. ReadFile reads
the entire content of a file.

Parameters:
  - path: Absolute path to the file to read

Returns:
  - *FileReadResult: Result containing file content and request ID
  - error: Error if the operation fails

Behavior:

- Automatically handles large files by reading in 50KB chunks - Returns empty string for empty files
- Fails if path is a directory or doesn't exist

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

	// Read a text file

	fileResult, err := session.FileSystem.ReadFile("/etc/hostname")
	if err != nil {
		fmt.Printf("Error: %v\n", err)
		os.Exit(1)
	}
	fmt.Printf("Content: %s\n", fileResult.Content)

	// Output: Content: agentbay-session-xyz

	session.Delete()
}
```

#### ReadMultipleFiles

```go
func (fs *FileSystem) ReadMultipleFiles(paths []string) (map[string]string, error)
```

ReadMultipleFiles reads multiple files and returns their contents as a map.

Parameters:
  - paths: Array of absolute paths to files to read

Returns:
  - map[string]string: Map with file paths as keys and their contents as values
  - error: Error if the operation fails

Behavior:

- Reads multiple files in a single operation - Returns a map with paths as keys and file contents as
values - Fails if any of the specified files don't exist

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

	// Read multiple files at once

	contents, err := session.FileSystem.ReadMultipleFiles([]string{
		"/etc/hostname",
		"/etc/os-release",
	})
	if err != nil {
		fmt.Printf("Error: %v\n", err)
		os.Exit(1)
	}
	for path, content := range contents {
		fmt.Printf("%s: %d bytes\n", path, len(content))
	}
	session.Delete()
}
```

#### SearchFiles

```go
func (fs *FileSystem) SearchFiles(path, pattern string, excludePatterns []string) (*SearchFilesResult, error)
```

SearchFiles searches for files matching a pattern.

Parameters:
  - path: Absolute path to the directory to search in
  - pattern: Pattern to match (supports wildcards like *.txt)
  - excludePatterns: Array of patterns to exclude from results

Returns:
  - *SearchFilesResult: Result containing matching file paths and request ID
  - error: Error if the operation fails

Behavior:

- Recursively searches the directory and subdirectories - Supports glob patterns for matching -
Exclude patterns help filter out unwanted results

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

	// Search for all .txt files (using partial name matching, NOT wildcards)

	searchResult, err := session.FileSystem.SearchFiles(
		"/tmp",
		".txt",
		[]string{"node_modules"},
	)
	if err != nil {
		fmt.Printf("Error: %v\n", err)
		os.Exit(1)
	}
	fmt.Printf("Found %d files\n", len(searchResult.Results))
	for _, file := range searchResult.Results {
		fmt.Println(file)
	}
	session.Delete()
}
```

#### WatchDirectory

```go
func (fs *FileSystem) WatchDirectory(
	path string,
	callback func([]*FileChangeEvent),
	interval time.Duration,
	stopCh <-chan struct{},
) *sync.WaitGroup
```

WatchDirectory watches a directory for file changes and calls the callback function when changes
occur.

Parameters:
  - path: Absolute path to the directory to watch
  - callback: Function called when changes are detected, receives array of FileChangeEvent
  - interval: Polling interval (e.g., 1*time.Second for 1 second)
  - stopCh: Channel to signal when to stop watching

Returns:
  - *sync.WaitGroup: WaitGroup that can be used to wait for monitoring to stop

Behavior:

- Continuously monitors directory for file changes at specified interval - Calls callback function
asynchronously when changes detected - Stops monitoring when stopCh is closed

**Example:**

```go
package main
import (
	"fmt"
	"os"
	"time"
	"github.com/aliyun/wuying-agentbay-sdk/golang/pkg/agentbay"
	"github.com/aliyun/wuying-agentbay-sdk/golang/pkg/agentbay/filesystem"
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

	// Create test directory

	_, err = session.FileSystem.CreateDirectory("/tmp/watch_demo")
	if err != nil {
		fmt.Printf("Error: %v\n", err)
		os.Exit(1)
	}

	// Define callback function

	callback := func(events []*filesystem.FileChangeEvent) {
		fmt.Printf("Detected %d changes:\n", len(events))
		for _, event := range events {
			fmt.Println(event.String())
		}
	}

	// Create stop channel

	stopCh := make(chan struct{})

	// Start watching with 1 second interval

	wg := session.FileSystem.WatchDirectory(
		"/tmp/watch_demo",
		callback,
		1*time.Second,
		stopCh,
	)

	// Simulate file operations

	time.Sleep(2 * time.Second)
	session.FileSystem.WriteFile("/tmp/watch_demo/test.txt", "content", "overwrite")

	// Wait for changes to be detected

	time.Sleep(2 * time.Second)

	// Stop monitoring

	close(stopCh)
	wg.Wait()
	fmt.Println("Monitoring stopped")
	session.Delete()
}
```

#### WatchDirectoryWithDefaults

```go
func (fs *FileSystem) WatchDirectoryWithDefaults(
	path string,
	callback func([]*FileChangeEvent),
	stopCh <-chan struct{},
) *sync.WaitGroup
```

WatchDirectoryWithDefaults watches a directory for file changes with default 500ms polling interval

#### WriteFile

```go
func (fs *FileSystem) WriteFile(path, content string, mode string) (*FileWriteResult, error)
```

WriteFile writes content to a file. Automatically handles large files by chunking. WriteFile writes
content to a file.

Parameters:
  - path: Absolute path to the file to write
  - content: Content to write to the file
  - mode: Write mode ("overwrite" or "append")

Returns:
  - *FileWriteResult: Result containing success status and request ID
  - error: Error if the operation fails

Behavior:

- Automatically handles large content by writing in 50KB chunks - Creates parent directories if they
don't exist - "overwrite" mode replaces existing file content - "append" mode adds to existing file
content

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

	// Write to a file

	writeResult, err := session.FileSystem.WriteFile(
		"/tmp/test.txt",
		"Hello, AgentBay!",
		"overwrite",
	)
	if err != nil {
		fmt.Printf("Error: %v\n", err)
		os.Exit(1)
	}
	if writeResult.Success {
		fmt.Println("File written successfully")

		// Output: File written successfully

	}
	session.Delete()
}
```

### Related Functions

#### NewFileSystem

```go
func NewFileSystem(session interface {
	GetAPIKey() string
	GetClient() *mcp.Client
	GetSessionId() string
	IsVpc() bool
	NetworkInterfaceIp() string
	HttpPort() string
	FindServerForTool(toolName string) string
	CallMcpTool(toolName string, args interface{}, autoGenSession ...bool) (*models.McpToolResult, error)
}) *FileSystem
```

NewFileSystem creates a new FileSystem instance

## Type FileWriteResult

```go
type FileWriteResult struct {
	models.ApiResponse	// Embedded ApiResponse
	Success			bool
}
```

FileWriteResult wraps file write operation result and RequestID

## Type SearchFilesResult

```go
type SearchFilesResult struct {
	models.ApiResponse
	Results	[]string
}
```

SearchFilesResult wraps file search result and RequestID

## Related Resources

- [Session API Reference](session.md)
- [Command API Reference](command.md)

---

*Documentation generated automatically from Go source code.*
