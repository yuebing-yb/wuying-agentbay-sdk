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

### Constructor

```java
public Code(Session session)
```

### Methods

### runCode

```java
public EnhancedCodeExecutionResult runCode(String code, String language, int timeoutS)
```

```java
public EnhancedCodeExecutionResult runCode(String code, String language)
```

### execute

```java
public EnhancedCodeExecutionResult execute(String code, String language)
```

```java
public EnhancedCodeExecutionResult execute(String code)
```

### run

```java
public EnhancedCodeExecutionResult run(String code, String language, int timeoutS)
```

```java
public EnhancedCodeExecutionResult run(String code, String language)
```



## 💡 Best Practices

- Validate code syntax before execution
- Set appropriate execution timeouts
- Handle execution errors and exceptions
- Use proper resource limits to prevent resource exhaustion
- Clean up temporary files after code execution

## 🔗 Related Resources

- [Session API Reference](../../api/common-features/basics/session.md)

