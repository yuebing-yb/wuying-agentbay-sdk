# Class: AgentBay

## 🚀 Related Tutorial

- [First Session Tutorial](../../../../../../docs/quickstart/first-session.md) - Get started with creating your first AgentBay session

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

Creates a new AgentBay session with specified configuration.

#### Parameters

| Name | Type | Description |
| :------ | :------ | :------ |
| `params` | ``CreateSessionParams`` | Configuration parameters for the session: - labels: Key-value pairs for session metadata - imageId: Custom image ID for the session environment - contextSync: Array of context synchronization configurations - browserContext: Browser-specific context configuration - isVpc: Whether to create a VPC session - policyId: Security policy ID - enableBrowserReplay: Enable browser session recording - extraConfigs: Additional configuration options - framework: Framework identifier for tracking |

#### Returns

`Promise`\<`SessionResult`\>

Promise resolving to SessionResult containing:
         - success: Whether session creation succeeded
         - session: Session object for interacting with the environment
         - requestId: Unique identifier for this API request
         - errorMessage: Error description if creation failed

**`Throws`**

Error if API call fails or authentication is invalid.

**`Example`**

```typescript
import { AgentBay } from 'wuying-agentbay-sdk';

const agentBay = new AgentBay({ apiKey: 'your_api_key' });

// Create session with default parameters
const result = await agentBay.create();
if (result.success) {
  const session = result.session;
  console.log(`Session ID: ${session.sessionId}`);
  // Output: Session ID: session-04bdwfj7u22a1s30g

  // Use the session
  const fileResult = await session.filesystem.readFile('/etc/hostname');
  console.log(`Hostname: ${fileResult.data}`);

  // Clean up
  await session.delete();
}

// Create session with custom parameters
const customResult = await agentBay.create({
  labels: { project: 'demo', env: 'test' },
  imageId: 'custom-image-v1',
  isVpc: true
});
if (customResult.success) {
  console.log('VPC session created');
  await customResult.session.delete();
}

// RECOMMENDED: Create a session with context synchronization
const contextResult = await agentBay.context.get('my-context', true);
if (contextResult.success && contextResult.context) {
  const contextSync = new ContextSync({
    contextId: contextResult.context.id,
    path: '/mnt/persistent',
    policy: SyncPolicy.default()
  });

  const syncResult = await agentBay.create({
    imageId: 'linux_latest',
    contextSync: [contextSync]
  });

  if (syncResult.success) {
    console.log(`Created session with context sync: ${syncResult.session.sessionId}`);
    await syncResult.session.delete();
  }
}
```

**`Remarks`**

**Behavior:**
- Creates a new isolated cloud runtime environment
- Automatically creates file transfer context if not provided
- Waits for context synchronization if contextSync is specified
- For VPC sessions, includes VPC-specific configuration
- Browser replay creates a separate recording context

**`See`**

[get](agentbay.md#get), [list](agentbay.md#list), [Session.delete](session.md#delete)

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
import { AgentBay } from 'wuying-agentbay-sdk';

const agentBay = new AgentBay({ apiKey: 'your_api_key' });

async function getSessionExample() {
  try {
    // First, create a session
    const createResult = await agentBay.create();
    if (!createResult.success) {
      console.error(`Failed to create session: ${createResult.errorMessage}`);
      return;
    }

    const sessionId = createResult.session.sessionId;
    console.log(`Created session with ID: ${sessionId}`);
    // Output: Created session with ID: session-xxxxxxxxxxxxxx

    // Retrieve the session by its ID
    const result = await agentBay.get(sessionId);
    if (result.success) {
      console.log(`Successfully retrieved session: ${result.session.sessionId}`);
      // Output: Successfully retrieved session: session-xxxxxxxxxxxxxx
      console.log(`Request ID: ${result.requestId}`);
      // Output: Request ID: XXXXXXXX-XXXX-XXXX-XXXX-XXXXXXXXXXXX

      // Use the retrieved session
      const fileResult = await result.session.fileSystem.readFile('/etc/hostname');
      if (fileResult.success) {
        console.log(`Hostname: ${fileResult.content}`);
      }

      // Clean up
      const deleteResult = await result.session.delete();
      if (deleteResult.success) {
        console.log(`Session ${sessionId} deleted successfully`);
        // Output: Session session-xxxxxxxxxxxxxx deleted successfully
      }
    } else {
      console.error(`Failed to get session: ${result.errorMessage}`);
    }
  } catch (error) {
    console.error('Error:', error);
  }
}

getSessionExample().catch(console.error);
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

### removeSession

▸ **removeSession**(`sessionId`): `void`

#### Parameters

| Name | Type | Description |
| :------ | :------ | :------ |
| `sessionId` | `string` | The ID of the session to remove. |

#### Returns

`void`

## Related Resources

- [Session API Reference](session.md)
- [Context API Reference](context.md)

