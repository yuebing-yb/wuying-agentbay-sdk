import unittest
from unittest.mock import MagicMock, patch

from agentbay._common.models.response import OperationResult
from agentbay._sync.command import Command, CommandResult


class DummySession:
    def __init__(self):
        self.api_key = "dummy_key"
        self.session_id = "dummy_session"
        self.client = MagicMock()
        # Add call_mcp_tool method for new API
        self.call_mcp_tool = MagicMock()

    def get_api_key(self):
        return self.api_key

    def get_session_id(self):
        return self.session_id

    def get_client(self):
        return self.client


class TestCommand(unittest.TestCase):
    def setUp(self):
        self.session = DummySession()
        self.command = Command(self.session)

    def test_execute_command_success(self):
        """
        Test execute_command method with successful response.
        """
        from agentbay._common.models.response import McpToolResult

        mock_result = McpToolResult(
            request_id="request-123", success=True, data="line1\nline2\n"
        )
        self.session.call_mcp_tool.return_value = mock_result

        result = self.command.execute_command("ls -la")
        self.assertIsInstance(result, CommandResult)
        self.assertTrue(result.success)
        self.assertEqual(result.request_id, "request-123")
        self.assertEqual(result.output, "line1\nline2\n")
        self.assertEqual(result.error_message, "")

        # Verify call arguments
        self.session.call_mcp_tool.assert_called_once()
        args = self.session.call_mcp_tool.call_args[0][1]
        self.assertEqual(args["command"], "ls -la")
        self.assertEqual(args["timeout_ms"], 60000)  # Default timeout

    def test_execute_command_with_custom_timeout(self):
        """
        Test execute_command method with custom timeout.
        """
        from agentbay._common.models.response import McpToolResult

        mock_result = McpToolResult(
            request_id="request-123", success=True, data="line1\nline2\n"
        )
        self.session.call_mcp_tool.return_value = mock_result

        custom_timeout = 2000
        result = self.command.execute_command("ls -la", timeout_ms=custom_timeout)
        self.assertIsInstance(result, CommandResult)
        self.assertTrue(result.success)
        self.assertEqual(result.output, "line1\nline2\n")

        # Verify custom timeout was used
        self.session.call_mcp_tool.assert_called_once()
        args = self.session.call_mcp_tool.call_args[0][1]
        self.assertEqual(args["timeout_ms"], custom_timeout)

    def test_execute_command_error(self):
        """
        Test execute_command method with error response.
        """
        from agentbay._common.models.response import McpToolResult

        mock_result = McpToolResult(
            request_id="request-123",
            success=False,
            error_message="Command execution failed",
        )
        self.session.call_mcp_tool.return_value = mock_result

        result = self.command.execute_command("ls -la")
        self.assertIsInstance(result, CommandResult)
        self.assertFalse(result.success)
        self.assertEqual(result.request_id, "request-123")
        self.assertEqual(result.error_message, "Command execution failed")
        self.assertEqual(result.output, "")

    def test_execute_command_exception(self):
        """
        Test execute_command method with exception.
        """
        self.session.call_mcp_tool.side_effect = Exception("mock error")

        result = self.command.execute_command("ls -la")
        self.assertIsInstance(result, CommandResult)
        self.assertFalse(result.success)
        self.assertEqual(result.request_id, "")
        self.assertIn("Failed to execute command: mock error", result.error_message)
        self.assertEqual(result.output, "")


if __name__ == "__main__":
    unittest.main()
