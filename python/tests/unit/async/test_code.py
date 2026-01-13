import unittest
import pytest
from unittest.mock import AsyncMock, MagicMock

from agentbay import AsyncCode, EnhancedCodeExecutionResult, McpToolResult


class TestAsyncCode(unittest.IsolatedAsyncioTestCase):
    """Unit tests for Code module."""

    def setUp(self):
        """Set up test fixtures."""
        self.mock_session = MagicMock()
        self.session = self.mock_session  # Add session reference
        self.mock_session._get_api_key.return_value = "test-api-key"
        self.mock_session._get_session_id.return_value = "test-session-id"
        self.mock_session._is_vpc_enabled.return_value = False
        self.mock_session.call_mcp_tool = AsyncMock()
        
        # AsyncCode constructor calls super which stores session
        self.code = AsyncCode(self.mock_session)

    @pytest.mark.asyncio
    async def test_run_code_success_python(self):
        """
        Test run_code method with Python code.
        """
        self.mock_session.call_mcp_tool.return_value = McpToolResult(
            request_id="test-request-id",
            success=True,
            data="Hello, world!\n2\n",
            error_message="",
        )

        code = "print('Hello, world!')\nx = 1 + 1\nprint(x)"
        result = await self.code.run_code(code, "python")

        self.mock_session.call_mcp_tool.assert_called_once()
        tool_name, args = self.mock_session.call_mcp_tool.call_args.args[:2]
        self.assertEqual(tool_name, "run_code")
        self.assertEqual(args["language"], "python")
        self.assertEqual(
            self.mock_session.call_mcp_tool.call_args.kwargs.get("server_name"),
            "wuying_codespace",
        )
        
        # Verify the result
        self.assertIsInstance(result, EnhancedCodeExecutionResult)
        self.assertTrue(result.success)
        self.assertEqual(result.result, "Hello, world!\n2\n")
        self.assertEqual(result.request_id, "test-request-id")

    @pytest.mark.asyncio
    async def test_run_alias_calls_run_code(self):
        self.mock_session.call_mcp_tool.return_value = McpToolResult(
            request_id="test-request-id",
            success=True,
            data="OK\n",
            error_message="",
        )

        result = await self.code.run("print('OK')", "python", timeout_s=10)
        self.assertTrue(result.success)
        self.mock_session.call_mcp_tool.assert_called_once()

        tool_name, args = self.mock_session.call_mcp_tool.call_args.args[:2]
        self.assertEqual(tool_name, "run_code")
        self.assertEqual(args["language"], "python")
        self.assertEqual(args["timeout_s"], 10)
        self.assertEqual(
            self.mock_session.call_mcp_tool.call_args.kwargs.get("server_name"),
            "wuying_codespace",
        )

    @pytest.mark.asyncio
    async def test_execute_alias_calls_run_code(self):
        self.mock_session.call_mcp_tool.return_value = McpToolResult(
            request_id="test-request-id",
            success=True,
            data="OK\n",
            error_message="",
        )

        result = await self.code.execute("print('OK')", "python")
        self.assertTrue(result.success)
        self.mock_session.call_mcp_tool.assert_called_once()
        self.assertEqual(
            self.mock_session.call_mcp_tool.call_args.kwargs.get("server_name"),
            "wuying_codespace",
        )

    @pytest.mark.asyncio
    async def test_run_code_success_javascript(self):
        """
        Test run_code method with JavaScript code.
        """
        self.mock_session.call_mcp_tool.return_value = McpToolResult(
            request_id="test-request-id",
            success=True,
            data="Hello, world!\n2\n",
            error_message="",
        )

        code = "console.log('Hello, world!');\nconst x = 1 + 1;\nconsole.log(x);"
        custom_timeout = 120

        result = await self.code.run_code(code, "javascript", timeout_s=custom_timeout)

        self.mock_session.call_mcp_tool.assert_called_once()
        tool_name, args = self.mock_session.call_mcp_tool.call_args.args[:2]
        self.assertEqual(tool_name, "run_code")
        self.assertEqual(args["language"], "javascript")
        self.assertEqual(args["timeout_s"], custom_timeout)
        self.assertEqual(
            self.mock_session.call_mcp_tool.call_args.kwargs.get("server_name"),
            "wuying_codespace",
        )

        self.assertIsInstance(result, EnhancedCodeExecutionResult)
        self.assertTrue(result.success)
        self.assertEqual(result.result, "Hello, world!\n2\n")
        self.assertEqual(result.request_id, "test-request-id")

    @pytest.mark.asyncio
    async def test_run_code_language_case_insensitive(self):
        """
        Test run_code method supports case-insensitive language input.
        """
        self.mock_session.call_mcp_tool.return_value = McpToolResult(
            request_id="test-request-id",
            success=True,
            data="OK\n",
            error_message="",
        )

        result = await self.code.run_code("print('OK')", "PyThOn")

        self.assertTrue(result.success)
        self.mock_session.call_mcp_tool.assert_called_once()

        tool_name, args = self.mock_session.call_mcp_tool.call_args.args[:2]
        self.assertEqual(tool_name, "run_code")
        self.assertEqual(args["language"], "python")
        self.assertEqual(
            self.mock_session.call_mcp_tool.call_args.kwargs.get("server_name"),
            "wuying_codespace",
        )

    @pytest.mark.asyncio
    async def test_run_code_supports_r_and_java(self):
        """
        Test run_code method supports R and Java.
        """
        self.mock_session.call_mcp_tool.return_value = McpToolResult(
            request_id="test-request-id",
            success=True,
            data="OK\n",
            error_message="",
        )

        # R (case-insensitive)
        result_r = await self.code.run_code('cat("OK\\n")', "R")
        self.assertTrue(result_r.success)

        tool_name_r, args_r = self.mock_session.call_mcp_tool.call_args.args[:2]
        self.assertEqual(tool_name_r, "run_code")
        self.assertEqual(args_r["language"], "r")
        self.assertEqual(
            self.mock_session.call_mcp_tool.call_args.kwargs.get("server_name"),
            "wuying_codespace",
        )

        self.mock_session.call_mcp_tool.reset_mock()
        self.mock_session.call_mcp_tool.return_value = McpToolResult(
            request_id="test-request-id",
            success=True,
            data="OK\n",
            error_message="",
        )

        # Java (case-insensitive)
        result_java = await self.code.run_code('System.out.println("OK");', "Java")
        self.assertTrue(result_java.success)

        tool_name_java, args_java = self.mock_session.call_mcp_tool.call_args.args[:2]
        self.assertEqual(tool_name_java, "run_code")
        self.assertEqual(args_java["language"], "java")
        self.assertEqual(
            self.mock_session.call_mcp_tool.call_args.kwargs.get("server_name"),
            "wuying_codespace",
        )

    @pytest.mark.asyncio
    async def test_run_code_invalid_language(self):
        """
        Test run_code method with invalid language.
        """
        result = await self.code.run_code("print('test')", "invalid_language")

        self.assertIsInstance(result, EnhancedCodeExecutionResult)
        self.assertFalse(result.success)
        self.assertIn("Unsupported language", result.error_message)

    @pytest.mark.asyncio
    async def test_run_code_error(self):
        """
        Test run_code method with error response.
        """
        self.mock_session.call_mcp_tool.return_value = McpToolResult(
            request_id="test-request-id",
            success=False,
            data="",
            error_message="Execution failed",
        )

        result = await self.code.run_code("print('test')", "python")

        self.assertIsInstance(result, EnhancedCodeExecutionResult)
        self.assertFalse(result.success)
        self.assertIn("Execution failed", result.error_message)
        self.assertEqual(result.request_id, "test-request-id")

    @pytest.mark.asyncio
    async def test_run_code_exception(self):
        """
        Test run_code method with exception.
        """
        self.mock_session.call_mcp_tool.side_effect = Exception("Network error")

        result = await self.code.run_code("print('test')", "python")

        self.assertIsInstance(result, EnhancedCodeExecutionResult)
        self.assertFalse(result.success)
        self.assertIn("Network error", result.error_message)


if __name__ == "__main__":
    unittest.main()
