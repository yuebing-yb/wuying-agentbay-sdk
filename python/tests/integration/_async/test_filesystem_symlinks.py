"""Integration tests for filesystem symlinks."""
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
async def test_create_symlink(test_session):
    """Test creating a symlink."""
    fs = test_session.file_system
    cmd = test_session.command
    
    # Create original file
    await fs.write_file("/tmp/original.txt", "original content")
    
    # Create symlink
    result = await cmd.execute_command("ln -s /tmp/original.txt /tmp/link.txt")
    assert result.success
    
    # Read through symlink
    read_result = await fs.read_file("/tmp/link.txt")
    assert read_result.success
    assert read_result.content == "original content"
    print("Symlink creation successful")


@pytest.mark.asyncio
async def test_symlink_to_directory(test_session):
    """Test symlink to directory."""
    fs = test_session.file_system
    cmd = test_session.command
    
    # Create directory with file
    await fs.create_directory("/tmp/orig_dir")
    await fs.write_file("/tmp/orig_dir/file.txt", "dir content")
    
    # Create symlink to directory
    result = await cmd.execute_command("ln -s /tmp/orig_dir /tmp/link_dir")
    assert result.success
    
    # Read file through symlink
    read_result = await fs.read_file("/tmp/link_dir/file.txt")
    assert read_result.success
    assert read_result.content == "dir content"
    print("Directory symlink successful")


