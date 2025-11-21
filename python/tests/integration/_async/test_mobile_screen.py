"""Integration tests for Mobile screen operations functionality."""
import os
import pytest
import pytest_asyncio

from agentbay import AsyncAgentBay
from agentbay.session_params import CreateSessionParams


@pytest_asyncio.fixture(scope="module")
async def agent_bay():
    """Create AsyncAgentBay instance."""
    api_key = os.environ.get("AGENTBAY_API_KEY")
    if not api_key:
        pytest.skip("AGENTBAY_API_KEY environment variable not set")
    return AsyncAgentBay(api_key=api_key)


@pytest_asyncio.fixture
async def session(agent_bay):
    """Create a session with mobile_latest image."""
    print("\nCreating session for mobile screen testing...")
    session_param = CreateSessionParams(image_id="mobile_latest")
    result = await agent_bay.create(session_param)
    assert result.success, f"Failed to create session: {result.error_message}"
    session = result.session
    print(f"Session created with ID: {session.session_id}")
    yield session
    print("\nCleaning up: Deleting the session...")
    await session.delete()


@pytest.mark.asyncio
async def test_take_screenshot(session):
    """Test mobile screenshot functionality."""
    # Arrange
    print("\nTest: Taking mobile screenshot...")

    # Act
    result = await session.mobile.screenshot()

    # Assert
    assert result.success, f"Screenshot failed: {result.error_message}"
    assert result.data is not None, "Screenshot data should not be None"
    assert isinstance(result.data, str), "Screenshot data should be a string (URL)"
    assert len(result.data) > 0, "Screenshot URL should not be empty"
    print(f"Screenshot taken successfully: {result.data}")


@pytest.mark.asyncio
async def test_get_device_info(session):
    """Test getting mobile device information."""
    # Arrange
    print("\nTest: Getting device info...")

    # Act - Use command to get device info
    result = await session.command.execute_command("getprop ro.product.model")

    # Assert
    assert result.success, f"Get device info failed: {result.error_message}"
    assert result.output is not None, "Device info should not be None"
    print(f"Device model: {result.output.strip()}")

