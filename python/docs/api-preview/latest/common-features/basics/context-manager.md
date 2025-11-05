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

#### sync

```python
async def sync(context_id: Optional[str] = None,
               path: Optional[str] = None,
               mode: Optional[str] = None,
               callback: Optional[Callable[[bool], None]] = None,
               max_retries: int = 150,
               retry_interval: int = 1500) -> ContextSyncResult
```

Synchronizes context with support for both async and sync calling patterns.

Usage:
# Async call - wait for completion
result = await session.context.sync()

# Sync call - immediate return with callback
session.context.sync(callback=lambda success: print(f"Done: {success}"))

**Arguments**:

- `context_id` - ID of the context to sync
- `path` - Path to sync
- `mode` - Sync mode
- `callback` - Optional callback function that receives success status
- `max_retries` - Maximum number of retries for polling (default: 150)
- `retry_interval` - Milliseconds to wait between retries (default: 1500)
  

**Returns**:

- `ContextSyncResult` - Result of the sync operation

---

*Documentation generated automatically from source code using pydoc-markdown.*
