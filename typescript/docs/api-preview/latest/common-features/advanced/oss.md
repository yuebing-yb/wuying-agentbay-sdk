# Class: Oss

## ☁️ Related Tutorial

- [OSS Integration Guide](../../../../../../docs/guides/common-features/advanced/oss-integration.md) - Integrate with Alibaba Cloud OSS for file storage

Handles OSS operations in the AgentBay cloud environment.

## Table of contents

### Constructors

- [constructor](oss.md#constructor)

### Methods

- [download](oss.md#download)
- [downloadAnonymous](oss.md#downloadanonymous)
- [envInit](oss.md#envinit)
- [upload](oss.md#upload)
- [uploadAnonymous](oss.md#uploadanonymous)

## Constructors

### constructor

• **new Oss**(`session`): [`Oss`](oss.md)

Initialize an Oss object.

#### Parameters

| Name | Type | Description |
| :------ | :------ | :------ |
| `session` | [`Session`](../basics/session.md) | The Session instance that this Oss belongs to. |

#### Returns

[`Oss`](oss.md)

## Methods

### download

▸ **download**(`bucket`, `object`, `path`): `Promise`\<`OSSDownloadResult`\>

Download a file from OSS.
Corresponds to Python's download() method

#### Parameters

| Name | Type | Description |
| :------ | :------ | :------ |
| `bucket` | `string` | The OSS bucket name |
| `object` | `string` | The OSS object key |
| `path` | `string` | The local file path to save the downloaded file |

#### Returns

`Promise`\<`OSSDownloadResult`\>

OSSDownloadResult with download result and requestId

**`Throws`**

APIError if the operation fails.

**`Example`**

```typescript
import { AgentBay } from 'wuying-agentbay-sdk';

const agentBay = new AgentBay({ apiKey: 'your_api_key' });

async function downloadFileFromOss() {
  try {
    const createResult = await agentBay.create();
    if (createResult.success) {
      const session = createResult.session;

      // First, initialize OSS environment
      await session.oss.envInit(
        'your_access_key_id',
        'your_access_key_secret',
        'your_security_token',
        'oss-cn-hangzhou.aliyuncs.com',
        'cn-hangzhou'
      );

      // Download a file from OSS
      const result = await session.oss.download(
        'my-bucket',
        'my-folder/file.txt',
        '/path/to/save/file.txt'
      );

      if (result.success) {
        console.log('File downloaded successfully');
        // Output: File downloaded successfully
        console.log(`Request ID: ${result.requestId}`);
      } else {
        console.error(`Download failed: ${result.errorMessage}`);
      }

      await session.delete();
    }
  } catch (error) {
    console.error('Error:', error);
  }
}

downloadFileFromOss().catch(console.error);
```

___

### downloadAnonymous

▸ **downloadAnonymous**(`url`, `path`): `Promise`\<`OSSDownloadResult`\>

Download a file from OSS using an anonymous URL.
Corresponds to Python's download_anonymous() method

#### Parameters

| Name | Type | Description |
| :------ | :------ | :------ |
| `url` | `string` | The anonymous download URL |
| `path` | `string` | The local file path to save the downloaded file |

#### Returns

`Promise`\<`OSSDownloadResult`\>

OSSDownloadResult with download result and requestId

**`Throws`**

APIError if the operation fails.

**`Example`**

```typescript
import { AgentBay } from 'wuying-agentbay-sdk';

const agentBay = new AgentBay({ apiKey: 'your_api_key' });

async function downloadFileAnonymously() {
  try {
    const createResult = await agentBay.create();
    if (createResult.success) {
      const session = createResult.session;

      // Download file using an anonymous URL
      const result = await session.oss.downloadAnonymous(
        'https://example.com/file.txt',
        '/path/to/save/file.txt'
      );

      if (result.success) {
        console.log('File downloaded anonymously');
        // Output: File downloaded anonymously
        console.log(`Request ID: ${result.requestId}`);
      } else {
        console.error(`Download failed: ${result.errorMessage}`);
      }

      await session.delete();
    }
  } catch (error) {
    console.error('Error:', error);
  }
}

downloadFileAnonymously().catch(console.error);
```

___

### envInit

▸ **envInit**(`accessKeyId`, `accessKeySecret`, `securityToken?`, `endpoint?`, `region?`): `Promise`\<`OSSClientResult`\>

Initialize OSS environment variables with the specified credentials.
Corresponds to Python's env_init() method

#### Parameters

| Name | Type | Description |
| :------ | :------ | :------ |
| `accessKeyId` | `string` | The access key ID |
| `accessKeySecret` | `string` | The access key secret |
| `securityToken?` | `string` | The security token (optional) |
| `endpoint?` | `string` | The OSS endpoint (optional) |
| `region?` | `string` | The OSS region (optional) |

#### Returns

`Promise`\<`OSSClientResult`\>

OSSClientResult with client configuration and requestId

**`Throws`**

APIError if the operation fails.

**`Example`**

```typescript
import { AgentBay } from 'wuying-agentbay-sdk';

const agentBay = new AgentBay({ apiKey: 'your_api_key' });

async function initializeOssEnvironment() {
  try {
    const createResult = await agentBay.create();
    if (createResult.success) {
      const session = createResult.session;

      const result = await session.oss.envInit(
        'your_access_key_id',
        'your_access_key_secret',
        'your_security_token',
        'oss-cn-hangzhou.aliyuncs.com',
        'cn-hangzhou'
      );

      if (result.success) {
        console.log('OSS environment initialized successfully');
        // Output: OSS environment initialized successfully
        console.log(`Request ID: ${result.requestId}`);
      } else {
        console.error(`Failed to initialize OSS: ${result.errorMessage}`);
      }

      await session.delete();
    }
  } catch (error) {
    console.error('Error:', error);
  }
}

initializeOssEnvironment().catch(console.error);
```

___

### upload

▸ **upload**(`bucket`, `object`, `path`): `Promise`\<`OSSUploadResult`\>

Upload a file to OSS.
Corresponds to Python's upload() method

#### Parameters

| Name | Type | Description |
| :------ | :------ | :------ |
| `bucket` | `string` | The OSS bucket name |
| `object` | `string` | The OSS object key |
| `path` | `string` | The local file path to upload |

#### Returns

`Promise`\<`OSSUploadResult`\>

OSSUploadResult with upload result and requestId

**`Throws`**

APIError if the operation fails.

**`Example`**

```typescript
import { AgentBay } from 'wuying-agentbay-sdk';

const agentBay = new AgentBay({ apiKey: 'your_api_key' });

async function uploadFileToOss() {
  try {
    const createResult = await agentBay.create();
    if (createResult.success) {
      const session = createResult.session;

      // First, initialize OSS environment
      await session.oss.envInit(
        'your_access_key_id',
        'your_access_key_secret',
        'your_security_token',
        'oss-cn-hangzhou.aliyuncs.com',
        'cn-hangzhou'
      );

      // Upload a file to OSS
      const result = await session.oss.upload(
        'my-bucket',
        'my-folder/file.txt',
        '/path/to/local/file.txt'
      );

      if (result.success) {
        console.log('File uploaded successfully');
        // Output: File uploaded successfully
        console.log(`Request ID: ${result.requestId}`);
      } else {
        console.error(`Upload failed: ${result.errorMessage}`);
      }

      await session.delete();
    }
  } catch (error) {
    console.error('Error:', error);
  }
}

uploadFileToOss().catch(console.error);
```

___

### uploadAnonymous

▸ **uploadAnonymous**(`url`, `path`): `Promise`\<`OSSUploadResult`\>

Upload a file to OSS using an anonymous URL.
Corresponds to Python's upload_anonymous() method

#### Parameters

| Name | Type | Description |
| :------ | :------ | :------ |
| `url` | `string` | The anonymous upload URL |
| `path` | `string` | The local file path to upload |

#### Returns

`Promise`\<`OSSUploadResult`\>

OSSUploadResult with upload result and requestId

**`Throws`**

APIError if the operation fails.

**`Example`**

```typescript
import { AgentBay } from 'wuying-agentbay-sdk';

const agentBay = new AgentBay({ apiKey: 'your_api_key' });

async function uploadFileAnonymously() {
  try {
    const createResult = await agentBay.create();
    if (createResult.success) {
      const session = createResult.session;

      // Upload file using an anonymous URL
      const result = await session.oss.uploadAnonymous(
        'https://example.com/upload',
        '/path/to/local/file.txt'
      );

      if (result.success) {
        console.log('File uploaded anonymously');
        // Output: File uploaded anonymously
        console.log(`Request ID: ${result.requestId}`);
      } else {
        console.error(`Upload failed: ${result.errorMessage}`);
      }

      await session.delete();
    }
  } catch (error) {
    console.error('Error:', error);
  }
}

uploadFileAnonymously().catch(console.error);
```

## Related Resources

- [Session API Reference](../../common-features/basics/session.md)
- [FileSystem API Reference](../../common-features/basics/filesystem.md)

