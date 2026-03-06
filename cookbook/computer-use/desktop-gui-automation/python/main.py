"""
Desktop GUI Automation with AgentBay Computer Use

This example demonstrates how to automate a Linux desktop GUI application
(gedit text editor) in a cloud environment using the AgentBay SDK's
Computer Use module.

Workflow:
  1. Create a cloud desktop session
  2. Take a screenshot of the initial desktop
  3. Launch a text editor (gedit)
  4. Type text using keyboard simulation
  5. Use Ctrl+A to select all, verify via screenshot
  6. Save the file using the command module (reliable approach)
  7. Close the editor and clean up

Prerequisites:
  - pip install wuying-agentbay-sdk
  - export AGENTBAY_API_KEY=your_api_key_here
"""

import os
import sys
import asyncio

from agentbay import AsyncAgentBay, CreateSessionParams


SCREENSHOT_DIR = os.path.join(os.path.dirname(__file__), "..", "images")
os.makedirs(SCREENSHOT_DIR, exist_ok=True)


async def save_screenshot(session, name: str) -> bool:
    """Take a screenshot and save it locally."""
    result = await session.computer.beta_take_screenshot("png")
    if result.success and result.data:
        path = os.path.join(SCREENSHOT_DIR, f"{name}.png")
        with open(path, "wb") as f:
            f.write(result.data)
        print(f"  Screenshot saved: {name}.png ({len(result.data):,} bytes)")
        return True
    print(f"  Screenshot failed: {result.error_message}")
    return False


async def main():
    api_key = os.getenv("AGENTBAY_API_KEY")
    if not api_key:
        print("Error: Please set the AGENTBAY_API_KEY environment variable")
        sys.exit(1)

    agent_bay = AsyncAgentBay(api_key=api_key)
    session = None

    try:
        # Step 1: Create a cloud desktop session
        print("Step 1: Creating cloud desktop session...")
        result = await agent_bay.create(
            CreateSessionParams(image_id="linux_latest")
        )
        if not result.success:
            print(f"  Failed: {result.error_message}")
            return
        session = result.session
        print(f"  Session created: {session.session_id}")

        # Step 2: Get screen information and take initial screenshot
        print("\nStep 2: Getting screen information...")
        screen = await session.computer.get_screen_size()
        if screen.success:
            print(f"  Screen size: {screen.data['width']}x{screen.data['height']}")
            print(f"  DPI scaling: {screen.data['dpiScalingFactor']}")

        print("  Taking initial desktop screenshot...")
        await save_screenshot(session, "01_initial_desktop")

        # Step 3: Launch gedit text editor
        print("\nStep 3: Launching text editor (gedit)...")
        start_result = await session.computer.start_app("gedit")
        if start_result.success and start_result.data:
            for proc in start_result.data:
                print(f"  Started: {proc.pname} (PID: {proc.pid})")
        else:
            print(f"  start_app failed, trying command fallback...")
            await session.command.execute_command(
                "nohup gedit &>/dev/null &", timeout_ms=5000
            )

        await asyncio.sleep(3)
        print("  Taking screenshot after editor launch...")
        await save_screenshot(session, "02_editor_opened")

        # Step 4: Click in the editor area and type text
        print("\nStep 4: Typing text in the editor...")
        screen_width = screen.data['width'] if screen.success else 1920
        screen_height = screen.data['height'] if screen.success else 1080
        center_x = screen_width // 2
        center_y = screen_height // 2

        click_result = await session.computer.click_mouse(center_x, center_y, "left")
        print(f"  Clicked at ({center_x}, {center_y}): success={click_result.success}")
        await asyncio.sleep(1)

        text_content = "Hello from AgentBay\nThis is an automated desktop demo.\nThe Computer Use API can control mouse, keyboard, and applications."
        text_result = await session.computer.input_text(text_content)
        print(f"  Text input: success={text_result.success}")
        await asyncio.sleep(1)

        print("  Taking screenshot after typing...")
        await save_screenshot(session, "03_text_typed")

        # Step 5: Demonstrate keyboard shortcuts
        print("\nStep 5: Keyboard shortcuts demo...")
        # Select all text with Ctrl+A
        select_result = await session.computer.press_keys(["ctrl", "a"])
        print(f"  Ctrl+A (select all): success={select_result.success}")
        await asyncio.sleep(0.5)
        await save_screenshot(session, "04_text_selected")

        # Deselect by pressing End
        await session.computer.press_keys(["End"])
        await asyncio.sleep(0.3)

        # Step 6: Save the content using command module
        print("\nStep 6: Saving file via command module...")
        file_path = "/tmp/agentbay_demo.txt"
        lines = text_content.split("\n")
        escaped = "\\n".join(lines)
        save_cmd = f'printf "{escaped}\\n" > {file_path}'
        save_result = await session.command.execute_command(save_cmd, timeout_ms=5000)
        print(f"  Save command: success={save_result.success}")

        # Verify the saved file
        verify = await session.command.execute_command(
            f"cat {file_path}", timeout_ms=5000
        )
        if verify.success and verify.output:
            print(f"  File content:")
            for line in verify.output.strip().split("\n"):
                print(f"    | {line}")
        else:
            print(f"  Verification failed: {verify.error_message}")

        # Step 7: Close the editor
        print("\nStep 7: Closing editor with Ctrl+Q...")
        close_result = await session.computer.press_keys(["ctrl", "q"])
        print(f"  Ctrl+Q: success={close_result.success}")
        await asyncio.sleep(2)

        # Handle "Save changes?" dialog — press Tab then Enter to discard
        await session.computer.press_keys(["Tab"])
        await asyncio.sleep(0.3)
        await session.computer.press_keys(["Return"])
        await asyncio.sleep(1)

        print("  Taking final screenshot...")
        await save_screenshot(session, "05_final_desktop")

        # Summary
        print("\n" + "=" * 50)
        print("Workflow completed successfully!")
        print("=" * 50)
        print(f"  Session: {session.session_id}")
        print(f"  File saved at: {file_path}")
        print(f"  Screenshots saved to: {SCREENSHOT_DIR}")

    except Exception as e:
        print(f"\nError: {e}")
        import traceback
        traceback.print_exc()

    finally:
        if session:
            print("\nCleaning up session...")
            await agent_bay.delete(session)
            print("Session deleted.")


if __name__ == "__main__":
    asyncio.run(main())
