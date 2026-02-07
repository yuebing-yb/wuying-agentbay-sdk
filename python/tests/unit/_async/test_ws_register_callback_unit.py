# -*- coding: utf-8 -*-
import asyncio
import json

import pytest


@pytest.mark.unit
@pytest.mark.asyncio
class TestWsRegisterCallbackUnit:
    async def test_register_callback_should_route_push_message_by_target(
        self,
        unused_tcp_port: int,
    ) -> None:
        websockets = pytest.importorskip("websockets")

        received: list[dict] = []
        received_signal = asyncio.Event()

        async def ws_handler(ws) -> None:
            await asyncio.sleep(0.05)
            await ws.send(
                json.dumps(
                    {
                        "requestId": "push_1",
                        "target": "wuying_cdp_mcp_server",
                        "data": {"method": "notification", "hello": "world"},
                    }
                )
            )
            await asyncio.sleep(0.2)

        server = await websockets.serve(ws_handler, "127.0.0.1", unused_tcp_port)
        try:
            from agentbay._async._internal.ws_client import WsClient

            client = WsClient(
                ws_url=f"ws://127.0.0.1:{unused_tcp_port}",
                ws_token="token_test",
                heartbeat_interval_s=999.0,
            )

            def cb(msg: dict) -> None:
                received.append(msg)
                received_signal.set()

            client.register_callback("wuying_cdp_mcp_server", cb)
            await client.connect()

            await asyncio.wait_for(received_signal.wait(), timeout=2.0)
            assert received == [
                {
                    "requestId": "push_1",
                    "target": "wuying_cdp_mcp_server",
                    "data": {"method": "notification", "hello": "world"},
                }
            ]
        finally:
            try:
                await client.close()
            except Exception:
                pass
            server.close()
            await server.wait_closed()

    async def test_unregister_callback_should_stop_routing(self) -> None:
        from agentbay._async._internal.ws_client import WsClient

        client = WsClient(
            ws_url="ws://127.0.0.1:1",
            ws_token="token_test",
            heartbeat_interval_s=999.0,
        )

        received: list[dict] = []

        def cb(msg: dict) -> None:
            received.append(msg)

        unsubscribe = client.register_callback("wuying_cdp_mcp_server", cb)
        unsubscribe()

        client._handle_incoming(  # noqa: SLF001
            json.dumps(
                {
                    "requestId": "push_2",
                    "target": "wuying_cdp_mcp_server",
                    "data": {"method": "notification"},
                }
            )
        )

        assert received == []

    async def test_register_callback_should_route_push_by_source_when_target_is_sdk(
        self,
        unused_tcp_port: int,
    ) -> None:
        websockets = pytest.importorskip("websockets")

        received: list[dict] = []
        received_signal = asyncio.Event()

        async def ws_handler(ws) -> None:
            await asyncio.sleep(0.05)
            await ws.send(
                json.dumps(
                    {
                        "invocationId": "push_3",
                        "source": "wuying_cdp_mcp_server",
                        "target": "SDK",
                        "data": json.dumps({"method": "notification", "status": "ok"}),
                    }
                )
            )
            await asyncio.sleep(0.2)

        server = await websockets.serve(ws_handler, "127.0.0.1", unused_tcp_port)
        try:
            from agentbay._async._internal.ws_client import WsClient

            client = WsClient(
                ws_url=f"ws://127.0.0.1:{unused_tcp_port}",
                ws_token="token_test",
                heartbeat_interval_s=999.0,
            )

            def cb(msg: dict) -> None:
                received.append(msg)
                received_signal.set()

            client.register_callback("wuying_cdp_mcp_server", cb)
            await client.connect()

            await asyncio.wait_for(received_signal.wait(), timeout=2.0)
            assert received == [
                {
                    "requestId": "push_3",
                    "target": "wuying_cdp_mcp_server",
                    "data": {"method": "notification", "status": "ok"},
                }
            ]
        finally:
            try:
                await client.close()
            except Exception:
                pass
            server.close()
            await server.wait_closed()

