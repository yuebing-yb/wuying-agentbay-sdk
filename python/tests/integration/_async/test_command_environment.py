"""Integration tests for command environment variables."""

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
async def test_command_with_env_vars(test_session):
    """Test command execution with environment variables."""
    cmd = test_session.command
    result = await cmd.execute_command("export TEST_VAR='hello' && echo $TEST_VAR")
    assert result.success
    assert "hello" in result.output
    print("Command with env vars executed successfully")


@pytest.mark.asyncio
async def test_command_path_env(test_session):
    """Test PATH environment variable."""
    cmd = test_session.command
    result = await cmd.execute_command("echo $PATH")
    assert result.success
    assert len(result.output) > 0
    print(f"PATH: {result.output[:100]}...")
