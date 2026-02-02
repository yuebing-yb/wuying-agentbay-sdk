# ☁️ Oss API Reference

## Overview

The Oss module provides specialized functionality for the AgentBay cloud platform. It includes various methods and utilities to interact with cloud services and manage resources.

## 📚 Tutorial

[OSS Integration Guide](../../../../../docs/guides/common-features/advanced/oss-integration.md)

Integrate with Alibaba Cloud OSS for file storage

## OSS

Handles Object Storage Service operations in the AgentBay cloud environment.
Similar to Python's Oss class.

### Constructor

```java
public OSS(Session session)
```

### Methods

### envInit

```java
public OSSClientResult envInit(String accessKeyId, String accessKeySecret, String securityToken, String endpoint, String region)
```

Create an OSS client with the provided credentials.
Similar to Python's env_init method.

**Parameters:**
- `accessKeyId` (String): The Access Key ID for OSS authentication
- `accessKeySecret` (String): The Access Key Secret for OSS authentication
- `securityToken` (String): Optional security token for temporary credentials
- `endpoint` (String): The OSS service endpoint
- `region` (String): The OSS region

**Returns:**
- `OSSClientResult`: OSSClientResult containing client configuration and error message if any

### upload

```java
public OSSUploadResult upload(String bucket, String object, String path)
```

Upload a local file or directory to OSS.
Similar to Python's upload method.

**Parameters:**
- `bucket` (String): OSS bucket name
- `object` (String): Object key in OSS
- `path` (String): Local file or directory path to upload

**Returns:**
- `OSSUploadResult`: OSSUploadResult containing upload result and error message if any

### uploadAnonymous

```java
public OSSUploadResult uploadAnonymous(String url, String path)
```

Upload a local file or directory to a URL anonymously.
Similar to Python's upload_anonymous method.

**Parameters:**
- `url` (String): The HTTP/HTTPS URL to upload the file to
- `path` (String): Local file or directory path to upload

**Returns:**
- `OSSUploadResult`: OSSUploadResult containing upload result and error message if any

### download

```java
public OSSDownloadResult download(String bucket, String object, String path)
```

Download an object from OSS to a local file or directory.
Similar to Python's download method.

**Parameters:**
- `bucket` (String): OSS bucket name
- `object` (String): Object key in OSS
- `path` (String): Local file or directory path to download to

**Returns:**
- `OSSDownloadResult`: OSSDownloadResult containing download status and error message if any

### downloadAnonymous

```java
public OSSDownloadResult downloadAnonymous(String url, String path)
```

Download a file from a URL anonymously to a local file path.
Similar to Python's download_anonymous method.

**Parameters:**
- `url` (String): The HTTP/HTTPS URL to download the file from
- `path` (String): Local file or directory path to download to

**Returns:**
- `OSSDownloadResult`: OSSDownloadResult containing download status and error message if any

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

