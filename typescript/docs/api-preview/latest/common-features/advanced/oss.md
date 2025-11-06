# Class: Oss

## ☁️ Related Tutorial

- [OSS Integration Guide](../../../../../docs/guides/common-features/advanced/oss-integration.md) - Integrate with Alibaba Cloud OSS for file storage

## ☁️ Related Tutorial

- [OSS Integration Guide](../../../../../docs/guides/common-features/advanced/oss-integration.md) - Integrate with Alibaba Cloud OSS for file storage

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

___

### uploadAnonymous

▸ **uploadAnonymous**(`url`, `path`): `Promise`\<`OSSUploadResult`\>

Upload a file to OSS using an anonymous URL.
Corresponds to Python's upload_anonymous() method

#### Parameters

| Name | Type | Description |
| :------ | :------ | :---## Related Resources

- [Session API Reference](../advanced/session.md)
- [FileSystem API Reference](../advanced/filesystem.md)


## Related Resources

- [Session API Reference](../advanced/session.md)
- [FileSystem API Reference](../advanced/filesystem.md)


--- |
| `url` | `string` | The anonymous upload URL |
| `path` | `string` | The local file path to upload |

#### Returns

`Promise`\<`OSSUploadResult`\>

OSSUploadResult with upload result and requestId

**`Throws`**

APIError if the operation fails.
