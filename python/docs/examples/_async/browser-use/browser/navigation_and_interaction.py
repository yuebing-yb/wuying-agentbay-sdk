"""
Browser Navigation and Interaction Example

This example demonstrates:
1. Basic browser navigation
2. Element interaction (click, type, select)
3. Page state verification
4. Navigation history management
"""

import asyncio
import os
import sys

# Add parent directory to path for imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))))

from agentbay import AsyncAgentBay, CreateSessionParams
from agentbay._async.browser import BrowserOption
from agentbay._async.browser_agent import ActOptions


async def main():
    """Demonstrate browser navigation and interaction."""
    print("=== Browser Navigation and Interaction Example ===\n")

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

        # Navigate to a test page
        print("\n1. Navigating to example.com...")
        await session.browser.agent.navigate("https://example.com")
        print("Navigation successful")

        # Take a screenshot
        print("\n2. Taking screenshot...")
        screenshot_path = await session.browser.agent.screenshot()
        print(f"Screenshot saved to: {screenshot_path}")

        # Navigate to another page
        print("\n3. Navigating to httpbin.org/forms/post...")
        await session.browser.agent.navigate("https://httpbin.org/forms/post")

        # Interact with form elements
        print("\n4. Filling form...")
        await session.browser.agent.act(ActOptions("Fill in the customer name field with 'John Doe'"))
        await session.browser.agent.act(ActOptions("Fill in the telephone field with '1234567890'"))
        await session.browser.agent.act(ActOptions("Fill in the email field with 'john@example.com'"))
        print("Form filled successfully")

        # Navigate back
        print("\n5. Navigating back...")
        await session.browser.agent.navigate("back")
        print("Navigated back to previous page")

        # Navigate forward
        print("\n6. Navigating forward...")
        await session.browser.agent.navigate("forward")
        print("Navigated forward")

        # Get current URL
        print("\n7. Extracting current URL...")
        url_result = await session.browser.agent.extract("What is the current page URL?")
        print(f"Current URL: {url_result.extracted_content}")

        # Verify page state
        print("\n8. Verifying page state...")
        state_result = await session.browser.agent.extract("Is there a form on this page?")
        print(f"Page state: {state_result.extracted_content}")

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

