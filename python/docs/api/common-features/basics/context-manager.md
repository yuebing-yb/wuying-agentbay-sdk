# Context Manager API Reference

## ContextStatusData

```python
class ContextStatusData()
```

## ContextInfoResult

```python
class ContextInfoResult(ApiResponse)
```

## ContextSyncResult

```python
class ContextSyncResult(ApiResponse)
```

## ContextManager

```python
class ContextManager()
```

Manages context operations within a session in the AgentBay cloud environment.

The ContextManager provides methods to get information about context synchronization
status and to synchronize contexts with the session.

**Example**:

```python
result = agent_bay.create()
session = result.session
info_result = session.context.info()
print(f"Found {len(info_result.context_status_data)} context items")
session.delete()
```

### info

```python
def info(context_id: Optional[str] = None,
         path: Optional[str] = None,
         task_type: Optional[str] = None) -> ContextInfoResult
```

Get information about context synchronization status.

**Arguments**:

    context_id: Optional ID of the context to get information for
    path: Optional path where the context is mounted
    task_type: Optional type of task to get information for (e.g., "upload", "download")
  

**Returns**:

    ContextInfoResult: Result object containing context status data and request ID
  

**Example**:

```python
result = agent_bay.create()
session = result.session
info_result = session.context.info()
for item in info_result.context_status_data:
  print(f"Context {item.context_id}: {item.status}")
session.delete()
```

### sync

```python
async def sync(context_id: Optional[str] = None,
               path: Optional[str] = None,
               mode: Optional[str] = None,
               callback: Optional[Callable[[bool], None]] = None,
               max_retries: int = 150,
               retry_interval: int = 1500) -> ContextSyncResult
```

Synchronize a context with the session.

This method supports two modes:
- Async mode (default): When called with await, it waits for the sync operation to complete
- Callback mode: When a callback is provided, it returns immediately and calls the callback when complete

**Arguments**:

    context_id: Optional ID of the context to synchronize
    path: Optional path where the context should be mounted
    mode: Optional synchronization mode (e.g., "upload", "download")
    callback: Optional callback function that receives success status. If provided, the method
  runs in background and calls callback when complete
    max_retries: Maximum number of retries for polling completion status (default: 150)
    retry_interval: Milliseconds to wait between retries (default: 1500)
  

**Returns**:

    ContextSyncResult: Result object containing success status and request ID
  

**Example**:

Async mode - waits for completion:
```python
result = agent_bay.create()
session = result.session
context = agent_bay.context.get('my-context', True).context
sync_result = await session.context.sync(context.id, "/mnt/data")
print(f"Sync success: {sync_result.success}")
session.delete()
```

Callback mode - returns immediately:
```python
result = agent_bay.create()
session = result.session

def on_complete(success: bool):
    print(f"Sync completed: {success}")

context = agent_bay.context.get('my-context', True).context
await session.context.sync(context.id, "/mnt/data", callback=on_complete)
session.delete()
```

---

*Documentation generated automatically from source code using pydoc-markdown.*
