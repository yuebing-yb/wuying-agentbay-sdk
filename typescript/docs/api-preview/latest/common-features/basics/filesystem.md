# Class: FileSystem

## 📁 Related Tutorial

- [File Operations Guide](../../../../../docs/guides/common-features/basics/file-operations.md) - Complete guide to file system operations

## 📁 Related Tutorial

- [File Operations Guide](../../../../../docs/guides/common-features/basics/file-operations.md) - Complete guide to file system operations

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

___

### listDirectory

▸ **listDirectory**(`path`): `Promise`\<`DirectoryListResult`\>

Lists the contents of a directory.
Corresponds to Python's list_directory() method

#### Parameters

| Name | Type | Description |
| :------ | :------ | :------ |
| `path` | `string` | Path to the directory to list. |

#### Returns

`Promise`\<`DirectoryListResult`\>

DirectoryListResult with directory entries and requestId

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

___

### readFile

▸ **readFile**(`path`): `Promise`\<`FileContentResult`\>

Reads the contents of a file. Automatically handles large files by chunking.

#### Parameters

| Name | Type | Description |
| :------ | :------ | :------ |
| `path` | `string` | Path to the file to read. |

#### Returns

`Promise`\<`FileContentResult`\>

FileContentResult with complete file content and requestId

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

Writes content to a file. Automatically handles large files by chunking.

#### Parameters

| Name | Type | Default value | Description |
| :------ | :------ | :------ | :---## Related Resources

- [Session API Reference](session.md)
- [Command API Reference](command.md)


## Related Resources

- [Session API Reference](session.md)
- [Command API Reference](command.md)


--- |
| `path` | `string` | `undefined` | Path to the file to write. |
| `content` | `string` | `undefined` | Content to write to the file. |
| `mode` | `string` | `"overwrite"` | Optional: Write mode. One of "overwrite", "append", or "create_new". Default is "overwrite". |

#### Returns

`Promise`\<`BoolResult`\>

BoolResult indicating success or failure with requestId
