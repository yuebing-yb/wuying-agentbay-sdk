# ⚡ Command API Reference

## Overview

The Command module provides methods for executing shell commands within a session in the AgentBay cloud environment.
Commands support configurable timeouts and optional working directory or environment settings.


## 📚 Tutorial

[Command Execution Guide](../../../../../docs/guides/common-features/basics/command-execution.md)

Learn how to execute commands in sessions

## Command

Async command execution service for session shells in the AgentBay cloud environment.

<p>Use this class for non-blocking command execution; for blocking/synchronous usage,
refer to the Command service in the sync API.

### Constructor

```java
public Command(Session session)
```

### Methods

### execute

```java
public CommandResult execute(String command)
```

```java
public CommandResult execute(String command, String input)
```

Execute a shell command with default timeout (50000ms).
Note: The input parameter is currently not used in the implementation.

**Parameters:**
- `command` (String): The shell command to execute
- `input` (String): Input parameter (currently unused)

**Returns:**
- `CommandResult`: CommandResult Result object containing execution details

### executeCommand

```java
public CommandResult executeCommand(String command, int timeoutMs)
```

```java
public CommandResult executeCommand(String command, int timeoutMs, String cwd, Map<String, String> envs)
```

Execute a shell command with optional working directory and environment variables.

<p>Executes a shell command in the session environment with configurable timeout,
working directory, and environment variables. The command runs with session
user permissions in a Linux shell environment.

**Parameters:**
- `command` (String): The shell command to execute
- `timeoutMs` (int): Timeout in milliseconds (default: 50000ms/50s). Maximum allowed
                 timeout is 50000ms (50s). If a larger value is provided, it will be
                 automatically limited to 50000ms
- `cwd` (String): The working directory for command execution. If not specified,
           the command runs in the default session directory
- `envs` (Map<String,String>): Environment variables as a map of key-value pairs.
            These variables are set for the command execution only

**Returns:**
- `CommandResult`: CommandResult Result object containing:
        <ul>
          <li>success: Whether the command executed successfully (exit_code == 0)</li>
          <li>output: Command output for backward compatibility (stdout + stderr)</li>
          <li>exitCode: The exit code of the command execution (0 for success)</li>
          <li>stdout: Standard output from the command execution</li>
          <li>stderr: Standard error from the command execution</li>
          <li>traceId: Trace ID for error tracking (only present when exit_code != 0)</li>
          <li>requestId: Unique identifier for this API request</li>
          <li>errorMessage: Error description if execution failed</li>
        </ul>

**Throws:**
- `IllegalArgumentException`: If environment variables contain non-string keys or values

### run

```java
public CommandResult run(String command, int timeoutMs)
```

```java
public CommandResult run(String command, int timeoutMs, String cwd, Map<String, String> envs)
```

Alias of executeCommand() for better ergonomics and LLM friendliness.

**Parameters:**
- `command` (String): The shell command to execute
- `timeoutMs` (int): Timeout in milliseconds
- `cwd` (String): The working directory for command execution
- `envs` (Map<String,String>): Environment variables as a map of key-value pairs

**Returns:**
- `CommandResult`: CommandResult Result object containing execution details

### exec

```java
public CommandResult exec(String command, int timeoutMs)
```

```java
public CommandResult exec(String command, int timeoutMs, String cwd, Map<String, String> envs)
```

Alias of executeCommand() for better ergonomics and LLM friendliness.

**Parameters:**
- `command` (String): The shell command to execute
- `timeoutMs` (int): Timeout in milliseconds
- `cwd` (String): The working directory for command execution
- `envs` (Map<String,String>): Environment variables as a map of key-value pairs

**Returns:**
- `CommandResult`: CommandResult Result object containing execution details



## 💡 Best Practices

- Always specify appropriate timeout values based on expected command duration
- Handle command execution errors gracefully
- Use absolute paths when referencing files in commands
- Be aware that commands run with session user permissions
- Clean up temporary files created by commands

## 🔗 Related Resources

- [Session API Reference](../../../api/common-features/basics/session.md)
- [FileSystem API Reference](../../../api/common-features/basics/filesystem.md)

