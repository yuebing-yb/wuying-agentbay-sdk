import asyncio
import os
import sys

sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from agentbay import AsyncAgentBay
from agentbay.exceptions import AgentBayError

async def main():
    api_key = os.environ.get("AGENTBAY_API_KEY") or "your_api_key_here"
    agent_bay = AsyncAgentBay(api_key=api_key)
    
    try:
        print("Listing contexts (Async)...")
        # Use .list() instead of .list_contexts()
        result = await agent_bay.context.list()
        contexts = result.contexts
        print(f"Found {len(contexts)} contexts")
        
        for ctx in contexts[:3]:
            print(f" - {ctx.name} ({ctx.id})")

    except AgentBayError as e:
        print(f"AgentBay error: {e}")
    except Exception as e:
        print(f"Unexpected error: {e}")

if __name__ == "__main__":
    asyncio.run(main())

