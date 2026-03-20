# AsyncAgent API Reference

> **💡 Sync Version**: This documentation covers the asynchronous API. For synchronous operations, see [`Agent`](../sync/agent.md).
>
> ⚡ **Performance Advantage**: Async API enables concurrent operations with 4-6x performance improvements for parallel tasks.

## 🤖 Related Tutorial

- [Agent Modules Guide](../../../../docs/guides/common-features/advanced/agent-modules.md) - Learn about agent modules and custom agents



#### AgentEventCallback

```python
AgentEventCallback = Optional[Callable[[AgentEvent], None]]
```

#### AsyncAgentEventCallback

```python
AsyncAgentEventCallback = Optional[Callable[[AgentEvent], Union[Awaitable[str],
                     ...
```

## TaskExecution

```python
class TaskExecution()
```

Handle for a running task, returned by ``execute_task()``.

If streaming callbacks were registered, events are dispatched in the
background as soon as the WebSocket connection delivers them.  Call
``wait()`` to block until the task completes and retrieve the final
``ExecutionResult``.

**Attributes**:

    task_id: The identifier of the running task (empty when using
  the WebSocket streaming path, since the task is managed
  by the server stream).

### __init__

```python
def __init__(self, task_id: str = "",
             *,
             _ws_handle: Optional[Any] = None,
             _context: Optional[_StreamContext] = None,
             _agent: Optional[Any] = None,
             _result: Optional[ExecutionResult] = None,
             _request_id: str = "")
```

### wait

```python
async def wait(timeout: int = 300) -> ExecutionResult
```

Block until the task completes and return the final result.

**Arguments**:

    timeout: Maximum seconds to wait. Default 300.
  

**Returns**:

  ExecutionResult with the task outcome.

## AsyncAgent

```python
class AsyncAgent(AsyncBaseService)
```

An Agent to manipulate applications to complete specific tasks.

> **⚠️ Note**: Currently, for agent services (including ComputerUseAgent, BrowserUseAgent, and MobileUseAgent), we do not provide services for overseas users registered with **alibabacloud.com**.

### __init__

```python
def __init__(self, session: "AsyncSession")
```

## Computer

```python
class Computer(_BaseTaskAgent)
```

An Agent to perform tasks on the computer.

> **⚠️ Note**: Currently, for agent services (including ComputerUseAgent, BrowserUseAgent, and MobileUseAgent), we do not provide services for overseas users registered with **alibabacloud.com**.

### __init__

```python
def __init__(self, session: "AsyncSession")
```

## Browser

```python
class Browser(_BaseTaskAgent)
```

> **⚠️ Note**: Currently, for agent services (including ComputerUseAgent, BrowserUseAgent, and MobileUseAgent), we do not provide services for overseas users registered with **alibabacloud.com**.

### __init__

```python
def __init__(self, session: "AsyncSession")
```

### initialize

```python
async def initialize(option: Optional[BrowserOption] = None) -> bool
```

Initialize the browser on which the agent performs tasks.
You are supposed to call this API before executeTask is called, but it's not optional.
If you want perform a hybrid usage of browser, you must call this API before executeTask is called.

**Returns**:

    bool: True if the browser is successfully initialized, False otherwise.

### execute_task

```python
async def execute_task(
        task: str,
        use_vision: bool = False,
        output_schema: Type[Schema] = None,
        full_page_screenshot: Optional[bool] = False) -> ExecutionResult
```

Execute a task described in human language on a browser without waiting for completion (non-blocking).

This is a fire-and-return interface that immediately provides a task ID.
Call get_task_status to check the task status. You can control the timeout
of the task execution in your own code by setting the frequency of calling
get_task_status.

**Arguments**:

    task: Task description in human language.
    use_vision: Whether to use vision to performe the task.
    output_schema: The schema of the structured output.
    full_page_screenshot: Whether to take a full page screenshot. This only works when use_vision is true.
  When use_vision is enabled, we need to provide a screenshot of the webpage to the LLM for grounding. There are two ways of screenshot:
  1. Full-page screenshot: Captures the entire webpage content, including parts not currently visible in the viewport.
  2. Viewport screenshot: Captures only the currently visible portion of the webpage.
  The first approach delivers all information to the LLM in one go, which can improve task success rates in certain information extraction scenarios. However, it also results in higher token consumption and increases the LLM's processing time.
  Therefore, we would like to give you the choice—you can decide whether to enable full-page screenshot based on your actual needs.

**Returns**:

    ExecutionResult: Result object containing success status, task ID,
  task status, and error message if any.
  

**Example**:

```python
session_result = await agent_bay.create()
session = session_result.session
class WeatherSchema(BaseModel):
  city:str
  weather: str
result = await session.agent.browser.execute_task(task="Query the weather in Shanghai",use_vision=False, output_schema=WeatherSchema, full_page_screenshot=True)
print(
  f"Task ID: {result.task_id}, Status: {result.task_status}")
status = await session.agent.browser.get_task_status(result.task_id)
print(f"Task status: {status.task_status}")
await session.delete()
```

### execute_task_and_wait

```python
async def execute_task_and_wait(
        task: str,
        timeout: int,
        use_vision: bool = False,
        output_schema: Type[Schema] = None,
        full_page_screenshot: Optional[bool] = False) -> ExecutionResult
```

Execute a task described in human language on a browser synchronously.

This is a synchronous interface that blocks until the task is completed or
an error occurs, or timeout happens. The default polling interval is 3 seconds.

**Arguments**:

    task: Task description in human language.
    timeout: Maximum time to wait for task completion in seconds.
    use_vision: Whether to use vision to perform the task.
    output_schema: The schema of the structured output.
    full_page_screenshot: Whether to take a full page screenshot.
  

**Returns**:

    ExecutionResult: Result object containing success status, task ID,
  task status, and error message if any.
  

**Example**:

```python
session_result = await agent_bay.create()
session = session_result.session
class WeatherSchema(BaseModel):
  city:str
  weather: str
result = await session.agent.browser.execute_task_and_wait(task="Query the weather in Shanghai",timeout=60, use_vision=False, output_schema=WeatherSchema, full_page_screenshot=True)
print(f"Task result: {result.task_result}")
await session.delete()
```

## Mobile

```python
class Mobile(_BaseTaskAgent)
```

An Agent to perform tasks on mobile devices.

> **⚠️ Note**: Currently, for agent services (including ComputerUseAgent, BrowserUseAgent, and MobileUseAgent), we do not provide services for overseas users registered with **alibabacloud.com**.

### __init__

```python
def __init__(self, session: "AsyncSession")
```

### execute_task

```python
async def execute_task(
        task: str,
        max_steps: int = 50,
        on_reasoning: AgentEventCallback = None,
        on_content: AgentEventCallback = None,
        on_tool_call: AgentEventCallback = None,
        on_tool_result: AgentEventCallback = None,
        on_error: AgentEventCallback = None,
        on_call_for_user: AsyncAgentEventCallback = None) -> TaskExecution
```

Execute a task in human language (non-blocking).

Returns a ``TaskExecution`` handle immediately. Call
``execution.wait(timeout)`` to block until the task completes.

When any ``on_*`` callback is provided, a WebSocket connection is
established and streaming events are dispatched in the background.

**Arguments**:

    task: Task description in human language.
    max_steps: Maximum number of steps (clicks/swipes/etc.) allowed.
  Default is 50.
    on_reasoning: Callback for reasoning events (LLM reasoning_content).
    on_content: Callback for content events (LLM content output).
    on_tool_call: Callback for tool_call events.
    on_tool_result: Callback for tool_result events.
    on_error: Callback for error events.
    on_call_for_user: Callback for call_for_user events.
  Returns the user's response string.
  

**Returns**:

    TaskExecution: Handle for the running task.
  

**Example**:

```python
session_result = await agent_bay.create()
session = session_result.session

# Non-blocking with streaming callbacks
execution = await session.agent.mobile.execute_task(
  "Open WeChat app",
  max_steps=100,
  on_reasoning=lambda e: print(e.content, end="", flush=True),
)
result = await execution.wait(timeout=180)
print(f"Task result: {result.task_result}")

# Non-blocking without streaming (poll with wait)
execution = await session.agent.mobile.execute_task("Open Settings")
result = await execution.wait(timeout=60)

await session.delete()
```

### execute_task_and_wait

```python
async def execute_task_and_wait(
        task: str,
        timeout: int,
        max_steps: int = 50,
        on_reasoning: AgentEventCallback = None,
        on_content: AgentEventCallback = None,
        on_tool_call: AgentEventCallback = None,
        on_tool_result: AgentEventCallback = None,
        on_error: AgentEventCallback = None,
        on_call_for_user: AsyncAgentEventCallback = None) -> ExecutionResult
```

Execute a task and wait for completion (blocking convenience wrapper).

Equivalent to ``execute_task(...) + execution.wait(timeout)``.

When any ``on_*`` callback is provided, the method uses the WebSocket
streaming channel for real-time event delivery instead of HTTP polling.

**Arguments**:

    task: Task description in human language.
    timeout: Maximum time to wait for task completion in seconds.
    max_steps: Maximum number of steps (clicks/swipes/etc.) allowed.
  Default is 50.
    on_reasoning: Callback for reasoning events (LLM reasoning_content).
    on_content: Callback for content events (LLM content output).
    on_tool_call: Callback for tool_call events.
    on_tool_result: Callback for tool_result events.
    on_error: Callback for error events.
    on_call_for_user: Callback for call_for_user events.
  Returns the user's response string.
  

**Returns**:

    ExecutionResult: Result object containing success status, task ID,
  task status, and error message if any.
  

**Example**:

```python
session_result = await agent_bay.create()
session = session_result.session
result = await session.agent.mobile.execute_task_and_wait(
  "Open WeChat app and send a message",
  timeout=180,
  max_steps=100,
  on_reasoning=lambda e: print(e.content, end="", flush=True),
)
print(f"Task result: {result.task_result}")
await session.delete()
```

### get_task_status

```python
async def get_task_status(task_id: str) -> QueryResult
```

### terminate_task

```python
async def terminate_task(task_id: str) -> ExecutionResult
```

## See Also

- [Synchronous vs Asynchronous API](../../../docs/guides/async-programming/sync-vs-async.md)

**Related APIs:**
- [Session API Reference](./async-session.md)

---

*Documentation generated automatically from source code using pydoc-markdown.*
