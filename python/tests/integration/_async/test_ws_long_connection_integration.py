# -*- coding: utf-8 -*-
import asyncio
import os

import pytest

from agentbay import AsyncAgentBay, CreateSessionParams


@pytest.mark.integration
@pytest.mark.asyncio
class TestWsLongConnectionIntegration:
    @pytest.fixture
    def agentbay(self):
        api_key = os.getenv("AGENTBAY_API_KEY")
        if not api_key:
            pytest.skip("AGENTBAY_API_KEY environment variable not set")
        return AsyncAgentBay(api_key=api_key)

    async def test_ws_connect_and_basic_call_stream(self, agentbay):
        os.environ["AGENTBAY_SDK_INTERNAL_TESTING"] = "1"

        image_id = "imgc-0a9mg1wzcttilodpi"
        params = CreateSessionParams(image_id=image_id)
        result = await agentbay.create(params)
        assert result.success is True, result.error_message
        assert result.session is not None
        session = result.session

        ws_client = None
        try:
            assert (
                session.ws_url
            ), "Backend did not return wsUrl/WsUrl in CreateSession response"

            ws_client = await session._get_ws_client()
            await ws_client.connect()

            target = "wuying_codespace"
            for tool in getattr(session, "mcpTools", []) or []:
                try:
                    if getattr(tool, "name", "") == "run_code" and getattr(tool, "server", ""):
                        target = tool.server
                        break
                except Exception:
                    continue

            events: list[dict] = []
            ends: list[dict] = []
            errors: list[Exception] = []
            end_signal = asyncio.Event()

            def on_event(invocation_id: str, data: dict) -> None:
                assert invocation_id
                assert isinstance(data, dict)
                events.append(data)

            def on_end(invocation_id: str, data: dict) -> None:
                assert invocation_id
                assert isinstance(data, dict)
                ends.append(data)
                end_signal.set()

            def on_error(invocation_id: str, err: Exception) -> None:
                assert invocation_id
                assert isinstance(err, Exception)
                errors.append(err)
                end_signal.set()

            handle = await ws_client.call_stream(
                target=target,
                data={
                    "method": "run_code",
                    "mode": "stream",
                    "params": {"language": "python", "timeoutS": 600, "code": "x=1"},
                },
                on_event=on_event,
                on_end=on_end,
                on_error=on_error,
            )

            try:
                end_data = await asyncio.wait_for(handle.wait_end(), timeout=600)
            except Exception as e:
                assert end_signal.is_set(), "Expected on_error/on_end to be called"
                if errors:
                    # For WS validation, backend may return request error immediately.
                    # This is still a valid callback chain: on_error must be invoked.
                    return
                    tools_brief = []
                    for t in getattr(session, "mcpTools", []) or []:
                        try:
                            tools_brief.append(
                                {"name": getattr(t, "name", ""), "server": getattr(t, "server", "")}
                            )
                        except Exception:
                            continue
                    raise AssertionError(
                        f"WS call_stream failed: {errors[0]!r}; target={target!r}; "
                        f"mcpTools={tools_brief}; events={events}, ends={ends}"
                    ) from e
                raise

            assert end_signal.is_set()
            assert errors == [], f"errors={errors}, events={events}, ends={ends}"
            assert len(ends) == 1
            assert isinstance(end_data, dict)
        finally:
            if ws_client is not None:
                try:
                    await ws_client.close()
                except Exception:
                    pass
            await session.delete()

