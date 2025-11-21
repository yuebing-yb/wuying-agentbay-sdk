"""Integration tests for different session images."""
import os
import pytest
import pytest_asyncio

from agentbay import AsyncAgentBay
from agentbay.session_params import CreateSessionParams


@pytest_asyncio.fixture(scope="module")
async def agent_bay():
    api_key = os.environ.get("AGENTBAY_API_KEY")
    if not api_key:
        pytest.skip("AGENTBAY_API_KEY environment variable not set")
    return AsyncAgentBay(api_key=api_key)


@pytest.mark.asyncio
async def test_ubuntu_session(agent_bay):
    """Test creating Ubuntu session."""
    params = CreateSessionParams(image_id="linux_latest")
    result = await agent_bay.create(params)
    assert result.success
    
    session = result.session
    print(f"Ubuntu session created: {session.session_id}")
    
    # Test basic command
    cmd_result = await session.command.execute_command("uname -a")
    assert cmd_result.success
    print(f"OS info: {cmd_result.output[:50]}...")
    
    await session.delete()


@pytest.mark.asyncio
async def test_browser_session(agent_bay):
    """Test creating browser session."""
    params = CreateSessionParams(image_id="browser_latest")
    result = await agent_bay.create(params)
    assert result.success
    
    session = result.session
    print(f"Browser session created: {session.session_id}")
    
    await session.delete()


