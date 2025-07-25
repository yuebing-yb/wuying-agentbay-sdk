# OSS API Reference

The OSS (Object Storage Service) module provides functionality for interacting with cloud storage services.

## OSS Class

The `OSS` class provides methods for OSS operations.

### env_init

Creates and initializes OSS environment variables with the specified credentials.

```python
def env_init(self, access_key_id: str, access_key_secret: str, securityToken: Optional[str] = None,
                 endpoint: Optional[str] = None, region: Optional[str] = None) -> OSSClientResult
```

**Parameters:**
- `access_key_id`: The Access Key ID for OSS authentication.
- `access_key_secret`: The Access Key Secret for OSS authentication.
- `securityToken`: The security token for OSS authentication. Optional.
- `endpoint`: The OSS service endpoint. If not specified, the default is used.
- `region`: The OSS region. If not specified, the default is used.

**Returns:**
- `OSSClientResult`: Result object containing client configuration, request ID, success status, and error message if any.

**OSSClientResult Structure:**
```python
class OSSClientResult(ApiResponse):
    def __init__(self, request_id: str = "", success: bool = False,
                 client_config: Optional[Dict[str, Any]] = None, error_message: str = "")
```

**Example:**
```python
from agentbay import AgentBay

# Initialize the SDK
agent_bay = AgentBay(api_key="your_api_key")

# Initialize OSS environment
result = agent_bay.oss.env_init(
    access_key_id="your_access_key_id",
    access_key_secret="your_access_key_secret",
    securityToken="your_security_token",
    endpoint="oss-cn-hangzhou.aliyuncs.com",
    region="cn-hangzhou"
)

if result.success:
    print(f"OSS environment initialized successfully, request ID: {result.request_id}")
else:
    print(f"Failed to initialize OSS environment: {result.error_message}")
```

### upload

**注意：在调用此API前，必须先调用`env_init`进行OSS环境初始化。**

Uploads a local file or directory to OSS.

```python
def upload(self, bucket: str, object: str, path: str) -> OSSUploadResult
```

**Parameters:**
- `bucket`: OSS bucket name.
- `object`: Object key in OSS.
- `path`: Local file or directory path to upload.

**Returns:**
- `OSSUploadResult`: Result object containing upload result, request ID, success status, and error message if any.

**OSSUploadResult Structure:**
```python
class OSSUploadResult(ApiResponse):
    def __init__(self, request_id: str = "", success: bool = False,
                 content: str = "", error_message: str = "")
```

**示例：**
```python
from wuying_agentbay_sdk import AgentBay

# 初始化SDK
agent_bay = AgentBay(api_key="your_api_key")

# 第一步：初始化OSS环境
agent_bay.oss.env_init(
    access_key_id="your_access_key_id",
    access_key_secret="your_access_key_secret",
    security_token="your_security_token",
    endpoint="oss-cn-hangzhou.aliyuncs.com",
    region="cn-hangzhou"
)

# 第二步：上传文件
result = agent_bay.oss.upload("my-bucket", "my-object", "/path/to/local/file")
print("文件上传成功：", result)
```

### upload_anonymous

**注意：在调用此API前，必须先调用`env_init`进行OSS环境初始化。**

Uploads a local file or directory to a URL anonymously.

```python
def upload_anonymous(self, url: str, path: str) -> OSSUploadResult
```

**Parameters:**
- `url`: The HTTP/HTTPS URL to upload the file to.
- `path`: Local file or directory path to upload.

**Returns:**
- `OSSUploadResult`: Result object containing upload result, request ID, success status, and error message if any.

**Example:**
```python
from agentbay import AgentBay

# Initialize the SDK
agent_bay = AgentBay(api_key="your_api_key")

# Upload file anonymously
result = agent_bay.oss.upload_anonymous("https://example.com/upload", "/path/to/local/file")

if result.success:
    print(f"File uploaded anonymously successfully, content: {result.content}")
    print(f"Request ID: {result.request_id}")
else:
    print(f"Failed to upload file anonymously: {result.error_message}")
```

**示例：**
```python
from wuying_agentbay_sdk import AgentBay

# 初始化SDK
agent_bay = AgentBay(api_key="your_api_key")

# 第一步：初始化OSS环境
agent_bay.oss.env_init(
    access_key_id="your_access_key_id",
    access_key_secret="your_access_key_secret",
    security_token="your_security_token",
    endpoint="oss-cn-hangzhou.aliyuncs.com",
    region="cn-hangzhou"
)

# 第二步：匿名上传文件
result = agent_bay.oss.upload_anonymous("https://example.com/upload", "/path/to/local/file")
print("匿名上传成功：", result)
```

### download

**注意：在调用此API前，必须先调用`env_init`进行OSS环境初始化。**

Downloads an object from OSS to a local file or directory.

```python
def download(self, bucket: str, object: str, path: str) -> OSSDownloadResult
```

**Parameters:**
- `bucket`: OSS bucket name.
- `object`: Object key in OSS.
- `path`: Local path to save the downloaded file.

**Returns:**
- `OSSDownloadResult`: Result object containing download result, request ID, success status, and error message if any.

**OSSDownloadResult Structure:**
```python
class OSSDownloadResult(ApiResponse):
    def __init__(self, request_id: str = "", success: bool = False,
                 content: str = "", error_message: str = "")
```

**示例：**
```python
from wuying_agentbay_sdk import AgentBay

# 初始化SDK
agent_bay = AgentBay(api_key="your_api_key")

# 第一步：初始化OSS环境
agent_bay.oss.env_init(
    access_key_id="your_access_key_id",
    access_key_secret="your_access_key_secret",
    security_token="your_security_token",
    endpoint="oss-cn-hangzhou.aliyuncs.com",
    region="cn-hangzhou"
)

# 第二步：下载文件
result = agent_bay.oss.download("my-bucket", "my-object", "/path/to/local/file")
print("文件下载成功：", result)
```

### download_anonymous

**注意：在调用此API前，必须先调用`env_init`进行OSS环境初始化。**

Downloads a file from a URL anonymously to a local file path.

```python
def download_anonymous(self, url: str, path: str) -> OSSDownloadResult
```

**Parameters:**
- `url`: The HTTP/HTTPS URL to download the file from.
- `path`: Local file or directory path to download to.

**Returns:**
- `OSSDownloadResult`: Result object containing download content, request ID, success status, and error message if any.

**Example:**
```python
from agentbay import AgentBay

# Initialize the SDK
agent_bay = AgentBay(api_key="your_api_key")

# Download file anonymously
result = agent_bay.oss.download_anonymous("https://example.com/file.txt", "/path/to/local/file.txt")

if result.success:
    print(f"File downloaded anonymously successfully, content: {result.content}")
    print(f"Request ID: {result.request_id}")
else:
    print(f"Failed to download file anonymously: {result.error_message}")
```

**示例：**
```python
from wuying_agentbay_sdk import AgentBay

# 初始化SDK
agent_bay = AgentBay(api_key="your_api_key")

# 第一步：初始化OSS环境
agent_bay.oss.env_init(
    access_key_id="your_access_key_id",
    access_key_secret="your_access_key_secret",
    security_token="your_security_token",
    endpoint="oss-cn-hangzhou.aliyuncs.com",
    region="cn-hangzhou"
)

# 第二步：匿名下载文件
result = agent_bay.oss.download_anonymous("https://example.com/file.txt", "/path/to/local/file.txt")
print("匿名下载成功：", result)
```

## Related Resources

- [Filesystem API Reference](filesystem.md)
- [Session API Reference](session.md)

