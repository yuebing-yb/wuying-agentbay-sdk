# Class: FileSystem

## 📁 Related Tutorial

- [File Operations Guide](../../../../../../docs/guides/common-features/basics/file-operations.md) - Complete guide to file system operations

Handles file operations in the AgentBay cloud environment.

## Table of contents

### Constructors

- [constructor](filesystem.md#constructor)

### Methods

- [createDirectory](filesystem.md#createdirectory)
- [downloadFile](filesystem.md#downloadfile)
- [editFile](filesystem.md#editfile)
- [getFileChange](filesystem.md#getfilechange)
- [getFileInfo](filesystem.md#getfileinfo)
- [listDirectory](filesystem.md#listdirectory)
- [moveFile](filesystem.md#movefile)
- [readFile](filesystem.md#readfile)
- [readMultipleFiles](filesystem.md#readmultiplefiles)
- [searchFiles](filesystem.md#searchfiles)
- [uploadFile](filesystem.md#uploadfile)
- [watchDirectory](filesystem.md#watchdirectory)
- [writeFile](filesystem.md#writefile)

## Constructors

### constructor

• **new FileSystem**(`session`): [`FileSystem`](filesystem.md)

Initialize a FileSystem object.

#### Parameters

| Name | Type | Description |
| :------ | :------ | :------ |
| `session` | [`Session`](session.md) | The Session instance that this FileSystem belongs to. |

#### Returns

[`FileSystem`](filesystem.md)

## Methods

### createDirectory

▸ **createDirectory**(`path`): `Promise`\<`BoolResult`\>

Creates a new directory at the specified path.
Corresponds to Python's create_directory() method

#### Parameters

| Name | Type | Description |
| :------ | :------ | :------ |
| `path` | `string` | Path to the directory to create. |

#### Returns

`Promise`\<`BoolResult`\>

BoolResult with creation result and requestId

**`Example`**

```typescript
import { AgentBay } from 'wuying-agentbay-sdk';

const agentBay = new AgentBay({ apiKey: 'your_api_key' });

async function demonstrateCreateDirectory() {
  try {
    const result = await agentBay.create();
    if (result.success) {
      const session = result.session;

      // Create a directory
      const createResult = await session.fileSystem.createDirectory('/tmp/mydir');
      if (createResult.success) {
        console.log('Directory created successfully');
        // Output: Directory created successfully
        console.log(`Request ID: ${createResult.requestId}`);
        // Output: Request ID: 9E3F4A5B-2C6D-7E8F-9A0B-1C2D3E4F5A6B
      }

      // Create nested directories
      const nestedResult = await session.fileSystem.createDirectory('/tmp/parent/child/grandchild');
      if (nestedResult.success) {
        console.log('Nested directories created');
      }

      await session.delete();
    }
  } catch (error) {
    console.error('Error:', error);
  }
}

demonstrateCreateDirectory().catch(console.error);
```

___

### downloadFile

▸ **downloadFile**(`remotePath`, `localPath`, `options?`): `Promise`\<`any`\>

Download a file from remote path to local path using pre-signed URLs.
This is a synchronous wrapper around the FileTransfer.download method.

#### Parameters

| Name | Type | Description |
| :------ | :------ | :------ |
| `remotePath` | `string` | Remote file path to download from |
| `localPath` | `string` | Local file path to download to |
| `options?` | `Object` | Optional parameters |
| `options.overwrite?` | `boolean` | - |
| `options.pollInterval?` | `number` | - |
| `options.progressCb?` | (`bytesReceived`: `number`) => `void` | - |
| `options.wait?` | `boolean` | - |
| `options.waitTimeout?` | `number` | - |

#### Returns

`Promise`\<`any`\>

DownloadResult with download result and requestId

**`Example`**

```typescript
import { AgentBay } from 'wuying-agentbay-sdk';
import * as fs from 'fs';

const agentBay = new AgentBay({ apiKey: 'your_api_key' });

async function demonstrateDownloadFile() {
  try {
    // Create session
    const result = await agentBay.create({
      imageId: 'code_latest'
    });

    if (result.success) {
      const session = result.session;

      // Create a file in the session
      await session.fileSystem.writeFile(
        '/workspace/remote_file.txt',
        'Content to download'
      );

      // Download the file
      const localPath = '/tmp/downloaded_file.txt';
      const downloadResult = await session.fileSystem.downloadFile(
        '/workspace/remote_file.txt',
        localPath
      );

      if (downloadResult.success) {
        console.log('File downloaded successfully');
        // Output: File downloaded successfully
        console.log(`Bytes received: ${downloadResult.bytesReceived}`);
        console.log(`Request ID (download URL): ${downloadResult.requestIdDownloadUrl}`);
        console.log(`Request ID (sync): ${downloadResult.requestIdSync}`);

        // Verify the downloaded file
        const content = fs.readFileSync(localPath, 'utf8');
        console.log(`Downloaded content: ${content}`);
        // Output: Downloaded content: Content to download
      } else {
        console.error(`Download failed: ${downloadResult.error}`);
      }

      await session.delete();
    }
  } catch (error) {
    console.error('Error:', error);
  }
}

demonstrateDownloadFile().catch(console.error);
```

___

### editFile

▸ **editFile**(`path`, `edits`, `dryRun?`): `Promise`\<`BoolResult`\>

Edits a file by replacing occurrences of oldText with newText.
Corresponds to Python's edit_file() method

#### Parameters

| Name | Type | Default value | Description |
| :------ | :------ | :------ | :------ |
| `path` | `string` | `undefined` | Path to the file to edit. |
| `edits` | \{ `newText`: `string` ; `oldText`: `string`  }[] | `undefined` | Array of edit operations, each containing oldText and newText. |
| `dryRun` | `boolean` | `false` | Optional: If true, preview changes without applying them. |

#### Returns

`Promise`\<`BoolResult`\>

BoolResult with edit result and requestId

**`Example`**

```typescript
import { AgentBay } from 'wuying-agentbay-sdk';

const agentBay = new AgentBay({ apiKey: 'your_api_key' });

async function demonstrateEditFile() {
  try {
    const result = await agentBay.create();
    if (result.success) {
      const session = result.session;

      // Create a test file
      await session.fileSystem.writeFile('/tmp/config.txt', 'DEBUG=false\\nLOG_LEVEL=info');

      // Edit the file with single replacement
      const edits = [{ oldText: 'DEBUG=false', newText: 'DEBUG=true' }];
      const editResult = await session.fileSystem.editFile('/tmp/config.txt', edits);
      if (editResult.success) {
        console.log('File edited successfully');
        // Output: File edited successfully
      }

      // Edit with multiple replacements
      const multiEdits = [
        { oldText: 'DEBUG=true', newText: 'DEBUG=false' },
        { oldText: 'LOG_LEVEL=info', newText: 'LOG_LEVEL=debug' }
      ];
      const multiEditResult = await session.fileSystem.editFile('/tmp/config.txt', multiEdits);
      if (multiEditResult.success) {
        console.log('Multiple edits applied');
      }

      // Preview changes with dry_run
      const dryRunResult = await session.fileSystem.editFile(
        '/tmp/config.txt',
        [{ oldText: 'debug', newText: 'trace' }],
        true
      );
      if (dryRunResult.success) {
        console.log('Dry run completed, no changes applied');
      }

      await session.delete();
    }
  } catch (error) {
    console.error('Error:', error);
  }
}

demonstrateEditFile().catch(console.error);
```

___

### getFileChange

▸ **getFileChange**(`path`): `Promise`\<``FileChangeResult``\>

Get file change information for the specified directory path

#### Parameters

| Name | Type |
| :------ | :------ |
| `path` | `string` |

#### Returns

`Promise`\<``FileChangeResult``\>

___

### getFileInfo

▸ **getFileInfo**(`path`): `Promise`\<`FileInfoResult`\>

Gets information about a file or directory.
Corresponds to Python's get_file_info() method

#### Parameters

| Name | Type | Description |
| :------ | :------ | :------ |
| `path` | `string` | Path to the file or directory to inspect. |

#### Returns

`Promise`\<`FileInfoResult`\>

FileInfoResult with file info and requestId

**`Example`**

```typescript
import { AgentBay } from 'wuying-agentbay-sdk';

const agentBay = new AgentBay({ apiKey: 'your_api_key' });

async function demonstrateGetFileInfo() {
  try {
    const result = await agentBay.create();
    if (result.success) {
      const session = result.session;

      // Create a test file
      await session.fileSystem.writeFile('/tmp/test.txt', 'Sample content');

      // Get file information
      const infoResult = await session.fileSystem.getFileInfo('/tmp/test.txt');
      if (infoResult.success) {
        console.log(`File info: ${JSON.stringify(infoResult.fileInfo)}`);
        // Output: File info: {"size": 14, "isDirectory": false, ...}
        console.log(`Size: ${infoResult.fileInfo.size} bytes`);
        // Output: Size: 14 bytes
        console.log(`Is directory: ${infoResult.fileInfo.isDirectory}`);
        // Output: Is directory: false
      }

      // Get directory information
      await session.fileSystem.createDirectory('/tmp/mydir');
      const dirInfo = await session.fileSystem.getFileInfo('/tmp/mydir');
      if (dirInfo.success) {
        console.log(`Is directory: ${dirInfo.fileInfo.isDirectory}`);
        // Output: Is directory: true
      }

      await session.delete();
    }
  } catch (error) {
    console.error('Error:', error);
  }
}

demonstrateGetFileInfo().catch(console.error);
```

___

### listDirectory

▸ **listDirectory**(`path`): `Promise`\<`DirectoryListResult`\>

Lists the contents of a directory.

#### Parameters

| Name | Type | Description |
| :------ | :------ | :------ |
| `path` | `string` | Absolute path to the directory to list. |

#### Returns

`Promise`\<`DirectoryListResult`\>

Promise resolving to DirectoryListResult containing array of entries.

**`Example`**

```typescript
import { AgentBay } from 'wuying-agentbay-sdk';

const agentBay = new AgentBay({ apiKey: 'your_api_key' });
const result = await agentBay.create();

if (result.success) {
  const session = result.session;

  // List directory contents
  const listResult = await session.fileSystem.listDirectory('/tmp');
  if (listResult.success) {
    console.log(`Found ${listResult.entries.length} entries`);
    for (const entry of listResult.entries) {
      console.log(`${entry.name} (${entry.isDirectory ? 'dir' : 'file'})`);
    }
  }

  await session.delete();
}
```

**`See`**

[readFile](filesystem.md#readfile), [writeFile](filesystem.md#writefile)

___

### moveFile

▸ **moveFile**(`source`, `destination`): `Promise`\<`BoolResult`\>

Moves a file or directory from source to destination.
Corresponds to Python's move_file() method

#### Parameters

| Name | Type | Description |
| :------ | :------ | :------ |
| `source` | `string` | Path to the source file or directory. |
| `destination` | `string` | Path to the destination file or directory. |

#### Returns

`Promise`\<`BoolResult`\>

BoolResult with move result and requestId

**`Example`**

```typescript
import { AgentBay } from 'wuying-agentbay-sdk';

const agentBay = new AgentBay({ apiKey: 'your_api_key' });

async function demonstrateMoveFile() {
  try {
    const result = await agentBay.create();
    if (result.success) {
      const session = result.session;

      // Create a test file
      await session.fileSystem.writeFile('/tmp/original.txt', 'Test content');

      // Move the file to a new location
      const moveResult = await session.fileSystem.moveFile('/tmp/original.txt', '/tmp/moved.txt');
      if (moveResult.success) {
        console.log('File moved successfully');
        // Output: File moved successfully
        console.log(`Request ID: ${moveResult.requestId}`);
        // Output: Request ID: 9E3F4A5B-2C6D-7E8F-9A0B-1C2D3E4F5A6B
      }

      // Verify the move
      const readResult = await session.fileSystem.readFile('/tmp/moved.txt');
      if (readResult.success) {
        console.log(`Content at new location: ${readResult.content}`);
        // Output: Content at new location: Test content
      }

      await session.delete();
    }
  } catch (error) {
    console.error('Error:', error);
  }
}

demonstrateMoveFile().catch(console.error);
```

___

### readFile

▸ **readFile**(`path`): `Promise`\<`FileContentResult`\>

Reads the entire content of a file.

#### Parameters

| Name | Type | Description |
| :------ | :------ | :------ |
| `path` | `string` | Absolute path to the file to read. |

#### Returns

`Promise`\<`FileContentResult`\>

Promise resolving to FileContentResult containing:
         - success: Whether the read operation succeeded
         - content: String content of the file
         - requestId: Unique identifier for this API request
         - errorMessage: Error description if read failed

**`Throws`**

Error if the API call fails.

**`Example`**

```typescript
import { AgentBay } from 'wuying-agentbay-sdk';

const agentBay = new AgentBay({ apiKey: 'your_api_key' });
const result = await agentBay.create();

if (result.success) {
  const session = result.session;

  // Read a text file
  const fileResult = await session.fileSystem.readFile('/etc/hostname');
  if (fileResult.success) {
    console.log(`Content: ${fileResult.content}`);
    // Output: Content: agentbay-session-xyz
  }

  await session.delete();
}
```

**`Remarks`**

**Behavior:**
- Automatically handles large files by reading in 60KB chunks
- Returns empty string for empty files
- Fails if path is a directory or doesn't exist
- Content is returned as UTF-8 string

**`See`**

[writeFile](filesystem.md#writefile), [listDirectory](filesystem.md#listdirectory)

___

### readMultipleFiles

▸ **readMultipleFiles**(`paths`): `Promise`\<`MultipleFileContentResult`\>

Reads the content of multiple files.
Corresponds to Python's read_multiple_files() method

#### Parameters

| Name | Type | Description |
| :------ | :------ | :------ |
| `paths` | `string`[] | Array of file paths to read. |

#### Returns

`Promise`\<`MultipleFileContentResult`\>

MultipleFileContentResult with file contents and requestId

**`Example`**

```typescript
import { AgentBay } from 'wuying-agentbay-sdk';

const agentBay = new AgentBay({ apiKey: 'your_api_key' });

async function demonstrateReadMultipleFiles() {
  try {
    const result = await agentBay.create();
    if (result.success) {
      const session = result.session;

      // Create multiple test files
      await session.fileSystem.writeFile('/tmp/file1.txt', 'Content of file 1');
      await session.fileSystem.writeFile('/tmp/file2.txt', 'Content of file 2');
      await session.fileSystem.writeFile('/tmp/file3.txt', 'Content of file 3');

      // Read multiple files at once
      const paths = ['/tmp/file1.txt', '/tmp/file2.txt', '/tmp/file3.txt'];
      const readResult = await session.fileSystem.readMultipleFiles(paths);
      if (readResult.success) {
        console.log(`Read ${Object.keys(readResult.contents).length} files`);
        // Output: Read 3 files
        for (const [path, content] of Object.entries(readResult.contents)) {
          console.log(`${path}: ${content}`);
        }
        // Output: /tmp/file1.txt: Content of file 1
        // Output: /tmp/file2.txt: Content of file 2
        // Output: /tmp/file3.txt: Content of file 3
      }

      await session.delete();
    }
  } catch (error) {
    console.error('Error:', error);
  }
}

demonstrateReadMultipleFiles().catch(console.error);
```

___

### searchFiles

▸ **searchFiles**(`path`, `pattern`, `excludePatterns?`): `Promise`\<`FileSearchResult`\>

Searches for files in a directory that match a pattern.
Corresponds to Python's search_files() method

#### Parameters

| Name | Type | Default value | Description |
| :------ | :------ | :------ | :------ |
| `path` | `string` | `undefined` | Path to the directory to search in. |
| `pattern` | `string` | `undefined` | Pattern to search for. Supports glob patterns. |
| `excludePatterns` | `string`[] | `[]` | Optional: Array of patterns to exclude. |

#### Returns

`Promise`\<`FileSearchResult`\>

FileSearchResult with search results and requestId

**`Example`**

```typescript
import { AgentBay } from 'wuying-agentbay-sdk';

const agentBay = new AgentBay({ apiKey: 'your_api_key' });

async function demonstrateSearchFiles() {
  try {
    const result = await agentBay.create();
    if (result.success) {
      const session = result.session;

      // Create test files
      await session.fileSystem.createDirectory('/tmp/test');
      await session.fileSystem.writeFile('/tmp/test/file1.py', "print('hello')");
      await session.fileSystem.writeFile('/tmp/test/file2.py', "print('world')");
      await session.fileSystem.writeFile('/tmp/test/file3.txt', 'text content');

      // Search for Python files
      const searchResult = await session.fileSystem.searchFiles('/tmp/test', '*.py');
      if (searchResult.success) {
        console.log(`Found ${searchResult.matches.length} Python files:`);
        // Output: Found 2 Python files:
        for (const match of searchResult.matches) {
          console.log(`  - ${match}`);
        }
        // Output:   - /tmp/test/file1.py
        // Output:   - /tmp/test/file2.py
      }

      // Search with exclusion pattern
      const excludeResult = await session.fileSystem.searchFiles(
        '/tmp/test',
        '*',
        ['*.txt']
      );
      if (excludeResult.success) {
        console.log(`Found ${excludeResult.matches.length} files (excluding .txt)`);
      }

      await session.delete();
    }
  } catch (error) {
    console.error('Error:', error);
  }
}

demonstrateSearchFiles().catch(console.error);
```

___

### uploadFile

▸ **uploadFile**(`localPath`, `remotePath`, `options?`): `Promise`\<`any`\>

Upload a file from local to remote path using pre-signed URLs.
This is a synchronous wrapper around the FileTransfer.upload method.

#### Parameters

| Name | Type | Description |
| :------ | :------ | :------ |
| `localPath` | `string` | Local file path to upload |
| `remotePath` | `string` | Remote file path to upload to |
| `options?` | `Object` | Optional parameters |
| `options.contentType?` | `string` | - |
| `options.pollInterval?` | `number` | - |
| `options.progressCb?` | (`bytesTransferred`: `number`) => `void` | - |
| `options.wait?` | `boolean` | - |
| `options.waitTimeout?` | `number` | - |

#### Returns

`Promise`\<`any`\>

UploadResult with upload result and requestId

**`Example`**

```typescript
import { AgentBay } from 'wuying-agentbay-sdk';
import * as fs from 'fs';

const agentBay = new AgentBay({ apiKey: 'your_api_key' });

async function demonstrateUploadFile() {
  try {
    // Create session with context sync for file transfer
    const result = await agentBay.create({
      imageId: 'code_latest'
    });

    if (result.success) {
      const session = result.session;

      // Create a local test file
      const localPath = '/tmp/local_upload_test.txt';
      fs.writeFileSync(localPath, 'Test upload content');

      // Upload the file
      const uploadResult = await session.fileSystem.uploadFile(
        localPath,
        '/workspace/uploaded_file.txt'
      );

      if (uploadResult.success) {
        console.log('File uploaded successfully');
        // Output: File uploaded successfully
        console.log(`Bytes sent: ${uploadResult.bytesSent}`);
        console.log(`Request ID (upload URL): ${uploadResult.requestIdUploadUrl}`);
        console.log(`Request ID (sync): ${uploadResult.requestIdSync}`);
      } else {
        console.error(`Upload failed: ${uploadResult.error}`);
      }

      // Verify the uploaded file exists in the session
      const readResult = await session.fileSystem.readFile('/workspace/uploaded_file.txt');
      if (readResult.success) {
        console.log(`File content in session: ${readResult.content}`);
      }

      await session.delete();
    }
  } catch (error) {
    console.error('Error:', error);
  }
}

demonstrateUploadFile().catch(console.error);
```

___

### watchDirectory

▸ **watchDirectory**(`path`, `callback`, `interval?`, `signal?`): `Promise`\<`void`\>

Watch a directory for file changes and call the callback function when changes occur

#### Parameters

| Name | Type | Default value |
| :------ | :------ | :------ |
| `path` | `string` | `undefined` |
| `callback` | (`events`: ``FileChangeEvent``[]) => `void` | `undefined` |
| `interval` | `number` | `500` |
| `signal?` | `AbortSignal` | `undefined` |

#### Returns

`Promise`\<`void`\>

___

### writeFile

▸ **writeFile**(`path`, `content`, `mode?`): `Promise`\<`BoolResult`\>

Writes content to a file.

#### Parameters

| Name | Type | Default value | Description |
| :------ | :------ | :------ | :------ |
| `path` | `string` | `undefined` | Absolute path to the file to write. |
| `content` | `string` | `undefined` | String content to write to the file. |
| `mode` | `string` | `"overwrite"` | Write mode: "overwrite" (default) or "append". |

#### Returns

`Promise`\<`BoolResult`\>

Promise resolving to BoolResult with success status.

**`Example`**

```typescript
import { AgentBay } from 'wuying-agentbay-sdk';

const agentBay = new AgentBay({ apiKey: 'your_api_key' });
const result = await agentBay.create();

if (result.success) {
  const session = result.session;

  // Write to a file (overwrite mode)
  const writeResult = await session.fileSystem.writeFile(
    '/tmp/test.txt',
    'Hello, AgentBay!'
  );
  if (writeResult.success) {
    console.log('File written successfully');
  }

  // Append to a file
  const appendResult = await session.fileSystem.writeFile(
    '/tmp/test.txt',
    '\nNew line',
    'append'
  );

  await session.delete();
}
```

**`Remarks`**

**Behavior:**
- Automatically handles large files by writing in 60KB chunks
- Creates parent directories if they don't exist
- "overwrite" mode replaces existing file content
- "append" mode adds content to the end of the file

**`See`**

[readFile](filesystem.md#readfile), [listDirectory](filesystem.md#listdirectory)

## Related Resources

- [Session API Reference](session.md)
- [Command API Reference](command.md)

