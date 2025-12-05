"""Command Execution Patterns Example"""
import asyncio
import os
import sys

sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))))

from agentbay import AsyncAgentBay
from agentbay import CreateSessionParams


async def main():
    print("=== Command Execution Patterns ===\n")
    client = AsyncAgentBay()
    session = None

    try:
        session_result = await client.create(CreateSessionParams(image_id="linux_latest"))
        session = session_result.session
        print(f"Session: {session.session_id}\n")

        # Simple command
        result = await session.command.execute_command("echo 'Hello'")
        print(f"1. Simple: {result.output}")

        # Piped commands
        result = await session.command.execute_command("echo 'test' | wc -c")
        print(f"2. Piped: {result.output}")

        # Multiple commands
        result = await session.command.execute_command("cd /tmp && pwd")
        print(f"3. Multiple: {result.output}")

        print("\n=== Completed ===")

    finally:
        if session:
            await client.delete(session)


if __name__ == "__main__":
    asyncio.run(main())

