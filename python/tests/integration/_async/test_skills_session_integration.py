"""Integration test for creating sessions with skills loaded.
ci-stable

This test calls the real backend without mocks.
"""

import os

import pytest
import pytest_asyncio

from agentbay import AsyncAgentBay
from agentbay._common.params.session_params import CreateSessionParams


@pytest_asyncio.fixture(scope="module")
async def agent_bay():
    api_key = os.environ.get("AGENTBAY_API_KEY")
    if not api_key:
        pytest.skip("AGENTBAY_API_KEY environment variable not set")
    return AsyncAgentBay(api_key=api_key)


@pytest.mark.asyncio
async def test_create_session_with_load_skills(agent_bay: AsyncAgentBay):
    """Creating session with load_skills=True should succeed (backend accepts the param)."""
    params = CreateSessionParams(load_skills=True)
    result = await agent_bay.create(params)
    assert result.success, f"Session creation failed: {result.error_message}"
    assert result.session is not None
    try:
        pass
    finally:
        await result.session.delete()


@pytest.mark.asyncio
async def test_create_session_without_skills(agent_bay: AsyncAgentBay):
    """Creating session without load_skills should succeed."""
    params = CreateSessionParams()
    result = await agent_bay.create(params)
    assert result.success, f"Session creation failed: {result.error_message}"
    assert result.session is not None
    try:
        pass
    finally:
        await result.session.delete()
