"""
Unit tests for Session LinkUrl HTTP client reuse.

Verifies that:
1. The same httpx.AsyncClient instance is reused across multiple calls
2. The client is properly cleaned up when the session is deleted
"""

import unittest
from unittest.mock import MagicMock, AsyncMock, patch
import httpx
import pytest


class DummyAgentBay:
    """Mock AgentBay for testing."""

    def __init__(self):
        self.client = MagicMock()
        self.api_key = "test_api_key"

    def get_api_key(self):
        return self.api_key

    def get_client(self):
        return self.client


class TestLinkHttpClientReuse(unittest.IsolatedAsyncioTestCase):
    """Test that the shared HTTP client is reused and properly cleaned up."""

    def setUp(self):
        from agentbay import AsyncSession

        self.agent_bay = DummyAgentBay()
        self.session = AsyncSession(self.agent_bay, "test_session_id")
        self.session.link_url = "https://example.com/mcp"
        self.session.token = "test_token"

    async def test_client_is_none_initially(self):
        """HTTP client should be None before any LinkUrl call."""
        self.assertIsNone(self.session._link_http_client)

    async def test_get_link_http_client_creates_client(self):
        """First call to _get_link_http_client should create a new client."""
        client = self.session._get_link_http_client()
        self.assertIsNotNone(client)
        self.assertIsInstance(client, httpx.AsyncClient)

    async def test_get_link_http_client_returns_same_instance(self):
        """Multiple calls should return the exact same client instance."""
        client1 = self.session._get_link_http_client()
        client2 = self.session._get_link_http_client()
        client3 = self.session._get_link_http_client()
        self.assertIs(client1, client2)
        self.assertIs(client2, client3)

    async def test_close_link_http_client_sets_none(self):
        """_close_link_http_client should set _link_http_client to None."""
        _ = self.session._get_link_http_client()
        self.assertIsNotNone(self.session._link_http_client)

        await self.session._close_link_http_client()
        self.assertIsNone(self.session._link_http_client)

    async def test_close_link_http_client_when_none(self):
        """_close_link_http_client should be safe to call when client is None."""
        self.assertIsNone(self.session._link_http_client)
        await self.session._close_link_http_client()
        self.assertIsNone(self.session._link_http_client)

    async def test_new_client_created_after_close(self):
        """After closing, a new call should create a fresh client instance."""
        client1 = self.session._get_link_http_client()
        await self.session._close_link_http_client()
        client2 = self.session._get_link_http_client()
        self.assertIsNotNone(client2)
        self.assertIsNot(client1, client2)

    @patch("agentbay._async.session.AsyncSession.get_status")
    async def test_delete_closes_link_http_client(self, mock_get_status):
        """Session.delete() should close the link HTTP client in its finally block."""
        from agentbay._async.session import SessionStatusResult

        _ = self.session._get_link_http_client()
        self.assertIsNotNone(self.session._link_http_client)

        mock_delete_response = MagicMock()
        mock_delete_response.to_map.return_value = {
            "body": {"Success": True, "RequestId": "test-req-id"},
            "headers": {"x-acs-request-id": "test-req-id"},
        }
        self.agent_bay.client.delete_session_async_async = AsyncMock(
            return_value=mock_delete_response
        )

        status_result = SessionStatusResult(
            request_id="test",
            success=True,
            status="FINISH",
        )
        mock_get_status.return_value = status_result

        await self.session.delete()

        self.assertIsNone(self.session._link_http_client)

    @patch("httpx.AsyncClient.post")
    async def test_call_mcp_tool_link_url_uses_shared_client(self, mock_post):
        """_call_mcp_tool_link_url should use the shared HTTP client."""
        from agentbay._common.models.mcp_tool import McpTool

        self.session.mcpTools = [McpTool(name="shell", server="wuying_shell")]

        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "exit_code": 0,
            "stdout": "hello",
            "stderr": "",
        }
        mock_response.text = '{"exit_code": 0, "stdout": "hello", "stderr": ""}'
        mock_post.return_value = mock_response

        self.assertIsNone(self.session._link_http_client)

        await self.session._call_mcp_tool_link_url(
            "shell", {"command": "echo hello"}, "wuying_shell"
        )

        self.assertIsNotNone(self.session._link_http_client)
        client_after_first_call = self.session._link_http_client

        await self.session._call_mcp_tool_link_url(
            "shell", {"command": "echo world"}, "wuying_shell"
        )

        self.assertIs(self.session._link_http_client, client_after_first_call)


if __name__ == "__main__":
    unittest.main()
