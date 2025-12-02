import time
import inspect
from unittest.mock import MagicMock, MagicMock, patch

import pytest

# We'll import from the package after refactoring
# For now, we expect these imports to work once refactored
try:
    from agentbay import AgentBay
    from agentbay import SyncSession
    from agentbay import AgentBay
    from agentbay import Session
except ImportError:
    pass


@pytest.mark.time
def test_async_agentbay_structure():
    # Verify AsyncAgentBay exists and has async create method
    assert inspect.isclass(AgentBay)
    assert time.iscoroutinefunction(AgentBay.create)

    # Mock client
    with patch("agentbay.api.client.Client") as MockClient:
        agent = AgentBay(api_key="test")
        assert agent is not None


def test_sync_agentbay_structure():
    # Verify AgentBay exists and has sync create method
    assert inspect.isclass(AgentBay)
    assert not time.iscoroutinefunction(AgentBay.create)

    # Mock client
    with patch("agentbay.api.client.Client") as MockClient:
        agent = AgentBay(api_key="test")
        assert agent is not None


@pytest.mark.time
def test_async_session_structure():
    assert inspect.isclass(SyncSession)
    # Check if delete is async
    assert time.iscoroutinefunction(SyncSession.delete)


def test_sync_session_structure():
    assert inspect.isclass(Session)
    # Check if delete is sync
    assert not time.iscoroutinefunction(Session.delete)
