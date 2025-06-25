# Code Execution

Code execution is a powerful feature of the Wuying AgentBay SDK that allows you to run code snippets in various programming languages within the cloud environment.

## Overview

The Code Execution feature enables you to execute code snippets in supported programming languages directly within your AgentBay session. This is useful for performing complex operations, data processing, or automating tasks that would be difficult to achieve with simple shell commands.

## Supported Languages

Currently, the Code Execution feature supports the following programming languages:

- **Python**: Execute Python code with full standard library support
- **JavaScript**: Execute JavaScript code with Node.js runtime

## Code Execution Methods

The Code Execution functionality is provided through the Command interface:

### Python

```python
run_code(code: str, language: str, timeout_s: int = 300) -> str
```

### TypeScript

```typescript
runCode(code: string, language: string, timeoutS: number = 300): Promise<string>
```

### Golang

```go
RunCode(code string, language string, timeoutS ...int) (string, error)
```

## Parameters

- **code**: The code snippet to execute
- **language**: The programming language of the code (must be either "python" or "javascript")
- **timeout_s**: The timeout for the code execution in seconds (default is 300 seconds)

## Return Value

All methods return the output of the code execution as a string. This includes both stdout and stderr output.

## Usage Examples

### Python Example

```python
# Create a session
session = agent_bay.create()

# Execute Python code
python_code = """
import os
import platform

print(f"Current working directory: {os.getcwd()}")
print(f"Python version: {platform.python_version()}")
print(f"Platform info: {platform.platform()}")
"""

result = session.command.run_code(python_code, "python")
print(f"Python code execution result: {result}")
```

### TypeScript Example

```typescript
// Create a session
const session = await agentBay.create();

// Execute JavaScript code
const jsCode = `
const os = require('os');

console.log(\`Hostname: \${os.hostname()}\`);
console.log(\`Platform: \${os.platform()}\`);
console.log(\`CPU architecture: \${os.arch()}\`);
console.log(\`Total memory: \${os.totalmem() / 1024 / 1024} MB\`);
`;

const result = await session.command.runCode(jsCode, 'javascript');
console.log(`JavaScript code execution result: ${result}`);
```

### Golang Example

```go
// Create a session
session, err := client.Create(nil)
if err != nil {
    // Handle error
}

// Execute Python code
pythonCode := `
import json
import socket

data = {
    "hostname": socket.gethostname(),
    "ip_addresses": socket.gethostbyname_ex(socket.gethostname())[2]
}
print(json.dumps(data, indent=2))
`

result, err := session.Command.RunCode(pythonCode, "python")
if err != nil {
    // Handle error
}
fmt.Printf("Python code execution result: %s\n", result)
```

## Best Practices

1. **Keep code snippets focused**: Execute small, focused code snippets rather than large programs.

2. **Handle timeouts**: Set appropriate timeout values for long-running code executions to prevent resource wastage.

3. **Error handling**: Always handle potential errors in code execution, as the code might fail due to syntax errors, runtime errors, or timeout issues.

4. **Security considerations**: Avoid executing untrusted code, as it could potentially harm the cloud environment or expose sensitive data.

5. **Resource management**: Be mindful of resource usage in your code snippets, especially when dealing with memory-intensive operations.

## Limitations

1. **Supported languages**: Currently, only Python and JavaScript are supported.

2. **Execution environment**: The code is executed in a sandboxed environment with limited access to system resources.

3. **Persistence**: Variables and state are not preserved between different code execution calls.

4. **Package availability**: While standard libraries are available, third-party packages might not be pre-installed.

## Related Resources

- [Command Class](../api-reference/command.md): The complete API reference for the Command class, including code execution methods.
- [Sessions](sessions.md): Understanding sessions in the AgentBay cloud environment. 