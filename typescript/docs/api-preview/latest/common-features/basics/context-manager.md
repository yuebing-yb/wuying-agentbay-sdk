# Class: ContextManager

## Table of contents

### Constructors

- [constructor](context-manager.md#constructor)

### Methods

- [info](context-manager.md#info)
- [infoWithParams](context-manager.md#infowithparams)
- [sync](context-manager.md#sync)

## Constructors

### constructor

• **new ContextManager**(`session`): [`ContextManager`](context-manager.md)

#### Parameters

| Name | Type |
| :------ | :------ |
| `session` | ``SessionInterface`` |

#### Returns

[`ContextManager`](context-manager.md)

## Methods

### info

▸ **info**(): `Promise`\<``ContextInfoResult``\>

#### Returns

`Promise`\<``ContextInfoResult``\>

___

### infoWithParams

▸ **infoWithParams**(`contextId?`, `path?`, `taskType?`): `Promise`\<``ContextInfoResult``\>

#### Parameters

| Name | Type |
| :------ | :------ |
| `contextId?` | `string` |
| `path?` | `string` |
| `taskType?` | `string` |

#### Returns

`Promise`\<``ContextInfoResult``\>

___

### sync

▸ **sync**(`contextId?`, `path?`, `mode?`, `callback?`, `maxRetries?`, `retryInterval?`): `Promise`\<``ContextSyncResult``\>

#### Parameters

| Name | Type | Default value |
| :------ | :------ | :------ |
| `contextId?` | `string` | `undefined` |
| `path?` | `string` | `undefined` |
| `mode?` | `string` | `undefined` |
| `callback?` | ``SyncCallback`` | `undefined` |
| `maxRetries` | `number` | `150` |
| `retryInterval` | `number` | `1500` |

#### Returns

`Promise`\<``ContextSyncResult``\>
