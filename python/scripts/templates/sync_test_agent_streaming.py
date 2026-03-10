# -*- coding: utf-8 -*-
"""
Sync version of agent streaming tests.
Only tests that don't require WS server are included here;
WS-based streaming tests are async-only.
"""
import pytest


@pytest.mark.unit
class TestAgentStreaming:
    """Unit tests for Agent streaming (sync version - non-WS tests only)."""

    def test_agent_event_model(self):
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

    def test_resolve_agent_target_browser(self):
        """Browser agent resolves to wuying_browseruse by default."""
        from agentbay import AgentBay
        from agentbay._sync.session import Session

        agentbay = AgentBay(api_key="test_api_key")
        session = Session(agentbay, "sess_test")
        browser_agent = session.agent.browser
        assert browser_agent._resolve_agent_target() == "wuying_browseruse"

    def test_resolve_agent_target_computer(self):
        """Computer agent resolves to wuying_computer_agent by default."""
        from agentbay import AgentBay
        from agentbay._sync.session import Session

        agentbay = AgentBay(api_key="test_api_key")
        session = Session(agentbay, "sess_test")
        computer_agent = session.agent.computer
        assert computer_agent._resolve_agent_target() == "wuying_computer_agent"

    def test_resolve_agent_target_mobile(self):
        """Mobile agent resolves to wuying_mobile_agent by default."""
        from agentbay import AgentBay
        from agentbay._sync.session import Session

        agentbay = AgentBay(api_key="test_api_key")
        session = Session(agentbay, "sess_test")
        mobile_agent = session.agent.mobile
        assert mobile_agent._resolve_agent_target() == "wuying_mobile_agent"

    def test_no_streaming_params_uses_http(self):
        """Without callbacks, the method does NOT use WS channel."""
        from agentbay import AgentBay
        from agentbay._sync.session import Session

        agentbay = AgentBay(api_key="test_api_key")
        session = Session(agentbay, "sess_test")
        agent = session.agent.mobile
        assert agent._has_streaming_params() is False
        assert agent._has_streaming_params(on_reasoning=lambda e: None) is True
        assert agent._has_streaming_params(on_content=lambda e: None) is True
        assert agent._has_streaming_params(on_error=lambda e: None) is True
