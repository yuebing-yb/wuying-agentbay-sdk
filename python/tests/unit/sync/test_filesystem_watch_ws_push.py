"""
Unit tests for the sync SDK watch_directory WS push fallback behavior.

The synchronous FileSystem.watch_directory always uses HTTP polling because
the WS push path requires a running asyncio event loop (via
asyncio.get_running_loop()), which is never available in pure sync context.

These tests verify:
  - Sync SDK always falls back to polling even when WS prerequisites are met
  - Polling correctly detects and reports file changes
  - Fallback behavior for missing WS prerequisites (ws_url, token, server_name)
"""

import threading
import time
import unittest
from typing import List
from unittest.mock import MagicMock, Mock, patch

import pytest

from agentbay import FileSystem, FileChangeEvent, FileChangeResult
from agentbay._common.models.mcp_tool import McpTool


def _make_session(
    *,
    ws_url: str = "wss://example.com/ws",
    token: str = "test-token",
    link_url: str = "",
    server_name: str = "wuying_filesystem",
    expired: bool = False,
) -> Mock:
    """Build a mock session with WS push prerequisites.

    link_url defaults to "" so that _poll_file_change falls through to
    the mockable _get_file_change path instead of httpx.post.
    """
    session = Mock()
    session.get_api_key.return_value = "test-api-key"
    session.get_session_id.return_value = "test-session-id"
    session._is_expired.return_value = expired
    session.ws_url = ws_url
    session.token = token
    session.link_url = link_url
    session.mcpTools = [McpTool(name="get_file_change", server=server_name)]
    return session


def _start_and_stop_thread(thread, *, start_sleep=1.5, stop_timeout=5.0):
    """Start a watch thread, wait, then stop it."""
    thread.start()
    time.sleep(start_sleep)
    thread.stop_event.set()
    thread.join(stop_timeout)


class TestSyncWatchAlwaysUsesPolling(unittest.TestCase):
    """Verify that the sync SDK always uses polling, never WS push."""

    @pytest.mark.sync
    def test_always_polling_even_with_ws_prerequisites(self):
        """Even when ws_url, token, and server_name are all present,
        the sync SDK should use polling because there is no running
        asyncio event loop."""
        session = _make_session()
        fs = FileSystem(session)

        with patch.object(fs, "_get_file_change", new_callable=MagicMock) as mock_gfc:
            mock_gfc.return_value = FileChangeResult(success=True, events=[])

            stop = threading.Event()
            thread = fs.watch_directory("/watch", lambda e: None, stop_event=stop)
            self.assertNotIn("WS", thread.name,
                             "Sync SDK should never use WS push thread naming")

            _start_and_stop_thread(thread, start_sleep=0.3)
            self.assertFalse(thread.is_alive())

    @pytest.mark.sync
    def test_polling_selected_when_no_ws_url(self):
        """Without ws_url, should use polling."""
        session = _make_session(ws_url="")
        fs = FileSystem(session)

        with patch.object(fs, "_get_file_change", new_callable=MagicMock) as mock_gfc:
            mock_gfc.return_value = FileChangeResult(success=True, events=[])

            stop = threading.Event()
            thread = fs.watch_directory("/watch", lambda e: None, stop_event=stop)
            self.assertNotIn("WS", thread.name)

            _start_and_stop_thread(thread, start_sleep=0.3)

    @pytest.mark.sync
    def test_polling_selected_when_no_token(self):
        """Without token, should use polling."""
        session = _make_session(token="")
        fs = FileSystem(session)

        with patch.object(fs, "_get_file_change", new_callable=MagicMock) as mock_gfc:
            mock_gfc.return_value = FileChangeResult(success=True, events=[])

            stop = threading.Event()
            thread = fs.watch_directory("/watch", lambda e: None, stop_event=stop)
            self.assertNotIn("WS", thread.name)

            _start_and_stop_thread(thread, start_sleep=0.3)

    @pytest.mark.sync
    def test_polling_selected_when_no_server_name(self):
        """Without get_file_change in mcpTools, should use polling."""
        session = _make_session()
        session.mcpTools = []
        fs = FileSystem(session)

        with patch.object(fs, "_get_file_change", new_callable=MagicMock) as mock_gfc:
            mock_gfc.return_value = FileChangeResult(success=True, events=[])

            stop = threading.Event()
            thread = fs.watch_directory("/watch", lambda e: None, stop_event=stop)
            self.assertNotIn("WS", thread.name)

            _start_and_stop_thread(thread, start_sleep=0.3)


class TestSyncPollingBehavior(unittest.TestCase):
    """Verify polling mode correctly detects and reports file changes."""

    @pytest.mark.sync
    def test_polling_detects_changes(self):
        """Polling should call _get_file_change and deliver events
        to the user callback."""
        session = _make_session()
        fs = FileSystem(session)

        received_events: List[FileChangeEvent] = []
        poll_count = 0

        with patch.object(fs, "_get_file_change", new_callable=MagicMock) as mock_gfc:
            def gfc_side_effect(path):
                nonlocal poll_count
                poll_count += 1
                if poll_count > 2:
                    return FileChangeResult(
                        success=True,
                        events=[FileChangeEvent("create", "/watch/new.txt", "file")],
                    )
                return FileChangeResult(success=True, events=[])

            mock_gfc.side_effect = gfc_side_effect

            thread = fs.watch_directory(
                "/watch",
                lambda e: received_events.extend(e),
                interval=0.1,
                stop_event=threading.Event(),
            )
            thread.start()
            time.sleep(3.0)

            thread.stop_event.set()
            thread.join(5.0)

            self.assertGreater(
                poll_count, 2,
                "Should have polled multiple times"
            )
            self.assertGreater(
                len(received_events), 0,
                "Should have received events via polling"
            )

    @pytest.mark.sync
    def test_polling_callback_exception_handled(self):
        """If user callback raises, the polling thread should not crash."""
        session = _make_session()
        fs = FileSystem(session)

        call_count = 0

        def failing_callback(events):
            raise RuntimeError("boom")

        with patch.object(fs, "_get_file_change", new_callable=MagicMock) as mock_gfc:
            def gfc_side_effect(path):
                nonlocal call_count
                call_count += 1
                return FileChangeResult(
                    success=True,
                    events=[FileChangeEvent("create", "/watch/x.txt", "file")],
                )

            mock_gfc.side_effect = gfc_side_effect

            thread = fs.watch_directory(
                "/watch", failing_callback, interval=0.2, stop_event=threading.Event()
            )
            thread.start()
            time.sleep(1.5)

            self.assertTrue(thread.is_alive(), "Thread should survive callback exception")

            thread.stop_event.set()
            thread.join(5.0)

            self.assertGreater(call_count, 1,
                               "Should have continued polling after callback exception")

    @pytest.mark.sync
    def test_ready_event_set_after_baseline(self):
        """ready_event should be set after the first poll (baseline)."""
        session = _make_session()
        fs = FileSystem(session)

        with patch.object(fs, "_get_file_change", new_callable=MagicMock) as mock_gfc:
            mock_gfc.return_value = FileChangeResult(success=True, events=[])

            thread = fs.watch_directory("/watch", lambda e: None, stop_event=threading.Event())
            thread.start()

            signaled = thread.ready_event.wait(timeout=5.0)
            self.assertTrue(signaled, "ready_event should be set after baseline poll")

            thread.stop_event.set()
            thread.join(5.0)

    @pytest.mark.sync
    def test_stop_event_terminates_polling(self):
        """Setting stop_event should terminate the polling thread."""
        session = _make_session()
        fs = FileSystem(session)

        with patch.object(fs, "_get_file_change", new_callable=MagicMock) as mock_gfc:
            mock_gfc.return_value = FileChangeResult(success=True, events=[])

            stop = threading.Event()
            thread = fs.watch_directory("/watch", lambda e: None, stop_event=stop)
            thread.start()

            thread.ready_event.wait(timeout=5.0)
            stop.set()
            thread.join(5.0)

            self.assertFalse(thread.is_alive(), "Thread should terminate after stop_event")


if __name__ == "__main__":
    unittest.main()
