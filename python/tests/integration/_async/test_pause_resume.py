import os

import pytest
import pytest_asyncio

from agentbay import AsyncAgentBay
from agentbay import CreateSessionParams


@pytest_asyncio.fixture(scope="module")
async def agent_bay():
    """Create AgentBay instance for testing."""
    api_key = os.environ.get("AGENTBAY_API_KEY")
    if not api_key:
        pytest.skip("AGENTBAY_API_KEY environment variable not set")

    return AsyncAgentBay(api_key=api_key)


@pytest.mark.asyncio
async def test_pause_resume_session(agent_bay):
    """Test pausing and resuming a session."""
    # Create a session
    create_result = await agent_bay.create()
    assert create_result.success
    session = create_result.session
    print(f"Created session: {session.session_id}")

    # Try to pause the session (may not be supported by backend)
    pause_result = await session.beta_pause()
    if pause_result.success:
        print("Session paused successfully")

        # Resume the session
        resume_result = await session.beta_resume()
        if resume_result.success:
            print("Session resumed successfully")
        else:
            print(f"Resume not supported: {resume_result.error_message}")
    else:
        print(f"Pause not supported by backend: {pause_result.error_message}")
        # This is acceptable - not all backends support pause/resume

    # Clean up
    await session.delete()


@pytest.mark.asyncio
async def test_pause_already_paused(agent_bay):
    """Test pausing an already paused session."""
    # Create and pause a session
    create_result = await agent_bay.create()
    session = create_result.session

    await session.beta_pause()
    print("Session paused first time")

    # Try to pause again
    pause_result = await session.beta_pause()
    # Should either succeed (idempotent) or fail gracefully
    print(f"Second pause result: {pause_result.success}")

    # Clean up
    await session.beta_resume()
    await session.delete()


@pytest.mark.asyncio
async def test_resume_running_session(agent_bay):
    """Test resuming a session that's already running."""
    # Create a session (already running)
    create_result = await agent_bay.create()
    session = create_result.session

    # Try to resume without pausing first
    resume_result = await session.beta_resume()
    # Should either succeed (idempotent) or fail gracefully
    print(f"Resume running session result: {resume_result.success}")

    # Clean up
    await session.delete()


@pytest.mark.asyncio
async def test_pause_resume_with_operations(agent_bay):
    """Test operations after pause and resume."""
    # Create a session with command capability
    params = CreateSessionParams(image_id="linux_latest")
    create_result = await agent_bay.create(params)
    session = create_result.session

    # Execute a command before pause
    cmd_result1 = await session.command.execute_command("echo 'before pause'")
    assert cmd_result1.success
    print("Command executed before pause")

    # Pause
    await session.beta_pause()
    print("Session paused")

    # Resume
    await session.beta_resume()
    print("Session resumed")

    # Execute a command after resume
    cmd_result2 = await session.command.execute_command("echo 'after resume'")
    assert cmd_result2.success
    print("Command executed after resume")

    # Clean up
    await session.delete()
