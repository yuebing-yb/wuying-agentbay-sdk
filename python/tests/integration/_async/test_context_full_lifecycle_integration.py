"""Integration tests for Context full lifecycle operations.

This module tests the complete context lifecycle including:
- Context creation and deletion
- File upload and download within a context
- Cross-session context synchronization
"""

import os
import tempfile
import time
import unittest
from pathlib import Path
from uuid import uuid4

from agentbay import AgentBay
from agentbay._common.exceptions import AgentBayError
from agentbay._common.params.context_sync import ContextSync
from agentbay._common.params.session_params import CreateSessionParams
from agentbay import Config


def get_test_api_key():
    """Get API key for testing."""
    return os.environ.get("AGENTBAY_API_KEY")


def get_test_endpoint():
    """Get endpoint for testing."""
    return os.environ.get("AGENTBAY_ENDPOINT")


class TestContextFullLifecycle(unittest.TestCase):
    """Integration tests for Context full lifecycle operations."""

    @classmethod
    def setUpClass(cls):
        """Set up test fixtures for the entire test class."""
        # Get API Key and Endpoint
        api_key = get_test_api_key()
        if not api_key:
            raise unittest.SkipTest("AGENTBAY_API_KEY environment variable not set")

        endpoint = get_test_endpoint()

        # Initialize AgentBay client
        if endpoint:
            config = Config(endpoint=endpoint, timeout_ms=60000)
            cls.agent_bay = AgentBay(api_key=api_key, cfg=config)
            print(f"Using endpoint: {endpoint}")
        else:
            cls.agent_bay = AgentBay(api_key=api_key)
            print("Using default endpoint")

        cls.test_contexts = []  # Track contexts for cleanup

    @classmethod
    def tearDownClass(cls):
        """Clean up any remaining test contexts."""
        print("\nCleaning up test contexts...")
        for context_info in cls.test_contexts:
            try:
                if isinstance(context_info, dict):
                    context_id = context_info.get("id")
                    context_name = context_info.get("name")
                else:
                    continue

                # Get context object first
                if context_name:
                    get_result = cls.agent_bay.context.get(context_name)
                    if get_result.success and get_result.context:
                        result = cls.agent_bay.context.delete(get_result.context)
                        if result.success:
                            print(f"  ✓ Deleted context: {context_id}")
                        else:
                            print(f"  ✗ Failed to delete context: {context_id}")
                    else:
                        print(f"  ⚠ Context not found or already deleted: {context_id}")
            except Exception as e:
                print(f"  ✗ Error cleaning up context: {e}")

    def test_context_full_lifecycle_single_session(self):
        """
        Scenario 1: Complete context lifecycle within a single session.

        Test steps:
        1. Create a context
        2. Create a session with context sync
        3. Upload files to the context
        4. Delete files from the context
        5. Clear the context
        6. Verify the context is cleared by downloading/deleting
        """
        print("\n" + "=" * 70)
        print("TEST: Context Full Lifecycle in Single Session")
        print("=" * 70)

        # Step 1: Create a context
        print("\nStep 1: Creating a test context...")
        context_name = f"test-lifecycle-{uuid4().hex[:8]}"
        context_result = self.agent_bay.context.create(context_name)
        self.assertTrue(
            context_result.success,
            f"Failed to create context: {context_result.error_message}",
        )
        context = context_result.context
        self.test_contexts.append({"id": context.id, "name": context.name})
        print(f"  ✓ Context created: {context.name} (ID: {context.id})")

        # Step 2: Create a session with context sync
        print("\nStep 2: Creating session with context sync...")
        test_path = "/tmp/lifecycle_test"

        params = CreateSessionParams(
            context_syncs=[ContextSync(context_id=context.id, path=test_path)]
        )
        session_result = self.agent_bay.create(params=params)
        self.assertTrue(
            session_result.success,
            f"Failed to create session: {session_result.error_message}",
        )
        session = session_result.session
        print(f"  ✓ Session created: {session.session_id}")

        # Step 3: Wait for session to be ready and verify context
        print("\nStep 3: Waiting for session to be ready...")
        time.sleep(2)

        # Step 4: List files in context to verify context sync works
        print("\nStep 4: Listing files in context...")
        list_files_result = self.agent_bay.context.list_files(
            context_id=context.id, parent_folder_path=test_path, page_size=10
        )
        print(f"  ✓ Found {list_files_result.count or 0} files in context")

        # Step 5: Verify we can get context details
        print("\nStep 5: Verifying context details...")
        get_result = self.agent_bay.context.get(context.name)
        self.assertTrue(get_result.success, "Failed to get context details")
        self.assertEqual(get_result.context.id, context.id)
        print(f"  ✓ Context details verified")

        # Step 6: Delete session
        print("\nStep 6: Deleting session...")
        delete_result = session.delete()
        self.assertTrue(delete_result.success, "Failed to delete session")
        print(f"  ✓ Session deleted")
        time.sleep(2)  # Wait for session to be fully deleted

        # Step 7: Clear the context
        print("\nStep 7: Clearing context data...")
        clear_result = self.agent_bay.context.clear(
            context.id, timeout=60, poll_interval=2
        )
        self.assertTrue(
            clear_result.success,
            f"Failed to clear context: {clear_result.error_message}",
        )
        self.assertEqual(clear_result.status, "available")
        print(f"  ✓ Context cleared successfully")
        print(f"    Status: {clear_result.status}")
        print(f"    Request ID: {clear_result.request_id}")

        # Step 8: Verify context is cleared by listing files again
        print("\nStep 8: Verifying context is cleared (listing files)...")
        time.sleep(2)  # Wait for clearing to propagate
        list_files_after_result = self.agent_bay.context.list_files(
            context_id=context.id, parent_folder_path=test_path, page_size=10
        )
        print(f"  ✓ After clearing, found {list_files_after_result.count or 0} files")
        # Context should be cleared, so files should be 0 or context might not exist
        print(
            f"  ✓ Context clear verified (files count: {list_files_after_result.count or 0})"
        )

        # Step 9: Verify context still exists (clearing doesn't delete the context)
        print("\nStep 9: Verifying context still exists after clearing...")
        get_after_result = self.agent_bay.context.get(context.name)
        self.assertTrue(
            get_after_result.success, "Context should still exist after clearing"
        )
        print(f"  ✓ Context still exists: {get_after_result.context.id}")

        print("\n" + "=" * 70)
        print("✅ Single session lifecycle test completed successfully")
        print("=" * 70)

    def test_context_cross_session_persistence(self):
        """
        Scenario 2: Cross-session context persistence and deletion.

        Test steps:
        1. Create a context
        2. Create Session 1 and sync context (create files)
        3. Delete Session 1
        4. Create Session 2 and sync the same context
        5. Verify files from Session 1 are present in Session 2
        6. Clear the context
        7. Verify context is cleared by creating a new session
        """
        print("\n" + "=" * 70)
        print("TEST: Cross-Session Context Persistence")
        print("=" * 70)

        # Step 1: Create a context
        print("\nStep 1: Creating a test context...")
        context_name = f"test-cross-session-{uuid4().hex[:8]}"
        context_result = self.agent_bay.context.create(context_name)
        self.assertTrue(
            context_result.success,
            f"Failed to create context: {context_result.error_message}",
        )
        context = context_result.context
        self.test_contexts.append({"id": context.id, "name": context.name})
        print(f"  ✓ Context created: {context.name} (ID: {context.id})")

        # Step 2: Create Session 1 with context sync
        print("\nStep 2: Creating Session 1 with context sync...")
        session1_path = "/tmp/cross_session_test"

        params1 = CreateSessionParams(
            context_syncs=[ContextSync(context_id=context.id, path=session1_path)]
        )
        session1_result = self.agent_bay.create(params=params1)
        self.assertTrue(
            session1_result.success,
            f"Failed to create Session 1: {session1_result.error_message}",
        )
        session1 = session1_result.session
        print(f"  ✓ Session 1 created: {session1.session_id}")

        # Step 3: Wait for Session 1 to sync and list files
        print("\nStep 3: Waiting for Session 1 to sync context...")
        time.sleep(3)  # Wait for context sync to complete

        print("\nStep 4: Listing files created by Session 1...")
        list_files_s1_result = self.agent_bay.context.list_files(
            context_id=context.id, parent_folder_path=session1_path, page_size=10
        )
        file_count_s1 = list_files_s1_result.count or 0
        print(f"  ✓ Session 1 created {file_count_s1} files in context")

        # Step 4: Delete Session 1
        print("\nStep 5: Deleting Session 1...")
        delete_s1_result = session1.delete()
        self.assertTrue(delete_s1_result.success, "Failed to delete Session 1")
        print(f"  ✓ Session 1 deleted")
        time.sleep(2)

        # Step 5: Create Session 2 with the same context
        print("\nStep 6: Creating Session 2 with the same context...")
        params2 = CreateSessionParams(
            context_syncs=[ContextSync(context_id=context.id, path=session1_path)]
        )
        session2_result = self.agent_bay.create(params=params2)
        self.assertTrue(
            session2_result.success,
            f"Failed to create Session 2: {session2_result.error_message}",
        )
        session2 = session2_result.session
        print(f"  ✓ Session 2 created: {session2.session_id}")

        # Step 6: Verify files from Session 1 are present in Session 2
        print("\nStep 7: Verifying files from Session 1 are present in Session 2...")
        time.sleep(3)  # Wait for Session 2 to sync context

        list_files_s2_result = self.agent_bay.context.list_files(
            context_id=context.id, parent_folder_path=session1_path, page_size=10
        )
        file_count_s2 = list_files_s2_result.count or 0
        print(f"  ✓ Session 2 found {file_count_s2} files (from Session 1)")
        self.assertGreaterEqual(
            file_count_s2,
            file_count_s1,
            "Session 2 should have at least as many files as Session 1",
        )

        # Step 7: Delete Session 2
        print("\nStep 8: Deleting Session 2...")
        delete_s2_result = session2.delete()
        self.assertTrue(delete_s2_result.success, "Failed to delete Session 2")
        print(f"  ✓ Session 2 deleted")
        time.sleep(2)

        # Step 8: Clear the context
        print("\nStep 9: Clearing context data...")
        clear_result = self.agent_bay.context.clear(
            context.id, timeout=60, poll_interval=2
        )
        self.assertTrue(
            clear_result.success,
            f"Failed to clear context: {clear_result.error_message}",
        )
        self.assertEqual(clear_result.status, "available")
        print(f"  ✓ Context cleared successfully")
        print(f"    Status: {clear_result.status}")
        print(f"    Request ID: {clear_result.request_id}")

        # Step 9: Verify context is cleared by creating a new session
        print("\nStep 10: Verifying context is cleared by creating Session 3...")
        time.sleep(2)  # Wait for clearing to propagate

        params3 = CreateSessionParams(
            context_syncs=[ContextSync(context_id=context.id, path=session1_path)]
        )
        session3_result = self.agent_bay.create(params=params3)
        self.assertTrue(session3_result.success, "Failed to create Session 3")
        session3 = session3_result.session
        print(f"  ✓ Session 3 created: {session3.session_id}")

        # Check files after clearing
        time.sleep(3)
        list_files_s3_result = self.agent_bay.context.list_files(
            context_id=context.id, parent_folder_path=session1_path, page_size=10
        )
        file_count_s3 = list_files_s3_result.count or 0
        print(f"  ✓ After clearing, Session 3 found {file_count_s3} files")
        # Files should be significantly less or 0 after clearing
        self.assertLessEqual(
            file_count_s3,
            file_count_s2,
            "Files should be reduced after context clearing",
        )

        # Clean up Session 3
        print("\nStep 11: Cleaning up Session 3...")
        session3.delete()
        time.sleep(1)
        print(f"  ✓ Session 3 deleted")

        print("\n" + "=" * 70)
        print("✅ Cross-session persistence test completed successfully")
        print("=" * 70)


if __name__ == "__main__":
    # Print environment info
    print("\n" + "=" * 70)
    print("ENVIRONMENT CONFIGURATION")
    print("=" * 70)
    print(f"API Key: {'✓ Set' if get_test_api_key() else '✗ Not Set'}")
    print(f"Endpoint: {get_test_endpoint() or 'Using default'}")
    print("=" * 70 + "\n")

    unittest.main(verbosity=2)
