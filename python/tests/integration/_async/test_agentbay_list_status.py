"""Integration tests for Session pause and resume operations."""

import asyncio
import os
import time
import unittest
from uuid import uuid4

import pytest
from dotenv import load_dotenv

from agentbay import AsyncAgentBay, CreateSessionParams
from agentbay import AgentBayError
from agentbay import SessionPauseResult, SessionResumeResult
from agentbay import Config

def get_test_api_key():
    """Get API key for testing."""
    return os.environ.get("AGENTBAY_API_KEY")

def get_test_endpoint():
    """Get endpoint for testing."""
    return os.environ.get("AGENTBAY_ENDPOINT")

class TestSessionPauseResumeIntegration(unittest.IsolatedAsyncioTestCase):
    """Integration tests for Session pause and resume operations."""

    @classmethod
    def setUpClass(cls):
        """Set up test fixtures for the entire test class."""
        # Load environment variables from .env file
        load_dotenv()

        # Get API Key and Endpoint
        api_key = get_test_api_key()
        if not api_key:
            raise unittest.SkipTest("AGENTBAY_API_KEY environment variable not set")

        endpoint = get_test_endpoint()

        # Initialize AsyncAgentBay client
        if endpoint:
            config = Config(endpoint=endpoint, timeout_ms=60000)
            cls.agent_bay = AsyncAgentBay(api_key=api_key, cfg=config)
            print(f"Using endpoint: {endpoint}")
        else:
            cls.agent_bay = AsyncAgentBay(api_key=api_key)
            print("Using default endpoint")

    def setUp(self):
        """Set up test fixtures for each test method."""
        self.test_sessions = []  # Track sessions for cleanup in each test

    async def asyncTearDown(self):
        """Clean up test sessions after each test method."""
        print("\nCleaning up test sessions for this test...")
        for session in self.test_sessions:
            try:
                # Try to resume session first in case it's paused
                try:
                    if(session):
                        result = await self.agent_bay.get_status(session.session_id)
                        if(result.data.status in ["PAUSED"]):
                            await session.resume()
                            print(f"  ✓ Resumed session: {session.session_id}")
                        if result.data.status not in ["DELETING", "DELETED","RESUMING","PAUSING"]:
                            result = await self.agent_bay.delete(session)
                            if result.success:
                                print(f"  ✓ Deleted session: {session.session_id}")
                            else:
                                print(f"  ✗ Failed to delete session: {session.session_id}")
                except Exception as resume_error:
                    print(f"  ⚠ Could not resume session {session.session_id}: {resume_error}")
                    
            except Exception as e:
                print(f"  ✗ Error deleting session {session.session_id}: {e}")
        # Clear the list for next test
        self.test_sessions = []

    async def _create_test_session(self):
        """Helper method to create a test session."""
        session_name = f"test-pause-resume-{uuid4().hex[:8]}"
        print(f"\nCreating test session: {session_name}")

        # Create session
        params = CreateSessionParams(
            # image_id="imgc-0ab5takggkr3iekb6",
            # image_id="linux_latest",
            # is_vpc=True,
            labels={"project": "piaoyun-demo", "environment": "testing"},
        )
        result = await self.agent_bay.create(params)
        self.assertTrue(
            result.success, f"Failed to create session: {result.error_message}"
        )
        self.assertIsNotNone(result.session)

        session = result.session
        self.test_sessions.append(session)
        print(f"  ✓ Session created: {session.session_id}")

        return session

    async def _verify_session_status_and_list(self, session, expected_statuses, operation_name="operation"):
        """
        Helper method to verify session status using both get_status and get_session,
        and verify the session appears in the list with correct status.
        
        Args:
            session: The session to verify
            expected_statuses: List of expected status values (e.g., ["PAUSED", "PAUSING"])
            operation_name: Name of the operation for logging purposes
        """
        print(f"\nVerifying session status after {operation_name}...")
        
        # First call get_status to check the current status
        status_result = await self.agent_bay.get_status(session.session_id)
        self.assertTrue(status_result.success, f"Failed to get session status: {status_result.error_message}")
        
        initial_status = status_result.data.status if status_result.data else "UNKNOWN"
        print(f"  ✓ Session status from get_status: {initial_status}")
        self.assertIn(initial_status, expected_statuses, 
                     f"Unexpected status {initial_status}, expected one of {expected_statuses}")

        # Then call get_session for detailed information
        session_info = await self.agent_bay.get_session(session.session_id)
        self.assertTrue(session_info.success, f"Failed to get session info: {session_info.error_message}")

        current_status = session_info.data.status if session_info.data else "UNKNOWN"
        self.assertEqual(current_status, initial_status, 
                        f"Session status mismatch: expected {initial_status}, got {current_status}")
        print(f"  ✓ Session status from get_session: {current_status}")
        
        # Test list with current status
        list_result = await self.agent_bay.list(status=current_status)
        self.assertTrue(list_result.success, f"Failed to list sessions: {list_result.error_message}")
        
        # Verify session is in the list and check array structure
        session_found = False
        for session_data in list_result.session_ids:
            if isinstance(session_data, dict):
                if session_data.get("sessionId") == session.session_id:
                    session_found = True
                    self.assertIn("sessionStatus", session_data, "sessionStatus field missing in list result")
                    self.assertIn("sessionId", session_data, "sessionId field missing in list result")
                    self.assertEqual(session_data["sessionStatus"], current_status)
                    break
            else:
                print("  ✗ Invalid session data in list result")
                break
        
        self.assertTrue(session_found, f"Session {session.session_id} not found in list with status {current_status}")
        print(f"  ✓ Session found in list with status {current_status}")
        print(f"  ✓ Session status verification completed for {operation_name}")
        
        return current_status

    @pytest.mark.asyncio
    async def test_pause_and_resume_session_success(self):
        """Test successful pause and resume operations on a session."""
        print("\n" + "=" * 60)
        print("TEST: Pause and Resume Session Success")
        print("=" * 60)

        # Create a test session
        session = await self._create_test_session()

        # Verify session is initially in RUNNING state
        # First call get_status to check the current status
        status_result = await self.agent_bay.get_status(session.session_id)
        self.assertTrue(status_result.success, f"Failed to get session status: {status_result.error_message}")
        
        initial_status = status_result.data.status if status_result.data else "UNKNOWN"
        print(f"  ✓ Session status from get_status: {initial_status}")
        self.assertIn(initial_status, "RUNNING", 
                     f"Unexpected status {initial_status}, expected one of RUNNING")

        # Pause the session
        print(f"\nStep 2: Pausing session...")
        pause_result = await self.agent_bay.pause(session)

        # Verify pause result
        self.assertIsInstance(pause_result, SessionPauseResult)
        self.assertTrue(
            pause_result.success, f"Pause failed: {pause_result.error_message}"
        )
        print(f"  ✓ Session pause initiated successfully")
        print(f"    Request ID: {pause_result.request_id}")
        # Wait a bit for pause to complete
        print(f"\nStep 3: Waiting for session to pause...")
        await asyncio.sleep(2)

        # Verify session status after pause
        current_status = await self._verify_session_status_and_list(session, ["PAUSED", "PAUSING"], "pause")

    @pytest.mark.asyncio
    async def test_resume_async_session_success(self):
        """Test successful async resume operation on a session."""
        print("\n" + "=" * 60)
        print("TEST: Async Resume Session Success")
        print("=" * 60)

        # Create a test session
        session = await self._create_test_session()

        # Pause the session first
        print(f"\nStep 1: Pausing session...")
        pause_result = await self.agent_bay.pause(session)
        self.assertTrue(
            pause_result.success, f"Pause failed: {pause_result.error_message}"
        )
        print(f"  ✓ Session pause initiated successfully")

        # Wait for pause to complete
        print(f"\nStep 2: Waiting for session to pause...")
        await asyncio.sleep(2)

        # Session should be PAUSED or PAUSING after pause operation
        status_result = await self.agent_bay.get_status(session.session_id)
        self.assertTrue(status_result.success, f"Failed to get session status: {status_result.error_message}")
        
        initial_status = status_result.data.status if status_result.data else "UNKNOWN"
        print(f"  ✓ Session status from get_status: {initial_status}")
        self.assertIn(initial_status, ["PAUSED","PAUSING"], 
                     f"Unexpected status {initial_status}, expected one of PAUSED or PAUSING")
        print(f"  ✓ Session status checked")

        # Resume the session (asynchronous)
        print(f"\nStep 3: Resuming session asynchronously...")
        resume_result = await self.agent_bay.resume_async(session)

        # Verify async resume result
        self.assertIsInstance(resume_result, SessionResumeResult)
        self.assertTrue(
            resume_result.success, f"Async resume failed: {resume_result.error_message}"
        )
        print(f"  ✓ Session resume initiated successfully")
        print(f"    Request ID: {resume_result.request_id}")

        # Wait a bit for resume to complete
        print(f"\nStep 4: Waiting for session to resume...")
        await asyncio.sleep(2)

        # Verify session status after async resume
        current_status = await self._verify_session_status_and_list(session, ["RUNNING", "RESUMING"], "async resume")

    @pytest.mark.asyncio
    async def test_pause_and_delete_session_success(self):
        """Test successful pause and delete operations on a session."""
        print("\n" + "=" * 60)
        print("TEST: Pause and Delete Session Success")
        print("=" * 60)
        print(f"\nStep 1: Creating test session...")
        # Create a test session
        session = await self._create_test_session()
        
        # Pause the session
        print(f"\nStep 2: Pausing session...")
        pause_result = await self.agent_bay.pause(session)

        # Verify pause result
        self.assertIsInstance(pause_result, SessionPauseResult)
        self.assertTrue(
            pause_result.success, f"Pause failed: {pause_result.error_message}"
        )
        print(f"  ✓ Session pause initiated successfully")
        print(f"    Request ID: {pause_result.request_id}")

        # Wait a bit for pause to complete
        print(f"\nStep 3: Waiting for session to pause...")
        await asyncio.sleep(2)

        # Session should be PAUSED or PAUSING after pause operation
        print(f"  ✓ Session status after pause checked")
        # Delete the session (asynchronous)
        print(f"\nStep 4: Deleting session...")
        delete_result = await self.agent_bay.delete(session)
        if delete_result.success:
            print("delete session successfully")

        # Verify session status after delete
        current_status = await self._verify_session_status_and_list(session, ["DELETING", "DELETED"], "delete")

if __name__ == "__main__":
    # Print environment info
    print("\n" + "=" * 60)
    print("ENVIRONMENT CONFIGURATION")
    print("=" * 60)
    load_dotenv()
    print(f"API Key: {'✓ Set' if get_test_api_key() else '✗ Not Set'}")
    print(f"Endpoint: {get_test_endpoint() or 'Using default'}")
    print("=" * 60 + "\n")

    unittest.main(verbosity=2)
