# Command API Reference

> **💡 Async Version**: This documentation covers the synchronous API. For async/await support, see [`AsyncCommand`](../async/async-command.md) which provides the same functionality with async methods.

## ⚡ Related Tutorial

- [Command Execution Guide](../../../../docs/guides/common-features/basics/command-execution.md) - Learn how to execute commands in sessions

## Overview

The Command module provides methods for executing shell commands within a session in the AgentBay cloud environment.
It supports both synchronous command execution with configurable timeouts.




## CommandResult

```python
class CommandResult(ApiResponse)
```

Result of command execution operations.

## Command

```python
class Command(BaseService)
```

Handles command execution operations in the AgentBay cloud environment.

### execute\_command

```python
def execute_command(command: str, timeout_ms: int = 60000) -> CommandResult
```

Execute a shell command with a timeout.

**Arguments**:

    command: The shell command to execute.
    timeout_ms: The timeout for the command execution in milliseconds. Default is 60000ms (60s).
  

**Returns**:

    CommandResult: Result object containing success status, execution
  output, and error message if any.
  

**Raises**:

    CommandError: If the command execution fails.
  

**Example**:

```python
result = session.command.execute_command("ls -la")
print(result.output)
```

## Best Practices

1. Always specify appropriate timeout values based on expected command duration
2. Handle command execution errors gracefully
3. Use absolute paths when referencing files in commands
4. Be aware that commands run with session user permissions
5. Clean up temporary files created by commands

## See Also

- [Synchronous vs Asynchronous API](../../../../docs/guides/common-features/sync-vs-async.md)

**Related APIs:**
- [Session API Reference](./session.md)
- [FileSystem API Reference](./filesystem.md)

---

*Documentation generated automatically from source code using pydoc-markdown.*
