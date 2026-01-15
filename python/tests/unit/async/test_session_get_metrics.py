"""
Unit tests for AsyncSession.get_metrics() public API.

This test suite follows TDD principles:
1. Write tests first (red)
2. Implement functionality (green)
3. Refactor if needed
"""

import json
import pytest
import unittest
from unittest.mock import AsyncMock, MagicMock


class DummyAgentBay:
    """Mock AgentBay for testing."""

    def __init__(self):
        self.client = MagicMock()
        self.api_key = "test_api_key"

    def get_api_key(self):
        return self.api_key

    def get_client(self):
        return self.client


class TestAsyncSessionGetMetrics(unittest.IsolatedAsyncioTestCase):
    """Test cases for AsyncSession.get_metrics()."""

    def setUp(self):
        from agentbay import AsyncSession

        self.agent_bay = DummyAgentBay()
        self.session = AsyncSession(self.agent_bay, "test_session_id")

    def test_get_metrics_method_exists(self):
        self.assertTrue(hasattr(self.session, "get_metrics"))
        self.assertTrue(callable(getattr(self.session, "get_metrics")))

    @pytest.mark.asyncio
    async def test_get_metrics_success_parses_json(self):
        from agentbay import McpToolResult

        raw = {
            "cpu_count": 4,
            "cpu_used_pct": 1.0,
            "disk_total": 105286258688,
            "disk_used": 30269431808,
            "mem_total": 7918718976,
            "mem_used": 2139729920,
            "rx_rate_kbyte_per_s": 0.22,
            "tx_rate_kbyte_per_s": 0.38,
            "rx_used_kbyte": 1247.27,
            "tx_used_kbyte": 120.13,
            "timestamp": "2025-12-24T10:54:23+08:00",
        }

        self.session.call_mcp_tool = AsyncMock(
            return_value=McpToolResult(
                request_id="req-1",
                success=True,
                data=json.dumps(raw, ensure_ascii=False),
                error_message="",
            )
        )

        result = await self.session.get_metrics()
        self.session.call_mcp_tool.assert_awaited_once_with(
            tool_name="get_metrics",
            args={},
            read_timeout=None,
            connect_timeout=None,
        )
        self.assertTrue(result.success)
        self.assertEqual(result.request_id, "req-1")
        self.assertIsNotNone(result.metrics)
        self.assertEqual(result.metrics.cpu_count, 4)
        self.assertAlmostEqual(result.metrics.cpu_used_pct, 1.0, places=6)
        self.assertEqual(result.metrics.mem_total, 7918718976)
        self.assertEqual(result.metrics.disk_total, 105286258688)
        self.assertAlmostEqual(result.metrics.rx_rate_kbyte_per_s, 0.22, places=6)
        self.assertAlmostEqual(result.metrics.tx_rate_kbyte_per_s, 0.38, places=6)
        self.assertEqual(result.metrics.timestamp, "2025-12-24T10:54:23+08:00")
        self.assertIn("rx_rate_kbyte_per_s", result.raw)
        self.assertIn("tx_rate_kbyte_per_s", result.raw)

    @pytest.mark.asyncio
    async def test_get_metrics_invalid_json_returns_error(self):
        from agentbay import McpToolResult

        self.session.call_mcp_tool = AsyncMock(
            return_value=McpToolResult(
                request_id="req-2",
                success=True,
                data="{not-json}",
                error_message="",
            )
        )

        result = await self.session.get_metrics()
        self.session.call_mcp_tool.assert_awaited_once_with(
            tool_name="get_metrics",
            args={},
            read_timeout=None,
            connect_timeout=None,
        )
        self.assertFalse(result.success)
        self.assertEqual(result.request_id, "req-2")
        self.assertIsNone(result.metrics)
        self.assertIn("Failed to parse get_metrics response", result.error_message)


