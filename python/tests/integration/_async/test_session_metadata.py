"""Integration tests for session metadata.
ci-stable
"""

import os

import pytest
import pytest_asyncio

from agentbay import AsyncAgentBay
from agentbay import CreateSessionParams


@pytest_asyncio.fixture
async def agent_bay():
    api_key = os.environ.get("AGENTBAY_API_KEY")
    print(f"Creating agent bay client with api key: {api_key}")
    if not api_key:
        pytest.skip("AGENTBAY_API_KEY environment variable not set")
    return AsyncAgentBay(api_key=api_key)


@pytest.mark.asyncio
async def test_session_with_metadata(agent_bay):
    """Test creating session with labels."""
    params = CreateSessionParams(
        image_id="code_latest",
        labels={"test_key": "test_value", "environment": "testing"},
    )
    result = await agent_bay.create(params)
    print(f"Session created with labels: {result.request_id}")
    assert result.success

    session = result.session
    print(f"Session created with labels: {session.session_id}")

    await session.delete()


@pytest.mark.asyncio
async def test_session_basic_attributes(agent_bay):
    """Test session basic attributes."""
    result = await agent_bay.create()
    assert result.success

    session = result.session
    assert session.session_id is not None
    assert session.agent_bay is agent_bay
    print(f"Session attributes verified: {session.session_id}")

    await session.delete()
