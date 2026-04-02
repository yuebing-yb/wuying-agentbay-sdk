"""Integration test for ListSkillMetaData POP action.

This test calls the real backend without mocks.
"""
# ci-stable

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
async def test_beta_skills_list_metadata(agent_bay: AsyncAgentBay):
    items = await agent_bay.beta.skills.list_metadata()
    assert isinstance(items, list)
    assert len(items) > 0
    first = items[0]
    assert isinstance(first.get("name"), str) and first["name"].strip()
    assert isinstance(first.get("description"), str)
    assert "dir" not in first

