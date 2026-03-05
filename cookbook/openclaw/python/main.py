import argparse
import json
import os
import re
import shlex
import time
from dataclasses import dataclass
from pathlib import Path
from typing import Optional, Tuple

from dotenv import load_dotenv

from agentbay import (
    AgentBay,
    Context,
    ContextSync,
    CreateSessionParams,
    SessionResult,
    SyncPolicy,
)

OPENCLAW_IMAGE_ID = "imgc-0a8urjaf5l1v84ny5"
OPENCLAW_CONTEXT_PATH = "/home/wuying/.openclaw"

# Deferred .env loading - only load as fallback when env var is not found in system
_dotenv_loaded = False
_dotenv_path: Optional[Path] = None


def _init_dotenv_path():
    """Initialize the .env file path from project root."""
    global _dotenv_path
    if _dotenv_path is not None:
        return
    script_dir = Path(__file__).resolve().parent
    dotenv_path = script_dir.parent.parent.parent / ".env"
    if dotenv_path.exists():
        _dotenv_path = dotenv_path


def _get_env_with_fallback(name: str) -> Optional[str]:
    """Get environment variable with priority: 1) System env, 2) .env file."""
    global _dotenv_loaded

    # Priority 1: System environment variable
    value = os.getenv(name)
    if value is not None and value.strip():
        return value.strip()

    # Priority 2: Load .env as fallback if not already loaded
    if not _dotenv_loaded and _dotenv_path is not None:
        load_dotenv(dotenv_path=_dotenv_path)
        _dotenv_loaded = True
        # Retry getting the value after loading .env
        value = os.getenv(name)
        if value is not None and value.strip():
            return value.strip()

    return None


# Initialize .env path (but don't load it yet)
_init_dotenv_path()


@dataclass(frozen=True)
class OpenClawEnv:
    dashscope_api_key: Optional[str]
    dingtalk_client_id: Optional[str]
    dingtalk_client_secret: Optional[str]
    feishu_app_id: Optional[str]
    feishu_app_secret: Optional[str]


def _get_optional_env(name: str) -> Optional[str]:
    return _get_env_with_fallback(name)


def load_openclaw_env() -> OpenClawEnv:
    return OpenClawEnv(
        dashscope_api_key=_get_optional_env("DASHSCOPE_API_KEY"),
        dingtalk_client_id=_get_optional_env("DINGTALK_CLIENT_ID"),
        dingtalk_client_secret=_get_optional_env("DINGTALK_CLIENT_SECRET"),
        feishu_app_id=_get_optional_env("FEISHU_APP_ID"),
        feishu_app_secret=_get_optional_env("FEISHU_APP_SECRET"),
    )


def build_openclaw_config_command(env: OpenClawEnv, bot_cmd: str) -> Optional[str]:
    parts: list[str] = []
    if env.dashscope_api_key:
        parts.append(
            f"{bot_cmd} config set models.providers.bailian.apiKey "
            f"{shlex.quote(env.dashscope_api_key)}"
        )
    if env.feishu_app_id and env.feishu_app_secret:
        parts.append(
            f"{bot_cmd} config set channels.feishu.appId {shlex.quote(env.feishu_app_id)}"
        )
        parts.append(
            f"{bot_cmd} config set channels.feishu.appSecret {shlex.quote(env.feishu_app_secret)}"
        )
    elif env.feishu_app_id or env.feishu_app_secret:
        raise ValueError(
            "FEISHU_APP_ID and FEISHU_APP_SECRET must be both set, or both unset"
        )
    if env.dingtalk_client_id and env.dingtalk_client_secret:
        parts.append(
            f"{bot_cmd} config set channels.dingtalk.clientId "
            f"{shlex.quote(env.dingtalk_client_id)}"
        )
        parts.append(
            f"{bot_cmd} config set channels.dingtalk.clientSecret "
            f"{shlex.quote(env.dingtalk_client_secret)}"
        )
    elif env.dingtalk_client_id or env.dingtalk_client_secret:
        raise ValueError(
            "DINGTALK_CLIENT_ID and DINGTALK_CLIENT_SECRET must be both set, or both unset"
        )
    if not parts:
        return None
    parts.append(f"{bot_cmd} gateway restart")
    return " && ".join(parts)


def run_command(session, command: str, timeout_ms: int = 50000) -> str:
    """Execute command and return output. Prints the command before execution and result after."""
    print(f"[CMD]: {command}")
    result = session.command.execute_command(command, timeout_ms=timeout_ms)
    if result.success:
        output = (result.output or "").strip()
        print(f"[OUTPUT]: {output if output else '(no output)'}")
        return output
    else:
        error_msg = result.error_message or "Command execution failed"
        print(f"[ERROR]: {error_msg}")
        raise RuntimeError(error_msg)


def detect_openclaw_command(session) -> str:
    """Detect which openclaw command is available in the session."""
    # First, check if openclaw is in PATH
    print("Checking if openclaw is in PATH...")
    cmd = "which openclaw"
    try:
        run_command(session, cmd, timeout_ms=10000)
        print("openclaw already in the PATH")
        return "openclaw"
    except RuntimeError:
        pass  # openclaw not in PATH, fall through to registration below

    # openclaw not in PATH, try to register it
    print("openclaw not found in PATH, registering to PATH...")
    cmd = "sudo ln -s $HOME/.npm-global/bin/openclaw /usr/local/bin/"
    try:
        run_command(session, cmd, timeout_ms=10000)
        print("openclaw registered to PATH")
    except RuntimeError as e:
        print(f"Warning: Failed to register openclaw to PATH: {e}")

    return "openclaw"


def open_console_with_delay(session, url: str) -> None:
    quoted_url = shlex.quote(url)
    cmd = (
        "bash -lc "
        + shlex.quote(
            "URL="
            + quoted_url
            + "; "
            + "for i in $(seq 1 15); do "
            + "if command -v curl >/dev/null 2>&1; then "
            + 'curl -fsS "$URL" >/dev/null 2>&1 && break; '
            + "elif command -v wget >/dev/null 2>&1; then "
            + 'wget -qO- "$URL" >/dev/null 2>&1 && break; '
            + "else "
            + "sleep 6; break; "
            + "fi; "
            + "sleep 2; "
            + "done; "
            + 'nohup firefox "$URL" >/dev/null 2>&1 &'
        )
    )
    run_command(session, cmd)


@dataclass(frozen=True)
class DashboardInfo:
    """Parsed information from openclaw dashboard command."""
    url: str
    port: int
    token: Optional[str]


def parse_dashboard_url(dashboard_output: str) -> DashboardInfo:
    """
    Parse the dashboard URL to extract port and token.

    Args:
        dashboard_output: Output from 'openclaw dashboard' command

    Returns:
        DashboardInfo with url, port, and token

    Raises:
        RuntimeError: If failed to parse the dashboard URL
    """
    url_match = re.search(r'http://[^\s]+', dashboard_output)
    if not url_match:
        raise RuntimeError(f"Failed to parse dashboard URL from output: {dashboard_output}")

    url = url_match.group(0)
    print(f"Dashboard URL: {url}")

    # Extract port from URL (e.g., http://localhost:30100/...)
    port_match = re.search(r'http://[^:/]+:(\d+)', url)
    if not port_match:
        raise RuntimeError(f"Failed to extract port from dashboard URL: {url}")
    port = int(port_match.group(1))

    # Extract token from URL fragment (e.g., #token=xxx)
    token = None
    token_match = re.search(r'#token=([a-f0-9]+)', url)
    if token_match:
        token = token_match.group(1)

    return DashboardInfo(url=url, port=port, token=token)


def get_openclaw_sse_url(session, port: int, token: Optional[str] = None) -> str:
    """
    Get the external SSE access URL for OpenClaw gateway.

    Args:
        session: AgentBay session object
        port: OpenClaw gateway port (range: 30100-30199)
        token: Optional token to append to the URL

    Returns:
        External accessible HTTPS URL for SSE connection

    Raises:
        RuntimeError: If failed to get the link
    """
    # if not (30100 <= port <= 30199):
    #     raise ValueError(f"Port must be in range [30100, 30199], got {port}")

    print(f"Getting openclaw dashboard URL (port={port})...")
    result = session.get_link(protocol_type="https", port=port)

    if result.success:
        sse_url = result.data
        # Append token if provided
        if token:
            sse_url = f"{sse_url}/#token={token}"
        print(f"SSE URL: {sse_url}")
        return sse_url
    else:
        raise RuntimeError(f"Failed to get SSE link: {result.error_message}")


def create_session_with_context(
    agent_bay: AgentBay,
    context_name: str,
    image_id: str,
) -> Tuple[SessionResult, Context]:
    """
    Create a session with OpenClaw Skills context synchronization.

    Args:
        agent_bay: AgentBay client
        context_name: Name of the context to use/create
        image_id: Image ID for the session

    Returns:
        Tuple of (session_result, context)

    Raises:
        RuntimeError: If context or session creation fails
    """
    # Get or create context
    print(f"Getting/creating context: {context_name}")
    context_result = agent_bay.context.get(context_name, create=True)
    if not context_result.success:
        raise RuntimeError(
            f"Failed to get/create context: {context_result.error_message}"
        )

    context = context_result.context
    print(f"Context ID: {context.id}")

    # Configure sync policy
    sync_policy = SyncPolicy.default()

    # Configure ContextSync - sync OpenClaw config directory
    context_sync = ContextSync.new(
        context_id=context.id,
        path=OPENCLAW_CONTEXT_PATH,
        policy=sync_policy,
    )

    # Create session with context sync
    params = CreateSessionParams(image_id=image_id)
    params.context_syncs = [context_sync]

    print(f"Creating session with context sync (path: {OPENCLAW_CONTEXT_PATH})...")
    session_result = agent_bay.create(params)

    return session_result, context


def reset_context(agent_bay: AgentBay, context_name: str) -> None:
    """
    Reset (clear all data in) a context.

    Args:
        agent_bay: AgentBay client
        context_name: Name of the context to reset

    Raises:
        RuntimeError: If context reset fails
    """
    print(f"Getting context: {context_name}")
    context_result = agent_bay.context.get(context_name, create=False)
    if not context_result.success:
        raise RuntimeError(f"Failed to get context: {context_result.error_message}")

    context = context_result.context
    print(f"Context ID: {context.id}")
    print(f"Clearing context data...")

    clear_result = agent_bay.context.clear(context.id, timeout=60)
    if not clear_result.success:
        raise RuntimeError(f"Failed to clear context: {clear_result.error_message}")

    print(f"Context '{context_name}' cleared successfully")


def parse_args():
    """Parse command line arguments."""
    parser = argparse.ArgumentParser(
        description="OpenClaw AgentBay Cookbook - Run OpenClaw in cloud environment"
    )
    parser.add_argument(
        "--no-sse",
        action="store_true",
        help="Skip getting SSE URL via get_link()",
    )
    parser.add_argument(
        "--no-context",
        action="store_true",
        help="Disable Context synchronization",
    )
    parser.add_argument(
        "--context",
        type=str,
        default="openclaw-skills",
        metavar="NAME",
        help="Context name for OpenClaw Skills synchronization (default: openclaw-skills)",
    )
    parser.add_argument(
        "--reset-context",
        type=str,
        default=None,
        metavar="NAME",
        help="Reset (clear all data in) the specified context and exit",
    )
    return parser.parse_args()


def main() -> None:
    args = parse_args()

    api_key = _get_env_with_fallback("AGENTBAY_API_KEY")
    if api_key is None or not api_key.strip():
        print("Error: AGENTBAY_API_KEY environment variable not set")
        return

    env = load_openclaw_env()

    print("Initializing AgentBay client...")
    agent_bay = AgentBay(api_key=api_key.strip())

    # Handle --reset-context flag
    if args.reset_context:
        try:
            reset_context(agent_bay, args.reset_context)
        except Exception as e:
            print(f"Error resetting context: {e}")
        return

    session = None
    context = None
    try:
        # Create session with or without context
        if not args.no_context:
            session_result, context = create_session_with_context(
                agent_bay,
                context_name=args.context,
                image_id=OPENCLAW_IMAGE_ID,
            )
        else:
            print(f"Creating session with image ID: {OPENCLAW_IMAGE_ID}")
            params = CreateSessionParams(image_id=OPENCLAW_IMAGE_ID)
            session_result = agent_bay.create(params)

        if not session_result.success:
            raise RuntimeError(session_result.error_message or "Failed to create session")

        session = session_result.session
        print(f"Session created successfully, Session ID: {session.session_id}")

        bot_cmd = detect_openclaw_command(session)
        print(f"Using bot command: {bot_cmd}")

        config_cmd = build_openclaw_config_command(env, bot_cmd=bot_cmd)
        if config_cmd:
            run_command(session, config_cmd)
        else:
            print("")
            print(
                "No provider/channel credentials found in environment variables. "
                "Skipping OpenClaw configuration."
            )

        # Get dashboard URL from openclaw dashboard command first
        # This gives us the port and token needed for SSE URL
        # Note: `openclaw dashboard` command prints URL then blocks, so we use timeout
        # and extract URL from stdout even on timeout
        print("")
        print("Getting dashboard URL...")
        dashboard_output = ""
        try:
            dashboard_output = run_command(session, f"{bot_cmd} dashboard", timeout_ms=10000)
        except RuntimeError as e:
            # Even on timeout, the stdout may contain the URL
            error_msg = str(e)
            # Try to extract stdout from error message (JSON format)
            try:
                error_data = json.loads(error_msg)
                dashboard_output = error_data.get("stdout", "")
            except json.JSONDecodeError:
                dashboard_output = ""

        # Parse dashboard URL to extract port and token
        dashboard_info = parse_dashboard_url(dashboard_output)

        # Get SSE access URL via get_link() using port from dashboard
        sse_url = None
        if not args.no_sse:
            print("")
            try:
                sse_url = get_openclaw_sse_url(
                    session,
                    port=dashboard_info.port,
                    token=dashboard_info.token
                )
            except Exception as e:
                print(f"Warning: Failed to get SSE URL: {e}")

        # open_console_with_delay(session, console_url)

        resource_url = (getattr(session, "resource_url", "") or "").strip()

        # Print summary
        print("")
        print("=" * 60)
        print("Session Information:")
        print("=" * 60)
        print(f"  Session ID:    {session.session_id}")
        if context:
            print(f"  Context Name:  {args.context}")
            print(f"  Context ID:    {context.id}")
        if sse_url:
            print(f"  openclaw dashboard URL:       {sse_url}")
        # print(f"  Dashboard URL: {console_url}")
        if resource_url:
            print(f"  Desktop URL:   {resource_url}")
        print("=" * 60)

        # Hold and wait for user to press Ctrl+C
        print("")
        print("Press Ctrl+C to exit and release the session.")
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print("\n\nInterrupted by user.")
    finally:
        # Delete session before exiting
        if session is not None:
            print("")
            print("Cleaning up session...")
            agent_bay.delete(session)
            print("Session cleanup completed.")

    print("")
    print("Session released.")


if __name__ == "__main__":
    main()
