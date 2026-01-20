"""Integration test for get_all_ui_elements XML format (no mocks)."""

import os
import asyncio

import pytest
import pytest_asyncio

from agentbay import AsyncAgentBay, CreateSessionParams


IMAGE_ID = "imgc-0ab5ta4mn31wth5lh"


@pytest_asyncio.fixture(scope="module")
async def agent_bay():
    api_key = os.environ.get("AGENTBAY_API_KEY")
    if not api_key:
        pytest.skip("AGENTBAY_API_KEY environment variable not set")
    return AsyncAgentBay(api_key=api_key)


@pytest_asyncio.fixture
async def session(agent_bay):
    last_error = ""
    for attempt in range(3):
        result = await agent_bay.create(CreateSessionParams(image_id=IMAGE_ID))
        if result.success and result.session:
            s = result.session
            try:
                yield s
            finally:
                await s.delete()
            return

        last_error = result.error_message or "unknown error"
        if attempt < 2:
            await asyncio.sleep(2 + attempt * 2)

    pytest.fail(f"Failed to create session after retries: {last_error}")


@pytest.mark.asyncio
@pytest.mark.integration
async def test_get_all_ui_elements_xml_format_contract(session):
    ui = await session.mobile.get_all_ui_elements(timeout_ms=10000, format="xml")
    assert ui.success, f"get_all_ui_elements(xml) failed: {ui.error_message}"
    assert ui.format == "xml"
    assert isinstance(ui.raw, str)
    assert ui.raw.strip() != ""
    assert ui.raw.lstrip().startswith("<?xml")
    assert "<hierarchy" in ui.raw
    assert isinstance(ui.elements, list)
    assert ui.elements == []
