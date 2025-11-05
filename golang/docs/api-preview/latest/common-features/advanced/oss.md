# OSS API Reference

## Type DownloadResult

```go
type DownloadResult struct {
	models.ApiResponse
	LocalPath	string
}
```

DownloadResult represents the result of a file download operation

## Type EnvInitResult

```go
type EnvInitResult struct {
	models.ApiResponse
	Result	string
}
```

EnvInitResult represents the result of OSS environment initialization

## Type OSSManager

```go
type OSSManager struct {
	Session interface {
		GetAPIKey() string
		GetClient() *mcp.Client
		GetSessionId() string
		IsVpc() bool
		NetworkInterfaceIp() string
		HttpPort() string
		FindServerForTool(toolName string) string
		CallMcpTool(toolName string, args interface{}, autoGenSession ...bool) (*models.McpToolResult, error)
	}
}
```

OSSManager handles Object Storage Service operations in the AgentBay cloud environment

### Methods

#### Download

```go
func (o *OSSManager) Download(bucket, object, path string) (*DownloadResult, error)
```

Download downloads an object from the specified OSS bucket to the given local path

#### DownloadAnonymous

```go
func (o *OSSManager) DownloadAnonymous(url, path string) (*DownloadResult, error)
```

DownloadAnonymous downloads a file from the specified URL to the given local path

#### EnvInit

```go
func (o *OSSManager) EnvInit(accessKeyId, accessKeySecret, securityToken, endpoint, region string) (*EnvInitResult, error)
```

EnvInit initializes OSS environment variables with the specified endpoint, access key ID, access key
secret, security token, and region

#### Upload

```go
func (o *OSSManager) Upload(bucket, object, path string) (*UploadResult, error)
```

Upload uploads a local file or directory to the specified OSS bucket

#### UploadAnonymous

```go
func (o *OSSManager) UploadAnonymous(url, path string) (*UploadResult, error)
```

UploadAnonymous uploads a local file or directory to the specified URL using HTTP PUT

### Related Functions

#### NewOss

```go
func NewOss(session interface {
	GetAPIKey() string
	GetClient() *mcp.Client
	GetSessionId() string
	IsVpc() bool
	NetworkInterfaceIp() string
	HttpPort() string
	FindServerForTool(toolName string) string
	CallMcpTool(toolName string, args interface{}, autoGenSession ...bool) (*models.McpToolResult, error)
}) *OSSManager
```

NewOss creates a new OSS manager instance

## Type UploadResult

```go
type UploadResult struct {
	models.ApiResponse
	URL	string
}
```

UploadResult represents the result of a file upload operation

---

*Documentation generated automatically from Go source code.*
