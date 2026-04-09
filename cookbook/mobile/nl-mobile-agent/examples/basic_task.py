#!/usr/bin/env python3
"""
Basic Mobile Agent Task Example

Demonstrates the simplest way to execute a natural language task
on a cloud phone using AgentBay's built-in mobile agent.

Only requires: AGENTBAY_API_KEY
"""

import asyncio
import os

from agentbay import AsyncAgentBay, CreateSessionParams


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

        task = os.getenv("MOBILE_TASK", "Open the Settings app")
        print(f"\nExecuting task: {task}")

        result = await session.agent.mobile.execute_task_and_wait(
            task=task,
            timeout=180,
            max_steps=50,
        )

        print(f"\nTask completed:")
        print(f"  Success: {result.success}")
        print(f"  Status:  {result.task_status}")
        if result.task_result:
            print(f"  Result:  {result.task_result[:500]}")
        if result.error_message:
            print(f"  Error:   {result.error_message}")

    except Exception as e:
        print(f"Error: {e}")
        raise
    finally:
        if session:
            await client.delete(session)
            print("\nSession cleaned up")


if __name__ == "__main__":
    asyncio.run(main())
