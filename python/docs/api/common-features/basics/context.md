# Context API Reference

The Context API provides functionality for managing persistent storage contexts in the AgentBay cloud environment. Contexts allow you to persist data across sessions and reuse it in future sessions.

## Context Class

The `Context` class represents a persistent storage context in the AgentBay cloud environment.

### Properties

```python
id  # The unique identifier of the context
name  # The name of the context
created_at  # Date and time when the Context was created
last_used_at  # Date and time when the Context was last used
```

## ContextService Class

The `ContextService` class provides methods for managing persistent contexts in the AgentBay cloud environment.

### list

Lists all available contexts with pagination support.

```python
list(params: Optional[ContextListParams] = None) -> ContextListResult
```

**Parameters:**
- `params` (ContextListParams, optional): Pagination parameters. If None, default values are used (max_results=10).

**Returns:**
- `ContextListResult`: A result object containing the list of Context objects, pagination info, and request ID.

**Example:**
```python
from agentbay import AgentBay

# Initialize the SDK
agent_bay = AgentBay(api_key="your_api_key")

# List all contexts (using default pagination)
result = agent_bay.context.list()
if result.success:
    print(f"Found {len(result.contexts)} contexts:")
    # Expected: Found X contexts (where X is the number of contexts, max 10 by default)
    print(f"Request ID: {result.request_id}")
    # Expected: A valid UUID-format request ID
    for i, context in enumerate(result.contexts):
        if i < 3:  # Show first 3 contexts
            print(f"Context ID: {context.id}, Name: {context.name}")
            # Expected output: Context ID: SdkCtx-xxx, Name: xxx
else:
    print("Failed to list contexts")
```

### get

Gets a context by name. Optionally creates it if it doesn't exist.

```python
get(name: str, create: bool = False) -> ContextResult
```

**Parameters:**
- `name` (str): The name of the context to get.
- `create` (bool, optional): Whether to create the context if it doesn't exist. Defaults to False.

**Returns:**
- `ContextResult`: A result object containing the Context object and request ID.

**Example:**
```python
from agentbay import AgentBay

# Initialize the SDK
agent_bay = AgentBay(api_key="your_api_key")

# Get a context, creating it if it doesn't exist
result = agent_bay.context.get("my-persistent-context", create=True)
if result.success:
    context = result.context
    print(f"Context ID: {context.id}, Name: {context.name}")
    # Expected output: Context ID: SdkCtx-xxx, Name: my-persistent-context
    print(f"Request ID: {result.request_id}")
    # Expected: A valid UUID-format request ID
else:
    print(f"Failed to get context: {result.error_message}")
```

### create

Creates a new context.

```python
create(name: str) -> ContextResult
```

**Parameters:**
- `name` (str): The name of the context to create.

**Returns:**
- `ContextResult`: A result object containing the created Context object and request ID.

**Example:**
```python
from agentbay import AgentBay

# Initialize the SDK
agent_bay = AgentBay(api_key="your_api_key")

# Create a new context
result = agent_bay.context.create("my-new-context")
if result.success:
    context = result.context
    print(f"Created context with ID: {context.id}, Name: {context.name}")
    # Expected output: Created context with ID: SdkCtx-xxx, Name: my-new-context
    print(f"Request ID: {result.request_id}")
    # Expected: A valid UUID-format request ID
else:
    print(f"Failed to create context: {result.error_message}")
```

### delete

Deletes a context.

```python
delete(context: Context) -> OperationResult
```

**Parameters:**
- `context` (Context): The Context object to delete.

**Returns:**
- `OperationResult`: A result object containing success status and request ID.

**Example:**
```python
from agentbay import AgentBay

# Initialize the SDK
agent_bay = AgentBay(api_key="your_api_key")

# Get a context first
result = agent_bay.context.get("my-context")
if result.success and result.context:
    # Delete the context
    delete_result = agent_bay.context.delete(result.context)
    if delete_result.success:
        print(f"Context deleted successfully, Success: {delete_result.success}")
        # Expected output: Context deleted successfully, Success: True
        print(f"Request ID: {delete_result.request_id}")
        # Expected: A valid UUID-format request ID
    else:
        print(f"Failed to delete context: {delete_result.error_message}")
else:
    print(f"Failed to get context: {result.error_message}")
```

### update

Updates a context's properties.

```python
update(context: Context) -> OperationResult
```

**Parameters:**
- `context` (Context): The Context object with updated properties.

**Returns:**
- `OperationResult`: A result object containing success status and request ID.

**Example:**
```python
from agentbay import AgentBay

# Initialize the SDK
agent_bay = AgentBay(api_key="your_api_key")

# Get a context first
result = agent_bay.context.get("my-context")
if result.success and result.context:
    # Update the context name
    context = result.context
    context.name = "my-renamed-context"

    # Save the changes
    update_result = agent_bay.context.update(context)
    if update_result.success:
        print(f"Context updated successfully, Success: {update_result.success}")
        # Expected output: Context updated successfully, Success: True
        print(f"Request ID: {update_result.request_id}")
        # Expected: A valid UUID-format request ID
    else:
        print(f"Failed to update context: {update_result.error_message}")
else:
    print(f"Failed to get context: {result.error_message}")
```

### get_file_download_url

Gets a presigned download URL for a file in a context.

```python
get_file_download_url(context_id: str, file_path: str) -> FileUrlResult
```

**Parameters:**
- `context_id` (str): The ID of the context.
- `file_path` (str): The path to the file in the context.

**Returns:**
- `FileUrlResult`: A result object containing the presigned URL, expire time, and request ID.

### get_file_upload_url

Gets a presigned upload URL for a file in a context.

```python
get_file_upload_url(context_id: str, file_path: str) -> FileUrlResult
```

**Parameters:**
- `context_id` (str): The ID of the context.
- `file_path` (str): The path to the file in the context.

**Returns:**
- `FileUrlResult`: A result object containing the presigned URL, expire time, and request ID.

### list_files

Lists files under a specific folder path in a context.

```python
list_files(context_id: str, parent_folder_path: str, page_number: int, page_size: int) -> FileListResult
```

**Parameters:**
- `context_id` (str): The ID of the context.
- `parent_folder_path` (str): The parent folder path to list files from.
- `page_number` (int): The page number for pagination.
- `page_size` (int): The number of items per page.

**Returns:**
- `FileListResult`: A result object containing the list of files and request ID.

### delete_file

Deletes a file in a context.

```python
delete_file(context_id: str, file_path: str) -> OperationResult
```

**Parameters:**
- `context_id` (str): The ID of the context.
- `file_path` (str): The path to the file to delete.

**Returns:**
- `OperationResult`: A result object containing success status and request ID.

### clear

Clears the context's persistent data.

```python
clear(context_id: str, timeout: int = 60, poll_interval: float = 2.0) -> ClearContextResult
```

**Parameters:**
- `context_id` (str): The unique identifier of the context to clear.
- `timeout` (int, optional): Timeout in seconds to wait for task completion. Default is 60 seconds.
- `poll_interval` (float, optional): Interval in seconds between status polls. Default is 2.0 seconds.

**Returns:**
- `ClearContextResult`: A result object containing the final task result. The status field will be "available" on success.

**State Transitions:**
- "clearing": Data clearing is in progress
- "available": Clearing completed successfully (final success state)
- "in-use": Context is being used
- "pre-available": Context is being prepared

**Example:**
```python
from agentbay import AgentBay

# Initialize the SDK
agent_bay = AgentBay(api_key="your_api_key")

# Get a context first
result = agent_bay.context.get("my-context")
if result.success and result.context:
    context = result.context

    # Clear context data synchronously (wait for completion)
    clear_result = agent_bay.context.clear(context.id)
    if clear_result.success:
        print(f"Context data cleared successfully")
        print(f"Final Status: {clear_result.status}")
        # Expected output: Final Status: available
        print(f"Request ID: {clear_result.request_id}")
        # Expected: A valid UUID-format request ID
    else:
        print(f"Failed to clear context: {clear_result.error_message}")
else:
    print(f"Failed to get context: {result.error_message}")
```

### clear_async

Asynchronously initiates a task to clear the context's persistent data.

```python
clear_async(context_id: str) -> ClearContextResult
```

**Parameters:**
- `context_id` (str): The unique identifier of the context to clear.

**Returns:**
- `ClearContextResult`: A result object indicating the task has been successfully started, with status field set to "clearing".

**Example:**
```python
from agentbay import AgentBay

# Initialize the SDK
agent_bay = AgentBay(api_key="your_api_key")

# Get a context first
result = agent_bay.context.get("my-context")
if result.success and result.context:
    context = result.context

    # Start clearing context data asynchronously (non-blocking)
    clear_result = agent_bay.context.clear_async(context.id)
    if clear_result.success:
        print(f"Clear task started: Success={clear_result.success}, Status={clear_result.status}")
        # Expected output: Clear task started: Success=True, Status=clearing
        print(f"Request ID: {clear_result.request_id}")
        # Expected: A valid UUID-format request ID
    else:
        print(f"Failed to start clear: {clear_result.error_message}")
else:
    print(f"Failed to get context: {result.error_message}")
```

### get_clear_status

Queries the status of the clearing task.

```python
get_clear_status(context_id: str) -> ClearContextResult
```

**Parameters:**
- `context_id` (str): The unique identifier of the context to check.

**Returns:**
- `ClearContextResult`: A result object containing the current task status.

**State Transitions:**
- "clearing": Data clearing is in progress
- "available": Clearing completed successfully (final success state)
- "in-use": Context is being used
- "pre-available": Context is being prepared

**Example:**
```python
from agentbay import AgentBay

# Initialize the SDK
agent_bay = AgentBay(api_key="your_api_key")

# Get a context first
result = agent_bay.context.get("my-context")
if result.success and result.context:
    context = result.context

    # Check clearing status
    status_result = agent_bay.context.get_clear_status(context.id)
    if status_result.success:
        print(f"Current status: {status_result.status}")
        print(f"Request ID: {status_result.request_id}")
        # Expected: Current status: clearing/available/in-use/pre-available
    else:
        print(f"Failed to get status: {status_result.error_message}")
else:
    print(f"Failed to get context: {result.error_message}")
```

## Related Resources

- [Session API Reference](session.md)
- [ContextManager API Reference](context-manager.md)