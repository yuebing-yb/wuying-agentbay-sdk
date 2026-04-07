"""Integration test for skills.get_metadata() via GetSkillMetaData POP action.
ci-stable

This test calls the real backend without mocks.
"""

import os

import pytest
import pytest_asyncio

from agentbay import AsyncAgentBay


@pytest_asyncio.fixture(scope="module")
async def agent_bay():
    api_key = os.environ.get("AGENTBAY_API_KEY")
    if not api_key:
        pytest.skip("AGENTBAY_API_KEY environment variable not set")
    return AsyncAgentBay(api_key=api_key)


@pytest.mark.asyncio
async def test_get_metadata_returns_skills_root_path(agent_bay: AsyncAgentBay):
    """get_metadata() should return SkillsMetadataResult with skills_root_path."""
    result = await agent_bay.beta_skills.get_metadata()

    assert result is not None
    assert isinstance(result.skills_root_path, str)
    assert len(result.skills_root_path) > 0, "skills_root_path should not be empty"
    assert isinstance(result.skills, list)


@pytest.mark.asyncio
async def test_get_metadata_with_skill_names(agent_bay: AsyncAgentBay):
    """get_metadata(skill_names=[...]) should not raise errors."""
    result = await agent_bay.beta_skills.get_metadata(skill_names=["non-existent-skill"])
    assert result is not None
    assert isinstance(result.skills, list)
    assert isinstance(result.skills_root_path, str)


@pytest.mark.asyncio
async def test_get_metadata_with_image_id(agent_bay: AsyncAgentBay):
    """get_metadata(image_id=...) should return skills_root_path for that image."""
    result = await agent_bay.beta_skills.get_metadata(image_id="linux_latest")
    assert result is not None
    assert isinstance(result.skills_root_path, str)
    assert len(result.skills_root_path) > 0
