"""Unit tests for BetaSkillsService (get_metadata)."""

import pytest
from unittest.mock import MagicMock, MagicMock, patch


@pytest.mark.sync
def test_agentbay_has_beta_skills():
    """AgentBay should have a 'beta_skills' attribute of type AsyncBetaSkillsService."""
    with patch("agentbay._sync.agentbay._load_config") as mock_load_config, \
         patch("agentbay._sync.agentbay.mcp_client") as mock_mcp_client:
        mock_load_config.return_value = {
            "endpoint": "test.endpoint.com",
            "timeout_ms": 30000,
            "region_id": None,
        }
        mock_mcp_client.return_value = MagicMock()
        from agentbay import AgentBay
        agent_bay = AgentBay(api_key="test-key")
        assert hasattr(agent_bay, "beta_skills")
        from agentbay._sync.beta import SyncBetaSkillsService
        assert isinstance(agent_bay.beta_skills, SyncBetaSkillsService)


@pytest.mark.sync
def test_get_metadata_parses_response():
    """get_metadata() should parse API response into SkillsMetadataResult."""
    with patch("agentbay._sync.agentbay._load_config") as mock_load_config, \
         patch("agentbay._sync.agentbay.mcp_client") as mock_mcp_client:
        mock_load_config.return_value = {
            "endpoint": "test.endpoint.com",
            "timeout_ms": 30000,
            "region_id": None,
        }
        mock_mcp_client.return_value = MagicMock()
        from agentbay import AgentBay
        agent_bay = AgentBay(api_key="test-key")

        body = MagicMock()
        body.success = True
        body.code = ""
        body.message = ""

        data = MagicMock()
        data.skill_path = "/home/wuying/skills"

        item1 = MagicMock()
        item1.name = "pdf"
        item1.description = "PDF processing skill"
        item2 = MagicMock()
        item2.name = "docx"
        item2.description = "Word document skill"
        data.meta_data_list = [item1, item2]

        body.data = data

        resp = MagicMock()
        resp.body = body

        agent_bay.client.get_skill_meta_data = MagicMock(return_value=resp)

        result = agent_bay.beta_skills.get_metadata()

        assert result.skills_root_path == "/home/wuying/skills"
        assert len(result.skills) == 2
        assert result.skills[0].name == "pdf"
        assert result.skills[0].description == "PDF processing skill"
        assert result.skills[1].name == "docx"
        assert result.skills[1].description == "Word document skill"


@pytest.mark.sync
def test_get_metadata_passes_skill_names():
    """get_metadata(skill_names=[...]) should pass SkillGroupIds to the API."""
    with patch("agentbay._sync.agentbay._load_config") as mock_load_config, \
         patch("agentbay._sync.agentbay.mcp_client") as mock_mcp_client:
        mock_load_config.return_value = {
            "endpoint": "test.endpoint.com",
            "timeout_ms": 30000,
            "region_id": None,
        }
        mock_mcp_client.return_value = MagicMock()
        from agentbay import AgentBay
        agent_bay = AgentBay(api_key="test-key")

        captured = {}

        def _fake_get_skill_meta_data(req):
            captured["authorization"] = getattr(req, "authorization", None)
            captured["image_id"] = getattr(req, "image_id", None)
            captured["skill_group_ids"] = getattr(req, "skill_group_ids", None)

            body = MagicMock()
            body.success = True
            body.code = ""
            body.message = ""
            data = MagicMock()
            data.skill_path = "/skills"
            data.meta_data_list = []
            body.data = data
            resp = MagicMock()
            resp.body = body
            return resp

        agent_bay.client.get_skill_meta_data = MagicMock(side_effect=_fake_get_skill_meta_data)

        result = agent_bay.beta_skills.get_metadata(
            skill_names=["grp-001", "grp-002"],
            image_id="my-image",
        )

        assert captured["authorization"] == "Bearer test-key"
        assert captured["skill_group_ids"] == ["grp-001", "grp-002"]
        assert captured["image_id"] == "my-image"
        assert result.skills_root_path == "/skills"
        assert result.skills == []


@pytest.mark.sync
def test_get_metadata_handles_api_failure():
    """get_metadata() should raise when API returns success=False."""
    with patch("agentbay._sync.agentbay._load_config") as mock_load_config, \
         patch("agentbay._sync.agentbay.mcp_client") as mock_mcp_client:
        mock_load_config.return_value = {
            "endpoint": "test.endpoint.com",
            "timeout_ms": 30000,
            "region_id": None,
        }
        mock_mcp_client.return_value = MagicMock()
        from agentbay import AgentBay
        agent_bay = AgentBay(api_key="test-key")

        body = MagicMock()
        body.success = False
        body.code = "InvalidRequest"
        body.message = "Bad group id"
        body.data = None

        resp = MagicMock()
        resp.body = body

        agent_bay.client.get_skill_meta_data = MagicMock(return_value=resp)

        with pytest.raises(RuntimeError, match="GetSkillMetaData failed"):
            agent_bay.beta_skills.get_metadata()


@pytest.mark.sync
def test_get_metadata_skips_empty_names():
    """get_metadata() should skip items with empty names."""
    with patch("agentbay._sync.agentbay._load_config") as mock_load_config, \
         patch("agentbay._sync.agentbay.mcp_client") as mock_mcp_client:
        mock_load_config.return_value = {
            "endpoint": "test.endpoint.com",
            "timeout_ms": 30000,
            "region_id": None,
        }
        mock_mcp_client.return_value = MagicMock()
        from agentbay import AgentBay
        agent_bay = AgentBay(api_key="test-key")

        body = MagicMock()
        body.success = True
        body.code = ""
        body.message = ""

        data = MagicMock()
        data.skill_path = "/skills"

        item1 = MagicMock()
        item1.name = ""
        item1.description = "Should be skipped"
        item2 = MagicMock()
        item2.name = "valid-skill"
        item2.description = "Valid"
        data.meta_data_list = [item1, item2]

        body.data = data
        resp = MagicMock()
        resp.body = body

        agent_bay.client.get_skill_meta_data = MagicMock(return_value=resp)

        result = agent_bay.beta_skills.get_metadata()

        assert len(result.skills) == 1
        assert result.skills[0].name == "valid-skill"
