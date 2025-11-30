import os
import time
import unittest
from unittest.mock import AsyncMock, MagicMock, patch

from agentbay._common.logger import get_logger
from agentbay._common.models.response import McpToolResult, OperationResult
from agentbay._async.agent import Agent, ExecutionResult

logger = get_logger("agentbay-unit-test")


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


class TestAsyncAgent(unittest.IsolatedAsyncioTestCase):
    async def setUp(self):
        self.session = DummyAsyncAsyncSession()
        self.agent = Agent(self.session)
        self.max_try_times = os.environ.get("AGENT_TASK_TIMEOUT")
        if not self.max_try_times:
            self.max_try_times = 5

    async def test_task_execute_success(self):
        """
        Test flux_execute_task method with successful response.
        """
        from agentbay._common.models.response import McpToolResult

        mock_result = McpToolResult(
            request_id="request-123",
            success=True,
            data="""{"task_id": "task-123", "status": "finished", "result":"", "product": "Task completed successfully"}""",
        )
        self.session.call_mcp_tool.return_value = mock_result

        result = self.agent.execute_task("Say hello", int(self.max_try_times))
        self.assertIsInstance(result, ExecutionResult)
        self.assertTrue(result.success)
        self.assertEqual(result.request_id, "request-123")
        self.assertEqual(result.task_status, "finished")
        self.assertEqual(result.error_message, "")

        # Verify call arguments
        self.assertEqual(self.session.call_mcp_tool.call_count, 2)
        args = self.session.call_mcp_tool.call_args[0][1]
        self.assertEqual(args["task_id"], "task-123")
        logger.info(f"Task Say hello result: {result.task_result}")

    async def test_execute_task_error(self):
        """
        Test execute_task method with error response.
        """
        from agentbay._common.models.response import McpToolResult

        mock_result = McpToolResult(
            request_id="request-123",
            success=False,
            error_message="Task execution failed",
            data="""{"task_id": "task-123", "status": "failed", "result":"", "product": "Task Failed"}""",
        )
        self.session.call_mcp_tool.return_value = mock_result
        result = self.agent.execute_task("Say hello", self.max_try_times)
        self.assertIsInstance(result, ExecutionResult)
        self.assertFalse(result.success)
        self.assertEqual(result.request_id, "request-123")
        self.assertEqual(result.error_message, "Task execution failed")
        self.assertEqual(result.task_status, "failed")
        args = self.session.call_mcp_tool.call_args[0][1]
        self.assertEqual(args["task"], "Say hello")
        logger.info(f"Task Say hello result: {result.task_result}")

    async def test_task_terminate_success(self):
        """
        Test terminate_task method with successful response.
        """
        from agentbay._common.models.response import McpToolResult

        mock_result = McpToolResult(
            request_id="request-123",
            success=True,
            data="""{"task_id": "task-123", "status": "finished", "result":"", "product": "Task completed successfully"}""",
        )
        self.session.call_mcp_tool.return_value = mock_result

        result = self.agent.terminate_task("task-123")
        self.assertIsInstance(result, ExecutionResult)
        self.assertTrue(result.success)
        self.assertEqual(result.request_id, "request-123")
        self.assertEqual(result.task_status, "finished")
        self.assertEqual(result.error_message, "")

        # Verify call arguments
        self.session.call_mcp_tool.assert_called_once()
        args = self.session.call_mcp_tool.call_args[0][1]
        self.assertEqual(args["task_id"], "task-123")

    async def test_task_async_execute_timeout(self):
        """
        Test flux_execute_task method with successful response.
        """
        from agentbay._common.models.response import McpToolResult

        mock_result = McpToolResult(
            request_id="request-123",
            success=True,
            data="""{"task_id": "task-123", "status": "finished", "result":"", "product": "Task completed successfully"}""",
        )
        self.session.call_mcp_tool.return_value = mock_result

        result = self.agent.async_execute_task("Say hello")
        self.assertIsInstance(result, ExecutionResult)
        self.assertTrue(result.success)
        self.assertEqual(result.request_id, "request-123")
        self.assertEqual(result.task_status, "running")
        self.assertEqual(result.error_message, "")
        self.assertEqual(result.task_id, "task-123")

        # Verify call arguments
        self.assertEqual(self.session.call_mcp_tool.call_count, 1)

        retry_times: int = 0
        while retry_times < int(self.max_try_times):
            mock_query_result = OperationResult(
                request_id="request-123",
                success=True,
                data="""{"task_id": "task-123", "status": "running", "result":"", "product": "Task is runnning."}""",
            )
            self.session.call_mcp_tool.return_value = mock_query_result
            query_result = self.agent.get_task_status(result.task_id)
            self.assertTrue(query_result.success)
            logger.info(
                f"⏳ Task {query_result.task_id} running 🚀: {query_result.task_product}."
            )
            if query_result.task_status == "finished":
                break
            retry_times += 1
            time.sleep(3)
        self.assertTrue(retry_times >= int(self.max_try_times))

    async def test_task_async_execute_success(self):
        """
        Test flux_execute_task method with successful response.
        """
        from agentbay._common.models.response import McpToolResult

        mock_result = McpToolResult(
            request_id="request-123",
            success=True,
            data="""{"task_id": "task-123", "status": "finished", "result":"", "product": "Task completed successfully"}""",
        )
        self.session.call_mcp_tool.return_value = mock_result

        result = self.agent.async_execute_task("Say hello")
        self.assertIsInstance(result, ExecutionResult)
        self.assertTrue(result.success)
        self.assertEqual(result.request_id, "request-123")
        self.assertEqual(result.task_status, "running")
        self.assertEqual(result.error_message, "")
        self.assertEqual(result.task_id, "task-123")

    async def test_task_terminate_error(self):
        """
        Test terminate_task method with successful response.
        """
        from agentbay._common.models.response import McpToolResult

        mock_result = McpToolResult(
            request_id="request-123",
            success=False,
            data="""{"task_id": "task-123", "status": "failed", "result":"", "product": "Task Failed"}""",
        )
        self.session.call_mcp_tool.return_value = mock_result

        result = self.agent.terminate_task("task-123")
        self.assertIsInstance(result, ExecutionResult)
        self.assertFalse(result.success)
        self.assertEqual(result.request_id, "request-123")
        self.assertEqual(result.task_status, "failed")

        # Verify call arguments
        self.session.call_mcp_tool.assert_called_once()
        args = self.session.call_mcp_tool.call_args[0][1]
        self.assertEqual(args["task_id"], "task-123")


if __name__ == "__main__":
    unittest.main()
