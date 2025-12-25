import unittest
from unittest.mock import MagicMock

import pytest

from agentbay import Session


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


class TestSessionGetStatus(unittest.TestCase):
    @pytest.mark.sync
    def test_get_status_calls_sync_client_method(self):
        """
        Regression test: generated _sync/session.py must call client.get_session_detail (sync),
        NOT client.get_session_detail_async (async).
        """
        client = MagicMock()
        client.get_session_detail = MagicMock(return_value=DummyResponse())

        # Deliberately do NOT provide get_session_detail_async on the client.
        # If generated sync code calls it, this test will fail.

        agent_bay = DummyAgentBay(client)
        session = Session(agent_bay, "test_session_id")

        result = session.get_status()

        client.get_session_detail.assert_called_once()
        self.assertTrue(result.success)
        self.assertEqual(result.status, "RUNNING")


