#!/usr/bin/env python3
"""
Streaming Mobile Agent Task Example

Demonstrates real-time streaming output from the built-in mobile agent
using typed callbacks (on_reasoning, on_content, on_tool_call, on_tool_result).

Only requires: AGENTBAY_API_KEY
"""

import asyncio
import json
import os

from agentbay import AsyncAgentBay, AgentEvent, CreateSessionParams


async def main() -> None:
    api_key = os.getenv("AGENTBAY_API_KEY")
    if not api_key:
        print("Error: AGENTBAY_API_KEY environment variable must be set")
        return

    client = AsyncAgentBay(api_key=api_key)
    session = None

    try:
        image_id = os.getenv("MOBILE_IMAGE_ID", "mobile_latest")
        session_result = await client.create(CreateSessionParams(image_id=image_id))
        session = session_result.session
        print(f"Session created: {session.session_id}")
        print(f"Resource URL: {getattr(session, 'resource_url', '')}")

        task = os.getenv("MOBILE_TASK", "Open the Settings app and find the Wi-Fi option")
        print(f"\nExecuting task: {task}")
        print("=" * 60)

        def on_reasoning(event: AgentEvent):
            print(f"[Reasoning] {event.content}", end="", flush=True)

        def on_content(event: AgentEvent):
            print(f"[Content] {event.content}", end="", flush=True)

        def on_tool_call(event: AgentEvent):
            args_str = json.dumps(event.args, ensure_ascii=False) if event.args else ""
            print(f"\n[ToolCall] {event.tool_name}({args_str})")

        def on_tool_result(event: AgentEvent):
            result_preview = str(event.result)[:200] if event.result else ""
            print(f"[ToolResult] {event.tool_name} -> {result_preview}")

        def on_error(event: AgentEvent):
            print(f"\n[Error] {event.error}")

        result = await session.agent.mobile.execute_task_and_wait(
            task=task,
            timeout=180,
            max_steps=50,
            on_reasoning=on_reasoning,
            on_content=on_content,
            on_tool_call=on_tool_call,
            on_tool_result=on_tool_result,
            on_error=on_error,
        )

        print("\n" + "=" * 60)
        print(f"Task completed:")
        print(f"  Success: {result.success}")
        print(f"  Status:  {result.task_status}")
        if result.task_result:
            print(f"  Result:  {result.task_result[:500]}")
        if result.error_message:
            print(f"  Error:   {result.error_message}")

    except Exception as e:
        print(f"\nError: {e}")
        raise
    finally:
        if session:
            await client.delete(session)
            print("\nSession cleaned up")


if __name__ == "__main__":
    asyncio.run(main())
