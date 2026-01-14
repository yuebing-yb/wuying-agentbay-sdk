"""
Unit tests for Session.call_mcp_tool() public API.

This test suite follows TDD principles:
1. Write tests first (red)
2. Implement functionality (green)
3. Refactor if needed
"""

import json
import pytest
import unittest
from unittest.mock import AsyncMock, MagicMock, Mock, patch


class DummyAgentBay:
    """Mock AgentBay for testing."""

    def __init__(self):
        self.client = MagicMock()
        self.api_key = "test_api_key"

    def get_api_key(self):
        return self.api_key

    def get_client(self):
        return self.client


class TestAsyncSessionCallMcpTool(unittest.IsolatedAsyncioTestCase):
    """Test cases for Session.call_mcp_tool() public API."""

    def setUp(self):
        """Set up test fixtures."""
        from agentbay import AsyncSession

        self.agent_bay = DummyAgentBay()
        self.session_id = "test_session_id"
        self.session = AsyncSession(self.agent_bay, self.session_id)

    def test_call_mcp_tool_method_exists(self):
        """Test that call_mcp_tool method exists and is public."""
        self.assertTrue(hasattr(self.session, "call_mcp_tool"))
        self.assertTrue(callable(getattr(self.session, "call_mcp_tool")))

    @patch("agentbay._async.session.CallMcpToolRequest")
    @patch("agentbay._async.session.extract_request_id")
    @pytest.mark.asyncio

    async def test_call_mcp_tool_success_non_vpc(
        self, mock_extract_request_id, MockCallMcpToolRequest
    ):
        """Test successful MCP tool call in non-VPC mode."""
        # Setup mocks
        mock_request = MagicMock()
        mock_response = MagicMock()
        MockCallMcpToolRequest.return_value = mock_request
        mock_extract_request_id.return_value = "request-123"
        self.agent_bay.client.call_mcp_tool_async = AsyncMock(
            return_value=mock_response
        )

        # Mock response structure
        mock_response.to_map.return_value = {
            "body": {
                "Data": json.dumps(
                    {
                        "content": [{"type": "text", "text": "command output"}],
                        "isError": False,
                    }
                ),
                "Success": True,
            }
        }

        # Call the method
        result = await self.session.call_mcp_tool(
            "shell", {"command": "ls", "timeout_ms": 1000}
        )

        # Assertions
        self.assertIsNotNone(result)
        self.assertEqual(result.request_id, "request-123")
        self.assertTrue(result.success)
        self.assertEqual(result.data, "command output")
        self.assertEqual(result.error_message, "")

        # Verify API was called correctly
        MockCallMcpToolRequest.assert_called_once()
        call_args = MockCallMcpToolRequest.call_args
        self.assertEqual(call_args[1]["authorization"], "Bearer test_api_key")
        self.assertEqual(call_args[1]["session_id"], "test_session_id")
        self.assertEqual(call_args[1]["name"], "shell")
        args_dict = json.loads(call_args[1]["args"])
        self.assertEqual(args_dict["command"], "ls")
        self.assertEqual(args_dict["timeout_ms"], 1000)

    @patch("agentbay._async.session.CallMcpToolRequest")
    @patch("agentbay._async.session.extract_request_id")
    @pytest.mark.asyncio
    async def test_call_mcp_tool_success_non_vpc_with_server_name(
        self, mock_extract_request_id, MockCallMcpToolRequest
    ):
        """Test non-VPC mode forwards explicit server_name to API request."""
        # Setup mocks
        mock_request = MagicMock()
        mock_response = MagicMock()
        MockCallMcpToolRequest.return_value = mock_request
        mock_extract_request_id.return_value = "request-123"
        self.agent_bay.client.call_mcp_tool_async = AsyncMock(
            return_value=mock_response
        )

        # Mock response structure
        mock_response.to_map.return_value = {
            "body": {
                "Data": json.dumps(
                    {
                        "content": [{"type": "text", "text": "command output"}],
                        "isError": False,
                    }
                ),
                "Success": True,
            }
        }

        # Call the method with explicit server_name
        result = await self.session.call_mcp_tool(
            "shell",
            {"command": "ls", "timeout_ms": 1000},
            server_name="wuying_shell",
        )

        self.assertTrue(result.success)
        MockCallMcpToolRequest.assert_called_once()
        call_args = MockCallMcpToolRequest.call_args[1]
        self.assertEqual(call_args.get("server"), "wuying_shell")

    @patch("agentbay._async.session.CallMcpToolRequest")
    @patch("agentbay._async.session.extract_request_id")
    @pytest.mark.asyncio

    async def test_call_mcp_tool_with_error_response(
        self, mock_extract_request_id, MockCallMcpToolRequest
    ):
        """Test MCP tool call with error response."""
        # Setup mocks
        mock_request = MagicMock()
        mock_response = MagicMock()
        MockCallMcpToolRequest.return_value = mock_request
        mock_extract_request_id.return_value = "request-456"
        self.agent_bay.client.call_mcp_tool_async = AsyncMock(
            return_value=mock_response
        )

        # Mock error response
        mock_response.to_map.return_value = {
            "body": {
                "Data": json.dumps(
                    {
                        "content": [
                            {"type": "text", "text": "Error: command not found"}
                        ],
                        "isError": True,
                    }
                ),
                "Success": False,
            }
        }

        # Call the method
        result = await self.session.call_mcp_tool("shell", {"command": "invalid_cmd"})

        # Assertions
        self.assertIsNotNone(result)
        self.assertEqual(result.request_id, "request-456")
        self.assertFalse(result.success)
        self.assertIn("Error", result.error_message)

    @patch("agentbay._async.session.CallMcpToolRequest")
    @patch("agentbay._async.session.extract_request_id")
    @pytest.mark.asyncio

    async def test_call_mcp_tool_api_exception(
        self, mock_extract_request_id, MockCallMcpToolRequest
    ):
        """Test MCP tool call when API raises exception."""
        # Setup mocks
        mock_request = MagicMock()
        MockCallMcpToolRequest.return_value = mock_request
        mock_extract_request_id.return_value = "request-789"
        self.agent_bay.client.call_mcp_tool_async = AsyncMock(
            side_effect=Exception("Network error")
        )

        # Call the method
        result = await self.session.call_mcp_tool("shell", {"command": "ls"})

        # Assertions
        self.assertIsNotNone(result)
        self.assertFalse(result.success)
        self.assertIn("Network error", result.error_message)

    @patch("httpx.AsyncClient")
    @pytest.mark.asyncio
    async def test_call_mcp_tool_link_url_success_with_server_name(
        self, mock_httpx_client
    ):
        """Test LinkUrl mode uses explicit server_name."""
        self.session.link_url = "http://127.0.0.1:9999/"
        self.session.token = "link_token_123"

        mock_resp = MagicMock()
        mock_resp.status_code = 200
        mock_resp.json.return_value = {
            "data": json.dumps(
                {
                    "result": {
                        "isError": False,
                        "content": [{"type": "text", "text": "link output"}],
                    }
                }
            )
        }
        mock_resp.text = ""

        mock_client_instance = MagicMock()
        mock_httpx_client.return_value.__aenter__ = AsyncMock(
            return_value=mock_client_instance
        )
        mock_httpx_client.return_value.__aexit__ = AsyncMock(return_value=None)
        mock_client_instance.post = AsyncMock(return_value=mock_resp)

        result = await self.session.call_mcp_tool(
            "shell",
            {"command": "echo hello"},
            server_name="wuying_shell",
        )

        self.assertTrue(result.success)
        self.assertEqual(result.data, "link output")
        mock_client_instance.post.assert_called_once()
        call_kwargs = mock_client_instance.post.call_args.kwargs
        self.assertEqual(call_kwargs["json"]["server"], "wuying_shell")
        self.assertEqual(call_kwargs["headers"]["X-Access-Token"], "link_token_123")

    @pytest.mark.asyncio
    async def test_call_mcp_tool_link_url_requires_server_name(self):
        """Test LinkUrl mode requires server_name."""
        self.session.link_url = "http://127.0.0.1:9999/"
        self.session.token = "link_token_123"

        result = await self.session.call_mcp_tool(
            "shell",
            {"command": "echo hello"},
        )

        self.assertFalse(result.success)
        self.assertIn("server name is required", result.error_message.lower())

    @patch("agentbay._async.session.CallMcpToolRequest")
    @patch("agentbay._async.session.extract_request_id")
    @pytest.mark.asyncio

    async def test_call_mcp_tool_with_custom_timeouts(
        self, mock_extract_request_id, MockCallMcpToolRequest
    ):
        """Test MCP tool call with custom timeout parameters."""
        # Setup mocks
        mock_request = MagicMock()
        mock_response = MagicMock()
        MockCallMcpToolRequest.return_value = mock_request
        mock_extract_request_id.return_value = "request-999"
        self.agent_bay.client.call_mcp_tool_async = AsyncMock(
            return_value=mock_response
        )

        # Mock response
        mock_response.to_map.return_value = {
            "body": {
                "Data": json.dumps(
                    {
                        "content": [{"type": "text", "text": "output"}],
                        "isError": False,
                    }
                ),
                "Success": True,
            }
        }

        # Call with custom timeouts
        result = await self.session.call_mcp_tool(
            "shell", {"command": "ls"}, read_timeout=60, connect_timeout=10
        )

        # Assertions
        self.assertTrue(result.success)

        # Verify timeouts were passed to client
        self.agent_bay.client.call_mcp_tool_async.assert_called_once()
        call_kwargs = self.agent_bay.client.call_mcp_tool_async.call_args[1]
        self.assertEqual(call_kwargs.get("read_timeout"), 60)
        self.assertEqual(call_kwargs.get("connect_timeout"), 10)

    @patch("agentbay._async.session.CallMcpToolRequest")
    @patch("agentbay._async.session.extract_request_id")
    @pytest.mark.asyncio

    async def test_call_mcp_tool_with_complex_args(
        self, mock_extract_request_id, MockCallMcpToolRequest
    ):
        """Test MCP tool call with complex nested arguments."""
        # Setup mocks
        mock_request = MagicMock()
        mock_response = MagicMock()
        MockCallMcpToolRequest.return_value = mock_request
        mock_extract_request_id.return_value = "request-complex"
        self.agent_bay.client.call_mcp_tool_async = AsyncMock(
            return_value=mock_response
        )

        # Mock response
        mock_response.to_map.return_value = {
            "body": {
                "Data": json.dumps(
                    {
                        "content": [{"type": "text", "text": "processed"}],
                        "isError": False,
                    }
                ),
                "Success": True,
            }
        }

        # Complex arguments
        complex_args = {
            "input_data": "sample",
            "options": {
                "format": "json",
                "compress": True,
                "filters": ["filter1", "filter2"],
            },
            "metadata": {"user": "test_user", "timestamp": 1234567890},
        }

        # Call the method
        result = await self.session.call_mcp_tool("data_processor", complex_args)

        # Assertions
        self.assertTrue(result.success)

        # Verify args were serialized correctly
        call_args = MockCallMcpToolRequest.call_args[1]
        args_dict = json.loads(call_args["args"])
        self.assertEqual(args_dict["input_data"], "sample")
        self.assertEqual(args_dict["options"]["format"], "json")
        self.assertTrue(args_dict["options"]["compress"])
        self.assertEqual(len(args_dict["options"]["filters"]), 2)

    @pytest.mark.asyncio


    async def test_call_mcp_tool_return_type(self):
        """Test that call_mcp_tool returns McpToolResult type."""
        from agentbay import McpToolResult

        # Mock the client
        mock_response = MagicMock()
        mock_response.to_map.return_value = {
            "body": {
                "Data": json.dumps(
                    {
                        "content": [{"type": "text", "text": "output"}],
                        "isError": False,
                    }
                ),
                "Success": True,
            }
        }
        self.agent_bay.client.call_mcp_tool_async = AsyncMock(
            return_value=mock_response
        )

        # Call the method
        result = await self.session.call_mcp_tool("shell", {"command": "ls"})

        # Verify return type
        self.assertIsInstance(result, McpToolResult)
        self.assertTrue(hasattr(result, "request_id"))
        self.assertTrue(hasattr(result, "success"))
        self.assertTrue(hasattr(result, "data"))
        self.assertTrue(hasattr(result, "error_message"))


class TestAsyncMcpToolResult(unittest.IsolatedAsyncioTestCase):
    """Test cases for McpToolResult model."""

    def test_mcp_tool_result_initialization(self):
        """Test McpToolResult can be initialized with all fields."""
        from agentbay import McpToolResult

        result = McpToolResult(
            request_id="req-123", success=True, data="test data", error_message=""
        )

        self.assertEqual(result.request_id, "req-123")
        self.assertTrue(result.success)
        self.assertEqual(result.data, "test data")
        self.assertEqual(result.error_message, "")

    def test_mcp_tool_result_defaults(self):
        """Test McpToolResult default values."""
        from agentbay import McpToolResult

        result = McpToolResult()

        self.assertEqual(result.request_id, "")
        self.assertFalse(result.success)
        self.assertEqual(result.data, "")
        self.assertEqual(result.error_message, "")


class TestAsyncSessionCallMcpToolApiFallback(unittest.IsolatedAsyncioTestCase):
    """Tests call_mcp_tool falls back to OpenAPI when LinkUrl is absent."""

    def setUp(self):
        from agentbay import AsyncSession

        self.agent_bay = DummyAgentBay()
        self.session_id = "test_session_id"
        self.session = AsyncSession(self.agent_bay, self.session_id)

    @patch("httpx.AsyncClient")
    @patch("agentbay._async.session.CallMcpToolRequest")
    @patch("agentbay._async.session.extract_request_id")
    @pytest.mark.asyncio
    async def test_call_mcp_tool_does_not_use_link_url_when_absent(
        self, mock_extract_request_id, MockCallMcpToolRequest, mock_httpx_client
    ):
        """
        When link_url/token are not set, call_mcp_tool must use the OpenAPI route and never use the httpx client.
        """
        mock_httpx_client.side_effect = AssertionError(
            "call_mcp_tool must not use httpx when LinkUrl is absent"
        )

        mock_request = MagicMock()
        mock_response = MagicMock()
        MockCallMcpToolRequest.return_value = mock_request
        mock_extract_request_id.return_value = "request-123"
        self.agent_bay.client.call_mcp_tool_async = AsyncMock(
            return_value=mock_response
        )
        mock_response.to_map.return_value = {
            "body": {
                "Data": json.dumps(
                    {
                        "content": [{"type": "text", "text": "api output"}],
                        "isError": False,
                    }
                ),
                "Success": True,
            }
        }

        result = await self.session.call_mcp_tool(
            "shell",
            {"command": "ls"},
            server_name="wuying_shell",
        )

        self.assertTrue(result.success)
        self.assertEqual(result.data, "api output")
        MockCallMcpToolRequest.assert_called_once()


if __name__ == "__main__":
    unittest.main()
