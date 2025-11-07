# Class: ContextManager

## 🗂️ Related Tutorial

- [Data Persistence Guide](../../../../../../docs/guides/common-features/basics/data-persistence.md) - Learn about context management and data persistence

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

Gets information about context synchronization status for the current session.

#### Returns

`Promise`\<``ContextInfoResult``\>

Promise resolving to ContextInfoResult containing context status data and request ID

**`Throws`**

Error if the API call fails

**`Example`**

```typescript
import { AgentBay } from 'wuying-agentbay-sdk';

const agentBay = new AgentBay({ apiKey: 'your_api_key' });

async function getContextInfo() {
  try {
    const result = await agentBay.create();
    if (result.success) {
      const session = result.session;

      // Get context synchronization information
      const infoResult = await session.context.info();
      console.log(`Request ID: ${infoResult.requestId}`);
      // Output: Request ID: 41FC3D61-4AFB-1D2E-A08E-5737B2313234
      console.log(`Context status data count: ${infoResult.contextStatusData.length}`);
      // Output: Context status data count: 0

      if (infoResult.contextStatusData.length > 0) {
        infoResult.contextStatusData.forEach(item => {
          console.log(`Context ${item.contextId}: Status=${item.status}, Path=${item.path}`);
        });
      }

      await session.delete();
    }
  } catch (error) {
    console.error('Error:', error);
  }
}

getContextInfo().catch(console.error);
```

___

### infoWithParams

▸ **infoWithParams**(`contextId?`, `path?`, `taskType?`): `Promise`\<``ContextInfoResult``\>

Gets information about context synchronization status with optional filter parameters.

#### Parameters

| Name | Type | Description |
| :------ | :------ | :------ |
| `contextId?` | `string` | Optional context ID to filter results |
| `path?` | `string` | Optional path to filter results |
| `taskType?` | `string` | Optional task type to filter results (e.g., "upload", "download") |

#### Returns

`Promise`\<``ContextInfoResult``\>

Promise resolving to ContextInfoResult containing filtered context status data and request ID

**`Throws`**

Error if the API call fails

**`Example`**

```typescript
import { AgentBay } from 'wuying-agentbay-sdk';

const agentBay = new AgentBay({ apiKey: 'your_api_key' });

async function getContextInfoWithParams() {
  try {
    const result = await agentBay.create();
    if (result.success) {
      const session = result.session;

      // Get info for a specific context and path
      const infoResult = await session.context.infoWithParams(
        'SdkCtx-04bdw8o39bq47rv1t',
        '/mnt/persistent'
      );

      console.log(`Request ID: ${infoResult.requestId}`);
      // Output: Request ID: EB18A2D5-3C51-1F50-9FF1-8543CA328772
      infoResult.contextStatusData.forEach(item => {
        console.log(`Context ${item.contextId}: Status=${item.status}`);
      });

      await session.delete();
    }
  } catch (error) {
    console.error('Error:', error);
  }
}

getContextInfoWithParams().catch(console.error);
```

___

### sync

▸ **sync**(`contextId?`, `path?`, `mode?`, `callback?`, `maxRetries?`, `retryInterval?`): `Promise`\<``ContextSyncResult``\>

Synchronizes a context with the session. Supports both async and callback modes.

#### Parameters

| Name | Type | Default value | Description |
| :------ | :------ | :------ | :------ |
| `contextId?` | `string` | `undefined` | Optional context ID to synchronize |
| `path?` | `string` | `undefined` | Optional path where the context should be mounted |
| `mode?` | `string` | `undefined` | Optional synchronization mode (e.g., "upload", "download") |
| `callback?` | ``SyncCallback`` | `undefined` | Optional callback function. If provided, runs in background and calls callback when complete |
| `maxRetries` | `number` | `150` | Maximum number of retries for polling completion status (default: 150) |
| `retryInterval` | `number` | `1500` | Milliseconds to wait between retries (default: 1500) |

#### Returns

`Promise`\<``ContextSyncResult``\>

Promise resolving to ContextSyncResult with success status and request ID

**`Throws`**

Error if the API call fails

**`Example`**

```typescript
import { AgentBay } from 'wuying-agentbay-sdk';

const agentBay = new AgentBay({ apiKey: 'your_api_key' });

async function syncContext() {
  try {
    const result = await agentBay.create();
    if (result.success) {
      const session = result.session;

      // Get or create a context
      const contextResult = await agentBay.context.get('my-context', true);
      if (contextResult.context) {
        // Sync mode: wait for completion
        const syncResult = await session.context.sync(
          contextResult.context.id,
          '/mnt/persistent',
          'upload'
        );

        console.log(`Sync completed - Success: ${syncResult.success}`);
        // Output: Sync completed - Success: true
        console.log(`Request ID: ${syncResult.requestId}`);
        // Output: Request ID: 39B00280-B9DA-17D1-BCBB-9C577E057F0A
      }

      await session.delete();
    }
  } catch (error) {
    console.error('Error:', error);
  }
}

syncContext().catch(console.error);
```

**`Example`**

```typescript
// Callback mode: returns immediately
const syncResult = await session.context.sync(
  contextId,
  '/mnt/persistent',
  'upload',
  (success: boolean) => {
    if (success) {
      console.log('Context sync completed successfully');
    } else {
      console.log('Context sync failed or timed out');
    }
  }
);
console.log(`Sync triggered - Success: ${syncResult.success}`);
// Output: Sync triggered - Success: true
```

## Related Resources

- [Context API Reference](context.md)
- [Session API Reference](session.md)

