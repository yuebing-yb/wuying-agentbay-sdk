# Context API Reference

```python
logger = get_logger("context")
```

## Context Objects

```python
class Context()
```

Represents a persistent storage context in the AgentBay cloud environment.

**Attributes**:

- `id` _str_ - The unique identifier of the context.
- `name` _str_ - The name of the context.
- `state` _str_ - **Deprecated.** This field is no longer used and will be removed in a future version.
- `created_at` _str_ - Date and time when the Context was created.
- `last_used_at` _str_ - Date and time when the Context was last used.
- `os_type` _str_ - **Deprecated.** This field is no longer used and will be removed in a future version.

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

- `ContextListResult` - A result object containing the list of Context objects,
  pagination information, and request ID.

#### get

```python
def get(name: Optional[str] = None,
        create: bool = False,
        context_id: Optional[str] = None) -> ContextResult
```

Gets a context by name or ID. Optionally creates it if it doesn't exist.

**Arguments**:

- `name` _Optional[str]_ - The name of the context to get.
- `create` _bool, optional_ - Whether to create the context if it doesn't exist.
- `context_id` _Optional[str]_ - The ID of the context to get.
  

**Returns**:

- `ContextResult` - The ContextResult object containing the Context and request
  ID.
  

**Notes**:

  Validation of parameter combinations is done by the server. If both name and
  context_id are provided, the request will be forwarded to the server for validation.

#### create

```python
def create(name: str) -> ContextResult
```

Creates a new context with the given name.

**Arguments**:

- `name` _str_ - The name for the new context.
  

**Returns**:

- `ContextResult` - The created ContextResult object with request ID.

#### update

```python
def update(context: Context) -> OperationResult
```

Updates the specified context.

**Arguments**:

- `context` _Context_ - The Context object to update.
  

**Returns**:

- `OperationResult` - Result object containing success status and request ID.

#### delete

```python
def delete(context: Context) -> OperationResult
```

Deletes the specified context.

**Arguments**:

- `context` _Context_ - The Context object to delete.
  

**Returns**:

- `OperationResult` - Result object containing success status and request ID.

#### get\_file\_download\_url

```python
def get_file_download_url(context_id: str, file_path: str) -> FileUrlResult
```

Get a presigned download URL for a file in a context.

#### get\_file\_upload\_url

```python
def get_file_upload_url(context_id: str, file_path: str) -> FileUrlResult
```

Get a presigned upload URL for a file in a context.

#### delete\_file

```python
def delete_file(context_id: str, file_path: str) -> OperationResult
```

Delete a file in a context.

#### list\_files

```python
def list_files(context_id: str,
               parent_folder_path: str,
               page_number: int = 1,
               page_size: int = 50) -> ContextFileListResult
```

List files under a specific folder path in a context.

#### clear\_async

```python
def clear_async(context_id: str) -> ClearContextResult
```

Asynchronously initiate a task to clear the context's persistent data.

This is a non-blocking method that returns immediately after initiating the clearing task
on the backend. The context's state will transition to "clearing" while the operation
is in progress.

**Arguments**:

- `context_id`: Unique ID of the context to clear.

**Raises**:

- `AgentBayError`: If the backend API rejects the clearing request (e.g., invalid ID).

**Returns**:

A ClearContextResult object indicating the task has been successfully started,
with status field set to "clearing".

#### get\_clear\_status

```python
def get_clear_status(context_id: str) -> ClearContextResult
```

Query the status of the clearing task.

This method calls GetContext API directly and parses the raw response to extract
the state field, which indicates the current clearing status.

**Arguments**:

- `context_id`: ID of the context.

**Returns**:

ClearContextResult object containing the current task status.

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

- `context_id`: Unique ID of the context to clear.
- `timeout`: (Optional) Timeout in seconds to wait for task completion, default is 60 seconds.
- `poll_interval`: (Optional) Interval in seconds between status polls, default is 2 seconds.

**Raises**:

- `ClearanceTimeoutError`: If the task fails to complete within the specified timeout.
- `AgentBayError`: If an API or network error occurs during execution.

**Returns**:

A ClearContextResult object containing the final task result.
The status field will be "available" on success, or other states if interrupted.

---

*Documentation generated automatically from source code using pydoc-markdown.*
