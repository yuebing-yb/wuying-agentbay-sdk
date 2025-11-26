"""Integration tests for command timeout."""

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
async def test_command_with_timeout(test_session):
    """Test command execution with timeout."""
    cmd = test_session.command
    result = await cmd.execute_command(
        "echo 'test' && sleep 1 && echo 'done'", timeout_ms=5000
    )
    assert result.success
    assert "test" in result.output
    assert "done" in result.output
    print("Command with timeout executed successfully")


@pytest.mark.asyncio
async def test_command_quick_execution(test_session):
    """Test quick command execution."""
    cmd = test_session.command
    result = await cmd.execute_command("echo 'quick'", timeout_ms=1000)
    assert result.success
    assert "quick" in result.output
    print("Quick command executed successfully")
