# 🤖 Agent API Reference

## Overview

The Agent module provides specialized functionality for the AgentBay cloud platform. It includes various methods and utilities to interact with cloud services and manage resources.

## 📚 Tutorial

[Agent Modules Guide](../../../../../docs/guides/common-features/advanced/agent-modules.md)

Learn about agent modules and custom agents

## Agent

An Agent to manipulate applications to complete specific tasks.

<p><strong>⚠️ Note</strong>: Currently, for agent services (including ComputerUseAgent, BrowserUseAgent, and MobileUseAgent), 
we do not provide services for overseas users registered with <strong>alibabacloud.com</strong>.</p>

### Constructor

```java
public Agent(Session session)
```

### Methods

### getComputer

```java
public Computer getComputer()
```

Get the Computer agent for desktop task execution.

**Returns:**
- `Computer`: Computer agent instance

### getBrowser

```java
public Browser getBrowser()
```

Get the Browser agent for browser task execution.

**Returns:**
- `Browser`: Browser agent instance

### getMobile

```java
public Mobile getMobile()
```

Get the Mobile agent for mobile device task execution.

**Returns:**
- `Mobile`: Mobile agent instance

---

## AgentEvent

Represents a streaming event from an Agent execution.

```java
public class AgentEvent {
    String type;         // "reasoning", "content", "tool_call", "tool_result", "error"
    int seq;
    int round;
    String content;
    String toolCallId;
    String toolName;
    Map<String, Object> args;
    Map<String, Object> result;
    Map<String, Object> error;
}
```

The `result` field in `tool_result` events carries an agent-defined structure that the SDK passes through without parsing. Typical fields include `isError` (bool), `output` (string), and optionally `screenshot` (base64). The final task outcome is delivered via the `ExecutionResult` return value of `executeTaskAndWait`.

---

## StreamOptions

Options for WebSocket streaming execution of agent tasks. When any callback is set, the SDK uses the WebSocket streaming channel for real-time event delivery instead of HTTP polling.

```java
public class StreamOptions {
    Consumer<AgentEvent> onReasoning;
    Consumer<AgentEvent> onContent;
    Consumer<AgentEvent> onToolCall;
    Consumer<AgentEvent> onToolResult;
    Consumer<AgentEvent> onError;
}
```

Use `StreamOptions.builder()` for fluent construction.

---

## MobileTaskOptions

Options for mobile task execution, extending `StreamOptions` with mobile-specific options.

```java
public class MobileTaskOptions extends StreamOptions {
    int maxSteps;                              // default 50
    Function<AgentEvent, String> onCallForUser; // human-in-the-loop callback
}
```

Use `MobileTaskOptions.mobileBuilder()` for fluent construction:

```java
MobileTaskOptions options = MobileTaskOptions.mobileBuilder()
    .maxSteps(100)
    .onReasoning(e -> System.out.print(e.getContent()))
    .onToolCall(e -> System.out.println("Calling: " + e.getToolName()))
    .onToolResult(e -> System.out.println("Result: " + e.getOutput()))
    .onError(e -> System.err.println("Error: " + e.getError()))
    .onCallForUser(e -> askUser(e.getContent()))
    .build();
```

---

## TaskExecution

Represents a running task that can be waited on for its final result. Returned by `Mobile.executeTask()`.

```java
public class TaskExecution {
    private final String taskId;
    private final CompletableFuture<ExecutionResult> resultFuture;
}
```

### Methods

### getTaskId

```java
public String getTaskId()
```

Returns the task ID (may be null when using WebSocket streaming mode).

### wait

```java
public ExecutionResult wait(int timeout)
```

Block until the task finishes or the timeout (in seconds) is reached. Returns an `ExecutionResult` with error information on timeout or failure.

---

## Mobile

The Mobile agent for executing tasks on mobile devices.

### executeTask

```java
public TaskExecution executeTask(String task)
public TaskExecution executeTask(String task, MobileTaskOptions options)
```

Start a mobile task and return a `TaskExecution` handle immediately (non-blocking). Use `TaskExecution.wait(timeout)` to block until the task completes.

When streaming callbacks are provided in `MobileTaskOptions`, real-time events are delivered via WebSocket. Otherwise the task is started via MCP and the handle supports polling-based `wait()`.

**Example (non-blocking):**

```java
TaskExecution execution = session.getAgent().getMobile().executeTask("Open WeChat app");
ExecutionResult result = execution.wait(180);
```

**Example (with streaming):**

```java
MobileTaskOptions options = MobileTaskOptions.mobileBuilder()
    .maxSteps(100)
    .onReasoning(e -> System.out.print(e.getContent()))
    .onToolCall(e -> System.out.println("Calling: " + e.getToolName()))
    .build();

TaskExecution execution = session.getAgent().getMobile().executeTask("Open Settings app", options);
ExecutionResult result = execution.wait(180);
```

### executeTaskAndWait

```java
public ExecutionResult executeTaskAndWait(String task, int timeout)
public ExecutionResult executeTaskAndWait(String task, int timeout, MobileTaskOptions options)
```

Convenience wrapper that starts a task via `executeTask` and immediately blocks until it completes or times out. Equivalent to `executeTask(task, options).wait(timeout)`.

**Example (simple):**

```java
ExecutionResult result = session.getAgent().getMobile()
    .executeTaskAndWait("Open WeChat app", 180);
```

**Example (with streaming):**

```java
MobileTaskOptions options = MobileTaskOptions.mobileBuilder()
    .maxSteps(100)
    .onReasoning(e -> System.out.print(e.getContent()))
    .onToolCall(e -> System.out.println("Calling: " + e.getToolName()))
    .onToolResult(e -> System.out.println("Result: " + e.getOutput()))
    .onError(e -> System.err.println("Error: " + e.getError()))
    .onCallForUser(e -> askUser(e.getContent()))
    .build();

ExecutionResult result = session.getAgent().getMobile()
    .executeTaskAndWait("Open Settings app", 180, options);
```

### getTaskStatus

```java
public QueryResult getTaskStatus(String taskId)
```

Get the status of a running task by its task ID.

### terminateTask

```java
public ExecutionResult terminateTask(String taskId)
```

Terminate a running task by its task ID.

---

## Computer

The Computer agent for executing tasks on a desktop environment.

### executeTask

```java
public ExecutionResult executeTask(String task)
```

Start a computer task (non-blocking). Returns an `ExecutionResult` containing the task ID.

### executeTaskAndWait

```java
public ExecutionResult executeTaskAndWait(String task, int timeout)
```

Execute a task on the desktop synchronously. Blocks until the task is completed, an error occurs, or timeout is reached.

### getTaskStatus

```java
public QueryResult getTaskStatus(String taskId)
```

Get the status of a running task.

### terminateTask

```java
public ExecutionResult terminateTask(String taskId)
```

Terminate a running task.

---

## Browser

The Browser agent for executing tasks in a browser.

### executeTask

```java
public ExecutionResult executeTask(String task, boolean useVision, Object outputSchema, boolean fullPageScreenShot)
```

Start a browser task (non-blocking). Returns an `ExecutionResult` containing the task ID.

### executeTaskAndWait

```java
public ExecutionResult executeTaskAndWait(String task, int timeout, boolean useVision, Object outputSchema, boolean fullPageScreenShot)
```

Execute a task on the browser synchronously. Blocks until the task is completed, an error occurs, or timeout is reached.

### getTaskStatus

```java
public QueryResult getTaskStatus(String taskId)
```

Get the status of a running task.

### terminateTask

```java
public ExecutionResult terminateTask(String taskId)
```

Terminate a running task.

---

## ExecutionResult

Represents the result of task execution.

```java
public class ExecutionResult {
    String requestId;
    boolean success;
    String errorMessage;
    String taskId;
    String taskStatus;
    String taskResult;
}
```

## QueryResult

Represents the result of task status query operations.

```java
public class QueryResult {
    String requestId;
    boolean success;
    String errorMessage;
    String taskId;
    String taskStatus;
    String taskAction;
    String taskProduct;
}
```

## 🔗 Related Resources

- [Session API Reference](../../../api/common-features/basics/session.md)

