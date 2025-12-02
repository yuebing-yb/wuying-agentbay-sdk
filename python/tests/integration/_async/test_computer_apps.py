"""Integration tests for Computer application management functionality."""

import os

import pytest
import pytest_asyncio

from agentbay import AsyncAgentBay
from agentbay import CreateSessionParams


@pytest_asyncio.fixture(scope="module")
async def agent_bay():
    """Create AsyncAgentBay instance."""
    api_key = os.environ.get("AGENTBAY_API_KEY")
    if not api_key:
        pytest.skip("AGENTBAY_API_KEY environment variable not set")
    return AsyncAgentBay(api_key=api_key)


@pytest_asyncio.fixture
async def session(agent_bay):
    """Create a session with windows_latest image."""
    print("\nCreating session for computer apps testing...")
    session_param = CreateSessionParams(image_id="windows_latest")
    result = await agent_bay.create(session_param)
    assert result.success, f"Failed to create session: {result.error_message}"
    session = result.session
    print(f"Session created with ID: {session.session_id}")
    yield session
    print("\nCleaning up: Deleting the session...")
    await session.delete()


@pytest.mark.asyncio
async def test_get_installed_apps(session):
    """Test getting list of installed applications."""
    # Arrange
    print("\nTest: Getting installed apps...")

    # Act
    result = await session.computer.get_installed_apps()

    # Assert
    assert result.success, f"Get installed apps failed: {result.error_message}"
    assert result.data is not None, "Apps list should not be None"
    assert isinstance(result.data, list), "Apps should be a list"
    print(f"Found {len(result.data)} installed apps")

    if len(result.data) > 0:
        app = result.data[0]
        assert hasattr(app, "name"), "App should have name"
        assert hasattr(app, "start_cmd"), "App should have start_cmd"
        print(f"First app: {app.name}")


@pytest.mark.asyncio
async def test_start_app(session):
    """Test starting an application."""
    # Arrange
    print("\nTest: Starting notepad app...")

    # Act - Try to start notepad (should be available on Windows)
    result = await session.computer.start_app("notepad.exe")

    # Assert
    assert result.success, f"Start app failed: {result.error_message}"
    assert result.data is not None, "Process list should not be None"
    assert isinstance(result.data, list), "Processes should be a list"
    print(f"Started {len(result.data)} process(es)")

    if len(result.data) > 0:
        process = result.data[0]
        assert hasattr(process, "pname"), "Process should have pname"
        assert hasattr(process, "pid"), "Process should have pid"
        print(f"Process: {process.pname}, PID: {process.pid}")


@pytest.mark.asyncio
async def test_stop_app(session):
    """Test stopping an application."""
    # Arrange
    print("\nTest: Stopping notepad app...")

    # Start notepad first
    start_result = await session.computer.start_app("notepad.exe")
    assert start_result.success, "Failed to start notepad for test"

    # Act - Stop notepad
    result = await session.computer.stop_app_by_pname("notepad.exe")

    # Assert
    assert result.success, f"Stop app failed: {result.error_message}"
    print("App stopped successfully")
