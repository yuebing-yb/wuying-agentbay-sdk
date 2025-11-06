# Class: ContextManager

## 🗂️ Related Tutorial

- [Data Persistence Guide](../../../../../docs/guides/common-features/basics/data-persistence.md) - Learn about context management and data persistence

## 🗂️ Related Tutorial

- [Data Persistence Guide](../../../../../docs/guides/common-features/basics/data-persistence.md) - Learn about context management and data persistence

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
| :------ | :------ | :---## Related Resources

- [Context API Reference](context.md)
- [Session API Reference](session.md)


## Related Resources

- [Context API Reference](context.md)
- [Session API Reference](session.md)


--- |
| `contextId?` | `string` | `undefined` |
| `path?` | `string` | `undefined` |
| `mode?` | `string` | `undefined` |
| `callback?` | ``SyncCallback`` | `undefined` |
| `maxRetries` | `number` | `150` |
| `retryInterval` | `number` | `1500` |

#### Returns

`Promise`\<``ContextSyncResult``\>
