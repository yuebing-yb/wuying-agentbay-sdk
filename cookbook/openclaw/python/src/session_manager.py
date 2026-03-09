"""
Session manager for OpenClaw sandbox sessions.

Responsible for creating, querying, and destroying OpenClaw sandbox sessions.
All session data is stored in memory (dict), no database used.
"""

import logging
from dataclasses import dataclass, field
from datetime import datetime
from typing import Dict, List, Optional

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

    def get_session(self, session_id: str) -> Optional[SessionResponse]:
        """Get session by ID."""
        info = self._sessions.get(session_id)
        return info.to_response() if info else None

    def delete_session(self, session_id: str) -> bool:
        """Delete session by ID."""
        info = self._sessions.pop(session_id, None)
        if info is None:
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


# Global session manager instance
session_manager = SessionManager()
