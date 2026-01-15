"""
Unit tests for tool list propagation into AsyncSession.
"""

import json
import unittest
from threading import Lock
from unittest.mock import MagicMock

import pytest


class TestAgentBayToolList(unittest.TestCase):
    @pytest.mark.sync
    def test_build_session_from_response_sets_session_mcp_tools(self):
        from agentbay._sync.agentbay import AgentBay
        from agentbay._common.params.session_params import CreateSessionParams

        agent_bay = object.__new__(AgentBay)
        agent_bay.api_key = "test_api_key"
        agent_bay._sessions = {}
        agent_bay._lock = Lock()

        tool_list = json.dumps(
            [
                {
                    "name": "shell",
                    "description": "Run shell commands",
                    "inputSchema": {"type": "object"},
                    "server": "wuying_shell",
                    "tool": "shell",
                }
            ],
            ensure_ascii=False,
        )
        response_data = {
            "SessionId": "sid-1",
            "ResourceUrl": "https://example.invalid/resource",
            "ToolList": tool_list,
        }

        session = agent_bay._build_session_from_response(
            response_data=response_data,
            params=CreateSessionParams(),
        )

        assert hasattr(session, "mcpTools")
        assert len(session.mcpTools) == 1
        assert session.mcpTools[0].name == "shell"
        assert session.mcpTools[0].server == "wuying_shell"

    @pytest.mark.sync
    def test_get_sets_session_mcp_tools_from_get_session_result(self):
        from agentbay._sync.agentbay import AgentBay
        from agentbay._common.models.response import GetSessionData, GetSessionResult

        agent_bay = object.__new__(AgentBay)
        agent_bay.api_key = "test_api_key"
        agent_bay._sessions = {}
        agent_bay._lock = Lock()

        tool_list = json.dumps(
            [{"name": "shell", "server": "wuying_shell"}],
            ensure_ascii=False,
        )
        agent_bay._get_session = MagicMock(
            return_value=GetSessionResult(
                request_id="req-1",
                success=True,
                data=GetSessionData(
                    session_id="sid-2",
                    resource_url="https://example.invalid/resource2",
                    tool_list=tool_list,
                ),
            )
        )

        result = agent_bay.get("sid-2")
        assert result.success is True
        assert result.session is not None
        assert len(result.session.mcpTools) == 1
        assert result.session.mcpTools[0].name == "shell"
        assert result.session.mcpTools[0].server == "wuying_shell"


if __name__ == "__main__":
    unittest.main()

