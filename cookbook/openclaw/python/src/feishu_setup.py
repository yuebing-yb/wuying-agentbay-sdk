"""
One-click Feishu bot setup - supports Playwright.

Backend selection:
- backend="playwright": Playwright (deterministic, fast) - default

Default: FEISHU_SETUP_BACKEND env or "playwright"
"""

import os
import logging
from typing import Optional, Tuple

from .config_builder import build_config
from .feishu_setup_common import FeishuCredentialsSchema
from .feishu_setup_playwright import (
    continue_feishu_setup as _continue_playwright,
    start_feishu_setup as _start_playwright,
)
from .models import SessionInfo

logger = logging.getLogger(__name__)

DEFAULT_BACKEND = os.environ.get("FEISHU_SETUP_BACKEND", "playwright")


def _get_backend(backend: Optional[str] = None) -> str:
    """Get backend name: playwright."""
    b = (backend or "").strip().lower()
    if b == "playwright":
        return b
    return "playwright"


async def start_feishu_setup(
    info: SessionInfo,
    backend: Optional[str] = None,
) -> Tuple[bool, str]:
    """
    Start Feishu setup: open browser to open.feishu.cn for QR login.

    Args:
        info: Session info
        backend: "playwright"

    Returns (success, error_message).
    """
    b = _get_backend(backend)
    return await _start_playwright(info)


async def continue_feishu_setup(
    info: SessionInfo,
    backend: Optional[str] = None,
) -> Tuple[bool, Optional[str], Optional[str], str]:
    """
    Continue after user logged in: create app, configure permissions, extract credentials.

    Args:
        info: Session info
        backend: "playwright"

    Returns (success, app_id, app_secret, error).
    """
    b = _get_backend(backend)
    return await _continue_playwright(info)


def apply_feishu_credentials(
    info: SessionInfo,
    app_id: str,
    app_secret: str,
) -> Tuple[bool, str]:
    """
    Write updated openclaw.json with Feishu credentials and restart gateway.

    Returns (success, error_message).
    """
    req = info.create_request
    if not req:
        return False, "缺少创建会话时的配置信息"

    try:
        config_json = build_config(
            bailian_api_key=req.bailian_api_key,
            dingtalk_client_id=req.dingtalk_client_id,
            dingtalk_client_secret=req.dingtalk_client_secret,
            feishu_app_id=app_id,
            feishu_app_secret=app_secret,
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
            "Updated OpenClaw config with Feishu credentials, restarted gateway"
        )
        return True, ""
    except Exception as e:
        logger.exception("Failed to apply Feishu credentials")
        return False, str(e)


# Re-export for external use
__all__ = [
    "FeishuCredentialsSchema",
    "start_feishu_setup",
    "continue_feishu_setup",
    "apply_feishu_credentials",
]
