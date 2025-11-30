"""Unit tests for Context clear operations."""

import time
import unittest
from unittest.mock import AsyncMock, MagicMock, patch

from agentbay._common.exceptions import AgentBayError, ClearanceTimeoutError
from agentbay._async.context import ClearContextResult, ContextService
from agentbay.api.models import (
    ClearContextResponse,
    ClearContextResponseBody,
    GetContextResponse,
    GetContextResponseBody,
)
from agentbay.api.models._get_context_response_body import GetContextResponseBodyData


class TestAsyncContextClear(unittest.IsolatedAsyncioTestCase):
    """Test suite for Context clear operations."""

    async def setUp(self):
        """Set up test fixtures."""
        self.agent_bay = MagicMock()
        self.agent_bay.api_key = "test-api-key"
        self.agent_bay.client = MagicMock()
        self.context_service = ContextService(self.agent_bay)

    async def test_clear_async_success(self):
        """Test successful async clear initiation."""
        # Mock the ClearContext response
        mock_response = ClearContextResponse()
        mock_response.body = ClearContextResponseBody(
            success=True,
            code=None,
            message=None,
            request_id="test-request-id",
        )
        self.agent_bay.client.clear_context.return_value = mock_response

        # Call the method
        result = self.context_service.clear_async("context-123")

        # Verify the result
        self.assertTrue(result.success)
        self.assertEqual(result.context_id, "context-123")
        self.assertEqual(result.status, "clearing")
        self.assertEqual(result.error_message, "")
        self.assertEqual(result.request_id, "test-request-id")

    async def test_clear_async_api_error(self):
        """Test async clear with API error."""
        # Mock the ClearContext response with error
        mock_response = ClearContextResponse()
        mock_response.body = ClearContextResponseBody(
            success=False,
            code="InvalidContext",
            message="Context not found",
            request_id="test-request-id",
        )
        self.agent_bay.client.clear_context.return_value = mock_response

        # Call the method
        result = self.context_service.clear_async("invalid-context")

        # Verify the result
        self.assertFalse(result.success)
        self.assertIn("InvalidContext", result.error_message)
        self.assertIn("Context not found", result.error_message)

    async def test_clear_async_empty_body(self):
        """Test async clear with empty response body."""
        # Mock the ClearContext response with no body
        mock_response = ClearContextResponse()
        mock_response.body = None
        self.agent_bay.client.clear_context.return_value = mock_response

        # Call the method
        result = self.context_service.clear_async("context-123")

        # Verify the result
        self.assertFalse(result.success)
        self.assertEqual(result.error_message, "Empty response body")

    async def test_clear_async_exception(self):
        """Test async clear with exception."""
        # Mock the client to raise an exception
        self.agent_bay.client.clear_context.side_effect = Exception("Network error")

        # Call the method and expect AgentBayError
        with self.assertRaises(AgentBayError) as context:
            self.context_service.clear_async("context-123")

        self.assertIn("Network error", str(context.exception))

    async def test_get_clear_status_clearing(self):
        """Test get clear status when clearing is in progress."""
        # Mock the GetContext response
        mock_response = GetContextResponse()
        mock_response.body = GetContextResponseBody(
            success=True,
            code=None,
            message=None,
            request_id="test-request-id",
            data=GetContextResponseBodyData(
                id="context-123",
                name="test-context",
                state="clearing",
            ),
        )
        self.agent_bay.client.get_context.return_value = mock_response

        # Call the method with context_id
        result = self.context_service.get_clear_status("context-123")

        # Verify the result
        self.assertTrue(result.success)
        self.assertEqual(result.context_id, "context-123")
        self.assertEqual(result.status, "clearing")

    async def test_get_clear_status_available(self):
        """Test get clear status when clearing is completed."""
        # Mock the GetContext response
        mock_response = GetContextResponse()
        mock_response.body = GetContextResponseBody(
            success=True,
            code=None,
            message=None,
            request_id="test-request-id",
            data=GetContextResponseBodyData(
                id="context-123",
                name="test-context",
                state="available",
            ),
        )
        self.agent_bay.client.get_context.return_value = mock_response

        # Call the method with context_id
        result = self.context_service.get_clear_status("context-123")

        # Verify the result
        self.assertTrue(result.success)
        self.assertEqual(result.context_id, "context-123")
        self.assertEqual(result.status, "available")

    async def test_get_clear_status_api_error(self):
        """Test get clear status with API error."""
        # Mock the GetContext response with error
        mock_response = GetContextResponse()
        mock_response.body = GetContextResponseBody(
            success=False,
            code="ContextNotFound",
            message="Context does not exist",
            request_id="test-request-id",
            data=None,
        )
        self.agent_bay.client.get_context.return_value = mock_response

        # Call the method with context_id
        result = self.context_service.get_clear_status("context-123")

        # Verify the result
        self.assertFalse(result.success)
        self.assertIn("ContextNotFound", result.error_message)

    async def test_get_clear_status_empty_body(self):
        """Test get clear status with empty response body."""
        # Mock the GetContext response with no body
        mock_response = GetContextResponse()
        mock_response.body = None
        self.agent_bay.client.get_context.return_value = mock_response

        # Call the method with context_id
        result = self.context_service.get_clear_status("context-123")

        # Verify the result
        self.assertFalse(result.success)
        self.assertEqual(result.error_message, "Empty response body")

    async def test_get_clear_status_no_data(self):
        """Test get clear status with no data in response."""
        # Mock the GetContext response with no data
        mock_response = GetContextResponse()
        mock_response.body = GetContextResponseBody(
            success=True,
            code=None,
            message=None,
            request_id="test-request-id",
            data=None,
        )
        self.agent_bay.client.get_context.return_value = mock_response

        # Call the method with context_id
        result = self.context_service.get_clear_status("context-123")

        # Verify the result
        self.assertFalse(result.success)
        self.assertEqual(result.error_message, "No data in response")

    @patch("time.sleep")  # Mock sleep to speed up the test
    async def test_clear_sync_success(self, mock_sleep):
        """Test successful synchronous clear operation."""
        # Mock clear_async
        clear_async_result = ClearContextResult(
            request_id="test-request-id",
            success=True,
            context_id="context-123",
            status="clearing",
            error_message="",
        )

        # Mock _get_clear_status to return clearing, then available
        status_clearing = ClearContextResult(
            request_id="test-request-id",
            success=True,
            context_id="context-123",
            status="clearing",
            error_message="",
        )
        status_available = ClearContextResult(
            request_id="test-request-id",
            success=True,
            context_id="context-123",
            status="available",
            error_message="",
        )

        with patch.object(
            self.context_service, "clear_async", return_value=clear_async_result
        ), patch.object(
            self.context_service,
            "get_clear_status",
            side_effect=[status_clearing, status_available],
        ):
            # Call the method
            result = self.context_service.clear(
                "context-123", timeout=10, poll_interval=1
            )

            # Verify the result
            self.assertTrue(result.success)
            self.assertEqual(result.context_id, "context-123")
            self.assertEqual(result.status, "available")
            self.assertEqual(mock_sleep.call_count, 2)

    @patch("time.sleep")
    async def test_clear_sync_timeout(self, mock_sleep):
        """Test synchronous clear operation timeout."""
        # Mock clear_async
        clear_async_result = ClearContextResult(
            request_id="test-request-id",
            success=True,
            context_id="context-123",
            status="clearing",
            error_message="",
        )

        # Mock _get_clear_status to always return clearing
        status_clearing = ClearContextResult(
            request_id="test-request-id",
            success=True,
            context_id="context-123",
            status="clearing",
            error_message="",
        )

        with patch.object(
            self.context_service, "clear_async", return_value=clear_async_result
        ), patch.object(
            self.context_service, "get_clear_status", return_value=status_clearing
        ):
            # Call the method and expect timeout
            with self.assertRaises(ClearanceTimeoutError) as context:
                self.context_service.clear("context-123", timeout=4, poll_interval=1)

            self.assertIn("timed out", str(context.exception))

    @patch("time.sleep")
    async def test_clear_sync_status_check_failure(self, mock_sleep):
        """Test synchronous clear when status check fails."""
        # Mock clear_async
        clear_async_result = ClearContextResult(
            request_id="test-request-id",
            success=True,
            context_id="context-123",
            status="clearing",
            error_message="",
        )

        # Mock _get_clear_status to return failure
        status_failure = ClearContextResult(
            request_id="test-request-id",
            success=False,
            error_message="Failed to check status",
        )

        with patch.object(
            self.context_service, "clear_async", return_value=clear_async_result
        ), patch.object(
            self.context_service, "get_clear_status", return_value=status_failure
        ):
            # Call the method
            result = self.context_service.clear("context-123")

            # Verify the result
            self.assertFalse(result.success)
            self.assertIn("Failed to check status", result.error_message)

    async def test_clear_sync_async_failure(self):
        """Test synchronous clear when async initiation fails."""
        # Mock clear_async to return failure
        clear_async_result = ClearContextResult(
            request_id="test-request-id",
            success=False,
            error_message="Failed to start clearing",
        )

        with patch.object(
            self.context_service, "clear_async", return_value=clear_async_result
        ):
            # Call the method
            result = self.context_service.clear("context-123")

            # Verify the result
            self.assertFalse(result.success)
            self.assertIn("Failed to start clearing", result.error_message)

    @patch("time.sleep")
    async def test_clear_sync_unexpected_state(self, mock_sleep):
        """Test synchronous clear with unexpected state."""
        # Mock clear_async
        clear_async_result = ClearContextResult(
            request_id="test-request-id",
            success=True,
            context_id="context-123",
            status="clearing",
            error_message="",
        )

        # Mock _get_clear_status to return unexpected state, then available
        status_in_use = ClearContextResult(
            request_id="test-request-id",
            success=True,
            context_id="context-123",
            status="in-use",
            error_message="",
        )
        status_available = ClearContextResult(
            request_id="test-request-id",
            success=True,
            context_id="context-123",
            status="available",
            error_message="",
        )

        with patch.object(
            self.context_service, "clear_async", return_value=clear_async_result
        ), patch.object(
            self.context_service,
            "get_clear_status",
            side_effect=[status_in_use, status_available],
        ):
            # Call the method
            result = self.context_service.clear(
                "context-123", timeout=10, poll_interval=1
            )

            # Verify the result - should continue polling and succeed
            self.assertTrue(result.success)
            self.assertEqual(result.status, "available")


class TestAsyncClearContextResult(unittest.IsolatedAsyncioTestCase):
    """Test suite for ClearContextResult class."""

    async def test_clear_context_result_initialization(self):
        """Test ClearContextResult initialization."""
        result = ClearContextResult(
            request_id="test-request-id",
            success=True,
            error_message="",
            status="clearing",
            context_id="context-123",
        )

        self.assertEqual(result.request_id, "test-request-id")
        self.assertTrue(result.success)
        self.assertEqual(result.error_message, "")
        self.assertEqual(result.status, "clearing")
        self.assertEqual(result.context_id, "context-123")

    async def test_clear_context_result_defaults(self):
        """Test ClearContextResult with default values."""
        result = ClearContextResult()

        self.assertEqual(result.request_id, "")
        self.assertFalse(result.success)
        self.assertEqual(result.error_message, "")
        self.assertIsNone(result.status)
        self.assertIsNone(result.context_id)


if __name__ == "__main__":
    unittest.main()
