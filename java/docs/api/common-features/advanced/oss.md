# ☁️ Oss API Reference

## Overview

The Oss module provides specialized functionality for the AgentBay cloud platform. It includes various methods and utilities to interact with cloud services and manage resources.

## 📚 Tutorial

[OSS Integration Guide](../../../../../docs/guides/common-features/advanced/oss-integration.md)

Integrate with Alibaba Cloud OSS for file storage

## OSS

Handles Object Storage Service operations in the AgentBay cloud environment.

### Constructor

```java
public OSS(Session session)
```

Initialize an OSS object.

**Parameters:**
- `session` (Session): The Session instance that this OSS belongs to

### Methods

### envInit

```java
public OSSClientResult envInit(String accessKeyId, String accessKeySecret, String securityToken, String endpoint, String region)
```

Create an OSS client with the provided STS temporary credentials.

**Parameters:**
- `accessKeyId` (String): The Access Key ID from STS temporary credentials.
- `accessKeySecret` (String): The Access Key Secret from STS temporary credentials.
- `securityToken` (String): Security token from STS temporary credentials. Required for security.
- `endpoint` (String): The OSS service endpoint. If not specified, the default is used.
- `region` (String): The OSS region. If not specified, the default is used.

**Returns:**
- `OSSClientResult`: OSSClientResult containing client configuration and error message if any.

### upload

```java
public OSSUploadResult upload(String bucket, String object, String path)
```

Upload a local file or directory to OSS.

<p>Note: Before calling this API, you must first call envInit to initialize
the OSS environment.</p>

**Parameters:**
- `bucket` (String): OSS bucket name.
- `object` (String): Object key in OSS.
- `path` (String): Local file or directory path to upload.

**Returns:**
- `OSSUploadResult`: OSSUploadResult containing upload result and error message if any.

### uploadAnonymous

```java
public OSSUploadResult uploadAnonymous(String url, String path)
```

Upload a local file or directory to a URL anonymously.

**Parameters:**
- `url` (String): The HTTP/HTTPS URL to upload the file to.
- `path` (String): Local file or directory path to upload.

**Returns:**
- `OSSUploadResult`: OSSUploadResult containing upload result and error message if any.

### download

```java
public OSSDownloadResult download(String bucket, String object, String path)
```

Download an object from OSS to a local file or directory.

<p>Note: Before calling this API, you must first call envInit to initialize
the OSS environment.</p>

**Parameters:**
- `bucket` (String): OSS bucket name.
- `object` (String): Object key in OSS.
- `path` (String): Local file or directory path to download to.

**Returns:**
- `OSSDownloadResult`: OSSDownloadResult containing download status and error message if any.

### downloadAnonymous

```java
public OSSDownloadResult downloadAnonymous(String url, String path)
```

Download a file from a URL anonymously to a local file path.

**Parameters:**
- `url` (String): The HTTP/HTTPS URL to download the file from.
- `path` (String): Local file or directory path to download to.

**Returns:**
- `OSSDownloadResult`: OSSDownloadResult containing download status and error message if any.

### uploadFile

```java
public OSSUploadResult uploadFile(String localPath, String remotePath) throws OSSException
```

### downloadFile

```java
public OSSDownloadResult downloadFile(String remotePath, String localPath) throws OSSException
```

### deleteFile

```java
public DeleteResult deleteFile(String remotePath) throws OSSException
```

### getClient

```java
public OSSClientResult getClient()
```

### uploadLegacy

```java
public OSSUploadResult uploadLegacy(String localPath, String remotePath, String bucketName) throws OSSException
```

### uploadAnonymousLegacy

```java
public OSSUploadResult uploadAnonymousLegacy(String localPath, String remotePath) throws OSSException
```

### downloadLegacy

```java
public OSSDownloadResult downloadLegacy(String remotePath, String localPath, String bucketName) throws OSSException
```

### deleteFileVoid

```java
public void deleteFileVoid(String remotePath) throws OSSException
```



## 🔗 Related Resources

- [Session API Reference](../../../api/common-features/basics/session.md)
- [FileSystem API Reference](../../../api/common-features/basics/filesystem.md)

