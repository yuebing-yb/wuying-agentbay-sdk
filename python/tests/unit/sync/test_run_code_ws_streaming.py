# -*- coding: utf-8 -*-
import pytest


@pytest.mark.unit
@pytest.mark.sync
class TestRunCodeWsStreaming:
    def test_sync_sdk_does_not_support_ws_streaming(self):
        from agentbay import AgentBay
        from agentbay._sync.session import Session

        agentbay = AgentBay(api_key="test_api_key")
        session = Session(agentbay, "sess_test")
        session.token = "token_test"
        session.ws_url = "ws://127.0.0.1:1"

        r = session.code.run_code(
            "print('hello')",
            "python",
            60,
            stream_beta=True,
        )
        assert r.success is False
        assert "only supported" in (r.error_message or "").lower()
