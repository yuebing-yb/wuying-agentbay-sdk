# -*- coding: utf-8 -*-
import asyncio
import json
from collections.abc import Awaitable, Callable
from typing import Any

import pytest


@pytest.mark.unit
@pytest.mark.asyncio
class TestAgentStreaming:
    """Unit tests for Agent WS streaming (on_* callbacks)."""

    async def _start_ws_server(
        self,
        handler: Callable[[Any], Awaitable[None]],
    ) -> tuple[Any, str]:
        import websockets

        server = await websockets.serve(handler, host="127.0.0.1", port=0)
        port = server.sockets[0].getsockname()[1]
        return server, f"ws://127.0.0.1:{port}"

    async def _create_session_with_ws(self, ws_url: str):
        from agentbay import AsyncAgentBay
        from agentbay._async.session import AsyncSession

        agentbay = AsyncAgentBay(api_key="test_api_key")
        session = AsyncSession(agentbay, "sess_test")
        session.token = "token_test"
        session.ws_url = ws_url
        return session

    async def test_agent_event_model(self):
        """Verify AgentEvent fields and repr."""
        from agentbay import AgentEvent

        event = AgentEvent(
            type="reasoning", seq=1, round=1, content="thinking..."
        )
        assert event.type == "reasoning"
        assert event.seq == 1
        assert event.round == 1
        assert event.content == "thinking..."
        assert "reasoning" in repr(event)

        tool_event = AgentEvent(
            type="tool_call", seq=2, round=1,
            tool_call_id="call_001", tool_name="browser_navigate",
            args={"url": "https://example.com"},
        )
        assert tool_event.tool_name == "browser_navigate"
        assert tool_event.args == {"url": "https://example.com"}

    async def test_mobile_error_event_handling(self):
        """Error events are dispatched and result in failed ExecutionResult."""
        async def ws_handler(ws):
            req_raw = await ws.recv()
            req = json.loads(req_raw)
            invocation_id = req["invocationId"]
            target = req["target"]

            await ws.send(json.dumps({
                "invocationId": invocation_id,
                "target": target,
                "data": {
                    "phase": "event", "seq": 1, "round": 1,
                    "eventType": "error",
                    "error": {"code": "TASK_FAILED", "message": "Something went wrong"},
                },
            }))
            await ws.send(json.dumps({
                "invocationId": invocation_id,
                "target": target,
                "data": {"phase": "end", "status": "failed"},
            }))

        server, ws_url = await self._start_ws_server(ws_handler)
        try:
            session = await self._create_session_with_ws(ws_url)
            ws_client = await session._get_ws_client()

            error_events = []
            result = await session.agent.mobile.execute_task_and_wait(
                task="Failing task",
                timeout=10,
                on_event=lambda e: error_events.append(e) if e.type == "error" else None,
            )

            assert result.success is False
            assert len(error_events) == 1
            assert error_events[0].error["code"] == "TASK_FAILED"

            await ws_client.close()
        finally:
            server.close()
            await server.wait_closed()

    async def test_mobile_timeout_during_streaming(self):
        """Timeout while waiting for WS end signal produces correct result."""
        async def ws_handler(ws):
            req_raw = await ws.recv()
            req = json.loads(req_raw)
            invocation_id = req["invocationId"]
            target = req["target"]

            await ws.send(json.dumps({
                "invocationId": invocation_id,
                "target": target,
                "data": {
                    "phase": "event", "seq": 1, "round": 1,
                    "eventType": "content", "content": "Partial output...",
                },
            }))
            await asyncio.sleep(10)

        server, ws_url = await self._start_ws_server(ws_handler)
        try:
            session = await self._create_session_with_ws(ws_url)
            ws_client = await session._get_ws_client()

            result = await session.agent.mobile.execute_task_and_wait(
                task="Slow task",
                timeout=2,
                on_event=lambda e: None,
            )

            assert result.success is False
            assert "timed out" in result.error_message.lower()
            assert "Partial output..." in result.task_result

            await ws_client.close()
        finally:
            server.close()
            await server.wait_closed()

    async def test_mobile_content_accumulated_for_task_result(self):
        """Content events are accumulated for the final task_result when taskResult not in end."""
        async def ws_handler(ws):
            req_raw = await ws.recv()
            req = json.loads(req_raw)
            invocation_id = req["invocationId"]
            target = req["target"]

            await ws.send(json.dumps({
                "invocationId": invocation_id,
                "target": target,
                "data": {"phase": "event", "seq": 1, "round": 1, "eventType": "content", "content": "Hello "},
            }))
            await ws.send(json.dumps({
                "invocationId": invocation_id,
                "target": target,
                "data": {"phase": "event", "seq": 2, "round": 1, "eventType": "content", "content": "World!"},
            }))
            await ws.send(json.dumps({
                "invocationId": invocation_id,
                "target": target,
                "data": {"phase": "end", "status": "finished"},
            }))

        server, ws_url = await self._start_ws_server(ws_handler)
        try:
            session = await self._create_session_with_ws(ws_url)
            ws_client = await session._get_ws_client()

            result = await session.agent.mobile.execute_task_and_wait(
                task="Test accumulation",
                timeout=10,
                on_event=lambda e: None,
            )

            assert result.success is True
            assert result.task_result == "Hello World!"

            await ws_client.close()
        finally:
            server.close()
            await server.wait_closed()

    async def test_resolve_agent_target_browser(self):
        """Browser agent resolves to wuying_browseruse by default."""
        from agentbay import AsyncAgentBay
        from agentbay._async.session import AsyncSession

        agentbay = AsyncAgentBay(api_key="test_api_key")
        session = AsyncSession(agentbay, "sess_test")
        browser_agent = session.agent.browser
        assert browser_agent._resolve_agent_target() == "wuying_browseruse"

    async def test_resolve_agent_target_computer(self):
        """Computer agent resolves to wuying_computer_agent by default."""
        from agentbay import AsyncAgentBay
        from agentbay._async.session import AsyncSession

        agentbay = AsyncAgentBay(api_key="test_api_key")
        session = AsyncSession(agentbay, "sess_test")
        computer_agent = session.agent.computer
        assert computer_agent._resolve_agent_target() == "wuying_computer_agent"

    async def test_resolve_agent_target_mobile(self):
        """Mobile agent resolves to wuying_mobile_agent by default."""
        from agentbay import AsyncAgentBay
        from agentbay._async.session import AsyncSession

        agentbay = AsyncAgentBay(api_key="test_api_key")
        session = AsyncSession(agentbay, "sess_test")
        mobile_agent = session.agent.mobile
        assert mobile_agent._resolve_agent_target() == "wuying_mobile_agent"

    async def test_no_streaming_params_uses_http(self):
        """Without callbacks, the method does NOT use WS channel."""
        from agentbay import AsyncAgentBay
        from agentbay._async.session import AsyncSession

        agentbay = AsyncAgentBay(api_key="test_api_key")
        session = AsyncSession(agentbay, "sess_test")
        agent = session.agent.mobile
        assert agent._has_streaming_params() is False
        assert agent._has_streaming_params(on_event=lambda e: None) is True
        assert agent._has_streaming_params(on_reasoning=lambda e: None) is True
        assert agent._has_streaming_params(on_content=lambda e: None) is True
        assert agent._has_streaming_params(on_error=lambda e: None) is True
        assert agent._has_streaming_params(on_call_for_user=lambda e: "yes") is True

    async def test_agent_event_prompt_field(self):
        """AgentEvent has a prompt field for call_for_user tool_call."""
        from agentbay import AgentEvent

        event = AgentEvent(
            type="tool_call", seq=5, round=2,
            tool_call_id="call_003", tool_name="call_for_user",
            args={"prompt": "Do you want to continue?"},
            prompt="Do you want to continue?",
        )
        assert event.prompt == "Do you want to continue?"
        assert event.tool_name == "call_for_user"

        event_no_prompt = AgentEvent(type="reasoning", seq=1, round=1, content="thinking")
        assert event_no_prompt.prompt == ""

    async def test_call_for_user_callback_invoked(self):
        """on_call_for_user is invoked when tool_call with toolName=call_for_user arrives."""
        async def ws_handler(ws):
            req_raw = await ws.recv()
            req = json.loads(req_raw)
            invocation_id = req["invocationId"]
            target = req["target"]

            await ws.send(json.dumps({
                "invocationId": invocation_id,
                "target": target,
                "data": {
                    "phase": "event", "seq": 1, "round": 1,
                    "eventType": "reasoning", "content": "Need user input.",
                },
            }))
            await ws.send(json.dumps({
                "invocationId": invocation_id,
                "target": target,
                "data": {
                    "phase": "event", "seq": 2, "round": 1,
                    "eventType": "tool_call",
                    "toolCallId": "call_003",
                    "toolName": "call_for_user",
                    "args": {"prompt": "Please enter verification code"},
                },
            }))

            resume_raw = await asyncio.wait_for(ws.recv(), timeout=5)
            resume_msg = json.loads(resume_raw)

            await ws.send(json.dumps({
                "invocationId": invocation_id,
                "target": target,
                "data": {
                    "phase": "event", "seq": 3, "round": 1,
                    "eventType": "tool_result",
                    "toolCallId": "call_003",
                    "toolName": "call_for_user",
                    "result": {"isError": False, "mime": {"text/plain": "385216"}},
                },
            }))
            await ws.send(json.dumps({
                "invocationId": invocation_id,
                "target": target,
                "data": {"phase": "end", "status": "finished", "taskResult": "Done."},
            }))

        server, ws_url = await self._start_ws_server(ws_handler)
        try:
            session = await self._create_session_with_ws(ws_url)
            ws_client = await session._get_ws_client()

            call_for_user_events = []

            async def handle_call(event):
                call_for_user_events.append(event)
                return "385216"

            result = await session.agent.mobile.execute_task_and_wait(
                task="Test call_for_user",
                timeout=10,
                on_call_for_user=handle_call,
            )

            assert result.success is True
            assert len(call_for_user_events) == 1
            assert call_for_user_events[0].tool_name == "call_for_user"
            assert call_for_user_events[0].prompt == "Please enter verification code"

            await ws_client.close()
        finally:
            server.close()
            await server.wait_closed()

    async def test_call_for_user_sends_resume_task(self):
        """After on_call_for_user returns, SDK sends resume_task upstream."""
        resume_messages: list[dict] = []

        async def ws_handler(ws):
            req_raw = await ws.recv()
            req = json.loads(req_raw)
            invocation_id = req["invocationId"]
            target = req["target"]

            await ws.send(json.dumps({
                "invocationId": invocation_id,
                "target": target,
                "data": {
                    "phase": "event", "seq": 1, "round": 1,
                    "eventType": "tool_call",
                    "toolCallId": "call_003",
                    "toolName": "call_for_user",
                    "args": {"prompt": "Continue?"},
                },
            }))

            resume_raw = await asyncio.wait_for(ws.recv(), timeout=5)
            resume_msg = json.loads(resume_raw)
            resume_messages.append(resume_msg)

            await ws.send(json.dumps({
                "invocationId": invocation_id,
                "target": target,
                "data": {
                    "phase": "event", "seq": 2, "round": 1,
                    "eventType": "tool_result",
                    "toolCallId": "call_003",
                    "toolName": "call_for_user",
                    "result": {"isError": False, "mime": {"text/plain": "yes"}},
                },
            }))
            await ws.send(json.dumps({
                "invocationId": invocation_id,
                "target": target,
                "data": {"phase": "end", "status": "finished", "taskResult": "Done."},
            }))

        server, ws_url = await self._start_ws_server(ws_handler)
        try:
            session = await self._create_session_with_ws(ws_url)
            ws_client = await session._get_ws_client()

            async def handle_call(event):
                return "yes"

            result = await session.agent.mobile.execute_task_and_wait(
                task="Test resume_task",
                timeout=10,
                on_call_for_user=handle_call,
            )

            assert result.success is True
            assert len(resume_messages) == 1
            resume_data = resume_messages[0]["data"]
            assert resume_data["method"] == "resume_task"
            assert resume_data["params"]["toolCallId"] == "call_003"
            assert resume_data["params"]["response"] == "yes"

            await ws_client.close()
        finally:
            server.close()
            await server.wait_closed()

    async def test_call_for_user_also_triggers_on_event_and_on_tool_call(self):
        """call_for_user tool_call also triggers on_event and on_tool_call callbacks."""
        async def ws_handler(ws):
            req_raw = await ws.recv()
            req = json.loads(req_raw)
            invocation_id = req["invocationId"]
            target = req["target"]

            await ws.send(json.dumps({
                "invocationId": invocation_id,
                "target": target,
                "data": {
                    "phase": "event", "seq": 1, "round": 1,
                    "eventType": "tool_call",
                    "toolCallId": "call_003",
                    "toolName": "call_for_user",
                    "args": {"prompt": "Input code"},
                },
            }))

            await asyncio.wait_for(ws.recv(), timeout=5)

            await ws.send(json.dumps({
                "invocationId": invocation_id,
                "target": target,
                "data": {
                    "phase": "event", "seq": 2, "round": 1,
                    "eventType": "tool_result",
                    "toolCallId": "call_003",
                    "toolName": "call_for_user",
                    "result": {"isError": False, "mime": {"text/plain": "123456"}},
                },
            }))
            await ws.send(json.dumps({
                "invocationId": invocation_id,
                "target": target,
                "data": {"phase": "end", "status": "finished", "taskResult": "Done."},
            }))

        server, ws_url = await self._start_ws_server(ws_handler)
        try:
            session = await self._create_session_with_ws(ws_url)
            ws_client = await session._get_ws_client()

            all_events = []
            tool_call_events = []

            async def handle_call(event):
                return "123456"

            result = await session.agent.mobile.execute_task_and_wait(
                task="Test callbacks",
                timeout=10,
                on_event=lambda e: all_events.append(e),
                on_tool_call=lambda e: tool_call_events.append(e),
                on_call_for_user=handle_call,
            )

            assert result.success is True
            assert any(e.tool_name == "call_for_user" for e in all_events)
            assert any(e.tool_name == "call_for_user" for e in tool_call_events)

            await ws_client.close()
        finally:
            server.close()
            await server.wait_closed()

    async def test_mobile_agent_streaming_routes_to_ws(self):
        """Mobile agent with callbacks routes to WS channel with correct params."""
        received_frames: list[dict[str, Any]] = []

        async def ws_handler(ws):
            req_raw = await ws.recv()
            req = json.loads(req_raw)
            received_frames.append(req)
            invocation_id = req["invocationId"]
            target = req["target"]

            await ws.send(json.dumps({
                "invocationId": invocation_id,
                "target": target,
                "data": {
                    "phase": "event", "seq": 1, "round": 1,
                    "eventType": "content",
                    "content": "Screenshot taken. I see the home screen.",
                },
            }))
            await ws.send(json.dumps({
                "invocationId": invocation_id,
                "target": target,
                "data": {
                    "phase": "end",
                    "status": "finished",
                    "taskResult": "Screenshot taken. I see the home screen.",
                },
            }))

        server, ws_url = await self._start_ws_server(ws_handler)
        try:
            session = await self._create_session_with_ws(ws_url)
            ws_client = await session._get_ws_client()

            events = []
            result = await session.agent.mobile.execute_task_and_wait(
                task="Take a screenshot",
                timeout=10,
                on_event=lambda e: events.append(e),
            )

            assert result.success is True
            assert result.task_result == "Screenshot taken. I see the home screen."
            assert result.task_status == "finished"

            assert len(received_frames) == 1
            req_data = received_frames[0]["data"]
            assert req_data["method"] == "exec_task"
            assert req_data["params"]["task"] == "Take a screenshot"

            assert len(events) == 1
            assert events[0].type == "content"

            await ws_client.close()
        finally:
            server.close()
            await server.wait_closed()

    async def test_mobile_agent_streaming_with_max_steps(self):
        """Mobile agent streaming sends max_steps in task_params."""
        received_frames: list[dict[str, Any]] = []

        async def ws_handler(ws):
            req_raw = await ws.recv()
            req = json.loads(req_raw)
            received_frames.append(req)
            invocation_id = req["invocationId"]
            target = req["target"]

            await ws.send(json.dumps({
                "invocationId": invocation_id,
                "target": target,
                "data": {"phase": "end", "status": "finished", "taskResult": "Done."},
            }))

        server, ws_url = await self._start_ws_server(ws_handler)
        try:
            session = await self._create_session_with_ws(ws_url)
            ws_client = await session._get_ws_client()

            result = await session.agent.mobile.execute_task_and_wait(
                task="Open app",
                timeout=10,
                max_steps=100,
                on_event=lambda e: None,
            )

            assert result.success is True

            req_data = received_frames[0]["data"]
            assert req_data["params"]["task"] == "Open app"
            assert req_data["params"]["max_steps"] == 100

            await ws_client.close()
        finally:
            server.close()
            await server.wait_closed()

    async def test_mobile_agent_streaming_default_max_steps(self):
        """Mobile agent streaming uses default max_steps=50."""
        received_frames: list[dict[str, Any]] = []

        async def ws_handler(ws):
            req_raw = await ws.recv()
            req = json.loads(req_raw)
            received_frames.append(req)
            invocation_id = req["invocationId"]
            target = req["target"]

            await ws.send(json.dumps({
                "invocationId": invocation_id,
                "target": target,
                "data": {"phase": "end", "status": "finished", "taskResult": "Done."},
            }))

        server, ws_url = await self._start_ws_server(ws_handler)
        try:
            session = await self._create_session_with_ws(ws_url)
            ws_client = await session._get_ws_client()

            result = await session.agent.mobile.execute_task_and_wait(
                task="Open app",
                timeout=10,
                on_event=lambda e: None,
            )

            assert result.success is True

            req_data = received_frames[0]["data"]
            assert req_data["params"]["max_steps"] == 50

            await ws_client.close()
        finally:
            server.close()
            await server.wait_closed()

    async def test_mobile_agent_callbacks_route_to_ws(self):
        """Mobile agent with callbacks routes to WS channel."""
        received_frames: list[dict[str, Any]] = []

        async def ws_handler(ws):
            req_raw = await ws.recv()
            req = json.loads(req_raw)
            received_frames.append(req)
            invocation_id = req["invocationId"]
            target = req["target"]

            events = [
                {"phase": "event", "seq": 1, "round": 1, "eventType": "reasoning", "content": "Planning..."},
                {"phase": "event", "seq": 2, "round": 1, "eventType": "content", "content": "Taking screenshot."},
                {"phase": "event", "seq": 3, "round": 1, "eventType": "tool_call",
                 "toolCallId": "call_001", "toolName": "screenshot", "args": {}},
                {"phase": "event", "seq": 4, "round": 1, "eventType": "tool_result",
                 "toolCallId": "call_001", "toolName": "screenshot",
                 "result": {"isError": False, "mime": {"text/plain": "OK"}}},
                {"phase": "event", "seq": 5, "round": 2, "eventType": "content", "content": "I see the home screen."},
            ]
            for event_data in events:
                await ws.send(json.dumps({
                    "invocationId": invocation_id,
                    "target": target,
                    "data": event_data,
                }))
            await ws.send(json.dumps({
                "invocationId": invocation_id,
                "target": target,
                "data": {"phase": "end", "status": "finished", "taskResult": "I see the home screen."},
            }))

        server, ws_url = await self._start_ws_server(ws_handler)
        try:
            session = await self._create_session_with_ws(ws_url)
            ws_client = await session._get_ws_client()

            reasoning_events = []
            content_events = []
            tool_call_events = []
            tool_result_events = []

            result = await session.agent.mobile.execute_task_and_wait(
                task="Describe screen",
                timeout=10,
                on_reasoning=lambda e: reasoning_events.append(e),
                on_content=lambda e: content_events.append(e),
                on_tool_call=lambda e: tool_call_events.append(e),
                on_tool_result=lambda e: tool_result_events.append(e),
            )

            assert result.success is True
            assert result.task_result == "I see the home screen."

            assert len(received_frames) == 1
            req_data = received_frames[0]["data"]
            assert req_data["method"] == "exec_task"

            assert len(reasoning_events) == 1
            assert reasoning_events[0].content == "Planning..."
            assert len(content_events) == 2
            assert len(tool_call_events) == 1
            assert len(tool_result_events) == 1

            await ws_client.close()
        finally:
            server.close()
            await server.wait_closed()

    async def test_mobile_agent_no_streaming_uses_http(self):
        """Mobile agent without callbacks uses HTTP polling (no WS)."""
        from agentbay import AsyncAgentBay
        from agentbay._async.session import AsyncSession

        agentbay = AsyncAgentBay(api_key="test_api_key")
        session = AsyncSession(agentbay, "sess_test")
        mobile_agent = session.agent.mobile
        assert mobile_agent._has_streaming_params() is False
        assert mobile_agent._has_streaming_params(on_event=lambda e: None) is True

    async def test_call_for_user_no_callback_sends_empty_response(self):
        """Without on_call_for_user callback, SDK sends empty string response."""
        resume_messages: list[dict] = []

        async def ws_handler(ws):
            req_raw = await ws.recv()
            req = json.loads(req_raw)
            invocation_id = req["invocationId"]
            target = req["target"]

            await ws.send(json.dumps({
                "invocationId": invocation_id,
                "target": target,
                "data": {
                    "phase": "event", "seq": 1, "round": 1,
                    "eventType": "tool_call",
                    "toolCallId": "call_003",
                    "toolName": "call_for_user",
                    "args": {"prompt": "Input something"},
                },
            }))

            resume_raw = await asyncio.wait_for(ws.recv(), timeout=5)
            resume_msg = json.loads(resume_raw)
            resume_messages.append(resume_msg)

            await ws.send(json.dumps({
                "invocationId": invocation_id,
                "target": target,
                "data": {
                    "phase": "event", "seq": 2, "round": 1,
                    "eventType": "tool_result",
                    "toolCallId": "call_003",
                    "toolName": "call_for_user",
                    "result": {"isError": False, "mime": {"text/plain": ""}},
                },
            }))
            await ws.send(json.dumps({
                "invocationId": invocation_id,
                "target": target,
                "data": {"phase": "end", "status": "finished", "taskResult": "Done."},
            }))

        server, ws_url = await self._start_ws_server(ws_handler)
        try:
            session = await self._create_session_with_ws(ws_url)
            ws_client = await session._get_ws_client()

            result = await session.agent.mobile.execute_task_and_wait(
                task="Test no callback",
                timeout=10,
                on_event=lambda e: None,
            )

            assert result.success is True
            assert len(resume_messages) == 1
            resume_data = resume_messages[0]["data"]
            assert resume_data["method"] == "resume_task"
            assert resume_data["params"]["response"] == ""

            await ws_client.close()
        finally:
            server.close()
            await server.wait_closed()
