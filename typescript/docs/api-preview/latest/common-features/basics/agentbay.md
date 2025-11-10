# Class: AgentBay

## 🚀 Related Tutorial

- [First Session Tutorial](../../../../../../docs/quickstart/first-session.md) - Get started with creating your first AgentBay session

Main class for interacting with the AgentBay cloud runtime environment.

## Table of contents


### Properties


### Methods

- [create](agentbay.md#create)
- [delete](agentbay.md#delete)
- [get](agentbay.md#get)
- [list](agentbay.md#list)
- [removeSession](agentbay.md#removesession)

## Properties

```typescript
context: [`ContextService`](context.md)
```


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

**`Example`**

```typescript
import { AgentBay } from 'wuying-agentbay-sdk';

const agentBay = new AgentBay({ apiKey: 'your_api_key' });

async function createAndDeleteSession() {
  try {
    // Create a session
    const createResult = await agentBay.create();
    if (createResult.success) {
      const session = createResult.session;
      console.log(`Created session with ID: ${session.sessionId}`);

      // Use the session for operations...

      // Delete the session when done
      const deleteResult = await agentBay.delete(session);
      if (deleteResult.success) {
        console.log('Session deleted successfully');
      } else {
        console.log(`Failed to delete session: ${deleteResult.errorMessage}`);
      }
    }
  } catch (error) {
    console.error('Error:', error);
  }
}

createAndDeleteSession().catch(console.error);
```

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

Remove a session from the internal session cache.

This is an internal utility method that removes a session reference from the AgentBay client's
session cache without actually deleting the session from the cloud. Use this when you need to
clean up local references to a session that was deleted externally or no longer needed.

#### Parameters

| Name | Type | Description |
| :------ | :------ | :------ |
| `sessionId` | `string` | The ID of the session to remove from the cache. |

#### Returns

`void`

**`Example`**

```typescript
import { AgentBay } from 'wuying-agentbay-sdk';

const agentBay = new AgentBay({ apiKey: 'your_api_key' });

async function demonstrateRemoveSession() {
  try {
    // Create a session
    const result = await agentBay.create();
    if (result.success) {
      const session = result.session;
      console.log(`Created session with ID: ${session.sessionId}`);
      // Output: Created session with ID: session-xxxxxxxxxxxxxx

      // Delete the session from cloud
      await session.delete();

      // Remove the session reference from local cache
      agentBay.removeSession(session.sessionId);
      console.log('Session removed from cache');
      // Output: Session removed from cache
    }
  } catch (error) {
    console.error('Error:', error);
  }
}

demonstrateRemoveSession().catch(console.error);
```

**`Remarks`**

**Note:** This method only removes the session from the local cache. It does not delete the
session from the cloud. To delete a session from the cloud, use [delete](agentbay.md#delete) or
[Session.delete](session.md#delete).

**`See`**

[delete](agentbay.md#delete), [Session.delete](session.md#delete)

## Related Resources

- [Session API Reference](session.md)
- [Context API Reference](context.md)

