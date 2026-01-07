import os

import pytest

from agentbay import AsyncAgentBay, CreateSessionParams


@pytest.mark.asyncio
async def test_network_create_describe_and_bind_session():
    api_key = os.getenv("AGENTBAY_API_KEY")
    if not api_key:
        pytest.skip("AGENTBAY_API_KEY environment variable not set")

    agent_bay = AsyncAgentBay(api_key=api_key)

    net_result = await agent_bay.network.get_network_bind_token()
    assert net_result.success, net_result.error_message
    assert net_result.network_id != ""
    assert net_result.network_token != ""

    status_result = await agent_bay.network.describe(net_result.network_id)
    assert status_result.success, status_result.error_message

    params = CreateSessionParams(
        image_id="imgc-0ab5takhjgjky7htu",
        labels={"test-type": "network-integration"},
        network_id=net_result.network_id,
    )

    create_result = await agent_bay.create(params)
    assert create_result.success, create_result.error_message
    assert create_result.session is not None

    try:
        pass
    finally:
        await create_result.session.delete()


