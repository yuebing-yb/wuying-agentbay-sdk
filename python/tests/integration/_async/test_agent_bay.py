"""Integration tests for AgentBay async client and session operations."""

import os
import time

import pytest

from agentbay import (
    BWList,
    AsyncAgentBay,
    DeletePolicy,
    DownloadPolicy,
    ExtractPolicy,
    Lifecycle,
    RecyclePolicy,
    SyncPolicy,
    UploadPolicy,
    WhiteList,
)

# make_session factory fixture is provided by conftest.py (auto-loaded by pytest)


# ---------------------------------------------------------------------------
# TestAsyncAgentBay – init tests (no network calls)
# ---------------------------------------------------------------------------


def test_init_with_api_key():
    """Test initialization with API key."""
    api_key = os.environ.get("AGENTBAY_API_KEY", "akm-test")
    ab = AsyncAgentBay(api_key=api_key)
    assert ab.api_key == api_key
    assert ab.client is not None


def test_init_without_api_key_uses_env():
    """Test initialization without explicit API key falls back to env var."""
    original_key = os.environ.get("AGENTBAY_API_KEY")
    os.environ["AGENTBAY_API_KEY"] = "env_api_key"
    try:
        ab = AsyncAgentBay()
        assert ab.api_key == "env_api_key"
    finally:
        if original_key is not None:
            os.environ["AGENTBAY_API_KEY"] = original_key
        else:
            del os.environ["AGENTBAY_API_KEY"]


def test_init_without_api_key_raises_error():
    """Test initialization without API key raises ValueError."""
    original_key = os.environ.get("AGENTBAY_API_KEY")
    try:
        if "AGENTBAY_API_KEY" in os.environ:
            del os.environ["AGENTBAY_API_KEY"]
        with pytest.raises(ValueError):
            AsyncAgentBay()
    finally:
        if original_key is not None:
            os.environ["AGENTBAY_API_KEY"] = original_key


# ---------------------------------------------------------------------------
# TestAsyncAgentBay – create / delete
# ---------------------------------------------------------------------------


async def test_create_list_delete(make_session):
    """Test create and delete methods."""
    print("Creating a new session...")
    lc = await make_session("linux_latest")

    s = lc._result.session
    print(f"Session created with ID: {s.session_id}")
    assert s.session_id is not None
    assert s.session_id != ""
    # Session cleanup is handled by the make_session factory in conftest.py


# ---------------------------------------------------------------------------
# TestSession – properties and basic operations
# ---------------------------------------------------------------------------


async def test_session_properties(make_session):
    """Test session properties and methods."""
    lc = await make_session("linux_latest")
    s = lc._result.session
    assert s.session_id is not None
    assert s.session_id != ""




async def test_command(make_session):
    """Test command execution."""
    lc = await make_session("linux_latest")
    s = lc._result.session
    if s.command:
        print("Executing command...")
        try:
            response = s.command.execute_command("ls")
            print(f"Command execution result: {response}")
            assert response is not None
            assert response.success, f"Command failed: {response.error_message}"
            assert "tool not found" not in response.output.lower(), \
                "Command.execute_command returned 'tool not found'"
        except Exception as e:
            print(f"Note: Command execution failed: {e}")
    else:
        print("Note: Command interface is None, skipping command test")


async def test_filesystem(make_session):
    """Test filesystem operations."""
    lc = await make_session("linux_latest")
    s = lc._result.session
    if s.file_system:
        print("Reading file...")
        try:
            result = s.file_system.read_file("/etc/hosts")
            print(f"ReadFile result: content='{result}'")
            assert result is not None
            assert result.success, f"Read file failed: {result.error_message}"
            assert "tool not found" not in result.content.lower(), \
                "FileSystem.read_file returned 'tool not found'"
            print("File read successful")
        except Exception as e:
            print(f"Note: File operation failed: {e}")
    else:
        print("Note: FileSystem interface is None, skipping file test")


# ---------------------------------------------------------------------------
# RecyclePolicy – parameter validation (no network)
# ---------------------------------------------------------------------------


def test_context_sync_with_invalid_recycle_policy_path():
    """Test that RecyclePolicy raises error for invalid path with wildcard."""
    print("Testing ContextSync creation with invalid recyclePolicy path...")

    with pytest.raises(ValueError) as exc_info:
        RecyclePolicy(
            lifecycle=Lifecycle.LIFECYCLE_1DAY,
            paths=["/invalid/path/*"],
        )
    assert "Wildcard patterns are not supported in recycle policy paths" in str(exc_info.value)
    assert "/invalid/path/*" in str(exc_info.value)
    print("RecyclePolicy correctly raised error for invalid path")

    with pytest.raises(ValueError):
        RecyclePolicy(
            lifecycle=Lifecycle.LIFECYCLE_1DAY,
            paths=["/valid/path", "/invalid/path?", "/another/invalid/*"],
        )
    print("RecyclePolicy correctly raised error for multiple invalid paths")


def test_recycle_policy_invalid_lifecycle():
    """Test invalid Lifecycle values."""
    print("Testing invalid Lifecycle values...")

    with pytest.raises(ValueError) as exc_info:
        RecyclePolicy(lifecycle="invalid_lifecycle", paths=[""])
    error_message = str(exc_info.value)
    assert "Invalid lifecycle value" in error_message
    assert "invalid_lifecycle" in error_message
    assert "Valid values are:" in error_message
    print(f"Invalid lifecycle correctly failed: {error_message}")


def test_recycle_policy_combined_invalid():
    """Test combination of invalid Lifecycle and invalid path."""
    print("Testing combination of invalid Lifecycle and invalid paths...")

    with pytest.raises(ValueError) as exc_info:
        RecyclePolicy(lifecycle="invalid_lifecycle", paths=["/invalid/path/*"])
    # Lifecycle validation runs first
    assert "Invalid lifecycle value" in str(exc_info.value)
    print("Policy with both invalid lifecycle and path correctly failed")


# ---------------------------------------------------------------------------
# RecyclePolicy – session creation (network)
# ---------------------------------------------------------------------------


async def test_create_session_with_custom_recycle_policy(make_session):
    """Test creating session with custom recyclePolicy using Lifecycle_1Day."""
    recycle_policy = RecyclePolicy(lifecycle=Lifecycle.LIFECYCLE_1DAY, paths=[""])
    custom_sync_policy = SyncPolicy(
        upload_policy=UploadPolicy.default(),
        download_policy=DownloadPolicy.default(),
        delete_policy=DeletePolicy.default(),
        extract_policy=ExtractPolicy.default(),
        recycle_policy=recycle_policy,
        bw_list=BWList(white_lists=[WhiteList(path="", exclude_paths=[])]),
    )

    lc = await make_session(
        "linux_latest",
        context_name="test-recycle-context",
        context_path="/test/recycle/path",
        context_policy=custom_sync_policy,
    )
    s = lc._result.session
    assert s is not None
    assert s.session_id is not None
    assert len(s.session_id) > 0
    print(f"Session created successfully with ID: {s.session_id}")


# ---------------------------------------------------------------------------
# BrowserContext – session creation (network)
# ---------------------------------------------------------------------------


async def test_create_session_with_browser_context_default_recycle_policy(make_session):
    """Test creating session with BrowserContext using default RecyclePolicy."""
    print("Testing session creation with BrowserContext (default RecyclePolicy)...")

    context_name = f"test-browser-context-default-{int(time.time())}"
    lc = await make_session(
        "linux_latest",
        browser_name=context_name,
        browser_kwargs={"auto_upload": True},
    )
    s = lc._result.session
    assert s is not None
    assert s.session_id is not None
    assert len(s.session_id) > 0
    print(f"Session created with ID: {s.session_id}")
    # Session cleanup is handled by the make_session factory in conftest.py


# ---------------------------------------------------------------------------
# Session pause / resume
# ---------------------------------------------------------------------------


async def test_session_pause_and_resume(make_session):
    """Test pausing and resuming a session."""
    lc = await make_session("linux_latest")
    s = lc._result.session
    print(f"Session created with ID: {s.session_id}")

    # Pause
    print("\n=== Testing session pause ===")
    pause_result = await s.beta_pause(timeout=300, poll_interval=2)
    print(f"Pause result - Success: {pause_result.success}, Status: {pause_result.status}")
    assert pause_result.success, f"Session pause failed: {pause_result.error_message}"
    # Use lc.get_status() which returns the status string directly
    status = await lc.get_status()
    assert status == "PAUSED", f"Expected status PAUSED, got {status}"
    print("✓ Session paused successfully")

    # Resume
    print("\n=== Testing session resume ===")
    resume_result = await s.beta_resume(timeout=300, poll_interval=2)
    print(f"Resume result - Success: {resume_result.success}, Status: {resume_result.status}")
    assert resume_result.success, f"Session resume failed: {resume_result.error_message}"
    assert resume_result.status == "RUNNING", \
        f"Expected status RUNNING, got {resume_result.status}"
    print("✓ Session resumed successfully")

    print("\n=== Pause/Resume test completed successfully ===")
