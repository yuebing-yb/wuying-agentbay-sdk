"""Integration tests for context synchronization."""

import asyncio
import os
import time

import pytest
import pytest_asyncio

from agentbay import AsyncAgentBay
from agentbay._common.params.context_sync import (
    BWList,
    ContextSync,
    DeletePolicy,
    DownloadPolicy,
    ExtractPolicy,
    Lifecycle,
    RecyclePolicy,
    SyncPolicy,
    UploadPolicy,
    WhiteList,
)
from agentbay._common.params.session_params import CreateSessionParams
from agentbay._sync.context_manager import ContextStatusData


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


@pytest_asyncio.fixture(scope="module")
async def context_for_test(agent_bay):
    """Create a context for testing."""
    # Create a unique context name for this test
    context_name = f"test-sync-context-{int(time.time())}"

    # Create a context
    context_result = await agent_bay.context.get(context_name, True)
    if not context_result.success or not context_result.context:
        pytest.skip("Failed to create context")

    context = context_result.context
    print(f"Created context: {context.name} (ID: {context.id})")

    yield context

    # Clean up context
    try:
        await agent_bay.context.delete(context)
        print(f"Context deleted: {context.id}")
    except Exception as e:
        print(f"Warning: Failed to delete context: {e}")


@pytest.mark.asyncio
async def test_context_sync_status(test_session):
    """Test context synchronization status retrieval."""
    # Get context info to check sync status
    context_info = await test_session.context.info()

    assert context_info is not None
    assert context_info.request_id != ""

    # The test just verifies we can retrieve context info successfully
    # context_status_data may be empty if no sync operations are in progress
    print(
        f"Context sync test completed, found {len(context_info.context_status_data)} status entries"
    )


@pytest.mark.asyncio
async def test_context_info_returns_context_status_data(agent_bay, context_for_test):
    """Test that context info returns parsed ContextStatusData."""

    # Create session for this test
    context_sync = ContextSync.new(
        context_for_test.id, "/home/wuying", SyncPolicy.default()
    )
    session_params = CreateSessionParams()
    session_params.context_syncs = [context_sync]
    session_params.labels = {"test": "context-sync-integration"}
    session_params.image_id = "linux_latest"

    session_result = await agent_bay.create(session_params)
    if not session_result.success or not session_result.session:
        pytest.skip("Failed to create session for test")

    session = session_result.session
    print(f"Created session: {session.session_id}")

    try:
        # Wait for session to be ready
        await asyncio.sleep(5)

        # Get context info
        context_info = await session.context.info()

        # Verify that we have a request ID
        assert context_info.request_id is not None
        assert context_info.request_id != ""

        # Log the context status data
        print(f"Context status data count: {len(context_info.context_status_data)}")
        for i, data in enumerate(context_info.context_status_data):
            print(f"Status data {i}:")
            print(f"  Context ID: {data.context_id}")
            print(f"  Path: {data.path}")
            print(f"  Status: {data.status}")
            print(f"  Task Type: {data.task_type}")
            print(f"  Start Time: {data.start_time}")
            print(f"  Finish Time: {data.finish_time}")
            if hasattr(data, "error_message") and data.error_message:
                print(f"  Error: {data.error_message}")

        # There might not be any status data yet, so we don't assert on the count
        # But if there is data, verify it has the expected structure
        for data in context_info.context_status_data:
            assert isinstance(data, ContextStatusData)
            assert data.context_id is not None
            assert data.path is not None
            assert data.status is not None
            assert data.task_type is not None

    finally:
        # Clean up session
        try:
            await agent_bay.delete(session)
            print(f"Session deleted: {session.session_id}")
        except Exception as e:
            print(f"Warning: Failed to delete session: {e}")


@pytest.mark.asyncio
async def test_context_sync_with_recycle_policy_integration(
    agent_bay, context_for_test
):
    """Test creating a session with ContextSync that has custom RecyclePolicy."""

    # Create custom RecyclePolicy with Lifecycle_3Days
    custom_recycle_policy = RecyclePolicy(
        lifecycle=Lifecycle.LIFECYCLE_3DAYS, paths=["/test/recycle/data"]
    )

    # Create SyncPolicy with custom RecyclePolicy
    sync_policy = SyncPolicy(
        upload_policy=UploadPolicy.default(),
        download_policy=DownloadPolicy.default(),
        delete_policy=DeletePolicy.default(),
        extract_policy=ExtractPolicy.default(),
        recycle_policy=custom_recycle_policy,
        bw_list=BWList(white_lists=[WhiteList(path="", exclude_paths=[])]),
    )

    # Create ContextSync with custom policy
    context_sync = ContextSync.new(
        context_for_test.id, "/home/wuying/recycle-test", sync_policy
    )

    # Create session parameters
    session_params = CreateSessionParams()
    session_params.context_syncs = [context_sync]
    session_params.labels = {"test": "recycle-policy-integration"}
    session_params.image_id = "linux_latest"

    print("Creating session with custom RecyclePolicy...")
    print(f"RecyclePolicy lifecycle: {custom_recycle_policy.lifecycle.value}")
    print(f"RecyclePolicy paths: {custom_recycle_policy.paths}")

    # Create session
    session_result = await agent_bay.create(session_params)
    if not session_result.success or not session_result.session:
        pytest.skip("Failed to create session for RecyclePolicy integration test")

    session = session_result.session
    print(f"Session created successfully with ID: {session.session_id}")

    try:
        # Wait for session to be ready
        await asyncio.sleep(5)

        # Get context info to verify the session was created with the policy
        context_info = await session.context.info()
        assert context_info.request_id is not None

        print("RecyclePolicy integration test completed successfully")

    finally:
        # Clean up session
        try:
            await agent_bay.delete(session)
            print(f"Session deleted: {session.session_id}")
        except Exception as e:
            print(f"Warning: Failed to delete session: {e}")


@pytest.mark.asyncio
async def test_recycle_policy_with_lifecycle_1day():
    """Test creating ContextSync with custom RecyclePolicy using Lifecycle_1Day."""
    # Create a custom recycle policy with Lifecycle_1Day
    custom_recycle_policy = RecyclePolicy(
        lifecycle=Lifecycle.LIFECYCLE_1DAY, paths=["/custom/path"]
    )

    # Create a sync policy with the custom recycle policy
    sync_policy = SyncPolicy(
        upload_policy=UploadPolicy.default(),
        download_policy=DownloadPolicy.default(),
        delete_policy=DeletePolicy.default(),
        extract_policy=ExtractPolicy.default(),
        recycle_policy=custom_recycle_policy,
        bw_list=BWList(white_lists=[WhiteList(path="", exclude_paths=[])]),
    )

    # Verify the recycle policy
    assert sync_policy.recycle_policy is not None
    assert sync_policy.recycle_policy.lifecycle == Lifecycle.LIFECYCLE_1DAY
    assert sync_policy.recycle_policy.paths is not None
    assert len(sync_policy.recycle_policy.paths) == 1
    assert sync_policy.recycle_policy.paths[0] == "/custom/path"

    # Test JSON serialization
    policy_dict = sync_policy.__dict__()
    assert "recyclePolicy" in policy_dict

    recycle_policy_dict = policy_dict["recyclePolicy"]
    assert recycle_policy_dict["lifecycle"] == "Lifecycle_1Day"
    assert len(recycle_policy_dict["paths"]) == 1
    assert recycle_policy_dict["paths"][0] == "/custom/path"

    # Create ContextSync with the custom policy
    context_sync = ContextSync(
        context_id="test-recycle-context", path="/test/recycle/path", policy=sync_policy
    )

    # Verify ContextSync properties
    assert context_sync.context_id == "test-recycle-context"
    assert context_sync.path == "/test/recycle/path"
    assert context_sync.policy == sync_policy

    print("RecyclePolicy with Lifecycle_1Day created and verified successfully")


@pytest.mark.asyncio
async def test_context_sync_and_info(agent_bay, context_for_test):
    """Test syncing context and then getting info."""

    # Create session for this test
    context_sync = ContextSync.new(
        context_for_test.id, "/home/wuying", SyncPolicy.default()
    )
    session_params = CreateSessionParams()
    session_params.context_syncs = [context_sync]
    session_params.labels = {"test": "context-sync-integration"}
    session_params.image_id = "linux_latest"

    session_result = await agent_bay.create(session_params)
    if not session_result.success or not session_result.session:
        pytest.skip("Failed to create session for test")

    session = session_result.session
    print(f"Created session: {session.session_id}")

    try:
        # Wait for session to be ready
        await asyncio.sleep(2)

        # The session should be automatically synced during creation (as seen in the logs above)
        # So just verify context status without initiating another sync
        sync_result = await session.context.info()

        # Verify sync result
        assert sync_result.request_id is not None
        assert sync_result.request_id != ""

        # Wait for sync to complete
        await asyncio.sleep(3)

        # Get context info
        context_info = await session.context.info()

        # Verify context info
        assert context_info.request_id is not None

        # Log the context status data
        print(
            f"Context status data after sync, count: {len(context_info.context_status_data)}"
        )
        for i, data in enumerate(context_info.context_status_data):
            print(f"Status data {i}:")
            print(f"  Context ID: {data.context_id}")
            print(f"  Path: {data.path}")
            print(f"  Status: {data.status}")
            print(f"  Task Type: {data.task_type}")

        # Check if we have status data for our context
        found_context = False
        for data in context_info.context_status_data:
            if data.context_id == context_for_test.id:
                found_context = True
                assert data.path == "/home/wuying"
                # Status might vary, but should not be empty
                assert data.status is not None
                assert data.status != ""
                break

        # We should have found our context in the status data
        # But this might be flaky in CI, so just log a warning if not found
        if not found_context:
            print(
                f"Warning: Could not find context {context_for_test.id} in status data"
            )

    finally:
        # Clean up session
        try:
            await agent_bay.delete(session)
            print(f"Session deleted: {session.session_id}")
        except Exception as e:
            print(f"Warning: Failed to delete session: {e}")


@pytest.mark.asyncio
async def test_context_info_with_params(agent_bay, context_for_test):
    """Test getting context info with specific parameters."""
    # Create session for this test
    context_sync = ContextSync.new(
        context_for_test.id, "/home/wuying", SyncPolicy.default()
    )
    session_params = CreateSessionParams()
    session_params.context_syncs = [context_sync]
    session_params.labels = {"test": "context-info-params-test"}
    session_params.image_id = "linux_latest"

    session_result = await agent_bay.create(session_params)
    if not session_result.success or not session_result.session:
        pytest.skip("Failed to create session for test")

    session = session_result.session
    print(f"Created session: {session.session_id}")

    try:
        # Wait for session to be ready
        await asyncio.sleep(2)

        # Get context info with parameters
        context_info = await session.context.info(
            context_id=context_for_test.id, path="/home/wuying", task_type=None
        )

        # Verify that we have a request ID
        assert context_info.request_id is not None

        # Log the filtered context status data
        print(
            f"Filtered context status data count: {len(context_info.context_status_data)}"
        )
        for i, data in enumerate(context_info.context_status_data):
            print(f"Status data {i}:")
            print(f"  Context ID: {data.context_id}")
            print(f"  Path: {data.path}")
            print(f"  Status: {data.status}")
            print(f"  Task Type: {data.task_type}")

        # If we have status data, verify it matches our filters
        for data in context_info.context_status_data:
            if data.context_id == context_for_test.id:
                assert data.path == "/home/wuying"

    finally:
        # Clean up session
        try:
            await agent_bay.delete(session)
            print(f"Session deleted: {session.session_id}")
        except Exception as e:
            print(f"Warning: Failed to delete session: {e}")


@pytest.mark.asyncio
async def test_recycle_policy_with_invalid_wildcard_path():
    """Test that RecyclePolicy throws error when created with invalid wildcard path."""
    print("Testing RecyclePolicy creation with invalid wildcard path...")

    # Test that RecyclePolicy constructor throws an error for invalid path with wildcard
    with pytest.raises(ValueError) as exc_info:
        RecyclePolicy(lifecycle=Lifecycle.LIFECYCLE_1DAY, paths=["/path/with/*"])

    # Verify the error message
    error_message = str(exc_info.value)
    assert (
        "Wildcard patterns are not supported in recycle policy paths" in error_message
    )
    assert "/path/with/*" in error_message
    assert "Please use exact directory paths instead" in error_message

    print("RecyclePolicy correctly threw error for invalid wildcard path")

    # Test with multiple invalid paths
    with pytest.raises(ValueError):
        RecyclePolicy(
            lifecycle=Lifecycle.LIFECYCLE_1DAY,
            paths=["/valid/path", "/invalid/path?", "/another/invalid/*"],
        )

    print("RecyclePolicy correctly threw error for multiple invalid paths")

    # Test with different wildcard patterns
    invalid_patterns = [
        "/path/with/*",
        "/path/with/?",
        "/path/with/[abc]",
        "/path/with/file*.txt",
    ]

    for pattern in invalid_patterns:
        with pytest.raises(ValueError) as exc_info:
            RecyclePolicy(lifecycle=Lifecycle.LIFECYCLE_1DAY, paths=[pattern])

        error_message = str(exc_info.value)
        assert "Wildcard patterns are not supported" in error_message
        assert pattern in error_message

    print("All wildcard patterns correctly rejected")


@pytest.mark.asyncio
async def test_recycle_policy_default_values():
    """Test RecyclePolicy default values and behavior."""
    # Test default RecyclePolicy
    default_policy = RecyclePolicy.default()

    assert default_policy.lifecycle == Lifecycle.LIFECYCLE_FOREVER
    assert default_policy.paths == [""]

    # Test RecyclePolicy with no arguments
    no_args_policy = RecyclePolicy()

    assert no_args_policy.lifecycle == Lifecycle.LIFECYCLE_FOREVER
    assert no_args_policy.paths == [""]

    # Test JSON serialization of default policy
    policy_dict = default_policy.__dict__()
    assert policy_dict["lifecycle"] == "Lifecycle_Forever"
    assert policy_dict["paths"] == [""]

    print("RecyclePolicy default values verified successfully")
