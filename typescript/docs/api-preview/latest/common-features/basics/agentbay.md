# Class: AgentBay

## 🚀 Related Tutorial

- [First Session Tutorial](../../../../../docs/quickstart/first-session.md) - Get started with creating your first AgentBay session

Main class for interacting with the AgentBay cloud runtime environment.

## Table of contents

### Constructors

- [constructor](agentbay.md#constructor)

### Properties

- [context](agentbay.md#context)

### Methods

- [create](agentbay.md#create)
- [delete](agentbay.md#delete)
- [get](agentbay.md#get)
- [getAPIKey](agentbay.md#getapikey)
- [getClient](agentbay.md#getclient)
- [getSession](agentbay.md#getsession)
- [list](agentbay.md#list)
- [listByLabels](agentbay.md#listbylabels)
- [removeSession](agentbay.md#removesession)

## Constructors

### constructor

• **new AgentBay**(`options?`): [`AgentBay`](agentbay.md)

Initialize the AgentBay client.

#### Parameters

| Name | Type | Description |
| :------ | :------ | :------ |
| `options` | `Object` | Configuration options |
| `options.apiKey?` | `string` | API key for authentication. If not provided, will look for AGENTBAY_API_KEY environment variable. |
| `options.config?` | ``Config`` | Custom configuration object. If not provided, will use environment-based configuration. |
| `options.envFile?` | `string` | Custom path to .env file. If not provided, will search upward from current directory. |

#### Returns

[`AgentBay`](agentbay.md)

## Properties

### context

• **context**: [`ContextService`](context.md)

Context service for managing persistent contexts.

## Methods

### create

▸ **create**(`params?`): `Promise`\<`SessionResult`\>

Create a new session in the AgentBay cloud environment.

#### Parameters

| Name | Type | Description |
| :------ | :------ | :------ |
| `params` | ``CreateSessionParams`` | Optional parameters for creating the session |

#### Returns

`Promise`\<`SessionResult`\>

SessionResult containing the created session and request ID

___

### delete

▸ **delete**(`session`, `syncContext?`): `Promise`\<``DeleteResult``\>

Delete a session by session object.

#### Parameters

| Name | Type | Default value | Description |
| :------ | :------ | :------ | :------ |
| `session` | [`Session`](session.md) | `undefined` | The session to delete. |
| `syncContext` | `boolean` | `false` | Whether to sync context data (trigger file uploads) before deleting the session. Defaults to false. |

#### Returns

`Promise`\<``DeleteResult``\>

DeleteResult indicating success or failure and request ID

___

### get

▸ **get**(`sessionId`): `Promise`\<`SessionResult`\>

Get a session by its ID.

This method retrieves a session by calling the GetSession API
and returns a SessionResult containing the Session object and request ID.

#### Parameters

| Name | Type | Description |
| :------ | :------ | :------ |
| `sessionId` | `string` | The ID of the session to retrieve |

#### Returns

`Promise`\<`SessionResult`\>

Promise resolving to SessionResult with the Session instance, request ID, and success status

**`Example`**

```typescript
const result = await agentBay.get("my-session-id");
if (result.success) {
  console.log(result.session.sessionId);
  console.log(result.requestId);
}
```

___

### getAPIKey

▸ **getAPIKey**(): `string`

#### Returns

`string`

___

### getClient

▸ **getClient**(): ``Client``

#### Returns

``Client``

___

### getSession

▸ **getSession**(`sessionId`): `Promise`\<`GetSessionResult`\>

Get session information by session ID.

#### Parameters

| Name | Type | Description |
| :------ | :------ | :------ |
| `sessionId` | `string` | The ID of the session to retrieve. |

#### Returns

`Promise`\<`GetSessionResult`\>

GetSessionResult containing session information

___

### list

▸ **list**(`labels?`, `page?`, `limit?`): `Promise`\<``SessionListResult``\>

Returns paginated list of session IDs filtered by labels.

#### Parameters

| Name | Type | Default value | Description |
| :------ | :------ | :------ | :------ |
| `labels` | `Record`\<`string`, `string`\> | `{}` | Optional labels to filter sessions (defaults to empty object) |
| `page?` | `number` | `undefined` | Optional page number for pagination (starting from 1, defaults to 1) |
| `limit` | `number` | `10` | Optional maximum number of items per page (defaults to 10) |

#### Returns

`Promise`\<``SessionListResult``\>

SessionListResult - Paginated list of session IDs that match the labels

**`Example`**

```typescript
const agentBay = new AgentBay({ apiKey: "your_api_key" });

// List all sessions
const result = await agentBay.list();

// List sessions with specific labels
const result = await agentBay.list({ project: "demo" });

// List sessions with pagination
const result = await agentBay.list({ "my-label": "my-value" }, 2, 10);

if (result.success) {
  for (const sessionId of result.sessionIds) {
    console.log(`Session ID: ${sessionId}`);
  }
  console.log(`Total count: ${result.totalCount}`);
  console.log(`Request ID: ${result.requestId}`);
}
```

___

### listByLabels

▸ **listByLabels**(`params?`): `Promise`\<``SessionListResult``\>

List sessions filtered by the provided labels with pagination support.
It returns sessions that match all the specified labels.

#### Parameters

| Name | Type | Description |
| :------ | :------ | :------ |
| `params?` | ``ListSessionParams`` | Parameters including labels and pagination options (required) |

#### Returns

`Promise`\<``SessionListResult``\>

API response with sessions list and pagination info

**`Deprecated`**

This method is deprecated and will be removed in a future version. Use list() instead.

**Breaking Change**: This method currently only accepts ListSessionParams parameters，

___

### removeSession

▸ **removeSession**(`sessionId`): `void`

#### Parameters

| Name | Type | Description |
| :------ | :------ | :---## Related Resources

- [Session API Reference](session.md)
- [Context API Reference](context.md)


--- |
| `sessionId` | `string` | The ID of the session to remove. |

#### Returns

`void`
