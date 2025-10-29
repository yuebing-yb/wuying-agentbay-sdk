"""
Example demonstrating screenshot capabilities with AgentBay SDK.
This example shows how to capture screenshots using both the browser agent and direct Playwright integration.

Features demonstrated:
- Creating a browser session with AgentBay
- Using Playwright to connect to the browser instance
- Taking screenshots using the browser agent (base64 data)
- Taking screenshots using direct Playwright integration (bytes data)
- Saving screenshots to local files
- Customizing screenshot options (full page, image format, quality)
"""

import os
import base64
import asyncio
from typing import Optional
from playwright.async_api import async_playwright

from agentbay import AgentBay
from agentbay.session import Session
from agentbay.session_params import CreateSessionParams
from agentbay.browser.browser import BrowserOption


async def take_agent_screenshots(session: Session):
    """Take screenshots using the browser agent (returns base64 data)."""
    print("📸 Taking screenshots using browser agent...")
    
    # Navigate to a website
    await session.browser.agent.navigate_async("https://www.aliyun.com")
    
    # Take a simple screenshot (returns base64 data)
    screenshot_b64 = await session.browser.agent.screenshot_async()
    print(f"✅ Agent screenshot captured (base64 length: {len(screenshot_b64)})")
    
    # Save the screenshot to a file
    if screenshot_b64.startswith("data:image/"):
        # Extract the base64 data from data URL
        _, encoded = screenshot_b64.split(",", 1)
        image_data = base64.b64decode(encoded)
    else:
        # Assume it's raw base64
        image_data = base64.b64decode(screenshot_b64)
    
    with open("agent_screenshot.png", "wb") as f:
        f.write(image_data)
    print("✅ Agent screenshot saved as agent_screenshot.png")
    
    # Take a full page screenshot with custom quality
    full_page_b64 = await session.browser.agent.screenshot_async(
        full_page=True,
        quality=75
    )
    print(f"✅ Agent full page screenshot captured (base64 length: {len(full_page_b64)})")
    
    # Save the full page screenshot
    if full_page_b64.startswith("data:image/"):
        _, encoded = full_page_b64.split(",", 1)
        image_data = base64.b64decode(encoded)
    else:
        image_data = base64.b64decode(full_page_b64)
    
    with open("agent_full_page_screenshot.png", "wb") as f:
        f.write(image_data)
    print("✅ Agent full page screenshot saved as agent_full_page_screenshot.png")


async def take_browser_screenshots(session: Session):
    """Take screenshots using direct Playwright integration (returns bytes data)."""
    print("📸 Taking screenshots using direct Playwright integration...")
    
    # Get the browser endpoint and connect with Playwright
    endpoint_url = session.browser.get_endpoint_url()
    async with async_playwright() as p:
        browser = await p.chromium.connect_over_cdp(endpoint_url)
        context = browser.contexts[0]
        page = await context.new_page()
        
        # Navigate to a website
        await page.goto("https://www.aliyun.com")
        print("✅ Navigated to website")
        
        # Take a simple screenshot (returns bytes data)
        screenshot_bytes = await session.browser.screenshot(page)
        print(f"✅ Browser screenshot captured ({len(screenshot_bytes)} bytes)")
        
        # Save the screenshot to a file
        with open("browser_screenshot.png", "wb") as f:
            f.write(screenshot_bytes)
        print("✅ Browser screenshot saved as browser_screenshot.png")
        
        # Take a full page screenshot with custom options
        full_page_bytes = await session.browser.screenshot(
            page,
            full_page=True,
            type="jpeg",
            quality=80
        )
        print(f"✅ Browser full page screenshot captured ({len(full_page_bytes)} bytes)")
        
        # Save the full page screenshot
        with open("browser_full_page_screenshot.jpg", "wb") as f:
            f.write(full_page_bytes)
        print("✅ Browser full page screenshot saved as browser_full_page_screenshot.jpg")
        
        # Take a screenshot with custom viewport settings
        custom_screenshot = await session.browser.screenshot(
            page,
            full_page=False,
            type="png",
            timeout=30000
        )
        print(f"✅ Browser custom screenshot captured ({len(custom_screenshot)} bytes)")
        
        # Save the custom screenshot
        with open("browser_custom_screenshot.png", "wb") as f:
            f.write(custom_screenshot)
        print("✅ Browser custom screenshot saved as browser_custom_screenshot.png")
        
        await browser.close()


async def main():
    # Get API key from environment variable
    api_key = os.getenv("AGENTBAY_API_KEY")
    if not api_key:
        print("Error: AGENTBAY_API_KEY environment variable not set")
        return

    # Initialize AgentBay client
    print("Initializing AgentBay client...")
    agent_bay = AgentBay(api_key=api_key)

    # Create a session
    print("Creating a new session...")
    params = CreateSessionParams(image_id="browser_latest")
    session_result = agent_bay.create(params)

    if not session_result.success:
        print(f"Failed to create session: {session_result.error_message}")
        return

    session: Optional[Session] = session_result.session
    if session is None:
        print("Failed to create session: session is None")
        return
        
    print(f"Session created with ID: {session.session_id}")

    try:
        # Initialize the browser
        browser_option = BrowserOption()
        if not await session.browser.initialize_async(browser_option):
            print("Failed to initialize browser")
            return
        
        print("Browser initialized successfully")
        
        # Take screenshots using the browser agent
        await take_agent_screenshots(session)
        
        print("\n" + "="*50 + "\n")
        
        # Take screenshots using direct Playwright integration
        await take_browser_screenshots(session)
        
        print("\n" + "="*50)
        print("✅ All screenshot demos completed successfully!")
        print("📁 Check the current directory for saved screenshot files:")
        print("   - agent_screenshot.png")
        print("   - agent_full_page_screenshot.png")
        print("   - browser_screenshot.png")
        print("   - browser_full_page_screenshot.jpg")
        print("   - browser_custom_screenshot.png")

    except Exception as e:
        print(f"Error during screenshot demo: {e}")
    
    finally:
        # Clean up: delete the session
        print(f"\n🧹 Cleaning up session {session.session_id}...")
        try:
            agent_bay.delete(session)
            print("✅ Session deleted successfully")
        except Exception as e:
            print(f"⚠️  Warning: Error during cleanup: {e}")


if __name__ == "__main__":
    print("📸 AgentBay Browser Screenshot Demo")
    print("=" * 50)
    asyncio.run(main())