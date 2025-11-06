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

### Related Functions

#### parseDirectoryListing

```go
func parseDirectoryListing(text string) ([]*DirectoryEntry, error)
```

Helper function to parse directory listing from string

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

#### ToDict

```go
func (e *FileChangeEvent) ToDict() map[string]string
```

ToDict converts FileChangeEvent to map

### Related Functions

#### FileChangeEventFromDict

```go
func FileChangeEventFromDict(data map[string]interface{}) *FileChangeEvent
```

FileChangeEventFromDict creates FileChangeEvent from map

#### parseFileChangeData

```go
func parseFileChangeData(rawData string) ([]*FileChangeEvent, error)
```

parseFileChangeData parses raw JSON data into FileChangeEvent slice

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

### Related Functions

#### parseFileInfo

```go
func parseFileInfo(fileInfoStr string) (*FileInfo, error)
```

Helper function to parse file info from string

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

#### EditFile

```go
func (fs *FileSystem) EditFile(path string, edits []map[string]string, dryRun bool) (*FileWriteResult, error)
```

EditFile edits a file with specified changes.

#### GetFileChange

```go
func (fs *FileSystem) GetFileChange(path string) (*FileChangeResult, error)
```

GetFileChange gets file change information for the specified directory path

#### GetFileInfo

```go
func (fs *FileSystem) GetFileInfo(path string) (*FileInfoResult, error)
```

GetFileInfo gets information about a file or directory.

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

Example:


package main


import (

	"fmt"

	"github.com/aliyun/wuying-agentbay-sdk/golang/pkg/agentbay"

)


func main() {

	client, err := agentbay.NewAgentBay("your_api_key")

	if err != nil {

		panic(err)

	}


	result, err := client.Create(nil)

	if err != nil {

		panic(err)

	}


	session := result.Session


	// List directory contents

	listResult, err := session.FileSystem.ListDirectory("/tmp")

	if err != nil {

		panic(err)

	}


	for _, entry := range listResult.Entries {

		fmt.Printf("%s (%s)\n", entry.Name, entry.Type)

	}

	// Output:

	// test.txt (file)

	// subdir (directory)


	session.Delete()

}

#### MoveFile

```go
func (fs *FileSystem) MoveFile(source, destination string) (*FileWriteResult, error)
```

MoveFile moves a file or directory from source to destination.

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

Example:


package main


import (

	"fmt"

	"github.com/aliyun/wuying-agentbay-sdk/golang/pkg/agentbay"

)


func main() {

	client, err := agentbay.NewAgentBay("your_api_key")

	if err != nil {

		panic(err)

	}


	result, err := client.Create(nil)

	if err != nil {

		panic(err)

	}


	session := result.Session


	// Read a text file

	fileResult, err := session.FileSystem.ReadFile("/etc/hostname")

	if err != nil {

		panic(err)

	}


	fmt.Printf("Content: %s\n", fileResult.Content)

	// Output: Content: agentbay-session-xyz


	session.Delete()

}

#### ReadMultipleFiles

```go
func (fs *FileSystem) ReadMultipleFiles(paths []string) (map[string]string, error)
```

ReadMultipleFiles reads multiple files and returns their contents as a map.

#### SearchFiles

```go
func (fs *FileSystem) SearchFiles(path, pattern string, excludePatterns []string) (*SearchFilesResult, error)
```

SearchFiles searches for files matching a pattern.

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
occur

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

Example:


package main


import (

	"fmt"

	"github.com/aliyun/wuying-agentbay-sdk/golang/pkg/agentbay"

)


func main() {

	client, err := agentbay.NewAgentBay("your_api_key")

	if err != nil {

		panic(err)

	}


	result, err := client.Create(nil)

	if err != nil {

		panic(err)

	}


	session := result.Session


	// Write to a file

	writeResult, err := session.FileSystem.WriteFile(

		"/tmp/test.txt",

		"Hello, AgentBay!",

		"overwrite",

	)

	if err != nil {

		panic(err)

	}


	if writeResult.Success {

		fmt.Println("File written successfully")

		// Output: File written successfully

	}


	session.Delete()

}

#### readFileChunk

```go
func (fs *FileSystem) readFileChunk(path string, optionalParams ...int) (*FileReadResult, error)
```

readFileChunk reads a file chunk. Internal method used for chunked file operations.

#### writeFileChunk

```go
func (fs *FileSystem) writeFileChunk(path, content string, mode string) (*FileWriteResult, error)
```

writeFileChunk writes a file chunk. Internal method used for chunked file operations.

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
