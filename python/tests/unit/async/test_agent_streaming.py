"""
Unit tests for Agent streaming output feature.

Tests the AgentEvent model, WS-based execution path,
and callback dispatching for execute_task_and_wait with streaming parameters.
"""

import asyncio
import json
import unittest
from unittest.mock import AsyncMock, MagicMock, patch, call

from agentbay import AsyncAgent, ExecutionResult, McpToolResult, AgentEvent


class TestAgentEventModel(unittest.TestCase):
    """Test AgentEvent data model."""

    def test_default_construction(self):
        event = AgentEvent()
        self.assertEqual(event.type, "")
        self.assertEqual(event.seq, 0)
        self.assertEqual(event.round, 0)
        self.assertEqual(event.content, "")
        self.assertEqual(event.tool_call_id, "")
        self.assertEqual(event.tool_name, "")
        self.assertEqual(event.args, {})
        self.assertEqual(event.result, {})
        self.assertEqual(event.error, {})

    def test_thought_event_construction(self):
        event = AgentEvent(
            type="thought",
            seq=1,
            round=1,
            content="I need to open the app",
        )
        self.assertEqual(event.type, "thought")
        self.assertEqual(event.seq, 1)
        self.assertEqual(event.round, 1)
        self.assertEqual(event.content, "I need to open the app")

    def test_tool_call_event_construction(self):
        event = AgentEvent(
            type="tool_call",
            seq=4,
            round=1,
            tool_call_id="call_001",
            tool_name="tap",
            args={"x": 100, "y": 200},
        )
        self.assertEqual(event.type, "tool_call")
        self.assertEqual(event.tool_call_id, "call_001")
        self.assertEqual(event.tool_name, "tap")
        self.assertEqual(event.args, {"x": 100, "y": 200})

    def test_tool_result_event_construction(self):
        event = AgentEvent(
            type="tool_result",
            seq=5,
            round=1,
            tool_call_id="call_001",
            tool_name="tap",
            result={
                "isError": False,
                "mime": {"text/plain": "Tap successful"},
            },
        )
        self.assertEqual(event.type, "tool_result")
        self.assertEqual(event.result["isError"], False)
        self.assertEqual(event.result["mime"]["text/plain"], "Tap successful")

    def test_response_event_construction(self):
        event = AgentEvent(
            type="response",
            seq=10,
            round=3,
            content="Task completed successfully.",
        )
        self.assertEqual(event.type, "response")
        self.assertEqual(event.content, "Task completed successfully.")

    def test_error_event_construction(self):
        event = AgentEvent(
            type="error",
            seq=6,
            round=2,
            error={"code": "TIMEOUT", "message": "Agent execution timed out"},
        )
        self.assertEqual(event.type, "error")
        self.assertEqual(event.error["code"], "TIMEOUT")

    def test_from_ws_data_thought(self):
        data = {
            "eventType": "thought",
            "seq": 1,
            "round": 1,
            "content": "Let me think...",
        }
        event = AgentEvent.from_ws_data(data)
        self.assertEqual(event.type, "thought")
        self.assertEqual(event.seq, 1)
        self.assertEqual(event.round, 1)
        self.assertEqual(event.content, "Let me think...")

    def test_from_ws_data_tool_call(self):
        data = {
            "eventType": "tool_call",
            "seq": 4,
            "round": 1,
            "toolCallId": "call_001",
            "toolName": "tap",
            "args": {"x": 100, "y": 200},
        }
        event = AgentEvent.from_ws_data(data)
        self.assertEqual(event.type, "tool_call")
        self.assertEqual(event.tool_call_id, "call_001")
        self.assertEqual(event.tool_name, "tap")
        self.assertEqual(event.args, {"x": 100, "y": 200})

    def test_from_ws_data_tool_result(self):
        data = {
            "eventType": "tool_result",
            "seq": 5,
            "round": 1,
            "toolCallId": "call_001",
            "toolName": "tap",
            "result": {"isError": False, "mime": {"text/plain": "OK"}},
        }
        event = AgentEvent.from_ws_data(data)
        self.assertEqual(event.type, "tool_result")
        self.assertEqual(event.tool_call_id, "call_001")
        self.assertEqual(event.result["mime"]["text/plain"], "OK")

    def test_from_ws_data_missing_fields(self):
        data = {"eventType": "thought"}
        event = AgentEvent.from_ws_data(data)
        self.assertEqual(event.type, "thought")
        self.assertEqual(event.seq, 0)
        self.assertEqual(event.round, 0)
        self.assertEqual(event.content, "")

    def test_repr(self):
        event = AgentEvent(type="thought", seq=1, round=1, content="Thinking...")
        repr_str = repr(event)
        self.assertIn("thought", repr_str)
        self.assertIn("seq=1", repr_str)
        self.assertIn("Thinking...", repr_str)


class _MockMcpTool:
    """Mock MCP tool descriptor."""

    def __init__(self, name: str, server: str):
        self.name = name
        self.server = server


class DummySession:
    """Mock session for unit testing."""

    def __init__(self):
        self.api_key = "dummy_key"
        self.session_id = "dummy_session"
        self.client = MagicMock()
        self.call_mcp_tool = AsyncMock()
        self.ws_url = "wss://test.example.com/ws"
        self.token = "dummy_token"
        self._ws_client = None
        self.mcpTools = [
            _MockMcpTool("execute_task", "wuying_mobile_agent"),
            _MockMcpTool("get_task_status", "wuying_mobile_agent"),
            _MockMcpTool("terminate_task", "wuying_mobile_agent"),
            _MockMcpTool("flux_execute_task", "wuying_computer_agent"),
            _MockMcpTool("flux_get_task_status", "wuying_computer_agent"),
            _MockMcpTool("browser_use_execute_task", "wuying_browser_agent"),
            _MockMcpTool("browser_use_get_task_status", "wuying_browser_agent"),
        ]

    def get_api_key(self):
        return self.api_key

    def get_session_id(self):
        return self.session_id

    def get_client(self):
        return self.client

    async def _get_ws_client(self):
        if self._ws_client is None:
            self._ws_client = MagicMock()
        return self._ws_client


class TestMobileAgentStreamingBackwardsCompatibility(unittest.IsolatedAsyncioTestCase):
    """Verify that existing code without new params still works via HTTP polling."""

    def setUp(self):
        self.session = DummySession()
        self.agent = AsyncAgent(self.session)

    async def test_no_streaming_params_uses_polling(self):
        """Without stream/callback params, should use HTTP polling path (call_mcp_tool)."""
        mock_result_execute = McpToolResult(
            request_id="request-123",
            success=True,
            data='{"task_id": "task-123"}',
        )
        mock_result_status = McpToolResult(
            request_id="request-124",
            success=True,
            data='{"task_id": "task-123", "status": "completed", "result": "Done"}',
        )
        self.session.call_mcp_tool.side_effect = [
            mock_result_execute,
            mock_result_status,
        ]

        result = await self.agent.mobile.execute_task_and_wait(
            "Open Settings", timeout=30, max_steps=50
        )
        self.assertIsInstance(result, ExecutionResult)
        self.assertTrue(result.success)
        self.assertEqual(result.task_status, "completed")
        # call_mcp_tool should have been used (polling path)
        self.assertTrue(self.session.call_mcp_tool.called)


class TestMobileAgentStreamingWSPath(unittest.IsolatedAsyncioTestCase):
    """Test that streaming parameters trigger WS execution path."""

    def setUp(self):
        self.session = DummySession()
        self.agent = AsyncAgent(self.session)

    async def test_on_event_callback_triggers_ws_path(self):
        """Passing on_event should route to WS path, not HTTP polling."""
        events_received = []

        def on_event(event):
            events_received.append(event)

        mock_ws_client = AsyncMock()
        mock_handle = AsyncMock()

        end_data = {
            "phase": "end",
            "status": "finished",
            "taskResult": "Task completed",
        }
        mock_handle.wait_end = AsyncMock(return_value=end_data)

        async def mock_call_stream(**kwargs):
            on_event_cb = kwargs.get("on_event")
            if on_event_cb:
                on_event_cb("inv-1", {
                    "phase": "event",
                    "eventType": "thought",
                    "seq": 1, "round": 1,
                    "content": "Thinking...",
                })
                on_event_cb("inv-1", {
                    "phase": "event",
                    "eventType": "response",
                    "seq": 2, "round": 1,
                    "content": "Done",
                })
            return mock_handle

        mock_ws_client.call_stream = mock_call_stream
        self.session._ws_client = mock_ws_client

        result = await self.agent.mobile.execute_task_and_wait(
            "Open Settings",
            timeout=30,
            max_steps=50,
            on_event=on_event,
        )

        self.assertIsInstance(result, ExecutionResult)
        self.assertTrue(result.success)
        self.assertEqual(result.task_status, "finished")
        self.assertEqual(result.task_result, "Task completed")
        # on_event should have received events
        self.assertEqual(len(events_received), 2)
        self.assertIsInstance(events_received[0], AgentEvent)
        self.assertEqual(events_received[0].type, "thought")
        self.assertEqual(events_received[0].content, "Thinking...")
        self.assertIsInstance(events_received[1], AgentEvent)
        self.assertEqual(events_received[1].type, "response")
        # call_mcp_tool should NOT have been called (WS path)
        self.session.call_mcp_tool.assert_not_called()

    async def test_stream_true_triggers_ws_path(self):
        """Passing stream=True alone should route to WS path."""
        mock_ws_client = AsyncMock()
        mock_handle = AsyncMock()

        end_data = {
            "phase": "end",
            "status": "finished",
            "taskResult": "Done",
        }
        mock_handle.wait_end = AsyncMock(return_value=end_data)

        async def mock_call_stream(**kwargs):
            return mock_handle

        mock_ws_client.call_stream = mock_call_stream
        self.session._ws_client = mock_ws_client

        result = await self.agent.mobile.execute_task_and_wait(
            "Open Settings",
            timeout=30,
            stream=True,
        )

        self.assertIsInstance(result, ExecutionResult)
        self.assertTrue(result.success)
        self.assertEqual(result.task_result, "Done")
        self.session.call_mcp_tool.assert_not_called()

    async def test_on_thought_callback_dispatched(self):
        """on_thought callback should only receive thought events."""
        thoughts = []
        non_thoughts = []

        def on_thought(event):
            thoughts.append(event)

        def on_response(event):
            non_thoughts.append(event)

        mock_ws_client = AsyncMock()
        mock_handle = AsyncMock()
        end_data = {"phase": "end", "status": "finished", "taskResult": "OK"}
        mock_handle.wait_end = AsyncMock(return_value=end_data)

        async def mock_call_stream(**kwargs):
            on_event_cb = kwargs.get("on_event")
            if on_event_cb:
                on_event_cb("inv-1", {
                    "phase": "event",
                    "eventType": "thought",
                    "seq": 1, "round": 1,
                    "content": "Step 1",
                })
                on_event_cb("inv-1", {
                    "phase": "event",
                    "eventType": "tool_call",
                    "seq": 2, "round": 1,
                    "toolCallId": "c1", "toolName": "tap", "args": {},
                })
                on_event_cb("inv-1", {
                    "phase": "event",
                    "eventType": "response",
                    "seq": 3, "round": 1,
                    "content": "Final answer",
                })
            return mock_handle

        mock_ws_client.call_stream = mock_call_stream
        self.session._ws_client = mock_ws_client

        result = await self.agent.mobile.execute_task_and_wait(
            "Open Settings",
            timeout=30,
            on_thought=on_thought,
            on_response=on_response,
        )

        self.assertEqual(len(thoughts), 1)
        self.assertEqual(thoughts[0].type, "thought")
        self.assertEqual(thoughts[0].content, "Step 1")
        self.assertEqual(len(non_thoughts), 1)
        self.assertEqual(non_thoughts[0].type, "response")
        self.assertEqual(non_thoughts[0].content, "Final answer")

    async def test_on_tool_call_and_tool_result_callbacks(self):
        """on_tool_call and on_tool_result callbacks dispatch correctly."""
        tool_calls = []
        tool_results = []

        mock_ws_client = AsyncMock()
        mock_handle = AsyncMock()
        end_data = {"phase": "end", "status": "finished", "taskResult": "OK"}
        mock_handle.wait_end = AsyncMock(return_value=end_data)

        async def mock_call_stream(**kwargs):
            on_event_cb = kwargs.get("on_event")
            if on_event_cb:
                on_event_cb("inv-1", {
                    "phase": "event",
                    "eventType": "tool_call",
                    "seq": 2, "round": 1,
                    "toolCallId": "c1", "toolName": "tap",
                    "args": {"x": 100, "y": 200},
                })
                on_event_cb("inv-1", {
                    "phase": "event",
                    "eventType": "tool_result",
                    "seq": 3, "round": 1,
                    "toolCallId": "c1", "toolName": "tap",
                    "result": {"isError": False, "mime": {"text/plain": "OK"}},
                })
            return mock_handle

        mock_ws_client.call_stream = mock_call_stream
        self.session._ws_client = mock_ws_client

        result = await self.agent.mobile.execute_task_and_wait(
            "Tap button",
            timeout=30,
            on_tool_call=lambda e: tool_calls.append(e),
            on_tool_result=lambda e: tool_results.append(e),
        )

        self.assertEqual(len(tool_calls), 1)
        self.assertEqual(tool_calls[0].tool_name, "tap")
        self.assertEqual(tool_calls[0].args, {"x": 100, "y": 200})
        self.assertEqual(len(tool_results), 1)
        self.assertEqual(tool_results[0].result["mime"]["text/plain"], "OK")

    async def test_on_event_receives_all_events(self):
        """on_event callback receives ALL events regardless of type."""
        all_events = []

        mock_ws_client = AsyncMock()
        mock_handle = AsyncMock()
        end_data = {"phase": "end", "status": "finished", "taskResult": "OK"}
        mock_handle.wait_end = AsyncMock(return_value=end_data)

        async def mock_call_stream(**kwargs):
            on_event_cb = kwargs.get("on_event")
            if on_event_cb:
                on_event_cb("inv-1", {"phase": "event", "eventType": "thought", "seq": 1, "round": 1, "content": "A"})
                on_event_cb("inv-1", {"phase": "event", "eventType": "tool_call", "seq": 2, "round": 1, "toolCallId": "c1", "toolName": "t", "args": {}})
                on_event_cb("inv-1", {"phase": "event", "eventType": "tool_result", "seq": 3, "round": 1, "toolCallId": "c1", "toolName": "t", "result": {}})
                on_event_cb("inv-1", {"phase": "event", "eventType": "response", "seq": 4, "round": 1, "content": "B"})
            return mock_handle

        mock_ws_client.call_stream = mock_call_stream
        self.session._ws_client = mock_ws_client

        result = await self.agent.mobile.execute_task_and_wait(
            "Do something",
            timeout=30,
            on_event=lambda e: all_events.append(e),
        )

        self.assertEqual(len(all_events), 4)
        types = [e.type for e in all_events]
        self.assertEqual(types, ["thought", "tool_call", "tool_result", "response"])

    async def test_on_event_and_typed_callbacks_both_fire(self):
        """on_event and typed callbacks (on_thought, etc.) both fire for the same event."""
        all_events = []
        thought_events = []

        mock_ws_client = AsyncMock()
        mock_handle = AsyncMock()
        end_data = {"phase": "end", "status": "finished", "taskResult": "OK"}
        mock_handle.wait_end = AsyncMock(return_value=end_data)

        async def mock_call_stream(**kwargs):
            on_event_cb = kwargs.get("on_event")
            if on_event_cb:
                on_event_cb("inv-1", {"phase": "event", "eventType": "thought", "seq": 1, "round": 1, "content": "X"})
            return mock_handle

        mock_ws_client.call_stream = mock_call_stream
        self.session._ws_client = mock_ws_client

        result = await self.agent.mobile.execute_task_and_wait(
            "Do something",
            timeout=30,
            on_event=lambda e: all_events.append(e),
            on_thought=lambda e: thought_events.append(e),
        )

        self.assertEqual(len(all_events), 1)
        self.assertEqual(len(thought_events), 1)
        self.assertEqual(all_events[0].type, "thought")
        self.assertEqual(thought_events[0].type, "thought")

    async def test_ws_error_in_end_signal(self):
        """When WS end signal has status=failed, return failed ExecutionResult."""
        mock_ws_client = AsyncMock()
        mock_handle = AsyncMock()
        end_data = {
            "phase": "end",
            "status": "failed",
            "error": "Agent execution error: timeout",
        }
        mock_handle.wait_end = AsyncMock(return_value=end_data)

        async def mock_call_stream(**kwargs):
            return mock_handle

        mock_ws_client.call_stream = mock_call_stream
        self.session._ws_client = mock_ws_client

        result = await self.agent.mobile.execute_task_and_wait(
            "Do something",
            timeout=30,
            stream=True,
        )

        self.assertIsInstance(result, ExecutionResult)
        self.assertFalse(result.success)
        self.assertEqual(result.task_status, "failed")
        self.assertIn("Agent execution error", result.error_message)

    async def test_ws_exception_returns_error_result(self):
        """When WS call raises an exception, return failed ExecutionResult."""
        mock_ws_client = AsyncMock()

        async def mock_call_stream(**kwargs):
            raise Exception("WebSocket connection failed")

        mock_ws_client.call_stream = mock_call_stream
        self.session._ws_client = mock_ws_client

        result = await self.agent.mobile.execute_task_and_wait(
            "Do something",
            timeout=30,
            stream=True,
        )

        self.assertIsInstance(result, ExecutionResult)
        self.assertFalse(result.success)
        self.assertIn("WebSocket connection failed", result.error_message)

    async def test_ws_request_includes_correct_params(self):
        """Verify the WS request includes correct method, stream, and params."""
        mock_ws_client = AsyncMock()
        mock_handle = AsyncMock()
        end_data = {"phase": "end", "status": "finished", "taskResult": "OK"}
        mock_handle.wait_end = AsyncMock(return_value=end_data)

        captured_kwargs = {}

        async def mock_call_stream(**kwargs):
            captured_kwargs.update(kwargs)
            return mock_handle

        mock_ws_client.call_stream = mock_call_stream
        self.session._ws_client = mock_ws_client

        result = await self.agent.mobile.execute_task_and_wait(
            "Open WeChat",
            timeout=60,
            max_steps=100,
            stream=True,
        )

        self.assertIn("target", captured_kwargs)
        self.assertEqual(captured_kwargs["target"], "wuying_mobile_agent")
        self.assertIn("data", captured_kwargs)
        ws_data = captured_kwargs["data"]
        self.assertEqual(ws_data["method"], "run_agent")
        self.assertEqual(ws_data["stream"], True)
        self.assertIn("params", ws_data)
        self.assertEqual(ws_data["params"]["task"], "Open WeChat")
        self.assertEqual(ws_data["params"]["max_steps"], 100)
        self.assertEqual(ws_data["params"]["agentType"], "mobile")

    async def test_callback_exception_does_not_break_execution(self):
        """Callback throwing exception should not break the main execution."""
        def bad_callback(event):
            raise ValueError("Callback error!")

        mock_ws_client = AsyncMock()
        mock_handle = AsyncMock()
        end_data = {"phase": "end", "status": "finished", "taskResult": "OK"}
        mock_handle.wait_end = AsyncMock(return_value=end_data)

        async def mock_call_stream(**kwargs):
            on_event_cb = kwargs.get("on_event")
            if on_event_cb:
                on_event_cb("inv-1", {"phase": "event", "eventType": "thought", "seq": 1, "round": 1, "content": "X"})
            return mock_handle

        mock_ws_client.call_stream = mock_call_stream
        self.session._ws_client = mock_ws_client

        result = await self.agent.mobile.execute_task_and_wait(
            "Do something",
            timeout=30,
            on_event=bad_callback,
        )

        # Should still return a successful result despite callback error
        self.assertIsInstance(result, ExecutionResult)
        self.assertTrue(result.success)
        self.assertEqual(result.task_result, "OK")


class TestBrowserAgentStreamingWSPath(unittest.IsolatedAsyncioTestCase):
    """Test Browser agent also supports streaming params."""

    def setUp(self):
        self.session = AsyncMock()
        self.session.ws_url = "wss://test.example.com/ws"
        self.session.token = "dummy_token"
        self.session._ws_client = None
        self.session.mcpTools = [
            _MockMcpTool("browser_use_execute_task", "wuying_browser_agent"),
        ]
        self.agent = AsyncAgent(self.session)

    async def test_browser_stream_triggers_ws_path(self):
        """Browser agent with stream=True should use WS path."""
        mock_ws_client = AsyncMock()
        mock_handle = AsyncMock()
        end_data = {"phase": "end", "status": "finished", "taskResult": "Search done"}
        mock_handle.wait_end = AsyncMock(return_value=end_data)

        async def mock_call_stream(**kwargs):
            return mock_handle

        mock_ws_client.call_stream = mock_call_stream
        self.session._get_ws_client = AsyncMock(return_value=mock_ws_client)
        self.session._ws_client = mock_ws_client

        result = await self.agent.browser.execute_task_and_wait(
            "Search Google for AgentBay",
            timeout=60,
            stream=True,
        )

        self.assertIsInstance(result, ExecutionResult)
        self.assertTrue(result.success)
        self.assertEqual(result.task_result, "Search done")


class TestComputerAgentStreamingWSPath(unittest.IsolatedAsyncioTestCase):
    """Test Computer agent also supports streaming params."""

    def setUp(self):
        self.session = DummySession()
        self.agent = AsyncAgent(self.session)

    async def test_computer_stream_triggers_ws_path(self):
        """Computer agent with on_event should use WS path."""
        events = []
        mock_ws_client = AsyncMock()
        mock_handle = AsyncMock()
        end_data = {"phase": "end", "status": "finished", "taskResult": "File created"}
        mock_handle.wait_end = AsyncMock(return_value=end_data)

        async def mock_call_stream(**kwargs):
            on_event_cb = kwargs.get("on_event")
            if on_event_cb:
                on_event_cb("inv-1", {"phase": "event", "eventType": "thought", "seq": 1, "round": 1, "content": "Creating file"})
            return mock_handle

        mock_ws_client.call_stream = mock_call_stream
        self.session._ws_client = mock_ws_client

        result = await self.agent.computer.execute_task_and_wait(
            "Create a text file",
            timeout=60,
            on_event=lambda e: events.append(e),
        )

        self.assertIsInstance(result, ExecutionResult)
        self.assertTrue(result.success)
        self.assertEqual(result.task_result, "File created")
        self.assertEqual(len(events), 1)
        self.assertEqual(events[0].content, "Creating file")


if __name__ == "__main__":
    unittest.main()
