"""
Example demonstrating Browser Fingerprint local sync feature with AgentBay SDK.

This example shows how to sync local browser fingerprint to remote browser fingerprint.
BrowserFingerprintGenerator has ability to dump local installed chrome browser fingerprint,
and then you can sync it to remote browser fingerprint by using BrowserOption.fingerprint_format.

This example will:
1. Generate local chrome browser fingerprint by BrowserFingerprintGenerator
2. Sync local browser fingerprint to remote browser fingerprint
3. Verify remote browser fingerprint
4. Clean up session
"""

import os
import asyncio

from agentbay import AgentBay
from agentbay.session_params import CreateSessionParams
from agentbay.browser.browser import BrowserOption
from agentbay.browser.fingerprint import BrowserFingerprintGenerator

from playwright.async_api import async_playwright


async def main():
    """Main function demonstrating browser fingerprint basic usage."""
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
    params = CreateSessionParams(
        image_id="browser_latest",
    )
    session_result = agent_bay.create(params)

    if session_result.success:
        session = session_result.session
        print(f"Session created with ID: {session.session_id}")

        fingerprint_generator = BrowserFingerprintGenerator()
        fingerprint_format = await fingerprint_generator.generate_fingerprint()

        # Create browser option with fingerprint format.
        # Fingerprint format is dumped from local chrome browser by BrowserFingerprintGenerator
        # automatically, you can use it to sync to remote browser fingerprint.
        browser_option = BrowserOption(
            use_stealth=True,
            fingerprint_format=fingerprint_format
        )

        if await session.browser.initialize_async(browser_option):
            endpoint_url = session.browser.get_endpoint_url()
            print("endpoint_url =", endpoint_url)

            async with async_playwright() as p:
                browser = await p.chromium.connect_over_cdp(endpoint_url)
                context = browser.contexts[0]
                page = await context.new_page()
                
                # Check user agent.
                print("\n--- Check User Agent ---")
                await page.goto("https://httpbin.org/user-agent")

                response = await page.evaluate("() => JSON.parse(document.body.textContent)")
                user_agent = response.get("user-agent", "")
                print(f"User Agent: {user_agent}")

                print("Please check if User Agent is synced correctly by visiting https://httpbin.org/user-agent in local chrome browser.")

                await page.wait_for_timeout(3000)
                await browser.close()

        # Clean up session
        agent_bay.delete(session)
    

if __name__ == "__main__":
    asyncio.run(main())