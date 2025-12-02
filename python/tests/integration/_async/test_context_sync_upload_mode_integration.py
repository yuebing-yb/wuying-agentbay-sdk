import asyncio
import os
import random
import time
import unittest

from agentbay import AsyncAgentBay, CreateSessionParams
from agentbay import (
    BWList,
    ContextSync,
    DeletePolicy,
    DownloadPolicy,
    ExtractPolicy,
    RecyclePolicy,
    SyncPolicy,
    UploadMode,
    UploadPolicy,
    WhiteList,
)
from agentbay import AsyncSession


def get_test_api_key():
    """Get API key for testing"""
    return os.environ.get("AGENTBAY_API_KEY")


def generate_unique_id():
    """Generate unique ID for test isolation."""
    timestamp = int(time.time() * 1000000) + random.randint(0, 999)
    random_part = random.randint(0, 9999)
    return f"{timestamp}-{random_part}"


class TestContextSyncUploadModeIntegration(unittest.IsolatedAsyncioTestCase):
    """Context Sync Upload Mode Integration Tests"""

    @classmethod
    def setUpClass(cls):
        """Setup test class with unique ID and session tracking."""
        # Get API Key
        api_key = get_test_api_key()
        if not api_key:
            raise unittest.SkipTest("AGENTBAY_API_KEY environment variable not set")

        # Initialize AsyncAgentBay client
        cls.agent_bay = AsyncAgentBay(api_key=api_key)

        cls.unique_id = generate_unique_id()
        cls.test_sessions = []
        print(f"Using unique ID for test: {cls.unique_id}")

    @classmethod
    def tearDownClass(cls):
        """Cleanup all test sessions."""
        print("Cleaning up: Deleting all test sessions...")
        # Note: Sessions should be cleaned up in individual tests
        # This is a safety net for any remaining sessions

    async def test_create_session_with_default_file_upload_mode(self):
        """Test creating session with default File upload mode and write file."""
        print("\n=== Testing basic functionality with default File upload mode ===")

        # Step 1: Use context.get method to generate contextId
        context_name = f"test-context-{self.__class__.unique_id}"
        print(f"Creating context with name: {context_name}")

        context_result = await self.agent_bay.context.get(context_name, True)
        self.assertTrue(
            context_result.success,
            f"Failed to create context: {context_result.error_message}",
        )
        self.assertIsNotNone(context_result.context_id)
        self.assertNotEqual(context_result.context_id, "")

        print(f"Generated contextId: {context_result.context_id}")
        print(f"Context get request ID: {context_result.request_id}")

        # Step 2: Create session with contextSync using default File uploadMode
        sync_policy = SyncPolicy.default()  # Uses default uploadMode "File"

        context_sync = ContextSync(
            context_id=context_result.context_id, path="/tmp/test", policy=sync_policy
        )

        session_params = CreateSessionParams(
            labels={
                "test": f"upload-mode-{self.__class__.unique_id}",
                "type": "basic-functionality",
            },
            context_syncs=[context_sync],
        )

        print("Creating session with default File upload mode...")
        session_result = await self.agent_bay.create(session_params)
        self.assertTrue(
            session_result.success,
            f"Failed to create session: {session_result.error_message}",
        )
        self.assertIsNotNone(session_result.session)
        self.assertIsNotNone(session_result.request_id)
        self.assertNotEqual(session_result.request_id, "")

        session = session_result.session
        self.test_sessions.append(session)

        print(f"✅ Session created successfully!")
        print(f"Session ID: {session.session_id}")
        print(f"Session creation request ID: {session_result.request_id}")

        # Get session info to verify appInstanceId
        session_info = await self.agent_bay.get_session(session.session_id)
        self.assertTrue(
            session_info.success,
            f"Failed to get session info: {session_info.error_message}",
        )
        self.assertIsNotNone(session_info.data)

        print(f"App Instance ID: {session_info.data.app_instance_id}")
        print(f"Get session request ID: {session_info.request_id}")

        print("✅ All basic functionality tests passed!")

        # Cleanup
        print("Cleaning up: Deleting the session...")
        delete_result = await self.agent_bay.delete(session, sync_context=True)
        self.assertTrue(
            delete_result.success,
            f"Failed to delete session: {delete_result.error_message}",
        )
        print(f"Session {session.session_id} deleted successfully")
        self.test_sessions.remove(session)

    async def test_context_sync_with_archive_mode_and_file_operations(self):
        """Test contextId and path usage with Archive mode and file operations."""
        print(
            "\n=== Testing contextId and path usage with Archive mode and file operations ==="
        )

        context_name = f"archive-mode-context-{self.__class__.unique_id}"
        context_result = await self.agent_bay.context.get(context_name, True)

        self.assertTrue(
            context_result.success,
            f"Failed to create context: {context_result.error_message}",
        )
        self.assertIsNotNone(context_result.context_id)
        self.assertNotEqual(context_result.context_id, "")

        print(f"Generated contextId: {context_result.context_id}")

        # Create sync policy with Archive upload mode
        upload_policy = UploadPolicy(upload_mode=UploadMode.ARCHIVE)
        sync_policy = SyncPolicy(upload_policy=upload_policy)

        context_sync = ContextSync.new(
            context_id=context_result.context_id,
            path="/tmp/archive-mode-test",
            policy=sync_policy,
        )

        self.assertEqual(context_sync.context_id, context_result.context_id)
        self.assertEqual(context_sync.path, "/tmp/archive-mode-test")
        self.assertEqual(
            context_sync.policy.upload_policy.upload_mode, UploadMode.ARCHIVE
        )

        print(
            "✅ ContextSync.new works correctly with contextId and path using Archive mode"
        )

        # Create session with the contextSync
        session_params = CreateSessionParams(
            labels={
                "test": f"archive-mode-{self.__class__.unique_id}",
                "type": "contextId-path-validation",
            },
            context_syncs=[context_sync],
        )

        print("Creating session with Archive mode contextSync...")
        session_result = await self.agent_bay.create(session_params)

        self.assertTrue(
            session_result.success,
            f"Failed to create session: {session_result.error_message}",
        )
        self.assertIsNotNone(session_result.session)
        self.assertIsNotNone(session_result.request_id)

        session = session_result.session
        self.test_sessions.append(session)

        # Get session info to verify appInstanceId
        session_info = await self.agent_bay.get_session(session.session_id)
        self.assertTrue(
            session_info.success,
            f"Failed to get session info: {session_info.error_message}",
        )
        self.assertIsNotNone(session_info.data)

        print(f"App Instance ID: {session_info.data.app_instance_id}")

        print(f"✅ Session created successfully with ID: {session.session_id}")
        print(f"Session creation request ID: {session_result.request_id}")

        # Write a 5KB file using FileSystem
        print("Writing 5KB file using FileSystem...")

        # Generate 5KB content (approximately 5120 bytes)
        content_size = 5 * 1024  # 5KB
        base_content = "Archive mode test successful! This is a test file created in the session path. "
        repeated_content = base_content * (content_size // len(base_content) + 1)
        file_content = repeated_content[:content_size]

        # Create file path in the session path directory
        file_path = "/tmp/archive-mode-test/test-file-5kb.txt"

        print(f"Creating file: {file_path}")
        print(f"File content size: {len(file_content)} bytes")

        write_result = await session.file_system.write_file(
            file_path, file_content, "overwrite"
        )

        # Verify file write success
        self.assertTrue(
            write_result.success, f"Failed to write file: {write_result.error_message}"
        )
        self.assertIsNotNone(write_result.request_id)
        self.assertNotEqual(write_result.request_id, "")

        print(f"✅ File write successful!")
        print(f"Write file request ID: {write_result.request_id}")

        # Test context sync and info functionality
        print("Testing context sync functionality...")
        # Call context sync before getting info
        print("Calling context sync before getting info...")

        # Call the async sync method directly
        sync_result = await session.context.sync()

        self.assertTrue(
            sync_result.success, f"Failed to sync context: {sync_result.error_message}"
        )
        self.assertIsNotNone(sync_result.request_id)

        print(f"✅ Context sync successful!")
        print(f"Sync request ID: {sync_result.request_id}")

        # Now call context info after sync
        print("Calling context info after sync...")
        info_result = await session.context.info()

        self.assertTrue(
            info_result.success,
            f"Failed to get context info: {info_result.error_message}",
        )
        self.assertIsNotNone(info_result.request_id)
        self.assertIsNotNone(info_result.context_status_data)

        print(f"✅ Context info successful!")
        print(f"Info request ID: {info_result.request_id}")
        print(f"Context status data count: {len(info_result.context_status_data)}")

        # Log context status details
        if len(info_result.context_status_data) > 0:
            print("Context status details:")
            for index, status in enumerate(info_result.context_status_data):
                print(
                    f"  [{index}] ContextId: {status.context_id}, Path: {status.path}, Status: {status.status}, TaskType: {status.task_type}"
                )

        # List files in context sync directory
        print("Listing files in context sync directory...")

        # Use the sync directory path
        sync_dir_path = "/tmp/archive-mode-test"

        list_result = await self.agent_bay.context.list_files(
            context_result.context_id, sync_dir_path, page_number=1, page_size=10
        )

        # Verify ListFiles success
        self.assertTrue(
            list_result.success,
            f"Failed to list files: {getattr(list_result, 'error_message', 'Unknown error')}",
        )
        self.assertIsNotNone(list_result.request_id)
        self.assertNotEqual(list_result.request_id, "")

        print(f"✅ List files successful!")
        print(f"List files request ID: {list_result.request_id}")
        print(f"Total files found: {len(list_result.entries)}")

        if list_result.entries:
            print("📋 Files in context sync directory:")
            for index, entry in enumerate(list_result.entries):
                print(f"  [{index}] FilePath: {entry.file_path}")
                print(f"      FileType: {entry.file_type}")
                print(f"      FileName: {entry.file_name}")
                print(f"      Size: {entry.size} bytes")

            # Check if any file contains 'zip' in fileName (for Archive mode)
            has_zip_file = any(
                "zip" in entry.file_name.lower()
                for entry in list_result.entries
                if entry.file_name
            )
            if has_zip_file:
                print(
                    "✅ Found zip file in Archive mode - this indicates successful archive compression"
                )
            else:
                print("ℹ️  No zip file found - files may be stored individually")
        else:
            print("No files found in context sync directory")
        print(
            "✅ Archive mode contextSync with contextId and path works correctly, and file operations completed successfully"
        )

        # Cleanup
        print("Cleaning up: Deleting the session...")
        delete_result = await self.agent_bay.delete(session, sync_context=True)
        self.assertTrue(
            delete_result.success,
            f"Failed to delete session: {delete_result.error_message}",
        )
        print(f"Session {session.session_id} deleted successfully")
        self.test_sessions.remove(session)

    async def test_invalid_upload_mode_with_policy_assignment(self):
        """Test error handling when using invalid uploadMode with policy assignment."""
        print("\n=== Testing invalid uploadMode with policy assignment ===")

        context_name = f"invalid-policy-context-{self.__class__.unique_id}"
        context_result = await self.agent_bay.context.get(context_name, True)
        self.assertTrue(
            context_result.success,
            f"Failed to create context: {context_result.error_message}",
        )

        # Test 1: Invalid upload mode through SyncPolicy creation (new test for agentbay.create scenario)
        print(
            "Testing invalid uploadMode through SyncPolicy instantiation (agentbay.create scenario)..."
        )

        with self.assertRaises(ValueError) as exc_info:
            # This simulates what happens when user passes invalid uploadMode in agentbay.create
            invalid_upload_policy = UploadPolicy(upload_mode="InvalidMode")
            sync_policy = SyncPolicy(upload_policy=invalid_upload_policy)

        self.assertIn("Invalid upload_mode value: InvalidMode", str(exc_info.exception))
        self.assertIn("Valid values are: File, Archive", str(exc_info.exception))

        print(
            "✅ SyncPolicy correctly threw error for invalid uploadMode during instantiation"
        )

        # Test 2: Test the complete flow with ContextSync (most realistic scenario)
        print("Testing invalid uploadMode through complete ContextSync flow...")

        with self.assertRaises(ValueError) as exc_info:
            # This is the most realistic scenario - user creates ContextSync with invalid policy
            invalid_upload_policy = UploadPolicy(upload_mode="BadValue")
            sync_policy = SyncPolicy(upload_policy=invalid_upload_policy)

            # This would be used in agentbay.create(CreateSessionParams(context_syncs=[context_sync]))
            context_sync = ContextSync.new(
                context_id=context_result.context_id,
                path="/tmp/test-invalid",
                policy=sync_policy,
            )

        self.assertIn("Invalid upload_mode value: BadValue", str(exc_info.exception))
        self.assertIn("Valid values are: File, Archive", str(exc_info.exception))

        print(
            "✅ Complete ContextSync flow correctly threw error for invalid uploadMode"
        )

    async def test_valid_upload_mode_values(self):
        """Test that valid uploadMode values are accepted."""
        print("\n=== Testing valid uploadMode values ===")

        context_name = f"valid-context-{self.__class__.unique_id}"
        context_result = await self.agent_bay.context.get(context_name, True)
        self.assertTrue(
            context_result.success,
            f"Failed to create context: {context_result.error_message}",
        )

        # Test "File" mode
        file_upload_policy = UploadPolicy(upload_mode=UploadMode.FILE)
        file_sync_policy = SyncPolicy(upload_policy=file_upload_policy)

        # Should not raise any exception
        file_context_sync = ContextSync.new(
            context_id=context_result.context_id,
            path="/tmp/test-file",
            policy=file_sync_policy,
        )

        self.assertEqual(
            file_context_sync.policy.upload_policy.upload_mode, UploadMode.FILE
        )
        print("✅ 'File' uploadMode accepted successfully")

        # Test "Archive" mode
        archive_upload_policy = UploadPolicy(upload_mode=UploadMode.ARCHIVE)
        archive_sync_policy = SyncPolicy(upload_policy=archive_upload_policy)

        # Should not raise any exception
        archive_context_sync = ContextSync.new(
            context_id=context_result.context_id,
            path="/tmp/test-archive",
            policy=archive_sync_policy,
        )

        self.assertEqual(
            archive_context_sync.policy.upload_policy.upload_mode, UploadMode.ARCHIVE
        )
        print("✅ 'Archive' uploadMode accepted successfully")

    def test_upload_policy_serialization(self):
        """Test that UploadPolicy serializes uploadMode correctly."""
        print("\n=== Testing UploadPolicy serialization ===")

        # Test File mode serialization
        file_policy = UploadPolicy(upload_mode=UploadMode.FILE)
        file_dict = file_policy.__dict__()

        self.assertIn("uploadMode", file_dict)
        self.assertEqual(file_dict["uploadMode"], "File")
        print("✅ File mode serialization works correctly")

        # Test Archive mode serialization
        archive_policy = UploadPolicy(upload_mode=UploadMode.ARCHIVE)
        archive_dict = archive_policy.__dict__()

        self.assertIn("uploadMode", archive_dict)
        self.assertEqual(archive_dict["uploadMode"], "Archive")
        print("✅ Archive mode serialization works correctly")

        # Test default policy serialization
        default_policy = UploadPolicy.default()
        default_dict = default_policy.__dict__()

        self.assertIn("uploadMode", default_dict)
        self.assertEqual(default_dict["uploadMode"], "File")  # Default should be File
        print("✅ Default policy serialization works correctly")


if __name__ == "__main__":
    unittest.main()
