import os
import pytest
import time
import unittest
from unittest.mock import MagicMock, MagicMock, patch

from agentbay import get_logger
from agentbay import OperationResult
from agentbay import Agent
from agentbay import ExecutionResult

logger = get_logger("agentbay-unit-test")

from dotenv import load_dotenv
load_dotenv()

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


class TestAsyncAgentComputer(unittest.TestCase):
    def setUp(self):
        self.session = DummySession()
        self.agent = Agent(self.session)
        timeout = os.environ.get("AGENT_TASK_TIMEOUT")
        if not timeout:
            timeout = 30
        self.timeout = int(timeout)

    @pytest.mark.sync


    def test_computer_task_execute_and_wait_success(self):
        """
        Test flux_execute_task method with successful response.
        """
        from agentbay import McpToolResult

        mock_result = McpToolResult(
            request_id="request-123",
            success=True,
            data="""{"task_id": "task-123", "status": "finished", "result":"", "product": "Task completed successfully"}""",
        )
        self.session.call_mcp_tool.return_value = mock_result

        result = self.agent.computer.execute_task_and_wait("Hello, Computer Agent", self.timeout)
        self.assertIsInstance(result, ExecutionResult)
        self.assertTrue(result.success)
        self.assertEqual(result.request_id, "request-123")
        self.assertEqual(result.task_status, "finished")
        self.assertEqual(result.error_message, "")

        # Verify call arguments
        self.assertEqual(self.session.call_mcp_tool.call_count, 2)
        args = self.session.call_mcp_tool.call_args[0][1]
        self.assertEqual(args["task_id"], "task-123")
        logger.info(f"Result of Task Hello, Computer Agent: {result.task_result}")

    @pytest.mark.sync


    def test_computer_execute_task_and_wait_error(self):
        """
        Test execute_task method with error response.
        """
        from agentbay import McpToolResult

        mock_result = McpToolResult(
            request_id="request-123",
            success=False,
            error_message="Task execution failed",
            data="""{"task_id": "task-123", "status": "failed", "result":"", "product": "Task Failed"}""",
        )
        self.session.call_mcp_tool.return_value = mock_result
        result = self.agent.computer.execute_task_and_wait("Hello, Computer Agent", self.timeout)
        self.assertIsInstance(result, ExecutionResult)
        self.assertFalse(result.success)
        self.assertEqual(result.request_id, "request-123")
        self.assertEqual(result.error_message, "Task execution failed")
        self.assertEqual(result.task_status, "failed")
        args = self.session.call_mcp_tool.call_args[0][1]
        self.assertEqual(args["task"], "Hello, Computer Agent")
        logger.info(f"Result of task Hello, Computer Agent: {result.task_result}")

    @pytest.mark.sync


    def test_computer_task_terminate_success(self):
        """
        Test terminate_task method with successful response.
        """
        from agentbay import McpToolResult

        mock_result = McpToolResult(
            request_id="request-123",
            success=True,
            data="""{"task_id": "task-123", "status": "finised", "result":"", "product": "Task completed successfully"}""",
        )
        self.session.call_mcp_tool.return_value = mock_result

        result = self.agent.computer.terminate_task("task-123")
        self.assertIsInstance(result, ExecutionResult)
        self.assertTrue(result.success)
        self.assertEqual(result.request_id, "request-123")
        self.assertEqual(result.task_status, "finised")
        self.assertEqual(result.error_message, "")

        # Verify call arguments
        self.session.call_mcp_tool.assert_called_once()
        args = self.session.call_mcp_tool.call_args[0][1]
        self.assertEqual(args["task_id"], "task-123")

    @pytest.mark.sync


    def test_computer_task_execute_timeout(self):
        """
        Test flux_execute_task method with successful response.
        """
        from agentbay import McpToolResult

        mock_result = McpToolResult(
            request_id="request-123",
            success=True,
            data="""{"task_id": "task-123", "status": "running", "result":"", "product": "Task completed successfully"}""",
        )
        self.session.call_mcp_tool.return_value = mock_result

        result = self.agent.computer.execute_task("Hello, Computer Agent")
        self.assertIsInstance(result, ExecutionResult)
        self.assertTrue(result.success)
        self.assertEqual(result.request_id, "request-123")
        self.assertEqual(result.task_status, "running")
        self.assertEqual(result.error_message, "")
        self.assertEqual(result.task_id, "task-123")

        # Verify call arguments
        self.assertEqual(self.session.call_mcp_tool.call_count, 1)

        retry_times: int = 0
        max_poll_attempts = self.timeout // 3
        with patch("time.sleep", return_value=None) as sleep_mock:
            while retry_times < max_poll_attempts:
                mock_query_result = OperationResult(
                    request_id="request-123",
                    success=True,
                    data="""{"task_id": "task-123", "status": "running", "result":"", "product": "Task is runnning."}""",
                )
                self.session.call_mcp_tool.return_value = mock_query_result
                query_result = self.agent.computer.get_task_status(result.task_id)
                self.assertTrue(query_result.success)
                logger.info(
                    f"⏳ Task {query_result.task_id} running 🚀: {query_result.task_product}."
                )
                if query_result.task_status == "finished":
                    break
                retry_times += 1
                time.sleep(3)
        self.assertTrue(retry_times >= max_poll_attempts)
        self.assertEqual(sleep_mock.call_count, max_poll_attempts)
        sleep_mock.assert_called_with(3)

    @pytest.mark.sync


    def test_computer_task_execute_success(self):
        """
        Test flux_execute_task method with successful response.
        """
        from agentbay import McpToolResult

        mock_result = McpToolResult(
            request_id="request-123",
            success=True,
            data="""{"task_id": "task-123", "status": "running", "result":"", "product": "Task completed successfully"}""",
        )
        self.session.call_mcp_tool.return_value = mock_result

        result = self.agent.computer.execute_task("Hello, Computer Agent")
        self.assertIsInstance(result, ExecutionResult)
        self.assertTrue(result.success)
        self.assertEqual(result.request_id, "request-123")
        self.assertEqual(result.task_status, "running")
        self.assertEqual(result.error_message, "")
        self.assertEqual(result.task_id, "task-123")

    @pytest.mark.sync


    def test_computer_task_terminate_error(self):
        """
        Test terminate_task method with successful response.
        """
        from agentbay import McpToolResult

        mock_result = McpToolResult(
            request_id="request-123",
            success=False,
            data="""{"task_id": "task-123", "status": "failed", "result":"", "product": "Task Failed"}""",
        )
        self.session.call_mcp_tool.return_value = mock_result

        result = self.agent.computer.terminate_task("task-123")
        self.assertIsInstance(result, ExecutionResult)
        self.assertFalse(result.success)
        self.assertEqual(result.request_id, "request-123")
        self.assertEqual(result.task_status, "failed")

        # Verify call arguments
        self.session.call_mcp_tool.assert_called_once()
        args = self.session.call_mcp_tool.call_args[0][1]
        self.assertEqual(args["task_id"], "task-123")

class TestAsyncAgentBrowser(unittest.TestCase):
    def setUp(self):
        self.session = DummySession()
        self.agent = Agent(self.session)
        timeout = os.environ.get("AGENT_TASK_TIMEOUT")
        if not timeout:
            timeout = 30
        self.timeout = int(timeout)

    @pytest.mark.sync


    def test_browser_task_execute_and_wait_success(self):
        """
        Test flux_execute_task method with successful response.
        """
        from agentbay import McpToolResult

        mock_result = McpToolResult(
            request_id="request-123",
            success=True,
            data="""{"task_id": "task-123", "status": "finished", "result":"", "product": "Task completed successfully"}""",
        )
        self.session.call_mcp_tool.return_value = mock_result

        result = self.agent.browser.execute_task_and_wait("Hello, Browser Agent", self.timeout)
        self.assertIsInstance(result, ExecutionResult)
        self.assertTrue(result.success)
        self.assertEqual(result.request_id, "request-123")
        self.assertEqual(result.task_status, "finished")
        self.assertEqual(result.error_message, "")

        # Verify call arguments
        self.assertEqual(self.session.call_mcp_tool.call_count, 2)
        args = self.session.call_mcp_tool.call_args[0][1]
        self.assertEqual(args["task_id"], "task-123")
        logger.info(f"Result of Task Hello, Browser Agent: {result.task_result}")

    @pytest.mark.sync


    def test_browser_execute_task_and_wait_error(self):
        """
        Test execute_task method with error response.
        """
        from agentbay import McpToolResult

        mock_result = McpToolResult(
            request_id="request-123",
            success=False,
            error_message="Task execution failed",
            data="""{"task_id": "task-123", "status": "failed", "result":"", "product": "Task Failed"}""",
        )
        self.session.call_mcp_tool.return_value = mock_result
        result = self.agent.browser.execute_task_and_wait("Hello, Browser Agent", self.timeout)
        self.assertIsInstance(result, ExecutionResult)
        self.assertFalse(result.success)
        self.assertEqual(result.request_id, "request-123")
        self.assertEqual(result.error_message, "Task execution failed")
        self.assertEqual(result.task_status, "failed")
        args = self.session.call_mcp_tool.call_args[0][1]
        self.assertEqual(args["task"], "Hello, Browser Agent")
        logger.info(f"Result of Task Hello, Browser Agent: {result.task_result}")

    @pytest.mark.sync


    def test_browser_task_terminate_success(self):
        """
        Test terminate_task method with successful response.
        """
        from agentbay import McpToolResult

        mock_result = McpToolResult(
            request_id="request-123",
            success=True,
            data="""{"task_id": "task-123", "status": "finised", "result":"", "product": "Task completed successfully"}""",
        )
        self.session.call_mcp_tool.return_value = mock_result

        result = self.agent.browser.terminate_task("task-123")
        self.assertIsInstance(result, ExecutionResult)
        self.assertTrue(result.success)
        self.assertEqual(result.request_id, "request-123")
        self.assertEqual(result.task_status, "finised")
        self.assertEqual(result.error_message, "")

        # Verify call arguments
        self.session.call_mcp_tool.assert_called_once()
        args = self.session.call_mcp_tool.call_args[0][1]
        self.assertEqual(args["task_id"], "task-123")

    @pytest.mark.sync


    def test_browser_task_execute_timeout(self):
        """
        Test flux_execute_task method with successful response.
        """
        from agentbay import McpToolResult

        mock_result = McpToolResult(
            request_id="request-123",
            success=True,
            data="""{"task_id": "task-123", "status": "running", "result":"", "product": "Task completed successfully"}""",
        )
        self.session.call_mcp_tool.return_value = mock_result

        result = self.agent.browser.execute_task("Hello, Browser Agent")
        self.assertIsInstance(result, ExecutionResult)
        self.assertTrue(result.success)
        self.assertEqual(result.request_id, "request-123")
        self.assertEqual(result.task_status, "running")
        self.assertEqual(result.error_message, "")
        self.assertEqual(result.task_id, "task-123")

        # Verify call arguments
        self.assertEqual(self.session.call_mcp_tool.call_count, 1)

        retry_times: int = 0
        max_poll_attempts = self.timeout // 3
        with patch("time.sleep", return_value=None) as sleep_mock:
            while retry_times < max_poll_attempts:
                mock_query_result = OperationResult(
                    request_id="request-123",
                    success=True,
                    data="""{"task_id": "task-123", "status": "running", "result":"", "product": "Task is runnning."}""",
                )
                self.session.call_mcp_tool.return_value = mock_query_result
                query_result = self.agent.browser.get_task_status(result.task_id)
                self.assertTrue(query_result.success)
                logger.info(
                    f"⏳ Task {query_result.task_id} running 🚀: {query_result.task_product}."
                )
                if query_result.task_status == "finished":
                    break
                retry_times += 1
                time.sleep(3)
        self.assertTrue(retry_times >= max_poll_attempts)
        self.assertEqual(sleep_mock.call_count, max_poll_attempts)
        sleep_mock.assert_called_with(3)

    @pytest.mark.sync


    def test_browser_task_execute_success(self):
        """
        Test flux_execute_task method with successful response.
        """
        from agentbay import McpToolResult

        mock_result = McpToolResult(
            request_id="request-123",
            success=True,
            data="""{"task_id": "task-123", "status": "running", "result":"", "product": "Task completed successfully"}""",
        )
        self.session.call_mcp_tool.return_value = mock_result

        result = self.agent.browser.execute_task("Hello, Browser Agent")
        self.assertIsInstance(result, ExecutionResult)
        self.assertTrue(result.success)
        self.assertEqual(result.request_id, "request-123")
        self.assertEqual(result.task_status, "running")
        self.assertEqual(result.error_message, "")
        self.assertEqual(result.task_id, "task-123")

    @pytest.mark.sync


    def test_browser_task_terminate_error(self):
        """
        Test terminate_task method with successful response.
        """
        from agentbay import McpToolResult

        mock_result = McpToolResult(
            request_id="request-123",
            success=False,
            data="""{"task_id": "task-123", "status": "failed", "result":"", "product": "Task Failed"}""",
        )
        self.session.call_mcp_tool.return_value = mock_result

        result = self.agent.browser.terminate_task("task-123")
        self.assertIsInstance(result, ExecutionResult)
        self.assertFalse(result.success)
        self.assertEqual(result.request_id, "request-123")
        self.assertEqual(result.task_status, "failed")

        # Verify call arguments
        self.session.call_mcp_tool.assert_called_once()
        args = self.session.call_mcp_tool.call_args[0][1]
        self.assertEqual(args["task_id"], "task-123")


class TestAsyncAgentMobile(unittest.TestCase):
    def setUp(self):
        self.session = DummySession()
        self.agent = Agent(self.session)
        timeout = os.environ.get("AGENT_TASK_TIMEOUT")
        if not timeout:
            timeout = 30
        self.timeout = int(timeout)

    @pytest.mark.sync
    def test_mobile_task_execute_success(self):
        """
        Test mobile_execute_task method with successful response.
        """
        from agentbay import McpToolResult

        mock_result = McpToolResult(
            request_id="request-123",
            success=True,
            data='{"task_id": "task-123"}',
        )
        self.session.call_mcp_tool.return_value = mock_result

        result = self.agent.mobile.execute_task(
            "Open WeChat app", max_steps=100
        )
        self.assertIsInstance(result, ExecutionResult)
        self.assertTrue(result.success)
        self.assertEqual(result.request_id, "request-123")
        self.assertEqual(result.task_id, "task-123")
        self.assertEqual(result.task_status, "running")
        self.assertEqual(result.error_message, "")

        # Verify call arguments
        self.session.call_mcp_tool.assert_called_once()
        args = self.session.call_mcp_tool.call_args[0][1]
        self.assertEqual(args["task"], "Open WeChat app")
        self.assertEqual(args["max_steps"], 100)

    @pytest.mark.sync
    def test_mobile_task_execute_and_wait_success(self):
        """
        Test mobile_execute_task_and_wait method with successful response.
        """
        from agentbay import McpToolResult

        mock_result_execute = McpToolResult(
            request_id="request-123",
            success=True,
            data='{"task_id": "task-123"}',
        )
        mock_result_status = McpToolResult(
            request_id="request-124",
            success=True,
            data='{"task_id": "task-123", "status": "completed", "action": "Completed", "product": "Task completed successfully"}',
        )
        self.session.call_mcp_tool.side_effect = [
            mock_result_execute,
            mock_result_status,
        ]

        result = self.agent.mobile.execute_task_and_wait(
            "Open WeChat app", timeout=30, max_steps=100
        )
        self.assertIsInstance(result, ExecutionResult)
        self.assertTrue(result.success)
        self.assertEqual(result.request_id, "request-123")
        self.assertEqual(result.task_status, "completed")
        self.assertEqual(result.error_message, "")
        self.assertEqual(result.task_result, "Task completed successfully")

        # Verify call arguments
        self.assertEqual(self.session.call_mcp_tool.call_count, 2)
        execute_args = self.session.call_mcp_tool.call_args_list[0][0][1]
        self.assertEqual(execute_args["task"], "Open WeChat app")
        self.assertEqual(execute_args["max_steps"], 100)

    @pytest.mark.sync
    def test_mobile_execute_task_and_wait_error(self):
        """
        Test execute_task_and_wait method with error response.
        """
        from agentbay import McpToolResult

        mock_result = McpToolResult(
            request_id="request-123",
            success=False,
            error_message="Task execution failed",
            data='{"task_id": "task-123", "status": "failed"}',
        )
        self.session.call_mcp_tool.return_value = mock_result
        result = self.agent.mobile.execute_task_and_wait(
            "Open WeChat app", timeout=30, max_steps=50
        )
        self.assertIsInstance(result, ExecutionResult)
        self.assertFalse(result.success)
        self.assertEqual(result.request_id, "request-123")
        self.assertEqual(result.error_message, "Task execution failed")
        self.assertEqual(result.task_status, "failed")
        args = self.session.call_mcp_tool.call_args[0][1]
        self.assertEqual(args["task"], "Open WeChat app")
        self.assertEqual(args["max_steps"], 50)

    @pytest.mark.sync
    def test_mobile_task_execute_timeout(self):
        """
        Test mobile_execute_task_and_wait method with timeout.
        """
        from agentbay import McpToolResult

        mock_result_execute = McpToolResult(
            request_id="request-123",
            success=True,
            data='{"task_id": "task-123"}',
        )
        mock_result_status = McpToolResult(
            request_id="request-124",
            success=True,
            data='{"task_id": "task-123", "status": "running", "action": "Processing"}',
        )
        self.session.call_mcp_tool.side_effect = [
            mock_result_execute,
            mock_result_status,
            mock_result_status,
            mock_result_status,
        ]

        with patch("time.sleep", new=MagicMock(return_value=None)) as sleep_mock:
            result = self.agent.mobile.execute_task_and_wait(
                "Open WeChat app", timeout=6, max_steps=50
            )
        self.assertIsInstance(result, ExecutionResult)
        self.assertFalse(result.success)
        self.assertEqual(result.request_id, "request-123")
        self.assertIn("Task execution timed out after 6 seconds", result.error_message)
        self.assertIn("task-123", result.error_message)
        self.assertIn("Polled 2 times (max: 2)", result.error_message)
        self.assertEqual(result.task_status, "failed")
        sleep_args = [call.args[0] for call in sleep_mock.call_args_list if call.args]
        self.assertIn(3, sleep_args)
        self.assertIn(1, sleep_args)

    @pytest.mark.sync
    def test_mobile_task_terminate_success(self):
        """
        Test terminate_task method with successful response.
        """
        from agentbay import McpToolResult

        mock_result = McpToolResult(
            request_id="request-123",
            success=True,
            data='{"task_id": "task-123", "status": "cancelling"}',
        )
        self.session.call_mcp_tool.return_value = mock_result

        result = self.agent.mobile.terminate_task("task-123")
        self.assertIsInstance(result, ExecutionResult)
        self.assertTrue(result.success)
        self.assertEqual(result.request_id, "request-123")
        self.assertEqual(result.task_status, "cancelling")
        self.assertEqual(result.error_message, "")

        # Verify call arguments
        self.session.call_mcp_tool.assert_called_once()
        args = self.session.call_mcp_tool.call_args[0][1]
        self.assertEqual(args["task_id"], "task-123")

    @pytest.mark.sync
    def test_mobile_task_terminate_error(self):
        """
        Test terminate_task method with error response.
        """
        from agentbay import McpToolResult

        mock_result = McpToolResult(
            request_id="request-123",
            success=False,
            error_message="Failed to terminate task",
            data='{"task_id": "task-123", "status": "failed"}',
        )
        self.session.call_mcp_tool.return_value = mock_result

        result = self.agent.mobile.terminate_task("task-123")
        self.assertIsInstance(result, ExecutionResult)
        self.assertFalse(result.success)
        self.assertEqual(result.request_id, "request-123")
        self.assertEqual(result.task_status, "failed")
        self.assertEqual(result.error_message, "Failed to terminate task")

        # Verify call arguments
        self.session.call_mcp_tool.assert_called_once()
        args = self.session.call_mcp_tool.call_args[0][1]
        self.assertEqual(args["task_id"], "task-123")

    @pytest.mark.sync
    def test_mobile_execute_task_with_default_params(self):
        """
        Test mobile_execute_task method with default parameters.
        """
        from agentbay import McpToolResult

        mock_result = McpToolResult(
            request_id="request-123",
            success=True,
            data='{"task_id": "task-123"}',
        )
        self.session.call_mcp_tool.return_value = mock_result

        result = self.agent.mobile.execute_task("Open WeChat app")
        self.assertIsInstance(result, ExecutionResult)
        self.assertTrue(result.success)

        # Verify call arguments with default values
        args = self.session.call_mcp_tool.call_args[0][1]
        self.assertEqual(args["task"], "Open WeChat app")
        self.assertEqual(args["max_steps"], 50)  # default value


if __name__ == "__main__":
    unittest.main()
