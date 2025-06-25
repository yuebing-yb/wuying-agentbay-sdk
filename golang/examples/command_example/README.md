# Command Example

This example demonstrates how to use the AgentBay SDK's Command module to execute shell commands and run code in various languages in the cloud environment.

## Features Demonstrated

- Executing simple shell commands
- Setting custom timeouts for commands
- Running Python code
- Running JavaScript code
- Executing complex multi-line shell command sequences

## Prerequisites

- Go 1.16 or later
- AgentBay API key (set as `AGENTBAY_API_KEY` environment variable)

## Running the Example

1. Set your API key:
   ```bash
   export AGENTBAY_API_KEY="your-api-key-here"
   ```

2. Run the example:
   ```bash
   go run main.go
   ```

## Expected Output

The example will create a session, perform various command operations, and clean up afterwards. 
You should see output showing the results of each operation, including:

- Simple command execution output
- Directory listing results
- Python code execution results 
- JavaScript code execution results
- Complex shell command sequence results

## Notes

- This example requires a session created with the `code_latest` image to support code execution
- The `RunCode` method currently supports Python and JavaScript languages
- All results are processed to extract text content from the response
- Long outputs are truncated for readability
- The session is automatically deleted at the end of the example 