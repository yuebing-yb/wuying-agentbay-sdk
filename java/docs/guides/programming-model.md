# Java SDK Programming Model

This guide explains the programming model and patterns used in the AgentBay Java SDK.

## 📖 Overview

The AgentBay Java SDK provides a **synchronous**, **blocking** API model that is simple and intuitive for Java developers. Unlike the Python SDK which offers both sync and async variants, the Java SDK focuses on a single, straightforward programming model.

## 🔄 Synchronous vs Asynchronous

### Java SDK: Synchronous Only

The Java SDK uses a **synchronous, blocking** programming model:

```java
AgentBay agentBay = new AgentBay();

// All operations block until complete
SessionResult result = agentBay.create();
Session session = result.getSession();

// Execute command (blocks until complete)
CommandResult cmdResult = session.getCommand().executeCommand("ls -la");
System.out.println(cmdResult.getOutput());

// File operations (block until complete)
session.getFileSystem().writeFile("/tmp/test.txt", "content");
String content = session.getFileSystem().readFile("/tmp/test.txt");
```

### Why Synchronous?

**Advantages:**
- ✅ **Simpler to use** - No async/await syntax required
- ✅ **Easier to debug** - Linear execution flow
- ✅ **Better for scripts** - Most automation scripts are sequential
- ✅ **Exception handling** - Standard try-catch blocks
- ✅ **Thread-safe** - Each session is independent

**When to use:**
- 📝 Automation scripts
- 🧪 Test automation
- 🔧 DevOps tools
- 📊 Data processing pipelines
- 🤖 Sequential workflows

## 🚀 Concurrent Operations

For concurrent operations, use Java's standard concurrency utilities:

### Using CompletableFuture

```java
import java.util.concurrent.CompletableFuture;
import java.util.List;
import java.util.stream.Collectors;

AgentBay agentBay = new AgentBay();

// Create multiple sessions concurrently
List<CompletableFuture<Session>> futures = List.of("task1", "task2", "task3")
    .stream()
    .map(taskId -> CompletableFuture.supplyAsync(() -> {
        SessionResult result = agentBay.create();
        return result.getSession();
    }))
    .collect(Collectors.toList());

// Wait for all sessions to be created
List<Session> sessions = futures.stream()
    .map(CompletableFuture::join)
    .collect(Collectors.toList());

// Use sessions concurrently
List<CompletableFuture<CommandResult>> cmdFutures = sessions.stream()
    .map(session -> CompletableFuture.supplyAsync(() ->
        session.getCommand().executeCommand("echo 'Hello'")
    ))
    .collect(Collectors.toList());

// Wait for all commands
List<CommandResult> results = cmdFutures.stream()
    .map(CompletableFuture::join)
    .collect(Collectors.toList());

// Cleanup
sessions.forEach(Session::delete);
```

### Using ExecutorService

```java
import java.util.concurrent.ExecutorService;
import java.util.concurrent.Executors;
import java.util.concurrent.Future;
import java.util.List;
import java.util.ArrayList;

AgentBay agentBay = new AgentBay();
ExecutorService executor = Executors.newFixedThreadPool(3);

// Submit tasks
List<Future<CommandResult>> futures = new ArrayList<>();
for (int i = 0; i < 3; i++) {
    final int taskId = i;
    Future<CommandResult> future = executor.submit(() -> {
        SessionResult sessionResult = agentBay.create();
        Session session = sessionResult.getSession();

        try {
            CommandResult result = session.getCommand()
                .executeCommand("echo 'Task " + taskId + "'");
            return result;
        } finally {
            session.delete();
        }
    });
    futures.add(future);
}

// Wait for results
for (Future<CommandResult> future : futures) {
    CommandResult result = future.get();
    System.out.println(result.getOutput());
}

executor.shutdown();
```

## 🎯 Callback-Based Async Operations

Some operations support callback-based asynchronous execution:

### Context Sync with Callback

```java
import java.util.concurrent.CompletableFuture;
import java.util.concurrent.TimeUnit;

Session session = agentBay.create().getSession();

// Async context sync with callback
CompletableFuture<Boolean> future = new CompletableFuture<>();
session.getContext().sync(success -> {
    System.out.println("Context sync completed: " + success);
    future.complete(success);
});

// Continue with other work while sync runs in background
System.out.println("Sync triggered, continuing with other work...");

// Wait for sync completion when needed
Boolean syncSuccess = future.get(5, TimeUnit.MINUTES);
System.out.println("Final sync result: " + syncSuccess);
```

### Blocking Alternative

For simpler cases, use the blocking variant:

```java
// Blocks until sync completes
ContextSyncResult result = session.getContext().syncAndWait();
if (result.isSuccess()) {
    System.out.println("Sync completed successfully");
}
```

## 📊 Comparison with Python SDK

| Feature | Java SDK | Python SDK |
|---------|----------|------------|
| **Programming Model** | Synchronous only | Sync + Async variants |
| **Method Calls** | `result = method()` | `result = method()` or `result = await method()` |
| **Concurrency** | Java ExecutorService, CompletableFuture | asyncio, async/await |
| **Use Case** | Scripts, automation, tests | High-concurrency web apps, async frameworks |
| **Learning Curve** | Simple, standard Java | Requires async/await understanding |
| **Performance** | Good for sequential tasks | 4-6x faster for parallel I/O operations |

## 🔧 Best Practices

### 1. Resource Management

Always clean up resources:

```java
Session session = null;
try {
    session = agentBay.create().getSession();
    // Use session
} finally {
    if (session != null) {
        session.delete();
    }
}
```

Or use try-with-resources if Session implements AutoCloseable (future enhancement):

```java
// Future enhancement
try (Session session = agentBay.create().getSession()) {
    // Use session
} // Automatically cleaned up
```

### 2. Error Handling

Check results and handle errors:

```java
SessionResult result = agentBay.create();
if (!result.isSuccess()) {
    System.err.println("Failed to create session: " + result.getErrorMessage());
    return;
}

Session session = result.getSession();
try {
    CommandResult cmdResult = session.getCommand().executeCommand("ls -la");
    if (!cmdResult.isSuccess()) {
        System.err.println("Command failed: " + cmdResult.getErrorMessage());
    }
} finally {
    session.delete();
}
```

### 3. Timeouts

Set appropriate timeouts for long-running operations:

```java
// Set timeout on individual operations
CommandResult result = session.getCommand()
    .executeCommand("long-running-task", 300); // 5 minute timeout
```

### 4. Thread Safety

Sessions are thread-safe, but it's recommended to use one session per thread:

```java
ExecutorService executor = Executors.newFixedThreadPool(3);

// Each thread gets its own session
for (int i = 0; i < 3; i++) {
    executor.submit(() -> {
        Session session = agentBay.create().getSession();
        try {
            // Use session
        } finally {
            session.delete();
        }
    });
}
```

## 🎓 Examples

### Sequential Workflow

```java
AgentBay agentBay = new AgentBay();
Session session = agentBay.create().getSession();

try {
    // Step 1: Create file
    session.getFileSystem().writeFile("/tmp/data.txt", "initial data");

    // Step 2: Process file
    CommandResult result = session.getCommand()
        .executeCommand("cat /tmp/data.txt | wc -l");
    System.out.println("Lines: " + result.getOutput());

    // Step 3: Update file
    session.getFileSystem().writeFile("/tmp/data.txt", "updated data");

} finally {
    session.delete();
}
```

### Parallel Processing

```java
AgentBay agentBay = new AgentBay();
List<String> files = List.of("file1.txt", "file2.txt", "file3.txt");

List<CompletableFuture<Integer>> futures = files.stream()
    .map(filename -> CompletableFuture.supplyAsync(() -> {
        Session session = agentBay.create().getSession();
        try {
            String content = session.getFileSystem().readFile("/data/" + filename);
            return content.length();
        } finally {
            session.delete();
        }
    }))
    .collect(Collectors.toList());

// Wait for all to complete
List<Integer> lengths = futures.stream()
    .map(CompletableFuture::join)
    .collect(Collectors.toList());

System.out.println("File lengths: " + lengths);
```

## 🔗 Related Documentation

- [Examples Index](../examples/README.md) - Practical examples
- [API Reference](../api/README.md) - Detailed API documentation
- [Session Management](../../../docs/guides/common-features/basics/session-management.md) - Session lifecycle
- [Context Synchronization](../api/common-features/basics/context-sync.md) - Async context operations

## 💡 Summary

The Java SDK provides a **simple, synchronous programming model** that is:
- ✅ Easy to learn and use
- ✅ Perfect for automation and scripts
- ✅ Compatible with standard Java concurrency utilities
- ✅ Supports callback-based async where needed (context sync)

For high-concurrency scenarios, use Java's built-in concurrency tools like `CompletableFuture` and `ExecutorService`.
