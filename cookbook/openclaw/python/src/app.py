"""
FastAPI application for OpenClaw session management.

Provides REST API endpoints for creating, querying, and deleting OpenClaw sandbox sessions.
Serves the frontend static files.
"""

import asyncio
import base64
import json
import logging
from pathlib import Path
from typing import List, Optional

from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse, JSONResponse
from fastapi.staticfiles import StaticFiles

from .dingtalk_setup import (
    apply_dingtalk_credentials,
    continue_dingtalk_setup,
    start_dingtalk_setup,
)
from .feishu_setup import (
    apply_feishu_credentials,
    continue_feishu_setup,
    start_feishu_setup,
)
from .feishu_setup_playwright import configure_feishu_event_subscription
from .models import CreateSessionRequest, DingtalkSetupStatus, FeishuSetupStatus, SessionResponse
from .session_manager import session_manager

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)

# Create FastAPI app
app = FastAPI(
    title="OpenClaw in AgentBay",
    description="REST API for managing OpenClaw sandbox sessions",
    version="1.0.0",
)

# CORS middleware - allow all origins
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Static files directory (parent of src = python/, static is in python/)
STATIC_DIR = Path(__file__).parent.parent / "static"


# ── API Routes ─────────────────────────────────────────────────────


@app.post("/api/sessions", response_model=SessionResponse)
async def create_session(request: CreateSessionRequest):
    """
    Create a new OpenClaw sandbox session.

    Flow: Create sandbox -> Write config -> Start Gateway -> Open Dashboard -> Return resource_url
    """
    # Validate required fields
    if not request.agentbay_api_key or not request.agentbay_api_key.strip():
        raise HTTPException(status_code=400, detail="agentbayApiKey cannot be empty")
    if not request.bailian_api_key or not request.bailian_api_key.strip():
        raise HTTPException(status_code=400, detail="bailianApiKey cannot be empty")
    if not request.username or not request.username.strip():
        raise HTTPException(status_code=400, detail="username cannot be empty")

    try:
        response = session_manager.create_session(request)
        return response
    except Exception as e:
        logger.error(f"Failed to create session: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/sessions/{session_id}", response_model=SessionResponse)
async def get_session(session_id: str, request: Request):
    """Query session status by ID. Accepts X-OpenClaw-Form-Data (base64 JSON) for restore."""
    form_data = None
    raw = request.headers.get("X-OpenClaw-Form-Data")
    if raw:
        try:
            form_data = json.loads(base64.b64decode(raw).decode("utf-8"))
        except Exception:
            form_data = None
    response = session_manager.get_session(
        session_id, form_data=form_data
    )
    if response is None:
        raise HTTPException(status_code=404, detail="Session not found")
    return response


@app.delete("/api/sessions/{session_id}")
async def delete_session(session_id: str):
    """Destroy a session by ID."""
    success = session_manager.delete_session(session_id)
    if not success:
        raise HTTPException(status_code=404, detail="Session not found")
    return {"message": "Session destroyed", "sessionId": session_id}


@app.post("/api/sessions/{session_id}/pause")
async def pause_session(session_id: str):
    """
    Pause (hibernate) a session to reduce resource usage.
    """
    success, err = session_manager.pause_session(session_id)
    if not success:
        raise HTTPException(status_code=500, detail=err or "Failed to pause session")
    return {"message": "会话已休眠", "sessionId": session_id}


@app.post("/api/sessions/{session_id}/resume", response_model=SessionResponse)
async def resume_session(session_id: str):
    """
    Resume (wake) a paused session. Returns updated session data.
    """
    success, err = session_manager.resume_session(session_id)
    if not success:
        raise HTTPException(status_code=500, detail=err or "Failed to resume session")
    info = session_manager.get_session_info(session_id)
    if not info:
        raise HTTPException(status_code=404, detail="Session not found")
    return info.to_response()


@app.post("/api/sessions/{session_id}/restart-dashboard")
async def restart_dashboard(session_id: str):
    """
    Restart dashboard (Firefox with OpenClaw UI) in sandbox.
    Called when user clicks "打开 OpenClaw UI".
    """
    success, err = session_manager.restart_dashboard(session_id)
    if not success:
        raise HTTPException(status_code=500, detail=err or "Failed to restart dashboard")
    return {"message": "Dashboard 已重启"}


@app.get("/api/sessions", response_model=List[SessionResponse])
async def list_sessions():
    """List all active sessions."""
    return session_manager.list_sessions()


# ── DingTalk One-Click Setup ────────────────────────────────────────


@app.post("/api/sessions/{session_id}/dingtalk-setup/start")
async def dingtalk_setup_start(session_id: str, backend: str = "playwright"):
    """
    Start DingTalk setup: open browser to open.dingtalk.com for QR login.

    backend: "playwright" (default), "operator", or "agent"
    """
    info = session_manager.get_session_info(session_id)
    if not info:
        raise HTTPException(status_code=404, detail="Session not found")
    success, err = await start_dingtalk_setup(info, backend=backend)
    if not success:
        raise HTTPException(status_code=500, detail=err)
    session_manager.set_dingtalk_setup_state(session_id, step="login", backend=backend)
    return {
        "message": "已打开钉钉开放平台，请使用钉钉 APP 扫码登录",
        "step": "login",
        "backend": backend,
    }


@app.post("/api/sessions/{session_id}/dingtalk-setup/continue")
async def dingtalk_setup_continue(session_id: str, backend: Optional[str] = None):
    """
    Continue after user logged in: create app, extract credentials,
    and automatically apply to OpenClaw config (restart gateway).

    backend: "operator" or "agent". Uses stored backend from start if not provided.
    """
    info = session_manager.get_session_info(session_id)
    if not info:
        raise HTTPException(status_code=404, detail="Session not found")
    state = session_manager.get_dingtalk_setup_state(session_id)
    backend = backend or (state.get("backend") if state else None) or "playwright"
    session_manager.set_dingtalk_setup_state(session_id, step="creating")
    success, client_id, client_secret, err = await continue_dingtalk_setup(
        info, backend=backend
    )
    if not success:
        session_manager.set_dingtalk_setup_state(
            session_id, step="error", error=err
        )
        raise HTTPException(status_code=500, detail=err)

    # 提取凭证成功后，自动应用到配置并重启 Gateway（参照飞书）
    applied = False
    apply_err: Optional[str] = None
    if client_id and client_secret:
        applied, apply_err = await asyncio.to_thread(
            apply_dingtalk_credentials, info, client_id, client_secret
        )
        if applied:
            # 配置已更新，重启 Dashboard
            restart_ok, restart_err = await asyncio.to_thread(
                session_manager.restart_dashboard, session_id
            )
            if not restart_ok:
                logger.warning("[钉钉配置] 重启 Dashboard 失败: %s", restart_err)
            else:
                logger.info("[钉钉配置] 配置已更新，Dashboard 已重启")

    session_manager.set_dingtalk_setup_state(
        session_id,
        step="done",
        client_id=client_id or "",
        client_secret=client_secret or "",
        applied=applied,
        apply_error=apply_err,
    )
    if applied:
        return {
            "message": "已获取钉钉应用凭证并已应用到配置，Gateway 已重启",
            "step": "done",
            "clientId": client_id,
            "clientSecret": client_secret,
            "applied": True,
        }
    return {
        "message": "已获取钉钉应用凭证，但自动应用失败，请点击「提交并更新配置」重试",
        "step": "done",
        "clientId": client_id,
        "clientSecret": client_secret,
        "applied": False,
        "applyError": apply_err,
    }


@app.get("/api/sessions/{session_id}/dingtalk-setup/status", response_model=DingtalkSetupStatus)
async def dingtalk_setup_status(session_id: str):
    """Get DingTalk setup status."""
    if not session_manager.get_session_info(session_id):
        raise HTTPException(status_code=404, detail="Session not found")
    state = session_manager.get_dingtalk_setup_state(session_id)
    if not state:
        return DingtalkSetupStatus(step="idle")
    return DingtalkSetupStatus(
        step=state.get("step", "idle"),
        client_id=state.get("client_id"),
        client_secret=state.get("client_secret"),
        error=state.get("error"),
        backend=state.get("backend"),
        applied=state.get("applied"),
        apply_error=state.get("apply_error"),
    )


@app.post("/api/sessions/{session_id}/dingtalk-setup/apply")
async def dingtalk_setup_apply(
    session_id: str,
    body: dict,
):
    """Apply extracted credentials to OpenClaw config, restart gateway and dashboard."""
    info = session_manager.get_session_info(session_id)
    if not info:
        raise HTTPException(status_code=404, detail="Session not found")
    client_id = body.get("clientId") or body.get("client_id", "")
    client_secret = body.get("clientSecret") or body.get("client_secret", "")
    if not client_id or not client_secret:
        raise HTTPException(status_code=400, detail="clientId and clientSecret required")
    success, err = apply_dingtalk_credentials(info, client_id, client_secret)
    if not success:
        raise HTTPException(status_code=500, detail=err)
    # 配置已更新，重启 Dashboard
    restart_ok, restart_err = await asyncio.to_thread(
        session_manager.restart_dashboard, session_id
    )
    if not restart_ok:
        logger.warning("[钉钉配置] 重启 Dashboard 失败: %s", restart_err)
    return {"message": "配置已更新，Gateway 已重启"}


# ── Feishu One-Click Setup ──────────────────────────────────────────


@app.post("/api/sessions/{session_id}/feishu-setup/start")
async def feishu_setup_start(session_id: str, backend: str = "playwright"):
    """
    Start Feishu setup: open browser to open.feishu.cn for QR login.

    backend: "playwright" (default)
    """
    info = session_manager.get_session_info(session_id)
    if not info:
        raise HTTPException(status_code=404, detail="Session not found")
    success, err = await start_feishu_setup(info, backend=backend)
    if not success:
        raise HTTPException(status_code=500, detail=err)
    session_manager.set_feishu_setup_state(session_id, step="login", backend=backend)
    return {
        "message": "已打开飞书开放平台，请使用飞书 APP 扫码登录",
        "step": "login",
        "backend": backend,
    }


@app.post("/api/sessions/{session_id}/feishu-setup/continue")
async def feishu_setup_continue(session_id: str, backend: Optional[str] = None):
    """
    Continue after user logged in: create app, configure permissions, extract credentials,
    and automatically apply to OpenClaw config (restart gateway).

    backend: "playwright". Uses stored backend from start if not provided.
    """
    info = session_manager.get_session_info(session_id)
    if not info:
        raise HTTPException(status_code=404, detail="Session not found")
    state = session_manager.get_feishu_setup_state(session_id)
    backend = backend or (state.get("backend") if state else None) or "playwright"
    session_manager.set_feishu_setup_state(session_id, step="creating")
    success, app_id, app_secret, err = await continue_feishu_setup(
        info, backend=backend
    )
    if not success:
        session_manager.set_feishu_setup_state(
            session_id, step="error", error=err
        )
        raise HTTPException(status_code=500, detail=err)

    # 提取凭证成功后，自动应用到配置并重启 Gateway
    applied = False
    apply_err: Optional[str] = None
    if app_id and app_secret:
        applied, apply_err = apply_feishu_credentials(info, app_id, app_secret)

    # 自动应用成功后，等待 6 秒再配置事件订阅、回调与版本发布（步骤9、10、11、12，需 Gateway 长连接客户端已启动）
    if applied:
        await asyncio.sleep(6)
        event_ok, event_err = await configure_feishu_event_subscription(info)
        if not event_ok:
            logger.warning("[飞书配置] 事件订阅配置失败: %s", event_err)
        elif event_ok:
            # 步骤12版本已发布，飞书配置完成，重启 OpenClaw dashboard
            restart_ok, restart_err = await asyncio.to_thread(
                session_manager.restart_dashboard, session_id
            )
            if not restart_ok:
                logger.warning("[飞书配置] 重启 Dashboard 失败: %s", restart_err)
            else:
                logger.info("[飞书配置] 步骤12版本已发布，Dashboard 已重启")

    session_manager.set_feishu_setup_state(
        session_id,
        step="done",
        app_id=app_id or "",
        app_secret=app_secret or "",
        applied=applied,
        apply_error=apply_err,
    )
    if applied:
        return {
            "message": "已获取飞书应用凭证并已应用到配置，Gateway 已重启",
            "step": "done",
            "appId": app_id,
            "appSecret": app_secret,
            "applied": True,
        }
    return {
        "message": "已获取飞书应用凭证，但自动应用失败，请点击「应用到配置」重试",
        "step": "done",
        "appId": app_id,
        "appSecret": app_secret,
        "applied": False,
        "applyError": apply_err,
    }


@app.get("/api/sessions/{session_id}/feishu-setup/status", response_model=FeishuSetupStatus)
async def feishu_setup_status(session_id: str):
    """Get Feishu setup status."""
    if not session_manager.get_session_info(session_id):
        raise HTTPException(status_code=404, detail="Session not found")
    state = session_manager.get_feishu_setup_state(session_id)
    if not state:
        return FeishuSetupStatus(step="idle")
    return FeishuSetupStatus(
        step=state.get("step", "idle"),
        appId=state.get("app_id"),
        appSecret=state.get("app_secret"),
        error=state.get("error"),
        backend=state.get("backend"),
        applied=state.get("applied"),
        applyError=state.get("apply_error"),
    )


@app.post("/api/sessions/{session_id}/feishu-setup/apply")
async def feishu_setup_apply(
    session_id: str,
    body: dict,
):
    """Apply extracted credentials to OpenClaw config, restart gateway, and configure event subscription."""
    info = session_manager.get_session_info(session_id)
    if not info:
        raise HTTPException(status_code=404, detail="Session not found")
    app_id = body.get("appId") or body.get("app_id", "")
    app_secret = body.get("appSecret") or body.get("app_secret", "")
    if not app_id or not app_secret:
        raise HTTPException(status_code=400, detail="appId and appSecret required")
    success, err = apply_feishu_credentials(info, app_id, app_secret)
    if not success:
        raise HTTPException(status_code=500, detail=err)
    # 等待 6 秒后配置事件订阅、回调与版本发布
    await asyncio.sleep(6)
    event_ok, event_err = await configure_feishu_event_subscription(info)
    if not event_ok:
        logger.warning("[飞书配置] 事件订阅配置失败: %s", event_err)
    elif event_ok:
        # 步骤12版本已发布，飞书配置完成，重启 OpenClaw dashboard
        restart_ok, restart_err = await asyncio.to_thread(
            session_manager.restart_dashboard, session_id
        )
        if not restart_ok:
            logger.warning("[飞书配置] 重启 Dashboard 失败: %s", restart_err)
        else:
            logger.info("[飞书配置] 步骤12版本已发布，Dashboard 已重启")
    return {"message": "配置已更新，Gateway 已重启"}


# ── Static Files ───────────────────────────────────────────────────


@app.get("/")
async def serve_index():
    """Serve the frontend index.html."""
    index_path = STATIC_DIR / "index.html"
    if index_path.exists():
        return FileResponse(index_path)
    raise HTTPException(status_code=404, detail="Frontend not found")


@app.get("/assets/{file_path:path}")
async def serve_assets(file_path: str):
    """Serve frontend static assets."""
    asset_path = STATIC_DIR / "assets" / file_path
    if asset_path.exists():
        return FileResponse(asset_path)
    raise HTTPException(status_code=404, detail="Asset not found")


# ── Error Handlers ──────────────────────────────────────────────────


@app.exception_handler(HTTPException)
async def http_exception_handler(request: Request, exc: HTTPException):
    """Custom HTTP exception handler to ensure consistent error format."""
    return JSONResponse(
        status_code=exc.status_code,
        content={"detail": exc.detail},
    )


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8080)
