"""Integration tests for Mobile Agent functionality."""

import asyncio
import os

import pytest
import pytest_asyncio

from agentbay import AsyncAgentBay
from agentbay import get_logger
from agentbay import CreateSessionParams

from dotenv import load_dotenv

logger = get_logger("mobile-agent-integration-test")
load_dotenv()


@pytest_asyncio.fixture(scope="module")
async def agent_bay():
    """Create an AsyncAgentBay instance."""
    api_key = os.getenv("AGENTBAY_API_KEY")
    if not api_key:
        pytest.skip("AGENTBAY_API_KEY environment variable not set")
    return AsyncAgentBay(api_key=api_key)


@pytest_asyncio.fixture(scope="module")
async def mobile_agent_session(agent_bay):
    """Create a session for mobile agent testing."""
    # Ensure a delay to avoid session creation conflicts
    await asyncio.sleep(3)
    params = CreateSessionParams(
        image_id="imgc-0aae4rgien5oudgb6",
    )
    session_result = await agent_bay.create(params)
    if not session_result.success or not session_result.session:
        # 打印错误信息以便调试
        print(f"\n❌ Failed to create session: {session_result.error_message}")
        logger.error(f"Failed to create session: {session_result.error_message}")
        pytest.skip("Failed to create session")

    session = session_result.session
    # 添加 session_id 打印
    print(f"\n✅ Session created: {session.session_id}")
    logger.info(f"Session created: {session.session_id}")
    yield session

    # Clean up session
    try:
        await session.delete()
        print(f"✅ Session deleted: {session.session_id}")
    except Exception as e:
        logger.info(f"Warning: Error deleting session: {e}")


@pytest.mark.asyncio
async def test_mobile_execute_task_success(mobile_agent_session):
    """Test execute_task basic functionality - non-blocking execution."""
    agent = mobile_agent_session.agent
    task_id = None

    try:
        task = "Open WeChat app"
        logger.info("🚀 Testing execute_task - non-blocking execution")
        
        # Execute task and get task_id immediately
        result = await agent.mobile.execute_task(
            task, max_steps=1, max_step_retries=1
        )
        task_id = result.task_id
        
        # Print results
        print(f"\n{'='*60}")
        print(f"📋 Request ID: {result.request_id}")
        print(f"📋 Task ID: {result.task_id}")
        print(f"📋 Task Status: {result.task_status}")
        print(f"📋 Success: {result.success}")
        print(f"📋 Error Message: {result.error_message}")
        print(f"{'='*60}\n")
        
        # Verify execute_task returned successfully
        assert result.success, f"execute_task failed: {result.error_message}"
        assert result.request_id != "", "Request ID should not be empty"
        assert result.task_id != "", "Task ID should not be empty"
        assert result.error_message == "", f"Error message should be empty: {result.error_message}"
        assert result.task_status == "running", f"Initial status should be 'running', got: {result.task_status}"
        
        logger.info(f"✅ execute_task succeeded: task_id={result.task_id}")
        
        # Poll until task completes to avoid blocking subsequent tests
        max_try_times = 100
        retry_times = 0
        import json

        while retry_times < max_try_times:
            # Call the underlying API directly to get raw response
            raw_result = await agent.mobile.session.call_mcp_tool(
                agent.mobile._get_tool_name("get_status"), {"task_id": task_id}
            )
            
            # Verify the response
            assert raw_result.success, f"get_task_status failed: {raw_result.error_message}"
            
            if raw_result.success and raw_result.data:
                try:
                    content = json.loads(raw_result.data)
                    
                    # Only print content
                    print(f"\n📋 Content (Attempt #{retry_times + 1}):")
                    print(json.dumps(content, indent=2, ensure_ascii=False))
                    print()
                    
                    # Check for error first (task finished or not found)
                    if "error" in content:
                        logger.info(f"✅ Task returned error (task finished or not found): {content.get('error')}")
                        break
                    
                    # Support both taskId (camelCase) and task_id (snake_case)
                    content_task_id = content.get("taskId") or content.get("task_id", task_id)
                    task_status = content.get("status", "unknown")
                    
                    assert content_task_id == task_id, f"Task ID mismatch: expected {task_id}, got {content_task_id}"
                    
                    logger.info(f"⏳ Polling task status: {task_status} (attempt {retry_times + 1})")
                    
                    # If task completed, end polling immediately
                    if task_status == "completed":
                        logger.info(f"✅ Task reached completed status")
                        break
                    
                    if task_status in ["failed", "unsupported"]:
                        logger.info(f"✅ Task reached final status: {task_status}")
                        break
                except json.JSONDecodeError as e:
                    logger.error(f"Failed to parse response: {e}")
                    print(f"📋 Raw Content (parse error): {raw_result.data}")
                    break
            
            retry_times += 1
            await asyncio.sleep(3)
        
        # Verify task completed
        assert retry_times < max_try_times, f"Task did not complete within {max_try_times} attempts"
        logger.info(f"✅ Task completed: status={task_status}")
        
    finally:
        # Final cleanup: terminate task if still running
        if task_id:
            try:
                status = await agent.mobile.get_task_status(task_id)
                if status.task_status == "running":
                    logger.info(f"Cleaning up: terminating task {task_id}")
                    terminate_result = await agent.mobile.terminate_task(task_id)
                    if terminate_result.success:
                        logger.info(f"✅ Task {task_id} terminated successfully")
            except Exception as e:
                logger.debug(f"Could not terminate task {task_id}: {e}")


@pytest.mark.asyncio
async def test_mobile_execute_task_and_wait_success(mobile_agent_session):
    """Test execute_task_and_wait - blocking execution with SDK polling."""
    agent = mobile_agent_session.agent
    task_id = None

    try:
        task = "Open WeChat app"
        logger.info("🚀 Testing execute_task_and_wait - blocking execution")
        
        # Execute task and wait for completion using SDK's built-in polling
        result = await agent.mobile.execute_task_and_wait(
            task,
            max_steps=1,
            max_step_retries=1,
            max_try_times=100  # Only 1 attempt for quick test
        )
        task_id = result.task_id
        
        # Print results
        print(f"\n{'='*60}")
        print(f"📋 Request ID: {result.request_id}")
        print(f"📋 Task ID: {result.task_id}")
        print(f"📋 Task Status: {result.task_status}")
        print(f"📋 Success: {result.success}")
        print(f"📋 Error Message: {result.error_message}")
        if result.task_result:
            print(f"📋 Task Result: {result.task_result}")
        print(f"{'='*60}\n")
        
        # Verify execute_task_and_wait behavior
        assert result.request_id != "", "Request ID should not be empty"
        if result.task_id:
            assert result.task_id != "", "Task ID should not be empty if provided"
        
        logger.info(f"✅ execute_task_and_wait completed: status={result.task_status}")
        
        # If task didn't complete (timeout), ensure it's terminated
        if result.task_status == "running" or (not result.success and task_id):
            logger.info(f"Task still running or failed, ensuring termination...")
            if task_id:
                terminate_result = await agent.mobile.terminate_task(task_id)
                if terminate_result.success:
                    logger.info(f"✅ Task {task_id} terminated successfully")
                else:
                    # Poll until task completes naturally
                    max_try_times = 100
                    retry_times = 0
                    while retry_times < max_try_times:
                        status = await agent.mobile.get_task_status(task_id)
                        if status.task_status in ["completed", "finished", "failed", "cancelled", "unsupported"]:
                            logger.info(f"✅ Task completed: {status.task_status}")
                            break
                        retry_times += 1
                        await asyncio.sleep(3)
        
    finally:
        # Final cleanup: terminate task if still running
        if task_id:
            try:
                status = await agent.mobile.get_task_status(task_id)
                if status.task_status == "running":
                    logger.info(f"Cleaning up: terminating task {task_id}")
                    terminate_result = await agent.mobile.terminate_task(task_id)
                    if terminate_result.success:
                        logger.info(f"✅ Task {task_id} terminated successfully")
            except Exception as e:
                logger.debug(f"Could not terminate task {task_id}: {e}")


@pytest.mark.asyncio
async def test_mobile_get_task_status_success(mobile_agent_session):
    """Test get_task_status - query task status and verify status changes."""
    agent = mobile_agent_session.agent
    task_id = None

    try:
        task = "Open WeChat app"
        logger.info("🚀 Testing get_task_status - status querying")
        
        # First, execute a task
        execute_result = await agent.mobile.execute_task(
            task, max_steps=1, max_step_retries=1
        )
        assert execute_result.success, f"execute_task failed: {execute_result.error_message}"
        task_id = execute_result.task_id
        
        logger.info(f"✅ Task started: task_id={task_id}")
        
        # Query status multiple times to verify status changes, and poll until completion
        max_try_times = 100
        retry_times = 0
        statuses_seen = []
        
        while retry_times < max_try_times:
            status_result = await agent.mobile.get_task_status(task_id)
            
            # Print status
            print(f"\n{'='*60}")
            print(f"📋 Query #{retry_times + 1}")
            print(f"📋 Request ID: {status_result.request_id}")
            print(f"📋 Task ID: {status_result.task_id}")
            print(f"📋 Task Status: {status_result.task_status}")
            print(f"📋 Task Action: {status_result.task_action}")
            print(f"📋 Success: {status_result.success}")
            print(f"📋 Error Message: {status_result.error_message}")
            print(f"{'='*60}\n")
            
            # Verify get_task_status returned successfully
            assert status_result.success, f"get_task_status failed: {status_result.error_message}"
            assert status_result.task_id == task_id, "Task ID should match"
            assert status_result.request_id != "", "Request ID should not be empty"
            
            statuses_seen.append(status_result.task_status)
            logger.info(f"✅ Query #{retry_times + 1}: status={status_result.task_status}, action={status_result.task_action}")
            
            # If task finished, we can stop querying
            if status_result.task_status in ["completed", "finished", "failed", "cancelled", "unsupported"]:
                logger.info(f"✅ Task reached final status: {status_result.task_status}")
                break
            
            retry_times += 1
            await asyncio.sleep(3)
        
        # Verify task completed
        assert retry_times < max_try_times, f"Task did not complete within {max_try_times} attempts"
        assert len(statuses_seen) > 0, "Should have queried status at least once"
        logger.info(f"✅ Statuses seen: {statuses_seen}")
        
    finally:
        # Clean up: terminate task if still running
        if task_id:
            try:
                status = await agent.mobile.get_task_status(task_id)
                if status.task_status == "running":
                    logger.info(f"Cleaning up: terminating task {task_id}")
                    terminate_result = await agent.mobile.terminate_task(task_id)
                    if terminate_result.success:
                        logger.info(f"✅ Task {task_id} terminated successfully")
            except Exception as e:
                logger.debug(f"Could not terminate task {task_id}: {e}")


@pytest.mark.asyncio
async def test_mobile_terminate_task_success(mobile_agent_session):
    """Test terminate_task - terminate a running task."""
    agent = mobile_agent_session.agent
    task_id = None

    try:
        task = "Open WeChat app"
        logger.info("🚀 Testing terminate_task - task termination")
        
        # First, execute a task
        execute_result = await agent.mobile.execute_task(
            task, max_steps=1, max_step_retries=1
        )
        assert execute_result.success, f"execute_task failed: {execute_result.error_message}"
        task_id = execute_result.task_id
        
        logger.info(f"✅ Task started: task_id={task_id}")
        
        # Wait a moment to ensure task is running
        await asyncio.sleep(2)
        
        # Verify task is running before termination
        status_before = await agent.mobile.get_task_status(task_id)
        assert status_before.success, f"get_task_status failed: {status_before.error_message}"
        logger.info(f"📋 Task status before termination: {status_before.task_status}")
        
        # Terminate the task
        terminate_result = await agent.mobile.terminate_task(task_id)
        
        # Print results
        print(f"\n{'='*60}")
        print(f"📋 Request ID: {terminate_result.request_id}")
        print(f"📋 Task ID: {terminate_result.task_id}")
        print(f"📋 Task Status: {terminate_result.task_status}")
        print(f"📋 Success: {terminate_result.success}")
        print(f"📋 Error Message: {terminate_result.error_message}")
        print(f"{'='*60}\n")
        
        # Verify terminate_task succeeded
        assert terminate_result.success, f"terminate_task failed: {terminate_result.error_message}"
        assert terminate_result.request_id != "", "Request ID should not be empty"
        assert terminate_result.task_id == task_id, "Task ID should match"
        
        logger.info(f"✅ terminate_task succeeded: status={terminate_result.task_status}")
        
        # Verify task status after termination - poll until confirmed terminated/completed
        max_try_times = 20
        retry_times = 0
        while retry_times < max_try_times:
            await asyncio.sleep(1)  # Wait a moment for termination to process
            status_after = await agent.mobile.get_task_status(task_id)
            assert status_after.success, f"get_task_status failed: {status_after.error_message}"
            logger.info(f"📋 Task status after termination (attempt {retry_times + 1}): {status_after.task_status}")
            
            # Task should be terminated, finished, or failed
            if status_after.task_status in ["completed", "finished", "failed", "cancelled", "unsupported"]:
                logger.info(f"✅ Task confirmed in final status: {status_after.task_status}")
                break
            
            retry_times += 1
        
        # Verify task is no longer running
        final_status = await agent.mobile.get_task_status(task_id)
        assert final_status.task_status != "running", f"Task should not be running after termination, got: {final_status.task_status}"
        logger.info(f"✅ Task termination confirmed: {final_status.task_status}")
        
    except Exception as e:
        logger.error(f"❌ Test failed: {e}")
        raise
    finally:
        # Final cleanup attempt - ensure task is completed or terminated
        if task_id:
            try:
                status = await agent.mobile.get_task_status(task_id)
                if status.task_status == "running":
                    logger.info(f"Final cleanup: attempting to terminate task {task_id}")
                    terminate_result = await agent.mobile.terminate_task(task_id)
                    if terminate_result.success:
                        logger.info(f"✅ Task {task_id} terminated in cleanup")
                    else:
                        # Poll until task completes naturally
                        max_try_times = 50
                        retry_times = 0
                        while retry_times < max_try_times:
                            status = await agent.mobile.get_task_status(task_id)
                            if status.task_status in ["completed", "finished", "failed", "cancelled", "unsupported"]:
                                logger.info(f"✅ Task completed in cleanup: {status.task_status}")
                                break
                            retry_times += 1
                            await asyncio.sleep(3)
            except Exception as e:
                logger.debug(f"Final cleanup failed for task {task_id}: {e}")

