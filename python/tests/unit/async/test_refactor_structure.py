import asyncio
import inspect
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

# We'll import from the package after refactoring
# For now, we expect these imports to work once refactored
try:
    from agentbay._async.agentbay import AsyncAgentBay, AsyncAgentBay, AsyncSession, Session
except ImportError:
    pass


@pytest.mark.asyncio
async def test_async_agentbay_structure():
    # Verify AsyncAgentBay exists and has async create method
    assert inspect.isclass(AsyncAgentBay)
    assert asyncio.iscoroutinefunction(AsyncAgentBay.create)

    # Mock client
    with patch("agentbay.api.client.Client") as MockClient:
        agent = AsyncAsyncAgentBay(api_key="test")
        assert agent is not None


def test_sync_agentbay_structure():
    # Verify AgentBay exists and has sync create method
    assert inspect.isclass(AgentBay)
    assert not asyncio.iscoroutinefunction(AgentBay.create)

    # Mock client
    with patch("agentbay.api.client.Client") as MockClient:
        agent = AsyncAgentBay(api_key="test")
        assert agent is not None


@pytest.mark.asyncio
async def test_async_session_structure():
    assert inspect.isclass(AsyncSession)
    # Check if delete is async
    assert asyncio.iscoroutinefunction(AsyncSession.delete)


def test_sync_session_structure():
    assert inspect.isclass(Session)
    # Check if delete is sync
    assert not asyncio.iscoroutinefunction(Session.delete)
