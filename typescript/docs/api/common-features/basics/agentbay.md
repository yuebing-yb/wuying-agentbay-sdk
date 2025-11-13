# Class: AgentBay

## 🚀 Related Tutorial

- [First Session Tutorial](../../../../../docs/quickstart/first-session.md) - Get started with creating your first AgentBay session

Main class for interacting with the AgentBay cloud runtime environment.

## Table of contents


### Properties


### Methods

- [create](#create)
- [delete](#delete)
- [get](#get)
- [list](#list)
- [pauseAsync](#pauseasync)
- [removeSession](#removesession)
- [resumeAsync](#resumeasync)

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
const agentBay = new AgentBay({ apiKey: 'your_api_key' });
const result = await agentBay.create({ labels: { project: 'demo' } });
if (result.success) {
  await result.session.filesystem.readFile('/etc/hostname');
  await result.session.delete();
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

[get](#get), [list](#list), [Session.delete](session.md#delete)

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
const agentBay = new AgentBay({ apiKey: 'your_api_key' });
const result = await agentBay.create();
if (result.success) {
  await agentBay.delete(result.session);
}
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
const agentBay = new AgentBay({ apiKey: 'your_api_key' });
const createResult = await agentBay.create();
if (createResult.success) {
  const result = await agentBay.get(createResult.session.sessionId);
  await result.session?.filesystem.readFile('/etc/hostname');
  await result.session?.delete();
}
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
const result = await agentBay.list({ project: "demo" }, 1, 10);
if (result.success) {
  console.log(`Found ${result.sessionIds.length} sessions`);
}
```

___

### pauseAsync

▸ **pauseAsync**(`session`, `timeout?`, `pollInterval?`): `Promise`\<`SessionPauseResult`\>

Asynchronously pause a session, putting it into a dormant state.

This method directly calls the PauseSessionAsync API without waiting for the session
to reach the PAUSED state.

#### Parameters

| Name | Type | Default value | Description |
| :------ | :------ | :------ | :------ |
| `session` | [`Session`](session.md) | `undefined` | The session to pause. |
| `timeout` | `number` | `600` | Timeout in seconds to wait for the session to pause. Defaults to 600 seconds. |
| `pollInterval` | `number` | `2.0` | Interval in seconds between status polls. Defaults to 2.0 seconds. |

#### Returns

`Promise`\<`SessionPauseResult`\>

SessionPauseResult indicating success or failure and request ID

**`Example`**

```typescript
import { AgentBay } from 'wuying-agentbay-sdk';

const agentBay = new AgentBay({ apiKey: 'your_api_key' });

async function pauseSessionAsyncExample() {
  try {
    // Create a session
    const result = await agentBay.create();
    if (result.success) {
      const session = result.session;

      // Pause the session asynchronously
      const pauseResult = await agentBay.pauseAsync(session);
      if (pauseResult.success) {
        console.log("Session pause request submitted successfully");
        // Output: Session pause request submitted successfully
      } else {
        console.log(`Failed to pause session: ${pauseResult.errorMessage}`);
      }

      await session.delete();
    }
  } catch (error) {
    console.error('Error:', error);
  }
}

pauseSessionAsyncExample().catch(console.error);
```

**`Remarks`**

**Behavior:**
- This method does not wait for the session to reach the PAUSED state
- It only submits the pause request to the API
- The session state transitions from RUNNING -> PAUSING -> PAUSED
- Paused sessions consume fewer resources but maintain their state

**`See`**

[resumeAsync](agentbay.md#resumeasync), [Session.pauseAsync](session.md#pauseasync)

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

