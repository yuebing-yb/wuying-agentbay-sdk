"""
FastAPI application for OpenClaw session management.

Provides REST API endpoints for creating, querying, and deleting OpenClaw sandbox sessions.
Serves the frontend static files.
"""

import asyncio
import base64
import json
import logging
import os
from pathlib import Path
from typing import List, Optional
from urllib.parse import urlparse

import websockets

from fastapi import FastAPI, HTTPException, Request, WebSocket, WebSocketDisconnect
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
from pydantic import BaseModel, Field

from .models import CreateSessionRequest, DingtalkSetupStatus, FeishuSetupStatus, SessionResponse
from .session_manager import session_manager

# Configure logging（默认 DEBUG：本地启动便于诊断；部署时可设 LOG_LEVEL=INFO）
logging.basicConfig(
    level=logging.DEBUG,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)

# LOG_LEVEL / OPENCLAW_LOG_LEVEL 覆盖默认级别（如生产环境 INFO / WARNING）
_env_log = (os.environ.get("OPENCLAW_LOG_LEVEL") or os.environ.get("LOG_LEVEL") or "").strip().upper()
if _env_log:
    _lvl = getattr(logging, _env_log, None)
    if _lvl is not None:
        logging.getLogger().setLevel(_lvl)


def _diagnostic_log_text(text: str) -> str:
    """
    长文本日志是否截断，由环境与 logging 级别共同决定：
    - OPENCLAW_LOG_FULL=1|true|yes|on → 永不截断
    - OPENCLAW_LOG_MAX_CHARS=N → 超过 N 字符截断；N<=0 表示不截断
    - 未设置 MAX_CHARS 且当前 logger 为 DEBUG（本地默认）→ 不截断
    - 否则默认截断到 4000 字符（INFO 及以上时常用）
    """
    if not text:
        return text
    full = os.environ.get("OPENCLAW_LOG_FULL", "").strip().lower() in ("1", "true", "yes", "on")
    if full:
        return text
    raw_max = os.environ.get("OPENCLAW_LOG_MAX_CHARS", "").strip()
    if raw_max:
        try:
            n = int(raw_max)
            if n <= 0:
                return text
            max_chars = n
        except ValueError:
            max_chars = 4000
    else:
        if logger.isEnabledFor(logging.DEBUG):
            return text
        max_chars = 4000
    if len(text) <= max_chars:
        return text
    return text[:max_chars] + f"...(truncated, total_len={len(text)})"

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


class OpenClawChatRequest(BaseModel):
    """Request body for HTTP chat (fallback when WebSocket chat.delta not received)."""

    message: str = Field(..., min_length=1, description="Chat message to send")


@app.post("/api/sessions/{session_id}/openclaw-chat")
async def openclaw_chat_http(session_id: str, body: OpenClawChatRequest):
    """
    HTTP fallback for OpenClaw chat when WebSocket chat.delta is not received
    (e.g. older Gateway without sessions.messages.subscribe).
    Proxies to Gateway HTTP API.
    """
    result = session_manager.get_openclaw_https_base(session_id)
    if not result:
        raise HTTPException(status_code=404, detail="Session not found or Gateway link unavailable")
    base_url, token = result

    import httpx

    # Try OpenCodeDocs /v1/agent/run first; fallback to OpenResponses /v1/responses
    for path, payload, extra_headers in [
        (
            "/v1/agent/run",
            {"message": body.message, "sessionKey": "main", "options": {"stream": False}},
            {},
        ),
        (
            "/v1/responses",
            {"model": "openclaw", "input": body.message},
            {"x-openclaw-session-key": "main"},
        ),
    ]:
        try:
            headers = {
                "Authorization": f"Bearer {token}",
                "Content-Type": "application/json",
                **extra_headers,
            }
            async with httpx.AsyncClient(timeout=120.0) as client:
                resp = await client.post(f"{base_url}{path}", json=payload, headers=headers)
                if resp.status_code == 200:
                    data = resp.json()
                    # OpenCodeDocs: { response, runId, usage }
                    text = data.get("response") or data.get("output") or ""
                    if isinstance(text, list):
                        text = " ".join(str(x) for x in text)
                    return {"response": str(text).strip(), "ok": True}
                if resp.status_code == 404:
                    continue
                logger.warning(
                    "OpenClaw HTTP chat %s: %s %s",
                    path,
                    resp.status_code,
                    _diagnostic_log_text(resp.text),
                )
        except Exception as e:
            logger.debug("OpenClaw HTTP chat %s failed: %s", path, e)
            continue

    # Fallback: run openclaw agent in sandbox via session.command
    info = session_manager.get_session_info(session_id)
    if info and info.session:
        try:
            import asyncio

            def _run_agent():
                # Escape message for shell: use single quotes, escape single quotes as '\''
                msg_escaped = body.message.replace("'", "'\"'\"'")
                # Use --agent main for main session; --local to run embedded when Gateway has issues
                result = info.session.command.execute_command(
                    f"openclaw agent --agent main --local --message '{msg_escaped}'",
                    timeout_ms=120000,
                )
                return result.stdout or result.output or ""

            output = asyncio.to_thread(_run_agent)
            output = await output
            if output and output.strip():
                # Extract reply (agent output is typically the response text)
                return {"response": output.strip()[:8000], "ok": True}
        except Exception as e:
            logger.warning("OpenClaw CLI agent fallback failed: %s", e)

    raise HTTPException(
        status_code=502,
        detail="Gateway HTTP API unavailable (tried /v1/agent/run, /v1/responses, and CLI fallback)",
    )


@app.get("/api/sessions/{session_id}/openclaw-wss-url")
async def get_openclaw_wss_url(session_id: str):
    """
    Get the external WSS URL for OpenClaw Gateway via get_link.
    Used for connecting to OpenClaw's WebSocket API for chat/dialogue.
    Prefer using the WebSocket proxy at /api/sessions/{id}/openclaw-wss for same-origin connection.
    """
    result = session_manager.get_openclaw_wss_url(session_id)
    if not result:
        raise HTTPException(status_code=404, detail="Session not found or WSS link unavailable")
    wss_url, gateway_token = result
    return {"wssUrl": wss_url, "gatewayToken": gateway_token}


@app.websocket("/api/sessions/{session_id}/openclaw-wss")
async def openclaw_wss_proxy(websocket: WebSocket, session_id: str):
    """
    WebSocket proxy: relay between frontend and OpenClaw Gateway WSS.
    Frontend connects here (same origin); backend connects to external WSS and relays.
    """
    await websocket.accept()
    logger.info("[WSS] 前端已连接 session_id=%s", session_id)
    result = session_manager.get_openclaw_wss_url(session_id)
    if not result:
        await websocket.close(code=4004, reason="Session not found")
        return
    wss_url, gateway_token = result
    logger.info("OpenClaw WSS proxy using get_link URL (with token): %s", wss_url)

    # Origin: same host as gateway (allowedOrigins: ["*"] may not match null; use gateway origin)
    parsed = urlparse(wss_url)
    origin = f"https://{parsed.hostname}" + (f":{parsed.port}" if parsed.port else "")
    logger.info("OpenClaw WSS proxy Origin header: %s", origin)

    async def forward_to_remote():
        try:
            async with websockets.connect(
                wss_url,
                origin=origin,
                close_timeout=5,
                open_timeout=15,
            ) as ws:
                # OpenClaw Protocol v3: handle connect.challenge -> connect (token-only, like Control UI)
                first = await ws.recv()
                first_str = first if isinstance(first, str) else first.decode("utf-8")
                first_msg = json.loads(first_str)

                if (
                    first_msg.get("type") == "event"
                    and first_msg.get("event") == "connect.challenge"
                ):
                    # Send connect with auth.token (same as "打开 OpenClaw UI" token-in-URL approach)
                    connect_req = {
                        "type": "req",
                        "id": f"connect-{session_id}",
                        "method": "connect",
                        "params": {
                            "minProtocol": 3,
                            "maxProtocol": 3,
                            "client": {
                                "id": "openclaw-control-ui",
                                "version": "1.0",
                                "platform": "web",
                                "mode": "webchat",
                            },
                            "role": "operator",
                            "scopes": ["operator.read", "operator.write", "operator.admin"],
                            "auth": {"token": gateway_token},
                            "locale": "zh-CN",
                            "userAgent": "openclaw-agentbay-proxy/1.0",
                        },
                    }
                    await ws.send(json.dumps(connect_req))
                    # Forward hello-ok (or error) to client
                    second = await ws.recv()
                    second_str = second if isinstance(second, str) else second.decode("utf-8")
                    await websocket.send_text(second_str)
                    second_msg = json.loads(second_str)
                    if (
                        second_msg.get("type") == "res"
                        and not second_msg.get("ok", True)
                    ):
                        err = second_msg.get("error", {})
                        logger.warning("OpenClaw connect rejected: %s", err)
                        return
                    logger.info("[WSS] Gateway 连接成功，开始双向转发")
                else:
                    # Not connect.challenge, forward and continue
                    await websocket.send_text(first_str)
                    logger.info("[WSS] Gateway 已连接（无 challenge），开始双向转发")

                async def from_remote_to_client():
                    try:
                        msg_count = 0
                        async for msg in ws:
                            txt = msg if isinstance(msg, str) else msg.decode("utf-8")
                            msg_count += 1
                            try:
                                m = json.loads(txt)
                                t = m.get("type", "")
                                ev = m.get("event", "")
                                # 始终打印 chat 相关事件（调试无回复问题）
                                if t == "chat.delta" or ev == "chat.delta" or ev == "session.message" or t == "chat.done" or ev == "chat.done" or ev == "chat":
                                    pl = m.get("payload") or m.get("data") or {}
                                    keys = list(pl.keys()) if isinstance(pl, dict) else []
                                    try:
                                        full_msg = json.dumps(m, ensure_ascii=False)
                                    except Exception:
                                        full_msg = str(m)
                                    logger.info(
                                        "[WSS 收到Gateway] #%d type=%s event=%s id=%s keys=%s %s",
                                        msg_count,
                                        t,
                                        ev,
                                        m.get("id", ""),
                                        keys,
                                        _diagnostic_log_text(full_msg),
                                    )
                                elif msg_count <= 5:
                                    logger.info(
                                        "[WSS 收到Gateway] #%d type=%s event=%s id=%s",
                                        msg_count,
                                        t,
                                        ev or "-",
                                        m.get("id", ""),
                                    )
                            except Exception:
                                if msg_count <= 5:
                                    logger.info(
                                        "[WSS 收到Gateway] #%d raw=%s",
                                        msg_count,
                                        _diagnostic_log_text(txt),
                                    )
                            await websocket.send_text(txt)
                    except Exception as e:
                        logger.debug("Remote->client forward ended: %s", e)

                async def from_client_to_remote():
                    try:
                        while True:
                            data = await websocket.receive_text()
                            try:
                                parsed = json.loads(data)
                                method = parsed.get("method", "")
                                req_id = parsed.get("id", "")
                                logger.info(
                                    "[WSS 收到前端] id=%s method=%s payload=%s",
                                    req_id,
                                    method,
                                    _diagnostic_log_text(
                                        json.dumps(parsed.get("params", {}), ensure_ascii=False)
                                    ),
                                )
                            except Exception:
                                logger.info(
                                    "[WSS 收到前端] raw=%s",
                                    _diagnostic_log_text(data if data else ""),
                                )
                            await ws.send(data)
                    except WebSocketDisconnect:
                        logger.info("[WSS] 前端断开连接")
                        pass
                    except Exception as e:
                        logger.debug("Client->remote forward ended: %s", e)

                await asyncio.gather(
                    asyncio.create_task(from_remote_to_client()),
                    asyncio.create_task(from_client_to_remote()),
                )
        except Exception as e:
            logger.warning("OpenClaw WSS proxy connect failed: %s", e)
            try:
                await websocket.send_text(
                    json.dumps({"type": "error", "message": str(e)})
                )
            except Exception:
                pass
        finally:
            try:
                await websocket.close()
            except Exception:
                pass

    try:
        await forward_to_remote()
    except WebSocketDisconnect:
        pass


@app.get("/api/sessions", response_model=List[SessionResponse])
async def list_sessions():
    """List all active sessions (in-memory only)."""
    return session_manager.list_sessions()


class AgentBayListRequest(BaseModel):
    """Request body for listing AgentBay sessions by API key."""

    agentbay_api_key: str = Field(..., alias="agentbayApiKey", description="AgentBay API Key")

    model_config = {"populate_by_name": True}


@app.post("/api/sessions/agentbay-list")
async def list_agentbay_sessions(body: AgentBayListRequest):
    """
    List all sessions under the given AgentBay API key via AgentBay cloud API.
    Returns session IDs that can be used to restore/navigate to sessions.
    """
    from agentbay import AgentBay

    if not body.agentbay_api_key or not body.agentbay_api_key.strip():
        raise HTTPException(status_code=400, detail="agentbayApiKey cannot be empty")
    try:
        agent_bay = AgentBay(api_key=body.agentbay_api_key.strip())
        result = agent_bay.list(limit=50)
        if not result.success:
            raise HTTPException(
                status_code=502,
                detail=result.error_message or "Failed to list sessions from AgentBay",
            )
        return {"sessionIds": result.session_ids or []}
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to list AgentBay sessions: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


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
@app.get("/chat")
async def serve_index():
    """Serve the frontend index.html (SPA fallback for / and /chat)."""
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
