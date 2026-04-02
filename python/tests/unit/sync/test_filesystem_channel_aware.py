"""Unit tests for channel-aware filesystem chunking optimization.

Tests that:
- _is_using_link_url correctly detects HTTP (LinkUrl) vs MQTT channel
- read_file skips chunking (no get_file_info, single _read_file_chunk call) on HTTP channel
- write_file skips chunking (single _write_file_chunk call) on HTTP channel
- read_file preserves chunking on MQTT channel
- write_file preserves chunking on MQTT channel
"""

import unittest
from unittest.mock import MagicMock, MagicMock, patch

import pytest

from agentbay import FileSystem, BoolResult
from agentbay import (
    BinaryFileContentResult,
    FileContentResult,
    FileInfoResult,
)


class LinkUrlSession:
    """Mock session that simulates HTTP (LinkUrl) channel."""

    def __init__(self):
        self.api_key = "dummy_key"
        self.session_id = "dummy_session"
        self.client = MagicMock()
        self.call_mcp_tool = MagicMock()

    def get_api_key(self):
        return self.api_key

    def get_session_id(self):
        return self.session_id

    def get_client(self):
        return self.client

    def _get_link_url(self):
        return "https://link.example.com"

    def _get_token(self):
        return "dummy-token-12345"


class MqttSession:
    """Mock session that simulates MQTT channel (no LinkUrl)."""

    def __init__(self):
        self.api_key = "dummy_key"
        self.session_id = "dummy_session"
        self.client = MagicMock()
        self.call_mcp_tool = MagicMock()

    def get_api_key(self):
        return self.api_key

    def get_session_id(self):
        return self.session_id

    def get_client(self):
        return self.client

    def _get_link_url(self):
        return ""

    def _get_token(self):
        return ""


class TestIsUsingLinkUrl(unittest.TestCase):
    """Test _is_using_link_url channel detection method."""

    def test_returns_true_when_link_url_and_token_present(self):
        session = LinkUrlSession()
        fs = FileSystem(session)
        self.assertTrue(fs._is_using_link_url())

    def test_returns_false_when_link_url_empty(self):
        session = MqttSession()
        fs = FileSystem(session)
        self.assertFalse(fs._is_using_link_url())

    def test_returns_false_when_token_empty(self):
        session = LinkUrlSession()
        session._get_token = lambda: ""
        fs = FileSystem(session)
        self.assertFalse(fs._is_using_link_url())

    def test_returns_false_when_link_url_none(self):
        session = LinkUrlSession()
        session._get_link_url = lambda: None
        fs = FileSystem(session)
        self.assertFalse(fs._is_using_link_url())

    def test_returns_false_when_session_lacks_methods(self):
        """Session without _get_link_url/_get_token should return False."""
        session = MagicMock(spec=[])
        session.api_key = "dummy"
        session.session_id = "dummy"
        session.client = MagicMock()
        session.call_mcp_tool = MagicMock()
        fs = FileSystem(session)
        self.assertFalse(fs._is_using_link_url())


class TestReadFileHttpChannel(unittest.TestCase):
    """Test read_file on HTTP (LinkUrl) channel — should NOT chunk."""

    def setUp(self):
        self.session = LinkUrlSession()
        self.fs = FileSystem(self.session)

    @patch("agentbay._sync.filesystem.FileSystem._read_file_chunk")
    @patch("agentbay._sync.filesystem.FileSystem.get_file_info")
    def test_read_file_http_skips_get_file_info(self, mock_get_file_info, mock_read_chunk):
        """On HTTP channel, read_file should NOT call get_file_info."""
        mock_read_chunk.return_value = FileContentResult(
            request_id="req-1", success=True, content="hello world"
        )

        result = self.fs.read_file("/tmp/test.txt")

        mock_get_file_info.assert_not_called()
        self.assertTrue(result.success)
        self.assertEqual(result.content, "hello world")

    @patch("agentbay._sync.filesystem.FileSystem._read_file_chunk")
    def test_read_file_http_single_chunk_call(self, mock_read_chunk):
        """On HTTP channel, read_file should call _read_file_chunk exactly once."""
        mock_read_chunk.return_value = FileContentResult(
            request_id="req-1", success=True, content="x" * 100000
        )

        result = self.fs.read_file("/tmp/large.txt")

        mock_read_chunk.assert_called_once()
        self.assertTrue(result.success)
        self.assertEqual(len(result.content), 100000)

    @patch("agentbay._sync.filesystem.FileSystem._read_file_chunk")
    def test_read_file_http_binary_format(self, mock_read_chunk):
        """On HTTP channel, binary read_file should work without chunking."""
        mock_read_chunk.return_value = BinaryFileContentResult(
            request_id="req-1", success=True, content=b"\x00\x01\x02" * 30000
        )

        result = self.fs.read_file("/tmp/binary.bin", format="bytes")

        mock_read_chunk.assert_called_once()
        self.assertIsInstance(result, BinaryFileContentResult)
        self.assertTrue(result.success)
        self.assertEqual(len(result.content), 90000)

    @patch("agentbay._sync.filesystem.FileSystem._read_file_chunk")
    def test_read_file_http_error_handling(self, mock_read_chunk):
        """On HTTP channel, read_file should handle errors gracefully."""
        mock_read_chunk.return_value = FileContentResult(
            request_id="req-1", success=False, error_message="File not found"
        )

        result = self.fs.read_file("/tmp/nonexistent.txt")

        self.assertFalse(result.success)
        self.assertIn("File not found", result.error_message)

    @patch("agentbay._sync.filesystem.FileSystem._read_file_chunk")
    def test_read_file_http_exception_handling(self, mock_read_chunk):
        """On HTTP channel, read_file should handle exceptions gracefully."""
        mock_read_chunk.side_effect = Exception("Network error")

        result = self.fs.read_file("/tmp/test.txt")

        self.assertFalse(result.success)
        self.assertIn("Network error", result.error_message)


class TestWriteFileHttpChannel(unittest.TestCase):
    """Test write_file on HTTP (LinkUrl) channel — should NOT chunk."""

    def setUp(self):
        self.session = LinkUrlSession()
        self.fs = FileSystem(self.session)

    @patch("agentbay._sync.filesystem.FileSystem._write_file_chunk")
    def test_write_file_http_single_call(self, mock_write_chunk):
        """On HTTP channel, write_file should call _write_file_chunk exactly once."""
        mock_write_chunk.return_value = BoolResult(
            request_id="req-1", success=True, data=True
        )

        # Write content larger than MQTT chunk size (51KB)
        large_content = "x" * 100000
        result = self.fs.write_file("/tmp/large.txt", large_content)

        mock_write_chunk.assert_called_once_with("/tmp/large.txt", large_content, "overwrite")
        self.assertTrue(result.success)

    @patch("agentbay._sync.filesystem.FileSystem._write_file_chunk")
    def test_write_file_http_append_mode(self, mock_write_chunk):
        """On HTTP channel, write_file append mode should work without chunking."""
        mock_write_chunk.return_value = BoolResult(
            request_id="req-1", success=True, data=True
        )

        result = self.fs.write_file("/tmp/test.txt", "appended content", mode="append")

        mock_write_chunk.assert_called_once_with("/tmp/test.txt", "appended content", "append")
        self.assertTrue(result.success)

    @patch("agentbay._sync.filesystem.FileSystem._write_file_chunk")
    def test_write_file_http_error_handling(self, mock_write_chunk):
        """On HTTP channel, write_file should handle errors gracefully."""
        mock_write_chunk.return_value = BoolResult(
            request_id="req-1", success=False, error_message="Permission denied"
        )

        result = self.fs.write_file("/tmp/readonly.txt", "content")

        self.assertFalse(result.success)
        self.assertIn("Permission denied", result.error_message)

    @patch("agentbay._sync.filesystem.FileSystem._write_file_chunk")
    def test_write_file_http_exception_handling(self, mock_write_chunk):
        """On HTTP channel, write_file should handle exceptions gracefully."""
        mock_write_chunk.side_effect = Exception("Network error")

        result = self.fs.write_file("/tmp/test.txt", "content")

        self.assertFalse(result.success)
        self.assertIn("Network error", result.error_message)


class TestReadFileMqttChannel(unittest.TestCase):
    """Test read_file on MQTT channel — should preserve chunking."""

    def setUp(self):
        self.session = MqttSession()
        self.fs = FileSystem(self.session)

    @patch("agentbay._sync.filesystem.FileSystem._read_file_chunk")
    @patch("agentbay._sync.filesystem.FileSystem.get_file_info")
    def test_read_file_mqtt_calls_get_file_info(self, mock_get_file_info, mock_read_chunk):
        """On MQTT channel, read_file should call get_file_info first."""
        mock_get_file_info.return_value = FileInfoResult(
            request_id="req-1", success=True,
            file_info={"size": 1024, "isDirectory": False},
        )
        mock_read_chunk.return_value = FileContentResult(
            request_id="req-1", success=True, content="file content"
        )

        result = self.fs.read_file("/tmp/test.txt")

        mock_get_file_info.assert_called_once()
        self.assertTrue(result.success)

    @patch("agentbay._sync.filesystem.FileSystem._read_file_chunk")
    @patch("agentbay._sync.filesystem.FileSystem.get_file_info")
    def test_read_file_mqtt_chunks_large_file(self, mock_get_file_info, mock_read_chunk):
        """On MQTT channel, read_file should chunk large files."""
        file_size = 120 * 1024  # 120KB, needs multiple chunks at 50KB each
        mock_get_file_info.return_value = FileInfoResult(
            request_id="req-1", success=True,
            file_info={"size": file_size, "isDirectory": False},
        )

        chunk_size = 50 * 1024
        chunk_content = "a" * chunk_size

        mock_read_chunk.return_value = FileContentResult(
            request_id="req-1", success=True, content=chunk_content
        )

        result = self.fs.read_file("/tmp/large.txt")

        # Should have called _read_file_chunk multiple times (120KB / 50KB = 3 chunks)
        self.assertGreater(mock_read_chunk.call_count, 1)
        self.assertTrue(result.success)


class TestWriteFileMqttChannel(unittest.TestCase):
    """Test write_file on MQTT channel — should preserve chunking."""

    def setUp(self):
        self.session = MqttSession()
        self.fs = FileSystem(self.session)

    @patch("agentbay._sync.filesystem.FileSystem._write_file_chunk")
    def test_write_file_mqtt_chunks_large_content(self, mock_write_chunk):
        """On MQTT channel, write_file should chunk large content."""
        mock_write_chunk.return_value = BoolResult(
            request_id="req-1", success=True, data=True
        )

        # Write content larger than MAX_CONTENT_BYTES (51KB)
        large_content = "x" * (60 * 1024)
        result = self.fs.write_file("/tmp/large.txt", large_content)

        # Should have called _write_file_chunk multiple times
        self.assertGreater(mock_write_chunk.call_count, 1)
        self.assertTrue(result.success)

    @patch("agentbay._sync.filesystem.FileSystem._write_file_chunk")
    def test_write_file_mqtt_small_content_single_call(self, mock_write_chunk):
        """On MQTT channel, write_file with small content should use single call."""
        mock_write_chunk.return_value = BoolResult(
            request_id="req-1", success=True, data=True
        )

        result = self.fs.write_file("/tmp/small.txt", "small content")

        mock_write_chunk.assert_called_once()
        self.assertTrue(result.success)


if __name__ == "__main__":
    unittest.main()
