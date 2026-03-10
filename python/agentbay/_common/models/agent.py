"""
Agent module data models.
"""

from .response import ApiResponse
from pydantic import BaseModel
from typing import TypeVar, Optional

Schema = TypeVar("Schema", bound=BaseModel)


class DefaultSchema(BaseModel):
    """Basic schema for agent output."""
    result: str


class AgentEvent:
    """
    Represents a streaming event from an Agent execution.

    Event types map directly to LLM output field names:
    - "reasoning": from LLM reasoning_content (model's internal reasoning/thinking)
    - "content": from LLM content (model's text output, intermediate analysis or final answer)
    - "tool_call": from LLM tool_calls (tool invocation request)
    - "tool_result": tool execution result
    - "error": execution error

    Attributes:
        type: Event type string.
        seq: Sequence number within the stream.
        round: Execution round number.
        content: Text content for reasoning/content events.
        tool_call_id: Identifier for the tool call (tool_call/tool_result events).
        tool_name: Name of the tool (tool_call/tool_result events).
        args: Tool call arguments dict (tool_call events).
        result: Tool execution result dict (tool_result events). The internal
            structure is agent-defined and not parsed by the SDK. Typical
            fields include ``isError`` (bool), ``output`` (str), and
            optionally ``screenshot`` (base64 str). The final task outcome
            is delivered via the ``ExecutionResult`` return value of
            ``execute_task_and_wait``.
        prompt: Prompt text for call_for_user tool_call events.
        error: Error information dict (error events).
    """

    def __init__(
        self,
        type: str = "",
        seq: int = 0,
        round: int = 0,
        content: str = "",
        tool_call_id: str = "",
        tool_name: str = "",
        args: Optional[dict] = None,
        result: Optional[dict] = None,
        prompt: str = "",
        error: Optional[dict] = None,
    ):
        self.type = type
        self.seq = seq
        self.round = round
        self.content = content
        self.tool_call_id = tool_call_id
        self.tool_name = tool_name
        self.args = args or {}
        self.result = result or {}
        self.prompt = prompt
        self.error = error or {}

    def __repr__(self) -> str:
        fields = [f"type={self.type!r}", f"seq={self.seq}", f"round={self.round}"]
        if self.content:
            fields.append(f"content={self.content!r}")
        if self.tool_name:
            fields.append(f"tool_name={self.tool_name!r}")
        return f"AgentEvent({', '.join(fields)})"

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
