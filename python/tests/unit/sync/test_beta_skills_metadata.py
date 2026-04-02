import unittest
from unittest.mock import MagicMock, patch

import pytest

from agentbay import AgentBay


class TestBetaSkillsMetadata(unittest.TestCase):
    @pytest.mark.sync
    def test_agentbay_has_beta_skills(self):
        with patch("agentbay._sync.agentbay._load_config") as mock_load_config, patch(
            "agentbay._sync.agentbay.mcp_client"
        ) as mock_mcp_client:
            mock_load_config.return_value = {
                "endpoint": "test.endpoint.com",
                "timeout_ms": 30000,
                "region_id": None,
            }
            mock_mcp_client.return_value = MagicMock()
            agent_bay = AgentBay(api_key="test-key")
            assert hasattr(agent_bay, "beta")
            assert hasattr(agent_bay.beta, "skills")

    @pytest.mark.sync
    def test_list_metadata_parses_response(self):
        with patch("agentbay._sync.agentbay._load_config") as mock_load_config, patch(
            "agentbay._sync.agentbay.mcp_client"
        ) as mock_mcp_client:
            mock_load_config.return_value = {
                "endpoint": "test.endpoint.com",
                "timeout_ms": 30000,
                "region_id": None,
            }
            mock_mcp_client.return_value = MagicMock()
            agent_bay = AgentBay(api_key="test-key")

            agent_bay.client = MagicMock()
            captured = {}

            def _fake_list_skill_meta_data(req):
                captured["authorization"] = getattr(req, "authorization", None)

                body = MagicMock()
                body.success = True
                body.code = ""
                body.message = ""
                item1 = MagicMock()
                item1.name = "sandbox-env-audit"
                item1.description = "Generate a sandbox report"
                item2 = MagicMock()
                item2.name = "empty-desc"
                item2.description = ""
                body.data = [item1, item2]

                resp = MagicMock()
                resp.body = body
                return resp

            agent_bay.client.list_skill_meta_data = MagicMock(side_effect=_fake_list_skill_meta_data)

            items = agent_bay.beta.skills.list_metadata()
            assert captured["authorization"] == "Bearer test-key"

            assert isinstance(items, list)
            assert items[0]["name"] == "sandbox-env-audit"
            assert items[0]["description"] == "Generate a sandbox report"
            assert "dir" not in items[0]
            assert items[1]["name"] == "empty-desc"
            assert items[1]["description"] == ""
            assert "dir" not in items[1]

