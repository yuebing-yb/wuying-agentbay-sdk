"""
Unit tests for the WebSocket push branch of watch_directory.

These tests validate the WS push monitoring mode (subscribe_file_change,
push event dispatch, reconnection catch-up, fallback to polling, and
cleanup on stop).
"""

import json
import threading
import time
import unittest
from typing import Any, Callable, Dict, List, Optional
from unittest.mock import MagicMock, MagicMock, Mock, call, patch

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


def _make_ws_client() -> MagicMock:
    """Build a mock WsClient with the methods used by watch_directory."""
    ws = MagicMock()
    ws.register_callback = MagicMock(return_value=MagicMock())
    ws.on_connection_state_change = MagicMock(return_value=None)

    handle = MagicMock()
    handle.wait_end_with_timeout = MagicMock(return_value={"phase": "end"})
    ws.call_stream = MagicMock(return_value=handle)
    ws.send_message = MagicMock()
    return ws


def _start_and_stop_thread(thread, *, start_sleep=1.5, stop_timeout=5.0):
    """Start a watch thread, wait, then stop it without blocking the event loop."""
    thread.start()
    time.sleep(start_sleep)
    thread.stop_event.set()
    thread.join(stop_timeout)


class TestWatchDirectoryWsPushActivation(unittest.TestCase):
    """Test that WS push mode is selected when all prerequisites are met."""

    @pytest.mark.sync
    def test_ws_push_selected_when_prerequisites_met(self):
        """When ws_url, token, server_name and running loop exist,
        the thread name should contain 'WS'."""
        session = _make_session()
        fs = FileSystem(session)
        mock_ws = _make_ws_client()
        session._get_ws_client = MagicMock(return_value=mock_ws)

        with patch.object(fs, "_get_file_change", new_callable=MagicMock) as mock_gfc:
            mock_gfc.return_value = FileChangeResult(success=True, events=[])

            stop = threading.Event()
            thread = fs.watch_directory("/watch", lambda e: None, stop_event=stop)
            self.assertIn("WS", thread.name)

            _start_and_stop_thread(thread)
            self.assertFalse(thread.is_alive())

    @pytest.mark.sync
    def test_polling_selected_when_no_ws_url(self):
        """Without ws_url, should fall back to polling."""
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
        """Without token, should fall back to polling."""
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
        """Without get_file_change in mcpTools, should fall back to polling."""
        session = _make_session()
        session.mcpTools = []
        fs = FileSystem(session)

        with patch.object(fs, "_get_file_change", new_callable=MagicMock) as mock_gfc:
            mock_gfc.return_value = FileChangeResult(success=True, events=[])

            stop = threading.Event()
            thread = fs.watch_directory("/watch", lambda e: None, stop_event=stop)
            self.assertNotIn("WS", thread.name)

            _start_and_stop_thread(thread, start_sleep=0.3)


class TestWatchDirectoryWsPushSubscription(unittest.TestCase):
    """Test the WS subscribe flow (call_stream + wait_end)."""

    @pytest.mark.sync
    def test_subscribe_called_with_correct_params(self):
        """call_stream should be invoked with subscribe_file_change method."""
        session = _make_session()
        fs = FileSystem(session)
        mock_ws = _make_ws_client()
        session._get_ws_client = MagicMock(return_value=mock_ws)

        with patch.object(fs, "_get_file_change", new_callable=MagicMock) as mock_gfc:
            mock_gfc.return_value = FileChangeResult(success=True, events=[])

            thread = fs.watch_directory(
                "/home/user/project", lambda e: None, stop_event=threading.Event()
            )
            _start_and_stop_thread(thread)

            mock_ws.call_stream.assert_called()
            call_args = mock_ws.call_stream.call_args
            self.assertEqual(call_args.kwargs["target"], "wuying_filesystem")
            data = call_args.kwargs["data"]
            self.assertEqual(data["method"], "subscribe_file_change")
            self.assertEqual(data["params"]["path"], "/home/user/project")

    @pytest.mark.sync
    def test_register_callback_called_with_server_name(self):
        """register_callback should be called on the ws_client for push events."""
        session = _make_session()
        fs = FileSystem(session)
        mock_ws = _make_ws_client()
        session._get_ws_client = MagicMock(return_value=mock_ws)

        with patch.object(fs, "_get_file_change", new_callable=MagicMock) as mock_gfc:
            mock_gfc.return_value = FileChangeResult(success=True, events=[])

            thread = fs.watch_directory("/watch", lambda e: None, stop_event=threading.Event())
            _start_and_stop_thread(thread)

            mock_ws.register_callback.assert_called_once()
            call_args = mock_ws.register_callback.call_args
            self.assertEqual(call_args[0][0], "wuying_filesystem")

    @pytest.mark.sync
    def test_on_connection_state_change_registered(self):
        """on_connection_state_change should be called to set up reconnect handler."""
        session = _make_session()
        fs = FileSystem(session)
        mock_ws = _make_ws_client()
        session._get_ws_client = MagicMock(return_value=mock_ws)

        with patch.object(fs, "_get_file_change", new_callable=MagicMock) as mock_gfc:
            mock_gfc.return_value = FileChangeResult(success=True, events=[])

            thread = fs.watch_directory("/watch", lambda e: None, stop_event=threading.Event())
            _start_and_stop_thread(thread)

            mock_ws.on_connection_state_change.assert_called_once()


class TestWatchDirectoryWsPushEventDispatch(unittest.TestCase):
    """Test that push events are correctly dispatched to user callback."""

    @pytest.mark.sync
    def test_push_event_dispatched_to_callback(self):
        """Simulated push events should be delivered to the user callback."""
        session = _make_session()
        fs = FileSystem(session)
        mock_ws = _make_ws_client()
        session._get_ws_client = MagicMock(return_value=mock_ws)

        received_events: List[FileChangeEvent] = []
        captured_push_handler: List[Callable] = []

        def capture_register_callback(target, cb):
            captured_push_handler.append(cb)
            return MagicMock()

        mock_ws.register_callback = MagicMock(side_effect=capture_register_callback)

        with patch.object(fs, "_get_file_change", new_callable=MagicMock) as mock_gfc:
            mock_gfc.return_value = FileChangeResult(success=True, events=[])

            thread = fs.watch_directory(
                "/watch", lambda e: received_events.extend(e), stop_event=threading.Event()
            )
            thread.start()
            time.sleep(1.5)

            self.assertEqual(len(captured_push_handler), 1)
            push_handler = captured_push_handler[0]

            push_handler({
                "data": {
                    "eventType": "file_change",
                    "path": "/watch",
                    "events": [
                        {"eventType": "create", "path": "/watch/new.txt", "pathType": "file"},
                        {"eventType": "modify", "path": "/watch/old.py", "pathType": "file"},
                    ]
                }
            })

            time.sleep(0.2)
            self.assertEqual(len(received_events), 2)
            self.assertEqual(received_events[0].event_type, "create")
            self.assertEqual(received_events[0].path, "/watch/new.txt")
            self.assertEqual(received_events[1].event_type, "modify")
            self.assertEqual(received_events[1].path, "/watch/old.py")

            thread.stop_event.set()
            thread.join(5.0)

    @pytest.mark.sync
    def test_push_event_wrong_path_ignored(self):
        """Push events for a different path should be ignored."""
        session = _make_session()
        fs = FileSystem(session)
        mock_ws = _make_ws_client()
        session._get_ws_client = MagicMock(return_value=mock_ws)

        received_events: List[FileChangeEvent] = []
        captured_push_handler: List[Callable] = []

        def capture_register_callback(target, cb):
            captured_push_handler.append(cb)
            return MagicMock()

        mock_ws.register_callback = MagicMock(side_effect=capture_register_callback)

        with patch.object(fs, "_get_file_change", new_callable=MagicMock) as mock_gfc:
            mock_gfc.return_value = FileChangeResult(success=True, events=[])

            thread = fs.watch_directory(
                "/watch", lambda e: received_events.extend(e), stop_event=threading.Event()
            )
            thread.start()
            time.sleep(1.5)

            push_handler = captured_push_handler[0]
            push_handler({
                "data": {
                    "eventType": "file_change",
                    "path": "/other_dir",
                    "events": [
                        {"eventType": "create", "path": "/other_dir/x.txt", "pathType": "file"},
                    ]
                }
            })

            time.sleep(0.2)
            self.assertEqual(len(received_events), 0)

            thread.stop_event.set()
            thread.join(5.0)

    @pytest.mark.sync
    def test_push_event_non_file_change_ignored(self):
        """Push events with eventType != 'file_change' should be ignored."""
        session = _make_session()
        fs = FileSystem(session)
        mock_ws = _make_ws_client()
        session._get_ws_client = MagicMock(return_value=mock_ws)

        received_events: List[FileChangeEvent] = []
        captured_push_handler: List[Callable] = []

        def capture_register_callback(target, cb):
            captured_push_handler.append(cb)
            return MagicMock()

        mock_ws.register_callback = MagicMock(side_effect=capture_register_callback)

        with patch.object(fs, "_get_file_change", new_callable=MagicMock) as mock_gfc:
            mock_gfc.return_value = FileChangeResult(success=True, events=[])

            thread = fs.watch_directory(
                "/watch", lambda e: received_events.extend(e), stop_event=threading.Event()
            )
            thread.start()
            time.sleep(1.5)

            push_handler = captured_push_handler[0]
            push_handler({
                "data": {
                    "eventType": "other_event_type",
                    "path": "/watch",
                    "events": [
                        {"eventType": "create", "path": "/watch/x.txt", "pathType": "file"},
                    ]
                }
            })

            time.sleep(0.2)
            self.assertEqual(len(received_events), 0)

            thread.stop_event.set()
            thread.join(5.0)

    @pytest.mark.sync
    def test_push_event_callback_exception_handled(self):
        """If user callback raises, the push handler should not crash."""
        session = _make_session()
        fs = FileSystem(session)
        mock_ws = _make_ws_client()
        session._get_ws_client = MagicMock(return_value=mock_ws)

        captured_push_handler: List[Callable] = []

        def capture_register_callback(target, cb):
            captured_push_handler.append(cb)
            return MagicMock()

        mock_ws.register_callback = MagicMock(side_effect=capture_register_callback)

        def failing_callback(events):
            raise RuntimeError("boom")

        with patch.object(fs, "_get_file_change", new_callable=MagicMock) as mock_gfc:
            mock_gfc.return_value = FileChangeResult(success=True, events=[])

            thread = fs.watch_directory(
                "/watch", failing_callback, stop_event=threading.Event()
            )
            thread.start()
            time.sleep(1.5)

            push_handler = captured_push_handler[0]
            push_handler({
                "data": {
                    "eventType": "file_change",
                    "path": "/watch",
                    "events": [
                        {"eventType": "create", "path": "/watch/x.txt", "pathType": "file"},
                    ]
                }
            })

            time.sleep(0.5)
            self.assertTrue(thread.is_alive(), "Thread should survive callback exception")

            thread.stop_event.set()
            thread.join(5.0)


class TestWatchDirectoryWsPushUnsubscribe(unittest.TestCase):
    """Test cleanup on stop: unsubscribe_file_change and callback unregister."""

    @pytest.mark.sync
    def test_unsubscribe_sent_on_stop(self):
        """send_message with unsubscribe_file_change should be called on stop."""
        session = _make_session()
        fs = FileSystem(session)
        mock_ws = _make_ws_client()
        session._get_ws_client = MagicMock(return_value=mock_ws)

        with patch.object(fs, "_get_file_change", new_callable=MagicMock) as mock_gfc:
            mock_gfc.return_value = FileChangeResult(success=True, events=[])

            thread = fs.watch_directory("/watch", lambda e: None, stop_event=threading.Event())
            _start_and_stop_thread(thread)

            mock_ws.send_message.assert_called()
            send_args = mock_ws.send_message.call_args
            self.assertEqual(send_args.kwargs["target"], "wuying_filesystem")
            data = send_args.kwargs["data"]
            self.assertEqual(data["method"], "unsubscribe_file_change")
            self.assertEqual(data["params"]["path"], "/watch")

    @pytest.mark.sync
    def test_push_callback_unregistered_on_stop(self):
        """The unsubscribe function from register_callback should be called on stop."""
        session = _make_session()
        fs = FileSystem(session)
        mock_ws = _make_ws_client()
        session._get_ws_client = MagicMock(return_value=mock_ws)

        unsubscribe_fn = MagicMock()
        mock_ws.register_callback = MagicMock(return_value=unsubscribe_fn)

        with patch.object(fs, "_get_file_change", new_callable=MagicMock) as mock_gfc:
            mock_gfc.return_value = FileChangeResult(success=True, events=[])

            thread = fs.watch_directory("/watch", lambda e: None, stop_event=threading.Event())
            _start_and_stop_thread(thread)

            unsubscribe_fn.assert_called()


class TestWatchDirectoryWsPushFallback(unittest.TestCase):
    """Test fallback to polling when WS subscribe fails."""

    @pytest.mark.sync
    def test_falls_back_to_polling_on_subscribe_error(self):
        """If WS subscribe raises, watch should fall back to polling
        and continue detecting changes via _get_file_change."""
        session = _make_session()
        fs = FileSystem(session)
        mock_ws = _make_ws_client()
        mock_ws.call_stream = MagicMock(side_effect=Exception("WS subscribe failed"))
        session._get_ws_client = MagicMock(return_value=mock_ws)

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
                "Should have polled multiple times in fallback mode"
            )
            self.assertGreater(
                len(received_events), 0,
                "Should have received events via polling fallback"
            )


class TestWatchDirectoryWsStateListenerCleanup(unittest.TestCase):
    """Test that state listeners are cleaned up when monitoring stops.

    This test validates the fix for the known issue where
    on_connection_state_change listeners accumulate across watch/stop cycles.
    """

    @pytest.mark.sync
    def test_state_listener_cleanup_on_stop(self):
        """The state listener should be removed when monitoring stops.

        Current implementation does NOT clean up the listener,
        so this test is expected to FAIL until the fix is applied.
        After the fix, on_connection_state_change should return an
        unsubscribe callable that is invoked during cleanup.
        """
        session = _make_session()
        fs = FileSystem(session)

        state_listeners: List[Callable] = []
        removed_listeners: List[Callable] = []

        mock_ws = _make_ws_client()
        session._get_ws_client = MagicMock(return_value=mock_ws)

        def mock_on_state_change(listener):
            state_listeners.append(listener)
            def _remove():
                removed_listeners.append(listener)
            return _remove

        mock_ws.on_connection_state_change = MagicMock(side_effect=mock_on_state_change)

        with patch.object(fs, "_get_file_change", new_callable=MagicMock) as mock_gfc:
            mock_gfc.return_value = FileChangeResult(success=True, events=[])

            thread = fs.watch_directory("/watch", lambda e: None, stop_event=threading.Event())
            _start_and_stop_thread(thread)

            self.assertEqual(len(state_listeners), 1, "Should register one state listener")
            self.assertEqual(
                len(removed_listeners), 1,
                "State listener should be removed on stop"
            )


if __name__ == "__main__":
    unittest.main()
