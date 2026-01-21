# Volume API Reference

## 💾 Related Tutorial

- [Volume (Beta) Guide](../../../../../docs/guides/common-features/advanced/volume.md) - Manage and mount block storage volumes

## Overview

The Volume module provides block storage volumes (data disks) that can be managed independently and mounted into sessions.
It is useful for persisting large datasets or reusing artifacts across multiple sessions.

## Type BetaVolumeService

```go
type BetaVolumeService struct {
	AgentBay *AgentBay
}
```

BetaVolumeService provides beta methods to manage volumes.

### Methods

### BetaDelete

```go
func (vs *BetaVolumeService) BetaDelete(volumeID string) (*BetaOperationResult, error)
```

BetaDelete deletes a volume by ID.

### BetaGetByID

```go
func (vs *BetaVolumeService) BetaGetByID(volumeID string, imageID string) (*BetaVolumeResult, error)
```

BetaGetByID gets a volume by ID via ListVolumes(VolumeIds=[id]). imageID is required to match the
underlying Aliyun SDK request.

### BetaGetByName

```go
func (vs *BetaVolumeService) BetaGetByName(name string, imageID string, create bool) (*BetaVolumeResult, error)
```

BetaGetByName gets a volume by name. If create is true, creates the volume if it doesn't exist.
imageID is required to match the underlying Aliyun SDK request.

### BetaList

```go
func (vs *BetaVolumeService) BetaList(params *BetaListVolumesParams) (*BetaVolumeListResult, error)
```

BetaList lists volumes. imageID is required to match the underlying Aliyun SDK request.

## Type Volume

```go
type Volume struct {
	ID	string
	Name	string
	Status	string
}
```

Volume represents a block storage volume (data disk). Note: This is a beta feature and may change in
future releases.

## Type BetaVolumeResult

```go
type BetaVolumeResult struct {
	models.ApiResponse
	Success		bool
	Volume		*Volume
	ErrorMessage	string
}
```

BetaVolumeResult wraps volume operation result and RequestID.

## Type BetaVolumeListResult

```go
type BetaVolumeListResult struct {
	models.ApiResponse
	Success		bool
	Volumes		[]*Volume
	NextToken	string
	MaxResults	int32
	TotalCount	int32
	ErrorMessage	string
}
```

BetaVolumeListResult wraps volume list result and RequestID.

## Type BetaOperationResult

```go
type BetaOperationResult struct {
	models.ApiResponse
	Success		bool
	ErrorMessage	string
}
```

BetaOperationResult is a generic operation result (for delete).

## Type BetaListVolumesParams

```go
type BetaListVolumesParams struct {
	ImageID		string
	MaxResults	int32
	NextToken	string
	VolumeIds	[]*string
	VolumeName	string
}
```

BetaListVolumesParams contains parameters for listing volumes.

## Best Practices

1. Use descriptive volume names and keep a mapping between name and volumeId
2. Prefer mounting volumes at session creation time
3. Always validate success and handle error messages
4. Clean up sessions after use

## Related Resources

- [AgentBay API Reference](../basics/agentbay.md)
- [Session Params API Reference](../basics/session-params.md)
- [Session API Reference](../basics/session.md)
- [Command API Reference](../basics/command.md)

---

*Documentation generated automatically from Go source code.*
