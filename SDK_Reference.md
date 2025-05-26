# Wuying AgentBay SDK Reference

## Table of Contents

- [Introduction](#introduction)
- [Installation](#installation)
- [Authentication](#authentication)
- [Core Concepts](#core-concepts)
- [API Reference](#api-reference)
  - [AgentBay Class](#agentbay-class)
  - [Session Class](#session-class)
  - [FileSystem Class](#filesystem-class)
  - [Command Class](#command-class)
  - [Adb Class](#adb-class)
- [Examples](#examples)
- [Error Handling](#error-handling)
- [Best Practices](#best-practices)

## Introduction

Wuying AgentBay SDK provides APIs for Python, TypeScript, and Golang to interact with the Alibaba Wuying AgentBay cloud runtime environment. This environment enables running commands, executing code, and manipulating files.

The SDK is designed to be easy to use and consistent across all supported languages, making it simple to integrate with your existing applications regardless of the programming language you're using.

## Installation

(Note: The following installation methods will be available in the future. Please refer to the current project documentation for setup instructions.)

### Python

```bash
pip install wuying-agentbay-sdk
```

### TypeScript

```bash
npm install wuying-agentbay-sdk
```

### Golang

```bash
go get github.com/aliyun/wuying-agentbay-sdk/golang/pkg/agentbay
```

## Authentication

Authentication is done using an API key, which can be provided in several ways:

1. As a parameter when initializing the SDK
2. Through environment variables (`AGENTBAY_API_KEY`)

### Python

```python
# Option 1: Provide API key directly
agent_bay = AgentBay(api_key="your_api_key")

# Option 2: Use environment variable
# export AGENTBAY_API_KEY=your_api_key
agent_bay = AgentBay()
```

### TypeScript

```typescript
// Option 1: Provide API key directly
const agentBay = new AgentBay({ apiKey: 'your_api_key' });

// Option 2: Use environment variable
// export AGENTBAY_API_KEY=your_api_key
const agentBay = new AgentBay();
```

### Golang

```go
// Option 1: Provide API key directly
client, err := agentbay.NewAgentBay("your_api_key")

// Option 2: Use environment variable
// export AGENTBAY_API_KEY=your_api_key
client, err := agentbay.NewAgentBay("")
```

## Core Concepts

The AgentBay SDK is built around a few core concepts:

### AgentBay Client

The main entry point for interacting with the AgentBay cloud environment. It provides methods for creating, retrieving, listing, and deleting sessions.

### Session

Represents a session in the AgentBay cloud environment. A session is a container for executing commands and manipulating files. Each session has its own isolated environment.

### FileSystem

Provides methods for reading files within a session.

### Command

Provides methods for executing commands within a session.

### Adb

Provides methods for executing ADB shell commands within a mobile environment (Android).

## API Reference

### AgentBay Class

The `AgentBay` class is the main entry point for interacting with the AgentBay cloud environment.

#### Constructor

##### Python

```python
AgentBay(api_key=None)
```

##### TypeScript

```typescript
new AgentBay({
  apiKey?: string;
})
```

##### Golang

```go
NewAgentBay(apiKey string) (*AgentBay, error)
```

#### Methods

##### create

Creates a new session in the AgentBay cloud environment.

###### Python

```python
create() -> Session
```

###### TypeScript

```typescript
create(): Promise<Session>
```

###### Golang

```go
Create() (*Session, error)
```

##### list / List

Lists all available sessions.

###### Python

```python
list() -> List[Dict[str, Any]]
```

###### TypeScript

```typescript
list(): Session[]
```

###### Golang

```go
List() ([]Session, error)
```

##### delete / Delete

Deletes a session by ID.

###### Python

```python
delete(session_id: str) -> bool
```

###### TypeScript

```typescript
delete(sessionId: string): Promise<boolean>
```

###### Golang

```go
Delete(session *Session) error
```

### Session Class

The `Session` class represents a session in the AgentBay cloud environment.

#### Properties

##### Python

- `session_id`: The ID of the session
- `filesystem`: The FileSystem instance for this session
- `command`: The Command instance for this session
- `adb`: The Adb instance for this session

##### TypeScript

- `sessionId`: The ID of the session
- `filesystem`: The FileSystem instance for this session
- `command`: The Command instance for this session
- `adb`: The Adb instance for this session

##### Golang

- `SessionID`: The ID of the session
- `FileSystem`: The FileSystem instance for this session
- `Command`: The Command instance for this session
- `Adb`: The Adb instance for this session

#### Methods


##### delete / Delete

Deletes the session.

###### Python

```python
delete() -> bool
```

###### TypeScript

```typescript
delete(): Promise<boolean>
```

###### Golang

```go
Delete() error
```

### FileSystem Class

The `FileSystem` class provides methods for reading files within a session.

#### Methods

##### read_file / ReadFile

Reads the contents of a file in the cloud environment.

###### Python

```python
read_file(path: str) -> str
```

###### TypeScript

```typescript
read_file(filePath: string): Promise<string>
```

###### Golang

```go
ReadFile(path string) (string, error)
```

### Command Class

The `Command` class provides methods for executing commands within a session.

#### Methods

##### execute_command / ExecuteCommand

Executes a command in the cloud environment.

###### Python

```python
execute_command(command: str) -> str
```

###### TypeScript

```typescript
execute_command(command: string): Promise<string>
```

###### Golang

```go
ExecuteCommand(command string) (string, error)
```

### Adb Class

The `Adb` class provides methods for executing ADB shell commands within a mobile environment (Android).

#### Methods

##### shell / Shell

Executes an ADB shell command in the mobile environment.

###### Python

```python
shell(command: str) -> str
```

###### TypeScript

```typescript
shell(command: string): Promise<string>
```

###### Golang

```go
Shell(command string) (string, error)
```


## Examples

### Basic Usage

#### Python

```python
from wuying_agentbay import AgentBay
from wuying_agentbay.exceptions import AgentBayError

# Initialize the AgentBay client
api_key = "your_api_key_here"
agent_bay = AgentBay(api_key=api_key)

# Create a new session
session = agent_bay.create()
print(f"Session created with ID: {session.session_id}")

# Execute a command
result = session.command.execute_command("ls -la")
print(f"Command result: {result}")

# Read a file
content = session.filesystem.read_file("/etc/hosts")
print(f"File content: {content}")

# Execute an ADB shell command (for mobile environments)
adb_result = session.adb.shell("ls /sdcard")
print(f"ADB shell result: {adb_result}")

# Delete the session
agent_bay.delete(session.session_id)
print("Session deleted successfully")
```

#### TypeScript

```typescript
import { AgentBay } from 'wuying-agentbay-sdk';

async function main() {
  // Initialize the AgentBay client
  const apiKey = 'your_api_key_here';
  const agentBay = new AgentBay({ apiKey });

  try {
    // Create a new session
    const session = await agentBay.create();
    console.log(`Session created with ID: ${session.sessionId}`);

    // Execute a command
    const result = await session.command.execute_command('ls -la');
    console.log('Command result:', result);

    // Read a file
    const content = await session.filesystem.read_file('/etc/hosts');
    console.log(`File content: ${content}`);

    // Execute an ADB shell command (for mobile environments)
    const adbResult = await session.adb.shell('ls /sdcard');
    console.log(`ADB shell result: ${adbResult}`);

    // Delete the session
    await agentBay.delete(session.sessionId);
    console.log('Session deleted successfully');
  } catch (error) {
    console.error('Error:', error);
  }
}

main();
```

#### Golang

```go
package main

import (
	"fmt"
	"os"

	"github.com/aliyun/wuying-agentbay-sdk/golang/pkg/agentbay"
)

func main() {
	// Initialize the AgentBay client
	apiKey := "your_api_key_here"
	client, err := agentbay.NewAgentBay(apiKey)
	if err != nil {
		fmt.Printf("Error initializing AgentBay client: %v\n", err)
		os.Exit(1)
	}

	// Create a new session
	session, err := client.Create()
	if err != nil {
		fmt.Printf("Error creating session: %v\n", err)
		os.Exit(1)
	}
	fmt.Printf("Session created with ID: %s\n", session.SessionID)

    // Execute a command
    result, err := session.Command.ExecuteCommand("ls -la")
    if err != nil {
        fmt.Printf("Error executing command: %v\n", err)
        os.Exit(1)
    }
    fmt.Printf("Command result: %v\n", result)

    // Read a file
    content, err := session.FileSystem.ReadFile("/etc/hosts")
    if err != nil {
        fmt.Printf("Error reading file: %v\n", err)
        os.Exit(1)
    }
    fmt.Printf("File content: %s\n", content)

    // Execute an ADB shell command (for mobile environments)
    adbResult, err := session.Adb.Shell("ls /sdcard")
    if err != nil {
        fmt.Printf("Error executing ADB shell command: %v\n", err)
        os.Exit(1)
    }
    fmt.Printf("ADB shell result: %s\n", adbResult)

	// Delete the session
	err = client.Delete(session)
	if err != nil {
		fmt.Printf("Error deleting session: %v\n", err)
		os.Exit(1)
	}
	fmt.Println("Session deleted successfully")
}
```


## Error Handling

The AgentBay SDK provides consistent error handling across all supported languages.

### Python

In Python, the SDK raises exceptions from the `agentbay.exceptions` module:

```python
from wuying_agentbay import AgentBay
from wuying_agentbay.exceptions import AuthenticationError, APIError

try:
    agent_bay = AgentBay(api_key="invalid_key")
    session = agent_bay.create()
except AuthenticationError as e:
    print(f"Authentication error: {e}")
except APIError as e:
    print(f"API error: {e}")
```

### TypeScript

In TypeScript, the SDK throws exceptions from the `exceptions` module:

```typescript
import { AgentBay } from 'wuying-agentbay-sdk';
import { AuthenticationError, APIError } from 'wuying-agentbay-sdk/exceptions';

try {
  const agentBay = new AgentBay({ apiKey: 'invalid_key' });
  const session = await agentBay.create();
} catch (error) {
  if (error instanceof AuthenticationError) {
    console.error(`Authentication error: ${error.message}`);
  } else if (error instanceof APIError) {
    console.error(`API error: ${error.message}`);
  } else {
    console.error(`Unexpected error: ${error}`);
  }
}
```

### Golang

In Golang, the SDK returns errors that can be checked and handled:

```go
client, err := agentbay.NewAgentBay("invalid_key")
if err != nil {
    if errors.Is(err, agentbay.ErrAuthentication) {
        fmt.Printf("Authentication error: %v\n", err)
    } else {
        fmt.Printf("Error initializing AgentBay client: %v\n", err)
    }
    return
}

session, err := client.Create()
if err != nil {
    fmt.Printf("Error creating session: %v\n", err)
    return
}
```

## Best Practices

### Session Management

1. **Create sessions as needed**: Sessions consume resources in the cloud environment, so create them only when needed and delete them when you're done.

2. **Reuse sessions**: If you need to perform multiple operations, reuse the same session instead of creating a new one for each operation.

3. **Handle session cleanup**: Always delete sessions when you're done with them to free up resources.

```python
# Python example of proper session cleanup
try:
    session = agent_bay.create()
    # Use the session...
finally:
    # Clean up the session even if an error occurs
    if 'session' in locals():
        try:
            session.delete()
        except:
            pass
```

### Error Handling

1. **Always check for errors**: All SDK operations can fail, so always check for and handle errors appropriately.

2. **Implement retries for transient errors**: Some errors may be transient (e.g., network issues). Implement retries with exponential backoff for these cases.

```python
# Python example of retry logic
import time
from wuying_agentbay.exceptions import APIError

max_retries = 3
retry_delay = 1  # seconds

for attempt in range(max_retries):
    try:
        result = session.command.execute_command("some_command")
        break  # Success, exit the retry loop
    except APIError as e:
        if attempt < max_retries - 1:
            # Wait before retrying, with exponential backoff
            time.sleep(retry_delay * (2 ** attempt))
            continue
        else:
            # Max retries reached, re-raise the exception
            raise
```

### Performance Optimization

1. **Optimize API calls**: Minimize the number of API calls to reduce latency and improve performance.

### Security

1. **Protect your API key**: Never hardcode your API key in your application. Use environment variables or a secure configuration system.

2. **Validate user input**: If your application accepts user input that is passed to the SDK, validate it to prevent injection attacks.

3. **Limit session permissions**: When creating sessions, specify only the permissions that are needed for your application.
