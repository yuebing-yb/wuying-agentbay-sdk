# Session API Reference

## 🔧 Related Tutorial

- [Session Management Guide](../../../../../docs/guides/common-features/basics/session-management.md) - Detailed tutorial on session lifecycle and management

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

#### GetToken

```go
func (s *Session) GetToken() string
```

GetToken returns the token for VPC sessions

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

## Type McpToolsResult

```go
type McpToolsResult struct {
	models.ApiResponse
	Tools	[]McpTool
}
```

McpToolsResult wraps MCP tools list and RequestID

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

## Functions

### Deprecated

```go
func Deprecated(reason, replacement, version string)
```

Deprecated marks a function or method as deprecated and emits a warning

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

**Example:**

```go
package main
import (
	"fmt"
	"github.com/aliyun/wuying-agentbay-sdk/golang/pkg/agentbay"
)
func main() {

	// Set log level to DEBUG

	agentbay.SetLogLevel(agentbay.LOG_DEBUG)

	// Check current level

	currentLevel := agentbay.GetLogLevel()
	fmt.Printf("Current log level: %d\n", currentLevel)
}
```

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

**Example:**

```go
package main
import (
	"fmt"
	"os"
	"github.com/aliyun/wuying-agentbay-sdk/golang/pkg/agentbay"
)
func main() {

	// Set log level to DEBUG to see API calls

	agentbay.SetLogLevel(agentbay.LOG_DEBUG)
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
	defer session.Delete()

	// API calls are automatically logged by the SDK

	// Output: 🔗 API Call: create_session

}
```

### LogAPIResponseWithDetails

```go
func LogAPIResponseWithDetails(apiName, requestID string, success bool, keyFields map[string]interface{}, fullResponse string)
```

LogAPIResponseWithDetails logs a structured API response with key fields

**Example:**

```go
package main
import (
	"fmt"
	"os"
	"github.com/aliyun/wuying-agentbay-sdk/golang/pkg/agentbay"
)
func main() {

	// Set log level to DEBUG to see detailed responses

	agentbay.SetLogLevel(agentbay.LOG_DEBUG)
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
	defer session.Delete()

	// API responses are automatically logged by the SDK

	// Output: ✅ API Response: create_session, RequestId=xxx

}
```

### LogCodeExecutionOutput

```go
func LogCodeExecutionOutput(requestID, rawOutput string)
```

LogCodeExecutionOutput extracts and logs the actual code execution output from run_code response

**Example:**

```go
package main
import (
	"fmt"
	"os"
	"github.com/aliyun/wuying-agentbay-sdk/golang/pkg/agentbay"
)
func main() {

	// Set log level to INFO to see code execution output

	agentbay.SetLogLevel(agentbay.LOG_INFO)
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
	defer session.Delete()

	// Execute code in the session

	execResult, err := session.Code.RunCode("print('Hello from AgentBay')", "python")
	if err != nil {
		fmt.Printf("Error: %v\n", err)
		os.Exit(1)
	}
	fmt.Printf("Code execution completed: %v\n", execResult.Success)

	// Output: 📋 Code Execution Output (RequestID: xxx):

	// Output:    Hello from AgentBay

}
```

### LogDebug

```go
func LogDebug(message string)
```

LogDebug logs a debug message

**Example:**

```go
package main
import (
	"fmt"
	"os"
	"github.com/aliyun/wuying-agentbay-sdk/golang/pkg/agentbay"
)
func main() {

	// Set log level to DEBUG to see debug messages

	agentbay.SetLogLevel(agentbay.LOG_DEBUG)
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
	defer session.Delete()

	// Log debug messages

	agentbay.LogDebug("Debugging session creation process")

	// Output: 🐛 Debugging session creation process

}
```

### LogInfo

```go
func LogInfo(message string)
```

LogInfo logs an informational message

**Example:**

```go
package main
import (
	"fmt"
	"os"
	"github.com/aliyun/wuying-agentbay-sdk/golang/pkg/agentbay"
)
func main() {

	// Set log level to INFO or DEBUG to see info messages

	agentbay.SetLogLevel(agentbay.LOG_INFO)
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
	defer session.Delete()

	// Log informational messages

	agentbay.LogInfo("Session created successfully")

	// Output: ℹ️  Session created successfully

}
```

### LogInfoWithColor

```go
func LogInfoWithColor(message string)
```

LogInfoWithColor logs an informational message with custom color

**Example:**

```go
package main
import (
	"fmt"
	"os"
	"github.com/aliyun/wuying-agentbay-sdk/golang/pkg/agentbay"
)
func main() {

	// Set log level to INFO or DEBUG to see colored messages

	agentbay.SetLogLevel(agentbay.LOG_INFO)
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
	defer session.Delete()

	// Log informational messages with color emphasis

	agentbay.LogInfoWithColor("Important: Session ready for use")

	// Output: ℹ️  Important: Session ready for use

}
```

### LogOperationError

```go
func LogOperationError(operation, errorMsg string, withStack bool)
```

LogOperationError logs an operation error with optional stack trace

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

		// Log operation errors

		agentbay.LogOperationError("Create Session", err.Error(), false)
		os.Exit(1)
	}
	session := result.Session
	defer session.Delete()

	// Output: ❌ Failed: Create Session

	// Output: 💥 Error: session creation failed

}
```

### MaskSensitiveData

```go
func MaskSensitiveData(data interface{}) interface{}
```

MaskSensitiveData recursively masks sensitive information in data structures

**Example:**

```go
package main
import (
	"fmt"
	"github.com/aliyun/wuying-agentbay-sdk/golang/pkg/agentbay"
)
func main() {

	// Create data with sensitive information

	data := map[string]interface{}{
		"api_key":    "sk_live_1234567890",
		"password":   "secret123",
		"auth_token": "Bearer xyz",
		"username":   "john_doe",
	}

	// Mask sensitive data

	masked := agentbay.MaskSensitiveData(data)
	fmt.Printf("Masked data: %v\n", masked)

	// Output: Masked data: map[api_key:sk****90 auth_token:Be****yz password:se****23 username:john_doe]

}
```

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

**Example:**

```go
package main
import (
	"fmt"
	"os"
	"github.com/aliyun/wuying-agentbay-sdk/golang/pkg/agentbay"
)
func main() {

	// Set log level to DEBUG to see all messages

	agentbay.SetLogLevel(agentbay.LOG_DEBUG)
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
	defer session.Delete()

	// Change to INFO level to reduce verbosity

	agentbay.SetLogLevel(agentbay.LOG_INFO)

	// Continue with your operations

}
```

### SetupLogger

```go
func SetupLogger(config LoggerConfig)
```

SetupLogger configures the logger with file logging support

**Example:**

```go
package main
import (
	"fmt"
	"os"
	"github.com/aliyun/wuying-agentbay-sdk/golang/pkg/agentbay"
)
func main() {

	// Configure file logging with rotation

	agentbay.SetupLogger(agentbay.LoggerConfig{
		Level:       "DEBUG",
		LogFile:     "/tmp/agentbay.log",
		MaxFileSize: "100 MB",
	})
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
	defer session.Delete()

	// All logs will be written to both console and file

}
```

## Related Resources

- [FileSystem API Reference](filesystem.md)
- [Command API Reference](command.md)
- [Context API Reference](context.md)
- [Context Manager API Reference](context-manager.md)
- [OSS API Reference](../advanced/oss.md)

---

*Documentation generated automatically from Go source code.*
