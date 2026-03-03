# -*- coding: utf-8 -*-
import asyncio
import json
from collections.abc import Awaitable, Callable
from typing import Any

import pytest


@pytest.mark.unit
@pytest.mark.asyncio
@pytest.mark.skip(reason="Streaming API temporarily disabled; will be re-enabled in a future release")
class TestRunCodeWsStreaming:
    async def _start_ws_server(
        self,
        handler: Callable[[Any], Awaitable[None]],
    ) -> tuple[Any, str]:
        import websockets

        server = await websockets.serve(handler, host="127.0.0.1", port=0)
        port = server.sockets[0].getsockname()[1]
        return server, f"ws://127.0.0.1:{port}"

    async def test_run_code_streaming_accumulates_and_returns_result(self):
        async def ws_handler(ws):
            assert ws.request is not None
            assert ws.request.headers.get("X-Access-Token") == "token_test"

            req_raw = await ws.recv()
            req = json.loads(req_raw)
            assert req["source"] == "SDK"
            assert req["target"] == "wuying_codespace"
            assert req["data"]["method"] == "run_code"
            assert req["data"]["mode"] == "stream"
            assert req["data"]["params"]["language"] == "python"
            assert req["data"]["params"]["timeoutS"] == 60
            assert "print('hello')" in req["data"]["params"]["code"]
            invocation_id = req["invocationId"]

            await ws.send(
                json.dumps(
                    {
                        "invocationId": invocation_id,
                        "source": "wuying_codespace",
                        "target": "wuying_codespace",
                        "data": {
                            "method": "run_code",
                            "mode": "stream",
                            "phase": "event",
                            "seq": 1,
                            "eventType": "stdout",
                            "chunk": "hello\n",
                        },
                    }
                )
            )
            await ws.send(
                json.dumps(
                    {
                        "invocationId": invocation_id,
                        "source": "wuying_codespace",
                        "target": "wuying_codespace",
                        "data": {
                            "method": "run_code",
                            "mode": "stream",
                            "phase": "event",
                            "seq": 2,
                            "eventType": "result",
                            "result": {
                                "isMainResult": True,
                                "mime": {"text/plain": "42"},
                            },
                        },
                    }
                )
            )
            await ws.send(
                json.dumps(
                    {
                        "invocationId": invocation_id,
                        "source": "wuying_codespace",
                        "target": "wuying_codespace",
                        "data": {
                            "method": "run_code",
                            "mode": "stream",
                            "phase": "end",
                            "seq": 3,
                            "status": "finished",
                            "executionError": None,
                            "executionCount": 7,
                            "executionTime": 0.12,
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

            stdout_chunks: list[str] = []
            stderr_chunks: list[str] = []
            errors: list[Any] = []

            def on_stdout(chunk: str) -> None:
                stdout_chunks.append(chunk)

            def on_stderr(chunk: str) -> None:
                stderr_chunks.append(chunk)

            def on_error(err: Any) -> None:
                errors.append(err)

            r = await session.code.run_code(
                "print('hello')\nprint(42)",
                "python",
                60,
                stream_beta=True,
                on_stdout=on_stdout,
                on_stderr=on_stderr,
                on_error=on_error,
            )

            assert errors == []
            assert "".join(stdout_chunks) == "hello\n"
            assert stderr_chunks == []
            assert r.success is True
            assert r.execution_count == 7
            assert abs(r.execution_time - 0.12) < 0.0001
            assert r.result == "42"
            assert r.logs.stdout == ["hello\n"]
            ws_client = await session._get_ws_client()
            await ws_client.close()
        finally:
            server.close()
            await server.wait_closed()

    async def test_run_code_streaming_remote_error_fails_call(self):
        async def ws_handler(ws):
            req_raw = await ws.recv()
            req = json.loads(req_raw)
            invocation_id = req["invocationId"]
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

            errors: list[Any] = []

            def on_error(err: Any) -> None:
                errors.append(err)

            r = await session.code.run_code(
                "print('hello')",
                "python",
                60,
                stream_beta=True,
                on_error=on_error,
            )

            assert r.success is False
            assert "bad request" in (r.error_message or "").lower()
            assert len(errors) == 1
            ws_client = await session._get_ws_client()
            await ws_client.close()
        finally:
            server.close()
            await server.wait_closed()

