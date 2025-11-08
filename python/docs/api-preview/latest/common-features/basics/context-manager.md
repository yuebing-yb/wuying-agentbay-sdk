# Context Manager API Reference

```python
logger = get_logger("context_manager")
```

## ContextStatusData Objects

```python
class ContextStatusData()
```

#### from\_dict

```python
@classmethod
def from_dict(cls, data: Dict[str, Any]) -> "ContextStatusData"
```

## ContextInfoResult Objects

```python
class ContextInfoResult(ApiResponse)
```

## ContextSyncResult Objects

```python
class ContextSyncResult(ApiResponse)
```

## ContextManager Objects

```python
class ContextManager()
```

#### info

```python
def info(context_id: Optional[str] = None,
         path: Optional[str] = None,
         task_type: Optional[str] = None) -> ContextInfoResult
```

Get information about context synchronization status.

**Arguments**:

- `context_id` - Optional ID of the context to get information for
- `path` - Optional path where the context is mounted
- `task_type` - Optional type of task to get information for (e.g., "upload", "download")
  

**Returns**:

- `ContextInfoResult` - Result object containing context status data and request ID
  

**Example**:

```python
from agentbay import AgentBay

agent_bay = AgentBay(api_key="your_api_key")

def get_context_info():
    try:
        result = agent_bay.create()
        if result.success:
            session = result.session

            # Get context synchronization information
            info_result = session.context.info()
            print(f"Request ID: {info_result.request_id}")
            print(f"Context status data count: {len(info_result.context_status_data)}")

            if info_result.context_status_data:
                for item in info_result.context_status_data:
                    print(f"  Context {item.context_id}: Status={item.status}, "
                          f"Path={item.path}, TaskType={item.task_type}")
            else:
                print("No context synchronization tasks found")

            session.delete()
    except Exception as e:
        print(f"Error: {e}")

get_context_info()
```

#### sync

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

- `context_id` - Optional ID of the context to synchronize
- `path` - Optional path where the context should be mounted
- `mode` - Optional synchronization mode (e.g., "upload", "download")
- `callback` - Optional callback function that receives success status. If provided, the method
  runs in background and calls callback when complete
- `max_retries` - Maximum number of retries for polling completion status (default: 150)
- `retry_interval` - Milliseconds to wait between retries (default: 1500)
  

**Returns**:

- `ContextSyncResult` - Result object containing success status and request ID
  
  Example (Async mode - waits for completion):
    ```python
    import asyncio
    from agentbay import AgentBay

    agent_bay = AgentBay(api_key="your_api_key")

    async def sync_context_async():
        try:
            result = agent_bay.create()
            if result.success:
                session = result.session

                # Get or create a context
                context_result = agent_bay.context.get('my-context', True)
                if context_result.context:
                    # Trigger context synchronization and wait for completion
                    sync_result = await session.context.sync(
                        context_id=context_result.context_id,
                        path="/mnt/persistent",
                        mode="upload"
                    )

                    print(f"Sync completed - Success: {sync_result.success}")
                    print(f"Request ID: {sync_result.request_id}")

                session.delete()
        except Exception as e:
            print(f"Error: {e}")

    asyncio.run(sync_context_async())
    ```
  
  Example (Callback mode - returns immediately):
    ```python
    import asyncio
    from agentbay import AgentBay

    agent_bay = AgentBay(api_key="your_api_key")

    async def sync_context_with_callback():
        try:
            result = agent_bay.create()
            if result.success:
                session = result.session

                context_result = agent_bay.context.get('my-context', True)

                # Define a callback function
                def on_sync_complete(success: bool):
                    if success:
                        print("Context sync completed successfully")
                    else:
                        print("Context sync failed or timed out")

                # Trigger sync with callback - returns immediately
                sync_result = await session.context.sync(
                    context_id=context_result.context_id,
                    path="/mnt/persistent",
                    mode="upload",
                    callback=on_sync_complete,
                    max_retries=10,
                    retry_interval=1000
                )

                print(f"Sync triggered - Success: {sync_result.success}")
                print(f"Request ID: {sync_result.request_id}")

                # Wait a bit for callback to be called
                await asyncio.sleep(3)

                session.delete()
        except Exception as e:
            print(f"Error: {e}")

    asyncio.run(sync_context_with_callback())
    ```

---

*Documentation generated automatically from source code using pydoc-markdown.*
