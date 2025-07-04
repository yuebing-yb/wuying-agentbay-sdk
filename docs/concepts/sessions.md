# Sessions

Sessions are one of the core concepts of the Wuying AgentBay SDK, representing an interaction instance with the Wuying AgentBay cloud runtime environment.

## Overview

A session is an isolated execution environment that allows you to execute commands, read files, and perform other operations. Each session has its own state and resources, which are released when the session ends.

## Session Lifecycle

1. **Creation**: Create a new session using the `Create` method of the AgentBay client.
2. **Usage**: Use the session to execute commands, read files, and perform other operations.
3. **Deletion**: When the session is no longer needed, delete it using the `Delete` method of the AgentBay client to release resources.

## Session Properties

Sessions have the following main properties:

- **Session ID**: A string that uniquely identifies the session.
- **FileSystem**: An instance that provides file operation functionality.
- **Command**: An instance that provides command execution functionality.
- **Application**: An instance that provides application management functionality.
- **Window**: An instance that provides window management functionality.
- **Labels**: Key-value pairs that can be used to categorize and filter sessions.

## Session Labels

Sessions can be labeled with key-value pairs to help organize and filter them. Labels are useful for categorizing sessions by purpose, environment, owner, or any other criteria.

### Setting Labels

You can set labels when creating a session or update them later:

#### Golang

```go
// Set labels when creating a session
params := agentbay.NewCreateSessionParams().WithLabels(map[string]string{
    "environment": "development",
    "owner": "team-a",
    "project": "project-x",
})
session, err := client.Create(params)

// Update labels for an existing session
labelsJSON := `{"environment": "staging", "owner": "team-a", "project": "project-x"}`
err = session.SetLabels(labelsJSON)
```

#### Python

```python
# Set labels when creating a session
params = {
    "labels": {
        "environment": "development",
        "owner": "team-a",
        "project": "project-x"
    }
}
session = agent_bay.create(params)

# Update labels for an existing session
session.set_labels({
    "environment": "staging",
    "owner": "team-a",
    "project": "project-x"
})
```

#### TypeScript

```typescript
// Set labels when creating a session
const params = {
  labels: {
    environment: "development",
    owner: "team-a",
    project: "project-x"
  }
};
const session = await agentBay.create(params);

// Update labels for an existing session
await session.setLabels({
  environment: "staging",
  owner: "team-a",
  project: "project-x"
});
```

### Getting Labels

You can retrieve the labels for a session:

#### Golang

```go
labelsJSON, err := session.GetLabels()
if err != nil {
    fmt.Printf("Error getting labels: %v\n", err)
    return
}
fmt.Printf("Session labels: %s\n", labelsJSON)
```

#### Python

```python
labels = session.get_labels()
print(f"Session labels: {labels}")
```

#### TypeScript

```typescript
const labels = await session.getLabels();
log("Session labels:", labels);
```

### Filtering Sessions by Labels

You can filter sessions by labels to find sessions that match specific criteria:

#### Golang

```go
// Find sessions with environment=development
params := agentbay.NewListSessionParams()
params.Labels = map[string]string{"environment": "development"}
result, err := client.ListByLabels(params)
if err != nil {
    fmt.Printf("Error listing sessions by labels: %v\n", err)
    return
}
fmt.Printf("Found %d sessions with environment=development (total: %d)\n", 
    len(result.Sessions), result.TotalCount)

// Find sessions with multiple labels
params = agentbay.NewListSessionParams()
params.Labels = map[string]string{
    "environment": "development",
    "owner": "team-a",
}
result, err = client.ListByLabels(params)
if err != nil {
    fmt.Printf("Error listing sessions by labels: %v\n", err)
    return
}
fmt.Printf("Found %d sessions with environment=development AND owner=team-a\n", 
    len(result.Sessions))

// Using pagination to handle large result sets
params = agentbay.NewListSessionParams()
params.Labels = map[string]string{"environment": "development"}
params.MaxResults = 5 // Limit to 5 results per page

// Get first page
firstPage, err := client.ListByLabels(params)
if err != nil {
    fmt.Printf("Error listing sessions by labels: %v\n", err)
    return
}
fmt.Printf("First page: Found %d sessions (total: %d)\n", 
    len(firstPage.Sessions), firstPage.TotalCount)

// If there are more pages, get the next page
if firstPage.NextToken != "" {
    params.NextToken = firstPage.NextToken
    secondPage, err := client.ListByLabels(params)
    if err != nil {
        fmt.Printf("Error listing second page: %v\n", err)
        return
    }
    fmt.Printf("Second page: Found %d more sessions\n", len(secondPage.Sessions))
}
```

#### Python

```python
# Find sessions with environment=development
sessions = agent_bay.list_by_labels({"environment": "development"})
print(f"Found {len(sessions)} sessions with environment=development")

# Find sessions with multiple labels
sessions = agent_bay.list_by_labels({
    "environment": "development",
    "owner": "team-a"
})
print(f"Found {len(sessions)} sessions with environment=development AND owner=team-a")
```

#### TypeScript

```typescript
// Find sessions with environment=development
const sessions = await agentBay.listByLabels({ environment: "development" });
log(`Found ${sessions.length} sessions with environment=development`);

// Find sessions with multiple labels
const sessions2 = await agentBay.listByLabels({
  environment: "development",
  owner: "team-a"
});
log(`Found ${sessions2.length} sessions with environment=development AND owner=team-a`);
```

## Usage Examples

### Golang

```go
// Create a session
session, err := client.Create(nil)
if err != nil {
    fmt.Printf("Error creating session: %v\n", err)
    os.Exit(1)
}
fmt.Printf("Session created with ID: %s\n", session.SessionID)

// Use the session to execute a command
result, err := session.Command.ExecuteCommand("ls -la")
if err != nil {
    fmt.Printf("Error executing command: %v\n", err)
    os.Exit(1)
}
fmt.Printf("Command result: %v\n", result)

// Delete the session
err = client.Delete(session)
if err != nil {
    fmt.Printf("Error deleting session: %v\n", err)
    os.Exit(1)
}
fmt.Println("Session deleted successfully")
```

### Python

```python
# Create a session
session = agent_bay.create()
print(f"Session created with ID: {session.session_id}")

# Use the session to execute a command
result = session.command.execute_command("ls -la")
print(f"Command result: {result}")

# Delete the session
agent_bay.delete(session)
print("Session deleted successfully")
```

### TypeScript

```typescript
// Create a session
const session = await agentBay.create();
log(`Session created with ID: ${session.sessionId}`);

// Use the session to execute a command
const result = await session.command.executeCommand('ls -la');
log('Command result:', result);

// Delete the session
await agentBay.delete(session);
log('Session deleted successfully');
```

## Related Resources

- [Contexts](contexts.md)
- [Applications](applications.md)
- [Session Creation Example](../../golang/examples/session_creation/README.md)
- [Session Parameters Example](../../golang/examples/session_params/README.md)
