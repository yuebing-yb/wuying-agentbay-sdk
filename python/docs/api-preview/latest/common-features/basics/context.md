# Context API Reference

## 💾 Related Tutorial

- [Data Persistence Guide](../../../../../../docs/guides/common-features/basics/data-persistence.md) - Learn about context management and data persistence



## Context Objects

```python
class Context()
```

Represents a persistent storage context in the AgentBay cloud environment.

**Attributes**:

- `id` _str_ - The unique identifier of the context.
- `name` _str_ - The name of the context.
- `created_at` _str_ - Date and time when the Context was created.
- `last_used_at` _str_ - Date and time when the Context was last used.

## ContextResult Objects

```python
class ContextResult(ApiResponse)
```

Result of operations returning a Context.

## ContextListResult Objects

```python
class ContextListResult(ApiResponse)
```

Result of operations returning a list of Contexts.

## ContextFileEntry Objects

```python
class ContextFileEntry()
```

Represents a file item in a context.

## FileUrlResult Objects

```python
class FileUrlResult(ApiResponse)
```

Result of a presigned URL request.

## ContextFileListResult Objects

```python
class ContextFileListResult(ApiResponse)
```

Result of file listing operation.

## ClearContextResult Objects

```python
class ClearContextResult(OperationResult)
```

Result of context clear operations, including the real-time status.

**Attributes**:

- `request_id` _str_ - Unique identifier for the API request.
- `success` _bool_ - Whether the operation was successful.
- `error_message` _str_ - Error message if the operation failed.
- `status` _Optional[str]_ - Current status of the clearing task. This corresponds to the
  context's state field. Possible values:
  - "clearing": Context data is being cleared (in progress)
  - "available": Clearing completed successfully
  - Other values may indicate the context state after clearing
- `context_id` _Optional[str]_ - The unique identifier of the context being cleared.

## ContextListParams Objects

```python
class ContextListParams()
```

Parameters for listing contexts with pagination support.

## ContextService Objects

```python
class ContextService()
```

Provides methods to manage persistent contexts in the AgentBay cloud environment.

#### list

```python
def list(params: Optional[ContextListParams] = None) -> ContextListResult
```

Lists all available contexts with pagination support.

**Arguments**:

- `params` _Optional[ContextListParams], optional_ - Parameters for listing contexts.
  If None, defaults will be used.
  

**Returns**:

    ContextListResult: A result object containing the list of Context objects,
  pagination information, and request ID.
  

**Example**:

```python
from agentbay import AgentBay
from agentbay.context import ContextListParams

agent_bay = AgentBay(api_key="your_api_key")

def list_contexts():
    try:
        # List contexts with default pagination (max 10)
        result = agent_bay.context.list()
        if result.success:
            print(f"Total contexts: {result.total_count}")
            # Output: Total contexts: 25
            print(f"Contexts in this page: {len(result.contexts)}")
            # Output: Contexts in this page: 10
            for context in result.contexts:
                print(f"  - {context.name} (ID: {context.id})")
                # Output:   - my-context-1 (ID: ctx-04bdwfj7u22a1s30g)

            # List with custom pagination
            params = ContextListParams(max_results=5)
            result = agent_bay.context.list(params)
            if result.success:
                print(f"Got {len(result.contexts)} contexts")
                # Output: Got 5 contexts
                if result.next_token:
                    # Get next page
                    next_params = ContextListParams(
                        max_results=5,
                        next_token=result.next_token
                    )
                    next_result = agent_bay.context.list(next_params)
                    print(f"Next page has {len(next_result.contexts)} contexts")
                    # Output: Next page has 5 contexts
    except Exception as e:
        print(f"Error: {e}")

list_contexts()
```

#### get

```python
def get(name: Optional[str] = None,
        create: bool = False,
        context_id: Optional[str] = None) -> ContextResult
```

Gets a context by name or ID. Optionally creates it if it doesn't exist.

**Arguments**:

- `name` _Optional[str], optional_ - The name of the context to get. Defaults to None.
- `create` _bool, optional_ - Whether to create the context if it doesn't exist. Defaults to False.
- `context_id` _Optional[str], optional_ - The ID of the context to get. Defaults to None.
  

**Returns**:

    ContextResult: The ContextResult object containing the Context and request ID.
  - success (bool): True if the operation succeeded
  - context (Context): The context object (if success is True)
  - context_id (str): The ID of the context
  - request_id (str): Unique identifier for this API request
  - error_message (str): Error description (if success is False)
  

**Raises**:

    AgentBayError: If neither name nor context_id is provided, or if create=True with context_id.
  

**Example**:

```python
from agentbay import AgentBay

# Initialize the SDK
agent_bay = AgentBay(api_key="your_api_key")

# Get an existing context by name
result = agent_bay.context.get(name="my-context")
if result.success:
    context = result.context
    print(f"Context ID: {context.id}")
    # Output: Context ID: ctx-04bdwfj7u22a1s30g
    print(f"Context Name: {context.name}")
    # Output: Context Name: my-context

# Create a new context if it doesn't exist
result = agent_bay.context.get(name="new-context", create=True)
if result.success:
    print(f"Context created: {result.context.id}")
    # Output: Context created: ctx-04bdwfj7u22a1s30h
    print(f"Request ID: {result.request_id}")
    # Output: Request ID: 9E3F4A5B-2C6D-7E8F-9A0B-1C2D3E4F5A6B

# Get a context by ID
result = agent_bay.context.get(context_id="ctx-04bdwfj7u22a1s30g")
if result.success:
    print(f"Found context: {result.context.name}")

# Handle context not found
result = agent_bay.context.get(name="nonexistent-context")
if not result.success:
    print(f"Error: {result.error_message}")
    # Output: Error: Context not found
```
  

**Notes**:

  - Either name or context_id must be provided (not both)
  - When create=True, only name parameter is allowed
  - Created contexts are persistent and can be shared across sessions
  - Context names must be unique within your account
  

**See Also**:

  ContextService.list, ContextService.update, ContextService.delete

#### create

```python
def create(name: str) -> ContextResult
```

Creates a new context with the given name.

**Arguments**:

- `name` _str_ - The name for the new context.
  

**Returns**:

    ContextResult: The created ContextResult object with request ID.
  

**Example**:

```python
from agentbay import AgentBay

agent_bay = AgentBay(api_key="your_api_key")

def create_context():
    try:
        # Create a new context
        result = agent_bay.context.create("my-new-context")
        if result.success:
            context = result.context
            print(f"Context created successfully")
            # Output: Context created successfully
            print(f"Context ID: {context.id}")
            # Output: Context ID: ctx-04bdwfj7u22a1s30g
            print(f"Context Name: {context.name}")
            # Output: Context Name: my-new-context
            print(f"Request ID: {result.request_id}")
            # Output: Request ID: 9E3F4A5B-2C6D-7E8F-9A0B-1C2D3E4F5A6B
        else:
            print(f"Failed to create context: {result.error_message}")
    except Exception as e:
        print(f"Error: {e}")

create_context()
```

#### update

```python
def update(context: Context) -> OperationResult
```

Updates the specified context (currently only name can be updated).

**Arguments**:

- `context` _Context_ - The Context object to update. Must have id and name attributes.
  

**Returns**:

    OperationResult: Result object containing success status and request ID.
  - success (bool): True if the operation succeeded
  - data (str): Success message (if success is True)
  - request_id (str): Unique identifier for this API request
  - error_message (str): Error description (if success is False)
  

**Raises**:

    AgentBayError: If the context update fails.
  

**Example**:

```python
from agentbay import AgentBay
from agentbay.context import Context

# Initialize the SDK
agent_bay = AgentBay(api_key="your_api_key")

# Get an existing context
result = agent_bay.context.get(name="old-name")
if result.success:
    context = result.context
    print(f"Original name: {context.name}")
    # Output: Original name: old-name

    # Update the context name
    context.name = "new-name"
    update_result = agent_bay.context.update(context)
    if update_result.success:
        print(f"Context updated successfully")
        # Output: Context updated successfully
        print(f"Request ID: {update_result.request_id}")
        # Output: Request ID: 9E3F4A5B-2C6D-7E8F-9A0B-1C2D3E4F5A6B

    # Verify the update
    verify_result = agent_bay.context.get(context_id=context.id)
    if verify_result.success:
        print(f"New name: {verify_result.context.name}")
        # Output: New name: new-name

# Handle update failure
invalid_context = Context(id="invalid-id", name="new-name")
result = agent_bay.context.update(invalid_context)
if not result.success:
    print(f"Error: {result.error_message}")
    # Output: Error: Context not found
```
  

**Notes**:

  - Currently only the context name can be updated
  - Context ID cannot be changed
  - The context must exist before it can be updated
  - Updated name must be unique within your account
  

**See Also**:

  ContextService.get, ContextService.list, ContextService.delete

#### delete

```python
def delete(context: Context) -> OperationResult
```

Deletes the specified context.

**Arguments**:

- `context` _Context_ - The Context object to delete.
  

**Returns**:

    OperationResult: Result object containing success status and request ID.
  

**Example**:

```python
from agentbay import AgentBay

agent_bay = AgentBay(api_key="your_api_key")

def delete_context():
    try:
        # Get a context first
        result = agent_bay.context.get(name="my-context")
        if result.success and result.context:
            # Delete the context
            delete_result = agent_bay.context.delete(result.context)
            if delete_result.success:
                print("Context deleted successfully")
                # Output: Context deleted successfully
                print(f"Request ID: {delete_result.request_id}")
                # Output: Request ID: 9E3F4A5B-2C6D-7E8F-9A0B-1C2D3E4F5A6B
            else:
                print(f"Failed to delete context: {delete_result.error_message}")
        else:
            print(f"Failed to get context: {result.error_message}")
    except Exception as e:
        print(f"Error: {e}")

delete_context()
```

#### get\_file\_download\_url

```python
def get_file_download_url(context_id: str, file_path: str) -> FileUrlResult
```

Get a presigned download URL for a file in a context.

**Arguments**:

- `context_id` _str_ - The ID of the context.
- `file_path` _str_ - The path to the file in the context.
  

**Returns**:

    FileUrlResult: A result object containing the presigned URL, expire time, and request ID.
  

**Example**:

```python
from agentbay import AgentBay
import requests

agent_bay = AgentBay(api_key="your_api_key")

def download_context_file():
    try:
        # Get a context
        ctx_result = agent_bay.context.get(name="my-context", create=True)
        if ctx_result.success:
            context = ctx_result.context

            # Get download URL for a file
            url_result = agent_bay.context.get_file_download_url(
                context.id,
                "/data/output.txt"
            )
            if url_result.success:
                print(f"Download URL obtained")
                # Output: Download URL obtained
                print(f"URL expires in: {url_result.expire_time} seconds")
                # Output: URL expires in: 3600 seconds
                print(f"Request ID: {url_result.request_id}")
                # Output: Request ID: 9E3F4A5B-2C6D-7E8F-9A0B-1C2D3E4F5A6B

                # Download the file using the presigned URL
                response = requests.get(url_result.url)
                if response.status_code == 200:
                    content = response.text
                    print(f"Downloaded content: {content}")
                    # Output: Downloaded content: Hello World
            else:
                print(f"Failed to get download URL: {url_result.error_message}")
    except Exception as e:
        print(f"Error: {e}")

download_context_file()
```

#### get\_file\_upload\_url

```python
def get_file_upload_url(context_id: str, file_path: str) -> FileUrlResult
```

Get a presigned upload URL for a file in a context.

**Arguments**:

- `context_id` _str_ - The ID of the context.
- `file_path` _str_ - The path to the file in the context.
  

**Returns**:

    FileUrlResult: A result object containing the presigned URL, expire time, and request ID.
  

**Example**:

```python
from agentbay import AgentBay
import requests

agent_bay = AgentBay(api_key="your_api_key")

def upload_context_file():
    try:
        # Get a context
        ctx_result = agent_bay.context.get(name="my-context", create=True)
        if ctx_result.success:
            context = ctx_result.context

            # Get upload URL for a file
            url_result = agent_bay.context.get_file_upload_url(
                context.id,
                "/data/input.txt"
            )
            if url_result.success:
                print(f"Upload URL obtained")
                # Output: Upload URL obtained
                print(f"URL expires in: {url_result.expire_time} seconds")
                # Output: URL expires in: 3600 seconds
                print(f"Request ID: {url_result.request_id}")
                # Output: Request ID: 9E3F4A5B-2C6D-7E8F-9A0B-1C2D3E4F5A6B

                # Upload the file using the presigned URL
                file_content = "Hello World"
                response = requests.put(
                    url_result.url,
                    data=file_content.encode('utf-8'),
                    headers={'Content-Type': 'text/plain'}
                )
                if response.status_code in (200, 204):
                    print("File uploaded successfully")
                    # Output: File uploaded successfully
            else:
                print(f"Failed to get upload URL: {url_result.error_message}")
    except Exception as e:
        print(f"Error: {e}")

upload_context_file()
```

#### delete\_file

```python
def delete_file(context_id: str, file_path: str) -> OperationResult
```

Delete a file in a context.

**Arguments**:

- `context_id` _str_ - The ID of the context.
- `file_path` _str_ - The path to the file to delete.
  

**Returns**:

    OperationResult: A result object containing success status and request ID.
  

**Example**:

```python
from agentbay import AgentBay

agent_bay = AgentBay(api_key="your_api_key")

def delete_context_file():
    try:
        # Get a context
        ctx_result = agent_bay.context.get(name="my-context", create=True)
        if ctx_result.success:
            context = ctx_result.context

            # Delete a file from the context
            delete_result = agent_bay.context.delete_file(
                context.id,
                "/data/temp.txt"
            )
            if delete_result.success:
                print("File deleted successfully")
                # Output: File deleted successfully
                print(f"Request ID: {delete_result.request_id}")
                # Output: Request ID: 9E3F4A5B-2C6D-7E8F-9A0B-1C2D3E4F5A6B
            else:
                print(f"Failed to delete file: {delete_result.error_message}")
    except Exception as e:
        print(f"Error: {e}")

delete_context_file()
```

#### list\_files

```python
def list_files(context_id: str,
               parent_folder_path: str,
               page_number: int = 1,
               page_size: int = 50) -> ContextFileListResult
```

List files under a specific folder path in a context.

**Arguments**:

- `context_id` _str_ - The ID of the context.
- `parent_folder_path` _str_ - The parent folder path to list files from.
- `page_number` _int_ - The page number for pagination. Default is 1.
- `page_size` _int_ - The number of items per page. Default is 50.
  

**Returns**:

    ContextFileListResult: A result object containing the list of files and request ID.
  

**Example**:

```python
from agentbay import AgentBay

agent_bay = AgentBay(api_key="your_api_key")

def list_context_files():
    try:
        # Get a context
        ctx_result = agent_bay.context.get(name="my-context", create=True)
        if ctx_result.success:
            context = ctx_result.context

            # List files in the context
            files_result = agent_bay.context.list_files(
                context.id,
                "/data",
                page_number=1,
                page_size=10
            )
            if files_result.success:
                print(f"Found {files_result.count} files")
                # Output: Found 3 files
                print(f"Request ID: {files_result.request_id}")
                # Output: Request ID: 9E3F4A5B-2C6D-7E8F-9A0B-1C2D3E4F5A6B

                for file_entry in files_result.entries:
                    print(f"  - {file_entry.file_name} ({file_entry.file_path})")
                    # Output:   - input.txt (/data/input.txt)
                    print(f"    Size: {file_entry.size} bytes")
                    # Output:     Size: 1024 bytes
                    print(f"    Status: {file_entry.status}")
                    # Output:     Status: active
            else:
                print(f"Failed to list files: {files_result.error_message}")
    except Exception as e:
        print(f"Error: {e}")

list_context_files()
```

#### clear\_async

```python
def clear_async(context_id: str) -> ClearContextResult
```

Asynchronously initiate a task to clear the context's persistent data.

This is a non-blocking method that returns immediately after initiating the clearing task
on the backend. The context's state will transition to "clearing" while the operation
is in progress.

**Arguments**:

    context_id: Unique ID of the context to clear.
  

**Returns**:

  A ClearContextResult object indicating the task has been successfully started,
  with status field set to "clearing".
  

**Raises**:

    AgentBayError: If the backend API rejects the clearing request (e.g., invalid ID).
  

**Example**:

```python
from agentbay import AgentBay

agent_bay = AgentBay(api_key="your_api_key")

def clear_context_async():
    try:
        # Get a context
        result = agent_bay.context.get(name="my-context", create=True)
        if result.success:
            context = result.context

            # Start clearing context data asynchronously (non-blocking)
            clear_result = agent_bay.context.clear_async(context.id)
            if clear_result.success:
                print(f"Clear task started: Status={clear_result.status}")
                # Output: Clear task started: Status=clearing
                print(f"Request ID: {clear_result.request_id}")
                # Output: Request ID: 9E3F4A5B-2C6D-7E8F-9A0B-1C2D3E4F5A6B

                # You can now check status periodically using get_clear_status
            else:
                print(f"Failed to start clear: {clear_result.error_message}")
        else:
            print(f"Failed to get context: {result.error_message}")
    except Exception as e:
        print(f"Error: {e}")

clear_context_async()
```

#### get\_clear\_status

```python
def get_clear_status(context_id: str) -> ClearContextResult
```

Query the status of the clearing task.

This method calls GetContext API directly and parses the raw response to extract
the state field, which indicates the current clearing status.

**Arguments**:

    context_id: ID of the context.
  

**Returns**:

  ClearContextResult object containing the current task status.
  

**Example**:

```python
from agentbay import AgentBay
import time

agent_bay = AgentBay(api_key="your_api_key")

def check_clear_status():
    try:
        # Get a context
        result = agent_bay.context.get(name="my-context", create=True)
        if result.success:
            context = result.context

            # Start clearing asynchronously
            clear_result = agent_bay.context.clear_async(context.id)
            if clear_result.success:
                print("Clear task started, checking status...")
                # Output: Clear task started, checking status...

                # Poll for status until complete
                for i in range(30):
                    time.sleep(2)
                    status_result = agent_bay.context.get_clear_status(context.id)
                    if status_result.success:
                        print(f"Current status: {status_result.status}")
                        # Output: Current status: clearing (or available when done)
                        if status_result.status == "available":
                            print("Context cleared successfully!")
                            # Output: Context cleared successfully!
                            break
                    else:
                        print(f"Failed to get status: {status_result.error_message}")
                        break
            else:
                print(f"Failed to start clear: {clear_result.error_message}")
        else:
            print(f"Failed to get context: {result.error_message}")
    except Exception as e:
        print(f"Error: {e}")

check_clear_status()
```

#### clear

```python
def clear(context_id: str,
          timeout: int = 60,
          poll_interval: float = 2.0) -> ClearContextResult
```

Synchronously clear the context's persistent data and wait for the final result.

This method wraps the `clear_async` and `_get_clear_status` polling logic,
providing the simplest and most direct way to handle clearing tasks.

The clearing process transitions through the following states:
- "clearing": Data clearing is in progress
- "available": Clearing completed successfully (final success state)

**Arguments**:

    context_id: Unique ID of the context to clear.
    timeout: Timeout in seconds to wait for task completion. Defaults to 60.
    poll_interval: Interval in seconds between status polls. Defaults to 2.0.
  

**Returns**:

  ClearContextResult object containing the final task result.
  The status field will be "available" on success.
  

**Raises**:

    ClearanceTimeoutError: If the task fails to complete within the timeout.
    AgentBayError: If an API or network error occurs during execution.
  

**Example**:

```python
from agentbay import AgentBay
from agentbay.exceptions import ClearanceTimeoutError

agent_bay = AgentBay(api_key="your_api_key")

def clear_context_example():
    try:
        # Get or create a context
        result = agent_bay.context.get(name="my-context", create=True)
        if result.success:
            context = result.context
            print(f"Context ID: {context.id}")
            # Output: Context ID: ctx-04bdwfj7u22a1s30g

            # Clear the context data synchronously
            # This will wait for the clearing to complete
            clear_result = agent_bay.context.clear(
                context.id,
                timeout=60,
                poll_interval=2.0
            )

            if clear_result.success:
                print("Context cleared successfully")
                # Output: Context cleared successfully
                print(f"Final status: {clear_result.status}")
                # Output: Final status: available
                print(f"Request ID: {clear_result.request_id}")
                # Output: Request ID: 9E3F4A5B-2C6D-7E8F-9A0B-1C2D3E4F5A6B
            else:
                print(f"Failed to clear context: {clear_result.error_message}")
        else:
            print(f"Failed to get context: {result.error_message}")

    except ClearanceTimeoutError as e:
        print(f"Clearing timed out: {e}")
    except Exception as e:
        print(f"Error: {e}")

clear_context_example()
```

## Related Resources

- [Session API Reference](session.md)
- [Context Manager API Reference](context-manager.md)

---

*Documentation generated automatically from source code using pydoc-markdown.*
