# Agent Class API Reference

The `Agent` class provides AI-powered capabilities for executing tasks, checking task status, and terminating tasks within a session. It enables natural language task execution and monitoring.

**⚠️ Important Note**: The Agent functionality is verified on the `windows_latest` system image.

## 📖 Related Tutorial

- [Agent Modules Guide](../../../docs/guides/common-features/advanced/agent-modules.md) - Detailed tutorial on AI-powered automation with Agent modules

## Constructor

### Agent

```python
Agent(session)
```

**Parameters:**
- `session` (Session): The Session instance that this Agent belongs to.

## Methods

### execute_task

Executes a specific task described in human language.
This is a synchronous interface that blocks until the task is completed or an error occurs, or timeout happens.
There is a timeout mechanism to prevent infinite loops by setting the `max_try_times` parameter. The default polling interval is 3 seconds, so set a proper `max_try_times` according to your task complexity.

```python
execute_task(task: str, max_try_times: int) -> ExecutionResult
```

**Parameters:**
- `task` (str): Task description in human language.
- `max_try_times` (int): Maximum number of retry attempts.

**Returns:**
- `ExecutionResult`: Result object containing success status, task ID, task status, and error message if any.

**Example:**
```python
from agentbay import AgentBay

# Initialize the SDK
agent_bay = AgentBay(api_key="your_api_key")

# Create a session with windows_latest image
from agentbay.session_params import CreateSessionParams
params = CreateSessionParams(image_id="windows_latest")
session_result = agent_bay.create(params)
if session_result.success:
    session = session_result.session
    
    # Execute a task using the Agent
    task_description = "Find the current weather in New York City"
    execution_result = session.agent.execute_task(task_description, max_try_times=10)
    
    if execution_result.success:
        print(f"Task completed successfully with status: {execution_result.task_status}")
        print(f"Task completed successfully with result: {execution_result.task_result}")
        print(f"Task ID: {execution_result.task_id}")
    else:
        print(f"Task failed: {execution_result.error_message}")
```

### async_execute_task

Executes a specific task described in human language.
This is a asynchronous interface that returns immediately with a task ID. Call `get_task_status` to check the task status.
You can control the timeout of the task execution in your own code by setting the frequence of calling get_task_status and the max_try_times.

```python
async_execute_task(task: str) -> ExecutionResult
```

**Parameters:**
- `task` (str): Task description in human language.

**Returns:**
- `ExecutionResult`: Result object containing success status, task ID, task status, and error message if any.

**Example:**
```python
import time
from agentbay import AgentBay


# Initialize the SDK
agent_bay = AgentBay(api_key="your_api_key")

# Create a session with windows_latest image
from agentbay.session_params import CreateSessionParams
params = CreateSessionParams(image_id="windows_latest")
session_result = agent_bay.create(params)
if session_result.success:
    session = session_result.session
    
    # Execute a task using the Agent
    task_description = "Find the current weather in New York City"
    execution_result = session.agent.async_execute_task(task_description)
    max_retry_times = 50  # Set your own max retry times
    if execution_result.success:
        retry_times = 0
        while retry_times < max_retry_times:
            query_result = session.agent.get_task_status(execution_result.task_id)
            print(
                f"⏳ Task {query_result.task_id} running 🚀: {query_result.task_action}."
            )
            if query_result.task_status == "finished":
                break
            retry_times += 1
            time.sleep(3)
        # Check if task completed within max retry times
        if retry_times < max_retry_times:
            print(
                f"Task completed successfully with status: {query_result.task_status}"
            )
            print(
                f"Task completed successfully with result: {query_result.task_result}"
            )
        else:
            print(f"Task execution timeout!")
    else:
        print(f"Task failed: {execution_result.error_message}")
```

### get_task_status

Gets the status of the task with the given task ID.

```python
get_task_status(task_id: str) -> QueryResult
```

**Parameters:**
- `task_id` (str): Task ID

**Returns:**
- `QueryResult`: Result object containing success status, output, and error message if any.

**Example:**
```python
# Get the status of a specific task
task_id = "task_12345"
status_result = session.agent.get_task_status(task_id)

if status_result.success:
    print(f"Task output: {status_result.task_status}")
    print(f"Task output: {status_result.task_product}")
    print(f"Task output: {status_result.task_action}")
else:
    print(f"Failed to get task status: {status_result.error_message}")
```

### terminate_task

Terminates a task with a specified task ID.

```python
terminate_task(task_id: str) -> ExecutionResult
```

**Parameters:**
- `task_id` (str): The ID of the running task.

**Returns:**
- `ExecutionResult`: Result object containing success status, task ID, task status, and error message if any.

**Example:**
```python
# Terminate a running task
task_id = "task_12345"
terminate_result = session.agent.terminate_task(task_id)

if terminate_result.success:
    print(f"Task terminated successfully with status: {terminate_result.task_status}")
else:
    print(f"Failed to terminate task: {terminate_result.error_message}")
```