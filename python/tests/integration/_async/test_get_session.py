import os

import pytest
import pytest_asyncio

from agentbay import AsyncAgentBay
from agentbay._common.params.session_params import CreateSessionParams


@pytest_asyncio.fixture(scope="module")
async def agent_bay():
    """Create AgentBay instance for testing."""
    api_key = os.environ.get("AGENTBAY_API_KEY")
    if not api_key:
        pytest.skip("AGENTBAY_API_KEY environment variable not set")

    return AsyncAgentBay(api_key=api_key)


@pytest.mark.asyncio
async def test_get_session_by_id(agent_bay):
    """Test getting a session by ID."""
    # Create a session first
    create_result = await agent_bay.create()
    assert create_result.success
    session_id = create_result.session.session_id
    print(f"Created session: {session_id}")

    # Get the session by ID
    get_result = await agent_bay.get(session_id)
    assert get_result.success
    assert get_result.session is not None
    assert get_result.session.session_id == session_id
    print(f"Successfully retrieved session: {session_id}")

    # Clean up
    await create_result.session.delete()


@pytest.mark.asyncio
async def test_get_nonexistent_session(agent_bay):
    """Test getting a non-existent session."""
    fake_session_id = "s-nonexistent12345"
    get_result = await agent_bay.get(fake_session_id)

    # Should fail or return None
    assert not get_result.success or get_result.session is None
    print("Correctly handled non-existent session")


@pytest.mark.asyncio
async def test_list_sessions(agent_bay):
    """Test listing sessions."""
    # Create a session
    create_result = await agent_bay.create()
    assert create_result.success
    session_id = create_result.session.session_id

    # List sessions
    list_result = await agent_bay.list()
    assert list_result.success
    assert list_result.session_ids is not None
    assert len(list_result.session_ids) > 0

    # Check if our session is in the list
    assert session_id in list_result.session_ids
    print(f"Found {len(list_result.session_ids)} sessions")

    # Clean up
    await create_result.session.delete()


@pytest.mark.asyncio
async def test_session_info(agent_bay):
    """Test getting session information."""
    # Create a session
    create_result = await agent_bay.create()
    assert create_result.success
    session = create_result.session

    # Verify session has basic info
    assert session.session_id is not None
    assert session.session_id != ""
    print(f"Session info retrieved: {session.session_id}")

    # Clean up
    await session.delete()
