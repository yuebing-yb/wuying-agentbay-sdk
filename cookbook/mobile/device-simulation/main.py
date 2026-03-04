"""
Cloud Phone Device Simulation Example

Demonstrates how to use MobileSimulateService to make a cloud phone
appear as a real physical device, and persist device identity across sessions.

Steps:
1. Upload mobile device info and create first simulated session
2. Verify device properties match the simulated device
3. Delete session and create a second session with the same context
4. Verify device identity is consistent across sessions
"""

import asyncio
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "../../../python"))

from agentbay import AsyncAgentBay, CreateSessionParams, ExtraConfigs
from agentbay import MobileExtraConfig, MobileSimulateMode
from agentbay import AsyncMobileSimulateService


MOBILE_INFO_FILE = os.path.join(
    os.path.dirname(__file__), "../../../resource/mobile_info_model_a.json"
)


async def main():
    api_key = os.environ.get("AGENTBAY_API_KEY")
    if not api_key:
        print("Error: AGENTBAY_API_KEY environment variable not set")
        return

    agent_bay = AsyncAgentBay(api_key)
    print("AgentBay client initialized\n")

    session1 = None
    session2 = None

    try:
        # ── Step 1: Upload device info and create first session ──────────
        print("=" * 60)
        print("Step 1: Upload device info & create first simulated session")
        print("=" * 60)

        simulate_service = AsyncMobileSimulateService(agent_bay)
        simulate_service.set_simulate_enable(True)
        simulate_service.set_simulate_mode(MobileSimulateMode.PROPERTIES_ONLY)

        with open(MOBILE_INFO_FILE, "r") as f:
            mobile_info_content = f.read()
        print(f"Loaded device info from: {MOBILE_INFO_FILE}")

        upload_result = await simulate_service.upload_mobile_info(mobile_info_content)
        if not upload_result.success:
            print(f"Failed to upload mobile info: {upload_result.error_message}")
            return

        simulate_context_id = upload_result.mobile_simulate_context_id
        print(f"Device info uploaded. Context ID: {simulate_context_id}")

        params = CreateSessionParams(
            image_id="mobile_latest",
            extra_configs=ExtraConfigs(
                mobile=MobileExtraConfig(
                    simulate_config=simulate_service.get_simulate_config()
                )
            ),
        )

        print("Creating first session...")
        result1 = await agent_bay.create(params)
        if not result1.success or not result1.session:
            print(f"Failed to create session: {result1.error_message}")
            return

        session1 = result1.session
        print(f"Session 1 created: {session1.session_id}\n")

        # ── Step 2: Verify simulated device properties ───────────────────
        print("=" * 60)
        print("Step 2: Verify simulated device properties")
        print("=" * 60)

        await asyncio.sleep(5)

        props_to_check = [
            "ro.product.model",
            "ro.product.brand",
            "ro.product.manufacturer",
        ]
        session1_props = {}
        for prop in props_to_check:
            cmd_result = await session1.command.execute_command(f"getprop {prop}")
            value = cmd_result.output.strip() if cmd_result.success else "ERROR"
            session1_props[prop] = value
            print(f"  {prop} = {value}")

        print()

        # ── Step 3: Delete session 1, create session 2 with same context ─
        print("=" * 60)
        print("Step 3: Recreate session with same device identity")
        print("=" * 60)

        print("Deleting session 1...")
        delete_result = await agent_bay.delete(session1, sync_context=True)
        if not delete_result.success:
            print(f"Failed to delete session 1: {delete_result.error_message}")
            return
        session1 = None
        print("Session 1 deleted.\n")

        await asyncio.sleep(3)

        simulate_service2 = AsyncMobileSimulateService(agent_bay)
        simulate_service2.set_simulate_enable(True)
        simulate_service2.set_simulate_mode(MobileSimulateMode.PROPERTIES_ONLY)
        simulate_service2.set_simulate_context_id(simulate_context_id)

        params2 = CreateSessionParams(
            image_id="mobile_latest",
            extra_configs=ExtraConfigs(
                mobile=MobileExtraConfig(
                    simulate_config=simulate_service2.get_simulate_config()
                )
            ),
        )

        print("Creating second session with same context...")
        result2 = await agent_bay.create(params2)
        if not result2.success or not result2.session:
            print(f"Failed to create session 2: {result2.error_message}")
            return

        session2 = result2.session
        print(f"Session 2 created: {session2.session_id}\n")

        # ── Step 4: Verify device identity consistency ───────────────────
        print("=" * 60)
        print("Step 4: Verify device identity consistency across sessions")
        print("=" * 60)

        await asyncio.sleep(5)

        all_match = True
        for prop in props_to_check:
            cmd_result = await session2.command.execute_command(f"getprop {prop}")
            value = cmd_result.output.strip() if cmd_result.success else "ERROR"
            prev = session1_props[prop]
            match = "✓" if value == prev else "✗"
            if value != prev:
                all_match = False
            print(f"  {match} {prop}: {value} (session 1: {prev})")

        print()
        if all_match:
            print("Device identity is consistent across sessions!")
        else:
            print("WARNING: Some properties differ between sessions.")

    except Exception as e:
        print(f"\nError: {e}")
        raise

    finally:
        if session1:
            print("\nCleaning up session 1...")
            await agent_bay.delete(session1)
        if session2:
            print("Cleaning up session 2...")
            await agent_bay.delete(session2)

    print("\nExample completed.")


if __name__ == "__main__":
    asyncio.run(main())
