import unittest
from unittest.mock import AsyncMock, MagicMock

import pytest

from agentbay import AsyncSession


class DummyResponse:
    def to_map(self):
        return {
            "body": {
                "HttpStatusCode": 200,
                "Code": "ok",
                "Success": True,
                "Message": "",
                "RequestId": "rid-test",
                "Data": {"Status": "RUNNING"},
            }
        }


class DummyAgentBay:
    def __init__(self, client):
        self.client = client
        self.api_key = "test_api_key"

    def get_client(self):
        return self.client


class TestSessionGetStatus(unittest.IsolatedAsyncioTestCase):
    @pytest.mark.asyncio
    async def test_get_status_calls_async_client_method(self):
        """
        Regression test: generated _async/session.py must call client.get_session_detail_async (async),
        and the mocked method must be awaitable.
        """
        client = MagicMock()
        client.get_session_detail_async = AsyncMock(return_value=DummyResponse())

        # Deliberately do NOT provide get_session_detail (sync) on the client.
        # If generated async code calls it, this test will fail.

        agent_bay = DummyAgentBay(client)
        session = AsyncSession(agent_bay, "test_session_id")

        result = await session.get_status()

        client.get_session_detail_async.assert_called_once()
        self.assertTrue(result.success)
        self.assertEqual(result.status, "RUNNING")


