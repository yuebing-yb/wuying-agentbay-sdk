"""Integration tests for Agent functionality."""

import asyncio
import os

import pytest
import pytest_asyncio

from agentbay import AsyncAgentBay
from agentbay import get_logger
from agentbay import CreateSessionParams
from agentbay  import AgentOptions

from dotenv import load_dotenv

logger = get_logger("agentbay-integration-test")
load_dotenv()


@pytest_asyncio.fixture(scope="module")
async def agent_bay():
    """Create an AsyncAgentBay instance."""
    api_key = os.getenv("AGENTBAY_API_KEY")
    if not api_key:
        pytest.skip("AGENTBAY_API_KEY environment variable not set")
    return AsyncAgentBay(api_key=api_key)


@pytest_asyncio.fixture(scope="module")
async def computer_agent_session(agent_bay):
    """Create a session for agent testing."""
    # Ensure a delay to avoid session creation conflicts
    await asyncio.sleep(3)
    params = CreateSessionParams(
        image_id="windows_latest",
    )
    session_result = await agent_bay.create(params)
    if not session_result.success or not session_result.session:
        pytest.skip("Failed to create session")

    session = session_result.session
    yield session

    # Clean up session
    try:
        await session.delete()
    except Exception as e:
        logger.info(f"Warning: Error deleting session: {e}")


@pytest_asyncio.fixture(scope="module")
async def browser_agent_session(agent_bay):
    """Create a session for agent testing."""
    # Ensure a delay to avoid session creation conflicts
    await asyncio.sleep(3)
    params = CreateSessionParams(
        image_id="imgc-0aae4rgkx5fdch0et",
    )
    session_result = await agent_bay.create(params)
    if not session_result.success or not session_result.session:
        pytest.skip("Failed to create session")

    session = session_result.session
    yield session

    # Clean up session
    try:
        await session.delete()
    except Exception as e:
        logger.info(f"Warning: Error deleting session: {e}")


@pytest_asyncio.fixture(scope="module")
async def mobile_agent_session(agent_bay):
    """Create a session for mobile agent testing."""
    # Ensure a delay to avoid session creation conflicts
    await asyncio.sleep(3)
    params = CreateSessionParams(
        image_id="mobile_latest",
    )
    session_result = await agent_bay.create(params)
    if not session_result.success or not session_result.session:
        pytest.skip("Failed to create session")

    session = session_result.session
    yield session

    # Clean up session
    try:
        await session.delete()
    except Exception as e:
        logger.info(f"Warning: Error deleting session: {e}")


@pytest.mark.asyncio
async def test_computer_execute_task_and_wait_success(computer_agent_session):
    """Test executing a flux task successfully."""
    agent = computer_agent_session.agent

    task = "create a folder named 'agentbay' in C:\\Window\\Temp"
    max_try_times = os.environ.get("AGENT_TASK_TIMEOUT")
    if not max_try_times:
        max_try_times = 100
    logger.info("🚀 task of creating folders")
    result = await agent.computer.execute_task_and_wait(task, int(max_try_times))
    assert result.success
    assert result.request_id != ""
    assert result.error_message == ""
    logger.info(f"✅ result {result.task_result}")


@pytest.mark.asyncio
async def test_computer_execute_task_success(computer_agent_session):
    """Test executing a flux task successfully."""
    agent = computer_agent_session.agent

    task = "create a folder named 'agentbay' in C:\\Window\\Temp"
    max_try_times = os.environ.get("AGENT_TASK_TIMEOUT")
    if not max_try_times:
        max_try_times = 100
    logger.info("🚀 async task of creating folders")
    result = await agent.computer.execute_task(task)
    assert result.success
    assert result.request_id != ""
    assert result.error_message == ""
    retry_times: int = 0
    query_result = None
    while retry_times < int(max_try_times):
        query_result = await agent.computer.get_task_status(result.task_id)
        assert result.success
        logger.info(
            f"⏳ Task {query_result.task_id} running 🚀: {query_result.task_action}."
        )
        if query_result.task_status == "completed":
            break
        retry_times += 1
        await asyncio.sleep(3)
    # Verify the final task status
    assert retry_times < int(max_try_times)
    logger.info(f"✅ result {query_result.task_product}")


@pytest.mark.asyncio
async def test_browser_execute_task_and_wait_success(browser_agent_session):
    """Test executing a flux task successfully."""
    agent = browser_agent_session.agent

    task = "Navigate to baidu.com and Query the date when Alibaba listed in the U.S"
    max_try_times = os.environ.get("AGENT_TASK_TIMEOUT")
    if not max_try_times:
        max_try_times = 100
    logger.info("🚀 task of Query the date when Alibaba listed in the U.S")
    options: AgentOptions = AgentOptions(use_vision=False, output_schema="text")
    result = await agent.browser.initialize(options)
    assert result.success
    result = await agent.browser.execute_task_and_wait(task, int(max_try_times))
    assert result.success
    assert result.request_id != ""
    assert result.error_message == ""
    logger.info(f"✅ result {result.task_result}")


@pytest.mark.asyncio
async def test_browser_execute_task_success(browser_agent_session):
    """Test executing a flux task successfully."""
    agent = browser_agent_session.agent

    task = "Navigate to baidu.com and Query the weather in Shanghai"
    max_try_times = os.environ.get("AGENT_TASK_TIMEOUT")
    if not max_try_times:
        max_try_times = 100
    logger.info("🚀 async task Query the weather in Shanghai.")
    result = await agent.browser.execute_task(task)
    assert result.success
    assert result.request_id != ""
    assert result.error_message == ""
    retry_times: int = 0
    query_result = None
    while retry_times < int(max_try_times):
        query_result = await agent.browser.get_task_status(result.task_id)
        assert result.success
        logger.info(
            f"⏳ Task {query_result.task_id} running 🚀: {query_result.task_action}."
        )
        if query_result.task_status == "completed":
            break
        retry_times += 1
        await asyncio.sleep(3)
    # Verify the final task status
    assert retry_times < int(max_try_times)
    logger.info(f"✅ result {query_result.task_product}")


@pytest.mark.asyncio
async def test_mobile_execute_task_and_wait_success(mobile_agent_session):
    """Test executing a mobile task successfully."""
    agent = mobile_agent_session.agent

    task = "Open WeChat app"
    max_poll_times = os.environ.get("AGENT_TASK_TIMEOUT")
    if not max_poll_times:
        max_poll_times = 100
    logger.info("🚀 task of opening WeChat app")
    result = await agent.mobile.execute_task_and_wait(
        task, max_steps=50, max_try_times=3, max_poll_times=int(max_poll_times)
    )
    assert result.success
    assert result.request_id != ""
    assert result.error_message == ""
    logger.info(f"✅ result {result.task_result}")


@pytest.mark.asyncio
async def test_mobile_execute_task_success(mobile_agent_session):
    """Test executing a mobile task successfully."""
    agent = mobile_agent_session.agent

    task = "Open WeChat app"
    max_try_times = os.environ.get("AGENT_TASK_TIMEOUT")
    if not max_try_times:
        max_try_times = 100
    logger.info("🚀 async task of opening WeChat app")
    result = await agent.mobile.execute_task(
        task, max_steps=50, max_try_times=3
    )
    assert result.success
    assert result.request_id != ""
    assert result.error_message == ""
    retry_times: int = 0
    query_result = None
    while retry_times < int(max_try_times):
        query_result = await agent.mobile.get_task_status(result.task_id)
        assert result.success
        logger.info(
            f"⏳ Task {query_result.task_id} running 🚀: {query_result.task_action}."
        )
        if query_result.task_status == "completed":
            break
        retry_times += 1
        await asyncio.sleep(3)
    # Verify the final task status
    assert retry_times < int(max_try_times)
    logger.info(f"✅ result {query_result.task_product}")
