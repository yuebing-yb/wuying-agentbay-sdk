# AgentBay Class API Reference

The `AgentBay` class is the main entry point for interacting with the AgentBay cloud environment. It provides methods for creating, retrieving, listing, and deleting sessions.

## RequestID Standardization

All API calls in the SDK return a unique request identifier (RequestID) as part of their response. This RequestID can be used for debugging, tracking, and correlating API requests with server-side logs.

### Golang

In Golang, all API responses inherit from the base `ApiResponse` type which contains the RequestID:

```go
type ApiResponse struct {
    RequestID string
}
```

API methods return structured results that embed this base type, for example:

```go
type SessionResult struct {
    ApiResponse
    Session *Session
}
```

You can access the RequestID directly from the result:

```go
result, err := agentBay.Create(nil)
if err != nil {
    // Handle error
}
fmt.Printf("Session created with ID: %s, RequestID: %s\n",
    result.Session.SessionID, result.RequestID)
```

## Constructor

### Python

```python
AgentBay(api_key=None)
```

**Parameters:**
- `api_key` (str, optional): The API key for authentication. If not provided, the SDK will look for the `AGENTBAY_API_KEY` environment variable.

**Raises:**
- `ValueError`: If no API key is provided and `AGENTBAY_API_KEY` environment variable is not set.

### TypeScript

```typescript
new AgentBay({
  apiKey?: string;
})
```

**Parameters:**
- `apiKey` (string, optional): The API key for authentication. If not provided, the SDK will look for the `AGENTBAY_API_KEY` environment variable.

### Golang

```go
NewAgentBay(apiKey string) (*AgentBay, error)
```

**Parameters:**
- `apiKey` (string): The API key for authentication. If empty, the SDK will look for the `AGENTBAY_API_KEY` environment variable.

**Returns:**
- `*AgentBay`: A pointer to the AgentBay instance.
- `error`: An error if the initialization fails.

## Methods

### create / Create

Creates a new session in the AgentBay cloud environment.

#### Python

```python
create(params: Optional[CreateSessionParams] = None) -> SessionResult
```

**Parameters:**
- `params` (CreateSessionParams, optional): Parameters for session creation. If None, default parameters will be used.

**Returns:**
- `SessionResult`: A result object containing the new Session instance, success status, request ID, and error message if any.

**Raises:**
- `AgentBayError`: If the session creation fails due to API errors or other issues.

#### TypeScript

```typescript
create(): Promise<Session>
```

**Returns:**
- `Promise<Session>`: A promise that resolves to a new Session instance.

**Throws:**
- `Error`: If the session creation fails.

#### Golang

```go
Create(params *CreateSessionParams) (*SessionResult, error)
```

**Parameters:**
- `params` (*CreateSessionParams, optional): Parameters for session creation. If nil, default parameters will be used.

**Returns:**
- `*SessionResult`: A result object containing the new Session instance and RequestID.
- `error`: An error if the session creation fails.

### list / List

Lists all available sessions cached in the current client instance.

#### Python

```python
list() -> List[Session]
```

**Returns:**
- `List[Session]`: A list of Session instances currently cached in the client.

**Raises:**
- `AgentBayError`: If the session listing fails.

#### TypeScript

```typescript
list(): Promise<Session[]>
```

**Returns:**
- `Promise<Session[]>`: A promise that resolves to an array of Session instances.

**Throws:**
- `Error`: If the session listing fails.

#### Golang

```go
List() (*SessionListResult, error)
```

**Returns:**
- `*SessionListResult`: A result object containing an array of Session instances and RequestID.
- `error`: An error if the session listing fails.

### list_by_labels / listByLabels / ListByLabels

Lists sessions filtered by the provided labels. It returns sessions that match all the specified labels.

#### Python

```python
list_by_labels(labels: Dict[str, str]) -> SessionListResult
```

**Parameters:**
- `labels` (Dict[str, str]): A dictionary of labels to filter sessions by.

**Returns:**
- `SessionListResult`: A result object containing a list of Session instances that match the specified labels, success status, request ID, and error message if any.

**Raises:**
- `AgentBayError`: If the session listing fails due to API errors or other issues.

#### TypeScript

```typescript
listByLabels(labels: Record<string, string>): Promise<Session[]>
```

**Parameters:**
- `labels` (Record<string, string>): An object of labels to filter sessions by.

**Returns:**
- `Promise<Session[]>`: A promise that resolves to an array of Session instances that match the specified labels.

**Throws:**
- `Error`: If the session listing fails.

#### Golang

```go
ListByLabels(labels map[string]string) (*SessionListResult, error)
```

**Parameters:**
- `labels` (map[string]string): A map of labels to filter sessions by.

**Returns:**
- `*SessionListResult`: A result object containing an array of Session instances and RequestID.
- `error`: An error if the session listing fails.

### delete / Delete

Deletes a session by ID.

#### Python

```python
delete(session_id: str) -> bool
```

**Parameters:**
- `session_id` (str): The ID of the session to delete.

**Returns:**
- `bool`: True if the session was deleted successfully, False otherwise.

**Raises:**
- `AgentBayError`: If the session deletion fails.

#### TypeScript

```typescript
delete(sessionId: string): Promise<boolean>
```

**Parameters:**
- `sessionId` (string): The ID of the session to delete.

**Returns:**
- `Promise<boolean>`: A promise that resolves to true if the session was deleted successfully, false otherwise.

**Throws:**
- `Error`: If the session deletion fails.

#### Golang

```go
Delete(session *Session) (*DeleteResult, error)
```

**Parameters:**
- `session` (*Session): The session to delete.

**Returns:**
- `*DeleteResult`: A result object containing success status and RequestID.
- `error`: An error if the session deletion fails.

## Context Service

The AgentBay class also provides access to the Context service, which allows you to manage persistent contexts.

### Python

```python
# Access the Context service
context_result = agent_bay.context.get("my-context", create=True)
if context_result.success:
    context = context_result.context
    print(f"Context ID: {context.id}")
else:
    print(f"Failed to get context: {context_result.error_message}")
```

### TypeScript

```typescript
// Access the Context service
const context = await agentBay.context.get("my-context", true);
```

### Golang

```go
// Access the Context service
context, err := agentBay.Context.Get("my-context", true)
```

For more information on the Context service, see the [Contexts](../concepts/contexts.md) documentation.

## Usage Examples

### Python

```python
from agentbay import AgentBay
from agentbay.exceptions import AgentBayError
from agentbay.session_params import CreateSessionParams

def main():
    # Initialize with API key
    api_key = "your_api_key"  # Or use os.environ.get("AGENTBAY_API_KEY")

    try:
        agent_bay = AgentBay(api_key=api_key)

        # Create a session with labels
        params = CreateSessionParams()
        params.labels = {
            "purpose": "demo",
            "environment": "development"
        }
        session_result = agent_bay.create(params)
        if not session_result.success:
            print(f"Failed to create session: {session_result.error_message}")
            return

        session = session_result.session
        print(f"Session created with ID: {session.session_id}, RequestID: {session_result.request_id}")

        # List all sessions
        all_sessions = agent_bay.list()
        print(f"Found {len(all_sessions)} sessions")

        # List sessions by labels
        filtered_result = agent_bay.list_by_labels({
            "purpose": "demo"
        })
        if not filtered_result.success:
            print(f"Failed to list sessions by labels: {filtered_result.error_message}")
        else:
            print(f"Found {len(filtered_result.sessions)} matching sessions, RequestID: {filtered_result.request_id}")

        # Delete the session
        delete_result = session.delete()
        if delete_result.success:
            print(f"Session deleted successfully, RequestID: {delete_result.request_id}")
        else:
            print(f"Failed to delete session: {delete_result.error_message}")

    except AgentBayError as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    main()
```

### TypeScript

```typescript
import { AgentBay } from 'wuying-agentbay-sdk';

async function main() {
  try {
    // Initialize with API key
    const agentBay = new AgentBay({ apiKey: 'your_api_key' });

    // Create a session with labels
    const session = await agentBay.create({
      labels: {
        purpose: 'demo',
        environment: 'development'
      }
    });
    log(`Session created with ID: ${session.sessionId}`);

    // List all sessions
    const allSessions = agentBay.list();
    log(`Found ${allSessions.length} sessions`);

    // List sessions by labels
    const filteredSessions = await agentBay.listByLabels({
      purpose: 'demo'
    });
    log(`Found ${filteredSessions.length} matching sessions`);

    // Delete the session
    await agentBay.delete(session);
    log('Session deleted successfully');
  } catch (error) {
    logError('Error:', error);
  }
}

main();
```

### Golang

```go
package main

import (
	"fmt"
	"os"

	"github.com/aliyun/wuying-agentbay-sdk/golang/pkg/agentbay"
)

func main() {
	// Initialize with API key
	apiKey := os.Getenv("AGENTBAY_API_KEY")
	if apiKey == "" {
		apiKey = "your_api_key" // Replace with your actual API key
	}

	client, err := agentbay.NewAgentBay(apiKey)
	if err != nil {
		fmt.Printf("Error initializing AgentBay client: %v\n", err)
		os.Exit(1)
	}

	// Create a session with labels
	params := agentbay.NewCreateSessionParams().
		WithLabels(map[string]string{
			"purpose":     "demo",
			"environment": "development",
		})
	session, err := client.Create(params)
	if err != nil {
		fmt.Printf("Error creating session: %v\n", err)
		os.Exit(1)
	}
	fmt.Printf("Session created with ID: %s, RequestID: %s\n",
		session.SessionID, session.RequestID)

	// List all sessions
	sessions, err := client.List()
	if err != nil {
		fmt.Printf("Error listing sessions: %v\n", err)
		os.Exit(1)
	}
	fmt.Printf("Found %d sessions, RequestID: %s\n", len(sessions), sessions.RequestID)

	// List sessions by labels
	filteredSessions, err := client.ListByLabels(map[string]string{
		"purpose": "demo",
	})
	if err != nil {
		fmt.Printf("Error listing sessions by labels: %v\n", err)
		os.Exit(1)
	}
	fmt.Printf("Found %d matching sessions, RequestID: %s\n", len(filteredSessions), filteredSessions.RequestID)

	// Delete the session
	result, err := client.Delete(session)
	if err != nil {
		fmt.Printf("Error deleting session: %v\n", err)
		os.Exit(1)
	}
	fmt.Printf("Session deleted successfully, RequestID: %s\n", result.RequestID)
}
```
