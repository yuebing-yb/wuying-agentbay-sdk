import os

import pytest

from agentbay import AsyncAgentBay, CreateSessionParams
from agentbay import AsyncSession


@pytest.fixture(scope="module")
def agentbay_client():
    api_key = os.getenv("AGENTBAY_API_KEY")
    if not api_key:
        pytest.fail("AGENTBAY_API_KEY environment variable is not set")
    return AsyncAgentBay(api_key=api_key)


async def test_get_api(agentbay_client: AsyncAgentBay):
    """Test Get API with a real session."""
    print("Creating a new session for Get API testing...")

    # Create session
    create_result = await agentbay_client.create()
    assert (
        create_result.success
    ), f"Failed to create session: {create_result.error_message}"
    created_session = create_result.session
    session_id = created_session.session_id
    print(f"Session created with ID: {session_id}")

    print("Testing Get API...")
    result = await agentbay_client.get(session_id)

    assert result is not None, "Get returned None result"
    assert result.success, f"Failed to get session: {result.error_message}"
    session = result.session
    assert session is not None, "Get returned None session"
    assert isinstance(
        session, AsyncSession
    ), f"Expected AsyncSession instance, got {type(session)}"
    assert (
        session.session_id == session_id
    ), f"Expected SessionID {session_id}, got {session.session_id}"
    assert session.agent_bay is not None, "Session agent_bay reference is None"

    print(f"Successfully retrieved session with ID: {session.session_id}")
    print("Get API test passed successfully")

    print("Cleaning up: Deleting the session...")
    delete_result = await session.delete()
    assert delete_result.success, f"Failed to delete session: {delete_result.success}"
    print(f"Session {session_id} deleted successfully")


async def test_get_non_existent_session(agentbay_client: AsyncAgentBay):
    """Test Get API with a non-existent session ID."""
    print("Testing Get API with non-existent session ID...")
    non_existent_session_id = "session-nonexistent-12345"

    result = await agentbay_client.get(non_existent_session_id)
    assert not result.success, "Expected get() to fail for non-existent session"
    assert "Failed to get session" in result.error_message
    print(f"Correctly received error for non-existent session: {result.error_message}")
    print("Get API non-existent session test passed successfully")


async def test_get_empty_session_id(agentbay_client: AsyncAgentBay):
    """Test Get API with empty session ID."""
    print("Testing Get API with empty session ID...")

    result = await agentbay_client.get("")
    assert not result.success, "Expected get() to fail for empty session ID"
    assert "session_id is required" in result.error_message
    print(f"Correctly received error for empty session ID: {result.error_message}")
    print("Get API empty session ID test passed successfully")


async def test_get_whitespace_session_id(agentbay_client: AsyncAgentBay):
    """Test Get API with whitespace-only session ID."""
    print("Testing Get API with whitespace session ID...")

    result = await agentbay_client.get("   ")
    assert not result.success, "Expected get() to fail for whitespace session ID"
    assert "session_id is required" in result.error_message
    print(f"Correctly received error for whitespace session ID: {result.error_message}")
    print("Get API whitespace session ID test passed successfully")
