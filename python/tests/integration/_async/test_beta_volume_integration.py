import os
import time

import pytest

from agentbay import AsyncAgentBay, CreateSessionParams


@pytest.mark.asyncio
async def test_beta_volume_create_list_mount_and_delete():
    api_key = os.getenv("AGENTBAY_API_KEY")
    if not api_key:
        pytest.fail("AGENTBAY_API_KEY environment variable is not set")

    agent_bay = AsyncAgentBay(api_key=api_key)
    image_id = "imgc-0ab5ta4mgqs15qxjf"
    volume_name = f"beta-volume-it-{int(time.time() * 1000)}"

    vol_result = await agent_bay.beta_volume.create(name=volume_name, image_id=image_id)
    assert vol_result.success, vol_result.error_message
    assert vol_result.volume is not None
    assert vol_result.volume.id

    volume_id = vol_result.volume.id

    try:
        list_result = await agent_bay.beta_volume.list(
            image_id=image_id, max_results=10, volume_name=volume_name
        )
        assert list_result.success, list_result.error_message
        assert any(v.id == volume_id for v in list_result.volumes)

        params = CreateSessionParams(image_id=image_id, volume=vol_result.volume)
        create_result = await agent_bay.create(params)
        assert create_result.success, create_result.error_message
        assert create_result.session is not None
        assert create_result.session.token

        await create_result.session.delete()
    finally:
        del_result = await agent_bay.beta_volume.delete(volume_id=volume_id)
        assert del_result.success, del_result.error_message


