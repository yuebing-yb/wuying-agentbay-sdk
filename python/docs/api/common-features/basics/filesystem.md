# File System API Reference

## 📁 Related Tutorial

- [File Operations Guide](../../../../../docs/guides/common-features/basics/file-operations.md) - Complete guide to file system operations



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

## FileChangeResult Objects

```python
class FileChangeResult(ApiResponse)
```

Result of file change detection operations.

This class provides methods to check and filter file change events detected
in a directory. It is typically returned by file monitoring operations.

**Example**:

```python
from agentbay import AgentBay
import time

agent_bay = AgentBay(api_key="your_api_key")

def analyze_file_changes():
    try:
        result = agent_bay.create()
        if result.success:
            session = result.session

            # Create a test directory and some files
            session.file_system.create_directory("/tmp/change_test")
            session.file_system.write_file("/tmp/change_test/file1.txt", "original content")
            session.file_system.write_file("/tmp/change_test/file2.txt", "original content")

            # Wait a moment for changes to be detected
            time.sleep(1)

            # Make some changes
            session.file_system.write_file("/tmp/change_test/file1.txt", "modified content")
            session.file_system.write_file("/tmp/change_test/file3.txt", "new file")

            time.sleep(1)

            # Get file changes using the internal API
            change_result = session.file_system._get_file_change("/tmp/change_test")

            if change_result.success:
                # Check if there are any changes
                if change_result.has_changes():
                    print(f"Detected {len(change_result.events)} change(s)")
                    # Output: Detected 2 change(s)

                    # Get modified files
                    modified = change_result.get_modified_files()
                    if modified:
                        print(f"Modified files: {modified}")
                        # Output: Modified files: ['/tmp/change_test/file1.txt']

                    # Get created files
                    created = change_result.get_created_files()
                    if created:
                        print(f"Created files: {created}")
                        # Output: Created files: ['/tmp/change_test/file3.txt']

                    # Get deleted files
                    deleted = change_result.get_deleted_files()
                    if deleted:
                        print(f"Deleted files: {deleted}")
                    else:
                        print("No files were deleted")
                        # Output: No files were deleted
                else:
                    print("No changes detected")

            session.delete()
    except Exception as e:
        print(f"Error: {e}")

analyze_file_changes()
```

#### has\_changes

```python
def has_changes() -> bool
```

Check if there are any file changes.

**Returns**:

    bool: True if there are any file change events, False otherwise.

#### get\_modified\_files

```python
def get_modified_files() -> List[str]
```

Get list of modified file paths.

**Returns**:

    List[str]: List of file paths that were modified.

#### get\_created\_files

```python
def get_created_files() -> List[str]
```

Get list of created file paths.

**Returns**:

    List[str]: List of file paths that were created.

#### get\_deleted\_files

```python
def get_deleted_files() -> List[str]
```

Get list of deleted file paths.

**Returns**:

    List[str]: List of file paths that were deleted.

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

    path: The path of the directory to create.
  

**Returns**:

    BoolResult: Result object containing success status and error message if
  any.
  

**Example**:

```python
from agentbay import AgentBay

# Initialize and create session
agent_bay = AgentBay(api_key="your_api_key")
result = agent_bay.create()
if result.success:
    session = result.session

    # Create a directory
    create_result = session.file_system.create_directory("/tmp/mydir")
    if create_result.success:
        print("Directory created successfully")
        # Output: Directory created successfully
        print(f"Request ID: {create_result.request_id}")
        # Output: Request ID: 9E3F4A5B-2C6D-7E8F-9A0B-1C2D3E4F5A6B

    # Create nested directories
    nested_result = session.file_system.create_directory("/tmp/parent/child/grandchild")
    if nested_result.success:
        print("Nested directories created")

    # Clean up
    session.delete()
```

#### edit\_file

```python
def edit_file(path: str,
              edits: List[Dict[str, str]],
              dry_run: bool = False) -> BoolResult
```

Edit a file by replacing occurrences of oldText with newText.

**Arguments**:

    path: The path of the file to edit.
    edits: A list of dictionaries specifying oldText and newText.
    dry_run: If True, preview changes without applying them.
  

**Returns**:

    BoolResult: Result object containing success status and error message if
  any.
  

**Example**:

```python
from agentbay import AgentBay

# Initialize and create session
agent_bay = AgentBay(api_key="your_api_key")
result = agent_bay.create()
if result.success:
    session = result.session

    # Create a test file
    session.file_system.write_file("/tmp/config.txt", "DEBUG=false\nLOG_LEVEL=info")

    # Edit the file with single replacement
    edits = [{"oldText": "DEBUG=false", "newText": "DEBUG=true"}]
    edit_result = session.file_system.edit_file("/tmp/config.txt", edits)
    if edit_result.success:
        print("File edited successfully")
        # Output: File edited successfully

    # Edit with multiple replacements
    edits = [
        {"oldText": "DEBUG=true", "newText": "DEBUG=false"},
        {"oldText": "LOG_LEVEL=info", "newText": "LOG_LEVEL=debug"}
    ]
    multi_edit_result = session.file_system.edit_file("/tmp/config.txt", edits)
    if multi_edit_result.success:
        print("Multiple edits applied")

    # Preview changes with dry_run
    dry_run_result = session.file_system.edit_file(
        "/tmp/config.txt",
        [{"oldText": "debug", "newText": "trace"}],
        dry_run=True
    )
    if dry_run_result.success:
        print("Dry run completed, no changes applied")

    # Clean up
    session.delete()
```

#### get\_file\_info

```python
def get_file_info(path: str) -> FileInfoResult
```

Get information about a file or directory.

**Arguments**:

    path: The path of the file or directory to inspect.
  

**Returns**:

    FileInfoResult: Result object containing file info and error message if any.
  

**Example**:

```python
from agentbay import AgentBay

# Initialize and create session
agent_bay = AgentBay(api_key="your_api_key")
result = agent_bay.create()
if result.success:
    session = result.session

    # Create a test file
    session.file_system.write_file("/tmp/test.txt", "Sample content")

    # Get file information
    info_result = session.file_system.get_file_info("/tmp/test.txt")
    if info_result.success:
        print(f"File info: {info_result.file_info}")
        # Output: File info: {'size': 14, 'isDirectory': False, ...}
        print(f"Size: {info_result.file_info.get('size')} bytes")
        # Output: Size: 14 bytes
        print(f"Is directory: {info_result.file_info.get('isDirectory')}")
        # Output: Is directory: False

    # Get directory information
    session.file_system.create_directory("/tmp/mydir")
    dir_info = session.file_system.get_file_info("/tmp/mydir")
    if dir_info.success:
        print(f"Is directory: {dir_info.file_info.get('isDirectory')}")
        # Output: Is directory: True

    # Clean up
    session.delete()
```

#### list\_directory

```python
def list_directory(path: str) -> DirectoryListResult
```

List the contents of a directory.

**Arguments**:

- `path` _str_ - The path of the directory to list.
  

**Returns**:

    DirectoryListResult: Result object containing directory entries and error message if any.
  - success (bool): True if the operation succeeded
  - entries (List[Dict[str, Union[str, bool]]]): List of directory entries (if success is True)
  Each entry contains:
  - name (str): Name of the file or directory
  - isDirectory (bool): True if entry is a directory, False if file
  - request_id (str): Unique identifier for this API request
  - error_message (str): Error description (if success is False)
  

**Raises**:

    FileError: If the directory does not exist or cannot be accessed.
  

**Example**:

```python
from agentbay import AgentBay

# Initialize and create session
agent_bay = AgentBay(api_key="your_api_key")
result = agent_bay.create()
if result.success:
    session = result.session

    # Create some test files and directories
    session.file_system.create_directory("/tmp/testdir")
    session.file_system.write_file("/tmp/testdir/file1.txt", "Content 1")
    session.file_system.write_file("/tmp/testdir/file2.txt", "Content 2")
    session.file_system.create_directory("/tmp/testdir/subdir")

    # List the directory
    list_result = session.file_system.list_directory("/tmp/testdir")
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
    result = session.file_system.list_directory("/tmp/nonexistent")
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

    source: The source path of the file or directory.
    destination: The destination path.
  

**Returns**:

    BoolResult: Result object containing success status and error message if
  any.
  

**Example**:

```python
from agentbay import AgentBay

# Initialize and create session
agent_bay = AgentBay(api_key="your_api_key")
result = agent_bay.create()
if result.success:
    session = result.session

    # Create a test file
    session.file_system.write_file("/tmp/original.txt", "Test content")

    # Move the file to a new location
    move_result = session.file_system.move_file("/tmp/original.txt", "/tmp/moved.txt")
    if move_result.success:
        print("File moved successfully")
        # Output: File moved successfully
        print(f"Request ID: {move_result.request_id}")
        # Output: Request ID: 9E3F4A5B-2C6D-7E8F-9A0B-1C2D3E4F5A6B

    # Verify the move
    read_result = session.file_system.read_file("/tmp/moved.txt")
    if read_result.success:
        print(f"Content at new location: {read_result.content}")
        # Output: Content at new location: Test content

    # Clean up
    session.delete()
```

#### read\_multiple\_files

```python
def read_multiple_files(paths: List[str]) -> MultipleFileContentResult
```

Read the contents of multiple files at once.

**Arguments**:

    paths: A list of file paths to read.
  

**Returns**:

    MultipleFileContentResult: Result object containing a dictionary mapping
  file paths to contents,
  and error message if any.
  

**Example**:

```python
from agentbay import AgentBay

# Initialize and create session
agent_bay = AgentBay(api_key="your_api_key")
result = agent_bay.create()
if result.success:
    session = result.session

    # Create multiple test files
    session.file_system.write_file("/tmp/file1.txt", "Content of file 1")
    session.file_system.write_file("/tmp/file2.txt", "Content of file 2")
    session.file_system.write_file("/tmp/file3.txt", "Content of file 3")

    # Read multiple files at once
    paths = ["/tmp/file1.txt", "/tmp/file2.txt", "/tmp/file3.txt"]
    read_result = session.file_system.read_multiple_files(paths)
    if read_result.success:
        print(f"Read {len(read_result.contents)} files")
        # Output: Read 3 files
        for path, content in read_result.contents.items():
            print(f"{path}: {content}")
        # Output: /tmp/file1.txt: Content of file 1
        # Output: /tmp/file2.txt: Content of file 2
        # Output: /tmp/file3.txt: Content of file 3

    # Clean up
    session.delete()
```

#### search\_files

```python
def search_files(
        path: str,
        pattern: str,
        exclude_patterns: Optional[List[str]] = None) -> FileSearchResult
```

Search for files in the specified path using a pattern.

**Arguments**:

    path: The base directory path to search in.
    pattern: The glob pattern to search for.
    exclude_patterns: Optional list of patterns to exclude from the search.
  

**Returns**:

    FileSearchResult: Result object containing matching file paths and error
  message if any.
  

**Example**:

```python
from agentbay import AgentBay

# Initialize and create session
agent_bay = AgentBay(api_key="your_api_key")
result = agent_bay.create()
if result.success:
    session = result.session

    # Create test files
    session.file_system.write_file("/tmp/test/file1.py", "print('hello')")
    session.file_system.write_file("/tmp/test/file2.py", "print('world')")
    session.file_system.write_file("/tmp/test/file3.txt", "text content")

    # Search for Python files (using partial name matching, NOT wildcards)
    search_result = session.file_system.search_files("/tmp/test", ".py")
    if search_result.success:
        print(f"Found {len(search_result.matches)} Python files:")
        # Output: Found 2 Python files:
        for match in search_result.matches:
            print(f"  - {match}")
        # Output:   - /tmp/test/file1.py
        # Output:   - /tmp/test/file2.py

    # Search with exclusion pattern (exclude files containing ".txt")
    search_result = session.file_system.search_files(
        "/tmp/test",
        "file",
        exclude_patterns=[".txt"]
    )
    if search_result.success:
        print(f"Found {len(search_result.matches)} files (excluding .txt)")
        # Output: Found 2 files (excluding .txt)

    # Clean up
    session.delete()
```

#### read\_file

```python
def read_file(path: str) -> FileContentResult
```

Read the contents of a file. Automatically handles large files by chunking.

**Arguments**:

- `path` _str_ - The path of the file to read.
  

**Returns**:

    FileContentResult: Result object containing file content and error message if any.
  - success (bool): True if the operation succeeded
  - content (str): The file content (if success is True)
  - request_id (str): Unique identifier for this API request
  - error_message (str): Error description (if success is False)
  

**Raises**:

    FileError: If the file does not exist or is a directory.
  

**Example**:

```python
from agentbay import AgentBay

# Initialize and create session
agent_bay = AgentBay(api_key="your_api_key")
result = agent_bay.create()
if result.success:
    session = result.session

    # Write a file first
    write_result = session.file_system.write_file("/tmp/test.txt", "Hello, World!")
    if write_result.success:
        print("File written successfully")

    # Read the file
    read_result = session.file_system.read_file("/tmp/test.txt")
    if read_result.success:
        print(f"File content: {read_result.content}")
        # Output: File content: Hello, World!
        print(f"Request ID: {read_result.request_id}")
        # Output: Request ID: 9E3F4A5B-2C6D-7E8F-9A0B-1C2D3E4F5A6B

    # Handle file not found
    result = session.file_system.read_file("/tmp/nonexistent.txt")
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

    BoolResult: Result object containing success status and error message if any.
  - success (bool): True if the operation succeeded
  - data (bool): True if the file was written successfully
  - request_id (str): Unique identifier for this API request
  - error_message (str): Error description (if success is False)
  

**Raises**:

    FileError: If the write operation fails.
  

**Example**:

            ```python
            from agentbay import AgentBay

            # Initialize and create session
            agent_bay = AgentBay(api_key="your_api_key")
            result = agent_bay.create()
            if result.success:
                session = result.session

                # Write a new file (overwrite mode)
                write_result = session.file_system.write_file("/tmp/test.txt", "Hello, World!")
                if write_result.success:
                    print("File written successfully")
                    # Output: File written successfully
                    print(f"Request ID: {write_result.request_id}")
                    # Output: Request ID: 9E3F4A5B-2C6D-7E8F-9A0B-1C2D3E4F5A6B

                # Append to existing file
                append_result = session.file_system.write_file(
                    "/tmp/test.txt",
                    "
Appended content",
                    mode="append"
                )
                if append_result.success:
                    print("Content appended successfully")

                # Verify the content
                read_result = session.file_system.read_file("/tmp/test.txt")
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

    local_path: Local file path to upload
    remote_path: Remote file path to upload to
    content_type: Optional content type for the file
    wait: Whether to wait for the sync operation to complete
    wait_timeout: Timeout for waiting for sync completion
    poll_interval: Interval between polling for sync completion
    progress_cb: Callback for upload progress updates
  

**Returns**:

    UploadResult: Result of the upload operation
  

**Example**:

```python
from agentbay import AgentBay
from agentbay.session_params import CreateSessionParams, ContextSync

agent_bay = AgentBay(api_key="your_api_key")

def upload_file_example():
    try:
        # Create a session with context sync configuration
        context_sync = ContextSync(
            context_id="your_context_id",
            path="/workspace"
        )
        params = CreateSessionParams(context_syncs=[context_sync])
        result = agent_bay.create(params)

        if result.success:
            session = result.session

            # Upload a local file to remote path
            upload_result = session.file_system.upload_file(
                local_path="/local/path/to/file.txt",
                remote_path="/workspace/file.txt",
                content_type="text/plain",
                wait=True,
                wait_timeout=30.0
            )

            if upload_result.success:
                print(f"File uploaded successfully: {upload_result.path}")
                print(f"Bytes sent: {upload_result.bytes_sent}")
                print(f"HTTP status: {upload_result.http_status}")
            else:
                print(f"Upload failed: {upload_result.error}")

            session.delete()
    except Exception as e:
        print(f"Error: {e}")

upload_file_example()
```

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

    remote_path: Remote file path to download from
    local_path: Local file path to download to
    overwrite: Whether to overwrite existing local file
    wait: Whether to wait for the sync operation to complete
    wait_timeout: Timeout for waiting for sync completion
    poll_interval: Interval between polling for sync completion
    progress_cb: Callback for download progress updates
  

**Returns**:

    DownloadResult: Result of the download operation
  

**Example**:

```python
from agentbay import AgentBay
from agentbay.session_params import CreateSessionParams, ContextSync

agent_bay = AgentBay(api_key="your_api_key")

def download_file_example():
    try:
        # Create a session with context sync configuration
        context_sync = ContextSync(
            context_id="your_context_id",
            path="/workspace"
        )
        params = CreateSessionParams(context_syncs=[context_sync])
        result = agent_bay.create(params)

        if result.success:
            session = result.session

            # Download a remote file to local path
            download_result = session.file_system.download_file(
                remote_path="/workspace/file.txt",
                local_path="/local/path/to/file.txt",
                overwrite=True,
                wait=True,
                wait_timeout=30.0
            )

            if download_result.success:
                print(f"File downloaded successfully: {download_result.local_path}")
                print(f"Bytes received: {download_result.bytes_received}")
                print(f"HTTP status: {download_result.http_status}")
            else:
                print(f"Download failed: {download_result.error}")

            session.delete()
    except Exception as e:
        print(f"Error: {e}")

download_file_example()
```

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

    path: The directory path to monitor for file changes.
    callback: Callback function that will be called with a list of FileChangeEvent
  objects when changes are detected.
    interval: Polling interval in seconds. Defaults to 0.5.
    stop_event: Optional threading.Event to stop the monitoring. If not provided,
  a new Event will be created and returned via the thread object.
  

**Returns**:

    threading.Thread: The monitoring thread. Call thread.start() to begin monitoring.
  Use the thread's stop_event attribute to stop monitoring.
  

**Example**:

```python
from agentbay import AgentBay
import time

agent_bay = AgentBay(api_key="your_api_key")

def demonstrate_watch_directory():
    try:
        result = agent_bay.create()
        if result.success:
            session = result.session

            # Create a test directory
            session.file_system.create_directory("/tmp/watch_test")

            # Define callback function
            def on_file_change(events):
                for event in events:
                    print(f"{event.event_type}: {event.path} ({event.path_type})")

            # Start monitoring
            monitor_thread = session.file_system.watch_directory(
                path="/tmp/watch_test",
                callback=on_file_change,
                interval=0.5
            )
            monitor_thread.start()

            # Create some test files to trigger events
            session.file_system.write_file("/tmp/watch_test/test1.txt", "content 1")
            time.sleep(1)
            session.file_system.write_file("/tmp/watch_test/test2.txt", "content 2")
            time.sleep(1)

            # Stop monitoring
            monitor_thread.stop_event.set()
            monitor_thread.join()

            session.delete()
    except Exception as e:
        print(f"Error: {e}")

demonstrate_watch_directory()
```

## Related Resources

- [Session API Reference](session.md)
- [Command API Reference](command.md)

---

*Documentation generated automatically from source code using pydoc-markdown.*
