import time
import unittest
from unittest.mock import patch

import pytest

from agentbay import AgentBay
from agentbay._common.models.context import ContextInfoResult, ContextStatusData


def _no_sleep(_seconds: float) -> None:
    return None


class _FakeContextManager:
    def __init__(self, result_sequence):
        self._result_sequence = result_sequence
        self.calls = 0

    def info(self):
        idx = min(self.calls, len(self._result_sequence) - 1)
        self.calls += 1
        return self._result_sequence[idx]


class _FakeSession:
    def __init__(self, context_manager):
        self.context = context_manager


class TestAgentBayContextWaitFlagBeta(unittest.TestCase):
    @pytest.mark.sync
    def test_wait_for_context_synchronization_respects_wait_context_ids(self):
        agent = AgentBay(api_key="dummy")

        info_result = ContextInfoResult(
            request_id="req",
            success=True,
            context_status_data=[
                ContextStatusData(context_id="wait", path="/a", status="Success"),
                ContextStatusData(context_id="skip", path="/b", status="Running"),
            ],
            error_message="",
        )
        fake_context = _FakeContextManager([info_result])
        session = _FakeSession(fake_context)

        with patch("agentbay._sync.agentbay.time.sleep", new=_no_sleep):
            agent._wait_for_context_synchronization(
                session,
                wait_context_ids={"wait"},
            )

        self.assertEqual(fake_context.calls, 1)

