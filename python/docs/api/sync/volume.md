# Volume API Reference

> **💡 Async Version**: This documentation covers the synchronous API. For async/await support, see [`AsyncVolume`](../async/async-volume.md) which provides the same functionality with async methods.

## 💾 Related Tutorial

- [Volume (Beta) Guide](../../../../docs/guides/common-features/advanced/volume.md) - Manage and mount block storage volumes

## Overview

The Volume module provides block storage volumes (data disks) that can be managed independently and mounted into sessions.
It is useful for persisting large datasets or reusing artifacts across multiple sessions.




## Volume

```python
class Volume()
```

Block storage volume (data disk).

Note: This is a beta feature and may change in future releases.

### __init__

```python
def __init__(self, id: str, name: str, status: str = "")
```

## VolumeResult

```python
class VolumeResult(ApiResponse)
```

### __init__

```python
def __init__(self, request_id: str = "",
             success: bool = False,
             volume: Optional[Volume] = None,
             error_message: str = "")
```

## VolumeListResult

```python
class VolumeListResult(ApiResponse)
```

### __init__

```python
def __init__(self, request_id: str = "",
             success: bool = False,
             volumes: Optional[List[Volume]] = None,
             next_token: str = "",
             max_results: int = 0,
             total_count: int = 0,
             error_message: str = "")
```

## SyncBetaVolumeService

```python
class SyncBetaVolumeService()
```

Beta volume service (trial feature).

### __init__

```python
def __init__(self, agent_bay: "AgentBay")
```

### create

```python
def create(name: str, image_id: str) -> VolumeResult
```

### get

```python
def get(*,
        volume_id: Optional[str] = None,
        name: Optional[str] = None,
        create: bool = False,
        image_id: str) -> VolumeResult
```

Get volume details.

- If volume_id is provided: uses ListVolumes(volume_ids=[volume_id])
- If name is provided: uses GetVolume(volume_name=name, allow_create=create)

image_id is required to match the underlying Aliyun SDK request.

### list

```python
def list(*,
         image_id: str,
         max_results: int = 10,
         next_token: str = "",
         volume_ids: Optional[List[str]] = None,
         volume_name: str = "") -> VolumeListResult
```

### delete

```python
def delete(volume_id: str) -> OperationResult
```

## Best Practices

1. Use descriptive volume names and keep a mapping between name and volumeId
2. Prefer mounting volumes at session creation time
3. Always validate success and handle error messages
4. Clean up sessions after use

## See Also

- [Synchronous vs Asynchronous API](../../../docs/guides/async-programming/sync-vs-async.md)

**Related APIs:**
- [AgentBay API Reference](./agentbay.md)
- [Session Params API Reference](./session-params.md)
- [Session API Reference](./session.md)
- [Command API Reference](./command.md)

---

*Documentation generated automatically from source code using pydoc-markdown.*
