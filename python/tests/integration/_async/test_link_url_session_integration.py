import os

import pytest

from agentbay import AsyncAgentBay, CreateSessionParams


@pytest.mark.asyncio
async def test_link_url_session_mcp_tools_and_call_tool():
    api_key = os.getenv("AGENTBAY_API_KEY")
    if not api_key:
        pytest.skip("AGENTBAY_API_KEY environment variable not set")

    agent_bay = AsyncAgentBay(api_key=api_key)

    params = CreateSessionParams(
        image_id="imgc-0ab5takhjgjky7htu",
        labels={"test-type": "link-url-integration"},
    )

    result = await agent_bay.create(params)
    assert result.success, result.error_message
    assert result.session is not None

    session = result.session
    try:
        assert session.get_token() != ""
        assert session.get_link_url() != ""
        assert len(session.mcp_tools) > 0

        # Force using LinkUrl route (not legacy ip:port route)
        session.network_interface_ip = ""
        session.http_port = ""

        cmd_result = await session.command.execute_command("echo link-url-route-ok")
        assert cmd_result.success, cmd_result.error_message
        assert "link-url-route-ok" in cmd_result.output
    finally:
        await session.delete()






