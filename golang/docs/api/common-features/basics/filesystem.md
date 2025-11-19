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

### String

```go
func (e *FileChangeEvent) String() string
```

String returns string representation of FileChangeEvent

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

### GetCreatedFiles

```go
func (r *FileChangeResult) GetCreatedFiles() []string
```

GetCreatedFiles returns list of created file paths

### GetDeletedFiles

```go
func (r *FileChangeResult) GetDeletedFiles() []string
```

GetDeletedFiles returns list of deleted file paths

### GetModifiedFiles

```go
func (r *FileChangeResult) GetModifiedFiles() []string
```

GetModifiedFiles returns list of modified file paths

### HasChanges

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

### CreateDirectory

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
client, _ := agentbay.NewAgentBay(os.Getenv("AGENTBAY_API_KEY"), nil)
result, _ := client.Create(nil)
defer result.Session.Delete()
createResult, _ := result.Session.FileSystem.CreateDirectory("/tmp/test_directory")
```

### EditFile

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
client, _ := agentbay.NewAgentBay(os.Getenv("AGENTBAY_API_KEY"), nil)
result, _ := client.Create(nil)
defer result.Session.Delete()
result.Session.FileSystem.WriteFile("/tmp/test.txt", "Hello World", "overwrite")
edits := []map[string]string{{"oldText": "Hello", "newText": "Hi"}}
editResult, _ := result.Session.FileSystem.EditFile("/tmp/test.txt", edits, false)
```

### GetFileChange

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
client, _ := agentbay.NewAgentBay(os.Getenv("AGENTBAY_API_KEY"), nil)
result, _ := client.Create(nil)
defer result.Session.Delete()
result.Session.FileSystem.CreateDirectory("/tmp/watch_test")
result.Session.FileSystem.GetFileChange("/tmp/watch_test")
result.Session.FileSystem.WriteFile("/tmp/watch_test/file.txt", "content", "overwrite")
changeResult, _ := result.Session.FileSystem.GetFileChange("/tmp/watch_test")
```

### GetFileInfo

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
client, _ := agentbay.NewAgentBay(os.Getenv("AGENTBAY_API_KEY"), nil)
result, _ := client.Create(nil)
defer result.Session.Delete()
fileInfo, _ := result.Session.FileSystem.GetFileInfo("/etc/hostname")
```

### ListDirectory

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
client, _ := agentbay.NewAgentBay(os.Getenv("AGENTBAY_API_KEY"), nil)
result, _ := client.Create(nil)
defer result.Session.Delete()
listResult, _ := result.Session.FileSystem.ListDirectory("/tmp")
```

### MoveFile

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
client, _ := agentbay.NewAgentBay(os.Getenv("AGENTBAY_API_KEY"), nil)
result, _ := client.Create(nil)
defer result.Session.Delete()
result.Session.FileSystem.WriteFile("/tmp/old.txt", "content", "overwrite")
moveResult, _ := result.Session.FileSystem.MoveFile("/tmp/old.txt", "/tmp/new.txt")
```

### ReadFile

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
client, _ := agentbay.NewAgentBay(os.Getenv("AGENTBAY_API_KEY"), nil)
result, _ := client.Create(nil)
defer result.Session.Delete()
fileResult, _ := result.Session.FileSystem.ReadFile("/etc/hostname")
```

### ReadMultipleFiles

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
client, _ := agentbay.NewAgentBay(os.Getenv("AGENTBAY_API_KEY"), nil)
result, _ := client.Create(nil)
defer result.Session.Delete()
paths := []string{"/etc/hostname", "/etc/os-release"}
contents, _ := result.Session.FileSystem.ReadMultipleFiles(paths)
```

### SearchFiles

```go
func (fs *FileSystem) SearchFiles(path, pattern string, excludePatterns []string) (*SearchFilesResult, error)
```

SearchFiles searches for files matching a wildcard pattern.

Parameters:
  - path: Absolute path to the directory to search in
  - pattern: Wildcard pattern to match against file names. Supports * (any characters) and ? (single
    character). Examples: "*.txt", "test_*", "*config*"
  - excludePatterns: Array of wildcard patterns to exclude from results

Returns:
  - *SearchFilesResult: Result containing matching file paths and request ID
  - error: Error if the operation fails

Behavior:

- Recursively searches the directory and subdirectories - Supports wildcard patterns for matching -
Exclude patterns help filter out unwanted results

**Example:**

```go
client, _ := agentbay.NewAgentBay(os.Getenv("AGENTBAY_API_KEY"), nil)
result, _ := client.Create(nil)
defer result.Session.Delete()
searchResult, _ := result.Session.FileSystem.SearchFiles("/tmp", "*.txt", []string{})
```

### WatchDirectory

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
client, _ := agentbay.NewAgentBay(os.Getenv("AGENTBAY_API_KEY"), nil)
result, _ := client.Create(nil)
defer result.Session.Delete()
result.Session.FileSystem.CreateDirectory("/tmp/watch")
stopCh := make(chan struct{})
wg := result.Session.FileSystem.WatchDirectory("/tmp/watch", func(events []*filesystem.FileChangeEvent) {}, 1*time.Second, stopCh)
close(stopCh)
wg.Wait()
```

### WatchDirectoryWithDefaults

```go
func (fs *FileSystem) WatchDirectoryWithDefaults(
	path string,
	callback func([]*FileChangeEvent),
	stopCh <-chan struct{},
) *sync.WaitGroup
```

WatchDirectoryWithDefaults watches a directory for file changes with default 500ms polling interval

### WriteFile

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
client, _ := agentbay.NewAgentBay(os.Getenv("AGENTBAY_API_KEY"), nil)
result, _ := client.Create(nil)
defer result.Session.Delete()
writeResult, _ := result.Session.FileSystem.WriteFile("/tmp/test.txt", "Hello", "overwrite")
```

### Related Functions

### NewFileSystem

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
