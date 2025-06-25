# Command Execution Example

This example demonstrates how to use the AgentBay SDK to execute commands and run code in different languages within a session.

## Features Demonstrated

- Executing shell commands:
  - Simple echo command
  - Command with custom timeout
  - Complex multi-line command sequence

- Running code in different languages:
  - Python code execution
  - JavaScript code execution with custom timeout

## Running the Example

Make sure you have set your AgentBay API key as an environment variable:

```bash
export AGENTBAY_API_KEY="your-api-key-here"
```

Then run the example:

```bash
npx ts-node command-example.ts
```

## Note

This example requires a session with the `code_latest` image to support code execution in different programming languages. The example demonstrates error handling to deal with cases where certain operations might not be supported. 

## Code Execution Details

The `runCode` method supports executing code in the following languages:

- **Python**: Full Python environment with standard libraries
- **JavaScript**: Node.js environment with standard modules

The method accepts the following parameters:

```typescript
runCode(code: string, language: string, timeoutS?: number): Promise<string>
```

- `code`: The code snippet to execute
- `language`: Either "python" or "javascript"
- `timeoutS`: Optional timeout in seconds (defaults to 300 seconds)

The method returns the output of the code execution as a string, including both stdout and stderr output. 