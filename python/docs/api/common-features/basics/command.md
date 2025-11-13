# Command API Reference

## ⚡ Related Tutorial

- [Command Execution Guide](../../../../../docs/guides/common-features/basics/command-execution.md) - Learn how to execute commands in sessions

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
def execute_command(command: str, timeout_ms: int = 1000) -> CommandResult
```

Execute a shell command in the cloud environment with a specified timeout.

**Arguments**:

- `command` _str_ - The shell command to execute.
- `timeout_ms` _int, optional_ - The timeout for the command execution in milliseconds.
  Defaults to 1000 (1 second).
  

**Returns**:

    CommandResult: Result object containing success status, command output, and error message if any.
  - success (bool): True if the operation succeeded
  - output (str): The command output (stdout and stderr combined)
  - request_id (str): Unique identifier for this API request
  - error_message (str): Error description (if success is False)
  

**Raises**:

    CommandError: If the command execution fails.
  

**Example**:

```python
session = agent_bay.create().session
cmd_result = session.command.execute_command("echo 'Hello, World!'")
print(cmd_result.output)
cmd_result = session.command.execute_command("sleep 2 && echo 'Done'", timeout_ms=5000)
session.delete()
```


**Notes**:

- Commands are executed in a Linux shell environment
- Default timeout is 1 second (1000ms)
- Output includes both stdout and stderr
- Long-running commands may timeout if timeout_ms is too small


**See Also**:

Command.execute_command_async

## Best Practices

1. Always specify appropriate timeout values based on expected command duration
2. Handle command execution errors gracefully
3. Use absolute paths when referencing files in commands
4. Be aware that commands run with session user permissions
5. Clean up temporary files created by commands

## Related Resources

- [Session API Reference](session.md)
- [FileSystem API Reference](filesystem.md)

---

*Documentation generated automatically from source code using pydoc-markdown.*
