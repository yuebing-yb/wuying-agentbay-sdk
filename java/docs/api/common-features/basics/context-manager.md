# 🗂️ Context-manager API Reference

## Overview

The Context-manager module provides specialized functionality for the AgentBay cloud platform. It includes various methods and utilities to interact with cloud services and manage resources.

## 📚 Tutorial

[Data Persistence Guide](../../../../../docs/guides/common-features/basics/data-persistence.md)

Learn about context management and data persistence

## ContextManager

### Constructor

```java
public ContextManager(Session session)
```

### Methods

### info

```java
public ContextInfoResult info()
```

```java
public ContextInfoResult info(String contextId, String path, String taskType)
```

Get context info with optional filters

**Parameters:**
- `contextId` (String): Context ID filter (optional)
- `path` (String): Path filter (optional)
- `taskType` (String): Task type filter (optional)

**Returns:**
- `ContextInfoResult`: ContextInfoResult containing status data

### sync

```java
public ContextSyncResult sync()
```

```java
public ContextSyncResult sync(String contextId, String path, String mode)
```

```java
public ContextSyncResult sync(Consumer<Boolean> callback)
```

```java
public ContextSyncResult sync(String contextId, String path, String mode, Consumer<Boolean> callback)
```

```java
public ContextSyncResult sync(String contextId, String path, String mode, Consumer<Boolean> callback, int maxRetries, int retryInterval)
```

Sync context data with optional parameters and callback mode (non-blocking)
Returns immediately and calls the callback when sync completes

**Parameters:**
- `contextId` (String): Context ID (optional)
- `path` (String): Path (optional)
- `mode` (String): Sync mode (optional)
- `callback` (Consumer<Boolean>): Callback function that receives success status (true if successful, false otherwise)
- `maxRetries` (int): Maximum number of retries for polling completion status (default: 150)
- `retryInterval` (int): Milliseconds to wait between retries (default: 2000)

**Returns:**
- `ContextSyncResult`: ContextSyncResult indicating initial sync trigger success/failure

### syncAndWait

```java
public ContextSyncResult syncAndWait()
```

```java
public ContextSyncResult syncAndWait(String contextId, String path, String mode)
```

```java
public ContextSyncResult syncAndWait(String contextId, String path, String mode, int maxRetries, int retryInterval)
```

Sync context data with optional parameters and wait for completion

**Parameters:**
- `contextId` (String): Context ID (optional)
- `path` (String): Path (optional)
- `mode` (String): Sync mode (optional)
- `maxRetries` (int): Maximum number of retries for polling completion status (default: 150)
- `retryInterval` (int): Milliseconds to wait between retries (default: 2000)

**Returns:**
- `ContextSyncResult`: ContextSyncResult indicating success/failure after waiting for completion



## 🔗 Related Resources

- [Context API Reference](/Users/liyuebing/Projects/wuying-agentbay-sdk/java/docs/api/common-features/basics/context.md)
- [Session API Reference](/Users/liyuebing/Projects/wuying-agentbay-sdk/java/docs/api/common-features/basics/session.md)

