"""Integration tests for context synchronization."""
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


@pytest_asyncio.fixture
async def test_session(agent_bay):
    result = await agent_bay.create()
    assert result.success
    yield result.session
    await result.session.delete()


@pytest.mark.asyncio
async def test_context_sync_status(test_session):
    """Test context synchronization status retrieval."""
    # Get context info to check sync status
    context_info = await test_session.context.info()

    assert context_info is not None
    assert context_info.request_id != ""

    # The test just verifies we can retrieve context info successfully
    # context_status_data may be empty if no sync operations are in progress
    print(f"Context sync test completed, found {len(context_info.context_status_data)} status entries")


