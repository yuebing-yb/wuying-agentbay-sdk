# -*- coding: utf-8 -*-
import asyncio
import json
from collections.abc import Awaitable, Callable
from typing import Any, Optional

import pytest


@pytest.mark.unit
@pytest.mark.asyncio
class TestWsLongConnection:
    async def _start_ws_server(
        self,
        handler: Callable[[Any], Awaitable[None]],
    ) -> tuple[Any, str]:
        import websockets

        server = await websockets.serve(handler, host="127.0.0.1", port=0)
        port = server.sockets[0].getsockname()[1]
        return server, f"ws://127.0.0.1:{port}"

    async def test_get_ws_client_is_accessible(self):
        from agentbay import AsyncAgentBay
        from agentbay._async.session import AsyncSession

        agentbay = AsyncAgentBay(api_key="test_api_key")
        session = AsyncSession(agentbay, "sess_test")
        session.token = "token_test"
        session.ws_url = "ws://127.0.0.1:1"

        ws_client = await session._get_ws_client()
        assert ws_client is not None

    async def test_call_stream_connect_and_routing_success(self):
        received_frames: list[dict[str, Any]] = []

        async def ws_handler(ws):
            assert ws.request is not None
            assert (
                ws.request.headers.get("X-Access-Token") == "token_test"
            ), "X-Access-Token header not set on WS connect"

            # Expect a business message directly (no handshake).
            req_raw = await ws.recv()
            req = json.loads(req_raw)
            received_frames.append(req)
            assert req["source"] == "SDK"
            assert req["target"] == "wuying_codespace"
            assert req["data"]["method"] == "run_code"
            invocation_id = req["invocationId"]

            # Send event + end
            await ws.send(
                json.dumps(
                    {
                        "invocationId": invocation_id,
                        "target": req["target"],
                        "data": {
                            "method": "run_code",
                            "mode": "stream",
                            "phase": "event",
                            "seq": 1,
                            "eventType": "stdout",
                            "chunk": "hello ",
                        },
                    }
                )
            )
            await ws.send(
                json.dumps(
                    {
                        "invocationId": invocation_id,
                        "target": req["target"],
                        "data": {
                            "method": "run_code",
                            "mode": "stream",
                            "phase": "end",
                            "seq": 2,
                            "status": "finished",
                        },
                    }
                )
            )

        server, ws_url = await self._start_ws_server(ws_handler)
        try:
            from agentbay import AsyncAgentBay
            from agentbay._async.session import AsyncSession

            agentbay = AsyncAgentBay(api_key="test_api_key")
            session = AsyncSession(agentbay, "sess_test")
            session.token = "token_test"
            session.ws_url = ws_url

            ws_client = await session._get_ws_client()

            events: list[dict[str, Any]] = []
            ended: list[dict[str, Any]] = []
            errors: list[Exception] = []

            def on_event(invocation_id: str, data: dict[str, Any]) -> None:
                assert invocation_id
                events.append(data)

            def on_end(invocation_id: str, data: dict[str, Any]) -> None:
                assert invocation_id
                ended.append(data)

            def on_error(invocation_id: str, err: Exception) -> None:
                assert invocation_id
                errors.append(err)

            handle = await ws_client.call_stream(
                target="wuying_codespace",
                data={"method": "run_code", "mode": "stream", "params": {"code": "x=1"}},
                on_event=on_event,
                on_end=on_end,
                on_error=on_error,
            )

            end_data = await asyncio.wait_for(handle.wait_end(), timeout=3)

            assert errors == []
            assert len(events) == 1
            assert events[0]["eventType"] == "stdout"
            assert events[0]["chunk"] == "hello "
            assert len(ended) == 1
            assert end_data["status"] == "finished"
            await ws_client.close()
        finally:
            server.close()
            await server.wait_closed()

    async def test_disconnect_fails_pending_without_retrying_business(self):
        async def ws_handler(ws):
            assert ws.request is not None
            assert ws.request.headers.get("X-Access-Token") == "token_test"

            # Receive business message then close immediately
            await ws.recv()
            await ws.close(code=1001, reason="server shutdown")

        server, ws_url = await self._start_ws_server(ws_handler)
        try:
            from agentbay import AsyncAgentBay
            from agentbay._async.session import AsyncSession

            agentbay = AsyncAgentBay(api_key="test_api_key")
            session = AsyncSession(agentbay, "sess_test")
            session.token = "token_test"
            session.ws_url = ws_url

            ws_client = await session._get_ws_client()

            errors: list[Exception] = []

            def on_error(invocation_id: str, err: Exception) -> None:
                errors.append(err)

            handle = await ws_client.call_stream(
                target="wuying_codespace",
                data={"method": "run_code", "mode": "stream"},
                on_event=None,
                on_end=None,
                on_error=on_error,
            )

            with pytest.raises(Exception) as excinfo:
                await asyncio.wait_for(handle.wait_end(), timeout=3)
            assert "closed" in str(excinfo.value).lower() or "disconnect" in str(
                excinfo.value
            ).lower()
            assert len(errors) >= 1
            await ws_client.close()
        finally:
            server.close()
            await server.wait_closed()

    async def test_protocol_requires_invocation_id(self):
        async def ws_handler(ws):
            assert ws.request is not None
            assert ws.request.headers.get("X-Access-Token") == "token_test"

            req_raw = await ws.recv()
            req = json.loads(req_raw)
            assert req["source"] == "SDK"
            # Send a malformed message without invocationId
            await ws.send(
                json.dumps(
                    {
                        "target": req["target"],
                        "data": {"phase": "end", "status": "finished"},
                    }
                )
            )

        server, ws_url = await self._start_ws_server(ws_handler)
        try:
            from agentbay import AsyncAgentBay
            from agentbay._async.session import AsyncSession

            agentbay = AsyncAgentBay(api_key="test_api_key")
            session = AsyncSession(agentbay, "sess_test")
            session.token = "token_test"
            session.ws_url = ws_url

            ws_client = await session._get_ws_client()

            errors: list[Exception] = []

            def on_error(invocation_id: str, err: Exception) -> None:
                errors.append(err)

            handle = await ws_client.call_stream(
                target="wuying_codespace",
                data={"method": "run_code", "mode": "stream"},
                on_event=None,
                on_end=None,
                on_error=on_error,
            )

            with pytest.raises(Exception) as excinfo:
                await asyncio.wait_for(handle.wait_end(), timeout=3)
            assert "invocationid" in str(excinfo.value).lower()
            assert len(errors) >= 1
            await ws_client.close()
        finally:
            server.close()
            await server.wait_closed()

    async def test_websocket_server_error_returns_to_caller_without_phase(self):
        async def ws_handler(ws):
            assert ws.request is not None
            assert ws.request.headers.get("X-Access-Token") == "token_test"

            req_raw = await ws.recv()
            req = json.loads(req_raw)
            invocation_id = req["invocationId"]

            # Send control-plane error message with source=WEBSOCKET_SERVER and no phase.
            await ws.send(
                json.dumps(
                    {
                        "invocationId": invocation_id,
                        "source": "WEBSOCKET_SERVER",
                        "data": {"error": "bad request"},
                    }
                )
            )

        server, ws_url = await self._start_ws_server(ws_handler)
        try:
            from agentbay import AsyncAgentBay
            from agentbay._async.session import AsyncSession

            agentbay = AsyncAgentBay(api_key="test_api_key")
            session = AsyncSession(agentbay, "sess_test")
            session.token = "token_test"
            session.ws_url = ws_url

            ws_client = await session._get_ws_client()

            errors: list[Exception] = []

            def on_error(invocation_id: str, err: Exception) -> None:
                errors.append(err)

            handle = await ws_client.call_stream(
                target="wuying_codespace",
                data={"method": "run_code", "mode": "stream"},
                on_event=None,
                on_end=None,
                on_error=on_error,
            )

            with pytest.raises(Exception) as excinfo:
                await asyncio.wait_for(handle.wait_end(), timeout=3)
            assert "bad request" in str(excinfo.value).lower()
            assert len(errors) == 1
            assert "bad request" in str(errors[0]).lower()
            await ws_client.close()
        finally:
            server.close()
            await server.wait_closed()

