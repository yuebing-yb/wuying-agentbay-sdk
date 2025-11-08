# Session API Reference

## 🚀 Related Tutorial

- [First Session Tutorial](../../../../../docs/quickstart/first-session.md) - Get started with creating your first AgentBay session

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

This is the unified public API for calling MCP tools. All feature modules (Command, Code, Agent,
etc.) use this method internally.

Parameters:
  - toolName: Name of the MCP tool to call
  - args: Arguments to pass to the tool (typically a map or struct)
  - autoGenSession: Optional boolean to auto-generate session if not exists (default: false)

Returns:
  - *models.McpToolResult: Result containing:
  - Success: Whether the tool call was successful
  - Data: Tool output data (text content extracted from response)
  - ErrorMessage: Error message if the call failed
  - RequestID: Unique identifier for the API request
  - error: Error if the call fails at the transport level

Behavior:

- Automatically detects VPC vs non-VPC mode - In VPC mode, uses HTTP requests to the VPC endpoint
- In non-VPC mode, uses traditional API calls - Parses response data to extract text content from
content[0].text - Handles the isError flag in responses - Returns structured error information

**Example:**

```go
package main
import (
	"fmt"
	"os"
	"github.com/aliyun/wuying-agentbay-sdk/golang/pkg/agentbay"
)
func main() {
	client, err := agentbay.NewAgentBay(os.Getenv("AGENTBAY_API_KEY"), nil)
	if err != nil {
		fmt.Printf("Error: %v\n", err)
		os.Exit(1)
	}
	result, err := client.Create(nil)
	if err != nil {
		fmt.Printf("Error: %v\n", err)
		os.Exit(1)
	}
	session := result.Session

	// Call the shell tool to execute a command

	toolResult, err := session.CallMcpTool("shell", map[string]interface{}{
		"command":    "echo 'Hello World'",
		"timeout_ms": 1000,
	})
	if err != nil {
		fmt.Printf("Error calling tool: %v\n", err)
		os.Exit(1)
	}
	if toolResult.Success {
		fmt.Printf("Output: %s\n", toolResult.Data)

		// Output: Hello World

		fmt.Printf("Request ID: %s\n", toolResult.RequestID)
	} else {
		fmt.Printf("Error: %s\n", toolResult.ErrorMessage)
	}

	// Example with error handling

	toolResult2, err := session.CallMcpTool("shell", map[string]interface{}{
		"command":    "invalid_command_12345",
		"timeout_ms": 1000,
	})
	if err != nil {
		fmt.Printf("Error calling tool: %v\n", err)
		os.Exit(1)
	}
	if !toolResult2.Success {
		fmt.Printf("Command failed: %s\n", toolResult2.ErrorMessage)

		// Output: Command failed: sh: 1: invalid_command_12345: not found

	}
	session.Delete()
}
```

#### CallMcpToolForBrowser

```go
func (s *Session) CallMcpToolForBrowser(toolName string, args interface{}) (*browser.McpToolResult, error)
```

CallMcpTool is a wrapper that converts the result to browser.McpToolResult

#### Delete

```go
func (s *Session) Delete(syncContext ...bool) (*DeleteResult, error)
```

Delete deletes this session. Delete deletes the session and releases all associated resources.

Parameters:
  - syncContext: Optional boolean to synchronize context data before deletion. If true, uploads all
    context data to OSS. Defaults to false.

Returns:
  - *DeleteResult: Result containing success status and request ID
  - error: Error if the operation fails

Behavior:

- If syncContext is true: Uploads all context data to OSS before deletion - If syncContext is false:
Deletes immediately without sync - Continues with deletion even if context sync fails - Releases all
associated resources (browser, computer, mobile, etc.)

**Example:**

```go
package main
import (
	"fmt"
	"github.com/aliyun/wuying-agentbay-sdk/golang/pkg/agentbay"
)
func main() {

	// Initialize the SDK

	client, err := agentbay.NewAgentBay("your_api_key")
	if err != nil {
		panic(err)
	}

	// Create a session

	result, err := client.Create(nil)
	if err != nil {
		panic(err)
	}
	session := result.Session
	fmt.Printf("Session ID: %s\n", session.SessionID)

	// Output: Session ID: session-04bdwfj7u22a1s30g

	// Delete session without context sync

	deleteResult, err := session.Delete()
	if err != nil {
		panic(err)
	}
	if deleteResult.Success {
		fmt.Println("Session deleted successfully")

		// Output: Session deleted successfully

	}
}
Note:
- Use syncContext=true when you need to preserve context data - For temporary sessions, use
syncContext=false for faster cleanup - Always call Delete() when done to avoid resource leaks
```

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

Returns:
  - *LabelResult: Result containing labels as JSON string and request ID
  - error: Error if the operation fails

Behavior:

- Retrieves the labels that were previously set for this session - Returns labels as a JSON string -
Can be used to identify and filter sessions

**Example:**

```go
package main
import (
	"encoding/json"
	"fmt"
	"github.com/aliyun/wuying-agentbay-sdk/golang/pkg/agentbay"
)
func main() {
	client, err := agentbay.NewAgentBay("your_api_key")
	if err != nil {
		panic(err)
	}

	// Create a session with labels

	params := agentbay.NewCreateSessionParams()
	params.Labels = map[string]string{
		"project": "demo",
		"env":     "production",
	}
	result, err := client.Create(params)
	if err != nil {
		panic(err)
	}
	session := result.Session

	// Get labels from the session

	labelResult, err := session.GetLabels()
	if err != nil {
		panic(err)
	}
	fmt.Printf("Retrieved labels: %s\n", labelResult.Labels)

	// Output: Retrieved labels: {"project":"demo","env":"production"}

	// Parse the JSON to use the labels

	var labels map[string]string
	if err := json.Unmarshal([]byte(labelResult.Labels), &labels); err == nil {
		fmt.Printf("Project: %s, Environment: %s\n", labels["project"], labels["env"])

		// Output: Project: demo, Environment: production

	}
	session.Delete()
}
```

#### GetLink

```go
func (s *Session) GetLink(protocolType *string, port *int32, options *string) (*LinkResult, error)
```

GetLink gets the link for this session. GetLink retrieves an access link for the session.

Parameters:
  - protocolType: Protocol type for the link (optional, reserved for future use)
  - port: Specific port number to access (must be in range [30100, 30199])
  - options: Additional options (optional)

Returns:
  - *LinkResult: Result containing the access URL and request ID
  - error: Error if port is out of range or operation fails

Behavior:

- Without port: Returns the default session access URL - With port: Returns URL for accessing
specific port-mapped service - Port must be in range [30100, 30199] for port forwarding

**Example:**

```go
package main
import (
	"fmt"
	"github.com/aliyun/wuying-agentbay-sdk/golang/pkg/agentbay"
)
func main() {
	client, err := agentbay.NewAgentBay("your_api_key")
	if err != nil {
		panic(err)
	}
	result, err := client.Create(nil)
	if err != nil {
		panic(err)
	}
	session := result.Session

	// Get default session link

	linkResult, err := session.GetLink(nil, nil, nil)
	if err != nil {
		panic(err)
	}
	fmt.Printf("Session link: %s\n", linkResult.Link)

	// Output: Session link: https://session-04bdwfj7u22a1s30g.agentbay.com

	// Get link for specific port

	port := int32(30150)
	portLinkResult, err := session.GetLink(nil, &port, nil)
	if err != nil {
		panic(err)
	}
	fmt.Printf("Port 30150 link: %s\n", portLinkResult.Link)

	// Output: Port 30150 link: https://session-04bdwfj7u22a1s30g-30150.agentbay.com

	session.Delete()
}
Note:
- Use default link for general session access - Use port-specific links for services on specific
ports - Validate port range before calling to avoid errors
```

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

Info gets information about this session. Info retrieves detailed information about the current
session.

Returns:
  - *InfoResult: Result containing SessionInfo object and request ID
  - error: Error if the operation fails or session not found

Behavior:

- Retrieves current session metadata from the backend - Includes resource URL, type, and connection
properties - Information is fetched in real-time from the API

**Example:**

```go
package main
import (
	"fmt"
	"github.com/aliyun/wuying-agentbay-sdk/golang/pkg/agentbay"
)
func main() {
	client, err := agentbay.NewAgentBay("your_api_key")
	if err != nil {
		panic(err)
	}
	result, err := client.Create(nil)
	if err != nil {
		panic(err)
	}
	session := result.Session

	// Get session information

	infoResult, err := session.Info()
	if err != nil {
		panic(err)
	}
	info := infoResult.Info
	fmt.Printf("Session ID: %s\n", info.SessionId)
	fmt.Printf("Resource URL: %s\n", info.ResourceUrl)
	fmt.Printf("Resource Type: %s\n", info.ResourceType)

	// Output:

	// Session ID: session-04bdwfj7u22a1s30g

	// Resource URL: https://...

	// Resource Type: vpc

	session.Delete()
}
```

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

Returns:
  - *McpToolsResult: Result containing list of MCP tools and request ID
  - error: Error if the operation fails

Behavior:

- Uses the ImageId from session creation - Defaults to "linux_latest" if ImageId is empty -
Retrieves all available MCP tools for the specified image - Updates the session's McpTools field
with the retrieved tools

**Example:**

```go
package main
import (
	"fmt"
	"os"
	"github.com/aliyun/wuying-agentbay-sdk/golang/pkg/agentbay"
)
func main() {
	client, err := agentbay.NewAgentBay(os.Getenv("AGENTBAY_API_KEY"), nil)
	if err != nil {
		fmt.Printf("Error: %v\n", err)
		os.Exit(1)
	}
	result, err := client.Create(nil)
	if err != nil {
		fmt.Printf("Error: %v\n", err)
		os.Exit(1)
	}
	session := result.Session

	// List MCP tools available for this session

	toolsResult, err := session.ListMcpTools()
	if err != nil {
		fmt.Printf("Error listing MCP tools: %v\n", err)
		os.Exit(1)
	}
	fmt.Printf("Found %d MCP tools\n", len(toolsResult.Tools))

	// Output: Found 27 MCP tools

	// Display first few tools

	for i, tool := range toolsResult.Tools {
		if i < 3 {
			fmt.Printf("Tool: %s - %s\n", tool.Name, tool.Description)
		}
	}

	// Output: Tool: execute_command - Execute a command on the system

	// Output: Tool: read_file - Read contents of a file

	// Output: Tool: write_file - Write content to a file

	fmt.Printf("Request ID: %s\n", toolsResult.RequestID)
	session.Delete()
}
```

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

Parameters:
  - labels: Labels to set for the session as a map of key-value pairs

Returns:
  - *LabelResult: Result containing request ID
  - error: Error if validation fails or operation fails

Behavior:

- Validates that labels map is not nil or empty - All keys and values must be non-empty strings
- Converts labels to JSON and sends to the backend - Labels can be used for session filtering and
organization

**Example:**

```go
package main
import (
	"fmt"
	"github.com/aliyun/wuying-agentbay-sdk/golang/pkg/agentbay"
)
func main() {
	client, err := agentbay.NewAgentBay("your_api_key")
	if err != nil {
		panic(err)
	}

	// Create a session

	result, err := client.Create(nil)
	if err != nil {
		panic(err)
	}
	session := result.Session

	// Set labels for the session

	labels := map[string]string{
		"project": "demo",
		"env":     "test",
	}
	labelResult, err := session.SetLabels(labels)
	if err != nil {
		panic(err)
	}
	fmt.Printf("Labels set successfully (RequestID: %s)\n", labelResult.RequestID)

	// Output: Labels set successfully (RequestID: 9E3F4A5B-2C6D-7E8F-9A0B-1C2D3E4F5A6B)

	// Get labels back

	getResult, err := session.GetLabels()
	if err != nil {
		panic(err)
	}
	fmt.Printf("Retrieved labels: %s\n", getResult.Labels)

	// Output: Retrieved labels: {"project":"demo","env":"test"}

	session.Delete()
}
```

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

### LogDebug

```go
func LogDebug(message string)
```

LogDebug logs a debug message

### LogInfo

```go
func LogInfo(message string)
```

LogInfo logs an informational message

### LogInfoWithColor

```go
func LogInfoWithColor(message string)
```

LogInfoWithColor logs an informational message with custom color

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

## Related Resources

- [Session API Reference](session.md)
- [Context API Reference](context.md)

---

*Documentation generated automatically from Go source code.*
