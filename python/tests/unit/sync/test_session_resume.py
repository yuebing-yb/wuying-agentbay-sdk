import time
"""Unit tests for Session resume operations."""

import unittest
from unittest.mock import MagicMock, MagicMock, patch

from agentbay import AgentBay
from agentbay import Session
from agentbay import (
    GetSessionData,
    GetSessionResult,
    SessionResumeResult,
)
from agentbay.api.models import (
    ResumeSessionAsyncResponse,
    ResumeSessionAsyncResponseBody,
)


class TestSessionResume(unittest.TestCase):
    """Test suite for Session resume operations."""

    def setUp(self):
        """Set up test fixtures."""
        self.agent_bay = AgentBay("test-api-key")
        self.agent_bay.client = MagicMock()

        # Create a mock session
        self.session = Session(self.agent_bay, "session-123")
        self.session.is_vpc = False
        self.session.network_interface_ip = ""
        self.session.http_port = ""
        self.session.token = ""
        self.session.resource_url = ""

    def test_resume_success_immediate(self):
        """Test successful beta session resume with immediate success."""
        # Mock the ResumeSessionAsync response
        mock_response = ResumeSessionAsyncResponse()
        mock_response.body = ResumeSessionAsyncResponseBody(
            success=True,
            code="Success",
            message="Session resume initiated successfully",
            request_id="test-request-id",
            http_status_code=200,
        )
        self.agent_bay.client.resume_session_async = MagicMock(
            return_value=mock_response
        )

        # Mock _get_session to return RUNNING immediately
        get_session_running = GetSessionResult(
            request_id="test-request-id",
            success=True,
            data=GetSessionData(
                session_id="session-123",
                status="RUNNING",
            ),
        )
        self.agent_bay._get_session = MagicMock(return_value=get_session_running)

        # Patch time.sleep to avoid waiting
        with patch("time.sleep", new_callable=MagicMock) as mock_sleep:
            # Call the method (beta_resume not beta_resume_async for polling)
            result = self.session.beta_resume(timeout=10, poll_interval=1)

            # Verify the result
            self.assertIsInstance(result, SessionResumeResult)
            self.assertTrue(result.success)
            self.assertEqual(result.request_id, "test-request-id")
            self.assertEqual(result.status, "RUNNING")
            self.assertEqual(result.error_message, "")

            # Verify that sleep was not called since we got RUNNING directly.
            mock_sleep.assert_not_called()

    def test_resume_success_after_polling(self):
        """Test successful beta session resume after polling."""
        # Mock the ResumeSessionAsync response
        mock_response = ResumeSessionAsyncResponse()
        mock_response.body = ResumeSessionAsyncResponseBody(
            success=True,
            code="Success",
            message="Session resume initiated successfully",
            request_id="test-request-id",
            http_status_code=200,
        )
        self.agent_bay.client.resume_session_async = MagicMock(
            return_value=mock_response
        )

        # Mock _get_session to return RESUMING first, then RUNNING
        get_session_resuming = GetSessionResult(
            request_id="test-request-id",
            success=True,
            data=GetSessionData(
                session_id="session-123",
                status="RESUMING",
            ),
        )

        get_session_running = GetSessionResult(
            request_id="test-request-id",
            success=True,
            data=GetSessionData(
                session_id="session-123",
                status="RUNNING",
            ),
        )
        self.agent_bay._get_session = MagicMock(
            side_effect=[get_session_resuming, get_session_running]
        )

        # Patch time.sleep to avoid waiting
        with patch("time.sleep", new_callable=MagicMock) as mock_sleep:
            # Call the method
            result = self.session.beta_resume(timeout=10, poll_interval=1)

            # Verify the result
            self.assertIsInstance(result, SessionResumeResult)
            self.assertTrue(result.success)
            self.assertEqual(result.request_id, "test-request-id")
            self.assertEqual(result.status, "RUNNING")
            self.assertEqual(result.error_message, "")

            # Verify that sleep was called once (after the first attempt)
            mock_sleep.assert_called_once_with(1)

    def test_resume_timeout(self):
        """Test beta session resume timeout."""
        # Mock the ResumeSessionAsync response
        mock_response = ResumeSessionAsyncResponse()
        mock_response.body = ResumeSessionAsyncResponseBody(
            success=True,
            code="Success",
            message="Session resume initiated successfully",
            request_id="test-request-id",
            http_status_code=200,
        )
        self.agent_bay.client.resume_session_async = MagicMock(
            return_value=mock_response
        )

        # Mock _get_session to always return RESUMING
        get_session_resuming = GetSessionResult(
            request_id="test-request-id",
            success=True,
            data=GetSessionData(
                session_id="session-123",
                status="RESUMING",
            ),
        )
        self.agent_bay._get_session = MagicMock(return_value=get_session_resuming)

        # Patch time.sleep to avoid waiting
        with patch("time.sleep", new_callable=MagicMock) as mock_sleep:
            # Call the method with a short timeout
            result = self.session.beta_resume(timeout=2, poll_interval=1)

            # Verify the result
            # The implementation now returns failure on timeout
            self.assertIsInstance(result, SessionResumeResult)
            self.assertFalse(result.success)
            self.assertIn("Timed out", result.error_message)
            self.assertEqual(result.request_id, "test-request-id")

    def test_resume_get_session_failure(self):
        """Test beta session resume when _get_session fails."""
        # Mock the ResumeSessionAsync response
        mock_response = ResumeSessionAsyncResponse()
        mock_response.body = ResumeSessionAsyncResponseBody(
            success=True,
            code="Success",
            message="Session resume initiated successfully",
            request_id="test-request-id",
            http_status_code=200,
        )
        self.agent_bay.client.resume_session_async = MagicMock(
            return_value=mock_response
        )

        # Mock _get_session to return failure
        get_session_failure = GetSessionResult(
            request_id="test-request-id",
            success=False,
            error_message="Failed to get session status",
        )
        self.agent_bay._get_session = MagicMock(return_value=get_session_failure)

        # Patch time.sleep to avoid waiting
        with patch("time.sleep", new_callable=MagicMock) as mock_sleep:
            # Call the method
            result = self.session.beta_resume(timeout=2, poll_interval=1)

            # Verify the result
            self.assertIsInstance(result, SessionResumeResult)
            self.assertFalse(result.success)
            self.assertIn("Timed out", result.error_message)
            self.assertEqual(result.request_id, "test-request-id")

    def test_resume_api_error(self):
        """Test beta session resume with API error."""
        # Mock the ResumeSessionAsync response with error
        mock_response = ResumeSessionAsyncResponse()
        mock_response.body = ResumeSessionAsyncResponseBody(
            success=False,
            code="SessionNotFound",
            message="Session does not exist",
            request_id="test-request-id",
            http_status_code=404,
        )
        self.agent_bay.client.resume_session_async = MagicMock(
            return_value=mock_response
        )

        # Patch time.sleep to avoid waiting
        with patch("time.sleep", new_callable=MagicMock) as mock_sleep:
            # Call the method
            result = self.session.beta_resume()

            # Verify the result
            self.assertIsInstance(result, SessionResumeResult)
            self.assertFalse(result.success)
            self.assertEqual(result.request_id, "test-request-id")
            self.assertEqual(
                result.error_message, "[SessionNotFound] Session does not exist"
            )

    def test_resume_empty_response_body(self):
        """Test beta session resume with empty response body."""
        # Mock the ResumeSessionAsync response with no body
        mock_response = ResumeSessionAsyncResponse(status_code=200)
        mock_response.body = None
        self.agent_bay.client.resume_session_async = MagicMock(
            return_value=mock_response
        )

        # Patch time.sleep to avoid waiting
        with patch("time.sleep", new_callable=MagicMock) as mock_sleep:
            # Call the method
            result = self.session.beta_resume()

            # Verify the result
            self.assertIsInstance(result, SessionResumeResult)
            self.assertFalse(result.success)
            self.assertEqual(result.error_message, "Invalid response body")
            self.assertEqual(result.request_id, "")

    def test_resume_invalid_response_format(self):
        """Test beta session resume with invalid response format."""
        # Mock the ResumeSessionAsync response with invalid format
        mock_response = MagicMock()
        mock_response.to_map.return_value = None
        self.agent_bay.client.resume_session_async = MagicMock(
            return_value=mock_response
        )

        # Patch time.sleep to avoid waiting
        with patch("time.sleep", new_callable=MagicMock) as mock_sleep:
            # Call the method
            result = self.session.beta_resume()

            # Verify the result
            self.assertIsInstance(result, SessionResumeResult)
            self.assertFalse(result.success)
            self.assertEqual(result.error_message, "Invalid response format")
            self.assertEqual(result.request_id, "")

    def test_resume_client_exception(self):
        """Test beta session resume with client exception."""
        # Mock the client to raise an exception
        self.agent_bay.client.resume_session_async.side_effect = Exception(
            "Network error"
        )

        # Patch time.sleep to avoid waiting
        with patch("time.sleep", new_callable=MagicMock) as mock_sleep:
            # Call the method
            result = self.session.beta_resume()

            # Verify the result
            self.assertIsInstance(result, SessionResumeResult)
            self.assertFalse(result.success)
            self.assertIn("Network error", result.error_message)
            self.assertEqual(result.request_id, "")

    def test_resume_unexpected_state(self):
        """Test beta session resume with unexpected state."""
        # Mock the ResumeSessionAsync response
        mock_response = ResumeSessionAsyncResponse()
        mock_response.body = ResumeSessionAsyncResponseBody(
            success=True,
            code="Success",
            message="Session resume initiated successfully",
            request_id="test-request-id",
            http_status_code=200,
        )
        self.agent_bay.client.resume_session_async = MagicMock(
            return_value=mock_response
        )

        # Mock _get_session to return unexpected state, then RUNNING
        get_session_paused = GetSessionResult(
            request_id="test-request-id",
            success=True,
            data=GetSessionData(
                session_id="session-123",
                status="other",
            ),
        )

        get_session_running = GetSessionResult(
            request_id="test-request-id",
            success=True,
            data=GetSessionData(
                session_id="session-123",
                status="RUNNING",
            ),
        )
        self.agent_bay._get_session = MagicMock(
            side_effect=[get_session_paused, get_session_running]
        )

        # Patch time.sleep to avoid waiting
        with patch("time.sleep", new_callable=MagicMock) as mock_sleep:
            # Call the method
            result = self.session.beta_resume(timeout=10, poll_interval=1)

            # Verify the result
            self.assertIsInstance(result, SessionResumeResult)
            self.assertTrue(result.success)
            self.assertEqual(result.request_id, "test-request-id")
            self.assertEqual(result.status, "RUNNING")
            self.assertEqual(result.error_message, "")

            # Verify that sleep was called once (after the first attempt)
            mock_sleep.assert_called_once_with(1)


if __name__ == "__main__":
    unittest.main()
