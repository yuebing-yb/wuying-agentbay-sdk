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

## SchemaHelper

### Methods

### generateJsonSchema

```java
public static String generateJsonSchema(Class<?> schemaClass)
```

## Computer

An Agent to perform tasks on the computer.

<p><strong>⚠️ Note</strong>: Currently, for agent services (including ComputerUseAgent, BrowserUseAgent, and MobileUseAgent), 
we do not provide services for overseas users registered with <strong>alibabacloud.com</strong>.</p>

### Constructor

```java
public Computer(Session session)
```

### Methods

### executeTask

```java
public ExecutionResult executeTask(String task)
```

Execute a task in human language without waiting for completion (non-blocking).

This is a fire-and-return interface that immediately provides a task ID.
Call getTaskStatus to check the task status. You can control the timeout
of the task execution in your own code by setting the frequency of calling
getTaskStatus.

**Parameters:**
- `task` (String): Task description in human language

**Returns:**
- `ExecutionResult`: ExecutionResult containing success status, task ID, task status, and error message if any

### executeTaskAndWait

```java
public ExecutionResult executeTaskAndWait(String task, int timeout)
```

Execute a specific task described in human language synchronously.

This is a synchronous interface that blocks until the task is completed or
an error occurs, or timeout happens. The default polling interval is 3 seconds.

**Parameters:**
- `task` (String): Task description in human language
- `timeout` (int): Maximum time to wait for task completion in seconds

**Returns:**
- `ExecutionResult`: ExecutionResult containing success status, task ID, task status, task result, and error message if any

### getTaskStatus

```java
public QueryResult getTaskStatus(String taskId)
```

Get the status of the task with the given task ID.

**Parameters:**
- `taskId` (String): The ID of the task to query

**Returns:**
- `QueryResult`: QueryResult containing success status, task status, task action, task product, and error message if any

### terminateTask

```java
public ExecutionResult terminateTask(String taskId)
```

Terminate a task with a specified task ID.

**Parameters:**
- `taskId` (String): The ID of the running task to terminate

**Returns:**
- `ExecutionResult`: ExecutionResult containing success status, task ID, task status, and error message if any

## Browser

Browser agent for browser automation with natural language.

<p><strong>⚠️ Note</strong>: Currently, for agent services (including ComputerUseAgent, BrowserUseAgent, and MobileUseAgent), 
we do not provide services for overseas users registered with <strong>alibabacloud.com</strong>.</p>

### Constructor

```java
public Browser(Session session)
```

### Methods

### initialize

```java
public boolean initialize(BrowserOption option)
```

Initialize the browser on which the agent performs tasks.
You are supposed to call this API before executeTask is called, but it's not optional.
If you want perform a hybrid usage of browser, you must call this API before executeTask is called.

**Parameters:**
- `option` (BrowserOption): the browser initialization options. If {@code null}, default options will be used

**Returns:**
- `boolean`: {@code true} if the browser is successfully initialized, {@code false} otherwise

### executeTask

```java
public ExecutionResult executeTask(String task, boolean useVision, Object outputSchema, boolean fullPageScreenShot)
```

Execute a task described in human language on a browser without waiting for completion (non-blocking).

This is a fire-and-return interface that immediately provides a task ID.
Call get_task_status to check the task status. You can control the timeout
of the task execution in your own code by setting the frequency of calling
get_task_status.

**Parameters:**
- `task` (String): Task description in human language
- `useVision` (boolean): Whether to use vision to performe the task
- `outputSchema` (Object): The schema of the structured output
- `fullPageScreenShot` (boolean): Whether to take a full page screenshot. This only works when use_vision is true.
                          When use_vision is enabled, we need to provide a screenshot of the webpage to the LLM for grounding. There are two ways of screenshot:
                          1. Full-page screenshot: Captures the entire webpage content, including parts not currently visible in the viewport.
                          2. Viewport screenshot: Captures only the currently visible portion of the webpage.
                          The first approach delivers all information to the LLM in one go, which can improve task success rates in certain information extraction scenarios. However, it also results in higher token consumption and increases the LLM's processing time.
                          Therefore, we would like to give you the choice—you can decide whether to enable full-page screenshot based on your actual needs.

**Returns:**
- `ExecutionResult`: ExecutionResult Result object containing success status, task ID, task status, and error message if any

### executeTaskAndWait

```java
public ExecutionResult executeTaskAndWait(String task, int timeout, boolean useVision, Object outputSchema, boolean fullPageScreenShot)
```

Execute a specific task described in human language synchronously.

This is a synchronous interface that blocks until the task is completed or
an error occurs, or timeout happens. The default polling interval is 3
seconds.

**Parameters:**
- `task` (String): Task description in human language
- `timeout` (int): Maximum time to wait for task completion in seconds
- `useVision` (boolean): Whether to use vision in the task
- `outputSchema` (Object): Optional Zod schema for a structured task output if
                          you need
- `fullPageScreenShot` (boolean): Whether to take a full page screenshot,
                          this only works if useVision is true

                          When use_vision is enabled, we need to provide a
                          screenshot of the webpage to the LLM for grounding.
                          There are two ways of screenshot:
                          1. Full-page screenshot: Captures the entire
                          webpage content, including parts not currently
                          visible in the viewport.
                          2. Viewport screenshot: Captures only the currently
                          visible portion of the webpage.
                          The first approach delivers all information to the
                          LLM in one go, which can improve task success rates
                          in certain information extraction scenarios.
                          However, it also results in higher token
                          consumption and increases the LLM's processing
                          time.
                          Therefore, we would like to give you the choice—you
                          can decide whether to enable full-page screenshot
                          based on your actual needs.

**Returns:**
- `ExecutionResult`: ExecutionResult containing success status, task ID, task status, task
        result, and error message if any

### getTaskStatus

```java
public QueryResult getTaskStatus(String taskId)
```

Get the status of the task with the given task ID.

**Parameters:**
- `taskId` (String): The ID of the task to query

**Returns:**
- `QueryResult`: QueryResult containing success status, task status, task action, task product, and error message if any

### terminateTask

```java
public ExecutionResult terminateTask(String taskId)
```

Terminate a task with a specified task ID.

**Parameters:**
- `taskId` (String): The ID of the running task to terminate

**Returns:**
- `ExecutionResult`: ExecutionResult containing success status, task ID, task status, and error message if any

## Mobile

Mobile agent for mobile device automation with natural language.
Uses execute_task, get_task_status, terminate_task MCP tools for task execution.

### Constructor

```java
public Mobile(Session session)
```

### Methods

### executeTask

```java
public TaskExecution executeTask(String task)
```

```java
public TaskExecution executeTask(String task, MobileTaskOptions options)
```

Execute a mobile task in human language without waiting for completion (non-blocking).

When options has streaming callbacks, uses WebSocket streaming for real-time events.
Otherwise uses MCP call and polling.

**Parameters:**
- `task` (String): Task description in human language
- `options` (MobileTaskOptions): Optional MobileTaskOptions (maxSteps, streaming callbacks)

**Returns:**
- `TaskExecution`: TaskExecution handle for the running task

### executeTaskAndWait

```java
public ExecutionResult executeTaskAndWait(String task, int timeout)
```

```java
public ExecutionResult executeTaskAndWait(String task, int timeout, MobileTaskOptions options)
```

Execute a task synchronously with optional WebSocket streaming.
When {@code options} has streaming params, uses WS streaming for real-time events.

**Parameters:**
- `task` (String): Task description in human language
- `timeout` (int): Maximum time to wait for task completion in seconds
- `options` (MobileTaskOptions): Optional MobileTaskOptions (maxSteps, streaming callbacks)

**Returns:**
- `ExecutionResult`: ExecutionResult containing success status, task ID, task status, task result, and error message if any

### getTaskStatus

```java
public QueryResult getTaskStatus(String taskId)
```

Get the status of the task with the given task ID.

**Parameters:**
- `taskId` (String): The ID of the task to query

**Returns:**
- `QueryResult`: QueryResult containing success status, task status, task action, task product, stream, error, and error message if any

### terminateTask

```java
public ExecutionResult terminateTask(String taskId)
```

Terminate a task with a specified task ID.

**Parameters:**
- `taskId` (String): The ID of the running task to terminate

**Returns:**
- `ExecutionResult`: ExecutionResult containing success status, task ID, task status, and error message if any



## AgentEvent

Represents a streaming event from an Agent execution.

<p>Event types map directly to LLM output field names:
<ul>
  <li>"reasoning": from LLM reasoning_content (model's internal reasoning/thinking)
  <li>"content": from LLM content (model's text output, intermediate analysis or final answer)
  <li>"tool_call": from LLM tool_calls (tool invocation request)
  <li>"tool_result": tool execution result
  <li>"error": execution error
</ul>

<p>The {@code result} field in tool_result events carries an agent-defined structure
that the SDK passes through without parsing. Typical fields include
{@code isError} (boolean), {@code output} (string), and optionally
{@code screenshot} (base64 string). The final task outcome is delivered via
the {@link com.aliyun.agentbay.model.ExecutionResult} return value of
{@code executeTaskAndWait}.

### Constructor

```java
public AgentEvent()
```

```java
public AgentEvent(String type, int seq, int round)
```

### Methods

### getSeq

```java
public int getSeq()
```

### setSeq

```java
public void setSeq(int seq)
```

### getRound

```java
public int getRound()
```

### setRound

```java
public void setRound(int round)
```

### getContent

```java
public String getContent()
```

### setContent

```java
public void setContent(String content)
```

### getToolCallId

```java
public String getToolCallId()
```

### setToolCallId

```java
public void setToolCallId(String toolCallId)
```

### getToolName

```java
public String getToolName()
```

### setToolName

```java
public void setToolName(String toolName)
```

### getArgs

```java
public Map<String, Object> getArgs()
```

### setArgs

```java
public void setArgs(Map<String, Object> args)
```

### getResult

```java
public Map<String, Object> getResult()
```

### setResult

```java
public void setResult(Map<String, Object> result)
```

### getError

```java
public Map<String, Object> getError()
```

### setError

```java
public void setError(Map<String, Object> error)
```



## StreamOptions

Options for WebSocket streaming execution of agent tasks.

<p>When any callback is set, the SDK uses the WebSocket streaming channel
for real-time event delivery instead of HTTP polling.</p>

### Constructor

```java
public StreamOptions()
```

### Methods

### getOnReasoning

```java
public Consumer<AgentEvent> getOnReasoning()
```

Returns the callback for reasoning events (LLM reasoning_content).

### setOnReasoning

```java
public void setOnReasoning(Consumer<AgentEvent> onReasoning)
```

### getOnContent

```java
public Consumer<AgentEvent> getOnContent()
```

Returns the callback for content events (LLM content output).

### setOnContent

```java
public void setOnContent(Consumer<AgentEvent> onContent)
```

### getOnToolCall

```java
public Consumer<AgentEvent> getOnToolCall()
```

Returns the callback for tool_call events.

### setOnToolCall

```java
public void setOnToolCall(Consumer<AgentEvent> onToolCall)
```

### getOnToolResult

```java
public Consumer<AgentEvent> getOnToolResult()
```

Returns the callback for tool_result events.

### setOnToolResult

```java
public void setOnToolResult(Consumer<AgentEvent> onToolResult)
```

### getOnError

```java
public Consumer<AgentEvent> getOnError()
```

Returns the callback for error events.

### setOnError

```java
public void setOnError(Consumer<AgentEvent> onError)
```

### hasStreamingParams

```java
public boolean hasStreamingParams()
```

Returns true if streaming should be used (any callback is set).

### builder

```java
public static Builder builder()
```

Builder for StreamOptions.

## Builder

### Methods

### onReasoning

```java
public Builder onReasoning(Consumer<AgentEvent> onReasoning)
```

### onContent

```java
public Builder onContent(Consumer<AgentEvent> onContent)
```

### onToolCall

```java
public Builder onToolCall(Consumer<AgentEvent> onToolCall)
```

### onToolResult

```java
public Builder onToolResult(Consumer<AgentEvent> onToolResult)
```

### onError

```java
public Builder onError(Consumer<AgentEvent> onError)
```

### build

```java
public StreamOptions build()
```



## MobileTaskOptions

Options for mobile task execution, including streaming callbacks.
Extends StreamOptions with mobile-specific options like maxSteps and onCallForUser.

### Constructor

```java
public MobileTaskOptions()
```

### Methods

### getMaxSteps

```java
public int getMaxSteps()
```

### setMaxSteps

```java
public void setMaxSteps(int maxSteps)
```

### getOnCallForUser

```java
public Function<AgentEvent, String> getOnCallForUser()
```

### setOnCallForUser

```java
public void setOnCallForUser(Function<AgentEvent, String> onCallForUser)
```

### hasStreamingParams

```java
public boolean hasStreamingParams()
```

### mobileBuilder

```java
public static MobileBuilder mobileBuilder()
```

## MobileBuilder

### Methods

### maxSteps

```java
public MobileBuilder maxSteps(int maxSteps)
```

### onReasoning

```java
public MobileBuilder onReasoning(java.util.function.Consumer<AgentEvent> cb)
```

### onContent

```java
public MobileBuilder onContent(java.util.function.Consumer<AgentEvent> cb)
```

### onToolCall

```java
public MobileBuilder onToolCall(java.util.function.Consumer<AgentEvent> cb)
```

### onToolResult

```java
public MobileBuilder onToolResult(java.util.function.Consumer<AgentEvent> cb)
```

### onError

```java
public MobileBuilder onError(java.util.function.Consumer<AgentEvent> cb)
```

### onCallForUser

```java
public MobileBuilder onCallForUser(Function<AgentEvent, String> cb)
```

### build

```java
public MobileTaskOptions build()
```



## TaskExecution

Represents a running task that can be waited on for its final result.
Returned by Mobile.executeTask() when the task is started.

### Constructor

```java
public TaskExecution(String taskId, CompletableFuture<ExecutionResult> resultFuture)
```

```java
public TaskExecution(String taskId, CompletableFuture<ExecutionResult> resultFuture, Runnable cancelFn)
```

### Methods

### getTaskId

```java
public String getTaskId()
```

### wait

```java
public ExecutionResult wait(int timeout)
```

Block until the task finishes or the timeout (in seconds) is reached.



## 🔗 Related Resources

- [Session API Reference](../../../api/common-features/basics/session.md)

