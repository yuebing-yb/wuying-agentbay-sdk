import asyncio
import json
import sys
from collections.abc import Awaitable
from typing import TYPE_CHECKING, Any, Callable, Type, Optional, Union

from .._common.exceptions import AgentBayError, AgentError
from .._common.logger import get_logger
from .._common.models.agent import (
    AgentEvent,
    ExecutionResult,
    QueryResult,
    DefaultSchema,
    Schema,
)
from .._common.models import BrowserOption

from .base_service import AsyncBaseService

if TYPE_CHECKING:
    from .session import AsyncSession

_logger = get_logger("agent")

AgentEventCallback = Optional[Callable[[AgentEvent], None]]
AsyncAgentEventCallback = Optional[Callable[[AgentEvent], Union[Awaitable[str], str]]]


class _StreamContext:
    """Mutable state shared between WS event callbacks and TaskExecution.wait()."""
    __slots__ = ("final_content_parts", "last_error", "errors")

    def __init__(self):
        self.final_content_parts: list[str] = []
        self.last_error: Optional[dict] = None
        self.errors: list[Exception] = []


class TaskExecution:
    """Handle for a running task, returned by ``execute_task()``.

    If streaming callbacks were registered, events are dispatched in the
    background as soon as the WebSocket connection delivers them.  Call
    ``wait()`` to block until the task completes and retrieve the final
    ``ExecutionResult``.

    Attributes:
        task_id: The identifier of the running task (empty when using
            the WebSocket streaming path, since the task is managed
            by the server stream).
    """

    def __init__(
        self,
        task_id: str = "",
        *,
        _ws_handle: Optional[Any] = None,
        _context: Optional[_StreamContext] = None,
        _agent: Optional[Any] = None,
        _result: Optional[ExecutionResult] = None,
        _request_id: str = "",
    ):
        self.task_id = task_id
        self._ws_handle = _ws_handle
        self._context = _context
        self._agent = _agent
        self._result = _result
        self._request_id = _request_id

    async def wait(self, timeout: int = 300) -> ExecutionResult:
        """Block until the task completes and return the final result.

        Args:
            timeout: Maximum seconds to wait. Default 300.

        Returns:
            ExecutionResult with the task outcome.
        """
        if self._result is not None:
            return self._result
        if self._ws_handle is not None:
            return await self._wait_ws(timeout)
        elif self._agent is not None:
            return await self._wait_polling(timeout)
        else:
            raise RuntimeError("TaskExecution is not properly initialized")

    async def _wait_ws(self, timeout: int) -> ExecutionResult:
        ctx = self._context
        ws_request_id = getattr(self._ws_handle, "invocation_id", "") or ""
        try:
            end_data = await self._ws_handle.wait_end_with_timeout(timeout)
        except TimeoutError:
            try:
                await self._ws_handle.cancel()
            except Exception:
                pass
            return ExecutionResult(
                request_id=ws_request_id,
                success=False,
                error_message=f"Task execution timed out after {timeout} seconds.",
                task_status="failed",
                task_result="".join(ctx.final_content_parts) or "Task execution timed out.",
            )

        if ctx.errors:
            return ExecutionResult(
                request_id=ws_request_id,
                success=False,
                error_message=str(ctx.errors[0]),
                task_status="failed",
                task_result="".join(ctx.final_content_parts),
            )

        if ctx.last_error:
            return ExecutionResult(
                request_id=ws_request_id,
                success=False,
                error_message=str(ctx.last_error),
                task_status="failed",
                task_result="".join(ctx.final_content_parts),
            )

        status = end_data.get("status", "finished") if end_data else "finished"
        task_result = end_data.get("taskResult", "") if end_data else ""
        if not task_result:
            task_result = "".join(ctx.final_content_parts)

        return ExecutionResult(
            request_id=ws_request_id,
            success=(status == "finished"),
            error_message="" if status == "finished" else f"Task ended with status: {status}",
            task_status=status,
            task_result=task_result,
        )

    async def _wait_polling(self, timeout: int) -> ExecutionResult:
        agent = self._agent
        task_id = self.task_id
        poll_interval = 3
        max_poll_attempts = timeout // poll_interval

        last_request_id = self._request_id
        tried_time = 0
        processed_timestamps: set = set()
        last_query = None

        while tried_time < max_poll_attempts:
            query = await agent.get_task_status(task_id)
            if query.stream:
                last_query = query

            if query.stream:
                for stream_item in query.stream:
                    if isinstance(stream_item, dict):
                        timestamp = stream_item.get("timestamp_ms")
                        if timestamp is not None and timestamp not in processed_timestamps:
                            processed_timestamps.add(timestamp)
                            content = stream_item.get("content", "")
                            reasoning = stream_item.get("reasoning", "")
                            if content:
                                sys.stdout.write(content)
                                sys.stdout.flush()
                            if reasoning:
                                _logger.debug(f"💭 {reasoning}")

            if query.error:
                _logger.warning(f"⚠️ Task error: {query.error}")

            if query.task_status == "completed":
                return ExecutionResult(
                    request_id=last_request_id,
                    success=True,
                    task_id=task_id,
                    task_status=query.task_status,
                    task_result=query.task_product,
                )
            elif query.task_status in ("failed", "cancelled", "unsupported"):
                error_msg = query.error or query.error_message or f"Task {query.task_status}."
                return ExecutionResult(
                    request_id=query.request_id,
                    success=False,
                    error_message=error_msg,
                    task_id=task_id,
                    task_status=query.task_status,
                )

            _logger.info(f"⏳ Task {task_id} running 🚀: {query.task_action}.")
            await asyncio.sleep(poll_interval)
            tried_time += 1

        _logger.warning("⚠️ task execution timeout!")
        try:
            terminate_result = await agent.terminate_task(task_id)
            if terminate_result.success:
                _logger.info(f"✅ Terminate request sent for task {task_id} after timeout")
            else:
                _logger.warning(f"⚠️ Failed to terminate task {task_id}: {terminate_result.error_message}")
        except Exception as e:
            _logger.warning(f"⚠️ Exception while terminating task {task_id}: {e}")

        _logger.info(f"⏳ Waiting for task {task_id} to be fully terminated...")
        terminate_tried = 0
        while terminate_tried < 30:
            try:
                status_query = await agent.get_task_status(task_id)
                if not status_query.success:
                    error_msg = status_query.error_message or ""
                    if error_msg.startswith("Task not found or already finished"):
                        _logger.info(f"✅ Task {task_id} confirmed terminated")
                        break
                await asyncio.sleep(1)
                terminate_tried += 1
            except Exception:
                await asyncio.sleep(1)
                terminate_tried += 1

        task_result_parts = [f"Task execution timed out after {timeout} seconds."]
        if last_query:
            if last_query.stream:
                stream_parts = []
                for item in last_query.stream:
                    if isinstance(item, dict):
                        c = item.get("content", "")
                        if c:
                            stream_parts.append(c)
                if stream_parts:
                    task_result_parts.append(f"Last task status output: {''.join(stream_parts)}")
            if last_query.task_action:
                task_result_parts.append(f"Last action: {last_query.task_action}")
            if last_query.task_product:
                task_result_parts.append(f"Last result: {last_query.task_product}")
            if last_query.error:
                task_result_parts.append(f"Last error: {last_query.error}")
            if last_query.task_status:
                task_result_parts.append(f"Last status: {last_query.task_status}")

        return ExecutionResult(
            request_id=last_request_id,
            success=False,
            error_message=f"Task execution timed out after {timeout} seconds. Task ID: {task_id}.",
            task_id=task_id,
            task_status="failed",
            task_result=" | ".join(task_result_parts),
        )


class AsyncAgent(AsyncBaseService):
    """
    An Agent to manipulate applications to complete specific tasks.

    > **⚠️ Note**: Currently, for agent services (including ComputerUseAgent, BrowserUseAgent, and MobileUseAgent), we do not provide services for overseas users registered with **alibabacloud.com**.
    """

    def __init__(self, session: "AsyncSession"):
        super().__init__(session)
        self.browser = self.Browser(session)
        self.computer = self.Computer(session)
        self.mobile = self.Mobile(session)

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

    class _BaseTaskAgent(AsyncBaseService):
        """Base class for task execution agents."""

        def __init__(self, session: "AsyncSession", tool_prefix: str):
            """
            Initialize base task agent.

            Args:
                session: The session object.
                tool_prefix: Prefix for MCP tool names (e.g., "flux" or "browser_use").
            """
            super().__init__(session)
            self.tool_prefix = tool_prefix

        def _get_tool_name(self, action: str) -> str:
            """Get the full MCP tool name based on prefix and action."""
            tool_map = {
                "execute": "execute_task",
                "get_status": "get_task_status",
                "terminate": "terminate_task",
            }
            base_name = tool_map.get(action, action)
            if self.tool_prefix:
                return f"{self.tool_prefix}_{base_name}"
            return base_name

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

        async def execute_task(self, task: str) -> ExecutionResult:
            """
            Execute a task in human language without waiting for completion (non-blocking).

            This is a fire-and-return interface that immediately provides a task ID.
            Call get_task_status to check the task status. You can control the timeout
            of the task execution in your own code by setting the frequency of calling
            get_task_status.

            Args:
                task: Task description in human language.

            Returns:
                ExecutionResult: Result object containing success status, task ID,
                    task status, and error message if any.

            Example:
                ```python
                session_result = await agent_bay.create()
                session = session_result.session
                result = await session.agent.computer.execute_task("Open Chrome browser")
                print(f"Task ID: {result.task_id}, Status: {result.task_status}")
                status = await session.agent.computer.get_task_status(result.task_id)
                print(f"Task status: {status.task_status}")
                await session.delete()
                ```
            """
            try:
                args = {"task": task}
                tool_name = self._get_tool_name("execute")
                result = await self.session.call_mcp_tool(
                    tool_name,
                    args,
                )
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
                handled_error = self._handle_error(e)
                return ExecutionResult(
                    request_id="", success=False, error_message=str(handled_error)
                )
            except Exception as e:
                handled_error = self._handle_error(AgentBayError(str(e)))
                return ExecutionResult(
                    request_id="",
                    success=False,
                    error_message=f"Failed to execute: {handled_error}",
                    task_status="failed",
                    task_id="",
                )

        def _has_streaming_params(
            self,
            on_reasoning: AgentEventCallback = None,
            on_content: AgentEventCallback = None,
            on_tool_call: AgentEventCallback = None,
            on_tool_result: AgentEventCallback = None,
            on_error: AgentEventCallback = None,
            on_call_for_user: AsyncAgentEventCallback = None,
        ) -> bool:
            return any([on_reasoning, on_content, on_tool_call, on_tool_result, on_error, on_call_for_user])

        def _resolve_agent_target(self) -> str:
            """Resolve the WS target for this agent from MCP tools list."""
            execute_tool_name = self._get_tool_name("execute")
            for tool in getattr(self.session, "mcpTools", []) or []:
                try:
                    if getattr(tool, "name", "") == execute_tool_name and getattr(tool, "server", ""):
                        return tool.server
                except Exception:
                    continue
            if self.tool_prefix == "browser_use":
                return "wuying_browseruse"
            elif self.tool_prefix == "flux":
                return "wuying_computer_agent"
            else:
                return "wuying_mobile_agent"

        async def _start_task_stream_ws(
            self,
            task_params: dict,
            on_reasoning: AgentEventCallback = None,
            on_content: AgentEventCallback = None,
            on_tool_call: AgentEventCallback = None,
            on_tool_result: AgentEventCallback = None,
            on_error: AgentEventCallback = None,
            on_call_for_user: AsyncAgentEventCallback = None,
        ) -> tuple[Any, _StreamContext]:
            """Set up WS streaming for a task (non-blocking).

            Returns (ws_handle, stream_context). Events are dispatched
            to the provided callbacks in the background. Use the returned
            handle with ``TaskExecution`` to wait for the final result.
            """
            target = self._resolve_agent_target()
            ws_client = await self.session._get_ws_client()

            ctx = _StreamContext()
            _ws_handle_ref: list[Any] = [None]

            def _dispatch_event(event: AgentEvent) -> None:
                try:
                    cb = {
                        "reasoning": on_reasoning,
                        "content": on_content,
                        "tool_call": on_tool_call,
                        "tool_result": on_tool_result,
                        "error": on_error,
                    }.get(event.type)
                    if cb:
                        cb(event)
                except Exception as ex:
                    _logger.warning(f"on_{event.type} callback error: {ex}")

            async def _handle_call_for_user(event: AgentEvent) -> None:
                response = ""
                if on_call_for_user:
                    try:
                        result = on_call_for_user(event)
                        if asyncio.iscoroutine(result) or asyncio.isfuture(result):
                            response = await result
                        else:
                            response = result
                    except Exception as ex:
                        _logger.warning(f"on_call_for_user callback error: {ex}")
                        response = ""
                else:
                    _logger.warning("Received call_for_user but no on_call_for_user callback is set, sending empty response")
                if _ws_handle_ref[0] is not None:
                    try:
                        await _ws_handle_ref[0].write({
                            "method": "resume_task",
                            "params": {
                                "toolCallId": event.tool_call_id,
                                "response": response or "",
                            },
                        })
                    except Exception as ex:
                        _logger.warning(f"Failed to send resume_task: {ex}")

            def _on_event(invocation_id: str, data: dict[str, Any]) -> None:
                event_type = data.get("eventType", "")
                seq = data.get("seq", 0)
                round_num = data.get("round", 0)

                if event_type == "reasoning":
                    event = AgentEvent(
                        type="reasoning", seq=seq, round=round_num,
                        content=data.get("content", ""),
                    )
                    _dispatch_event(event)
                elif event_type == "content":
                    content_text = data.get("content", "")
                    ctx.final_content_parts.append(content_text)
                    event = AgentEvent(
                        type="content", seq=seq, round=round_num,
                        content=content_text,
                    )
                    _dispatch_event(event)
                elif event_type == "tool_call":
                    args = data.get("args", {})
                    tool_name = data.get("toolName", "")
                    event = AgentEvent(
                        type="tool_call", seq=seq, round=round_num,
                        tool_call_id=data.get("toolCallId", ""),
                        tool_name=tool_name,
                        args=args,
                        prompt=args.get("prompt", "") if tool_name == "call_for_user" else "",
                    )
                    _dispatch_event(event)
                    if tool_name == "call_for_user":
                        asyncio.create_task(_handle_call_for_user(event))
                elif event_type == "tool_result":
                    event = AgentEvent(
                        type="tool_result", seq=seq, round=round_num,
                        tool_call_id=data.get("toolCallId", ""),
                        tool_name=data.get("toolName", ""),
                        result=data.get("result", {}),
                    )
                    _dispatch_event(event)
                elif event_type == "error":
                    ctx.last_error = data.get("error", data)
                    event = AgentEvent(
                        type="error", seq=seq, round=round_num,
                        error=ctx.last_error,
                    )
                    _dispatch_event(event)

            def _on_error_ws(invocation_id: str, err: Exception) -> None:
                ctx.errors.append(err)

            handle = await ws_client.call_stream(
                target=target,
                data={
                    "method": "exec_task",
                    "params": task_params,
                },
                on_event=_on_event,
                on_end=None,
                on_error=_on_error_ws,
            )
            _ws_handle_ref[0] = handle

            return handle, ctx

        async def _execute_task_stream_ws(
            self,
            task_params: dict,
            timeout: int,
            on_reasoning: AgentEventCallback = None,
            on_content: AgentEventCallback = None,
            on_tool_call: AgentEventCallback = None,
            on_tool_result: AgentEventCallback = None,
            on_error: AgentEventCallback = None,
            on_call_for_user: AsyncAgentEventCallback = None,
        ) -> ExecutionResult:
            """Execute a task via WS streaming channel (blocking convenience wrapper)."""
            ws_handle, ctx = await self._start_task_stream_ws(
                task_params=task_params,
                on_reasoning=on_reasoning,
                on_content=on_content,
                on_tool_call=on_tool_call,
                on_tool_result=on_tool_result,
                on_error=on_error,
                on_call_for_user=on_call_for_user,
            )
            execution = TaskExecution(
                task_id="", _ws_handle=ws_handle, _context=ctx,
            )
            return await execution.wait(timeout=timeout)

        async def execute_task_and_wait(
            self,
            task: str,
            timeout: int,
        ) -> ExecutionResult:
            """
            Execute a specific task described in human language synchronously.

            This is a synchronous interface that blocks until the task is completed or
            an error occurs, or timeout happens. The default polling interval is 3 seconds.

            Args:
                task: Task description in human language.
                timeout: Maximum time to wait for task completion in seconds.

            Returns:
                ExecutionResult: Result object containing success status, task ID,
                    task status, and error message if any.

            Example:
                ```python
                session_result = await agent_bay.create()
                session = session_result.session
                result = await session.agent.computer.execute_task_and_wait("Open Chrome browser", timeout=60)
                print(f"Task result: {result.task_result}")
                await session.delete()
                ```
            """
            poll_interval = 3
            max_poll_attempts = timeout // poll_interval

            try:
                args = {"task": task}
                tool_name = self._get_tool_name("execute")
                result = await self.session.call_mcp_tool(
                    tool_name,
                    args,
                )
                if result.success:
                    content = json.loads(result.data)
                    task_id = content.get("task_id", "")
                    tried_time: int = 0
                    while tried_time < max_poll_attempts:
                        query = await self.get_task_status(task_id)
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
                            error_msg = query.error_message or "Failed to execute task."
                            return ExecutionResult(
                                request_id=query.request_id,
                                success=False,
                                error_message="Failed to execute task.",
                                task_id=task_id,
                                task_status=query.task_status,
                            )
                        elif query.task_status == "unsupported":
                            error_msg = query.error_message or "Unsupported task."
                            return ExecutionResult(
                                request_id=query.request_id,
                                success=False,
                                error_message=error_msg,
                                task_id=task_id,
                                task_status=query.task_status,
                            )
                        _logger.info(
                            f"⏳ Task {task_id} running 🚀: {query.task_action}."
                        )
                        await asyncio.sleep(poll_interval)
                        tried_time += 1
                    _logger.warning("⚠️ task execution timeout!")
                    try:
                        terminate_result = await self.terminate_task(task_id)
                        if terminate_result.success:
                            _logger.info(f"✅ Task {task_id} terminated successfully after timeout")
                        else:
                            _logger.warning(f"⚠️ Failed to terminate task {task_id} after timeout: {terminate_result.error_message}")
                    except Exception as e:
                        _logger.warning(f"⚠️ Exception while terminating task {task_id} after timeout: {e}")
                    timeout_error_msg = f"Task execution timed out after {timeout} seconds. Task ID: {task_id}. Polled {tried_time} times (max: {max_poll_attempts})."
                    return ExecutionResult(
                        request_id=result.request_id,
                        success=False,
                        error_message=timeout_error_msg,
                        task_id=task_id,
                        task_status="failed",
                        task_result=f"Task execution timed out after {timeout} seconds.",
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
                handled_error = self._handle_error(e)
                return ExecutionResult(
                    request_id="",
                    success=False,
                    error_message=str(handled_error),
                    task_status="failed",
                    task_id="",
                    task_result="Task Failed",
                )
            except Exception as e:
                handled_error = self._handle_error(AgentBayError(str(e)))
                return ExecutionResult(
                    request_id="",
                    success=False,
                    error_message=f"Failed to execute: {handled_error}",
                    task_status="failed",
                    task_id="",
                    task_result="Task Failed",
                )

        async def get_task_status(self, task_id: str) -> QueryResult:
            """
            Get the status of the task with the given task ID.

            Args:
                task_id: The ID of the task to query.

            Returns:
                QueryResult: Result object containing success status, task status,
                    task action, task product, and error message if any.

            Example:
                ```python
                session_result = await agent_bay.create()
                session = session_result.session
                result = await session.agent.computer.execute_task("Query the weather in Shanghai with Baidu")
                status = await session.agent.computer.get_task_status(result.task_id)
                print(f"Status: {status.task_status}, Action: {status.task_action}")
                await session.delete()
                ```
            """
            try:
                args = {"task_id": task_id}
                tool_name = self._get_tool_name("get_status")
                result = await self.session.call_mcp_tool(
                    tool_name,
                    args,
                )
                if result.success:
                    content = json.loads(result.data)
                    return QueryResult(
                        success=True,
                        request_id=result.request_id,
                        error_message="",
                        task_id=content.get("task_id", task_id),
                        task_status=content.get("status", "finished"),
                        task_action=content.get("action", ""),
                        task_product=content.get("product", ""),
                    )
                else:
                    return QueryResult(
                        request_id=result.request_id,
                        success=False,
                        error_message=result.error_message
                        or "Failed to get task status",
                        task_id=task_id,
                        task_status="failed",
                    )
            except AgentError as e:
                handled_error = self._handle_error(e)
                return QueryResult(
                    request_id="",
                    success=False,
                    error_message=str(handled_error),
                    task_id=task_id,
                    task_status="failed",
                )
            except Exception as e:
                handled_error = self._handle_error(AgentBayError(str(e)))
                return QueryResult(
                    request_id="",
                    success=False,
                    error_message=f"Failed to get task status: {handled_error}",
                    task_id=task_id,
                    task_status="failed",
                )

        async def terminate_task(self, task_id: str) -> ExecutionResult:
            """
            Terminate a task with a specified task ID.

            Args:
                task_id: The ID of the running task to terminate.

            Returns:
                ExecutionResult: Result object containing success status, task ID,
                    task status, and error message if any.

            Example:
                ```python
                session_result = await agent_bay.create()
                session = session_result.session
                result = await session.agent.computer.execute_task("Query the weather in Shanghai with Baidu")
                terminate_result = await session.agent.computer.terminate_task(result.task_id)
                print(f"Terminated: {terminate_result.success}")
                await session.delete()
                ```
            """
            _logger.info("Terminating task")
            try:
                args = {"task_id": task_id}
                tool_name = self._get_tool_name("terminate")
                result = await self.session.call_mcp_tool(
                    tool_name,
                    args,
                )
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
                    content = json.loads(result.data) if result.data else {}
                    return ExecutionResult(
                        request_id=result.request_id,
                        success=False,
                        error_message=result.error_message
                        or "Failed to terminate task",
                        task_id=task_id,
                        task_status="failed",
                    )
            except AgentError as e:
                handled_error = self._handle_error(e)
                return ExecutionResult(
                    request_id=result.request_id if "result" in locals() else "",
                    success=False,
                    error_message=str(handled_error),
                    task_id=task_id,
                    task_status="failed",
                )
            except Exception as e:
                handled_error = self._handle_error(AgentBayError(str(e)))
                return ExecutionResult(
                    request_id="",
                    success=False,
                    error_message=f"Failed to terminate: {handled_error}",
                    task_id=task_id,
                    task_status="failed",
                )

    class Computer(_BaseTaskAgent):
        """
        An Agent to perform tasks on the computer.

        > **⚠️ Note**: Currently, for agent services (including ComputerUseAgent, BrowserUseAgent, and MobileUseAgent), we do not provide services for overseas users registered with **alibabacloud.com**.
        """

        def __init__(self, session: "AsyncSession"):
            super().__init__(session, tool_prefix="flux")

    class Browser(_BaseTaskAgent):
        """

        > **⚠️ Note**: Currently, for agent services (including ComputerUseAgent, BrowserUseAgent, and MobileUseAgent), we do not provide services for overseas users registered with **alibabacloud.com**.
        """

        def __init__(self, session: "AsyncSession"):
            super().__init__(session, tool_prefix="browser_use")
            self.initialized = False

        async def initialize(self, option:Optional[BrowserOption]=None) -> bool:
            """
            Initialize the browser on which the agent performs tasks.
            You are supposed to call this API before executeTask is called, but it's not optional.
            If you want perform a hybrid usage of browser, you must call this API before executeTask is called.
            Returns:
                bool: True if the browser is successfully initialized, False otherwise.
            """
            if self.initialized:
                return True

            if option is None:
                option = BrowserOption()
            success = await self.session.browser.initialize(option)
            self.initialized = success
            return success


        async def execute_task(
            self,
            task: str,
            use_vision: bool = False,
            output_schema: Type[Schema] = None,
            full_page_screenshot: Optional[bool] = False,
        ) -> ExecutionResult:
            """
            Execute a task described in human language on a browser without waiting for completion (non-blocking).

            This is a fire-and-return interface that immediately provides a task ID.
            Call get_task_status to check the task status. You can control the timeout
            of the task execution in your own code by setting the frequency of calling
            get_task_status.

            Args:
                task: Task description in human language.
                use_vision: Whether to use vision to performe the task.
                output_schema: The schema of the structured output.
                full_page_screenshot: Whether to take a full page screenshot. This only works when use_vision is true.
                When use_vision is enabled, we need to provide a screenshot of the webpage to the LLM for grounding. There are two ways of screenshot:
                1. Full-page screenshot: Captures the entire webpage content, including parts not currently visible in the viewport.  
                2. Viewport screenshot: Captures only the currently visible portion of the webpage.
                The first approach delivers all information to the LLM in one go, which can improve task success rates in certain information extraction scenarios. However, it also results in higher token consumption and increases the LLM's processing time.
                Therefore, we would like to give you the choice—you can decide whether to enable full-page screenshot based on your actual needs.
            Returns:
                ExecutionResult: Result object containing success status, task ID,
                    task status, and error message if any.

            Example:
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
            """
            if self.initialized == False:
                _logger.info("Browser is not initialized. Initialize browser first...")
                success = await self.initialize()
                if not success:
                    return ExecutionResult(
                        request_id="",
                        success=False,
                        error_message="Failed to initialize browser",
                        task_status="failed",
                        task_id="",
                    )
            try:
                args = {
                    "task": task,
                    "use_vision": use_vision,
                    "full_page_screenshot": full_page_screenshot,
                }
                if output_schema:
                    args["output_schema"] = json.dumps(
                        output_schema.model_json_schema()
                    )
                else:
                    args["output_schema"] = json.dumps(
                        DefaultSchema.model_json_schema()
                    )

                tool_name = self._get_tool_name("execute")
                result = await self.session.call_mcp_tool(
                    tool_name,
                    args,
                )
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
                handled_error = self._handle_error(e)
                return ExecutionResult(
                    request_id="", success=False, error_message=str(handled_error)
                )
            except Exception as e:
                handled_error = self._handle_error(AgentBayError(str(e)))
                return ExecutionResult(
                    request_id="",
                    success=False,
                    error_message=f"Failed to execute: {handled_error}",
                    task_status="failed",
                    task_id="",
                )

        async def execute_task_and_wait(
            self,
            task: str,
            timeout: int,
            use_vision: bool = False,
            output_schema: Type[Schema] = None,
            full_page_screenshot: Optional[bool] = False,
        ) -> ExecutionResult:
            """
            Execute a task described in human language on a browser synchronously.

            This is a synchronous interface that blocks until the task is completed or
            an error occurs, or timeout happens. The default polling interval is 3 seconds.

            Args:
                task: Task description in human language.
                timeout: Maximum time to wait for task completion in seconds.
                use_vision: Whether to use vision to perform the task.
                output_schema: The schema of the structured output.
                full_page_screenshot: Whether to take a full page screenshot.

            Returns:
                ExecutionResult: Result object containing success status, task ID,
                    task status, and error message if any.

            Example:
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
            """
            if self.initialized == False:
                _logger.info("Browser is not initialized. Initialize browser first...")
                success = await self.initialize()
                if not success:
                    return ExecutionResult(
                        request_id="",
                        success=False,
                        error_message="Failed to initialize browser",
                        task_status="failed",
                        task_id="",
                    )

            poll_interval = 3
            max_poll_attempts = timeout // poll_interval

            try:
                args = {
                    "task": task,
                    "use_vision": use_vision,
                    "full_page_screenshot": full_page_screenshot,
                }
                if output_schema:
                    args["output_schema"] = json.dumps(
                        output_schema.model_json_schema()
                    )
                else:
                    args["output_schema"] = json.dumps(
                        DefaultSchema.model_json_schema()
                    )

                tool_name = self._get_tool_name("execute")
                result = await self.session.call_mcp_tool(
                    tool_name,
                    args,
                )
                if result.success:
                    content = json.loads(result.data)
                    task_id = content.get("task_id", "")
                    tried_time: int = 0
                    while tried_time < max_poll_attempts:
                        query = await self.get_task_status(task_id)
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
                            error_msg = query.error_message or "Failed to execute task."
                            return ExecutionResult(
                                request_id=query.request_id,
                                success=False,
                                error_message="Failed to execute task.",
                                task_id=task_id,
                                task_status=query.task_status,
                            )
                        elif query.task_status == "unsupported":
                            error_msg = query.error_message or "Unsupported task."
                            return ExecutionResult(
                                request_id=query.request_id,
                                success=False,
                                error_message=error_msg,
                                task_id=task_id,
                                task_status=query.task_status,
                            )
                        _logger.info(
                            f"⏳ Task {task_id} running 🚀: {query.task_action}."
                        )
                        await asyncio.sleep(poll_interval)
                        tried_time += 1
                    _logger.warning("⚠️ task execution timeout!")
                    # Automatically terminate the task on timeout
                    try:
                        terminate_result = await self.terminate_task(task_id)
                        if terminate_result.success:
                            _logger.info(
                                f"✅ Task {task_id} terminated successfully after timeout"
                            )
                        else:
                            _logger.warning(
                                f"⚠️ Failed to terminate task {task_id} after timeout: {terminate_result.error_message}"
                            )
                    except Exception as e:
                        _logger.warning(
                            f"⚠️ Exception while terminating task {task_id} after timeout: {e}"
                        )
                    timeout_error_msg = f"Task execution timed out after {timeout} seconds. Task ID: {task_id}. Polled {tried_time} times (max: {max_poll_attempts})."
                    return ExecutionResult(
                        request_id=result.request_id,
                        success=False,
                        error_message=timeout_error_msg,
                        task_id=task_id,
                        task_status="failed",
                        task_result=f"Task execution timed out after {timeout} seconds.",
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
                handled_error = self._handle_error(e)
                return ExecutionResult(
                    request_id="",
                    success=False,
                    error_message=str(handled_error),
                    task_status="failed",
                    task_id="",
                    task_result="Task Failed",
                )
            except Exception as e:
                handled_error = self._handle_error(AgentBayError(str(e)))
                return ExecutionResult(
                    request_id="",
                    success=False,
                    error_message=f"Failed to execute: {handled_error}",
                    task_status="failed",
                    task_id="",
                    task_result="Task Failed",
                )

    class Mobile(_BaseTaskAgent):
        """
        An Agent to perform tasks on mobile devices.

        > **⚠️ Note**: Currently, for agent services (including ComputerUseAgent, BrowserUseAgent, and MobileUseAgent), we do not provide services for overseas users registered with **alibabacloud.com**.
        """

        def __init__(self, session: "AsyncSession"):
            super().__init__(session, tool_prefix="")

        async def execute_task(
            self,
            task: str,
            max_steps: int = 50,
            on_reasoning: AgentEventCallback = None,
            on_content: AgentEventCallback = None,
            on_tool_call: AgentEventCallback = None,
            on_tool_result: AgentEventCallback = None,
            on_error: AgentEventCallback = None,
            on_call_for_user: AsyncAgentEventCallback = None,
        ) -> TaskExecution:
            """
            Execute a task in human language (non-blocking).

            Returns a ``TaskExecution`` handle immediately. Call
            ``execution.wait(timeout)`` to block until the task completes.

            When any ``on_*`` callback is provided, a WebSocket connection is
            established and streaming events are dispatched in the background.

            Args:
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

            Returns:
                TaskExecution: Handle for the running task.

            Example:
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
            """
            task_params = {
                "task": task,
                "max_steps": max_steps,
            }

            if self._has_streaming_params(
                on_reasoning, on_content, on_tool_call,
                on_tool_result, on_error, on_call_for_user,
            ):
                ws_handle, ctx = await self._start_task_stream_ws(
                    task_params=task_params,
                    on_reasoning=on_reasoning,
                    on_content=on_content,
                    on_tool_call=on_tool_call,
                    on_tool_result=on_tool_result,
                    on_error=on_error,
                    on_call_for_user=on_call_for_user,
                )
                return TaskExecution(
                    task_id="", _ws_handle=ws_handle, _context=ctx,
                )
            else:
                tool_name = self._get_tool_name("execute")
                result = await self.session.call_mcp_tool(
                    tool_name, task_params,
                )
                if result.success:
                    try:
                        content = json.loads(result.data)
                    except (json.JSONDecodeError, TypeError, ValueError):
                        # Backend executed the task synchronously and returned
                        # the result as plain text instead of JSON with taskId.
                        return TaskExecution(
                            task_id="",
                            _result=ExecutionResult(
                                request_id=result.request_id,
                                success=True,
                                task_status="completed",
                                task_result=result.data or "",
                            ),
                        )
                    task_id = content.get("taskId") or content.get("task_id", "")
                    if not task_id:
                        return TaskExecution(
                            task_id="",
                            _result=ExecutionResult(
                                request_id=result.request_id,
                                success=True,
                                task_status="completed",
                                task_result=result.data or "",
                            ),
                        )
                    return TaskExecution(task_id=task_id, _agent=self, _request_id=result.request_id)
                else:
                    error_message = result.error_message or "Failed to execute task"
                    _logger.error(f"Task execution failed: {error_message}")
                    raise AgentError(error_message)

        async def execute_task_and_wait(
            self,
            task: str,
            timeout: int,
            max_steps: int = 50,
            on_reasoning: AgentEventCallback = None,
            on_content: AgentEventCallback = None,
            on_tool_call: AgentEventCallback = None,
            on_tool_result: AgentEventCallback = None,
            on_error: AgentEventCallback = None,
            on_call_for_user: AsyncAgentEventCallback = None,
        ) -> ExecutionResult:
            """
            Execute a task and wait for completion (blocking convenience wrapper).

            Equivalent to ``execute_task(...) + execution.wait(timeout)``.

            When any ``on_*`` callback is provided, the method uses the WebSocket
            streaming channel for real-time event delivery instead of HTTP polling.

            Args:
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

            Returns:
                ExecutionResult: Result object containing success status, task ID,
                    task status, and error message if any.

            Example:
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
            """
            try:
                execution = await self.execute_task(
                    task,
                    max_steps=max_steps,
                    on_reasoning=on_reasoning,
                    on_content=on_content,
                    on_tool_call=on_tool_call,
                    on_tool_result=on_tool_result,
                    on_error=on_error,
                    on_call_for_user=on_call_for_user,
                )
            except (AgentError, AgentBayError) as e:
                return ExecutionResult(
                    success=False,
                    error_message=str(e),
                    task_status="failed",
                    task_result="Task Failed",
                )
            except Exception as e:
                return ExecutionResult(
                    success=False,
                    error_message=f"Failed to execute: {e}",
                    task_status="failed",
                    task_result="Task Failed",
                )

            return await execution.wait(timeout=timeout)

        async def get_task_status(self, task_id: str) -> QueryResult:
            try:
                args = {"task_id": task_id}
                tool_name = self._get_tool_name("get_status")
                result = await self.session.call_mcp_tool(
                    tool_name,
                    args,
                )
                if result.success:
                    content = json.loads(result.data)
                    content_task_id = content.get("taskId") or content.get("task_id", task_id)
                    task_product = content.get("result") or content.get("product", "")

                    stream = content.get("stream", [])
                    if not isinstance(stream, list):
                        _logger.warning(f"⚠️ Stream is not a list (type: {type(stream)}), converting to empty list")
                        stream = []

                    error = content.get("error", "")

                    return QueryResult(
                        success=True,
                        request_id=result.request_id,
                        error_message="",
                        task_id=content_task_id,
                        task_status=content.get("status", "completed"),
                        task_action=content.get("action", ""),
                        task_product=task_product,
                        stream=stream,
                        error=error,
                    )
                else:
                    return QueryResult(
                        request_id=result.request_id,
                        success=False,
                        error_message=result.error_message
                        or "Failed to get task status",
                        task_id=task_id,
                        task_status="failed",
                    )
            except AgentError as e:
                handled_error = self._handle_error(e)
                return QueryResult(
                    request_id="",
                    success=False,
                    error_message=str(handled_error),
                    task_id=task_id,
                    task_status="failed",
                )
            except Exception as e:
                handled_error = self._handle_error(AgentBayError(str(e)))
                return QueryResult(
                    request_id="",
                    success=False,
                    error_message=f"Failed to get task status: {handled_error}",
                    task_id=task_id,
                    task_status="failed",
                )

        async def terminate_task(self, task_id: str) -> ExecutionResult:
            _logger.info("Terminating task")
            try:
                args = {"task_id": task_id}
                tool_name = self._get_tool_name("terminate")
                result = await self.session.call_mcp_tool(
                    tool_name,
                    args,
                )
                if result.success:
                    content = json.loads(result.data)
                    content_task_id = content.get("taskId") or content.get("task_id", task_id)
                    return ExecutionResult(
                        request_id=result.request_id,
                        success=True,
                        error_message="",
                        task_id=content_task_id,
                        task_status=content.get("status", "cancelling"),
                    )
                else:
                    content = json.loads(result.data) if result.data else {}
                    return ExecutionResult(
                        request_id=result.request_id,
                        success=False,
                        error_message=result.error_message
                        or "Failed to terminate task",
                        task_id=task_id,
                        task_status="failed",
                    )
            except AgentError as e:
                handled_error = self._handle_error(e)
                return ExecutionResult(
                    request_id=result.request_id if "result" in locals() else "",
                    success=False,
                    error_message=str(handled_error),
                    task_id=task_id,
                    task_status="failed",
                )
            except Exception as e:
                handled_error = self._handle_error(AgentBayError(str(e)))
                return ExecutionResult(
                    request_id="",
                    success=False,
                    error_message=f"Failed to terminate: {handled_error}",
                    task_id=task_id,
                    task_status="failed",
                )
