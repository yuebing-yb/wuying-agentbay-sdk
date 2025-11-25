#!/usr/bin/env python3
"""
AgentBay SDK - Context Sync Example

This example demonstrates the context.sync_context() method:
- Context creation for persistent storage
- Synchronous API usage
- Timing and status monitoring
- Error handling and timeout scenarios
"""

import json
import time
from agentbay import AgentBay, CreateSessionParams, ContextSync, SyncPolicy

def main():
    """Main function"""
    print("🔄 AgentBay Context Sync Example")

    # Initialize AgentBay client
    agent_bay = AgentBay()

    try:
        # Method 1: Sync API demo
        print("\n" + "="*60)
        print("🔄 Method 1: context_sync_demo_1")
        print("="*60)
        context_sync_demo_1(agent_bay)
        print("="*60)

        # Sleep 3 seconds
        print("\n⏳ Sleeping 3 seconds before next demo...")
        time.sleep(3)

        # Method 2: Sync API demo
        print("\n" + "="*60)
        print("🔄 Method 2: context_sync_demo_2")
        print("="*60)
        context_sync_demo_2(agent_bay)

    except Exception as e:
        print(f"❌ Example execution failed: {e}")
        import traceback
        traceback.print_exc()

    print("✅ Context sync example completed")


def context_sync_demo_1(agent_bay):
    """Method 1: Synchronous context sync demo"""
    print("\n🔄 Method 1: context_sync_demo_1")
    print("📤 This method uses synchronous API")
    print("⏳ Function waits until sync is complete")
    
    # Create context and session
    print("\n📦 Creating context and session...")
    context_result = agent_bay.context.get("sync-demo-1", create=True)
    if not context_result.success:
        print(f"❌ Context creation failed: {context_result.error_message}")
        return
    
    context = context_result.context
    print(f"✅ Context created: {context.id}")
    
    # Create session with context sync
    sync_policy = SyncPolicy.default()
    context_sync = ContextSync.new(
        context_id=context.id,
        path="/tmp/sync_data",
        policy=sync_policy
    )
    
    params = CreateSessionParams()
    params.context_syncs = [context_sync]
    session_result = agent_bay.create(params)
    
    if not session_result.success:
        print(f"❌ Session creation failed: {session_result.error_message}")
        return
    
    session = session_result.session
    print(f"✅ Session created: {session.session_id}")
    
    # Create test data
    print("\n💾 Creating test data...")
    session.command.execute_command("mkdir -p /tmp/sync_data/test_files")
    
    test_files = [
        ("/tmp/sync_data/test_files/small.txt", "Small test file content\n" * 10),
        ("/tmp/sync_data/test_files/medium.txt", "Medium test file content\n" * 100),
        ("/tmp/sync_data/config.json", json.dumps({
            "sync_demo": True,
            "created_at": time.strftime("%Y-%m-%d %H:%M:%S"),
            "session_id": session.session_id
        }, indent=2))
    ]
    
    created_files = 0
    for file_path, content in test_files:
        write_result = session.file_system.write_file(file_path, content)
        if write_result.success:
            print(f"✅ Created file: {file_path}")
            created_files += 1
        else:
            print(f"❌ Failed to create file {file_path}: {write_result.error_message}")
    
    print(f"📊 Created {created_files}/{len(test_files)} test files")
    
    # Track sync timing
    sync_start_time = time.time()
    
    # Call context.sync_context() - wait for completion
    print("\n📤 Calling session.context.sync_context()...")
    sync_result = session.context.sync_context(
        context_id=context.id,
        path="/tmp/sync_data"
    )
    
    sync_duration = time.time() - sync_start_time

    if sync_result.success:
        print("✅ Sync completed successfully")
        print(f"   Request ID: {sync_result.request_id}")
        print(f"   Final success: {sync_result.success}")
        print(f"   Duration: {sync_duration:.2f} seconds")
    else:
        print("❌ Sync failed")
        print(f"   Request ID: {sync_result.request_id}")
        print(f"   Error: {sync_result.error_message}")
        print(f"   Duration: {sync_duration:.2f} seconds")

    # Clean up session
    print("\n🧹 Cleaning up session...")
    delete_result = agent_bay.delete(session)
    if delete_result.success:
        print("✅ Session deleted successfully")
    else:
        print(f"❌ Session deletion failed: {delete_result.error_message}")

    print("✅ Method 1 completed")

def context_sync_demo_2(agent_bay):
    """Method 2: Synchronous context sync demo"""
    print("\n🔄 Method 2: context_sync_demo_2")
    print("📤 This method uses synchronous API")
    print("⏳ Function waits until sync is complete")
    
    # Create context and session
    print("\n📦 Creating context and session...")
    context_result = agent_bay.context.get("sync-demo-2", create=True)
    if not context_result.success:
        print(f"❌ Context creation failed: {context_result.error_message}")
        return
    
    context = context_result.context
    print(f"✅ Context created: {context.id}")
    
    # Create session with context sync
    sync_policy = SyncPolicy.default()
    context_sync = ContextSync.new(
        context_id=context.id,
        path="/tmp/sync_data",
        policy=sync_policy
    )
    
    params = CreateSessionParams()
    params.context_syncs = [context_sync]
    session_result = agent_bay.create(params)
    
    if not session_result.success:
        print(f"❌ Session creation failed: {session_result.error_message}")
        return
    
    session = session_result.session
    print(f"✅ Session created: {session.session_id}")
    
    # Create test data
    print("\n💾 Creating test data...")
    session.command.execute_command("mkdir -p /tmp/sync_data/test_files")
    
    test_files = [
        ("/tmp/sync_data/test_files/small.txt", "Small test file content\n" * 10),
        ("/tmp/sync_data/test_files/medium.txt", "Medium test file content\n" * 100),
        ("/tmp/sync_data/config.json", json.dumps({
            "sync_demo": True,
            "created_at": time.strftime("%Y-%m-%d %H:%M:%S"),
            "session_id": session.session_id
        }, indent=2))
    ]
    
    created_files = 0
    for file_path, content in test_files:
        write_result = session.file_system.write_file(file_path, content)
        if write_result.success:
            print(f"✅ Created file: {file_path}")
            created_files += 1
        else:
            print(f"❌ Failed to create file {file_path}: {write_result.error_message}")
    
    print(f"📊 Created {created_files}/{len(test_files)} test files")
    
    # Track sync timing
    sync_start_time = time.time()
    
    # Call context.sync_context() - wait for completion
    print("\n📤 Calling session.context.sync_context()...")
    sync_result = session.context.sync_context(
        context_id=context.id,
        path="/tmp/sync_data"
    )
    
    sync_duration = time.time() - sync_start_time
    
    if sync_result.success:
        print("✅ Sync completed successfully")
        print(f"   Request ID: {sync_result.request_id}")
        print(f"   Final success: {sync_result.success}")
        print(f"   Duration: {sync_duration:.2f} seconds")
    else:
        print("❌ Sync failed")
        print(f"   Request ID: {sync_result.request_id}")
        print(f"   Final success: {sync_result.success}")
        print(f"   Duration: {sync_duration:.2f} seconds")
    
    # Clean up session
    print("\n🧹 Cleaning up session...")
    delete_result = agent_bay.delete(session)
    if delete_result.success:
        print("✅ Session deleted successfully")
    else:
        print(f"❌ Session deletion failed: {delete_result.error_message}")

    print("✅ Method 2 completed")



if __name__ == "__main__":
    main()

