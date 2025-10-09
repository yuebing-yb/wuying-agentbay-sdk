# Get API Example

This example demonstrates how to use the `Get` API to retrieve a session by its ID.

## Description

The `Get` API allows you to retrieve a session object by providing its session ID. This is useful when you have a session ID from a previous operation and want to access or manage that session.

## Prerequisites

- Go 1.21 or higher
- Valid API key set in `AGENTBAY_API_KEY` environment variable

## Usage

```bash
# Set your API key
export AGENTBAY_API_KEY="your-api-key-here"

# Run the example
go run main.go
```

## Code Example

```go
package main

import (
    "fmt"
    "log"
    "os"

    "github.com/aliyun/wuying-agentbay-sdk/golang/pkg/agentbay"
)

func main() {
    // Initialize AgentBay client
    apiKey := os.Getenv("AGENTBAY_API_KEY")
    client, err := agentbay.NewAgentBay(apiKey, nil)
    if err != nil {
        log.Fatalf("Failed to initialize AgentBay client: %v", err)
    }

    // Retrieve a session by ID
    sessionID := "your-session-id"
    session, err := client.Get(sessionID)
    if err != nil {
        log.Fatalf("Failed to get session: %v", err)
    }

    fmt.Printf("Retrieved session: %s\n", session.SessionID)

    // Use the session for further operations
    // ...
}
```

## API Reference

### Get

```go
func (a *AgentBay) Get(sessionID string) (*Session, error)
```

Retrieves a session by its ID.

**Parameters:**
- `sessionID` (string): The ID of the session to retrieve

**Returns:**
- `*Session`: The Session instance
- `error`: An error if the operation fails

**Errors:**
- Returns error if `sessionID` is empty
- Returns error if session is not found
- Returns error if API call fails

## Expected Output

```
Creating a session...
Created session with ID: session-xxxxxxxxxxxxx

Retrieving session using Get API...
Successfully retrieved session:
  Session ID: session-xxxxxxxxxxxxx

Session is ready for use

Cleaning up...
Session session-xxxxxxxxxxxxx deleted successfully
```

## Notes

- The session ID must be valid and from an existing session
- The Get API internally calls the GetSession API endpoint
- The returned session object can be used for all session operations (commands, files, etc.)
- Always clean up sessions when done to avoid resource waste

