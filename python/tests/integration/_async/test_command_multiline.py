"""Integration tests for multiline commands."""

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
async def test_multiline_script(test_session):
    """Test executing multiline script."""
    cmd = test_session.command

    script = """
for i in 1 2 3; do
    echo "Number: $i"
done
"""
    result = await cmd.execute_command(script)
    assert result.success
    assert "Number: 1" in result.output
    assert "Number: 2" in result.output
    assert "Number: 3" in result.output
    print("Multiline script executed successfully")


@pytest.mark.asyncio
async def test_command_with_conditionals(test_session):
    """Test command with if-else."""
    cmd = test_session.command

    script = """
if [ -d /tmp ]; then
    echo "tmp exists"
else
    echo "tmp not found"
fi
"""
    result = await cmd.execute_command(script)
    assert result.success
    assert "tmp exists" in result.output
    print("Conditional command executed successfully")


@pytest.mark.asyncio
async def test_command_with_functions(test_session):
    """Test command with bash functions."""
    cmd = test_session.command

    script = """
test_function() {
    echo "Function called with: $1"
}
test_function "hello"
"""
    result = await cmd.execute_command(script)
    assert result.success
    assert "Function called with: hello" in result.output
    print("Function command executed successfully")
