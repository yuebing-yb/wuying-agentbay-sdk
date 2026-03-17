# 💻 Code API Reference

## Overview

The Code module provides secure code execution capabilities in isolated environments.
It supports multiple programming languages including Python, JavaScript, and more.


## 📚 Tutorial

[Code Execution Guide](../../../../docs/guides/codespace/code-execution.md)

Execute code in isolated environments

## 📋 Requirements

- Requires `code_latest` image for code execution features

## Code

Handles code execution operations in the AgentBay cloud environment.

<p>This service provides methods to execute code in various programming languages
(Python, JavaScript, R, Java) within a cloud-based code execution environment.
It supports both synchronous and WebSocket-based streaming execution modes.</p>

### Constructor

```java
public Code(Session session)
```

Creates a new Code service instance bound to the given session.

**Parameters:**
- `session` (Session): The session to bind this code execution service to.

### Methods

### runCode

```java
public EnhancedCodeExecutionResult runCode(String code, String language, int timeoutS)
```

```java
public EnhancedCodeExecutionResult runCode(String code, String language, int timeoutS, boolean streamBeta, Consumer<String> onStdout, Consumer<String> onStderr, Consumer<Object> onError)
```

```java
public EnhancedCodeExecutionResult runCode(String code, String language)
```

Execute code with optional WebSocket streaming for real-time stdout/stderr output.

**Parameters:**
- `code` (String): The code to execute.
- `language` (String): The programming language of the code. Case-insensitive.
- `timeoutS` (int): The timeout for the code execution in seconds.
- `streamBeta` (boolean): If true, use WebSocket streaming for real-time output.
- `onStdout` (Consumer<String>): Callback invoked for each stdout chunk. May be null.
- `onStderr` (Consumer<String>): Callback invoked for each stderr chunk. May be null.
- `onError` (Consumer<Object>): Callback invoked when an error occurs. May be null.

**Returns:**
- `EnhancedCodeExecutionResult`: EnhancedCodeExecutionResult containing success status, execution result, and logs.

### execute

```java
public EnhancedCodeExecutionResult execute(String code, String language)
```

```java
public EnhancedCodeExecutionResult execute(String code)
```

Alias of runCode with a default timeout of 60 seconds.

**Parameters:**
- `code` (String): The code to execute.
- `language` (String): The programming language of the code.

**Returns:**
- `EnhancedCodeExecutionResult`: EnhancedCodeExecutionResult containing success status and execution result.

### run

```java
public EnhancedCodeExecutionResult run(String code, String language, int timeoutS)
```

```java
public EnhancedCodeExecutionResult run(String code, String language)
```

Alias of runCode for better ergonomics and LLM friendliness.

**Parameters:**
- `code` (String): The code to execute.
- `language` (String): The programming language of the code.
- `timeoutS` (int): The timeout for the code execution in seconds.

**Returns:**
- `EnhancedCodeExecutionResult`: EnhancedCodeExecutionResult containing success status and execution result.



## 💡 Best Practices

- Validate code syntax before execution
- Set appropriate execution timeouts
- Handle execution errors and exceptions
- Use proper resource limits to prevent resource exhaustion
- Clean up temporary files after code execution

## 🔗 Related Resources

- [Session API Reference](../../api/common-features/basics/session.md)

