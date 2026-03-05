"""Integration tests for Agent streaming output feature.

Tests the WS-based streaming execution path with real backend services.
Uses debug image imgc-0ab5takhnmlvhx9gp for Mobile Agent.
"""
import asyncio
import os

import pytest
import pytest_asyncio

from agentbay import AsyncAgentBay, AgentEvent, CreateSessionParams, get_logger

from dotenv import load_dotenv

logger = get_logger("agent-streaming-integration-test")
load_dotenv()


@pytest_asyncio.fixture(scope="module")
async def agent_bay():
    """Create an AsyncAgentBay instance."""
    api_key = os.getenv("AGENTBAY_API_KEY")
    if not api_key:
        pytest.skip("AGENTBAY_API_KEY environment variable not set")
    return AsyncAgentBay(api_key=api_key)


@pytest_asyncio.fixture(scope="module")
async def mobile_streaming_session(agent_bay):
    """Create a session with Mobile Agent debug image for streaming tests."""
    await asyncio.sleep(3)
    params = CreateSessionParams(
        image_id="imgc-0ab5takhnmlvhx9gp",
    )
    session_result = await agent_bay.create(params)
    if not session_result.success or not session_result.session:
        print(f"\n❌ Failed to create session: {session_result.error_message}")
        logger.error(f"Failed to create session: {session_result.error_message}")
        pytest.skip("Failed to create session")

    session = session_result.session
    print(f"\n✅ Session created: {session.session_id}")
    print(f"   WS URL: {session.ws_url}")
    logger.info(f"Session created: {session.session_id}, ws_url={session.ws_url}")
    yield session

    try:
        print(f"🧹 Cleaning up session: {session.session_id}")
        await asyncio.wait_for(session.delete(), timeout=10.0)
        print(f"✅ Session deleted: {session.session_id}")
    except asyncio.TimeoutError:
        logger.warning(f"Session deletion timed out: {session.session_id}")
    except Exception as e:
        logger.warning(f"Error deleting session: {e}")


@pytest.mark.asyncio
async def test_mobile_streaming_with_on_event(mobile_streaming_session):
    """Test mobile agent streaming with on_event callback (stream=False, step-level events)."""
    agent = mobile_streaming_session.agent
    events_received = []

    def on_event(event: AgentEvent):
        events_received.append(event)
        print(f"  [Event] type={event.type}, seq={event.seq}, round={event.round}", end="")
        if event.content:
            print(f", content={event.content[:80]}...", end="")
        if event.tool_name:
            print(f", tool={event.tool_name}", end="")
        print()

    print(f"\n{'='*60}")
    print("🚀 Testing mobile agent streaming with on_event (stream=False)")
    print(f"{'='*60}")

    result = await agent.mobile.execute_task_and_wait(
        task="Open Settings app",
        timeout=180,
        max_steps=10,
        stream_beta=False,
        on_event=on_event,
    )

    print(f"\n{'='*60}")
    print(f"📋 Result:")
    print(f"  Success: {result.success}")
    print(f"  Status: {result.task_status}")
    print(f"  Error: {result.error_message}")
    if result.task_result:
        print(f"  Task Result: {result.task_result[:200]}")
    print(f"  Events received: {len(events_received)}")
    print(f"{'='*60}\n")

    assert isinstance(result.task_status, str), "task_status should be a string"
    assert len(events_received) > 0, "Should have received at least one event"

    event_types = [e.type for e in events_received]
    print(f"Event types received: {event_types}")
    logger.info(f"Event types: {event_types}")


@pytest.mark.asyncio
async def test_mobile_streaming_with_typed_callbacks(mobile_streaming_session):
    """Test mobile agent streaming with typed callbacks (on_thought, on_tool_call, etc.)."""
    agent = mobile_streaming_session.agent
    thoughts = []
    tool_calls = []
    tool_results = []
    responses = []

    def on_thought(event: AgentEvent):
        thoughts.append(event)
        print(f"  [Thought] round={event.round}: {event.content[:100]}...")

    def on_tool_call(event: AgentEvent):
        tool_calls.append(event)
        print(f"  [ToolCall] round={event.round}: {event.tool_name}({event.args})")

    def on_tool_result(event: AgentEvent):
        tool_results.append(event)
        result_preview = str(event.result)[:100]
        print(f"  [ToolResult] round={event.round}: {event.tool_name} -> {result_preview}...")

    def on_response(event: AgentEvent):
        responses.append(event)
        print(f"  [Response] round={event.round}: {event.content[:100]}...")

    print(f"\n{'='*60}")
    print("🚀 Testing mobile agent streaming with typed callbacks (stream=False)")
    print(f"{'='*60}")

    result = await agent.mobile.execute_task_and_wait(
        task="Open Settings app",
        timeout=180,
        max_steps=10,
        stream_beta=False,
        on_thought=on_thought,
        on_tool_call=on_tool_call,
        on_tool_result=on_tool_result,
        on_response=on_response,
    )

    print(f"\n{'='*60}")
    print(f"📋 Result:")
    print(f"  Success: {result.success}")
    print(f"  Status: {result.task_status}")
    print(f"  Thoughts: {len(thoughts)}")
    print(f"  Tool Calls: {len(tool_calls)}")
    print(f"  Tool Results: {len(tool_results)}")
    print(f"  Responses: {len(responses)}")
    print(f"{'='*60}\n")

    assert isinstance(result.task_status, str), "task_status should be a string"


@pytest.mark.asyncio
async def test_mobile_streaming_token_level(mobile_streaming_session):
    """Test mobile agent streaming with stream=True (token-level streaming)."""
    agent = mobile_streaming_session.agent
    all_events = []
    thought_chunks = []
    response_chunks = []

    def on_event(event: AgentEvent):
        all_events.append(event)

    def on_thought(event: AgentEvent):
        thought_chunks.append(event.content)
        print(event.content, end="", flush=True)

    def on_response(event: AgentEvent):
        response_chunks.append(event.content)
        print(event.content, end="", flush=True)

    def on_tool_call(event: AgentEvent):
        print(f"\n  [ToolCall] {event.tool_name}({event.args})")

    print(f"\n{'='*60}")
    print("🚀 Testing mobile agent streaming with stream=True (token-level)")
    print(f"{'='*60}")
    print("\nStreaming output:")

    result = await agent.mobile.execute_task_and_wait(
        task="Open Settings app",
        timeout=180,
        max_steps=10,
        stream_beta=True,
        on_event=on_event,
        on_thought=on_thought,
        on_tool_call=on_tool_call,
        on_response=on_response,
    )

    print(f"\n\n{'='*60}")
    print(f"📋 Result:")
    print(f"  Success: {result.success}")
    print(f"  Status: {result.task_status}")
    print(f"  Total events: {len(all_events)}")
    print(f"  Thought chunks: {len(thought_chunks)}")
    print(f"  Response chunks: {len(response_chunks)}")
    if result.task_result:
        print(f"  Task Result: {result.task_result[:200]}")
    print(f"{'='*60}\n")

    assert isinstance(result.task_status, str), "task_status should be a string"
    assert len(all_events) > 0, "Should have received at least one event"

    if thought_chunks:
        full_thought = "".join(thought_chunks)
        print(f"Reconstructed thought: {full_thought[:200]}...")
    if response_chunks:
        full_response = "".join(response_chunks)
        print(f"Reconstructed response: {full_response[:200]}...")
