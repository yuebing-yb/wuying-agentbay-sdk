"""
Session manager for OpenClaw sandbox sessions.

Responsible for creating, querying, and destroying OpenClaw sandbox sessions.
Session restore relies on frontend passing form_data (X-OpenClaw-Form-Data header).
"""

import asyncio
import logging
from dataclasses import dataclass, field
from datetime import datetime
from typing import Any, Dict, List, Optional

from agentbay import AgentBay, ContextSync, CreateSessionParams, SyncPolicy, UploadMode

from .config_builder import build_config
from .models import CreateSessionRequest, SessionInfo, SessionResponse

logger = logging.getLogger(__name__)

# Constants
OPENCLAW_IMAGE_ID = "openclaw-linux-ubuntu-2204"
CONFIG_PATH = "/home/wuying/.openclaw/openclaw.json"
GATEWAY_PORT = 30100
GATEWAY_TOKEN = "4decb1b9ff4997825eb91e37bf28798e0af1f7f00c6b4b1c"
CONTEXT_SYNC_PATH = "/home/wuying/.openclaw/"


@dataclass
class SessionManager:
    """Session manager for OpenClaw sandbox sessions."""

    # In-memory session storage
    _sessions: Dict[str, SessionInfo] = field(default_factory=dict)
    # DingTalk setup state per session: {session_id: {"step": str, "client_id": str, "client_secret": str, "error": str}}
    _dingtalk_setup: Dict[str, dict] = field(default_factory=dict)
    # Feishu setup state per session: {session_id: {"step": str, "app_id": str, "app_secret": str, "error": str}}
    _feishu_setup: Dict[str, dict] = field(default_factory=dict)

    def _execute_command(self, session, command: str, timeout_ms: int = 30000) -> str:
        """Execute command and return output."""
        logger.debug(f"Executing command: {command}")
        result = session.command.execute_command(command, timeout_ms=timeout_ms)
        if result.output:
            logger.debug(f"Command output: {result.output[:200]}")
        if not result.success:
            logger.error(f"Command failed: {result.error_message}")
        return result.output or ""

    def create_session(self, request: CreateSessionRequest) -> SessionResponse:
        """
        Create a new OpenClaw sandbox session.

        Flow:
        1. Create AgentBay Session (using API Key from request)
        2. Detect available bot command in sandbox
        3. Generate and write openclaw.json config
        4. Stop old gateway -> Start new gateway in background
        5. Wait for gateway to be ready
        6. Get OpenClaw UI external link via getLink
        7. Return resource_url + openclawUrl
        """
        logger.info(f"Creating AgentBay session for user {request.username}...")

        # 1. Create client with API Key from request, configure Context persistence
        agent_bay = AgentBay(api_key=request.agentbay_api_key)
        session = None

        try:
            # Get or create persistent Context based on username
            context_name = f"openclaw-{request.username}"
            logger.info(f"Getting/creating persistent Context: {context_name}")
            context_result = agent_bay.context.get(context_name, create=True)
            if not context_result.success:
                raise RuntimeError(f"Failed to get Context: {context_result.error_message}")
            context_id = context_result.context.id
            logger.info(f"Context ready: id={context_id}")

            # Configure sync policy with archive mode
            sync_policy = SyncPolicy.default()
            sync_policy.upload_policy.upload_mode = UploadMode.ARCHIVE
            sync_policy.extract_policy.delete_src_file = True
            sync_policy.extract_policy.extract_current_folder = True
            sync_policy.extract_policy.extract = True

            context_sync = ContextSync.new(
                context_id=context_id,
                path=CONTEXT_SYNC_PATH,
                policy=sync_policy,
                beta_wait_for_completion=True,
            )

            params = CreateSessionParams(image_id=OPENCLAW_IMAGE_ID)
            params.context_syncs = [context_sync]

            session_result = agent_bay.create(params)
            if not session_result.success:
                raise RuntimeError(f"Failed to create session: {session_result.error_message}")
            session = session_result.session

        except Exception as e:
            logger.error(f"Failed to create session: {e}")
            raise RuntimeError(f"Failed to create session: {e}")

        logger.info(f"Session created successfully: {session.session_id}")

        try:
            # 2. Bot command is fixed as 'openclaw'
            bot_cmd = "openclaw"

            # 3. Generate config and write to sandbox
            logger.info("Writing OpenClaw configuration file...")
            config_json = build_config(
                bailian_api_key=request.bailian_api_key,
                dingtalk_client_id=request.dingtalk_client_id,
                dingtalk_client_secret=request.dingtalk_client_secret,
                feishu_app_id=request.feishu_app_id,
                feishu_app_secret=request.feishu_app_secret,
                model_base_url=request.model_base_url,
                model_id=request.model_id,
            )
            session.file_system.write(CONFIG_PATH, config_json)
            logger.info("Configuration file written successfully")

            # 4. Stop old gateway
            logger.info("Stopping old gateway process...")
            self._execute_command(
                session,
                "openclaw gateway stop; pkill -f 'openclaw gateway' || true",
                timeout_ms=10000,
            )

            # 5. Start new gateway in background
            logger.info("Starting gateway in background...")
            self._execute_command(
                session,
                f"bash -lc 'nohup {bot_cmd} gateway > /tmp/gateway.log 2>&1 &'",
                timeout_ms=15000,
            )

            # 6. Wait for gateway to be ready and open dashboard in sandbox
            dashboard_url = f"http://127.0.0.1:{GATEWAY_PORT}/#token={GATEWAY_TOKEN}"
            logger.info("Waiting for gateway to be ready...")
            self._execute_command(
                session,
                f"bash -lc '"
                f"for i in $(seq 1 15); do "
                f"curl -fsS http://127.0.0.1:{GATEWAY_PORT} >/dev/null 2>&1 && break; "
                f"sleep 2; "
                f"done; "
                f'nohup firefox "{dashboard_url}" >/dev/null 2>&1 &'
                f"'",
                timeout_ms=60000,
            )

            # 7. Get OpenClaw UI external access link via getLink
            openclaw_url = ""
            try:
                link_result = session.get_link(protocol_type="https", port=GATEWAY_PORT)
                if link_result.success:
                    openclaw_url = f"{link_result.data}/#token={GATEWAY_TOKEN}"
                    logger.info(f"OpenClaw UI link: {openclaw_url}")
                else:
                    logger.warning(f"Failed to get OpenClaw UI link: {link_result.error_message}")
            except Exception as e:
                logger.warning(f"Exception getting OpenClaw UI link: {e}")

            # 8. Save to memory and return
            now = datetime.now().isoformat()
            info = SessionInfo(
                session_id=session.session_id,
                resource_url=getattr(session, "resource_url", "") or "",
                openclaw_url=openclaw_url,
                username=request.username,
                created_at=now,
                status="running",
                agent_bay=agent_bay,
                session=session,
                create_request=request,
            )

            self._sessions[session.session_id] = info

            logger.info(
                f"Session started! sessionId={session.session_id}, resourceUrl={info.resource_url}"
            )

            return info.to_response()

        except Exception as e:
            logger.error(f"Error during session creation, cleaning up...", exc_info=True)
            if session:
                try:
                    agent_bay.delete(session)
                except Exception:
                    pass
            raise RuntimeError(f"Failed to create session: {e}")

    def get_session(
        self,
        session_id: str,
        form_data: Optional[Dict[str, Any]] = None,
    ) -> Optional[SessionResponse]:
        """Get session by ID. If not in memory, restore via AgentBay API (requires form_data from frontend)."""
        info = self._sessions.get(session_id)
        if info:
            return info.to_response()

        # Restore: requires form_data from X-OpenClaw-Form-Data header (agentbayApiKey, etc.)
        api_key = (form_data or {}).get("agentbayApiKey") or (form_data or {}).get("agentbay_api_key")
        if not form_data or not api_key:
            return None

        username = form_data.get("username") or "unknown"
        created_at = datetime.now().isoformat()
        create_request: Optional[CreateSessionRequest] = None
        try:
            create_request = CreateSessionRequest.model_validate(form_data)
        except Exception:
            pass

        try:
            agent_bay = AgentBay(api_key=api_key)
            result = agent_bay.get(session_id)
            if not result.success:
                logger.info(f"Session {session_id} not found on AgentBay cloud: {result.error_message}")
                return None

            session = result.session
            resource_url = getattr(session, "resource_url", "") or ""
            status = "running"

            # Get OpenClaw UI link
            openclaw_url = ""
            try:
                link_result = session.get_link(protocol_type="https", port=GATEWAY_PORT)
                if link_result.success:
                    openclaw_url = f"{link_result.data}/#token={GATEWAY_TOKEN}"
            except Exception as e:
                logger.warning(f"Failed to get OpenClaw link for restored session: {e}")

            info = SessionInfo(
                session_id=session_id,
                resource_url=resource_url,
                openclaw_url=openclaw_url,
                username=username,
                created_at=created_at,
                status=status,
                agent_bay=agent_bay,
                session=session,
                create_request=create_request,
            )
            self._sessions[session_id] = info
            logger.info(f"Restored session {session_id} via AgentBay API")
            return info.to_response()

        except Exception as e:
            logger.warning(f"Failed to restore session {session_id} via AgentBay API: {e}")
            return None

    def get_session_info(self, session_id: str) -> Optional[SessionInfo]:
        """Get full SessionInfo (for internal use e.g. dingtalk setup)."""
        return self._sessions.get(session_id)

    def restart_dashboard(self, session_id: str) -> tuple[bool, str]:
        """
        Restart dashboard (kill Firefox and reopen with OpenClaw UI) in sandbox.
        Called when user clicks "打开 OpenClaw UI".

        Returns (success, error_message).
        """
        info = self._sessions.get(session_id)
        if not info or not info.session:
            return False, "Session not found"
        session = info.session
        try:
            dashboard_url = f"http://127.0.0.1:{GATEWAY_PORT}/#token={GATEWAY_TOKEN}"
            self._execute_command(session, "pkill -f firefox || true", timeout_ms=5000)
            self._execute_command(
                session,
                f"bash -lc '"
                f"for i in $(seq 1 15); do "
                f"curl -fsS http://127.0.0.1:{GATEWAY_PORT} >/dev/null 2>&1 && break; "
                f"sleep 2; "
                f"done; "
                f'nohup firefox "{dashboard_url}" >/dev/null 2>&1 &'
                f"'",
                timeout_ms=60000,
            )
            logger.info("Dashboard restarted for session %s", session_id)
            return True, ""
        except Exception as e:
            logger.exception("Failed to restart dashboard for session %s", session_id)
            return False, str(e)

    def delete_session(self, session_id: str) -> bool:
        """Delete session by ID. Restores via form_data if not in memory."""
        info = self._sessions.pop(session_id, None)
        self.clear_dingtalk_setup_state(session_id)
        self.clear_feishu_setup_state(session_id)
        if info is None:
            # Not in memory - cannot restore without form_data (no persisted file)
            return False

        try:
            if info.session:
                # delete() will sync Context data before destroying
                info.session.delete()
                logger.info(f"Session {session_id} destroyed (Context synced)")
        except Exception as e:
            logger.error(f"Error destroying session {session_id}: {e}")

        return True

    def list_sessions(self) -> List[SessionResponse]:
        """List all active sessions."""
        return [info.to_response() for info in self._sessions.values()]

    def get_dingtalk_setup_state(self, session_id: str) -> Optional[dict]:
        """Get DingTalk setup state for session."""
        return self._dingtalk_setup.get(session_id)

    def set_dingtalk_setup_state(
        self,
        session_id: str,
        step: str,
        client_id: Optional[str] = None,
        client_secret: Optional[str] = None,
        error: Optional[str] = None,
        backend: Optional[str] = None,
        applied: Optional[bool] = None,
        apply_error: Optional[str] = None,
    ) -> None:
        """Update DingTalk setup state."""
        state = self._dingtalk_setup.get(session_id) or {}
        state["step"] = step
        if step == "done":
            try:
                from .dingtalk_setup_playwright import clear_dingtalk_browser_cache
                clear_dingtalk_browser_cache(session_id)
            except ImportError:
                pass
        if client_id is not None:
            state["client_id"] = client_id
        if client_secret is not None:
            state["client_secret"] = client_secret
        if error is not None:
            state["error"] = error
        if backend is not None:
            state["backend"] = backend
        if applied is not None:
            state["applied"] = applied
        if apply_error is not None:
            state["apply_error"] = apply_error
        self._dingtalk_setup[session_id] = state

    def clear_dingtalk_setup_state(self, session_id: str) -> None:
        """Clear DingTalk setup state when session is deleted."""
        self._dingtalk_setup.pop(session_id, None)
        try:
            from .dingtalk_setup_playwright import clear_dingtalk_browser_cache
            clear_dingtalk_browser_cache(session_id)
        except ImportError:
            pass

    def get_feishu_setup_state(self, session_id: str) -> Optional[dict]:
        """Get Feishu setup state for session."""
        return self._feishu_setup.get(session_id)

    def set_feishu_setup_state(
        self,
        session_id: str,
        step: str,
        app_id: Optional[str] = None,
        app_secret: Optional[str] = None,
        error: Optional[str] = None,
        backend: Optional[str] = None,
        applied: Optional[bool] = None,
        apply_error: Optional[str] = None,
    ) -> None:
        """Update Feishu setup state."""
        state = self._feishu_setup.get(session_id) or {}
        state["step"] = step
        if step == "done":
            try:
                from .feishu_setup_playwright import clear_feishu_browser_cache
                try:
                    loop = asyncio.get_running_loop()
                    loop.create_task(clear_feishu_browser_cache(session_id))
                except RuntimeError:
                    asyncio.run(clear_feishu_browser_cache(session_id))
            except ImportError:
                pass
        if app_id is not None:
            state["app_id"] = app_id
        if app_secret is not None:
            state["app_secret"] = app_secret
        if error is not None:
            state["error"] = error
        if backend is not None:
            state["backend"] = backend
        if applied is not None:
            state["applied"] = applied
        if apply_error is not None:
            state["apply_error"] = apply_error
        self._feishu_setup[session_id] = state

    def clear_feishu_setup_state(self, session_id: str) -> None:
        """Clear Feishu setup state when session is deleted."""
        self._feishu_setup.pop(session_id, None)
        try:
            from .feishu_setup_playwright import clear_feishu_browser_cache
            try:
                loop = asyncio.get_running_loop()
                loop.create_task(clear_feishu_browser_cache(session_id))
            except RuntimeError:
                asyncio.run(clear_feishu_browser_cache(session_id))
        except ImportError:
            pass


# Global session manager instance
session_manager = SessionManager()
