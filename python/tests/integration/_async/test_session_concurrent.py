"""Integration tests for concurrent session operations."""

import asyncio
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


@pytest.mark.asyncio
async def test_concurrent_file_operations(agent_bay):
    """Test concurrent file operations in same session."""
    result = await agent_bay.create()
    assert result.success
    session = result.session

    fs = session.file_system

    # Concurrent writes
    tasks = [
        fs.write_file(f"/tmp/concurrent_{i}.txt", f"content_{i}") for i in range(5)
    ]
    results = await asyncio.gather(*tasks)

    assert all(r.success for r in results)
    print("Concurrent file operations successful")

    await session.delete()


@pytest.mark.asyncio
async def test_concurrent_commands(agent_bay):
    """Test concurrent command execution."""
    result = await agent_bay.create()
    assert result.success
    session = result.session

    cmd = session.command

    # Concurrent commands
    tasks = [cmd.execute_command(f"echo 'test_{i}'") for i in range(3)]
    results = await asyncio.gather(*tasks)

    assert all(r.success for r in results)
    print("Concurrent commands executed successfully")

    await session.delete()
