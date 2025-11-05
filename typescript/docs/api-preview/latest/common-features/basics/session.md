# Class: Session

Represents a session in the AgentBay cloud environment.

## Table of contents

### Constructors

- [constructor](session.md#constructor)

### Properties

- [agent](session.md#agent)
- [application](session.md#application)
- [browser](session.md#browser)
- [code](session.md#code)
- [command](session.md#command)
- [computer](session.md#computer)
- [context](session.md#context)
- [enableBrowserReplay](session.md#enablebrowserreplay)
- [fileSystem](session.md#filesystem)
- [fileTransferContextId](session.md#filetransfercontextid)
- [httpPort](session.md#httpport)
- [isVpc](session.md#isvpc)
- [mcpTools](session.md#mcptools)
- [mobile](session.md#mobile)
- [networkInterfaceIp](session.md#networkinterfaceip)
- [oss](session.md#oss)
- [recordContextId](session.md#recordcontextid)
- [resourceUrl](session.md#resourceurl)
- [sessionId](session.md#sessionid)
- [token](session.md#token)
- [ui](session.md#ui)
- [window](session.md#window)

### Methods

- [callMcpTool](session.md#callmcptool)
- [delete](session.md#delete)
- [findServerForTool](session.md#findserverfortool)
- [getAPIKey](session.md#getapikey)
- [getAgentBay](session.md#getagentbay)
- [getClient](session.md#getclient)
- [getHttpPort](session.md#gethttpport)
- [getLabels](session.md#getlabels)
- [getLink](session.md#getlink)
- [getLinkAsync](session.md#getlinkasync)
- [getNetworkInterfaceIp](session.md#getnetworkinterfaceip)
- [getSessionId](session.md#getsessionid)
- [getToken](session.md#gettoken)
- [info](session.md#info)
- [isVpcEnabled](session.md#isvpcenabled)
- [listMcpTools](session.md#listmcptools)
- [setLabels](session.md#setlabels)

## Constructors

### constructor

• **new Session**(`agentBay`, `sessionId`): [`Session`](session.md)

Initialize a Session object.

#### Parameters

| Name | Type | Description |
| :------ | :------ | :------ |
| `agentBay` | [`AgentBay`](agentbay.md) | The AgentBay instance that created this session. |
| `sessionId` | `string` | The ID of this session. |

#### Returns

[`Session`](session.md)

## Properties

### agent

• **agent**: [`Agent`](../advanced/agent.md)

___

### application

• **application**: [`Application`](../../computer-use/application.md)

___

### browser

• **browser**: [`Browser`](../../browser-use/browser.md)

___

### code

• **code**: [`Code`](../../codespace/code.md)

___

### command

• **command**: [`Command`](command.md)

___

### computer

• **computer**: [`Computer`](../../computer-use/computer.md)

___

### context

• **context**: [`ContextManager`](context-manager.md)

___

### enableBrowserReplay

• **enableBrowserReplay**: `boolean` = `false`

___

### fileSystem

• **fileSystem**: [`FileSystem`](filesystem.md)

___

### fileTransferContextId

• **fileTransferContextId**: ``null`` \| `string` = `null`

___

### httpPort

• **httpPort**: `string` = `""`

___

### isVpc

• **isVpc**: `boolean` = `false`

___

### mcpTools

• **mcpTools**: `McpTool`[] = `[]`

___

### mobile

• **mobile**: [`Mobile`](../../mobile-use/mobile.md)

___

### networkInterfaceIp

• **networkInterfaceIp**: `string` = `""`

___

### oss

• **oss**: [`Oss`](../advanced/oss.md)

___

### recordContextId

• **recordContextId**: ``null`` \| `string` = `null`

___

### resourceUrl

• **resourceUrl**: `string` = `""`

___

### sessionId

• **sessionId**: `string`

___

### token

• **token**: `string` = `""`

___

### ui

• **ui**: [`UI`](../../computer-use/ui.md)

___

### window

• **window**: [`WindowManager`](../../computer-use/window.md)

## Methods

### callMcpTool

▸ **callMcpTool**(`toolName`, `args`, `autoGenSession?`): `Promise`\<``McpToolResult``\>

Call an MCP tool and return the result in a format compatible with Agent.

#### Parameters

| Name | Type | Default value | Description |
| :------ | :------ | :------ | :------ |
| `toolName` | `string` | `undefined` | Name of the MCP tool to call |
| `args` | `any` | `undefined` | Arguments to pass to the tool |
| `autoGenSession` | `boolean` | `false` | Whether to automatically generate session if not exists (default: false) |

#### Returns

`Promise`\<``McpToolResult``\>

McpToolResult containing the response data

___

### delete

▸ **delete**(`syncContext?`): `Promise`\<``DeleteResult``\>

Delete this session.

#### Parameters

| Name | Type | Default value | Description |
| :------ | :------ | :------ | :------ |
| `syncContext` | `boolean` | `false` | Whether to sync context data (trigger file uploads) before deleting the session. Defaults to false. |

#### Returns

`Promise`\<``DeleteResult``\>

DeleteResult indicating success or failure and request ID

___

### findServerForTool

▸ **findServerForTool**(`toolName`): `string`

Find the server that provides the given tool.

#### Parameters

| Name | Type |
| :------ | :------ |
| `toolName` | `string` |

#### Returns

`string`

___

### getAPIKey

▸ **getAPIKey**(): `string`

Return the API key for this session.

#### Returns

`string`

___

### getAgentBay

▸ **getAgentBay**(): [`AgentBay`](agentbay.md)

Return the AgentBay instance that created this session.

#### Returns

[`AgentBay`](agentbay.md)

___

### getClient

▸ **getClient**(): ``Client``

Return the HTTP client for this session.

#### Returns

``Client``

___

### getHttpPort

▸ **getHttpPort**(): `string`

Return the HTTP port for VPC sessions.

#### Returns

`string`

___

### getLabels

▸ **getLabels**(): `Promise`\<`OperationResult`\>

Gets the labels for this session.

#### Returns

`Promise`\<`OperationResult`\>

OperationResult containing the labels as data and request ID

**`Throws`**

Error if the operation fails (matching Python SessionError)

___

### getLink

▸ **getLink**(`protocolType?`, `port?`, `options?`): `Promise`\<`OperationResult`\>

Get a link associated with the current session.

#### Parameters

| Name | Type | Description |
| :------ | :------ | :------ |
| `protocolType?` | `string` | Optional protocol type to use for the link |
| `port?` | `number` | Optional port to use for the link (must be in range [30100, 30199]) |
| `options?` | `string` | - |

#### Returns

`Promise`\<`OperationResult`\>

OperationResult containing the link as data and request ID

**`Throws`**

Error if the operation fails (matching Python SessionError)

___

### getLinkAsync

▸ **getLinkAsync**(`protocolType?`, `port?`, `options?`): `Promise`\<`OperationResult`\>

Asynchronously get a link associated with the current session.

#### Parameters

| Name | Type | Description |
| :------ | :------ | :------ |
| `protocolType?` | `string` | Optional protocol type to use for the link |
| `port?` | `number` | Optional port to use for the link (must be in range [30100, 30199]) |
| `options?` | `string` | - |

#### Returns

`Promise`\<`OperationResult`\>

OperationResult containing the link as data and request ID

**`Throws`**

Error if the operation fails (matching Python SessionError)

___

### getNetworkInterfaceIp

▸ **getNetworkInterfaceIp**(): `string`

Return the network interface IP for VPC sessions.

#### Returns

`string`

___

### getSessionId

▸ **getSessionId**(): `string`

Return the session_id for this session.

#### Returns

`string`

___

### getToken

▸ **getToken**(): `string`

Return the token for VPC sessions.

#### Returns

`string`

___

### info

▸ **info**(): `Promise`\<`OperationResult`\>

Gets information about this session.

#### Returns

`Promise`\<`OperationResult`\>

OperationResult containing the session information as data and request ID

**`Throws`**

Error if the operation fails (matching Python SessionError)

___

### isVpcEnabled

▸ **isVpcEnabled**(): `boolean`

Return whether this session uses VPC resources.

#### Returns

`boolean`

___

### listMcpTools

▸ **listMcpTools**(`imageId?`): `Promise`\<`McpToolsResult`\>

List MCP tools available for this session.

#### Parameters

| Name | Type | Description |
| :------ | :------ | :------ |
| `imageId?` | `string` | Optional image ID, defaults to session's imageId or "linux_latest" |

#### Returns

`Promise`\<`McpToolsResult`\>

McpToolsResult containing tools list and request ID

___

### setLabels

▸ **setLabels**(`labels`): `Promise`\<`OperationResult`\>

Sets the labels for this session.

#### Parameters

| Name | Type | Description |
| :------ | :------ | :------ |
| `labels` | `Record`\<`string`, `string`\> | The labels to set for the session. |

#### Returns

`Promise`\<`OperationResult`\>

OperationResult indicating success or failure with request ID

**`Throws`**

Error if the operation fails (matching Python SessionError)
