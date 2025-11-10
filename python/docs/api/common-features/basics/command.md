# Command API Reference

## ⚡ Related Tutorial

- [Command Execution Guide](../../../../../docs/guides/common-features/basics/command-execution.md) - Learn how to execute commands in sessions

## Overview

The Command module provides methods for executing shell commands within a session in the AgentBay cloud environment.
It supports both synchronous command execution with configurable timeouts.


## Requirements

- Any session image (browser_latest, code_latest, windows_latest, mobile_latest)



```python
class CommandResult(ApiResponse)
```

Result of command execution operations.

## Command Objects

```python
class Command(BaseService)
```

Handles command execution operations in the AgentBay cloud environment.

#### execute\_command

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
from agentbay import AgentBay

agent_bay = AgentBay(api_key="your_api_key")

def execute_commands():
    try:
        result = agent_bay.create()
        if result.success:
            session = result.session

            # Execute a simple command
            cmd_result = session.command.execute_command("echo 'Hello, World!'")
            if cmd_result.success:
                print(f"Command output: {cmd_result.output}")
                # Output: Command output: Hello, World!
                print(f"Request ID: {cmd_result.request_id}")
                # Output: Request ID: 9E3F4A5B-2C6D-7E8F-9A0B-1C2D3E4F5A6B

            # Execute a command with custom timeout (5 seconds)
            cmd_result = session.command.execute_command("sleep 2 && echo 'Done'", timeout_ms=5000)
            if cmd_result.success:
                print(f"Command output: {cmd_result.output}")
                # Output: Command output: Done

            # Execute a command that lists files
            cmd_result = session.command.execute_command("ls -la /tmp")
            if cmd_result.success:
                print(f"Directory listing:
{cmd_result.output}")

            # Handle command timeout
            cmd_result = session.command.execute_command("sleep 10", timeout_ms=1000)
            if not cmd_result.success:
                print(f"Error: {cmd_result.error_message}")
                # Output: Error: Command execution timed out

            # Clean up
            session.delete()
    except Exception as e:
        print(f"Error: {e}")

execute_commands()
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
