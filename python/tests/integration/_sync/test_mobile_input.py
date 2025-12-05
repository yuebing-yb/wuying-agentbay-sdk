"""Integration tests for Mobile input operations functionality."""

import os

import pytest
import pytest_asyncio

from agentbay import AgentBay
from agentbay import CreateSessionParams
from agentbay import KeyCode


@pytest_asyncio.fixture(scope="module")
def agent_bay():
    """Create AsyncAgentBay instance."""
    api_key = os.environ.get("AGENTBAY_API_KEY")
    if not api_key:
        pytest.skip("AGENTBAY_API_KEY environment variable not set")
    return AgentBay(api_key=api_key)


@pytest_asyncio.fixture
def session(agent_bay):
    """Create a session with mobile_latest image."""
    print("\nCreating session for mobile input testing...")
    session_param = CreateSessionParams(image_id="mobile_latest")
    result = agent_bay.create(session_param)
    assert result.success, f"Failed to create session: {result.error_message}"
    session = result.session
    print(f"Session created with ID: {session.session_id}")
    yield session
    print("\nCleaning up: Deleting the session...")
    session.delete()


@pytest.mark.asyncio
def test_tap(session):
    """Test tap operation."""
    # Arrange
    print("\nTest: Tap operation...")

    # Act - Tap at center of screen
    result = session.mobile.tap(500, 800)

    # Assert
    assert result.success, f"Tap failed: {result.error_message}"
    assert result.data is True, "Tap should return True"
    print("Tap operation successful")


@pytest.mark.asyncio
def test_swipe(session):
    """Test swipe operation."""
    # Arrange
    print("\nTest: Swipe operation...")

    # Act - Swipe from bottom to top
    result = session.mobile.swipe(500, 1500, 500, 500, duration_ms=500)

    # Assert
    assert result.success, f"Swipe failed: {result.error_message}"
    assert result.data is True, "Swipe should return True"
    print("Swipe operation successful")


@pytest.mark.asyncio
def test_input_text(session):
    """Test text input operation."""
    # Arrange
    print("\nTest: Text input...")
    test_text = "Hello Mobile"

    # Act
    result = session.mobile.input_text(test_text)

    # Assert
    assert result.success, f"Input text failed: {result.error_message}"
    assert result.data is True, "Input should return True"
    print(f"Text input successful: '{test_text}'")


@pytest.mark.asyncio
def test_press_key(session):
    """Test key press operation."""
    # Arrange
    print("\nTest: Press HOME key...")

    # Act - Press HOME key
    result = session.mobile.send_key(KeyCode.KEYCODE_HOME)

    # Assert
    assert result.success, f"Press key failed: {result.error_message}"
    assert result.data is True, "Press key should return True"
    print("Key press successful")
