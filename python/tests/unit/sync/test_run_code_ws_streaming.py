# -*- coding: utf-8 -*-
import asyncio
import json
import threading
from typing import Any

import pytest


@pytest.mark.unit
@pytest.mark.sync
class TestRunCodeWsStreaming:
    def _start_server_in_thread(self, handler):
        import websockets

        loop = asyncio.new_event_loop()
        started = threading.Event()
        holder: dict[str, Any] = {}

        async def _start() -> None:
            server = await websockets.serve(handler, host="127.0.0.1", port=0)
            port = server.sockets[0].getsockname()[1]
            holder["server"] = server
            holder["url"] = f"ws://127.0.0.1:{port}"
            started.set()

        def _runner() -> None:
            asyncio.set_event_loop(loop)
            loop.create_task(_start())
            loop.run_forever()

        t = threading.Thread(target=_runner, name="ws-unit-server", daemon=True)
        t.start()
        started.wait(timeout=5.0)
        if "url" not in holder:
            raise RuntimeError("failed to start ws server")

        def _stop() -> None:
            server = holder.get("server")
            if server is not None:
                server.close()
                asyncio.run_coroutine_threadsafe(server.wait_closed(), loop).result(timeout=5.0)
            loop.call_soon_threadsafe(loop.stop)

        return holder["url"], _stop

    def test_run_code_streaming_accumulates_and_returns_result(self):
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
                            "result": {"isMainResult": True, "mime": {"text/plain": "42"}},
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

        ws_url, stop = self._start_server_in_thread(ws_handler)
        try:
            from agentbay import AgentBay
            from agentbay._sync.session import Session

            agentbay = AgentBay(api_key="test_api_key")
            session = Session(agentbay, "sess_test")
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

            r = session.code.run_code(
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
            session._get_ws_client().close()
        finally:
            stop()

    def test_run_code_streaming_remote_error_fails_call(self):
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

        ws_url, stop = self._start_server_in_thread(ws_handler)
        try:
            from agentbay import AgentBay
            from agentbay._sync.session import Session

            agentbay = AgentBay(api_key="test_api_key")
            session = Session(agentbay, "sess_test")
            session.token = "token_test"
            session.ws_url = ws_url

            errors: list[Any] = []

            def on_error(err: Any) -> None:
                errors.append(err)

            r = session.code.run_code(
                "print('hello')",
                "python",
                60,
                stream_beta=True,
                on_error=on_error,
            )

            assert r.success is False
            assert "bad request" in (r.error_message or "").lower()
            assert len(errors) == 1
            session._get_ws_client().close()
        finally:
            stop()

