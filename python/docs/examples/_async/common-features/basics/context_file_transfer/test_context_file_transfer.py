#!/usr/bin/env python3
"""
Integration tests for ContextFileTransfer.

These tests use real API calls (no mocks). Requires AGENTBAY_API_KEY env var.
"""

import asyncio
import io
import os
import shutil
import tempfile
import time

import pytest
import pytest_asyncio

from agentbay import AsyncAgentBay
from agentbay._common.exceptions import AgentBayError
from context_file_transfer import ContextFileTransfer


@pytest.fixture(scope="module")
def event_loop():
    loop = asyncio.new_event_loop()
    yield loop
    loop.close()


@pytest_asyncio.fixture(scope="module")
async def setup():
    """Create AgentBay, ContextFileTransfer, and a test context."""
    agent_bay = AsyncAgentBay()
    transfer = ContextFileTransfer(agent_bay)
    ctx_name = f"file-transfer-test-{int(time.time())}"
    ctx_result = await agent_bay.context.get(ctx_name, create=True)
    assert ctx_result.success, f"Failed to create context: {ctx_result.error_message}"
    context_id = ctx_result.context_id
    context = ctx_result.context

    yield agent_bay, transfer, context_id

    await agent_bay.context.delete(context)


# ── upload_file ──────────────────────────────────────────────────────────

@pytest.mark.asyncio
async def test_upload_file_bytes(setup):
    """upload_file should upload bytes and the content should be readable back."""
    _, transfer, context_id = setup
    test_content = b"Hello, Context File Transfer!"
    result = await transfer.upload_file(
        context_id, "/test_upload.txt", test_content
    )
    assert result.success, f"upload_file failed: {result.error_message}"

    downloaded = await transfer.download_file(context_id, "/test_upload.txt")
    assert downloaded == test_content.decode("utf-8"), (
        f"Content mismatch: expected '{test_content.decode()}', got '{downloaded}'"
    )


@pytest.mark.asyncio
async def test_upload_file_stream(setup):
    """upload_file should upload from a file-like object and content should match."""
    _, transfer, context_id = setup
    original = b"Stream content for upload test"
    stream = io.BytesIO(original)
    result = await transfer.upload_file(
        context_id, "/test_upload_stream.txt", stream
    )
    assert result.success, f"upload_file failed: {result.error_message}"

    downloaded = await transfer.download_file(context_id, "/test_upload_stream.txt")
    assert downloaded == original.decode("utf-8"), (
        f"Content mismatch: expected '{original.decode()}', got '{downloaded}'"
    )


# ── download_file ────────────────────────────────────────────────────────

@pytest.mark.asyncio
async def test_download_file(setup):
    """download_file should return the content of a previously uploaded file."""
    _, transfer, context_id = setup
    test_content = "Download test content 12345"
    await transfer.upload_file(
        context_id, "/test_download.txt", test_content.encode("utf-8")
    )
    content = await transfer.download_file(context_id, "/test_download.txt")
    assert content == test_content, f"Content mismatch: got '{content}'"


@pytest.mark.asyncio
async def test_download_file_nonexistent(setup):
    """download_file should raise AgentBayError for non-existent file."""
    _, transfer, context_id = setup
    with pytest.raises(Exception):
        await transfer.download_file(context_id, "/nonexistent_file_999.txt")


# ── upload_directory ─────────────────────────────────────────────────────

@pytest.mark.asyncio
async def test_upload_directory(setup):
    """upload_directory should upload all files in a local directory."""
    _, transfer, context_id = setup

    temp_dir = tempfile.mkdtemp(prefix="ctx_upload_test_")
    try:
        with open(os.path.join(temp_dir, "file1.txt"), "w") as f:
            f.write("Content of file 1")
        sub_dir = os.path.join(temp_dir, "subdir")
        os.makedirs(sub_dir)
        with open(os.path.join(sub_dir, "file2.txt"), "w") as f:
            f.write("Content of file 2 in subdir")

        result = await transfer.upload_directory(
            context_id, "/test_dir_upload", temp_dir
        )
        assert result.success, f"upload_directory failed: {result.error_message}"
        assert result.data["total"] == 2
        assert result.data["succeeded"] == 2
        assert result.data["failed"] == 0

        content1 = await transfer.download_file(
            context_id, "/test_dir_upload/file1.txt"
        )
        assert content1 == "Content of file 1", (
            f"file1.txt content mismatch: got '{content1}'"
        )

        content2 = await transfer.download_file(
            context_id, "/test_dir_upload/subdir/file2.txt"
        )
        assert content2 == "Content of file 2 in subdir", (
            f"file2.txt content mismatch: got '{content2}'"
        )
    finally:
        shutil.rmtree(temp_dir)


@pytest.mark.asyncio
async def test_upload_directory_nonexistent(setup):
    """upload_directory should fail for non-existent local directory."""
    _, transfer, context_id = setup
    with pytest.raises(AgentBayError):
        await transfer.upload_directory(
            context_id, "/test_dir", "/nonexistent/directory/path"
        )


# ── download_directory ───────────────────────────────────────────────────

@pytest.mark.asyncio
async def test_download_directory(setup):
    """download_directory should download files from context to local directory."""
    _, transfer, context_id = setup

    await transfer.upload_file(
        context_id, "/test_dir_download/a.txt", b"File A content"
    )
    await transfer.upload_file(
        context_id, "/test_dir_download/b.txt", b"File B content"
    )

    download_dir = tempfile.mkdtemp(prefix="ctx_download_test_")
    try:
        result = await transfer.download_directory(
            context_id, "/test_dir_download", download_dir
        )
        assert result.success, f"download_directory failed: {result.error_message}"
        assert result.data["succeeded"] >= 2

        a_path = os.path.join(download_dir, "a.txt")
        assert os.path.exists(a_path), "a.txt should exist"
        with open(a_path, "r") as f:
            assert f.read() == "File A content"

        b_path = os.path.join(download_dir, "b.txt")
        assert os.path.exists(b_path), "b.txt should exist"
        with open(b_path, "r") as f:
            assert f.read() == "File B content"
    finally:
        shutil.rmtree(download_dir)
