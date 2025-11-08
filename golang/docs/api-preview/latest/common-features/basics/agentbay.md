# AgentBay API Reference

## 🚀 Related Tutorial

- [First Session Tutorial](../../../../../docs/quickstart/first-session.md) - Get started with creating your first AgentBay session

## Type AgentBayConfig

```go
type AgentBayConfig struct {
	cfg	*Config
	envFile	string
}
```

AgentBayConfig holds optional configuration for the AgentBay client.

## Type AgentBay

```go
type AgentBay struct {
	APIKey		string
	Client		*mcp.Client
	Sessions	sync.Map
	Context		*ContextService
}
```

AgentBay represents the main client for interacting with the AgentBay cloud runtime environment.

### Methods

#### Create

```go
func (a *AgentBay) Create(params *CreateSessionParams) (*SessionResult, error)
```

Create creates a new session in the AgentBay cloud environment. If params is nil, default parameters
will be used. Create creates a new AgentBay session with specified configuration.

Parameters:
  - params: Configuration parameters for the session (optional)
  - Labels: Key-value pairs for session metadata
  - ImageId: Custom image ID for the session environment
  - IsVpc: Whether to create a VPC session
  - PolicyId: Security policy ID
  - ExtraConfigs: Additional configuration options

Returns:
  - *SessionResult: Result containing Session object and request ID
  - error: Error if the operation fails

Behavior:

- Creates a new isolated cloud runtime environment - Waits for session to be ready before returning
- For VPC sessions, includes VPC-specific configuration

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

	// Create session with default parameters

	result, err := client.Create(nil)
	if err != nil {
		panic(err)
	}
	session := result.Session
	fmt.Printf("Session ID: %s\n", session.SessionID)

	// Output: Session ID: session-04bdwfj7u22a1s30g

	// Create session with custom parameters

	params := agentbay.NewCreateSessionParams()
	params.Labels = map[string]string{"project": "demo"}
	params.IsVpc = true
	customResult, err := client.Create(params)
	if err != nil {
		panic(err)
	}
	fmt.Println("VPC session created")

	// Output: VPC session created

	// RECOMMENDED: Create a session with context synchronization

	// First, create a context

	contextResult, err := client.Context.Get("my-context", true)
	if err != nil {
		panic(err)
	}

	// Result: Created context with ID: SdkCtx-xxxxxxxxxxxxxxx

	contextSync := &agentbay.ContextSync{
		ContextID: contextResult.Context.ID,
		Path:      "/home/wuying",
		Policy:    agentbay.NewSyncPolicy(),
	}
	syncParams := &agentbay.CreateSessionParams{
		ImageId:     "windows_latest",
		ContextSync: []*agentbay.ContextSync{contextSync},
	}
	syncResult, err := client.Create(syncParams)
	if err != nil {
		panic(err)
	}
	fmt.Printf("Created session with context sync: %s\n", syncResult.Session.SessionID)

	// Result: Waiting for context synchronization to complete...

	// Result: Context SdkCtx-xxxxxxxxxxxxxxx status: Preparing, path: /home/wuying

	// Result: Context SdkCtx-xxxxxxxxxxxxxxx status: Success, path: /home/wuying

	// Result: Context synchronization completed successfully

	// Result: Created session with context sync: session-xxxxxxxxxxxxxxx

	session.Delete()
	customResult.Session.Delete()
	syncResult.Session.Delete()
}
```

#### Delete

```go
func (a *AgentBay) Delete(session *Session, syncContext ...bool) (*DeleteResult, error)
```

Delete deletes a session by ID.

#### Get

```go
func (a *AgentBay) Get(sessionID string) (*SessionResult, error)
```

Get retrieves a session by its ID. This method calls the GetSession API and returns a SessionResult
containing the Session object and request ID.

Parameters:
  - sessionID: The ID of the session to retrieve

Returns:
  - *SessionResult: Result containing the Session instance, request ID, and success status
  - error: An error if the operation fails

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
	createResult, err := client.Create(nil)
	if err != nil {
		fmt.Printf("Error: %v\n", err)
		os.Exit(1)
	}
	sessionID := createResult.Session.SessionID
	fmt.Printf("Created session with ID: %s\n", sessionID)

	// Output: Created session with ID: session-xxxxxxxxxxxxxx

	result, err := client.Get(sessionID)
	if err != nil {
		fmt.Printf("Error: %v\n", err)
		os.Exit(1)
	}
	if result.Success {
		fmt.Printf("Successfully retrieved session: %s\n", result.Session.SessionID)

		// Output: Successfully retrieved session: session-xxxxxxxxxxxxxx

		fmt.Printf("Request ID: %s\n", result.RequestID)

		// Output: Request ID: XXXXXXXX-XXXX-XXXX-XXXX-XXXXXXXXXXXX

		deleteResult, err := result.Session.Delete()
		if err != nil {
			fmt.Printf("Error: %v\n", err)
			os.Exit(1)
		}
		if deleteResult.Success {
			fmt.Printf("Session %s deleted successfully\n", sessionID)

			// Output: Session session-xxxxxxxxxxxxxx deleted successfully

		}
	} else {
		fmt.Printf("Failed to get session: %s\n", result.ErrorMessage)
	}
}
```

#### GetSession

```go
func (a *AgentBay) GetSession(sessionID string) (*GetSessionResult, error)
```

GetSession retrieves session information by session ID

#### List

```go
func (a *AgentBay) List(labels map[string]string, page *int, limit *int32) (*SessionListResult, error)
```

List returns paginated list of session IDs filtered by labels.

Parameters:
  - labels: Optional labels to filter sessions (can be nil for no filtering)
  - page: Optional page number for pagination (starting from 1, nil or 0 for first page)
  - limit: Optional maximum number of items per page (nil or 0 uses default of 10)

Returns:
  - *SessionListResult: Paginated list of session IDs that match the labels
  - error: An error if the operation fails

**Example:**

```go
agentBay, _ := agentbay.NewAgentBay("your_api_key")

// List all sessions

result, err := agentBay.List(nil, nil, nil)

// List sessions with specific labels

result, err := agentBay.List(map[string]string{"project": "demo"}, nil, nil)

// List sessions with pagination

page := 2
limit := int32(10)
result, err := agentBay.List(map[string]string{"my-label": "my-value"}, &page, &limit)
if err == nil {
    for _, sessionId := range result.SessionIds {
        fmt.Printf("Session ID: %s\n", sessionId)
    }
    fmt.Printf("Total count: %d\n", result.TotalCount)
    fmt.Printf("Request ID: %s\n", result.RequestID)
}
```

### Related Functions

#### NewAgentBay

```go
func NewAgentBay(apiKey string, opts ...Option) (*AgentBay, error)
```

NewAgentBay creates a new AgentBay client. If apiKey is empty, it will look for the AGENTBAY_API_KEY
environment variable.

#### NewAgentBayWithDefaults

```go
func NewAgentBayWithDefaults(apiKey string) (*AgentBay, error)
```

NewAgentBayWithDefaults creates a new AgentBay client using default configuration. This is a
convenience function that allows calling NewAgentBay without a config parameter.

## Type Option

```go
type Option func(*AgentBayConfig)
```

Option is a function that sets optional parameters for AgentBay client.

### Related Functions

#### WithConfig

```go
func WithConfig(cfg *Config) Option
```

WithConfig returns an Option that sets the configuration for the AgentBay client.

#### WithEnvFile

```go
func WithEnvFile(envFile string) Option
```

WithEnvFile returns an Option that sets a custom .env file path for the AgentBay client.

## Functions

### NewAgentBay

```go
func NewAgentBay(apiKey string, opts ...Option) (*AgentBay, error)
```

NewAgentBay creates a new AgentBay client. If apiKey is empty, it will look for the AGENTBAY_API_KEY
environment variable.

### NewAgentBayWithDefaults

```go
func NewAgentBayWithDefaults(apiKey string) (*AgentBay, error)
```

NewAgentBayWithDefaults creates a new AgentBay client using default configuration. This is a
convenience function that allows calling NewAgentBay without a config parameter.

### WithConfig

```go
func WithConfig(cfg *Config) Option
```

WithConfig returns an Option that sets the configuration for the AgentBay client.

### WithEnvFile

```go
func WithEnvFile(envFile string) Option
```

WithEnvFile returns an Option that sets a custom .env file path for the AgentBay client.

## Related Resources

- [Session API Reference](session.md)
- [Context API Reference](context.md)

---

*Documentation generated automatically from Go source code.*
