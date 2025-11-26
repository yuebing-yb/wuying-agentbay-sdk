"""Integration tests for context file operations."""

import os

import pytest
import pytest_asyncio

from agentbay import AsyncAgentBay


@pytest_asyncio.fixture(scope="module")
async def agent_bay():
    api_key = os.environ.get("AGENTBAY_API_KEY")
    if not api_key:
        pytest.skip("AGENTBAY_API_KEY environment variable not set")
    return AsyncAgentBay(api_key=api_key)


@pytest_asyncio.fixture
async def test_session(agent_bay):
    result = await agent_bay.create()
    assert result.success
    yield result.session
    await result.session.delete()


@pytest.mark.asyncio
async def test_context_file_operations(test_session):
    """Test context file operations using upload/download URLs."""
    import httpx

    # Create a context
    ctx_result = await test_session.agent_bay.context.get("test_ctx", create=True)
    assert ctx_result.success

    # Get upload URL for a file
    upload_url_result = await test_session.agent_bay.context.get_file_upload_url(
        ctx_result.context_id, "/test_file.txt"
    )
    assert upload_url_result.success
    assert upload_url_result.url != ""

    # Upload file content
    file_content = b"test content for context file"
    async with httpx.AsyncClient() as client:
        response = await client.put(upload_url_result.url, content=file_content)
        assert response.status_code == 200

    # List files in context
    files_result = await test_session.agent_bay.context.list_files(
        ctx_result.context_id, "/"
    )
    assert files_result.success

    # Get download URL
    download_url_result = await test_session.agent_bay.context.get_file_download_url(
        ctx_result.context_id, "/test_file.txt"
    )
    assert download_url_result.success
    assert download_url_result.url != ""

    # Download and verify content
    async with httpx.AsyncClient() as client:
        response = await client.get(download_url_result.url)
        assert response.status_code == 200
        assert response.content == file_content

    # Delete the file
    delete_result = await test_session.agent_bay.context.delete_file(
        ctx_result.context_id, "/test_file.txt"
    )
    assert delete_result.success

    # Clean up context
    await test_session.agent_bay.context.delete(ctx_result.context)

    print("Context file operations test completed successfully")
