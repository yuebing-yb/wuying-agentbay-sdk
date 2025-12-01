import json
import os
from uuid import uuid4

import pytest
import pytest_asyncio

from agentbay import AsyncAgentBay
from agentbay.api.models import MobileSimulateMode
from agentbay import Context
from agentbay._common.params.context_sync import BWList, ContextSync, SyncPolicy


@pytest_asyncio.fixture(scope="module")
async def agent_bay():
    """Create AsyncAgentBay instance."""
    api_key = os.environ.get("AGENTBAY_API_KEY")
    if not api_key:
        pytest.skip("AGENTBAY_API_KEY environment variable not set")
    return AsyncAgentBay(api_key=api_key)


@pytest.mark.asyncio
async def test_mobile_simulate_basic_flow(agent_bay):
    """Test basic mobile simulate flow."""
    service = agent_bay.mobile_simulate

    # 1. Set configs
    service.set_simulate_enable(True)
    service.set_simulate_mode(MobileSimulateMode.ALL)
    assert service.get_simulate_enable() is True
    assert service.get_simulate_mode() == MobileSimulateMode.ALL

    # 2. Upload mobile info (internal context)
    mobile_info = json.dumps({"device": "pixel_6", "os_version": "12"})
    upload_result = await service.upload_mobile_info(mobile_info)
    assert upload_result.success is True
    context_id = upload_result.mobile_simulate_context_id
    assert context_id is not None
    print(f"Uploaded mobile info to internal context: {context_id}")

    # 3. Verify config has context id
    config = service.get_simulate_config()
    assert config.simulate is True
    assert config.simulate_mode == MobileSimulateMode.ALL
    assert config.simulated_context_id == context_id

    # Cleanup context
    await agent_bay.context.delete(Context(id=context_id, name=""))


@pytest.mark.asyncio
async def test_mobile_simulate_external_context(agent_bay):
    """Test mobile simulate with external context."""
    service = agent_bay.mobile_simulate

    # Create a context first
    context_name = f"mobile-sim-ext-{uuid4().hex[:8]}"
    context_result = await agent_bay.context.create(context_name)
    assert context_result.success is True
    context = context_result.context

    try:
        # Create context sync
        context_sync = ContextSync(
            context_id=context.id,
            path="/tmp/mobile_sim_test",
            policy=SyncPolicy(bw_list=BWList(white_lists=[])),
        )

        # Upload mobile info
        mobile_info = json.dumps({"device": "iphone_13", "os_version": "15"})
        upload_result = await service.upload_mobile_info(
            mobile_info, context_sync=context_sync
        )
        assert upload_result.success is True
        assert upload_result.mobile_simulate_context_id == context.id

        # Check has_mobile_info
        has_info = await service.has_mobile_info(context_sync)
        assert has_info is True

        # Verify config
        config = service.get_simulate_config()
        # For external context, simulated_context_id is None in config (it is managed by user)
        assert config.simulated_context_id is None

    finally:
        await agent_bay.context.delete(context)
