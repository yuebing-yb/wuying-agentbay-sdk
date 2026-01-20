# Beta Volume API Reference

## Overview

The Volume module provides **block storage volumes (data disks)** that can be managed independently and mounted into sessions.

Typical use cases include:

- Persisting large datasets across sessions
- Reusing build artifacts and caches
- Attaching shared storage to multiple sessions over time

## Limitations and access

- This feature currently supports **Mobile Use** scenarios only.
- Volume is currently in **beta**. Both functionality and APIs may change in future releases.
- Volume currently works only with **custom images**. In the examples below, use placeholders like `image_xxx` to represent a custom `imageId`.
- Volume is currently available via **allowlist**. To request access, email `agentbay_dev@alibabacloud.com`.

## BetaVolumeService

```java
public class BetaVolumeService
```

Service for managing volumes.

### get

```java
public VolumeResult get(String name, String imageId, boolean create)
```

Get a volume by name. If `create` is true, the volume will be created when it does not exist.

**Parameters:**

- `name` (String): Volume name
- `imageId` (String): Image ID used for the request (required by the underlying API)
- `create` (boolean): Whether to create the volume if it doesn't exist

**Returns:**

- `VolumeResult`: Result containing the volume details

**Example:**

```java
VolumeResult vol = agentBay.getBetaVolume().get("demo-volume", "image_xxx", true);
if (!vol.isSuccess()) {
    throw new RuntimeException(vol.getErrorMessage());
}
System.out.println("VolumeId: " + vol.getVolume().getId());
```

### list

```java
public VolumeListResult list(String imageId, int maxResults, String nextToken)
```

List volumes for an image.

**Parameters:**

- `imageId` (String): Image ID (required)
- `maxResults` (int): Max items per page
- `nextToken` (String): Pagination token (optional)

**Returns:**

- `VolumeListResult`: Result containing a list of volumes and pagination info

### delete

```java
public OperationResult delete(String volumeId)
```

Delete a volume by ID.

**Parameters:**

- `volumeId` (String): Volume ID

**Returns:**

- `OperationResult`: Result indicating whether the operation succeeded

## Mount a volume during session creation

To mount a volume into a session, set the volume ID in `CreateSessionParams` when creating the session:

```java
// Get (or create) a volume
VolumeResult vol = agentBay.getBetaVolume().get("demo-volume", "image_xxx", true);
String volumeId = vol.getVolume().getId();

// Create a session with the volume mounted
CreateSessionParams params = new CreateSessionParams();
params.setImageId("image_xxx");
params.setBetaVolumeId(volumeId);

SessionResult sessionResult = agentBay.create(params);
sessionResult.getSession().getCommand().executeCommand("ls -la");
sessionResult.getSession().delete();
```

## Best Practices

1. **Use descriptive names**: Keep a stable mapping between volume name and `volumeId`.
2. **Mount early**: Prefer mounting during session creation for predictable behavior.
3. **Validate results**: Always check `success` and handle `errorMessage`.
4. **Clean up**: Delete sessions after use.

## Related APIs

- [CreateSessionParams](../basics/session-params.md) - Session configuration parameters
- [Session](../basics/session.md) - Session management
- [Command](../basics/command.md) - Command execution

