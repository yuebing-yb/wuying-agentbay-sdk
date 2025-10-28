# CodeSpace Examples

This directory contains examples demonstrating code execution capabilities in AgentBay SDK.

## Overview

CodeSpace environment (`code_latest` image) provides a cloud-based development environment where you can:
- Execute Python and JavaScript code
- Perform file operations
- Run shell commands
- Manage packages (pip, npm)

## Examples

### code_execution_example.py

Comprehensive example demonstrating:
- **Python Code Execution**: Run Python scripts with full standard library access
- **JavaScript Code Execution**: Execute Node.js code with npm packages
- **File Operations**: Read, write, and manage files in the code environment
- **Command Execution**: Run shell commands for system operations

## Prerequisites

- Python 3.8 or later
- Valid `AGENTBAY_API_KEY` environment variable
- AgentBay SDK installed

## Installation

```bash
pip install wuying-agentbay-sdk
```

## Usage

```bash
# Set your API key
export AGENTBAY_API_KEY=your_api_key_here

# Run the example
python code_execution_example.py
```

## Features Demonstrated

### Python Code Execution

```python
python_code = """
import sys
print(f"Python version: {sys.version}")
"""

result = session.code.run_code(python_code, "python")
if result.success:
    print(result.result)
```

### JavaScript Code Execution

```python
js_code = """
const os = require('os');
console.log(`Platform: ${os.platform()}`);
"""

result = session.code.run_code(js_code, "javascript")
if result.success:
    print(result.result)
```

### File Operations

```python
# Write file
session.file_system.write_file("/tmp/test.txt", "Hello World")

# Read file
result = session.file_system.read_file("/tmp/test.txt")
print(result.content)
```

### Command Execution

```python
# Execute shell command
result = session.command.execute_command("python --version")
if result.success:
    print(result.output)
```

## Use Cases

1. **Automated Testing**: Run test suites in isolated environments
2. **Code Validation**: Validate code snippets before deployment
3. **Data Processing**: Execute data transformation scripts
4. **CI/CD Integration**: Integrate with continuous integration pipelines
5. **Educational Tools**: Provide safe code execution environments for learning

## API Methods Used

| Method | Purpose |
|--------|---------|
| `session.code.run_code()` | Execute Python or JavaScript code |
| `session.file_system.write_file()` | Write content to a file |
| `session.file_system.read_file()` | Read content from a file |
| `session.command.execute_command()` | Execute shell commands |

## Best Practices

1. **Error Handling**: Always check `result.success` before using output
2. **Resource Cleanup**: Delete sessions when done to free resources
3. **Timeout Management**: Set appropriate timeouts for long-running code
4. **Security**: Never execute untrusted code without proper validation
5. **Package Management**: Install required packages before code execution

## Related Documentation

- [Code Execution Guide](../../../../docs/guides/codespace/code-execution.md)
- [Session Management](../../../../docs/guides/common-features/basics/session-management.md)
- [File Operations](../../../../docs/guides/common-features/basics/file-operations.md)

## Troubleshooting

### Code Execution Timeout

If your code takes too long to execute, consider:
- Breaking it into smaller chunks
- Increasing timeout settings
- Using asynchronous execution patterns

### Package Not Found

If you need additional packages:
```python
# Install Python package
session.command.execute_command("pip install package-name")

# Install Node.js package
session.command.execute_command("npm install package-name")
```

### Permission Denied

Ensure you're writing to accessible directories like `/tmp` or user home directory.

