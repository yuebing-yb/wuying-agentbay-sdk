"""
Agent module data models.
"""

from .response import ApiResponse
from pydantic import BaseModel
from typing import Any, Dict, Optional, TypeVar

Schema = TypeVar("Schema", bound=BaseModel)


class DefaultSchema(BaseModel):
    """Basic schema for agent output."""
    result: str


class AgentEvent:
    """
    Represents a single event emitted during Agent streaming execution.

    Depending on the event type, different fields are populated:
    - thought/response: content is set
    - tool_call: tool_call_id, tool_name, args are set
    - tool_result: tool_call_id, tool_name, result are set
    - error: error is set
    """

    def __init__(
        self,
        type: str = "",
        seq: int = 0,
        round: int = 0,
        content: str = "",
        tool_call_id: str = "",
        tool_name: str = "",
        args: Optional[Dict[str, Any]] = None,
        result: Optional[Dict[str, Any]] = None,
        error: Optional[Dict[str, Any]] = None,
    ):
        self.type = type
        self.seq = seq
        self.round = round
        self.content = content
        self.tool_call_id = tool_call_id
        self.tool_name = tool_name
        self.args = args if args is not None else {}
        self.result = result if result is not None else {}
        self.error = error if error is not None else {}

    def __repr__(self) -> str:
        parts = [f"type={self.type!r}", f"seq={self.seq}", f"round={self.round}"]
        if self.content:
            parts.append(f"content={self.content!r}")
        if self.tool_call_id:
            parts.append(f"tool_call_id={self.tool_call_id!r}")
        if self.tool_name:
            parts.append(f"tool_name={self.tool_name!r}")
        return f"AgentEvent({', '.join(parts)})"

    @classmethod
    def from_ws_data(cls, data: Dict[str, Any]) -> "AgentEvent":
        """Construct an AgentEvent from a WS event data dict."""
        event_type = data.get("eventType", "")
        return cls(
            type=event_type,
            seq=data.get("seq", 0),
            round=data.get("round", 0),
            content=data.get("content", ""),
            tool_call_id=data.get("toolCallId", ""),
            tool_name=data.get("toolName", ""),
            args=data.get("args") if isinstance(data.get("args"), dict) else {},
            result=data.get("result") if isinstance(data.get("result"), dict) else {},
            error=data.get("error") if isinstance(data.get("error"), dict) else {},
        )

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
        stream: list = None,
        error: str = "",
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
            stream (list, optional): Stream fragments array containing incremental updates.
            error (str, optional): Error description from the task response.
        """
        super().__init__(request_id)
        self.success = success
        self.error_message = error_message
        self.task_id = task_id
        self.task_status = task_status
        self.task_action = task_action
        self.task_product = task_product
        self.stream = stream if stream is not None else []
        self.error = error


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
