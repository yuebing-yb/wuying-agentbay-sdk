# Session API Reference

## Type SessionResult

```go
type SessionResult struct {
	models.ApiResponse
	Session		*Session
	Success		bool
	ErrorMessage	string
}
```

SessionResult wraps Session object and RequestID

## Type SessionListResult

```go
type SessionListResult struct {
	models.ApiResponse
	SessionIds	[]string	// Session IDs
	NextToken	string		// Token for the next page
	MaxResults	int32		// Number of results per page
	TotalCount	int32		// Total number of results
}
```

SessionListResult wraps Session list and RequestID

## Type InfoResult

```go
type InfoResult struct {
	models.ApiResponse
	Info	*SessionInfo
}
```

InfoResult wraps SessionInfo and RequestID

## Type LabelResult

```go
type LabelResult struct {
	models.ApiResponse
	Labels	string
}
```

LabelResult wraps label operation result and RequestID

## Type LinkResult

```go
type LinkResult struct {
	models.ApiResponse
	Link	string
}
```

LinkResult wraps link result and RequestID

## Type DeleteResult

```go
type DeleteResult struct {
	models.ApiResponse
	Success		bool
	ErrorMessage	string
}
```

DeleteResult wraps deletion operation result and RequestID

## Type McpTool

```go
type McpTool struct {
	Name		string			`json:"name"`		// Tool name
	Description	string			`json:"description"`	// Tool description
	InputSchema	map[string]interface{}	`json:"inputSchema"`	// Input parameter schema
	Server		string			`json:"server"`		// Server name that provides this tool
	Tool		string			`json:"tool"`		// Tool identifier
}
```

McpTool represents an MCP tool with complete information

### Methods

#### GetName

```go
func (m *McpTool) GetName() string
```

GetName returns the tool name

#### GetServer

```go
func (m *McpTool) GetServer() string
```

GetServer returns the server name that provides this tool

## Type McpToolsResult

```go
type McpToolsResult struct {
	models.ApiResponse
	Tools	[]McpTool
}
```

McpToolsResult wraps MCP tools list and RequestID

## Type SessionInfo

```go
type SessionInfo struct {
	SessionId		string
	ResourceUrl		string
	AppId			string
	AuthCode		string
	ConnectionProperties	string
	ResourceId		string
	ResourceType		string
	Ticket			string
}
```

SessionInfo contains information about a session.

## Type Session

```go
type Session struct {
	AgentBay	*AgentBay
	SessionID	string
	ImageId		string	// ImageId used when creating this session

	// VPC-related information
	IsVpcEnabled		bool	// Whether this session uses VPC resources
	NetworkInterfaceIP	string	// Network interface IP for VPC sessions
	HttpPortNumber		string	// HTTP port for VPC sessions
	Token			string	// Token for VPC sessions

	// Resource URL for accessing the session
	ResourceUrl	string

	// File transfer context ID for file operations
	FileTransferContextID	string

	// File, command and code handlers
	FileSystem	*filesystem.FileSystem
	Command		*command.Command
	Code		*code.Code
	Oss		*oss.OSSManager

	// UI, application and window management
	UI		*ui.UIManager
	Application	*application.ApplicationManager
	Window		*window.WindowManager

	// Platform-specific automation modules
	Computer	*computer.Computer
	Mobile		*mobile.Mobile

	// Browser for web automation
	Browser	*browser.Browser

	// Agent for task execution
	Agent	*agent.Agent

	// Context management
	Context	*ContextManager

	// MCP tools available for this session
	McpTools	[]McpTool
}
```

Session represents a session in the AgentBay cloud environment.

### Methods

#### CallMcpTool

```go
func (s *Session) CallMcpTool(toolName string, args interface{}, autoGenSession ...bool) (*models.McpToolResult, error)
```

CallMcpTool calls the MCP tool and handles both VPC and non-VPC scenarios

#### CallMcpToolForBrowser

```go
func (s *Session) CallMcpToolForBrowser(toolName string, args interface{}) (*browser.McpToolResult, error)
```

CallMcpTool is a wrapper that converts the result to browser.McpToolResult

#### Delete

```go
func (s *Session) Delete(syncContext ...bool) (*DeleteResult, error)
```

Delete deletes this session.

#### FindServerForTool

```go
func (s *Session) FindServerForTool(toolName string) string
```

FindServerForTool searches for the server that provides the given tool

#### GetAPIKey

```go
func (s *Session) GetAPIKey() string
```

GetAPIKey returns the API key for this session.

#### GetClient

```go
func (s *Session) GetClient() *mcp.Client
```

GetClient returns the HTTP client for this session.

#### GetCommand

```go
func (s *Session) GetCommand() *command.Command
```

GetCommand returns the command handler for this session.

#### GetHttpPortNumber

```go
func (s *Session) GetHttpPortNumber() string
```

GetHttpPortNumber returns the HTTP port for VPC sessions.

#### GetImageID

```go
func (s *Session) GetImageID() string
```

GetImageID returns the image ID for this session.

#### GetLabels

```go
func (s *Session) GetLabels() (*LabelResult, error)
```

GetLabels gets the labels for this session.

#### GetLink

```go
func (s *Session) GetLink(protocolType *string, port *int32, options *string) (*LinkResult, error)
```

GetLink gets the link for this session.

#### GetLinkForBrowser

```go
func (s *Session) GetLinkForBrowser(protocolType *string, port *int32, options *string) (*browser.LinkResult, error)
```

GetLinkForBrowser is a wrapper that converts the result to browser.LinkResult

#### GetMcpTools

```go
func (s *Session) GetMcpTools() []interface{}
```

GetMcpTools returns the MCP tools available for this session

#### GetNetworkInterfaceIP

```go
func (s *Session) GetNetworkInterfaceIP() string
```

GetNetworkInterfaceIP returns the network interface IP for VPC sessions.

#### GetSessionID

```go
func (s *Session) GetSessionID() string
```

GetSessionID returns the session ID for this session (browser interface method).

#### GetSessionId

```go
func (s *Session) GetSessionId() string
```

GetSessionId returns the session ID for this session.

#### GetToken

```go
func (s *Session) GetToken() string
```

GetToken returns the token for VPC sessions

#### HttpPort

```go
func (s *Session) HttpPort() string
```

HttpPort returns the HTTP port for VPC sessions

#### Info

```go
func (s *Session) Info() (*InfoResult, error)
```

Info gets information about this session.

#### IsVPCEnabled

```go
func (s *Session) IsVPCEnabled() bool
```

IsVPCEnabled returns whether this session uses VPC resources.

#### IsVpc

```go
func (s *Session) IsVpc() bool
```

IsVpc returns whether this session uses VPC resources

#### ListMcpTools

```go
func (s *Session) ListMcpTools() (*McpToolsResult, error)
```

ListMcpTools lists MCP tools available for this session. It uses the ImageId from the session
creation, or "linux_latest" as default.

#### NetworkInterfaceIp

```go
func (s *Session) NetworkInterfaceIp() string
```

NetworkInterfaceIp returns the network interface IP for VPC sessions

#### SetLabels

```go
func (s *Session) SetLabels(labels map[string]string) (*LabelResult, error)
```

SetLabels sets the labels for this session.

#### ValidateLabels

```go
func (s *Session) ValidateLabels(labels map[string]string) string
```

ValidateLabels validates labels parameter for label operations. Returns error message if validation
fails, empty string if validation passes

#### callMcpToolAPI

```go
func (s *Session) callMcpToolAPI(toolName, argsJSON string, autoGenSession bool) (*models.McpToolResult, error)
```

callMcpToolAPI handles traditional API-based MCP tool calls

#### callMcpToolVPC

```go
func (s *Session) callMcpToolVPC(toolName, argsJSON string) (*models.McpToolResult, error)
```

callMcpToolVPC handles VPC-based MCP tool calls

#### extractTextContentFromResponse

```go
func (s *Session) extractTextContentFromResponse(data interface{}) string
```

extractTextContentFromResponse extracts text content from various response formats

### Related Functions

#### NewSession

```go
func NewSession(agentBay *AgentBay, sessionID string) *Session
```

NewSession creates a new Session object.

## Type CreateSessionParams

```go
type CreateSessionParams struct {
	// Labels are custom labels for the Session. These can be used for organizing and filtering sessions.
	Labels	map[string]string

	// ImageId specifies the image ID to use for the session.
	ImageId	string

	// ContextSync is a list of context synchronization configurations.
	// These configurations define how contexts should be synchronized and mounted.
	ContextSync	[]*ContextSync

	// IsVpc specifies whether to create a VPC-based session. Defaults to false.
	IsVpc	bool

	// PolicyId specifies the policy ID to apply when creating the session.
	PolicyId	string

	// ExtraConfigs contains extra configuration settings for different session types
	ExtraConfigs	*models.ExtraConfigs

	// Framework specifies the framework name for tracking (e.g., "langchain"). Empty string means direct call.
	Framework	string
}
```

CreateSessionParams provides a way to configure the parameters for creating a new session in the
AgentBay cloud environment.

### Methods

#### AddContextSync

```go
func (p *CreateSessionParams) AddContextSync(contextID, path string, policy *SyncPolicy) *CreateSessionParams
```

AddContextSync adds a context sync configuration to the session parameters.

#### AddContextSyncConfig

```go
func (p *CreateSessionParams) AddContextSyncConfig(contextSync *ContextSync) *CreateSessionParams
```

AddContextSyncConfig adds a pre-configured context sync to the session parameters.

#### GetExtraConfigsJSON

```go
func (p *CreateSessionParams) GetExtraConfigsJSON() (string, error)
```

GetExtraConfigsJSON returns the extra configs as a JSON string.

#### GetLabelsJSON

```go
func (p *CreateSessionParams) GetLabelsJSON() (string, error)
```

GetLabelsJSON returns the labels as a JSON string.

#### WithContextSync

```go
func (p *CreateSessionParams) WithContextSync(contextSyncs []*ContextSync) *CreateSessionParams
```

WithContextSync sets the context sync configurations for the session parameters.

#### WithExtraConfigs

```go
func (p *CreateSessionParams) WithExtraConfigs(extraConfigs *models.ExtraConfigs) *CreateSessionParams
```

WithExtraConfigs sets the extra configurations for the session parameters and returns the updated
parameters.

#### WithImageId

```go
func (p *CreateSessionParams) WithImageId(imageId string) *CreateSessionParams
```

WithImageId sets the image ID for the session parameters and returns the updated parameters.

#### WithIsVpc

```go
func (p *CreateSessionParams) WithIsVpc(isVpc bool) *CreateSessionParams
```

WithIsVpc sets the VPC flag for the session parameters and returns the updated parameters.

#### WithLabels

```go
func (p *CreateSessionParams) WithLabels(labels map[string]string) *CreateSessionParams
```

WithLabels sets the labels for the session parameters and returns the updated parameters.

#### WithPolicyId

```go
func (p *CreateSessionParams) WithPolicyId(policyId string) *CreateSessionParams
```

WithPolicyId sets the policy ID for the session parameters and returns the updated parameters.

### Related Functions

#### NewCreateSessionParams

```go
func NewCreateSessionParams() *CreateSessionParams
```

NewCreateSessionParams creates a new CreateSessionParams with default values.

## Type ContextSync

```go
type ContextSync struct {
	// ContextID is the ID of the context to synchronize
	ContextID	string	`json:"contextId"`
	// Path is the path where the context should be mounted
	Path	string	`json:"path"`
	// Policy defines the synchronization policy
	Policy	*SyncPolicy	`json:"policy,omitempty"`
}
```

ContextSync defines the context synchronization configuration

### Methods

#### WithPolicy

```go
func (cs *ContextSync) WithPolicy(policy *SyncPolicy) (*ContextSync, error)
```

WithPolicy sets the policy and returns the context sync for chaining

### Related Functions

#### NewContextSync

```go
func NewContextSync(contextID, path string, policy *SyncPolicy) (*ContextSync, error)
```

NewContextSync creates a new context sync configuration

## Type SyncPolicy

```go
type SyncPolicy struct {
	// UploadPolicy defines the upload policy
	UploadPolicy	*UploadPolicy	`json:"uploadPolicy,omitempty"`
	// DownloadPolicy defines the download policy
	DownloadPolicy	*DownloadPolicy	`json:"downloadPolicy,omitempty"`
	// DeletePolicy defines the delete policy
	DeletePolicy	*DeletePolicy	`json:"deletePolicy,omitempty"`
	// ExtractPolicy defines the extract policy
	ExtractPolicy	*ExtractPolicy	`json:"extractPolicy,omitempty"`
	// RecyclePolicy defines the recycle policy
	RecyclePolicy	*RecyclePolicy	`json:"recyclePolicy,omitempty"`
	// BWList defines the black and white list
	BWList	*BWList	`json:"bwList,omitempty"`
}
```

SyncPolicy defines the synchronization policy

### Methods

#### MarshalJSON

```go
func (sp *SyncPolicy) MarshalJSON() ([]byte, error)
```

MarshalJSON ensures all fields have default values before marshaling

#### ensureDefaults

```go
func (sp *SyncPolicy) ensureDefaults()
```

ensureDefaults ensures all policy fields have default values if not provided

### Related Functions

#### NewSyncPolicy

```go
func NewSyncPolicy() *SyncPolicy
```

NewSyncPolicy creates a new sync policy with default values

## Type UploadPolicy

```go
type UploadPolicy struct {
	// AutoUpload enables automatic upload
	AutoUpload	bool	`json:"autoUpload"`
	// UploadStrategy defines the upload strategy
	UploadStrategy	UploadStrategy	`json:"uploadStrategy"`
	// UploadMode defines the upload mode
	UploadMode	UploadMode	`json:"uploadMode"`
}
```

UploadPolicy defines the upload policy for context synchronization

### Related Functions

#### NewUploadPolicy

```go
func NewUploadPolicy() *UploadPolicy
```

NewUploadPolicy creates a new upload policy with default values

## Type DownloadPolicy

```go
type DownloadPolicy struct {
	// AutoDownload enables automatic download
	AutoDownload	bool	`json:"autoDownload"`
	// DownloadStrategy defines the download strategy
	DownloadStrategy	DownloadStrategy	`json:"downloadStrategy"`
}
```

DownloadPolicy defines the download policy for context synchronization

### Related Functions

#### NewDownloadPolicy

```go
func NewDownloadPolicy() *DownloadPolicy
```

NewDownloadPolicy creates a new download policy with default values

## Type DeletePolicy

```go
type DeletePolicy struct {
	// SyncLocalFile enables synchronization of local file deletions
	SyncLocalFile bool `json:"syncLocalFile"`
}
```

DeletePolicy defines the delete policy for context synchronization

### Related Functions

#### NewDeletePolicy

```go
func NewDeletePolicy() *DeletePolicy
```

NewDeletePolicy creates a new delete policy with default values

## Type ExtractPolicy

```go
type ExtractPolicy struct {
	// Extract enables file extraction
	Extract	bool	`json:"extract"`
	// DeleteSrcFile enables deletion of source file after extraction
	DeleteSrcFile	bool	`json:"deleteSrcFile"`
	// ExtractToCurrentFolder enables extraction to current folder
	ExtractToCurrentFolder	bool	`json:"extractToCurrentFolder"`
}
```

ExtractPolicy defines the extract policy for context synchronization

### Related Functions

#### NewExtractPolicy

```go
func NewExtractPolicy() *ExtractPolicy
```

NewExtractPolicy creates a new extract policy with default values

## Type RecyclePolicy

```go
type RecyclePolicy struct {
	// Lifecycle defines how long the context data should be retained
	Lifecycle	Lifecycle	`json:"lifecycle"`
	// Paths specifies which directories or files should be subject to the recycle policy
	Paths	[]string	`json:"paths"`
}
```

RecyclePolicy defines the recycle policy for context synchronization

The RecyclePolicy determines how long context data should be retained and which paths are subject to
the policy.

Lifecycle field determines the data retention period:
  - Lifecycle1Day: Keep data for 1 day
  - Lifecycle3Days: Keep data for 3 days
  - Lifecycle5Days: Keep data for 5 days
  - Lifecycle10Days: Keep data for 10 days
  - Lifecycle15Days: Keep data for 15 days
  - Lifecycle30Days: Keep data for 30 days
  - Lifecycle90Days: Keep data for 90 days
  - Lifecycle180Days: Keep data for 180 days
  - Lifecycle360Days: Keep data for 360 days
  - LifecycleForever: Keep data permanently (default)

Paths field specifies which directories or files should be subject to the recycle policy:
  - Must use exact directory/file paths
  - Wildcard patterns (* ? [ ]) are NOT supported
  - Empty string "" means apply to all paths in the context
  - Multiple paths can be specified as a slice
  - Default: []string{""} (applies to all paths)

### Methods

#### Validate

```go
func (rp *RecyclePolicy) Validate() error
```

Validate validates the RecyclePolicy configuration

### Related Functions

#### NewRecyclePolicy

```go
func NewRecyclePolicy() *RecyclePolicy
```

NewRecyclePolicy creates a new recycle policy with default values

## Type WhiteList

```go
type WhiteList struct {
	// Path is the path to include in the white list
	Path	string	`json:"path"`
	// ExcludePaths are the paths to exclude from the white list
	ExcludePaths	[]string	`json:"excludePaths,omitempty"`
}
```

WhiteList defines the white list configuration

### Methods

#### Validate

```go
func (wl *WhiteList) Validate() error
```

## Type BWList

```go
type BWList struct {
	// WhiteLists defines the white lists
	WhiteLists []*WhiteList `json:"whiteLists,omitempty"`
}
```

BWList defines the black and white list configuration

## Functions

### Deprecated

```go
func Deprecated(reason, replacement, version string)
```

Deprecated marks a function or method as deprecated and emits a warning

### DeprecatedFunc

```go
func DeprecatedFunc(reason, replacement, version string) func()
```

DeprecatedFunc is a helper function to mark functions as deprecated Usage: defer
DeprecatedFunc("reason", "replacement", "version")()

### DeprecatedMethod

```go
func DeprecatedMethod(methodName, reason, replacement, version string) func()
```

DeprecatedMethod is a helper function to mark methods as deprecated Usage: defer
DeprecatedMethod("MethodName", "reason", "replacement", "version")()

### FindDotEnvFile

```go
func FindDotEnvFile(startPath string) string
```

FindDotEnvFile searches for .env file upward from startPath. Search order: 1. Current working
directory 2. Parent directories (up to root) 3. Git repository root (if found)

Args:


startPath: Starting directory for search (empty string means current directory)

Returns:


Path to .env file if found, empty string otherwise

### GetLogLevel

```go
func GetLogLevel() int
```

GetLogLevel returns the current global log level

### LoadDotEnvWithFallback

```go
func LoadDotEnvWithFallback(customEnvPath string)
```

LoadDotEnvWithFallback loads .env file with improved search strategy.

Args:


customEnvPath: Custom path to .env file (empty string means search upward)

### LogAPICall

```go
func LogAPICall(apiName, requestParams string)
```

LogAPICall logs an API call with request parameters

### LogAPIResponseWithDetails

```go
func LogAPIResponseWithDetails(apiName, requestID string, success bool, keyFields map[string]interface{}, fullResponse string)
```

LogAPIResponseWithDetails logs a structured API response with key fields

### LogCodeExecutionOutput

```go
func LogCodeExecutionOutput(requestID, rawOutput string)
```

LogCodeExecutionOutput extracts and logs the actual code execution output from run_code response

### LogOperationError

```go
func LogOperationError(operation, errorMsg string, withStack bool)
```

LogOperationError logs an operation error with optional stack trace

### MaskSensitiveData

```go
func MaskSensitiveData(data interface{}) interface{}
```

MaskSensitiveData recursively masks sensitive information in data structures

### SetDeprecationConfig

```go
func SetDeprecationConfig(config *DeprecationConfig)
```

SetDeprecationConfig sets the global deprecation configuration

### SetLogLevel

```go
func SetLogLevel(level int)
```

SetLogLevel sets the global log level

### SetupLogger

```go
func SetupLogger(config LoggerConfig)
```

SetupLogger configures the logger with file logging support

### TestCreateLogging

```go
func TestCreateLogging(t *testing.T)
```

TestCreateLogging verifies that Create() method uses new structured logging

### TestErrorHandlingStructure

```go
func TestErrorHandlingStructure(t *testing.T)
```

TestErrorHandlingStructure verifies error response handling structure

### TestIsSensitiveField

```go
func TestIsSensitiveField(t *testing.T)
```

TestIsSensitiveField verifies the sensitive field detection

### TestKeyFieldsExtraction

```go
func TestKeyFieldsExtraction(t *testing.T)
```

TestKeyFieldsExtraction verifies key fields can be properly extracted for logging

### TestListSessionParams

```go
func TestListSessionParams(t *testing.T)
```

TestListSessionParams verifies ListSessionParams initialization

### TestLogAPICall

```go
func TestLogAPICall(t *testing.T)
```

TestLogAPICall verifies LogAPICall produces correct formatted output

### TestLogAPIResponseWithDetailsFailure

```go
func TestLogAPIResponseWithDetailsFailure(t *testing.T)
```

TestLogAPIResponseWithDetailsFailure verifies failed API response logging

### TestLogAPIResponseWithDetailsSuccess

```go
func TestLogAPIResponseWithDetailsSuccess(t *testing.T)
```

TestLogAPIResponseWithDetailsSuccess verifies successful API response logging

### TestLogLevelConstants

```go
func TestLogLevelConstants(t *testing.T)
```

TestLogLevelConstants verifies log level constants

### TestLogLevelControl

```go
func TestLogLevelControl(t *testing.T)
```

TestLogLevelControl tests the log level control functionality

### TestLogOperationErrorWithStack

```go
func TestLogOperationErrorWithStack(t *testing.T)
```

TestLogOperationErrorWithStack verifies error logging with stack trace

### TestLogOperationErrorWithoutStack

```go
func TestLogOperationErrorWithoutStack(t *testing.T)
```

TestLogOperationErrorWithoutStack verifies error logging without stack trace

### TestMaskSensitiveDataInRequestParams

```go
func TestMaskSensitiveDataInRequestParams(t *testing.T)
```

TestMaskSensitiveDataInRequestParams verifies sensitive data masking in API requests

### TestMaskSensitiveDataPreservesNonSensitive

```go
func TestMaskSensitiveDataPreservesNonSensitive(t *testing.T)
```

TestMaskSensitiveDataPreservesNonSensitive verifies non-sensitive data is unchanged

### TestMaskSensitiveDataWithArray

```go
func TestMaskSensitiveDataWithArray(t *testing.T)
```

TestMaskSensitiveDataWithArray verifies masking in arrays

### TestMaskSensitiveDataWithMapApiKey

```go
func TestMaskSensitiveDataWithMapApiKey(t *testing.T)
```

TestMaskSensitiveDataWithMapApiKey verifies API key masking in maps

### TestMaskSensitiveDataWithNestedStructure

```go
func TestMaskSensitiveDataWithNestedStructure(t *testing.T)
```

TestMaskSensitiveDataWithNestedStructure verifies recursive masking

### TestMaskSensitiveDataWithPassword

```go
func TestMaskSensitiveDataWithPassword(t *testing.T)
```

TestMaskSensitiveDataWithPassword verifies password masking

### TestMaskSensitiveDataWithShortSecret

```go
func TestMaskSensitiveDataWithShortSecret(t *testing.T)
```

TestMaskSensitiveDataWithShortSecret verifies masking of short sensitive values

### TestMaskSensitiveDataWithToken

```go
func TestMaskSensitiveDataWithToken(t *testing.T)
```

TestMaskSensitiveDataWithToken verifies token masking

### TestNewListSessionParams

```go
func TestNewListSessionParams(t *testing.T)
```

TestNewListSessionParams verifies default parameter initialization

### TestRequestIDExtraction

```go
func TestRequestIDExtraction(t *testing.T)
```

TestRequestIDExtraction simulates RequestID extraction for logging

### TestResponseJSONMarshaling

```go
func TestResponseJSONMarshaling(t *testing.T)
```

TestResponseJSONMarshaling verifies response data can be properly JSON marshaled

### containsWildcard

```go
func containsWildcard(path string) bool
```

### getColorCodes

```go
func getColorCodes() (reset, green, red, yellow, blue string)
```

getColorCodes returns ANSI color codes based on environment detection

### getVersion

```go
func getVersion() string
```

getVersion attempts to read version from Go module info Returns the version from go.mod or a default
fallback

### init

```go
func init()
```

Initialize log level from environment variable

### isIDEEnvironment

```go
func isIDEEnvironment() bool
```

isIDEEnvironment detects if running in an IDE that supports ANSI colors

### isReleaseVersion

```go
func isReleaseVersion() bool
```

isReleaseVersion checks if this is a release build Returns true only if the SDK is installed from
GitHub (github.com/aliyun/wuying-agentbay-sdk/golang) Returns false if: 1. Developing the SDK
locally (main module) 2. Installed via go.mod replace from internal source (code.alibaba-inc.com) 3.
Installed from a pseudo-version

### isSensitiveField

```go
func isSensitiveField(fieldName string, sensitiveFields []string) bool
```

### isValidLifecycle

```go
func isValidLifecycle(lifecycle Lifecycle) bool
```

isValidLifecycle checks if the given lifecycle value is valid

### isValidUploadMode

```go
func isValidUploadMode(uploadMode UploadMode) bool
```

isValidUploadMode checks if the given uploadMode value is valid

### maskSensitiveDataInternal

```go
func maskSensitiveDataInternal(data interface{}, fields []string) interface{}
```

### maskSensitiveDataString

```go
func maskSensitiveDataString(jsonStr string) string
```

maskSensitiveDataString masks sensitive information in a JSON string

### maskSensitiveDataWithRegex

```go
func maskSensitiveDataWithRegex(str string) string
```

maskSensitiveDataWithRegex masks sensitive data using regex patterns

### parseFileSize

```go
func parseFileSize(sizeStr string) int64
```

parseFileSize parses size string like "10 MB" to bytes

### parseLogLevel

```go
func parseLogLevel(levelStr string) int
```

parseLogLevel converts string to log level constant

### validateSyncPolicy

```go
func validateSyncPolicy(policy *SyncPolicy) error
```

### writeToFile

```go
func writeToFile(message string)
```

writeToFile writes a message to the log file with rotation

---

*Documentation generated automatically from Go source code.*
