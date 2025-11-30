"""
Browser Multi-Tab Management Example

This example demonstrates:
1. Opening multiple tabs
2. Switching between tabs
3. Managing tab state
4. Coordinating actions across tabs
"""

import asyncio
import os
import sys

# Add parent directory to path for imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))))

from agentbay import AsyncAgentBay, CreateSessionParams
from agentbay._async.browser import BrowserOption
from agentbay._async.browser_agent import ExtractOptions


async def main():
    """Demonstrate browser multi-tab management."""
    print("=== Browser Multi-Tab Management Example ===\n")

    # Initialize AgentBay client
    client = AsyncAgentBay()
    session = None

    try:
        # Create a session with browser enabled
        print("Creating session with browser...")
        session_result = await client.create(
            CreateSessionParams(image_id="browser_latest")
        )
        session = session_result.session
        print(f"Session created: {session.session_id}")

        # Initialize browser
        print("Initializing browser...")
        if not await session.browser.initialize(BrowserOption()):
            raise Exception("Failed to initialize browser")
        print("Browser initialized")

        # Open first tab
        print("\n1. Opening first tab (example.com)...")
        await session.browser.agent.navigate("https://example.com")
        tab1_result = await session.browser.agent.extract(ExtractOptions("What is the page title?"))
        print(f"Tab 1 title: {tab1_result.extracted_content}")

        # Open second tab by navigating to a new URL
        print("\n2. Opening second tab (httpbin.org)...")
        await session.browser.agent.act("Open a new tab and navigate to https://httpbin.org")
        tab2_result = await session.browser.agent.extract(ExtractOptions("What is the page title?"))
        print(f"Tab 2 title: {tab2_result.extracted_content}")

        # Extract information from current tab
        print("\n3. Extracting information from current tab...")
        info_result = await session.browser.agent.extract("What HTTP testing endpoints are available?")
        print(f"Available endpoints:\n{info_result.extracted_content}")

        # Switch back to first tab
        print("\n4. Switching back to first tab...")
        await session.browser.agent.act("Switch to the first tab")
        current_result = await session.browser.agent.extract("What is the current page URL?")
        print(f"Current URL: {current_result.extracted_content}")

        # Open third tab
        print("\n5. Opening third tab (github.com)...")
        await session.browser.agent.act("Open a new tab and navigate to https://github.com")
        tab3_result = await session.browser.agent.extract("What is the page title?")
        print(f"Tab 3 title: {tab3_result.extracted_content}")

        # List all tabs
        print("\n6. Listing all open tabs...")
        tabs_result = await session.browser.agent.extract("How many tabs are open and what are their URLs?")
        print(f"Open tabs:\n{tabs_result.extracted_content}")

        # Close a specific tab
        print("\n7. Closing the second tab...")
        await session.browser.agent.act("Close the tab with httpbin.org")
        remaining_result = await session.browser.agent.extract("How many tabs are now open?")
        print(f"Remaining tabs: {remaining_result.extracted_content}")

        print("\n=== Example completed successfully ===")

    except Exception as e:
        print(f"\nError occurred: {str(e)}")
        raise

    finally:
        # Clean up
        if session:
            print("\nCleaning up session...")
            await client.delete(session)
            print("Session closed")


if __name__ == "__main__":
    asyncio.run(main())

