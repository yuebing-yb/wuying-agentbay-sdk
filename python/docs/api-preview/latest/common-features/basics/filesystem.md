# File System API Reference

## 📁 Related Tutorial

- [File Operations Guide](../../../../../../docs/guides/common-features/basics/file-operations.md) - Complete guide to file system operations


```python
logger = get_logger("filesystem")
```

## UploadResult Objects

```python
@dataclass
class UploadResult()
```

Result structure for file upload operations.

#### success: `bool`

```python
success = None
```

#### request\_id\_upload\_url: `Optional[str]`

```python
request_id_upload_url = None
```

#### request\_id\_sync: `Optional[str]`

```python
request_id_sync = None
```

#### http\_status: `Optional[int]`

```python
http_status = None
```

#### etag: `Optional[str]`

```python
etag = None
```

#### bytes\_sent: `int`

```python
bytes_sent = None
```

#### path: `str`

```python
path = None
```

#### error: `Optional[str]`

```python
error = None
```

## DownloadResult Objects

```python
@dataclass
class DownloadResult()
```

Result structure for file download operations.

#### success: `bool`

```python
success = None
```

#### request\_id\_download\_url: `Optional[str]`

```python
request_id_download_url = None
```

#### request\_id\_sync: `Optional[str]`

```python
request_id_sync = None
```

#### http\_status: `Optional[int]`

```python
http_status = None
```

#### bytes\_received: `int`

```python
bytes_received = None
```

#### path: `str`

```python
path = None
```

#### local\_path: `str`

```python
local_path = None
```

#### error: `Optional[str]`

```python
error = None
```

## FileTransfer Objects

```python
class FileTransfer()
```

FileTransfer provides pre-signed URL upload/download functionality between local and OSS,
with integration to Session Context synchronization.

Prerequisites and Constraints:
- Session must be associated with the corresponding context_id and path through 
  CreateSessionParams.context_syncs, and remote_path should fall within that 
  synchronization path (or conform to backend path rules).
- Requires available AgentBay context service (agent_bay.context) and session context.

#### upload

```python
async def upload(
        local_path: str,
        remote_path: str,
        *,
        content_type: Optional[str] = None,
        wait: bool = True,
        wait_timeout: float = 30.0,
        poll_interval: float = 1.5,
        progress_cb: Optional[Callable[[int], None]] = None) -> UploadResult
```

Upload workflow:
1) Get OSS pre-signed URL via context.get_file_upload_url
2) Upload local file to OSS using the URL (HTTP PUT)
3) Trigger session.context.sync(mode="upload") to sync OSS objects to cloud disk
4) If wait=True, poll session.context.info until upload task reaches completion or timeout

Returns UploadResult containing request_ids, HTTP status, ETag and other information.

#### download

```python
async def download(
        remote_path: str,
        local_path: str,
        *,
        overwrite: bool = True,
        wait: bool = True,
        wait_timeout: float = 300.0,
        poll_interval: float = 1.5,
        progress_cb: Optional[Callable[[int], None]] = None) -> DownloadResult
```

Download workflow:
1) Trigger session.context.sync(mode="upload") to sync cloud disk data to OSS
2) Get pre-signed download URL via context.get_file_download_url
3) Download the file and save to local local_path
4) If wait=True, wait for download task to reach completion after step 1 
   (ensuring backend has prepared the download object)

Returns DownloadResult containing sync and download request_ids, HTTP status, byte count, etc.

## FileChangeEvent Objects

```python
class FileChangeEvent()
```

Represents a single file change event.

#### to\_dict

```python
def to_dict() -> Dict[str, str]
```

Convert to dictionary representation.

#### from\_dict

```python
@classmethod
def from_dict(cls, data: Dict[str, str]) -> "FileChangeEvent"
```

Create FileChangeEvent from dictionary.

## FileChangeResult Objects

```python
class FileChangeResult(ApiResponse)
```

Result of file change detection operations.

#### has\_changes

```python
def has_changes() -> bool
```

Check if there are any file changes.

#### get\_modified\_files

```python
def get_modified_files() -> List[str]
```

Get list of modified file paths.

#### get\_created\_files

```python
def get_created_files() -> List[str]
```

Get list of created file paths.

#### get\_deleted\_files

```python
def get_deleted_files() -> List[str]
```

Get list of deleted file paths.

## FileInfoResult Objects

```python
class FileInfoResult(ApiResponse)
```

Result of file info operations.

## DirectoryListResult Objects

```python
class DirectoryListResult(ApiResponse)
```

Result of directory listing operations.

## FileContentResult Objects

```python
class FileContentResult(ApiResponse)
```

Result of file read operations.

## MultipleFileContentResult Objects

```python
class MultipleFileContentResult(ApiResponse)
```

Result of multiple file read operations.

## FileSearchResult Objects

```python
class FileSearchResult(ApiResponse)
```

Result of file search operations.

## FileSystem Objects

```python
class FileSystem(BaseService)
```

Handles file operations in the AgentBay cloud environment.

#### DEFAULT\_CHUNK\_SIZE

```python
DEFAULT_CHUNK_SIZE = 50 * 1024
```

#### create\_directory

```python
def create_directory(path: str) -> BoolResult
```

Create a new directory at the specified path.

**Arguments**:

- `path` - The path of the directory to create.
  

**Returns**:

- `BoolResult` - Result object containing success status and error message if
  any.

#### edit\_file

```python
def edit_file(path: str,
              edits: List[Dict[str, str]],
              dry_run: bool = False) -> BoolResult
```

Edit a file by replacing occurrences of oldText with newText.

**Arguments**:

- `path` - The path of the file to edit.
- `edits` - A list of dictionaries specifying oldText and newText.
- `dry_run` - If True, preview changes without applying them.
  

**Returns**:

- `BoolResult` - Result object containing success status and error message if
  any.

#### get\_file\_info

```python
def get_file_info(path: str) -> FileInfoResult
```

Get information about a file or directory.

**Arguments**:

- `path` - The path of the file or directory to inspect.
  

**Returns**:

- `FileInfoResult` - Result object containing file info and error message if any.

#### list\_directory

```python
def list_directory(path: str) -> DirectoryListResult
```

List the contents of a directory.

**Arguments**:

- `path` _str_ - The path of the directory to list.
  

**Returns**:

- `DirectoryListResult` - Result object containing directory entries and error message if any.
  - success (bool): True if the operation succeeded
  - entries (List[Dict[str, Union[str, bool]]]): List of directory entries (if success is True)
  Each entry contains:
  - name (str): Name of the file or directory
  - isDirectory (bool): True if entry is a directory, False if file
  - request_id (str): Unique identifier for this API request
  - error_message (str): Error description (if success is False)
  

**Raises**:

- `FileError` - If the directory does not exist or cannot be accessed.
  

**Example**:

    ```python
    from agentbay import AgentBay

    # Initialize and create session
    agent_bay = AgentBay(api_key="your_api_key")
    result = agent_bay.create()
    if result.success:
        session = result.session

        # Create some test files and directories
        session.filesystem.create_directory("/tmp/testdir")
        session.filesystem.write_file("/tmp/testdir/file1.txt", "Content 1")
        session.filesystem.write_file("/tmp/testdir/file2.txt", "Content 2")
        session.filesystem.create_directory("/tmp/testdir/subdir")

        # List the directory
        list_result = session.filesystem.list_directory("/tmp/testdir")
        if list_result.success:
            print(f"Found {len(list_result.entries)} entries")
            # Output: Found 3 entries
            for entry in list_result.entries:
                entry_type = "DIR" if entry["isDirectory"] else "FILE"
                print(f"[{entry_type}] {entry['name']}")
            # Output: [FILE] file1.txt
            # Output: [FILE] file2.txt
            # Output: [DIR] subdir
            print(f"Request ID: {list_result.request_id}")
            # Output: Request ID: 9E3F4A5B-2C6D-7E8F-9A0B-1C2D3E4F5A6B

        # Handle directory not found
        result = session.filesystem.list_directory("/tmp/nonexistent")
        if not result.success:
            print(f"Error: {result.error_message}")
            # Output: Error: Failed to list directory

        # Clean up
        session.delete()
    ```
  

**Notes**:

  - Returns empty list for empty directories
  - Each entry includes name and isDirectory flag
  - Does not recursively list subdirectories
  

**See Also**:

  FileSystem.create_directory, FileSystem.get_file_info, FileSystem.read_file

#### move\_file

```python
def move_file(source: str, destination: str) -> BoolResult
```

Move a file or directory from source path to destination path.

**Arguments**:

- `source` - The source path of the file or directory.
- `destination` - The destination path.
  

**Returns**:

- `BoolResult` - Result object containing success status and error message if
  any.

#### read\_multiple\_files

```python
def read_multiple_files(paths: List[str]) -> MultipleFileContentResult
```

Read the contents of multiple files at once.

**Arguments**:

- `paths` - A list of file paths to read.
  

**Returns**:

- `MultipleFileContentResult` - Result object containing a dictionary mapping
  file paths to contents,
  and error message if any.

#### search\_files

```python
def search_files(
        path: str,
        pattern: str,
        exclude_patterns: Optional[List[str]] = None) -> FileSearchResult
```

Search for files in the specified path using a pattern.

**Arguments**:

- `path` - The base directory path to search in.
- `pattern` - The glob pattern to search for.
- `exclude_patterns` - Optional list of patterns to exclude from the search.
  

**Returns**:

- `FileSearchResult` - Result object containing matching file paths and error
  message if any.

#### read\_file

```python
def read_file(path: str) -> FileContentResult
```

Read the contents of a file. Automatically handles large files by chunking.

**Arguments**:

- `path` _str_ - The path of the file to read.
  

**Returns**:

- `FileContentResult` - Result object containing file content and error message if any.
  - success (bool): True if the operation succeeded
  - content (str): The file content (if success is True)
  - request_id (str): Unique identifier for this API request
  - error_message (str): Error description (if success is False)
  

**Raises**:

- `FileError` - If the file does not exist or is a directory.
  

**Example**:

    ```python
    from agentbay import AgentBay

    # Initialize and create session
    agent_bay = AgentBay(api_key="your_api_key")
    result = agent_bay.create()
    if result.success:
        session = result.session

        # Write a file first
        write_result = session.filesystem.write_file("/tmp/test.txt", "Hello, World!")
        if write_result.success:
            print("File written successfully")

        # Read the file
        read_result = session.filesystem.read_file("/tmp/test.txt")
        if read_result.success:
            print(f"File content: {read_result.content}")
            # Output: File content: Hello, World!
            print(f"Request ID: {read_result.request_id}")
            # Output: Request ID: 9E3F4A5B-2C6D-7E8F-9A0B-1C2D3E4F5A6B

        # Handle file not found
        result = session.filesystem.read_file("/tmp/nonexistent.txt")
        if not result.success:
            print(f"Error: {result.error_message}")
            # Output: Error: Path does not exist or is a directory: /tmp/nonexistent.txt

        # Clean up
        session.delete()
    ```
  

**Notes**:

  - Automatically handles large files by reading in chunks (default 50KB per chunk)
  - Returns empty string for empty files
  - Returns error if path is a directory
  

**See Also**:

  FileSystem.write_file, FileSystem.list_directory, FileSystem.get_file_info

#### write\_file

```python
def write_file(path: str, content: str, mode: str = "overwrite") -> BoolResult
```

Write content to a file. Automatically handles large files by chunking.

**Arguments**:

- `path` _str_ - The path of the file to write.
- `content` _str_ - The content to write to the file.
- `mode` _str, optional_ - The write mode. Defaults to "overwrite".
  - "overwrite": Replace file content
  - "append": Append to existing content
  

**Returns**:

- `BoolResult` - Result object containing success status and error message if any.
  - success (bool): True if the operation succeeded
  - data (bool): True if the file was written successfully
  - request_id (str): Unique identifier for this API request
  - error_message (str): Error description (if success is False)
  

**Raises**:

- `FileError` - If the write operation fails.
  

**Example**:

            ```python
            from agentbay import AgentBay

            # Initialize and create session
            agent_bay = AgentBay(api_key="your_api_key")
            result = agent_bay.create()
            if result.success:
                session = result.session

                # Write a new file (overwrite mode)
                write_result = session.filesystem.write_file("/tmp/test.txt", "Hello, World!")
                if write_result.success:
                    print("File written successfully")
                    # Output: File written successfully
                    print(f"Request ID: {write_result.request_id}")
                    # Output: Request ID: 9E3F4A5B-2C6D-7E8F-9A0B-1C2D3E4F5A6B

                # Append to existing file
                append_result = session.filesystem.write_file(
                    "/tmp/test.txt",
                    "
Appended content",
                    mode="append"
                )
                if append_result.success:
                    print("Content appended successfully")

                # Verify the content
                read_result = session.filesystem.read_file("/tmp/test.txt")
                if read_result.success:
                    print(f"File content: {read_result.content}")
                    # Output: File content: Hello, World!
                    # Appended content

                # Clean up
                session.delete()
            ```
  

**Notes**:

  - Automatically handles large files by writing in chunks (default 50KB per chunk)
  - Creates parent directories if they don't exist
  - In "overwrite" mode, replaces the entire file content
  - In "append" mode, adds content to the end of the file
  

**See Also**:

  FileSystem.read_file, FileSystem.create_directory, FileSystem.edit_file

#### upload\_file

```python
def upload_file(
        local_path: str,
        remote_path: str,
        *,
        content_type: Optional[str] = None,
        wait: bool = True,
        wait_timeout: float = 30.0,
        poll_interval: float = 1.5,
        progress_cb: Optional[Callable[[int], None]] = None) -> UploadResult
```

Upload a file from local to remote path using pre-signed URLs.

This is a synchronous wrapper around the async FileTransfer.upload method.

**Arguments**:

- `local_path` - Local file path to upload
- `remote_path` - Remote file path to upload to
- `content_type` - Optional content type for the file
- `wait` - Whether to wait for the sync operation to complete
- `wait_timeout` - Timeout for waiting for sync completion
- `poll_interval` - Interval between polling for sync completion
- `progress_cb` - Callback for upload progress updates
  

**Returns**:

- `UploadResult` - Result of the upload operation

#### download\_file

```python
def download_file(
        remote_path: str,
        local_path: str,
        *,
        overwrite: bool = True,
        wait: bool = True,
        wait_timeout: float = 30.0,
        poll_interval: float = 1.5,
        progress_cb: Optional[Callable[[int], None]] = None) -> DownloadResult
```

Download a file from remote path to local path using pre-signed URLs.

This is a synchronous wrapper around the async FileTransfer.download method.

**Arguments**:

- `remote_path` - Remote file path to download from
- `local_path` - Local file path to download to
- `overwrite` - Whether to overwrite existing local file
- `wait` - Whether to wait for the sync operation to complete
- `wait_timeout` - Timeout for waiting for sync completion
- `poll_interval` - Interval between polling for sync completion
- `progress_cb` - Callback for download progress updates
  

**Returns**:

- `DownloadResult` - Result of the download operation

#### watch\_directory

```python
def watch_directory(
        path: str,
        callback: Callable[[List[FileChangeEvent]], None],
        interval: float = 0.5,
        stop_event: Optional[threading.Event] = None) -> threading.Thread
```

Watch a directory for file changes and call the callback function when changes occur.

**Arguments**:

- `path` - The directory path to monitor for file changes.
- `callback` - Callback function that will be called with a list of FileChangeEvent
  objects when changes are detected.
- `interval` - Polling interval in seconds. Defaults to 0.5.
- `stop_event` - Optional threading.Event to stop the monitoring. If not provided,
  a new Event will be created and returned via the thread object.
  

**Returns**:

- `threading.Thread` - The monitoring thread. Call thread.start() to begin monitoring.
  Use the thread's stop_event attribute to stop monitoring.

## Related Resources

- [Session API Reference](session.md)
- [Command API Reference](command.md)

---

*Documentation generated automatically from source code using pydoc-markdown.*
