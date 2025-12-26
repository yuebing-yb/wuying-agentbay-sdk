# Command API Reference

## ⚡ Related Tutorial

- [Command Execution Guide](../../../../../docs/guides/common-features/basics/command-execution.md) - Learn how to execute commands in sessions

## Overview

The Command module provides methods for executing shell commands within a session in the AgentBay cloud environment. It supports synchronous command execution with configurable timeouts.

## CommandResult

```java
public class CommandResult extends ApiResponse
```

Result of command execution operations.

**Fields:**
- `success` (boolean): True if the operation succeeded
- `output` (String): The command output (stdout and stderr combined)  
- `requestId` (String): Unique identifier for this API request
- `errorMessage` (String): Error description (if success is false)
- `exitCode` (int): Command exit code

## Command

```java
public class Command extends BaseService
```

Handles command execution operations in the AgentBay cloud environment.

### executeCommand

```java
public CommandResult executeCommand(String command, int timeoutMs)
```

Execute a shell command in the cloud environment with a specified timeout.

**Parameters:**
- `command` (String): The shell command to execute
- `timeoutMs` (int): The timeout for the command execution in milliseconds. Defaults to 1000 (1 second).

**Returns:**
- `CommandResult`: Result object containing success status, command output, and error message if any.
  - `success` (boolean): True if the operation succeeded
  - `output` (String): The command output (stdout and stderr combined)
  - `requestId` (String): Unique identifier for this API request
  - `errorMessage` (String): Error description (if success is false)
  - `exitCode` (int): Command exit code

**Throws:**
- No checked exceptions (errors are returned in CommandResult)

**Example:**

```java
Session session = agentBay.create().getSession();
CommandResult result = session.getCommand().executeCommand("echo 'Hello, World!'", 1000);
System.out.println(result.getOutput());

// Long-running command with increased timeout
CommandResult longResult = session.getCommand().executeCommand("sleep 2 && echo 'Done'", 5000);
session.delete();
```

### executeCommand (with cwd and envs)

```java
public CommandResult executeCommand(String command, int timeoutMs, String cwd, Map<String, String> envs)
```

Execute a shell command with optional working directory and environment variables.

Executes a shell command in the session environment with configurable timeout, working directory, and environment variables. The command runs with session user permissions in a Linux shell environment.

**Parameters:**
- `command` (String): The shell command to execute
- `timeoutMs` (int): The timeout for the command execution in milliseconds. Defaults to 1000 (1 second).
- `cwd` (String): The working directory for command execution. If null, the command runs in the default session directory
- `envs` (Map<String, String>): Environment variables as a map of key-value pairs. These variables are set for the command execution only. If null, no additional environment variables are set.

**Returns:**
- `CommandResult`: Result object containing success status, command output, and error message if any.
  - `success` (boolean): True if the operation succeeded
  - `output` (String): The command output (stdout and stderr combined)
  - `requestId` (String): Unique identifier for this API request
  - `errorMessage` (String): Error description (if success is false)
  - `exitCode` (int): Command exit code

**Throws:**
- `IllegalArgumentException`: If environment variables contain non-string keys or values

**Example:**

```java
Session session = agentBay.create().getSession();

// Execute command with working directory
CommandResult result = session.getCommand().executeCommand("pwd", 5000, "/tmp", null);
System.out.println(result.getOutput());

// Execute command with environment variables
Map<String, String> envs = new HashMap<>();
envs.put("TEST_VAR", "test_value");
CommandResult result2 = session.getCommand().executeCommand("echo $TEST_VAR", 5000, null, envs);
System.out.println(result2.getOutput());

// Execute command with both cwd and envs
Map<String, String> envs2 = new HashMap<>();
envs2.put("CUSTOM_VAR", "custom_value");
CommandResult result3 = session.getCommand().executeCommand(
    "pwd && echo $CUSTOM_VAR",
    5000,
    "/tmp",
    envs2
);
System.out.println(result3.getOutput());

session.delete();
```

### execute

```java
public CommandResult execute(String command)
```

Execute a shell command with default timeout (1000ms).

**Parameters:**
- `command` (String): The shell command to execute

**Returns:**
- `CommandResult`: Result object containing execution results

**Example:**

```java
CommandResult result = session.getCommand().execute("ls -la");
if (result.isSuccess()) {
    System.out.println(result.getOutput());
}
```

## Best Practices

1. Always specify appropriate timeout values based on expected command duration
2. Handle command execution errors gracefully by checking `result.isSuccess()`
3. Use absolute paths when referencing files in commands
4. Be aware that commands run with session user permissions
5. Clean up temporary files created by commands
6. Check exit codes for command success/failure status
7. Use `cwd` parameter to set working directory instead of using `cd` in commands
8. Use `envs` parameter to pass environment variables securely instead of embedding them in command strings
9. All environment variable keys and values must be strings, otherwise `IllegalArgumentException` will be thrown

## Notes

- Commands are executed in a Linux shell environment
- Default timeout is 1 second (1000ms)
- Output includes both stdout and stderr
- Long-running commands may timeout if timeout_ms is too small
- Commands execute asynchronously on the server side

## Related Resources

- [Session API Reference](session.md)
- [FileSystem API Reference](filesystem.md)
- [Command Execution Example](../../../../agentbay/src/main/java/com/aliyun/agentbay/examples/FileSystemExample.java)

---

*Documentation for AgentBay Java SDK*

