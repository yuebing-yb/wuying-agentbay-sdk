# FileSystem Class API Reference

The `FileSystem` class provides methods for file operations within a session in the AgentBay cloud environment. This includes reading, writing, editing, and searching files, as well as directory operations.

## Methods

### create_directory / createDirectory / CreateDirectory

Creates a new directory at the specified path.

#### TypeScript

```typescript
createDirectory(path: string): Promise<boolean>
```

**Parameters:**
- `path` (string): The path of the directory to create.

**Returns:**
- `Promise<boolean>`: A promise that resolves to true if the directory was created successfully.

**Throws:**
- `APIError`: If the directory creation fails.

#### Golang

```go
CreateDirectory(path string) (bool, error)
```

**Parameters:**
- `path` (string): The path of the directory to create.

**Returns:**
- `bool`: True if the directory was created successfully.
- `error`: An error if the directory creation fails.

### edit_file / editFile / EditFile

Edits a file by replacing occurrences of oldText with newText.

#### TypeScript

```typescript
editFile(path: string, edits: Array<{oldText: string, newText: string}>, dryRun?: boolean): Promise<boolean>
```

**Parameters:**
- `path` (string): The path of the file to edit.
- `edits` (Array<{oldText: string, newText: string}>): Array of edit operations, each containing oldText and newText.
- `dryRun` (boolean, optional): If true, preview changes without applying them. Default is false.

**Returns:**
- `Promise<boolean>`: A promise that resolves to true if the file was edited successfully.

**Throws:**
- `APIError`: If the file editing fails.

#### Golang

```go
EditFile(path string, edits []map[string]string, dryRun bool) (bool, error)
```

**Parameters:**
- `path` (string): The path of the file to edit.
- `edits` ([]map[string]string): Array of edit operations, each containing oldText and newText.
- `dryRun` (bool): If true, preview changes without applying them.

**Returns:**
- `bool`: True if the file was edited successfully.
- `error`: An error if the file editing fails.

### get_file_info / getFileInfo / GetFileInfo

Gets information about a file or directory.

#### TypeScript

```typescript
getFileInfo(path: string): Promise<Record<string, any>>
```

**Parameters:**
- `path` (string): The path of the file or directory to inspect.

**Returns:**
- `Promise<Record<string, any>>`: A promise that resolves to information about the file or directory.

**Throws:**
- `APIError`: If getting the file information fails.

#### Golang

```go
GetFileInfo(path string) (map[string]interface{}, error)
```

**Parameters:**
- `path` (string): The path of the file or directory to inspect.

**Returns:**
- `map[string]interface{}`: Information about the file or directory.
- `error`: An error if getting the file information fails.

### list_directory / listDirectory / ListDirectory

Lists the contents of a directory.

#### TypeScript

```typescript
listDirectory(path: string): Promise<Array<Record<string, any>>>
```

**Parameters:**
- `path` (string): The path of the directory to list.

**Returns:**
- `Promise<Array<Record<string, any>>>`: A promise that resolves to an array of directory entries.

**Throws:**
- `APIError`: If listing the directory fails.

#### Golang

```go
ListDirectory(path string) ([]map[string]interface{}, error)
```

**Parameters:**
- `path` (string): The path of the directory to list.

**Returns:**
- `[]map[string]interface{}`: An array of directory entries.
- `error`: An error if listing the directory fails.

### move_file / moveFile / MoveFile

Moves a file or directory from source to destination.

#### TypeScript

```typescript
moveFile(source: string, destination: string): Promise<boolean>
```

**Parameters:**
- `source` (string): The path of the source file or directory.
- `destination` (string): The path of the destination file or directory.

**Returns:**
- `Promise<boolean>`: A promise that resolves to true if the file was moved successfully.

**Throws:**
- `APIError`: If moving the file fails.

#### Golang

```go
MoveFile(source, destination string) (bool, error)
```

**Parameters:**
- `source` (string): The path of the source file or directory.
- `destination` (string): The path of the destination file or directory.

**Returns:**
- `bool`: True if the file was moved successfully.
- `error`: An error if moving the file fails.

### read_file / readFile / ReadFile

Reads the contents of a file in the cloud environment.

#### Python

```python
read_file(path: str) -> str
```

**Parameters:**
- `path` (str): The path of the file to read.

**Returns:**
- `str`: The contents of the file.

**Raises:**
- `AgentBayError`: If the file reading fails.

#### TypeScript

```typescript
readFile(path: string, offset?: number, length?: number): Promise<string>
```

**Parameters:**
- `path` (string): The path of the file to read.
- `offset` (number, optional): Start reading from this byte offset. Default is 0.
- `length` (number, optional): Number of bytes to read. If 0, read to end of file. Default is 0.

**Returns:**
- `Promise<string>`: A promise that resolves to the contents of the file.

**Throws:**
- `APIError`: If the file reading fails.

#### Golang

```go
ReadFile(path string, optionalParams ...int) (string, error)
```

**Parameters:**
- `path` (string): The path of the file to read.
- `optionalParams` (int, optional): Optional parameters for offset and length.

**Returns:**
- `string`: The contents of the file.
- `error`: An error if the file reading fails.

### read_multiple_files / readMultipleFiles / ReadMultipleFiles

Reads the contents of multiple files.

#### TypeScript

```typescript
readMultipleFiles(paths: string[]): Promise<Record<string, string>>
```

**Parameters:**
- `paths` (string[]): Array of paths to the files to read.

**Returns:**
- `Promise<Record<string, string>>`: A promise that resolves to an object mapping file paths to their contents.

**Throws:**
- `APIError`: If reading the files fails.

#### Golang

```go
ReadMultipleFiles(paths []string) (map[string]string, error)
```

**Parameters:**
- `paths` ([]string): Array of paths to the files to read.

**Returns:**
- `map[string]string`: An object mapping file paths to their contents.
- `error`: An error if reading the files fails.

### search_files / searchFiles / SearchFiles

Searches for files matching a pattern in a directory.

#### TypeScript

```typescript
searchFiles(path: string, pattern: string, excludePatterns?: string[]): Promise<Array<Record<string, any>>>
```

**Parameters:**
- `path` (string): The path of the directory to start the search.
- `pattern` (string): Pattern to match.
- `excludePatterns` (string[], optional): Patterns to exclude. Default is an empty array.

**Returns:**
- `Promise<Array<Record<string, any>>>`: A promise that resolves to an array of search results.

**Throws:**
- `APIError`: If the search fails.

#### Golang

```go
SearchFiles(path, pattern string, excludePatterns []string) ([]map[string]interface{}, error)
```

**Parameters:**
- `path` (string): The path of the directory to start the search.
- `pattern` (string): Pattern to match.
- `excludePatterns` ([]string): Patterns to exclude.

**Returns:**
- `[]map[string]interface{}`: An array of search results.
- `error`: An error if the search fails.

### write_file / writeFile / WriteFile

Writes content to a file.

#### TypeScript

```typescript
writeFile(path: string, content: string, mode?: string): Promise<boolean>
```

**Parameters:**
- `path` (string): The path of the file to write.
- `content` (string): Content to write to the file.
- `mode` (string, optional): "overwrite" (default) or "append".

**Returns:**
- `Promise<boolean>`: A promise that resolves to true if the file was written successfully.

**Throws:**
- `APIError`: If writing the file fails.

#### Golang

```go
WriteFile(path, content string, mode string) (bool, error)
```

**Parameters:**
- `path` (string): The path of the file to write.
- `content` (string): Content to write to the file.
- `mode` (string): "overwrite" (default) or "append".

**Returns:**
- `bool`: True if the file was written successfully.
- `error`: An error if writing the file fails.

## Usage Examples

### Python

```python
# Create a session
session = agent_bay.create()

# Read a file
content = session.filesystem.read_file("/etc/hosts")
print(f"File content: {content}")
```

### TypeScript

```typescript
// Create a session
const session = await agentBay.create();

// Read a file
const content = await session.filesystem.readFile('/etc/hosts');
log(`File content: ${content}`);

// Create a directory
await session.filesystem.createDirectory('/tmp/test');

// Write a file
await session.filesystem.writeFile('/tmp/test/example.txt', 'Hello, world!');

// Edit a file
await session.filesystem.editFile('/tmp/test/example.txt', [
  { oldText: 'Hello', newText: 'Hi' }
]);

// Get file info
const fileInfo = await session.filesystem.getFileInfo('/tmp/test/example.txt');
log(`File size: ${fileInfo.size}`);

// List directory
const entries = await session.filesystem.listDirectory('/tmp/test');
for (const entry of entries) {
  log(`${entry.isDirectory ? 'Directory' : 'File'}: ${entry.name}`);
}

// Move a file
await session.filesystem.moveFile('/tmp/test/example.txt', '/tmp/test/moved.txt');

// Read multiple files
const files = await session.filesystem.readMultipleFiles([
  '/tmp/test/moved.txt',
  '/etc/hosts'
]);
for (const [path, content] of Object.entries(files)) {
  log(`${path}: ${content}`);
}

// Search files
const results = await session.filesystem.searchFiles('/tmp', 'world', ['node_modules']);
for (const result of results) {
  log(`Found in ${result.path}`);
}
```

### Golang

```go
// Create a session
session, err := client.Create(nil)
if err != nil {
    // Handle error
}

// Read a file
content, err := session.FileSystem.ReadFile("/etc/hosts")
if err != nil {
    // Handle error
}
fmt.Printf("File content: %s\n", content)

// Create a directory
success, err := session.FileSystem.CreateDirectory("/tmp/test")
if err != nil {
    // Handle error
}

// Write a file
success, err = session.FileSystem.WriteFile("/tmp/test/example.txt", "Hello, world!", "overwrite")
if err != nil {
    // Handle error
}

// Edit a file
edits := []map[string]string{
    {
        "oldText": "Hello",
        "newText": "Hi",
    },
}
success, err = session.FileSystem.EditFile("/tmp/test/example.txt", edits, false)
if err != nil {
    // Handle error
}

// Get file info
fileInfo, err := session.FileSystem.GetFileInfo("/tmp/test/example.txt")
if err != nil {
    // Handle error
}
fmt.Printf("File size: %f\n", fileInfo["size"])

// List directory
entries, err := session.FileSystem.ListDirectory("/tmp/test")
if err != nil {
    // Handle error
}
for _, entry := range entries {
    entryType := "File"
    if entry["isDirectory"].(bool) {
        entryType = "Directory"
    }
    fmt.Printf("%s: %s\n", entryType, entry["name"])
}

// Move a file
success, err = session.FileSystem.MoveFile("/tmp/test/example.txt", "/tmp/test/moved.txt")
if err != nil {
    // Handle error
}

// Read multiple files
paths := []string{
    "/tmp/test/moved.txt",
    "/etc/hosts",
}
files, err := session.FileSystem.ReadMultipleFiles(paths)
if err != nil {
    // Handle error
}
for path, content := range files {
    fmt.Printf("%s: %s\n", path, content)
}

// Search files
excludePatterns := []string{"node_modules"}
results, err := session.FileSystem.SearchFiles("/tmp", "world", excludePatterns)
if err != nil {
    // Handle error
}
for _, result := range results {
    fmt.Printf("Found in %s\n", result["path"])
}
```

## Related Resources

- [Session Class](session.md): The session class that provides access to the FileSystem class.
- [Command Class](command.md): Provides methods for executing commands within a session.
