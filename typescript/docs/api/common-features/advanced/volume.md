# Class: BetaVolumeService

## 💾 Related Tutorial

- [Volume (Beta) Guide](../../../../../docs/guides/common-features/advanced/volume.md) - Manage and mount block storage volumes

## Overview

The Volume module provides block storage volumes (data disks) that can be managed independently and mounted into sessions.
It is useful for persisting large datasets or reusing artifacts across multiple sessions.

## Table of contents


### Methods

- [create](#create)
- [delete](#delete)
- [get](#get)
- [list](#list)

## Methods

### create

▸ **create**(`name`, `imageId`): `Promise`\<``VolumeResult``\>

#### Parameters

| Name | Type |
| :------ | :------ |
| `name` | `string` |
| `imageId` | `string` |

#### Returns

`Promise`\<``VolumeResult``\>

___

### delete

▸ **delete**(`volumeId`): `Promise`\<\{ `errorMessage?`: `string` ; `requestId`: `string` ; `success`: `boolean`  }\>

#### Parameters

| Name | Type |
| :------ | :------ |
| `volumeId` | `string` |

#### Returns

`Promise`\<\{ `errorMessage?`: `string` ; `requestId`: `string` ; `success`: `boolean`  }\>

___

### get

▸ **get**(`params`): `Promise`\<``VolumeResult``\>

#### Parameters

| Name | Type |
| :------ | :------ |
| `params` | `Object` |
| `params.create?` | `boolean` |
| `params.imageId` | `string` |
| `params.name?` | `string` |
| `params.volumeId?` | `string` |

#### Returns

`Promise`\<``VolumeResult``\>

___

### list

▸ **list**(`params`): `Promise`\<``VolumeListResult``\>

#### Parameters

| Name | Type |
| :------ | :------ |
| `params` | `Object` |
| `params.imageId` | `string` |
| `params.maxResults?` | `number` |
| `params.nextToken?` | `string` |
| `params.volumeIds?` | `string`[] |
| `params.volumeName?` | `string` |

#### Returns

`Promise`\<``VolumeListResult``\>

## Best Practices

1. Use descriptive volume names and keep a mapping between name and volumeId
2. Prefer mounting volumes at session creation time
3. Always validate success and handle error messages
4. Clean up sessions after use


## Related Resources

- [AgentBay API Reference](../../common-features/basics/agentbay.md)
- [Session Params API Reference](../../common-features/basics/session-params.md)
- [Session API Reference](../../common-features/basics/session.md)
- [Command API Reference](../../common-features/basics/command.md)

