"""
One-click DingTalk bot setup - supports Playwright, Browser Operator, BrowserUseAgent.

Backend selection:
- backend="playwright": Playwright (deterministic, fast) - default
- backend="operator": Browser Operator (page_use_*) - step-by-step act/extract
- backend="agent": BrowserUseAgent - natural language execute_task_and_wait

Default: DINGTALK_SETUP_BACKEND env or "playwright"
"""

import asyncio
import os
import logging
from typing import Optional, Tuple

from .config_builder import build_config
from .dingtalk_setup_common import DingtalkCredentialsSchema
from .dingtalk_setup_playwright import (
    continue_dingtalk_setup as _continue_playwright,
    start_dingtalk_setup as _start_playwright,
)
from .dingtalk_setup_browser_operator import (
    continue_dingtalk_setup as _continue_operator,
    start_dingtalk_setup as _start_operator,
)
from .dingtalk_setup_browser_agent import (
    continue_dingtalk_setup as _continue_agent,
    start_dingtalk_setup as _start_agent,
)
from .models import SessionInfo

logger = logging.getLogger(__name__)

DEFAULT_BACKEND = os.environ.get("DINGTALK_SETUP_BACKEND", "playwright")


def _get_backend(backend: Optional[str] = None) -> str:
    """Get backend name: playwright, operator, or agent."""
    b = (backend or "").strip().lower()
    if b in ("playwright", "operator", "agent"):
        return b
    return (
        DEFAULT_BACKEND
        if DEFAULT_BACKEND in ("playwright", "operator", "agent")
        else "playwright"
    )


async def start_dingtalk_setup(
    info: SessionInfo,
    backend: Optional[str] = None,
) -> Tuple[bool, str]:
    """
    Start DingTalk setup: open browser to open.dingtalk.com for QR login.

    Args:
        info: Session info
        backend: "playwright", "operator", or "agent"

    Returns (success, error_message).
    """
    b = _get_backend(backend)
    if b == "agent":
        return await asyncio.to_thread(_start_agent, info)
    if b == "operator":
        return await asyncio.to_thread(_start_operator, info)
    return await asyncio.to_thread(_start_playwright, info)


async def continue_dingtalk_setup(
    info: SessionInfo,
    backend: Optional[str] = None,
) -> Tuple[bool, Optional[str], Optional[str], str]:
    """
    Continue after user logged in: create app, extract credentials.

    Args:
        info: Session info
        backend: "playwright", "operator", or "agent"

    Returns (success, client_id, client_secret, error).
    """
    b = _get_backend(backend)
    if b == "agent":
        return await asyncio.to_thread(_continue_agent, info)
    if b == "operator":
        return await asyncio.to_thread(_continue_operator, info)
    return await asyncio.to_thread(_continue_playwright, info)


def apply_dingtalk_credentials(
    info: SessionInfo,
    client_id: str,
    client_secret: str,
) -> Tuple[bool, str]:
    """
    Write updated openclaw.json with DingTalk credentials and restart gateway.

    Returns (success, error_message).
    """
    req = info.create_request
    if not req:
        return False, "缺少创建会话时的配置信息"

    try:
        config_json = build_config(
            bailian_api_key=req.bailian_api_key,
            dingtalk_client_id=client_id,
            dingtalk_client_secret=client_secret,
            feishu_app_id=req.feishu_app_id,
            feishu_app_secret=req.feishu_app_secret,
            model_base_url=req.model_base_url,
            model_id=req.model_id,
        )
    except Exception as e:
        return False, str(e)

    session = info.session
    from .session_manager import (
        CONFIG_PATH,
        session_manager,
    )

    try:
        session.file_system.write(CONFIG_PATH, config_json)
        session_manager._execute_command(
            session,
            "openclaw gateway stop; pkill -f 'openclaw gateway' || true",
            timeout_ms=10000,
        )
        session_manager._execute_command(
            session,
            "bash -lc 'nohup openclaw gateway > /tmp/gateway.log 2>&1 &'",
            timeout_ms=15000,
        )
        logger.info(
            "Updated OpenClaw config with DingTalk credentials, restarted gateway"
        )
        return True, ""
    except Exception as e:
        logger.exception("Failed to apply DingTalk credentials")
        return False, str(e)


# Re-export for external use
__all__ = [
    "DingtalkCredentialsSchema",
    "start_dingtalk_setup",
    "continue_dingtalk_setup",
    "apply_dingtalk_credentials",
]
