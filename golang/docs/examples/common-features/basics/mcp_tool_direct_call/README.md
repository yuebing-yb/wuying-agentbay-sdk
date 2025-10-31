# MCP Tool Direct Call Example (Golang)

This example demonstrates how to list available MCP tools and call them using the AgentBay Golang SDK.

## Prerequisites

- Go 1.19 or higher
- AgentBay API Key (set as environment variable `AGENTBAY_API_KEY`)

## Running the Example

```bash
# Set your API key
export AGENTBAY_API_KEY=your_api_key_here

# Run the example
cd golang/docs/examples/mcp_tool_list_and_call
go run main.go
```

## What This Example Does

1. **Creates a Session**: Initializes an AgentBay session
2. **Lists MCP Tools**: Retrieves all available MCP tools
3. **Finds Shell Tool**: Locates the 'shell' tool and displays its details
4. **Calls Shell Tool**: Executes a simple echo command
5. **Demonstrates Flexibility**: Runs another command (pwd)
6. **Error Handling**: Shows how errors are handled
7. **Cleanup**: Properly deletes the session

## Expected Output

```
Initializing AgentBay client...

1. Creating session...
✓ Session created successfully
  Session ID: sess-xxxxx
  Request ID: req-xxxxx

2. Listing available MCP tools...
✓ Found XX MCP tools
  Request ID: req-xxxxx

  Available tools (showing first 10):
  1. shell
     Description: Execute shell commands
     Server: system
     Required params: command

  ...

3. Finding 'shell' tool details...
✓ Found 'shell' tool
  Description: Execute shell commands
  Server: system
  Input Schema:
    {
      "type": "object",
      "properties": {
        "command": {
          "type": "string"
        },
        "timeout_ms": {
          "type": "integer"
        }
      },
      "required": ["command"]
    }

4. Calling 'shell' tool...
✓ Tool call successful
  Request ID: req-xxxxx
  Output:
    Hello from MCP Tool!

5. Calling 'shell' tool with different command...
✓ Tool call successful
  Request ID: req-xxxxx
  Current directory:
    /home/user

6. Demonstrating error handling (invalid command)...
✓ Error handled correctly
  Request ID: req-xxxxx
  Error message: command not found...

7. Cleaning up...
✓ Session deleted successfully
  Request ID: req-xxxxx

============================================================
Example completed successfully!
============================================================
```

## Key Points

- The `CallMcpTool` method is the unified API for calling any MCP tool
- Tool discovery is done via `ListMcpTools`
- Both VPC and non-VPC modes are supported automatically
- Proper error handling and cleanup are demonstrated

