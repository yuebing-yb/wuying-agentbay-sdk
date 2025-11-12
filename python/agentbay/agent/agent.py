from agentbay.exceptions import AgentError, AgentBayError
from agentbay.api.base_service import BaseService
from agentbay.model import ApiResponse
from agentbay.logger import get_logger
import time, json

# Initialize logger for this module
_logger = get_logger("agent")


class QueryResult(ApiResponse):
    """Result of query operations."""

    def __init__(
        self,
        request_id: str = "",
        success: bool = False,
        error_message: str = "",
        task_id: str = "",
        task_status: str = "",
        task_action: str = "",
        task_product: str = "",
    ):
        """
        Initialize a QueryResult..

        Args:
            request_id (str, optional): Unique identifier for the API request.
            success (bool, optional): Whether the operation was successful.
            error_message (str, optional): Error message if the operation failed.
            task_id (str, optional): The id of the task.
            task_status (str, optional): The status of the task.
            task_action (str, optional): The current action of the task.
            task_product (str, optional): The product of the task.
        """
        super().__init__(request_id)
        self.success = success
        self.error_message = error_message
        self.task_id = task_id
        self.task_status = task_status
        self.task_action = task_action
        self.task_product = task_product


class ExecutionResult(ApiResponse):
    """Result of task execution."""

    def __init__(
        self,
        request_id: str = "",
        success: bool = False,
        error_message: str = "",
        task_id: str = "",
        task_status: str = "",
        task_result: str = "",
    ):
        """
        Initialize a ExecutionResult object.

        Args:
            request_id (str, optional): Unique identifier for the API request.
            success (bool, optional): Whether the execution was successful.
            error_message (str, optional): Error message if the execution failed.
        """
        super().__init__(request_id)
        self.success = success
        self.error_message = error_message
        self.task_id = task_id
        self.task_status = task_status
        self.task_result = task_result


class Agent(BaseService):
    """
    An Agent to manipulate applications to complete specific tasks.
    """

    def __init__(self, session):
        self.session = session

    def _handle_error(self, e):
        """
        Convert AgentBayError to AgentError for compatibility.

        Args:
            e (Exception): The exception to convert.

        Returns:
            AgentError: The converted exception.
        """
        if isinstance(e, AgentError):
            return e
        if isinstance(e, AgentBayError):
            return AgentError(str(e))
        return e

    def async_execute_task(self, task: str) -> ExecutionResult:
        """
        Execute a specific task described in human language asynchronously.

        This is an asynchronous interface that returns immediately with a task ID.
        Call get_task_status to check the task status. You can control the timeout
        of the task execution in your own code by setting the frequency of calling
        get_task_status and the max_try_times.

        Args:
            task: Task description in human language.

        Returns:
            ExecutionResult: Result object containing success status, task ID,
                task status, and error message if any.

        Example:
            ```python
            session = agent_bay.create().session
            result = session.agent.async_execute_task("Open Chrome browser")
            print(f"Task ID: {result.task_id}, Status: {result.task_status}")
            status = session.agent.get_task_status(result.task_id)
            print(f"Task status: {status.task_status}")
            session.delete()
            ```
        """
        try:
            args = {"task": task}
            result = self.session.call_mcp_tool("flux_execute_task", args)
            if result.success:
                content = json.loads(result.data)
                task_id = content.get("task_id", "")
                return ExecutionResult(
                    request_id=result.request_id,
                    success=True,
                    error_message="",
                    task_id=task_id,
                    task_status="running",
                )
            else:
                _logger.error("task execute failed")
                return ExecutionResult(
                    request_id=result.request_id,
                    success=False,
                    error_message=result.error_message or "Failed to execute task",
                    task_status="failed",
                    task_id="",
                )
        except AgentError as e:
            return ExecutionResult(request_id="", success=False, error_message=str(e))
        except Exception as e:
            return ExecutionResult(
                request_id="",
                success=False,
                error_message=f"Failed to execute: {e}",
                task_status="failed",
                task_id="",
            )

    def execute_task(self, task: str, max_try_times: int) -> ExecutionResult:
        """
        Execute a specific task described in human language synchronously.

        This is a synchronous interface that blocks until the task is completed or
        an error occurs, or timeout happens. The default polling interval is 3 seconds,
        so set a proper max_try_times according to your task complexity.

        Args:
            task: Task description in human language.
            max_try_times: Maximum number of retries.

        Returns:
            ExecutionResult: Result object containing success status, task ID,
                task status, and error message if any.

        Example:
            ```python
            session = agent_bay.create().session
            result = session.agent.execute_task("Open Chrome browser", max_try_times=20)
            print(f"Task result: {result.task_result}")
            session.delete()
            ```
        """
        try:
            args = {"task": task}
            result = self.session.call_mcp_tool("flux_execute_task", args)
            if result.success:
                content = json.loads(result.data)
                task_id = content.get("task_id", "")
                tried_time: int = 0
                while tried_time < max_try_times:
                    query = self.get_task_status(task_id)
                    if query.task_status == "finished":
                        return ExecutionResult(
                            request_id=result.request_id,
                            success=True,
                            error_message="",
                            task_id=task_id,
                            task_status=query.task_status,
                            task_result=query.task_product,
                        )
                    elif query.task_status == "failed":
                        return ExecutionResult(
                            request_id=result.request_id,
                            success=False,
                            error_message="Failed to execute task.",
                            task_id=task_id,
                            task_status=query.task_status,
                        )
                    elif query.task_status == "unsupported":
                        return ExecutionResult(
                            request_id=result.request_id,
                            success=False,
                            error_message="Unsuppported task.",
                            task_id=task_id,
                            task_status=query.task_status,
                        )
                    _logger.info(f"⏳ Task {task_id} running 🚀: {query.task_action}.")
                    # keep waiting unit timeout if the status is running
                    # task_status {running, finished, failed, unsupported}
                    time.sleep(3)
                    tried_time += 1
                _logger.warning("⚠️ task execution timeout!")
                return ExecutionResult(
                    request_id=result.request_id,
                    success=False,
                    error_message="Task timeout.",
                    task_id=task_id,
                    task_status="failed",
                    task_result="Task timeout.",
                )
            else:
                _logger.error("❌ Task execution failed")
                return ExecutionResult(
                    request_id=result.request_id,
                    success=False,
                    error_message=result.error_message or "Failed to execute task",
                    task_status="failed",
                    task_id="",
                    task_result="Task Failed",
                )
        except AgentError as e:
            return ExecutionResult(
                request_id="",
                success=False,
                error_message=str(e),
                task_status="failed",
                task_id="",
                task_result="Task Failed",
            )
        except Exception as e:
            return ExecutionResult(
                request_id="",
                success=False,
                error_message=f"Failed to execute: {e}",
                task_status="failed",
                task_id="",
                task_result="Task Failed",
            )

    def get_task_status(self, task_id: str) -> QueryResult:
        """
        Get the status of the task with the given task ID.

        Args:
            task_id: The ID of the task to query.

        Returns:
            QueryResult: Result object containing success status, task status,
                task action, task product, and error message if any.

        Example:
            ```python
            session = agent_bay.create().session
            result = session.agent.async_execute_task("Open Chrome browser")
            status = session.agent.get_task_status(result.task_id)
            print(f"Status: {status.task_status}, Action: {status.task_action}")
            session.delete()
            ```
        """
        try:
            args = {"task_id": task_id}
            result = self.session.call_mcp_tool("flux_get_task_status", args)
            if result.success:
                content = json.loads(result.data)
                return QueryResult(
                    success=True,
                    request_id=result.request_id,
                    error_message="",
                    task_id=content.get("task_id", task_id),
                    task_status=content.get("status", "finised"),
                    task_action=content.get("action", ""),
                    task_product=content.get("product", ""),
                )
            else:
                return QueryResult(
                    request_id=result.request_id,
                    success=False,
                    error_message=result.error_message or "Failed to terminate task",
                    task_id=task_id,
                    task_status="failed",
                )
        except AgentError as e:
            return QueryResult(
                request_id="",
                success=False,
                error_message=str(e),
                task_id=task_id,
                task_status="failed",
            )
        except Exception as e:
            return QueryResult(
                request_id="",
                success=False,
                error_message=f"Failed to get task status: {e}",
                task_id=task_id,
                task_status="failed",
            )

    def terminate_task(self, task_id: str) -> ExecutionResult:
        """
        Terminate a task with a specified task ID.

        Args:
            task_id: The ID of the running task to terminate.

        Returns:
            ExecutionResult: Result object containing success status, task ID,
                task status, and error message if any.

        Example:
            ```python
            session = agent_bay.create().session
            result = session.agent.async_execute_task("Open Chrome browser")
            terminate_result = session.agent.terminate_task(result.task_id)
            print(f"Terminated: {terminate_result.success}")
            session.delete()
            ```
        """
        _logger.info("Terminating task")
        try:
            args = {"task_id": task_id}

            result = self.session.call_mcp_tool("flux_terminate_task", args)
            if result.success:
                content = json.loads(result.data)
                task_id = content.get("task_id", task_id)
                return ExecutionResult(
                    request_id=result.request_id,
                    success=True,
                    error_message="",
                    task_id=task_id,
                    task_status=content.get("status", "finished"),
                )
            else:
                content = json.loads(result.data)
                return ExecutionResult(
                    request_id=result.request_id,
                    success=False,
                    error_message=result.error_message or "Failed to terminate task",
                    task_id=task_id,
                    task_status="failed",
                )
        except AgentError as e:
            return ExecutionResult(
                request_id=result.request_id,
                success=False,
                error_message=str(e),
                task_id=task_id,
                task_status="failed",
            )
        except Exception as e:
            return ExecutionResult(
                request_id="",
                success=False,
                error_message=f"Failed to terminate: {e}",
                task_id=task_id,
                task_status="failed",
            )
