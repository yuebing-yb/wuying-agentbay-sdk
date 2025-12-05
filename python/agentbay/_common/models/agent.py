"""
Agent module data models.
"""

from .response import ApiResponse


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

