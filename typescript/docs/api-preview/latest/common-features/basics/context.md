# Class: ContextService

## 💾 Related Tutorial

- [Data Persistence Guide](../../../../../docs/guides/common-features/basics/data-persistence.md) - Learn about context management and data persistence

Provides methods to manage persistent contexts in the AgentBay cloud environment.

## Table of contents

### Constructors

- [constructor](context.md#constructor)

### Methods

- [clear](context.md#clear)
- [clearAsync](context.md#clearasync)
- [create](context.md#create)
- [delete](context.md#delete)
- [deleteFile](context.md#deletefile)
- [get](context.md#get)
- [getClearStatus](context.md#getclearstatus)
- [getFileDownloadUrl](context.md#getfiledownloadurl)
- [getFileUploadUrl](context.md#getfileuploadurl)
- [list](context.md#list)
- [listFiles](context.md#listfiles)
- [update](context.md#update)

## Constructors

### constructor

• **new ContextService**(`agentBay`): [`ContextService`](context.md)

Initialize the ContextService.

#### Parameters

| Name | Type | Description |
| :------ | :------ | :------ |
| `agentBay` | [`AgentBay`](agentbay.md) | The AgentBay instance. |

#### Returns

[`ContextService`](context.md)

## Methods

### clear

▸ **clear**(`contextId`, `timeout?`, `pollInterval?`): `Promise`\<`ClearContextResult`\>

Synchronously clear the context's persistent data and wait for the final result.

This method wraps the `clearAsync` and `getClearStatus` polling logic,
providing the simplest and most direct way to handle clearing tasks.

The clearing process transitions through the following states:
- "clearing": Data clearing is in progress
- "available": Clearing completed successfully (final success state)

#### Parameters

| Name | Type | Default value | Description |
| :------ | :------ | :------ | :------ |
| `contextId` | `string` | `undefined` | Unique ID of the context to clear. |
| `timeout` | `number` | `60` | (Optional) Timeout in seconds to wait for task completion, default is 60 seconds. |
| `pollInterval` | `number` | `2.0` | (Optional) Interval in seconds between status polls, default is 2 seconds. |

#### Returns

`Promise`\<`ClearContextResult`\>

A ClearContextResult object containing the final task result.
         The status field will be "available" on success, or other states if interrupted.

**`Throws`**

APIError - If the task fails to complete within the specified timeout.

___

### clearAsync

▸ **clearAsync**(`contextId`): `Promise`\<`ClearContextResult`\>

Asynchronously initiate a task to clear the context's persistent data.

This is a non-blocking method that returns immediately after initiating the clearing task
on the backend. The context's state will transition to "clearing" while the operation
is in progress.

#### Parameters

| Name | Type | Description |
| :------ | :------ | :------ |
| `contextId` | `string` | Unique ID of the context to clear. |

#### Returns

`Promise`\<`ClearContextResult`\>

A ClearContextResult object indicating the task has been successfully started,
         with status field set to "clearing".

**`Throws`**

APIError - If the backend API rejects the clearing request (e.g., invalid ID).

___

### create

▸ **create**(`name`): `Promise`\<`ContextResult`\>

Creates a new context with the given name.
Corresponds to Python's create() method

#### Parameters

| Name | Type | Description |
| :------ | :------ | :------ |
| `name` | `string` | The name for the new context. |

#### Returns

`Promise`\<`ContextResult`\>

ContextResult with created context data and requestId

___

### delete

▸ **delete**(`context`): `Promise`\<`OperationResult`\>

Deletes the specified context.
Corresponds to Python's delete() method

#### Parameters

| Name | Type | Description |
| :------ | :------ | :------ |
| `context` | ``Context`` | The Context object to delete. |

#### Returns

`Promise`\<`OperationResult`\>

OperationResult with requestId

___

### deleteFile

▸ **deleteFile**(`contextId`, `filePath`): `Promise`\<`OperationResult`\>

Delete a file in a context.

#### Parameters

| Name | Type |
| :------ | :------ |
| `contextId` | `string` |
| `filePath` | `string` |

#### Returns

`Promise`\<`OperationResult`\>

___

### get

▸ **get**(`name`, `create?`): `Promise`\<`ContextResult`\>

Gets a context by name. Optionally creates it if it doesn't exist.
Corresponds to Python's get() method

#### Parameters

| Name | Type | Default value | Description |
| :------ | :------ | :------ | :------ |
| `name` | `string` | `undefined` | The name of the context to get. |
| `create` | `boolean` | `false` | Whether to create the context if it doesn't exist. |

#### Returns

`Promise`\<`ContextResult`\>

ContextResult with context data and requestId

___

### getClearStatus

▸ **getClearStatus**(`contextId`): `Promise`\<`ClearContextResult`\>

Queries the status of the clearing task.

This method calls GetContext API directly and parses the raw response to extract
the state field, which indicates the current clearing status.

#### Parameters

| Name | Type | Description |
| :------ | :------ | :------ |
| `contextId` | `string` | ID of the context. |

#### Returns

`Promise`\<`ClearContextResult`\>

ClearContextResult object containing the current task status.

___

### getFileDownloadUrl

▸ **getFileDownloadUrl**(`contextId`, `filePath`): `Promise`\<`FileUrlResult`\>

Get a presigned download URL for a file in a context.

#### Parameters

| Name | Type |
| :------ | :------ |
| `contextId` | `string` |
| `filePath` | `string` |

#### Returns

`Promise`\<`FileUrlResult`\>

___

### getFileUploadUrl

▸ **getFileUploadUrl**(`contextId`, `filePath`): `Promise`\<`FileUrlResult`\>

Get a presigned upload URL for a file in a context.

#### Parameters

| Name | Type |
| :------ | :------ |
| `contextId` | `string` |
| `filePath` | `string` |

#### Returns

`Promise`\<`FileUrlResult`\>

___

### list

▸ **list**(`params?`): `Promise`\<`ContextListResult`\>

Lists all available contexts with pagination support.
Corresponds to Python's list() method

#### Parameters

| Name | Type | Description |
| :------ | :------ | :------ |
| `params?` | `ContextListParams` | Optional parameters for listing contexts. |

#### Returns

`Promise`\<`ContextListResult`\>

ContextListResult with contexts list and pagination information

___

### listFiles

▸ **listFiles**(`contextId`, `parentFolderPath`, `pageNumber?`, `pageSize?`): `Promise`\<`ContextFileListResult`\>

List files under a specific folder path in a context.

#### Parameters

| Name | Type | Default value |
| :------ | :------ | :------ |
| `contextId` | `string` | `undefined` |
| `parentFolderPath` | `string` | `undefined` |
| `pageNumber` | `number` | `1` |
| `pageSize` | `number` | `50` |

#### Returns

`Promise`\<`ContextFileListResult`\>

___

### update

▸ **update**(`context`): `Promise`\<`OperationResult`\>

Updates the specified context.
Corresponds to Python's update() method

#### Parameters

| Name | Type | Description |
| :------ | :------ | :---## Related Resources

- [Session API Reference](session.md)
- [Context Manager API Reference](context-manager.md)


--- |
| `context` | ``Context`` | The Context object to update. |

#### Returns

`Promise`\<`OperationResult`\>

OperationResult with updated context data and requestId
