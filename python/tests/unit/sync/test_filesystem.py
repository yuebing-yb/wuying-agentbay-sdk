import unittest
import pytest
from unittest.mock import MagicMock, MagicMock, patch

from agentbay import McpToolResult, OperationResult
from agentbay import FileSystem, BoolResult
from agentbay import (
    BinaryFileContentResult,
    DirectoryListResult,
    FileContentResult,
    FileInfoResult,
    FileSearchResult,
    MultipleFileContentResult,
)


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


class TestAsyncFileSystem(unittest.TestCase):
    def setUp(self):
        self.session = DummySession()
        self.fs = FileSystem(self.session)

    @patch("agentbay._sync.filesystem.FileSystem.get_file_info")
    @patch("agentbay._sync.filesystem.FileSystem._read_file_chunk")
    @pytest.mark.sync

    def test_read_file_success(self, mock_read_file_chunk, mock_get_file_info):
        """
        Test read_file method with successful response (small file).
        """
        # Mock file info for small file
        file_info_result = FileInfoResult(
            request_id="request-123",
            success=True,
            file_info={"size": 1024, "isDirectory": False},  # 1KB file
        )
        mock_get_file_info.return_value = file_info_result

        # Mock single chunk read
        mock_read_file_chunk.return_value = FileContentResult(
            request_id="request-123", success=True, content="file content"
        )

        result = self.fs.read_file("/path/to/file.txt")
        self.assertIsInstance(result, FileContentResult)
        self.assertTrue(result.success)
        self.assertEqual(result.content, "file content")
        self.assertEqual(result.request_id, "request-123")

    @patch("agentbay._sync.filesystem.FileSystem.get_file_info")
    @pytest.mark.sync

    def test_read_file_get_info_error(self, mock_get_file_info):
        """
        Test read_file method with error in get_file_info.
        """
        error_result = FileInfoResult(
            request_id="request-123",
            success=False,
            error_message="Error in response: some error message",
        )
        mock_get_file_info.return_value = error_result

        result = self.fs.read_file("/path/to/file.txt")
        self.assertIsInstance(result, FileContentResult)
        self.assertFalse(result.success)
        self.assertEqual(result.request_id, "request-123")
        self.assertEqual(result.error_message, "Error in response: some error message")
        self.assertEqual(result.content, "")

    @patch("agentbay._sync.filesystem.FileSystem.get_file_info")
    @patch("agentbay._sync.filesystem.FileSystem._read_file_chunk")
    @pytest.mark.sync

    def test_read_file_chunk_error(
        self, mock_read_file_chunk, mock_get_file_info
    ):
        """
        Test read_file method with error in chunk reading.
        """
        # Mock file info for small file
        file_info_result = FileInfoResult(
            request_id="request-123",
            success=True,
            file_info={"size": 1024, "isDirectory": False},
        )
        mock_get_file_info.return_value = file_info_result

        # Mock chunk read error
        mock_read_file_chunk.return_value = FileContentResult(
            request_id="request-123",
            success=False,
            error_message="Invalid response body",
        )

        result = self.fs.read_file("/path/to/file.txt")
        self.assertIsInstance(result, FileContentResult)
        self.assertFalse(result.success)
        self.assertEqual(result.request_id, "request-123")
        self.assertEqual(result.error_message, "Invalid response body")

    @pytest.mark.sync


    def test_create_directory_success(self):
        """
        Test create_directory method with successful response.
        """
        from agentbay import McpToolResult

        mock_result = McpToolResult(request_id="request-123", success=True, data="True")
        self.session.call_mcp_tool.return_value = mock_result

        result = self.fs.create_directory("/path/to/directory")
        self.assertIsInstance(result, BoolResult)
        self.assertTrue(result.success)
        self.assertEqual(result.request_id, "request-123")
        self.assertTrue(result.data)

    @pytest.mark.sync


    def test_create_directory_error(self):
        """
        Test create_directory method with error response.
        """
        # Create an OperationResult object with error_message and request_id
        mock_result = McpToolResult(
            request_id="request-123",
            success=False,
            error_message="Directory creation failed",
        )
        self.session.call_mcp_tool.return_value = mock_result

        result = self.fs.create_directory("/path/to/directory")
        self.assertIsInstance(result, BoolResult)
        self.assertFalse(result.success)
        self.assertEqual(result.request_id, "request-123")
        self.assertEqual(result.error_message, "Directory creation failed")

    @pytest.mark.sync
    def test_delete_file_success(self):
        """
        Test delete_file method with successful response.
        """
        mock_result = McpToolResult(request_id="request-123", success=True, data="True")
        self.session.call_mcp_tool.return_value = mock_result

        result = self.fs.delete_file("/path/to/file.txt")
        self.assertIsInstance(result, BoolResult)
        self.assertTrue(result.success)
        self.assertEqual(result.request_id, "request-123")
        self.assertTrue(result.data)
        self.session.call_mcp_tool.assert_called_once_with(
            "delete_file", {"path": "/path/to/file.txt"}
        )

    @patch("agentbay._sync.filesystem.FileSystem.get_file_info")
    @pytest.mark.sync
    def test_read_alias_calls_read_file(self, mock_get_file_info):
        file_info_result = FileInfoResult(
            request_id="request-123",
            success=True,
            file_info={"size": 0, "isDirectory": False},
        )
        mock_get_file_info.return_value = file_info_result

        result = self.fs.read("/path/to/file.txt")
        self.assertIsInstance(result, FileContentResult)
        self.assertTrue(result.success)

    @patch("agentbay._sync.filesystem.FileSystem._write_file_chunk")
    @pytest.mark.sync
    def test_write_alias_calls_write_file(self, mock_write_file_chunk):
        mock_write_file_chunk.return_value = BoolResult(
            request_id="request-123", success=True, data=True
        )
        result = self.fs.write("/path/to/file.txt", "content")
        self.assertIsInstance(result, BoolResult)
        self.assertTrue(result.success)

    @pytest.mark.sync
    def test_list_alias_calls_list_directory(self):
        mock_result = McpToolResult(
            request_id="request-123",
            success=True,
            data="[FILE] a.txt",
        )
        self.session.call_mcp_tool.return_value = mock_result
        result = self.fs.list("/path/to")
        self.assertIsInstance(result, DirectoryListResult)
        self.assertTrue(result.success)

    @pytest.mark.sync
    def test_delete_alias_calls_delete_file(self):
        mock_result = McpToolResult(request_id="request-123", success=True, data="True")
        self.session.call_mcp_tool.return_value = mock_result
        result = self.fs.delete("/path/to/file.txt")
        self.assertIsInstance(result, BoolResult)
        self.assertTrue(result.success)

    @pytest.mark.sync
    def test_delete_file_error(self):
        """
        Test delete_file method with error response.
        """
        mock_result = McpToolResult(
            request_id="request-123",
            success=False,
            error_message="Delete failed",
        )
        self.session.call_mcp_tool.return_value = mock_result

        result = self.fs.delete_file("/path/to/file.txt")
        self.assertIsInstance(result, BoolResult)
        self.assertFalse(result.success)
        self.assertEqual(result.request_id, "request-123")
        self.assertEqual(result.error_message, "Delete failed")

    @pytest.mark.sync


    def test_edit_file_success(self):
        """
        Test edit_file method with successful response.
        """
        from agentbay import McpToolResult

        mock_result = McpToolResult(request_id="request-123", success=True, data="True")
        self.session.call_mcp_tool.return_value = mock_result

        result = self.fs.edit_file(
            "/path/to/file.txt", [{"oldText": "foo", "newText": "bar"}]
        )
        self.assertIsInstance(result, BoolResult)
        self.assertTrue(result.success)
        self.assertEqual(result.request_id, "request-123")
        self.assertTrue(result.data)

    @pytest.mark.sync


    def test_edit_file_error(self):
        """
        Test edit_file method with error response.
        """
        from agentbay import McpToolResult

        mock_result = McpToolResult(
            request_id="request-123",
            success=False,
            error_message="Edit failed",
        )
        self.session.call_mcp_tool.return_value = mock_result

        result = self.fs.edit_file(
            "/path/to/file.txt", [{"oldText": "foo", "newText": "bar"}]
        )
        self.assertIsInstance(result, BoolResult)
        self.assertFalse(result.success)
        self.assertEqual(result.request_id, "request-123")
        self.assertEqual(result.error_message, "Edit failed")

    @patch("agentbay._sync.filesystem.FileSystem._write_file_chunk")
    @pytest.mark.sync

    def test_write_file_success(self, mock_write_file_chunk):
        """
        Test write_file method with successful response (small content).
        """
        mock_write_file_chunk.return_value = BoolResult(
            request_id="request-123", success=True, data=True
        )

        result = self.fs.write_file(
            "/path/to/file.txt", "content to write", "overwrite"
        )
        self.assertIsInstance(result, BoolResult)
        self.assertTrue(result.success)
        self.assertEqual(result.request_id, "request-123")
        self.assertTrue(result.data)
        mock_write_file_chunk.assert_called_once_with(
            "/path/to/file.txt", "content to write", "overwrite"
        )

    @patch("agentbay._sync.filesystem.FileSystem._write_file_chunk")
    @pytest.mark.sync

    def test_write_file_error(self, mock_write_file_chunk):
        """
        Test write_file method with error response.
        """
        mock_write_file_chunk.return_value = BoolResult(
            request_id="request-123",
            success=False,
            error_message="Write failed",
        )

        result = self.fs.write_file(
            "/path/to/file.txt", "content to write", "overwrite"
        )
        self.assertIsInstance(result, BoolResult)
        self.assertFalse(result.success)
        self.assertEqual(result.request_id, "request-123")
        self.assertEqual(result.error_message, "Write failed")

    @pytest.mark.sync


    def test_get_file_info_success(self):
        """
        Test get_file_info method with successful response.
        """
        from agentbay import McpToolResult

        mock_result = McpToolResult(
            request_id="request-123",
            success=True,
            data="name: test.txt\nsize: 100\nmodified: 2023-01-01T12:00:00Z\nisDirectory: false",
        )
        self.session.call_mcp_tool.return_value = mock_result

        result = self.fs.get_file_info("/path/to/file.txt")
        self.assertIsInstance(result, FileInfoResult)
        self.assertTrue(result.success)
        self.assertEqual(result.request_id, "request-123")
        self.assertEqual(result.file_info["name"], "test.txt")
        self.assertEqual(result.file_info["size"], 100)
        self.assertEqual(result.file_info["modified"], "2023-01-01T12:00:00Z")
        self.assertEqual(result.file_info["isDirectory"], False)

    @pytest.mark.sync


    def test_get_file_info_error(self):
        """
        Test get_file_info method with error response.
        """
        from agentbay import McpToolResult

        mock_result = McpToolResult(
            request_id="request-123",
            success=False,
            error_message="File not found",
        )
        self.session.call_mcp_tool.return_value = mock_result

        result = self.fs.get_file_info("/path/to/file.txt")
        self.assertIsInstance(result, FileInfoResult)
        self.assertFalse(result.success)
        self.assertEqual(result.request_id, "request-123")
        self.assertEqual(result.error_message, "File not found")

    @pytest.mark.sync


    def test_list_directory_success(self):
        """
        Test list_directory method with successful response.
        """
        from agentbay import McpToolResult

        mock_result = McpToolResult(
            request_id="request-123",
            success=True,
            data="[FILE] file1.txt\n[DIR] dir1\n[FILE] file2.txt",
        )
        self.session.call_mcp_tool.return_value = mock_result

        result = self.fs.list_directory("/path/to/directory")
        self.assertIsInstance(result, DirectoryListResult)
        self.assertTrue(result.success)
        self.assertEqual(result.request_id, "request-123")
        self.assertEqual(len(result.entries), 3)
        self.assertEqual(result.entries[0].name, "file1.txt")
        self.assertEqual(result.entries[0].is_directory, False)
        self.assertEqual(result.entries[1].name, "dir1")
        self.assertEqual(result.entries[1].is_directory, True)
        self.assertEqual(result.entries[2].name, "file2.txt")
        self.assertEqual(result.entries[2].is_directory, False)

    @pytest.mark.sync


    def test_list_directory_error(self):
        """
        Test list_directory method with error response.
        """
        from agentbay import McpToolResult

        mock_result = McpToolResult(
            request_id="request-123",
            success=False,
            error_message="Directory not found",
        )
        self.session.call_mcp_tool.return_value = mock_result

        result = self.fs.list_directory("/path/to/directory")
        self.assertIsInstance(result, DirectoryListResult)
        self.assertFalse(result.success)
        self.assertEqual(result.request_id, "request-123")
        self.assertEqual(result.error_message, "Directory not found")
        self.assertEqual(result.entries, [])

    @pytest.mark.sync


    def test_move_file_success(self):
        """
        Test move_file method with successful response.
        """
        from agentbay import McpToolResult

        mock_result = McpToolResult(request_id="request-123", success=True, data="True")
        self.session.call_mcp_tool.return_value = mock_result

        result = self.fs.move_file("/path/to/source.txt", "/path/to/dest.txt")
        self.assertIsInstance(result, BoolResult)
        self.assertTrue(result.success)
        self.assertEqual(result.request_id, "request-123")
        self.assertTrue(result.data)

    @pytest.mark.sync


    def test_move_file_error(self):
        """
        Test move_file method with error response.
        """
        from agentbay import McpToolResult

        mock_result = McpToolResult(
            request_id="request-123",
            success=False,
            error_message="Move operation failed",
        )
        self.session.call_mcp_tool.return_value = mock_result

        result = self.fs.move_file("/path/to/source.txt", "/path/to/dest.txt")
        self.assertIsInstance(result, BoolResult)
        self.assertFalse(result.success)
        self.assertEqual(result.request_id, "request-123")
        self.assertEqual(result.error_message, "Move operation failed")

    @pytest.mark.sync


    def test_read_multiple_files_success(self):
        """
        Test read_multiple_files method with successful response.
        """
        from agentbay import McpToolResult

        mock_result = McpToolResult(
            request_id="request-123",
            success=True,
            data="file1.txt:\nFile 1 content\n---\nfile2.txt:\nFile 2 content\n---",
        )
        self.session.call_mcp_tool.return_value = mock_result

        result = self.fs.read_multiple_files(
            ["/path/to/file1.txt", "/path/to/file2.txt"]
        )
        self.assertIsInstance(result, MultipleFileContentResult)
        self.assertTrue(result.success)
        self.assertEqual(result.request_id, "request-123")
        self.assertEqual(len(result.contents), 2)
        self.assertEqual(result.contents["file1.txt"], "File 1 content")
        self.assertEqual(result.contents["file2.txt"], "File 2 content")

    @pytest.mark.sync


    def test_search_files_success(self):
        """
        Test search_files method with successful response.
        """
        from agentbay import McpToolResult

        mock_result = McpToolResult(
            request_id="request-123",
            success=True,
            data="/path/to/file1.txt\n/path/to/file2.txt",
        )
        self.session.call_mcp_tool.return_value = mock_result

        result = self.fs.search_files("/path/to", "pattern")
        self.assertIsInstance(result, FileSearchResult)
        self.assertTrue(result.success)
        self.assertEqual(result.request_id, "request-123")
        self.assertEqual(len(result.matches), 2)
        self.assertEqual(result.matches[0], "/path/to/file1.txt")
        self.assertEqual(result.matches[1], "/path/to/file2.txt")

    @pytest.mark.sync


    def test_search_files_with_exclude(self):
        """
        Test search_files method with exclude patterns.
        """
        from agentbay import McpToolResult

        mock_result = McpToolResult(
            request_id="request-123", success=True, data="/path/to/file1.txt"
        )
        self.session.call_mcp_tool.return_value = mock_result

        result = self.fs.search_files(
            "/path/to", "pattern", exclude_patterns=["*.py", "node_modules"]
        )
        self.assertIsInstance(result, FileSearchResult)
        self.assertTrue(result.success)
        self.assertEqual(result.request_id, "request-123")
        self.assertEqual(len(result.matches), 1)
        self.assertEqual(result.matches[0], "/path/to/file1.txt")

    @patch("agentbay._sync.filesystem.FileSystem.get_file_info")
    @patch("agentbay._sync.filesystem.FileSystem._read_file_chunk")
    @pytest.mark.sync

    def test_read_file_large_success(
        self, mock_read_file_chunk, mock_get_file_info
    ):
        """
        Test read_file method with large file (automatic chunking).
        """
        # Mock file info
        file_info_result = FileInfoResult(
            request_id="request-123",
            success=True,
            file_info={"size": 150 * 1024, "isDirectory": False},  # 150KB file
        )
        mock_get_file_info.return_value = file_info_result

        # Mock chunked reads (3 chunks of 50KB each)
        mock_read_file_chunk.side_effect = [
            FileContentResult(
                request_id="request-123-1", success=True, content="chunk1"
            ),
            FileContentResult(
                request_id="request-123-2", success=True, content="chunk2"
            ),
            FileContentResult(
                request_id="request-123-3", success=True, content="chunk3"
            ),
        ]

        result = self.fs.read_file("/path/to/large_file.txt")
        self.assertIsInstance(result, FileContentResult)
        self.assertTrue(result.success)
        self.assertEqual(result.content, "chunk1chunk2chunk3")
        mock_get_file_info.assert_called_once()
        self.assertEqual(mock_read_file_chunk.call_count, 3)

    @patch("agentbay._sync.filesystem.FileSystem.get_file_info")
    @pytest.mark.sync

    def test_read_file_error(self, mock_get_file_info):
        """
        Test read_file method with error in get_file_info.
        """
        error_result = FileInfoResult(
            request_id="request-123",
            success=False,
            error_message="File not found",
        )
        mock_get_file_info.return_value = error_result

        result = self.fs.read_file("/path/to/large_file.txt")
        self.assertIsInstance(result, FileContentResult)
        self.assertFalse(result.success)
        self.assertEqual(result.error_message, "File not found")
        mock_get_file_info.assert_called_once()

    @patch("agentbay._sync.filesystem.FileSystem._write_file_chunk")
    @pytest.mark.sync

    def test_write_file_large_success(self, mock_write_file_chunk):
        """
        Test write_file method with large content (automatic chunking).
        """
        mock_write_file_chunk.side_effect = [
            BoolResult(request_id="request-123-1", success=True, data=True),
            BoolResult(request_id="request-123-2", success=True, data=True),
            BoolResult(request_id="request-123-3", success=True, data=True),
        ]

        content = "a" * (150 * 1024)  # 150KB content
        result = self.fs.write_file("/path/to/large_file.txt", content)
        self.assertIsInstance(result, BoolResult)
        self.assertTrue(result.success)
        self.assertTrue(result.data)
        self.assertEqual(mock_write_file_chunk.call_count, 3)

        # Verify the calls (first overwrite, then appends)
        calls = mock_write_file_chunk.call_args_list
        self.assertEqual(calls[0][0][2], "overwrite")  # First call mode
        self.assertEqual(calls[1][0][2], "append")  # Second call mode
        self.assertEqual(calls[2][0][2], "append")  # Third call mode

    @patch("agentbay._sync.filesystem.FileSystem._write_file_chunk")
    @pytest.mark.sync

    def test_write_file_small_content(self, mock_write_file_chunk):
        """
        Test write_file method with content smaller than chunk size.
        """
        mock_write_file_chunk.return_value = BoolResult(
            request_id="request-123", success=True, data=True
        )

        content = "small content"
        result = self.fs.write_file("/path/to/file.txt", content)
        self.assertIsInstance(result, BoolResult)
        self.assertTrue(result.success)
        self.assertTrue(result.data)
        mock_write_file_chunk.assert_called_once_with(
            "/path/to/file.txt", content, "overwrite"
        )

    @patch("agentbay._sync.filesystem.FileSystem._write_file_chunk")
    @pytest.mark.sync

    def test_write_file_large_error(self, mock_write_file_chunk):
        """
        Test write_file method with error in first write.
        """
        mock_write_file_chunk.return_value = BoolResult(
            request_id="request-123",
            success=False,
            error_message="Write error",
        )

        content = "a" * (100 * 1024)  # 100KB content
        result = self.fs.write_file("/path/to/large_file.txt", content)
        self.assertIsInstance(result, BoolResult)
        self.assertFalse(result.success)
        self.assertEqual(result.error_message, "Write error")
        mock_write_file_chunk.assert_called_once()

    @patch("agentbay._sync.filesystem.FileSystem._write_file_chunk")
    @pytest.mark.sync

    def test_write_file_invalid_mode(self, mock_write_file_chunk):
        """
        Test write_file method with invalid mode.
        """
        mock_write_file_chunk.return_value = BoolResult(
            request_id="",
            success=False,
            error_message="Invalid write mode: invalid_mode. Must be 'overwrite' or 'append'.",
        )

        result = self.fs.write_file(
            "/path/to/file.txt", "content", "invalid_mode"
        )
        self.assertIsInstance(result, BoolResult)
        self.assertFalse(result.success)
        self.assertIn("Invalid write mode", result.error_message)

    @patch("agentbay._sync.filesystem.FileSystem.get_file_info")
    @patch("agentbay._sync.filesystem.FileSystem._read_file_chunk")
    @pytest.mark.sync
    def test_read_file_binary_format_success(
        self, mock_read_file_chunk, mock_get_file_info
    ):
        """
        Test read_file method with format='bytes' for binary files.
        """
        import base64

        # Mock file info for binary file
        file_info_result = FileInfoResult(
            request_id="request-123",
            success=True,
            file_info={"size": 1024, "isDirectory": False},  # 1KB file
        )
        mock_get_file_info.return_value = file_info_result

        # Mock binary chunk read - backend returns base64, SDK decodes to bytes
        binary_data = b'\xff\xd8\xff\xe0\x00\x10JFIF'  # JPEG header
        base64_data = base64.b64encode(binary_data).decode('ascii')
        
        mock_read_file_chunk.return_value = BinaryFileContentResult(
            request_id="request-123",
            success=True,
            content=binary_data,
            size=len(binary_data),
        )

        result = self.fs.read_file("/path/to/image.jpeg", format="bytes")
        self.assertIsInstance(result, BinaryFileContentResult)
        self.assertTrue(result.success)
        self.assertIsInstance(result.content, bytes)
        self.assertEqual(result.content, binary_data)
        self.assertEqual(result.request_id, "request-123")
        # Verify JPEG header
        self.assertEqual(result.content[:3], b'\xff\xd8\xff')

    @patch("agentbay._sync.filesystem.FileSystem.get_file_info")
    @patch("agentbay._sync.filesystem.FileSystem._read_file_chunk")
    @pytest.mark.sync
    def test_read_file_binary_format_large_file(
        self, mock_read_file_chunk, mock_get_file_info
    ):
        """
        Test read_file method with format='bytes' for large binary files (chunking).
        """
        import base64

        # Mock file info for large binary file (150KB)
        file_info_result = FileInfoResult(
            request_id="request-123",
            success=True,
            file_info={"size": 150 * 1024, "isDirectory": False},
        )
        mock_get_file_info.return_value = file_info_result

        # Mock chunked binary reads (3 chunks of 50KB each)
        chunk1 = b'\x00' * (50 * 1024)
        chunk2 = b'\x01' * (50 * 1024)
        chunk3 = b'\x02' * (50 * 1024)
        
        mock_read_file_chunk.side_effect = [
            BinaryFileContentResult(
                request_id="request-123-1", success=True, content=chunk1
            ),
            BinaryFileContentResult(
                request_id="request-123-2", success=True, content=chunk2
            ),
            BinaryFileContentResult(
                request_id="request-123-3", success=True, content=chunk3
            ),
        ]

        result = self.fs.read_file("/path/to/large_binary.bin", format="bytes")
        self.assertIsInstance(result, BinaryFileContentResult)
        self.assertTrue(result.success)
        self.assertIsInstance(result.content, bytes)
        # Verify all chunks are concatenated correctly
        expected_content = chunk1 + chunk2 + chunk3
        self.assertEqual(result.content, expected_content)
        self.assertEqual(len(result.content), 150 * 1024)
        self.assertEqual(mock_read_file_chunk.call_count, 3)

    @patch("agentbay._sync.filesystem.FileSystem.get_file_info")
    @pytest.mark.sync
    def test_read_file_binary_format_get_info_error(self, mock_get_file_info):
        """
        Test read_file method with format='bytes' when get_file_info fails.
        """
        error_result = FileInfoResult(
            request_id="request-123",
            success=False,
            error_message="File not found",
        )
        mock_get_file_info.return_value = error_result

        result = self.fs.read_file("/path/to/image.jpeg", format="bytes")
        self.assertIsInstance(result, BinaryFileContentResult)
        self.assertFalse(result.success)
        self.assertEqual(result.request_id, "request-123")
        self.assertEqual(result.error_message, "File not found")
        self.assertEqual(result.content, b"")

    @patch("agentbay._sync.filesystem.FileSystem.get_file_info")
    @patch("agentbay._sync.filesystem.FileSystem._read_file_chunk")
    @pytest.mark.sync
    def test_read_file_binary_format_chunk_error(
        self, mock_read_file_chunk, mock_get_file_info
    ):
        """
        Test read_file method with format='bytes' when chunk reading fails.
        """
        # Mock file info
        file_info_result = FileInfoResult(
            request_id="request-123",
            success=True,
            file_info={"size": 1024, "isDirectory": False},
        )
        mock_get_file_info.return_value = file_info_result

        # Mock chunk read error
        mock_read_file_chunk.return_value = BinaryFileContentResult(
            request_id="request-123",
            success=False,
            content=b"",
            error_message="Failed to decode base64",
        )

        result = self.fs.read_file("/path/to/image.jpeg", format="bytes")
        self.assertIsInstance(result, BinaryFileContentResult)
        self.assertFalse(result.success)
        self.assertEqual(result.error_message, "Failed to decode base64")
        self.assertEqual(result.content, b"")

    @patch("agentbay._sync.filesystem.FileSystem.get_file_info")
    @pytest.mark.sync
    def test_read_file_binary_format_empty_file(self, mock_get_file_info):
        """
        Test read_file method with format='bytes' for empty file.
        """
        file_info_result = FileInfoResult(
            request_id="request-123",
            success=True,
            file_info={"size": 0, "isDirectory": False},
        )
        mock_get_file_info.return_value = file_info_result

        result = self.fs.read_file("/path/to/empty.bin", format="bytes")
        self.assertIsInstance(result, BinaryFileContentResult)
        self.assertTrue(result.success)
        self.assertEqual(result.content, b"")
        self.assertEqual(result.size, 0)

    @patch("agentbay._sync.filesystem.FileSystem.get_file_info")
    @patch("agentbay._sync.filesystem.FileSystem._read_file_chunk")
    @pytest.mark.sync
    def test_read_file_text_format_explicit(
        self, mock_read_file_chunk, mock_get_file_info
    ):
        """
        Test read_file method with explicit format='text' (should work same as default).
        """
        file_info_result = FileInfoResult(
            request_id="request-123",
            success=True,
            file_info={"size": 1024, "isDirectory": False},
        )
        mock_get_file_info.return_value = file_info_result

        mock_read_file_chunk.return_value = FileContentResult(
            request_id="request-123", success=True, content="file content"
        )

        result = self.fs.read_file("/path/to/file.txt", format="text")
        self.assertIsInstance(result, FileContentResult)
        self.assertTrue(result.success)
        self.assertEqual(result.content, "file content")
        self.assertIsInstance(result.content, str)

    @pytest.mark.sync
    def test_read_file_chunk_binary_format(self):
        """
        Test _read_file_chunk method with format='binary'.
        """
        import base64
        from agentbay import McpToolResult

        # Mock MCP tool call returning base64-encoded string
        binary_data = b'\xff\xd8\xff\xe0\x00\x10JFIF'
        base64_data = base64.b64encode(binary_data).decode('ascii')
        
        mock_result = McpToolResult(
            request_id="request-123",
            success=True,
            data=base64_data,
        )
        self.session.call_mcp_tool.return_value = mock_result

        result = self.fs._read_file_chunk(
            "/path/to/image.jpeg", offset=0, length=1024, format_type="binary"
        )
        
        self.assertIsInstance(result, BinaryFileContentResult)
        self.assertTrue(result.success)
        self.assertIsInstance(result.content, bytes)
        self.assertEqual(result.content, binary_data)
        
        # Verify MCP tool was called with format='binary'
        self.session.call_mcp_tool.assert_awaited_once()
        call_args = self.session.call_mcp_tool.call_args
        self.assertEqual(call_args[0][0], "read_file")
        self.assertEqual(call_args[0][1]["format"], "binary")
        self.assertEqual(call_args[0][1]["path"], "/path/to/image.jpeg")
        self.assertEqual(call_args[0][1]["offset"], 0)
        self.assertEqual(call_args[0][1]["length"], 1024)

    @pytest.mark.sync
    def test_read_file_chunk_binary_format_base64_decode_error(self):
        """
        Test _read_file_chunk method with format='binary' when base64 decode fails.
        """
        from agentbay import McpToolResult

        # Mock MCP tool call returning invalid base64 string
        mock_result = McpToolResult(
            request_id="request-123",
            success=True,
            data="invalid-base64!!!",  # Invalid base64
        )
        self.session.call_mcp_tool.return_value = mock_result

        result = self.fs._read_file_chunk(
            "/path/to/image.jpeg", offset=0, length=1024, format_type="binary"
        )
        
        self.assertIsInstance(result, BinaryFileContentResult)
        self.assertFalse(result.success)
        self.assertEqual(result.content, b"")
        self.assertIn("Failed to decode base64", result.error_message)

    @pytest.mark.sync
    def test_read_file_chunk_text_format_no_format_param(self):
        """
        Test _read_file_chunk method with format='text' (default) - should not pass format param.
        """
        from agentbay import McpToolResult

        mock_result = McpToolResult(
            request_id="request-123",
            success=True,
            data="text content",
        )
        self.session.call_mcp_tool.return_value = mock_result

        result = self.fs._read_file_chunk(
            "/path/to/file.txt", offset=0, length=1024, format_type="text"
        )
        
        self.assertIsInstance(result, FileContentResult)
        self.assertTrue(result.success)
        self.assertEqual(result.content, "text content")
        
        # Verify MCP tool was called WITHOUT format parameter (default text)
        self.session.call_mcp_tool.assert_awaited_once()
        call_args = self.session.call_mcp_tool.call_args
        self.assertEqual(call_args[0][0], "read_file")
        self.assertNotIn("format", call_args[0][1])  # format should not be in args for text


if __name__ == "__main__":
    unittest.main()
