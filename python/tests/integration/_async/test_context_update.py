"""Integration tests for context updates."""

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
async def test_context_file_update(test_session):
    """Test updating file in context using upload URLs."""
    import httpx

    # Create a context
    ctx_result = await test_session.agent_bay.context.get("update_ctx", create=True)
    assert ctx_result.success

    # Upload initial file
    upload_url_result = await test_session.agent_bay.context.get_file_upload_url(
        ctx_result.context_id, "/update_file.txt"
    )
    assert upload_url_result.success

    original_content = b"original content"
    async with httpx.AsyncClient() as client:
        response = await client.put(upload_url_result.url, content=original_content)
        assert response.status_code == 200

    # Update the file with new content
    upload_url_result2 = await test_session.agent_bay.context.get_file_upload_url(
        ctx_result.context_id, "/update_file.txt"
    )
    assert upload_url_result2.success

    updated_content = b"updated content"
    async with httpx.AsyncClient() as client:
        response = await client.put(upload_url_result2.url, content=updated_content)
        assert response.status_code == 200

    # Verify the file was updated
    download_url_result = await test_session.agent_bay.context.get_file_download_url(
        ctx_result.context_id, "/update_file.txt"
    )
    assert download_url_result.success

    async with httpx.AsyncClient() as client:
        response = await client.get(download_url_result.url)
        assert response.status_code == 200
        assert response.content == updated_content

    # Clean up
    await test_session.agent_bay.context.delete(ctx_result.context)

    print("Context file updated successfully")
