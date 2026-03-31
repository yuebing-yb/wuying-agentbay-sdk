# 📁 Filesystem API Reference

## Overview

The FileSystem module provides comprehensive file and directory operations in the cloud environment. It supports reading, writing, uploading, downloading, and managing files and directories.

## 📚 Tutorial

[File Operations Guide](../../../../../docs/guides/common-features/basics/file-operations.md)

Complete guide to file system operations

## FileSystem

Handles file operations in the AgentBay cloud environment.

### Constructor

```java
public FileSystem(Session session)
```

Initialize FileSystem with FileTransfer capability.

**Parameters:**
- `session` (Session): The session object for file operations

### Methods

### getFileTransferContextPath

```java
public String getFileTransferContextPath()
```

Get the context path for file transfer operations.

<p>This method ensures the context ID is loaded and returns the associated
context path that was retrieved from GetAndLoadInternalContext API.</p>

**Returns:**
- `String`: The context path if available, null otherwise

### read

```java
public String read(String path) throws AgentBayException
```

Read a file, alias of readFile().

**Parameters:**
- `path` (String): The path of the file to read

**Returns:**
- `String`: File content as string

**Throws:**
- `AgentBayException`: if reading fails

### write

```java
public String write(String path, String content) throws AgentBayException
```

Write content to a file.

**Parameters:**
- `path` (String): The path of the file to write
- `content` (String): The content to write to the file

**Returns:**
- `String`: Write result as string

**Throws:**
- `AgentBayException`: if writing fails

### list

```java
public String list(String path) throws AgentBayException
```

List the contents of a directory.

**Parameters:**
- `path` (String): The path of the directory to list

**Returns:**
- `String`: Directory listing as string

**Throws:**
- `AgentBayException`: if listing fails or directory does not exist

### exists

```java
public boolean exists(String path) throws AgentBayException
```

Check if a file or directory exists.

**Parameters:**
- `path` (String): Path to check

**Returns:**
- `boolean`: true if exists, false otherwise

**Throws:**
- `AgentBayException`: if check fails

### mkdir

```java
public String mkdir(String path) throws AgentBayException
```

Create a directory.

**Parameters:**
- `path` (String): Directory path to create

**Returns:**
- `String`: Creation result as string

**Throws:**
- `AgentBayException`: if creation fails or path is invalid

### removeLegacy

```java
public String removeLegacy(String path) throws AgentBayException
```

Remove a file or directory using shell command.

**Parameters:**
- `path` (String): Path to remove

**Returns:**
- `String`: Removal result

**Throws:**
- `AgentBayException`: if removal fails

### copy

```java
public String copy(String source, String destination) throws AgentBayException
```

Copy a file or directory.

**Parameters:**
- `source` (String): Source path to copy from
- `destination` (String): Destination path to copy to

**Returns:**
- `String`: Copy result as string

**Throws:**
- `AgentBayException`: if copy fails, source does not exist, or destination is invalid

### move

```java
public String move(String source, String destination) throws AgentBayException
```

Move a file or directory.

**Parameters:**
- `source` (String): Source path to move from
- `destination` (String): Destination path to move to

**Returns:**
- `String`: Move result as string

**Throws:**
- `AgentBayException`: if move fails, source does not exist, or destination is invalid

### getInfo

```java
public String getInfo(String path) throws AgentBayException
```

Get file information.

**Parameters:**
- `path` (String): File path to inspect

**Returns:**
- `String`: File information as string (ls -la output)

**Throws:**
- `AgentBayException`: if getting info fails or file does not exist

### writeFile

```java
public BoolResult writeFile(String path, String content, String mode, boolean createParentDir)
```

```java
public BoolResult writeFile(String path, String content)
```

```java
public BoolResult writeFile(String path, String content, String mode)
```

Write content to a file.
For MQTT channel, automatically handles large files by chunking.
For HTTP LinkUrl channel, writes the entire content in a single call without chunking.

<p>Similar to Python's write_file method.</p>

**Parameters:**
- `path` (String): File path
- `content` (String): Content to write
- `mode` (String): Write mode ("overwrite" or "append")
- `createParentDir` (boolean): Whether to create parent directories if they don't exist (default: false)

**Returns:**
- `BoolResult`: BoolResult containing success status and error message if any

### readFile

```java
public FileContentResult readFile(String path)
```

Read file content using FileContentResult

**Parameters:**
- `path` (String): File path to read

**Returns:**
- `FileContentResult`: FileContentResult containing success status, file content, and error message if any

### searchFiles

```java
public FileSearchResult searchFiles(String directory, String pattern)
```

```java
public FileSearchResult searchFiles(String directory, String pattern, List<String> excludePatterns)
```

Search for files matching a pattern

**Parameters:**
- `directory` (String): Directory to search in
- `pattern` (String): Wildcard pattern to match against file names. Supports * (any characters) and ? (single character). Examples: "*.py", "test_*", "*config*".
- `excludePatterns` (List<String>): Optional list of wildcard patterns to exclude from the search.

**Returns:**
- `FileSearchResult`: FileSearchResult containing list of matching file paths and error message if any

### readMultipleFiles

```java
public MultipleFileContentResult readMultipleFiles(List<String> paths)
```

Read multiple files at once

**Parameters:**
- `paths` (List<String>): List of file paths to read

**Returns:**
- `MultipleFileContentResult`: MultipleFileContentResult containing map of file paths to their content and error message if any

### deleteFile

```java
public BoolResult deleteFile(String path)
```

Delete a file at the specified path.

**Parameters:**
- `path` (String): The path of the file to delete

**Returns:**
- `BoolResult`: BoolResult containing success status and error message if any

### createDirectory

```java
public BoolResult createDirectory(String path)
```

Create a new directory at the specified path.

**Parameters:**
- `path` (String): The path of the directory to create

**Returns:**
- `BoolResult`: BoolResult containing success status and error message if any

### listDirectory

```java
public com.aliyun.agentbay.model.DirectoryListResult listDirectory(String path)
```

List the contents of a directory.

**Parameters:**
- `path` (String): The path of the directory to list

**Returns:**
- `com.aliyun.agentbay.model.DirectoryListResult`: DirectoryListResult containing directory entries and error message if any
 - success (bool): True if the operation succeeded
  - entries (List[Dict[str, Union[str, bool]]]): List of directory entries (if success is True)
     Each entry contains:
     - name (str): Name of the file or directory
    - isDirectory (bool): True if entry is a directory, False if file
- requestId (str): Unique identifier for this API request
- errorMessage (str): Error description (if success is False)

### getFileInfo

```java
public com.aliyun.agentbay.model.FileInfoResult getFileInfo(String path)
```

Get information about a file or directory.

**Parameters:**
- `path` (String): The path of the file or directory to inspect

**Returns:**
- `com.aliyun.agentbay.model.FileInfoResult`: FileInfoResult containing file info and error message if any

### editFile

```java
public BoolResult editFile(String path, java.util.List<java.util.Map<String, String>> edits)
```

```java
public BoolResult editFile(String path, java.util.List<java.util.Map<String, String>> edits, boolean dryRun)
```

Edit a file by replacing occurrences of oldText with newText.

**Parameters:**
- `path` (String): The path of the file to edit
- `edits` (java.util.List<java.util.Map<String,String>>): A list of maps specifying oldText and newText for replacements
- `dryRun` (boolean): If true, preview changes without applying them

**Returns:**
- `BoolResult`: BoolResult containing success status and error message if any

### moveFile

```java
public BoolResult moveFile(String source, String destination)
```

Move a file from source to destination path.

**Parameters:**
- `source` (String): Source file path to move from
- `destination` (String): Destination file path to move to

**Returns:**
- `BoolResult`: BoolResult containing success status and error message if any

### uploadFile

```java
public UploadResult uploadFile(String localPath, String remotePath, String contentType, boolean wait, float waitTimeout, float pollInterval)
```

```java
public UploadResult uploadFile(String localPath, String remotePath, String contentType, boolean wait, float waitTimeout, float pollInterval, ProgressCallback progressCallback)
```

```java
public UploadResult uploadFile(String localPath, String remotePath)
```

Upload a local file to remote path using pre-signed URLs.

**Parameters:**
- `localPath` (String): Local file path to upload
- `remotePath` (String): Remote file path to upload to
- `contentType` (String): Optional content type for the file (can be null)
- `wait` (boolean): Whether to wait for the sync operation to complete
- `waitTimeout` (float): Timeout for waiting for sync completion (seconds)
- `pollInterval` (float): Interval between polling for sync completion (seconds)
- `progressCallback` (ProgressCallback): Callback for upload progress updates

**Returns:**
- `UploadResult`: UploadResult containing the result of the upload operation

### downloadFile

```java
public DownloadResult downloadFile(String remotePath, String localPath, boolean overwrite, boolean wait, float waitTimeout, float pollInterval)
```

```java
public DownloadResult downloadFile(String remotePath, String localPath, boolean overwrite, boolean wait, float waitTimeout, float pollInterval, ProgressCallback progressCallback)
```

```java
public DownloadResult downloadFile(String remotePath, String localPath)
```

```java
public DownloadResult downloadFile(String remotePath)
```

Download a file from remote path to local path using pre-signed URLs.

**Parameters:**
- `remotePath` (String): Remote file path to download from
- `localPath` (String): Local file path to download to
- `overwrite` (boolean): Whether to overwrite existing local file
- `wait` (boolean): Whether to wait for the sync operation to complete
- `waitTimeout` (float): Timeout for waiting for sync completion (seconds)
- `pollInterval` (float): Interval between polling for sync completion (seconds)
- `progressCallback` (ProgressCallback): Callback for download progress updates

**Returns:**
- `DownloadResult`: DownloadResult containing the result of the download operation

### uploadFileBytes

```java
public UploadResult uploadFileBytes(byte[] content, String remotePath, String contentType, boolean wait, float waitTimeout, float pollInterval, ProgressCallback progressCallback)
```

```java
public UploadResult uploadFileBytes(byte[] content, String remotePath)
```

Upload byte array to remote path using pre-signed URLs.
This is a Java SDK extension that allows uploading data from memory without writing to disk first.

**Parameters:**
- `content` (byte[]): Byte array content to upload
- `remotePath` (String): Remote file path to upload to
- `contentType` (String): Optional content type for the file
- `wait` (boolean): Whether to wait for the sync operation to complete
- `waitTimeout` (float): Timeout for waiting for sync completion (seconds)
- `pollInterval` (float): Interval between polling for sync completion (seconds)
- `progressCallback` (ProgressCallback): Callback for upload progress updates

**Returns:**
- `UploadResult`: UploadResult containing the result of the upload operation

### downloadFileBytes

```java
public DownloadResult downloadFileBytes(String remotePath, boolean wait, float waitTimeout, float pollInterval, ProgressCallback progressCallback)
```

```java
public DownloadResult downloadFileBytes(String remotePath)
```

Download file from remote path to byte array using pre-signed URLs.
This is a Java SDK extension that allows downloading data to memory without writing to disk.

**Parameters:**
- `remotePath` (String): Remote file path to download from
- `wait` (boolean): Whether to wait for the sync operation to complete
- `waitTimeout` (float): Timeout for waiting for sync completion (seconds)
- `pollInterval` (float): Interval between polling for sync completion (seconds)
- `progressCallback` (ProgressCallback): Callback for download progress updates

**Returns:**
- `DownloadResult`: DownloadResult containing the downloaded byte array in the content field

### delete

```java
public BoolResult delete(String path)
```

Delete a file at the specified path. Alias for deleteFile().

**Parameters:**
- `path` (String): The path of the file to delete

**Returns:**
- `BoolResult`: BoolResult containing success status and error message if any

### remove

```java
public BoolResult remove(String path)
```

Remove a file at the specified path. Alias for deleteFile().

**Parameters:**
- `path` (String): The path of the file to remove

**Returns:**
- `BoolResult`: BoolResult containing success status and error message if any

### rm

```java
public BoolResult rm(String path)
```

Remove a file at the specified path. Alias for deleteFile().

**Parameters:**
- `path` (String): The path of the file to remove

**Returns:**
- `BoolResult`: BoolResult containing success status and error message if any

### ls

```java
public com.aliyun.agentbay.model.DirectoryListResult ls(String path)
```

List directory contents. Alias for listDirectory().

**Parameters:**
- `path` (String): The path of the directory to list

**Returns:**
- `com.aliyun.agentbay.model.DirectoryListResult`: DirectoryListResult containing directory entries and error message if any



## 🔗 Related Resources

- [Session API Reference](../../../api/common-features/basics/session.md)
- [Command API Reference](../../../api/common-features/basics/command.md)

