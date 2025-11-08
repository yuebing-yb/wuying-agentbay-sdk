# OSS API Reference

## ☁️ Related Tutorial

- [OSS Integration Guide](../../../../../../docs/guides/common-features/advanced/oss-integration.md) - Integrate with Alibaba Cloud OSS for file storage



```python
logger = get_logger("oss")
```

## OSSClientResult Objects

```python
class OSSClientResult(ApiResponse)
```

Result of OSS client creation operations.

## OSSUploadResult Objects

```python
class OSSUploadResult(ApiResponse)
```

Result of OSS upload operations.

## OSSDownloadResult Objects

```python
class OSSDownloadResult(ApiResponse)
```

Result of OSS download operations.

## Oss Objects

```python
class Oss(BaseService)
```

Handles Object Storage Service operations in the AgentBay cloud environment.

#### env\_init

```python
def env_init(access_key_id: str,
             access_key_secret: str,
             securityToken: Optional[str] = None,
             endpoint: Optional[str] = None,
             region: Optional[str] = None) -> OSSClientResult
```

Create an OSS client with the provided credentials.

**Arguments**:

- `access_key_id` - The Access Key ID for OSS authentication.
- `access_key_secret` - The Access Key Secret for OSS authentication.
- `securityToken` - Optional security token for temporary credentials.
- `endpoint` - The OSS service endpoint. If not specified, the default is used.
- `region` - The OSS region. If not specified, the default is used.
  

**Returns**:

- `OSSClientResult` - Result object containing client configuration and error
  message if any.
  

**Example**:

```python
from agentbay import AgentBay

agent_bay = AgentBay(api_key="your_api_key")

def initialize_oss_environment():
    try:
        result = agent_bay.create()
        if result.success:
            session = result.session

            # Initialize OSS environment
            oss_result = session.oss.env_init(
                access_key_id="your_access_key_id",
                access_key_secret="your_access_key_secret",
                securityToken="your_security_token",
                endpoint="oss-cn-hangzhou.aliyuncs.com",
                region="cn-hangzhou"
            )

            if oss_result.success:
                print(f"OSS environment initialized successfully")
                print(f"Request ID: {oss_result.request_id}")
            else:
                print(f"Failed to initialize OSS: {oss_result.error_message}")

            session.delete()
    except Exception as e:
        print(f"Error: {e}")

initialize_oss_environment()
```

#### upload

```python
def upload(bucket: str, object: str, path: str) -> OSSUploadResult
```

Upload a local file or directory to OSS.

Note: Before calling this API, you must first call env_init to initialize
the OSS environment.

**Arguments**:

- `bucket` - OSS bucket name.
- `object` - Object key in OSS.
- `path` - Local file or directory path to upload.
  

**Returns**:

- `OSSUploadResult` - Result object containing upload result and error message
  if any.
  

**Example**:

```python
from agentbay import AgentBay

agent_bay = AgentBay(api_key="your_api_key")

def upload_file_to_oss():
    try:
        result = agent_bay.create()
        if result.success:
            session = result.session

            # Step 1: Initialize OSS environment
            session.oss.env_init(
                access_key_id="your_access_key_id",
                access_key_secret="your_access_key_secret",
                endpoint="oss-cn-hangzhou.aliyuncs.com",
                region="cn-hangzhou"
            )

            # Step 2: Upload file
            upload_result = session.oss.upload(
                bucket="my-bucket",
                object="my-object",
                path="/path/to/local/file"
            )

            if upload_result.success:
                print(f"File uploaded successfully")
                print(f"Content: {upload_result.content}")
            else:
                print(f"Upload failed: {upload_result.error_message}")

            session.delete()
    except Exception as e:
        print(f"Error: {e}")

upload_file_to_oss()
```

#### upload\_anonymous

```python
def upload_anonymous(url: str, path: str) -> OSSUploadResult
```

Upload a local file or directory to a URL anonymously.

**Arguments**:

- `url` - The HTTP/HTTPS URL to upload the file to.
- `path` - Local file or directory path to upload.
  

**Returns**:

- `OSSUploadResult` - Result object containing upload result and error message
  if any.
  

**Example**:

```python
from agentbay import AgentBay

agent_bay = AgentBay(api_key="your_api_key")

def upload_file_anonymously():
    try:
        result = agent_bay.create()
        if result.success:
            session = result.session

            # Upload file anonymously to a URL
            upload_result = session.oss.upload_anonymous(
                url="https://example.com/upload",
                path="/path/to/local/file"
            )

            if upload_result.success:
                print(f"File uploaded anonymously successfully")
                print(f"Content: {upload_result.content}")
            else:
                print(f"Upload failed: {upload_result.error_message}")

            session.delete()
    except Exception as e:
        print(f"Error: {e}")

upload_file_anonymously()
```

#### download

```python
def download(bucket: str, object: str, path: str) -> OSSDownloadResult
```

Download an object from OSS to a local file or directory.

Note: Before calling this API, you must first call env_init to initialize
the OSS environment.

**Arguments**:

- `bucket` - OSS bucket name.
- `object` - Object key in OSS.
- `path` - Local file or directory path to download to.
  

**Returns**:

- `OSSDownloadResult` - Result object containing download status and error
  message if any.
  

**Example**:

```python
from agentbay import AgentBay

agent_bay = AgentBay(api_key="your_api_key")

def download_file_from_oss():
    try:
        result = agent_bay.create()
        if result.success:
            session = result.session

            # Step 1: Initialize OSS environment
            session.oss.env_init(
                access_key_id="your_access_key_id",
                access_key_secret="your_access_key_secret",
                endpoint="oss-cn-hangzhou.aliyuncs.com",
                region="cn-hangzhou"
            )

            # Step 2: Download file
            download_result = session.oss.download(
                bucket="my-bucket",
                object="my-object",
                path="/path/to/local/file"
            )

            if download_result.success:
                print(f"File downloaded successfully")
                print(f"Content: {download_result.content}")
            else:
                print(f"Download failed: {download_result.error_message}")

            session.delete()
    except Exception as e:
        print(f"Error: {e}")

download_file_from_oss()
```

#### download\_anonymous

```python
def download_anonymous(url: str, path: str) -> OSSDownloadResult
```

Download a file from a URL anonymously to a local file path.

**Arguments**:

- `url` - The HTTP/HTTPS URL to download the file from.
- `path` - Local file or directory path to download to.
  

**Returns**:

- `OSSDownloadResult` - Result object containing download status and error
  message if any.
  

**Example**:

```python
from agentbay import AgentBay

agent_bay = AgentBay(api_key="your_api_key")

def download_file_anonymously():
    try:
        result = agent_bay.create()
        if result.success:
            session = result.session

            # Download file anonymously from a URL
            download_result = session.oss.download_anonymous(
                url="https://example.com/file.txt",
                path="/path/to/local/file.txt"
            )

            if download_result.success:
                print(f"File downloaded anonymously successfully")
                print(f"Content: {download_result.content}")
            else:
                print(f"Download failed: {download_result.error_message}")

            session.delete()
    except Exception as e:
        print(f"Error: {e}")

download_file_anonymously()
```

## Related Resources

- [Session API Reference](../../common-features/basics/session.md)
- [FileSystem API Reference](../../common-features/basics/filesystem.md)

---

*Documentation generated automatically from source code using pydoc-markdown.*
