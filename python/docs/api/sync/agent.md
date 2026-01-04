# Agent API Reference

> **💡 Async Version**: This documentation covers the synchronous API. For async/await support, see [`AsyncAgent`](../async/async-agent.md) which provides the same functionality with async methods.

## 🤖 Related Tutorial

- [Agent Modules Guide](../../../../docs/guides/common-features/advanced/agent-modules.md) - Learn about agent modules and custom agents



## Agent

```python
class Agent(BaseService)
```

An Agent to manipulate applications to complete specific tasks.

> **⚠️ Note**: Currently, for agent services (including ComputerUseAgent, BrowserUseAgent, and MobileUseAgent), we do not provide services for overseas users registered with **alibabacloud.com**.

### \_\_init\_\_

```python
def __init__(self, session: "Session")
```

## Computer

```python
class Computer(_BaseTaskAgent)
```

An Agent to perform tasks on the computer.

> **⚠️ Note**: Currently, for agent services (including ComputerUseAgent, BrowserUseAgent, and MobileUseAgent), we do not provide services for overseas users registered with **alibabacloud.com**.

### \_\_init\_\_

```python
def __init__(self, session: "Session")
```

## Browser

```python
class Browser(_BaseTaskAgent)
```

An Agent(⚠️ Still in BETA) to perform tasks on the browser

> **⚠️ Note**: Currently, for agent services (including ComputerUseAgent, BrowserUseAgent, and MobileUseAgent), we do not provide services for overseas users registered with **alibabacloud.com**.

### \_\_init\_\_

```python
def __init__(self, session: "Session")
```

### initialize

```python
def initialize(options: AgentOptions = None) -> InitializationResult
```

Initialize the browser agent with options.

**Arguments**:

    options: options for the agent.
  

**Returns**:

    InitializationResult: Result object containing success status, and error message if any.
  

**Example**:

```python
session_result = agent_bay.create()
session = session_result.session
options:AgentOptions = AgentOptions(use_vision=False, output_schema="")
initialize_result = session.agent.browser.initialize(options)
print(f"Initialized: {initialize_result.success}")
session.delete()
```

## Mobile

```python
class Mobile(_BaseTaskAgent)
```

An Agent to perform tasks on mobile devices.

> **⚠️ Note**: Currently, for agent services (including ComputerUseAgent, BrowserUseAgent, and MobileUseAgent), we do not provide services for overseas users registered with **alibabacloud.com**.

### \_\_init\_\_

```python
def __init__(self, session: "Session")
```

### execute\_task

```python
def execute_task(task: str, max_steps: int = 50) -> ExecutionResult
```

Execute a task in human language without waiting for completion
(non-blocking).

This is a fire-and-return interface that immediately provides a task ID.
Call get_task_status to check the task status. You can control the timeout
of the task execution in your own code by setting the frequency of calling
get_task_status.

**Arguments**:

    task: Task description in human language.
    max_steps: Maximum number of steps (clicks/swipes/etc.) allowed.
  Used to prevent infinite loops or excessive resource consumption.
  Default is 50.
  

**Returns**:

    ExecutionResult: Result object containing success status, task ID,
  task status, and error message if any.
  

**Example**:

```python
session_result = agent_bay.create()
session = session_result.session
result = session.agent.mobile.execute_task(
  "Open WeChat app", max_steps=100
)
print(f"Task ID: {result.task_id}, Status: {result.task_status}")
status = session.agent.mobile.get_task_status(result.task_id)
print(f"Task status: {status.task_status}")
session.delete()
```

### execute\_task\_and\_wait

```python
def execute_task_and_wait(task: str,
                          timeout: int,
                          max_steps: int = 50) -> ExecutionResult
```

Execute a specific task described in human language synchronously.

This is a synchronous interface that blocks until the task is
completed or an error occurs, or timeout happens. The default
polling interval is 3 seconds.

**Arguments**:

    task: Task description in human language.
    timeout: Maximum time to wait for task completion in seconds.
  Used to control how long to wait for task completion.
    max_steps: Maximum number of steps (clicks/swipes/etc.) allowed.
  Used to prevent infinite loops or excessive resource consumption.
  Default is 50.
  

**Returns**:

    ExecutionResult: Result object containing success status, task ID,
  task status, and error message if any.
  

**Example**:

```python
session_result = agent_bay.create()
session = session_result.session
result = session.agent.mobile.execute_task_and_wait(
  "Open WeChat app and send a message",
  timeout=180,
  max_steps=100
)
print(f"Task result: {result.task_result}")
session.delete()
```

### get\_task\_status

```python
def get_task_status(task_id: str) -> QueryResult
```

### terminate\_task

```python
def terminate_task(task_id: str) -> ExecutionResult
```

## See Also

- [Synchronous vs Asynchronous API](../../../docs/guides/async-programming/sync-vs-async.md)

**Related APIs:**
- [Session API Reference](./session.md)

---

*Documentation generated automatically from source code using pydoc-markdown.*
