# Agent API Reference

## 🤖 Related Tutorial

- [Agent Modules Guide](../../../../../../docs/guides/common-features/advanced/agent-modules.md) - Learn about agent modules and custom agents



## QueryResult Objects

```python
class QueryResult(ApiResponse)
```

Result of query operations.

## ExecutionResult Objects

```python
class ExecutionResult(ApiResponse)
```

Result of task execution.

## Agent Objects

```python
class Agent(BaseService)
```

An Agent to manipulate applications to complete specific tasks.

#### async\_execute\_task

```python
def async_execute_task(task: str) -> ExecutionResult
```

Execute a specific task described in human language asynchronously.

This is an asynchronous interface that returns immediately with a task ID.
Call get_task_status to check the task status. You can control the timeout
of the task execution in your own code by setting the frequency of calling
get_task_status and the max_try_times.

**Arguments**:

    task: Task description in human language.
  

**Returns**:

    ExecutionResult: Result object containing success status, task ID,
  task status, and error message if any.
  

**Example**:

```python
import time
from agentbay import AgentBay
from agentbay.session_params import CreateSessionParams

agent_bay = AgentBay(api_key="your_api_key")

def async_execute_agent_task():
    try:
        # Create a session with windows_latest image
        params = CreateSessionParams(image_id="windows_latest")
        result = agent_bay.create(params)
        if result.success:
            session = result.session

            # Execute a task asynchronously
            task_description = "Open calculator and compute 123 + 456"
            execution_result = session.agent.async_execute_task(task_description)

            if execution_result.success:
                # Poll for task status
                max_retry_times = 50
                retry_times = 0
                while retry_times < max_retry_times:
                    query_result = session.agent.get_task_status(
                        execution_result.task_id
                    )
                    print(f"Task {query_result.task_id} running: {query_result.task_action}")

                    if query_result.task_status == "finished":
                        print(f"Task completed with result: {query_result.task_product}")
                        break

                    retry_times += 1
                    time.sleep(3)

                if retry_times >= max_retry_times:
                    print("Task execution timeout!")
            else:
                print(f"Task failed: {execution_result.error_message}")

            session.delete()
    except Exception as e:
        print(f"Error: {e}")

async_execute_agent_task()
```

#### execute\_task

```python
def execute_task(task: str, max_try_times: int) -> ExecutionResult
```

Execute a specific task described in human language synchronously.

This is a synchronous interface that blocks until the task is completed or
an error occurs, or timeout happens. The default polling interval is 3 seconds,
so set a proper max_try_times according to your task complexity.

**Arguments**:

    task: Task description in human language.
    max_try_times: Maximum number of retries.
  

**Returns**:

    ExecutionResult: Result object containing success status, task ID,
  task status, and error message if any.
  

**Example**:

```python
from agentbay import AgentBay
from agentbay.session_params import CreateSessionParams

agent_bay = AgentBay(api_key="your_api_key")

def execute_agent_task():
    try:
        # Create a session with windows_latest image
        params = CreateSessionParams(image_id="windows_latest")
        result = agent_bay.create(params)
        if result.success:
            session = result.session

            # Execute a task using the Agent
            task_description = "Open notepad and type 'Hello World'"
            execution_result = session.agent.execute_task(
                task=task_description,
                max_try_times=20
            )

            if execution_result.success:
                print(f"Task completed successfully")
                print(f"Task status: {execution_result.task_status}")
                print(f"Task result: {execution_result.task_result}")
            else:
                print(f"Task failed: {execution_result.error_message}")

            session.delete()
    except Exception as e:
        print(f"Error: {e}")

execute_agent_task()
```

#### get\_task\_status

```python
def get_task_status(task_id: str) -> QueryResult
```

Get the status of the task with the given task ID.

**Arguments**:

    task_id: The ID of the task to query.
  

**Returns**:

    QueryResult: Result object containing success status, task status,
  task action, task product, and error message if any.
  

**Example**:

```python
from agentbay import AgentBay
from agentbay.session_params import CreateSessionParams

agent_bay = AgentBay(api_key="your_api_key")

def query_agent_task_status():
    try:
        # Create a session with windows_latest image
        params = CreateSessionParams(image_id="windows_latest")
        result = agent_bay.create(params)
        if result.success:
            session = result.session

            # First, execute a task asynchronously
            execution_result = session.agent.async_execute_task(
                "Open notepad"
            )

            if execution_result.success:
                task_id = execution_result.task_id

                # Get the status of the task
                status_result = session.agent.get_task_status(task_id)

                if status_result.success:
                    print(f"Task status: {status_result.task_status}")
                    print(f"Task action: {status_result.task_action}")
                    print(f"Task product: {status_result.task_product}")
                else:
                    print(f"Failed to get status: {status_result.error_message}")

            session.delete()
    except Exception as e:
        print(f"Error: {e}")

query_agent_task_status()
```

#### terminate\_task

```python
def terminate_task(task_id: str) -> ExecutionResult
```

Terminate a task with a specified task ID.

**Arguments**:

    task_id: The ID of the running task to terminate.
  

**Returns**:

    ExecutionResult: Result object containing success status, task ID,
  task status, and error message if any.
  

**Example**:

```python
from agentbay import AgentBay
from agentbay.session_params import CreateSessionParams

agent_bay = AgentBay(api_key="your_api_key")

def terminate_agent_task():
    try:
        # Create a session with windows_latest image
        params = CreateSessionParams(image_id="windows_latest")
        result = agent_bay.create(params)
        if result.success:
            session = result.session

            # First, execute a task asynchronously
            execution_result = session.agent.async_execute_task(
                "Search for Python tutorials online"
            )

            if execution_result.success:
                task_id = execution_result.task_id
                print(f"Task {task_id} started")

                # Terminate the running task
                terminate_result = session.agent.terminate_task(task_id)

                if terminate_result.success:
                    print(f"Task terminated successfully")
                    print(f"Task status: {terminate_result.task_status}")
                else:
                    print(f"Failed to terminate: {terminate_result.error_message}")

            session.delete()
    except Exception as e:
        print(f"Error: {e}")

terminate_agent_task()
```

## Related Resources

- [Session API Reference](../../common-features/basics/session.md)

---

*Documentation generated automatically from source code using pydoc-markdown.*
