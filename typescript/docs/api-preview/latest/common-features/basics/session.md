# Class: Session

## 🔧 Related Tutorial

- [Session Management Guide](../../../../../../docs/guides/common-features/basics/session-management.md) - Detailed tutorial on session lifecycle and management

Represents a session in the AgentBay cloud environment.

## Table of contents

### Constructors

- [constructor](session.md#constructor)

### Properties

- [agent](session.md#agent)
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

Deletes the session and releases all associated resources.

#### Parameters

| Name | Type | Default value | Description |
| :------ | :------ | :------ | :------ |
| `syncContext` | `boolean` | `false` | Whether to synchronize context data before deletion. If true, uploads all context data to OSS. If false but browser replay is enabled, syncs only the recording context. Defaults to false. |

#### Returns

`Promise`\<``DeleteResult``\>

Promise resolving to DeleteResult containing:
         - success: Whether deletion succeeded
         - requestId: Unique identifier for this API request
         - errorMessage: Error description if deletion failed

**`Throws`**

Error if the API call fails or network issues occur.

**`Example`**

```typescript
import { AgentBay } from 'wuying-agentbay-sdk';

// Initialize the SDK
const agentBay = new AgentBay({ apiKey: 'your_api_key' });

// Create a session
const result = await agentBay.create();
if (result.success) {
  const session = result.session;
  console.log(`Session ID: ${session.sessionId}`);
  // Output: Session ID: session-04bdwfj7u22a1s30g

  // Delete session without context sync
  const deleteResult = await session.delete();
  if (deleteResult.success) {
    console.log('Session deleted successfully');
    // Output: Session deleted successfully
  }
}

// Example with context synchronization
const result2 = await agentBay.create();
if (result2.success) {
  const session = result2.session;

  // Perform operations that modify context
  await session.filesystem.writeFile('/tmp/data.txt', 'Important data');

  // Delete with context sync to preserve data
  const deleteResult = await session.delete(true);
  if (deleteResult.success) {
    console.log('Session deleted and context synced');
    // Output: Session deleted and context synced
  }
}
```

**`Remarks`**

**Behavior:**
- If `syncContext=true`: Uploads all context data to OSS before deletion
- If `syncContext=false` but browser replay enabled: Syncs only recording context
- If `syncContext=false` and no browser replay: Deletes immediately without sync
- Continues with deletion even if context sync fails
- Releases all associated resources (browser, computer, mobile, etc.)

**Best Practices:**
- Use `syncContext=true` when you need to preserve context data for later retrieval
- For temporary sessions, use `syncContext=false` for faster cleanup
- Always call `delete()` when done to avoid resource leaks
- Handle deletion errors gracefully in production code

**`See`**

[info](session.md#info), [ContextManager.sync](context-manager.md#sync)

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

Retrieves an access link for the session.

#### Parameters

| Name | Type | Description |
| :------ | :------ | :------ |
| `protocolType?` | `string` | Protocol type for the link (optional, reserved for future use) |
| `port?` | `number` | Specific port number to access (must be in range [30100, 30199]). If not specified, returns the default session link. |
| `options?` | `string` | - |

#### Returns

`Promise`\<`OperationResult`\>

Promise resolving to OperationResult containing:
         - success: Whether the operation succeeded
         - data: String URL for accessing the session
         - requestId: Unique identifier for this API request
         - errorMessage: Error description if operation failed

**`Throws`**

Error if the API call fails or port is out of valid range.

**`Example`**

```typescript
import { AgentBay } from 'wuying-agentbay-sdk';

const agentBay = new AgentBay({ apiKey: 'your_api_key' });
const result = await agentBay.create();

if (result.success) {
  const session = result.session;

  // Get default session link
  const linkResult = await session.getLink();
  if (linkResult.success) {
    console.log(`Session link: ${linkResult.data}`);
    // Output: Session link: https://session-04bdwfj7u22a1s30g.agentbay.com
  }

  // Get link for specific port
  const portLinkResult = await session.getLink(undefined, 30150);
  if (portLinkResult.success) {
    console.log(`Port 30150 link: ${portLinkResult.data}`);
    // Output: Port 30150 link: https://session-04bdwfj7u22a1s30g-30150.agentbay.com
  }

  await session.delete();
}
```

**`Remarks`**

**Behavior:**
- Without port: Returns the default session access URL
- With port: Returns URL for accessing specific port-mapped service
- Port must be in range [30100, 30199] for port forwarding
- For ADB connections, use `session.mobile.getAdbUrl()` instead

**Best Practices:**
- Use default link for general session access
- Use port-specific links when you've started services on specific ports
- Validate port range before calling to avoid errors

**`See`**

[info](session.md#info), [Mobile.getAdbUrl](../../mobile-use/mobile.md#getadburl)

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

Retrieves detailed information about the current session.

#### Returns

`Promise`\<`OperationResult`\>

Promise resolving to OperationResult containing:
         - success: Whether the operation succeeded (always true if no exception)
         - data: SessionInfo object with the following fields:
           - sessionId (string): The session identifier
           - resourceUrl (string): URL for accessing the session
           - appId (string): Application ID (for desktop sessions)
           - authCode (string): Authentication code
           - connectionProperties (string): Connection configuration
           - resourceId (string): Resource identifier
           - resourceType (string): Type of resource (e.g., "Desktop")
           - ticket (string): Access ticket
         - requestId: Unique identifier for this API request
         - errorMessage: Error description if operation failed

**`Throws`**

Error if the API request fails or response is invalid.

**`Example`**

```typescript
import { AgentBay } from 'wuying-agentbay-sdk';

// Initialize the SDK
const agentBay = new AgentBay({ apiKey: 'your_api_key' });

// Create a session
const result = await agentBay.create();
if (result.success) {
  const session = result.session;

  // Get session information
  const infoResult = await session.info();
  if (infoResult.success) {
    const info = infoResult.data;
    console.log(`Session ID: ${info.sessionId}`);
    // Output: Session ID: session-04bdwfj7u22a1s30g

    console.log(`Resource URL: ${info.resourceUrl}`);
    // Output: Resource URL: https://session-04bdwfj7u22a1s30g.agentbay.aliyun.com

    console.log(`Resource Type: ${info.resourceType}`);
    // Output: Resource Type: Desktop

    console.log(`Request ID: ${infoResult.requestId}`);
    // Output: Request ID: 8D2C3E4F-1A5B-6C7D-8E9F-0A1B2C3D4E5F

    // Use resource_url for external access
    if (info.resourceUrl) {
      console.log(`Access session at: ${info.resourceUrl}`);
      // Output: Access session at: https://session-04bdwfj7u22a1s30g.agentbay.aliyun.com
    }
  }

  // Clean up
  await session.delete();
}
```

**`Remarks`**

**Behavior:**
- This method calls the GetMcpResource API to retrieve session metadata
- The returned SessionInfo contains:
  - sessionId: The session identifier
  - resourceUrl: URL for accessing the session
  - Desktop-specific fields (appId, authCode, connectionProperties, etc.)
    are populated from the DesktopInfo section of the API response
- Session info is retrieved from the AgentBay API in real-time
- The resourceUrl can be used for browser-based access
- Desktop-specific fields (appId, authCode) are only populated for desktop sessions
- This method does not modify the session state

**`See`**

[delete](session.md#delete), [getLink](session.md#getlink)

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

## Related Resources

- [FileSystem API Reference](filesystem.md)
- [Command API Reference](command.md)
- [Context API Reference](context.md)
- [Context Manager API Reference](context-manager.md)
- [OSS API Reference](../../common-features/advanced/oss.md)
- [Application API Reference](../../computer-use/application.md)

