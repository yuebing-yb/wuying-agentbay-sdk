"""
Integration tests for AsyncMobile beta screenshot APIs.

These tests use real backend resources (no mocks).
"""

import asyncio
import os

import pytest
import pytest_asyncio

from agentbay import AsyncAgentBay, CreateSessionParams
from agentbay import AgentBayError


async def _set_low_android_resolution(session) -> None:
    """
    Reduce Android resolution to make screenshots smaller for tests.
    """
    cmds = [
        "wm size 720x1280",
        "wm density 160",
    ]
    for cmd in cmds:
        r = await session.command.execute_command(cmd)
        assert r.success, f"Command failed: {cmd} error={r.error_message}"


async def _prepare_for_screenshot_tests(session) -> None:
    await _set_low_android_resolution(session)
    start = await session.mobile.start_app("monkey -p com.android.settings 1")
    assert start.success, f"Failed to start Settings: {start.error_message}"
    await asyncio.sleep(2)


@pytest_asyncio.fixture(scope="module")
async def agent_bay():
    api_key = os.environ.get("AGENTBAY_API_KEY")
    if not api_key:
        pytest.skip("AGENTBAY_API_KEY environment variable not set")
    return AsyncAgentBay(api_key=api_key)


@pytest_asyncio.fixture
async def session(agent_bay):
    params = CreateSessionParams(image_id="imgc-0ab5ta4mn31wth5lh")
    result = await agent_bay.create(params)
    assert result.success, f"Failed to create session: {result.error_message}"
    assert result.session is not None
    yield result.session
    await result.session.delete()


@pytest.mark.asyncio
async def test_mobile_beta_take_screenshot_png(session):
    await _prepare_for_screenshot_tests(session)
    result = await session.mobile.beta_take_screenshot()
    assert result.success is True
    assert result.format == "png"
    assert isinstance(result.width, int)
    assert isinstance(result.height, int)
    assert result.width > 0
    assert result.height > 0
    assert isinstance(result.data, (bytes, bytearray))
    assert len(result.data) > 0
    assert bytes(result.data[:8]) == b"\x89PNG\r\n\x1a\n"


@pytest.mark.asyncio
async def test_mobile_beta_take_long_screenshot_png(session):
    await _prepare_for_screenshot_tests(session)
    result = await session.mobile.beta_take_long_screenshot(max_screens=2, format="png")
    assert result.success is True
    assert result.format == "png"
    assert isinstance(result.width, int)
    assert isinstance(result.height, int)
    assert result.width > 0
    assert result.height > 0
    assert isinstance(result.data, (bytes, bytearray))
    assert len(result.data) > 0
    assert bytes(result.data[:8]) == b"\x89PNG\r\n\x1a\n"

