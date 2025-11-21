import os
import pytest
from agentbay import AsyncAgentBay

@pytest.mark.asyncio
async def test_create_list_delete():
    """Test create, list, and delete methods."""
    api_key = os.environ.get("AGENTBAY_API_KEY")
    if not api_key:
        pytest.skip("AGENTBAY_API_KEY environment variable not set")

    agent_bay = AsyncAgentBay(api_key=api_key)

    # Create a session
    print("Creating a new session...")
    result = await agent_bay.create()
    
    # Check if session creation was successful
    assert result.success, f"Session creation failed: {result.error_message}"
    assert result.session is not None, "Session object is None"
    
    session = result.session
    print(f"Session created with ID: {session.session_id}")

    # Ensure session ID is not empty
    assert session.session_id is not None
    assert session.session_id != ""

    # Delete the session
    print("Deleting the session...")
    await session.delete()

    # Session deletion completed

