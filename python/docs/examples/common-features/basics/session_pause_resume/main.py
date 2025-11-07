# Session Pause and Resume Example

# This example demonstrates the complete workflow of session pause and resume operations.

import asyncio
import time
from agentbay import AgentBay

def basic_pause_resume():
    """Basic pause and resume workflow"""
    print("=== Basic Pause and Resume Example ===")
    
    # Initialize SDK
    agent_bay = AgentBay()

    # Create session
    print("🔧 Creating session...")
    create_result = agent_bay.create()
    if not create_result.success:
        print(f"❌ Failed to create session: {create_result.error_message}")
        return

    session = create_result.session
    print(f"✅ Session created: {session.session_id}")

    # Perform some work
    print("💻 Executing initial commands...")
    result = session.command.execute_command("echo 'Initial work completed'")
    print(f"Output: {result.output}")

    # Pause the session
    print("⏸️  Pausing session...")
    pause_result = session.pause()
    if not pause_result.success:
        print(f"❌ Failed to pause session: {pause_result.error_message}")
    else:
        print("✅ Session paused successfully")

    # Resume the session
    print("▶️  Resuming session...")
    resume_result = session.resume()
    if not resume_result.success:
        print(f"❌ Failed to resume session: {resume_result.error_message}")
    else:
        print("✅ Session resumed successfully")

    # Perform work after resume
    print("💻 Executing commands after resume...")
    result = session.command.execute_command("echo 'Work after resume completed'")
    print(f"Output: {result.output}")

    # Clean up
    print("🧹 Deleting session...")
    delete_result = agent_bay.delete(session)
    if delete_result.success:
        print("✅ Session deleted successfully")
    else:
        print(f"❌ Failed to delete session: {delete_result.error_message}")

def session_status_monitoring():
    """Monitor session status during pause/resume operations"""
    print("\n=== Session Status Monitoring Example ===")
    
    def check_session_status(session):
        """Check and display session status"""
        info_result = session.info()
        if info_result.success:
            status = getattr(info_result.data, 'status', 'UNKNOWN')
            print(f"📊 Session status: {status}")
            return status
        else:
            print(f"❌ Failed to get session info: {info_result.error_message}")
            return None

    # Initialize SDK
    agent_bay = AgentBay()

    # Create session
    print("🔧 Creating session...")
    create_result = agent_bay.create()
    if not create_result.success:
        print(f"❌ Failed to create session: {create_result.error_message}")
        return

    session = create_result.session
    print(f"✅ Session created: {session.session_id}")

    # Check initial status
    print("🔍 Checking initial session status...")
    check_session_status(session)

    # Perform some work
    print("💻 Executing work before pause...")
    result = session.command.execute_command("sleep 2 && echo 'Work completed'")
    print(f"Output: {result.output}")

    # Check status before pause
    print("🔍 Checking session status before pause...")
    check_session_status(session)

    # Pause the session
    print("⏸️  Pausing session...")
    pause_result = session.pause(timeout=120)  # 2 minute timeout
    if pause_result.success:
        print("✅ Session paused successfully")
    else:
        print(f"❌ Failed to pause session: {pause_result.error_message}")

    # Check status after pause
    print("🔍 Checking session status after pause...")
    check_session_status(session)

    # Resume the session
    print("▶️  Resuming session...")
    resume_result = session.resume(timeout=120)  # 2 minute timeout
    if resume_result.success:
        print("✅ Session resumed successfully")
    else:
        print(f"❌ Failed to resume session: {resume_result.error_message}")

    # Check status after resume
    print("🔍 Checking session status after resume...")
    check_session_status(session)

    # Clean up
    print("🧹 Deleting session...")
    delete_result = agent_bay.delete(session)
    if delete_result.success:
        print("✅ Session deleted successfully")
    else:
        print(f"❌ Failed to delete session: {delete_result.error_message}")

async def async_pause_resume():
    """Asynchronous pause and resume operations"""
    print("\n=== Asynchronous Pause and Resume Example ===")
    
    # Initialize SDK
    agent_bay = AgentBay()

    # Create session
    print("🔧 Creating session...")
    create_result = agent_bay.create()
    if not create_result.success:
        print(f"❌ Failed to create session: {create_result.error_message}")
        return

    session = create_result.session
    print(f"✅ Session created: {session.session_id}")

    # Perform some work
    print("💻 Executing initial work...")
    result = session.command.execute_command("echo 'Async operations test'")
    print(f"Output: {result.output}")

    # Asynchronously pause the session
    print("⏸️  Asynchronously pausing session...")
    pause_result = await session.pause_async()
    if pause_result.success:
        print("✅ Session paused successfully")
        print(f"Request ID: {pause_result.request_id}")
    else:
        print(f"❌ Failed to pause session: {pause_result.error_message}")

    # Asynchronously resume the session
    print("▶️  Asynchronously resuming session...")
    resume_result = await session.resume_async()
    if resume_result.success:
        print("✅ Session resumed successfully")
        print(f"Request ID: {resume_result.request_id}")
    else:
        print(f"❌ Failed to resume session: {resume_result.error_message}")

    # Perform work after resume
    print("💻 Executing work after async resume...")
    result = session.command.execute_command("echo 'Work after async resume'")
    print(f"Output: {result.output}")

    # Clean up
    print("🧹 Deleting session...")
    delete_result = agent_bay.delete(session)
    if delete_result.success:
        print("✅ Session deleted successfully")
    else:
        print(f"❌ Failed to delete session: {delete_result.error_message}")

def error_handling():
    """Error handling scenarios"""
    print("\n=== Error Handling Example ===")
    
    # Initialize SDK
    agent_bay = AgentBay()

    # Try to pause a non-existent session
    print("🧪 Testing pause on non-existent session...")
    try:
        # Try to get a session that doesn't exist
        get_result = agent_bay.get("session-non-existent-id")
        if get_result.success:
            fake_session = get_result.session
            pause_result = fake_session.pause()
            if not pause_result.success:
                print(f"✅ Expected error: {pause_result.error_message}")
        else:
            print(f"✅ Expected error when getting session: {get_result.error_message}")
    except Exception as e:
        print(f"✅ Caught expected exception: {e}")

    # Create a valid session for further testing
    print("🔧 Creating valid session for testing...")
    create_result = agent_bay.create()
    if not create_result.success:
        print(f"❌ Failed to create session: {create_result.error_message}")
        return

    session = create_result.session
    print(f"✅ Session created: {session.session_id}")

    # Test pause with short timeout (likely to fail)
    print("🧪 Testing pause with very short timeout...")
    pause_result = session.pause(timeout=1, poll_interval=0.1)
    if not pause_result.success:
        print(f"✅ Handled short timeout gracefully: {pause_result.error_message}")

    # Clean up
    print("🧹 Cleaning up...")
    delete_result = agent_bay.delete(session)
    if delete_result.success:
        print("✅ Session deleted successfully")
    else:
        print(f"❌ Failed to delete session: {delete_result.error_message}")

def main():
    """Run all examples"""
    print("🚀 Running Session Pause and Resume Examples")
    
    # Run basic example
    basic_pause_resume()
    
    # Run status monitoring example
    session_status_monitoring()
    
    # Run async example
    asyncio.run(async_pause_resume())
    
    # Run error handling example
    error_handling()
    
    print("\n🎉 All examples completed!")

if __name__ == "__main__":
    main()