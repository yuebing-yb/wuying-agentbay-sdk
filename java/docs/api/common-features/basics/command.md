# ⚡ Command API Reference

## Overview

The Command module provides methods for executing shell commands within a session in the AgentBay cloud environment.
Commands support configurable timeouts and optional working directory or environment settings.


## 📚 Tutorial

[Command Execution Guide](../../../../../docs/guides/common-features/basics/command-execution.md)

Learn how to execute commands in sessions

## Command

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

### executeCommand

```java
public CommandResult executeCommand(String command, int timeoutMs)
```

```java
public CommandResult executeCommand(String command, int timeoutMs, String cwd, Map<String, String> envs)
```

### run

```java
public CommandResult run(String command, int timeoutMs)
```

```java
public CommandResult run(String command, int timeoutMs, String cwd, Map<String, String> envs)
```

### exec

```java
public CommandResult exec(String command, int timeoutMs)
```

```java
public CommandResult exec(String command, int timeoutMs, String cwd, Map<String, String> envs)
```



## 💡 Best Practices

- Always specify appropriate timeout values based on expected command duration
- Handle command execution errors gracefully
- Use absolute paths when referencing files in commands
- Be aware that commands run with session user permissions
- Clean up temporary files created by commands

## 🔗 Related Resources

- [Session API Reference](/Users/liyuebing/Projects/wuying-agentbay-sdk/java/docs/api/common-features/basics/session.md)
- [FileSystem API Reference](/Users/liyuebing/Projects/wuying-agentbay-sdk/java/docs/api/common-features/basics/filesystem.md)

