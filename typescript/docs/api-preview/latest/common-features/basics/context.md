# Class: ContextService

## 💾 Related Tutorial

- [Data Persistence Guide](../../../../../../docs/guides/common-features/basics/data-persistence.md) - Learn about context management and data persistence

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

**`Example`**

```typescript
import { AgentBay } from 'wuying-agentbay-sdk';

const agentBay = new AgentBay({ apiKey: 'your_api_key' });

async function clearContext() {
  try {
    // Get an existing context
    const getResult = await agentBay.context.get('my-context');
    if (getResult.success && getResult.context) {
      const context = getResult.context;

      // Clear context data synchronously (wait for completion)
      const clearResult = await agentBay.context.clear(context.id);
      if (clearResult.success) {
        console.log('Context data cleared successfully');
        // Output: Context data cleared successfully
        console.log(`Final Status: ${clearResult.status}`);
        // Output: Final Status: available
        console.log(`Request ID: ${clearResult.requestId}`);
        // Output: Request ID: 9E3F4A5B-2C6D-7E8F-9A0B-1C2D3E4F5A6B
      } else {
        console.log(`Failed to clear context: ${clearResult.errorMessage}`);
      }
    } else {
      console.log(`Failed to get context: ${getResult.errorMessage}`);
    }
  } catch (error) {
    console.error('Error:', error);
  }
}

clearContext().catch(console.error);
```

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

**`Example`**

```typescript
import { AgentBay } from 'wuying-agentbay-sdk';

const agentBay = new AgentBay({ apiKey: 'your_api_key' });

async function clearContextAsync() {
  try {
    // Get an existing context
    const getResult = await agentBay.context.get('my-context');
    if (getResult.success && getResult.context) {
      const context = getResult.context;

      // Start clearing context data asynchronously (non-blocking)
      const clearResult = await agentBay.context.clearAsync(context.id);
      if (clearResult.success) {
        console.log(`Clear task started successfully`);
        // Output: Clear task started successfully
        console.log(`Status: ${clearResult.status}`);
        // Output: Status: clearing
        console.log(`Request ID: ${clearResult.requestId}`);
        // Output: Request ID: 9E3F4A5B-2C6D-7E8F-9A0B-1C2D3E4F5A6B
      } else {
        console.log(`Failed to start clear: ${clearResult.errorMessage}`);
      }
    } else {
      console.log(`Failed to get context: ${getResult.errorMessage}`);
    }
  } catch (error) {
    console.error('Error:', error);
  }
}

clearContextAsync().catch(console.error);
```

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

**`Example`**

```typescript
import { AgentBay } from 'wuying-agentbay-sdk';

const agentBay = new AgentBay({ apiKey: 'your_api_key' });

async function createContext() {
  try {
    // Create a new context
    const result = await agentBay.context.create('my-new-context');
    if (result.success) {
      const context = result.context;
      console.log('Context created successfully');
      // Output: Context created successfully
      console.log(`Context ID: ${context.id}`);
      // Output: Context ID: ctx-04bdwfj7u22a1s30g
      console.log(`Context Name: ${context.name}`);
      // Output: Context Name: my-new-context
      console.log(`Request ID: ${result.requestId}`);
      // Output: Request ID: 9E3F4A5B-2C6D-7E8F-9A0B-1C2D3E4F5A6B
    } else {
      console.log(`Failed to create context: ${result.errorMessage}`);
    }
  } catch (error) {
    console.error('Error:', error);
  }
}

createContext().catch(console.error);
```

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

**`Example`**

```typescript
import { AgentBay } from 'wuying-agentbay-sdk';

const agentBay = new AgentBay({ apiKey: 'your_api_key' });

async function deleteContext() {
  try {
    // Get an existing context
    const getResult = await agentBay.context.get('my-context');
    if (getResult.success && getResult.context) {
      const context = getResult.context;

      // Delete the context
      const deleteResult = await agentBay.context.delete(context);
      if (deleteResult.success) {
        console.log('Context deleted successfully');
        // Output: Context deleted successfully
        console.log(`Request ID: ${deleteResult.requestId}`);
        // Output: Request ID: 9E3F4A5B-2C6D-7E8F-9A0B-1C2D3E4F5A6B
      } else {
        console.log(`Failed to delete context: ${deleteResult.errorMessage}`);
      }
    } else {
      console.log(`Failed to get context: ${getResult.errorMessage}`);
    }
  } catch (error) {
    console.error('Error:', error);
  }
}

deleteContext().catch(console.error);
```

___

### deleteFile

▸ **deleteFile**(`contextId`, `filePath`): `Promise`\<`OperationResult`\>

Delete a file in a context.

#### Parameters

| Name | Type | Description |
| :------ | :------ | :------ |
| `contextId` | `string` | The ID of the context. |
| `filePath` | `string` | The path to the file to delete. |

#### Returns

`Promise`\<`OperationResult`\>

OperationResult indicating success or failure.

**`Example`**

```typescript
import { AgentBay } from 'wuying-agentbay-sdk';

const agentBay = new AgentBay({ apiKey: 'your_api_key' });

async function deleteContextFile() {
  try {
    // Get an existing context
    const contextResult = await agentBay.context.get('my-context');
    if (contextResult.success && contextResult.context) {
      const context = contextResult.context;

      // Delete a file from the context
      const deleteResult = await agentBay.context.deleteFile(
        context.id,
        '/data/myfile.txt'
      );

      if (deleteResult.success) {
        console.log('File deleted successfully');
        // Output: File deleted successfully
        console.log(`Request ID: ${deleteResult.requestId}`);
        // Output: Request ID: 9E3F4A5B-2C6D-7E8F-9A0B-1C2D3E4F5A6B
      } else {
        console.error(`Failed to delete file: ${deleteResult.errorMessage}`);
      }
    }
  } catch (error) {
    console.error('Error:', error);
  }
}

deleteContextFile().catch(console.error);
```

___

### get

▸ **get**(`name`, `create?`): `Promise`\<`ContextResult`\>

Retrieves an existing context or creates a new one.

#### Parameters

| Name | Type | Default value | Description |
| :------ | :------ | :------ | :------ |
| `name` | `string` | `undefined` | The name of the context to retrieve or create. |
| `create` | `boolean` | `false` | If true, creates the context if it doesn't exist. Defaults to false. |

#### Returns

`Promise`\<`ContextResult`\>

Promise resolving to ContextResult containing the Context object.

**`Example`**

```typescript
import { AgentBay } from 'wuying-agentbay-sdk';

const agentBay = new AgentBay({ apiKey: 'your_api_key' });

async function getOrCreateContext() {
  try {
    // Get existing context or create if not exists
    const result = await agentBay.context.get('my-context', true);
    if (result.success) {
      const context = result.context;
      console.log(`Context ID: ${context.id}`);
      // Output: Context ID: ctx-04bdwfj7u22a1s30g
      console.log(`Context Name: ${context.name}`);
      // Output: Context Name: my-context
      console.log(`Request ID: ${result.requestId}`);
      // Output: Request ID: 9E3F4A5B-2C6D-7E8F-9A0B-1C2D3E4F5A6B
    } else {
      console.log(`Failed to get context: ${result.errorMessage}`);
    }
  } catch (error) {
    console.error('Error:', error);
  }
}

getOrCreateContext().catch(console.error);
```

**`See`**

[update](context.md#update), [list](context.md#list)

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

**`Example`**

```typescript
import { AgentBay } from 'wuying-agentbay-sdk';

const agentBay = new AgentBay({ apiKey: 'your_api_key' });

async function checkClearStatus() {
  try {
    // Get an existing context
    const getResult = await agentBay.context.get('my-context');
    if (getResult.success && getResult.context) {
      const context = getResult.context;

      // Check clearing status
      const statusResult = await agentBay.context.getClearStatus(context.id);
      if (statusResult.success) {
        console.log(`Current status: ${statusResult.status}`);
        // Output: Current status: clearing (or available/in-use/pre-available)
        console.log(`Request ID: ${statusResult.requestId}`);
        // Output: Request ID: 9E3F4A5B-2C6D-7E8F-9A0B-1C2D3E4F5A6B
      } else {
        console.log(`Failed to get status: ${statusResult.errorMessage}`);
      }
    } else {
      console.log(`Failed to get context: ${getResult.errorMessage}`);
    }
  } catch (error) {
    console.error('Error:', error);
  }
}

checkClearStatus().catch(console.error);
```

___

### getFileDownloadUrl

▸ **getFileDownloadUrl**(`contextId`, `filePath`): `Promise`\<`FileUrlResult`\>

Get a presigned download URL for a file in a context.

#### Parameters

| Name | Type | Description |
| :------ | :------ | :------ |
| `contextId` | `string` | The ID of the context. |
| `filePath` | `string` | The path to the file in the context. |

#### Returns

`Promise`\<`FileUrlResult`\>

FileUrlResult with the presigned URL and expiration time.

**`Example`**

```typescript
import { AgentBay } from 'wuying-agentbay-sdk';
import axios from 'axios';
import * as fs from 'fs';

const agentBay = new AgentBay({ apiKey: 'your_api_key' });

async function downloadFileFromContext() {
  try {
    // Get an existing context
    const contextResult = await agentBay.context.get('my-context');
    if (contextResult.success && contextResult.context) {
      const context = contextResult.context;

      // Get presigned download URL
      const urlResult = await agentBay.context.getFileDownloadUrl(
        context.id,
        '/data/myfile.txt'
      );

      if (urlResult.success) {
        console.log('Download URL obtained successfully');
        // Output: Download URL obtained successfully
        console.log(`URL expires at: ${urlResult.expireTime}`);
        // Output: URL expires at: 2024-01-01T12:00:00Z

        // Download file using the presigned URL
        const response = await axios.get(urlResult.url, {
          responseType: 'arraybuffer'
        });
        fs.writeFileSync('/local/path/downloaded.txt', response.data);
        console.log('File downloaded successfully');
        // Output: File downloaded successfully
      } else {
        console.error(`Failed to get download URL: ${urlResult.errorMessage}`);
      }
    }
  } catch (error) {
    console.error('Error:', error);
  }
}

downloadFileFromContext().catch(console.error);
```

___

### getFileUploadUrl

▸ **getFileUploadUrl**(`contextId`, `filePath`): `Promise`\<`FileUrlResult`\>

Get a presigned upload URL for a file in a context.

#### Parameters

| Name | Type | Description |
| :------ | :------ | :------ |
| `contextId` | `string` | The ID of the context. |
| `filePath` | `string` | The path to the file in the context. |

#### Returns

`Promise`\<`FileUrlResult`\>

FileUrlResult with the presigned URL and expiration time.

**`Example`**

```typescript
import { AgentBay } from 'wuying-agentbay-sdk';
import * as fs from 'fs';
import axios from 'axios';

const agentBay = new AgentBay({ apiKey: 'your_api_key' });

async function uploadFileToContext() {
  try {
    // Get or create a context
    const contextResult = await agentBay.context.get('my-context', true);
    if (contextResult.success && contextResult.context) {
      const context = contextResult.context;

      // Get presigned upload URL
      const urlResult = await agentBay.context.getFileUploadUrl(
        context.id,
        '/data/myfile.txt'
      );

      if (urlResult.success) {
        console.log('Upload URL obtained successfully');
        // Output: Upload URL obtained successfully
        console.log(`URL expires at: ${urlResult.expireTime}`);
        // Output: URL expires at: 2024-01-01T12:00:00Z

        // Upload file using the presigned URL
        const fileContent = fs.readFileSync('/local/path/file.txt');
        await axios.put(urlResult.url, fileContent, {
          headers: { 'Content-Type': 'text/plain' }
        });
        console.log('File uploaded successfully');
        // Output: File uploaded successfully
      } else {
        console.error(`Failed to get upload URL: ${urlResult.errorMessage}`);
      }
    }
  } catch (error) {
    console.error('Error:', error);
  }
}

uploadFileToContext().catch(console.error);
```

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

**`Example`**

```typescript
import { AgentBay } from 'wuying-agentbay-sdk';

const agentBay = new AgentBay({ apiKey: 'your_api_key' });

async function listContexts() {
  try {
    // List contexts with default pagination (max 10)
    const result = await agentBay.context.list();
    if (result.success) {
      console.log(`Total contexts: ${result.totalCount}`);
      // Output: Total contexts: 25
      console.log(`Contexts in this page: ${result.contexts.length}`);
      // Output: Contexts in this page: 10
      for (const context of result.contexts) {
        console.log(`  - ${context.name} (ID: ${context.id})`);
        // Output:   - my-context-1 (ID: ctx-04bdwfj7u22a1s30g)
      }

      // List with custom pagination
      const customResult = await agentBay.context.list({ maxResults: 5 });
      if (customResult.success) {
        console.log(`Got ${customResult.contexts.length} contexts`);
        // Output: Got 5 contexts
        if (customResult.nextToken) {
          // Get next page
          const nextResult = await agentBay.context.list({
            maxResults: 5,
            nextToken: customResult.nextToken
          });
          console.log(`Next page has ${nextResult.contexts.length} contexts`);
          // Output: Next page has 5 contexts
        }
      }
    }
  } catch (error) {
    console.error('Error:', error);
  }
}

listContexts().catch(console.error);
```

___

### listFiles

▸ **listFiles**(`contextId`, `parentFolderPath`, `pageNumber?`, `pageSize?`): `Promise`\<`ContextFileListResult`\>

List files under a specific folder path in a context.

#### Parameters

| Name | Type | Default value | Description |
| :------ | :------ | :------ | :------ |
| `contextId` | `string` | `undefined` | The ID of the context. |
| `parentFolderPath` | `string` | `undefined` | The parent folder path to list files from. |
| `pageNumber` | `number` | `1` | Page number for pagination (default: 1). |
| `pageSize` | `number` | `50` | Number of files per page (default: 50). |

#### Returns

`Promise`\<`ContextFileListResult`\>

ContextFileListResult with file entries and total count.

**`Example`**

```typescript
import { AgentBay } from 'wuying-agentbay-sdk';

const agentBay = new AgentBay({ apiKey: 'your_api_key' });

async function listContextFiles() {
  try {
    // Get an existing context
    const contextResult = await agentBay.context.get('my-context');
    if (contextResult.success && contextResult.context) {
      const context = contextResult.context;

      // List files in a folder
      const listResult = await agentBay.context.listFiles(
        context.id,
        '/data'
      );

      if (listResult.success) {
        console.log(`Found ${listResult.entries.length} files`);
        // Output: Found 5 files
        console.log(`Total count: ${listResult.count}`);
        // Output: Total count: 5

        for (const entry of listResult.entries) {
          console.log(`  - ${entry.fileName} (${entry.size} bytes)`);
          // Output:   - myfile.txt (1024 bytes)
        }

        console.log(`Request ID: ${listResult.requestId}`);
        // Output: Request ID: 9E3F4A5B-2C6D-7E8F-9A0B-1C2D3E4F5A6B
      } else {
        console.error(`Failed to list files: ${listResult.errorMessage}`);
      }
    }
  } catch (error) {
    console.error('Error:', error);
  }
}

listContextFiles().catch(console.error);
```

___

### update

▸ **update**(`context`): `Promise`\<`OperationResult`\>

Updates a context's name.

#### Parameters

| Name | Type | Description |
| :------ | :------ | :------ |
| `context` | ``Context`` | The Context object with updated name. |

#### Returns

`Promise`\<`OperationResult`\>

Promise resolving to OperationResult with success status.

**`Example`**

```typescript
import { AgentBay } from 'wuying-agentbay-sdk';

const agentBay = new AgentBay({ apiKey: 'your_api_key' });

async function updateContextName() {
  try {
    // Get an existing context
    const getResult = await agentBay.context.get('old-name');
    if (getResult.success && getResult.context) {
      const context = getResult.context;
      context.name = 'new-name';

      // Update the context
      const updateResult = await agentBay.context.update(context);
      if (updateResult.success) {
        console.log('Context name updated successfully');
        // Output: Context name updated successfully
        console.log(`Request ID: ${updateResult.requestId}`);
        // Output: Request ID: 9E3F4A5B-2C6D-7E8F-9A0B-1C2D3E4F5A6B
      } else {
        console.log(`Failed to update context: ${updateResult.errorMessage}`);
      }
    } else {
      console.log(`Failed to get context: ${getResult.errorMessage}`);
    }
  } catch (error) {
    console.error('Error:', error);
  }
}

updateContextName().catch(console.error);
```

**`See`**

[get](context.md#get), [list](context.md#list)

## Related Resources

- [Session API Reference](session.md)
- [Context Manager API Reference](context-manager.md)

