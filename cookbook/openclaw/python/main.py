import argparse
import os
import re
import time
from dataclasses import dataclass
from typing import Optional, Tuple

from agentbay import (
    AgentBay,
    Context,
    ContextSync,
    CreateSessionParams,
    SessionResult,
    SyncPolicy,
)

OPENCLAW_IMAGE_ID = "openclaw-linux-ubuntu-2204"
OPENCLAW_CONTEXT_PATH = "/home/wuying/.openclaw"
OPENCLAW_CONTEXT_NAME = "openclaw-files"
GATEWAY_PORT = 30100


def _get_env(name: str) -> Optional[str]:
    """Get environment variable from system (e.g. export AGENTBAY_API_KEY=xxx)."""
    value = os.getenv(name)
    if value is not None and value.strip():
        return value.strip()
    return None


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
    print("Checking if openclaw is in PATH...")
    cmd = "which openclaw"
    try:
        run_command(session, cmd, timeout_ms=10000)
        print("openclaw already in the PATH")
        return "openclaw"
    except RuntimeError:
        pass

    print("openclaw not found in PATH, registering to PATH...")
    cmd = "sudo ln -s $HOME/.npm-global/bin/openclaw /usr/local/bin/"
    try:
        run_command(session, cmd, timeout_ms=10000)
        print("openclaw registered to PATH")
    except RuntimeError as e:
        print(f"Warning: Failed to register openclaw to PATH: {e}")

    print("Verifying openclaw is now in PATH...")
    try:
        run_command(session, "which openclaw", timeout_ms=10000)
        print("openclaw successfully verified in PATH")
        return "openclaw"
    except RuntimeError:
        raise RuntimeError(
            "openclaw command not found in PATH after registration. "
            "Please ensure openclaw is installed in the session."
        )


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
    print(f"OpenClaw Dashboard URL: {url}")

    port_match = re.search(r'http://[^:/]+:(\d+)', url)
    if not port_match:
        raise RuntimeError(f"Failed to extract port from dashboard URL: {url}")
    port = int(port_match.group(1))

    token = None
    token_match = re.search(r'#token=([a-f0-9]+)', url)
    if token_match:
        token = token_match.group(1)

    return DashboardInfo(url=url, port=port, token=token)


def get_openclaw_weburl_outside(
    session, port: int, token: Optional[str] = None
) -> str:
    """
    Get the external web URL for OpenClaw gateway.

    Args:
        session: AgentBay session object
        port: OpenClaw gateway port (range: 30100-30199)
        token: Optional token to append to the URL

    Returns:
        External accessible HTTPS URL for web access

    Raises:
        ValueError: If port is not in the valid range [30100, 30199]
        RuntimeError: If failed to get the link
    """
    if not (30100 <= port <= 30199):
        raise ValueError(
            f"Port must be in range [30100, 30199], got {port}. "
            "This method only supports ports 30100-30199."
        )

    print(f"Getting openclaw dashboard URL (port={port})...")
    result = session.get_link(protocol_type="https", port=port)

    if result.success:
        sse_url = result.data
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
    print(f"Getting/creating context: {context_name}")
    context_result = agent_bay.context.get(context_name, create=True)
    if not context_result.success:
        raise RuntimeError(
            f"Failed to get/create context: {context_result.error_message}"
        )

    context = context_result.context
    print(f"Context ID: {context.id}")

    sync_policy = SyncPolicy.default()
    context_sync = ContextSync.new(
        context_id=context.id,
        path=OPENCLAW_CONTEXT_PATH,
        policy=sync_policy,
    )

    params = CreateSessionParams(image_id=image_id)
    params.context_syncs = [context_sync]

    print(f"Creating session with context sync (path: {OPENCLAW_CONTEXT_PATH})...")
    session_result = agent_bay.create(params)

    return session_result, context


def parse_args():
    """Parse command line arguments."""
    parser = argparse.ArgumentParser(
        description="OpenClaw session manager for AgentBay"
    )
    parser.add_argument(
        "--expose-web",
        action="store_true",
        help="Expose OpenClaw web URL outside the sandbox (ports 30100-30199)",
    )
    return parser.parse_args()


def main() -> None:
    args = parse_args()

    api_key = _get_env("AGENTBAY_API_KEY")
    if api_key is None or not api_key.strip():
        print("Error: AGENTBAY_API_KEY environment variable not set")
        return

    print("Initializing AgentBay client...")
    agent_bay = AgentBay(api_key=api_key.strip())

    session = None
    context = None
    try:
        session_result, context = create_session_with_context(
            agent_bay,
            context_name=OPENCLAW_CONTEXT_NAME,
            image_id=OPENCLAW_IMAGE_ID,
        )

        if not session_result.success:
            raise RuntimeError(session_result.error_message or "Failed to create session")

        session = session_result.session
        print(f"Session created successfully, Session ID: {session.session_id}")

        bot_cmd = detect_openclaw_command(session)
        print(f"Using bot command: {bot_cmd}")

        gateway_log = "/tmp/openclaw_gateway.log"
        dashboard_log = "/tmp/openclaw_dashboard.log"

        if args.expose_web:
            print("")
            print("Configuring gateway for external web access...")
            config_cmds = [
                f"{bot_cmd} config set gateway.port {GATEWAY_PORT}",
                f"{bot_cmd} config set gateway.mode local",
                f"{bot_cmd} config set gateway.bind lan",
                f"{bot_cmd} config set gateway.controlUi.allowedOrigins '[\"*\"]'",
                f"{bot_cmd} config set gateway.controlUi.dangerouslyDisableDeviceAuth true",
            ]
            run_command(
                session,
                " && ".join(config_cmds),
                timeout_ms=15000,
            )

        print("")
        print("Killing any existing openclaw gateway and dashboard processes...")
        session.command.execute_command(
            "pkill -f 'openclaw gateway' 2>/dev/null || true",
            timeout_ms=5000,
        )
        session.command.execute_command(
            "pkill -f 'openclaw dashboard' 2>/dev/null || true",
            timeout_ms=5000,
        )
        print("Done.")
        time.sleep(2)

        if args.expose_web:
            print("")
            print("Starting openclaw gateway in background (--port 30100)...")
            run_command(
                session,
                f"nohup {bot_cmd} gateway --port {GATEWAY_PORT} --bind lan > {gateway_log} 2>&1 &",
                timeout_ms=5000,
            )
            print("Waiting for gateway to be ready (5 seconds)...")
            time.sleep(5)
            print("Getting dashboard URL...")
            dashboard_output = run_command(
                session,
                f"{bot_cmd} dashboard --no-open 2>&1",
                timeout_ms=15000,
            )
            print(f"Dashboard output: {dashboard_output[:500] if dashboard_output else '(empty)'}")
        else:
            print("")
            print("Starting openclaw dashboard in background...")
            run_command(
                session,
                f"nohup {bot_cmd} dashboard > {dashboard_log} 2>&1 &",
                timeout_ms=5000,
            )
            print("Waiting for dashboard to start (3 seconds)...")
            time.sleep(3)
            cat_result = session.file_system.read_file(dashboard_log)
            dashboard_output = (cat_result.content or "") if cat_result.success else ""
            print(f"Dashboard log: {dashboard_output[:500] if dashboard_output else '(empty)'}")

        dashboard_info = parse_dashboard_url(dashboard_output)
        resource_url = (getattr(session, "resource_url", "") or "").strip()

        external_url = None
        if args.expose_web:
            print("")
            try:
                external_url = get_openclaw_weburl_outside(
                    session,
                    port=dashboard_info.port,
                    token=dashboard_info.token
                )
            except Exception as e:
                print(f"Warning: Failed to get external URL: {e}")
        else:
            print("")
            print(
                "Tip: Use --expose-web to get an external accessible URL "
                "for OpenClaw dashboard."
            )

        print("")
        print("=" * 60)
        print("Session Information:")
        print("=" * 60)
        print(f"  Session ID:    {session.session_id}")
        if context:
            print(f"  Context Name:  {OPENCLAW_CONTEXT_NAME}")
            print(f"  Context ID:    {context.id}")
        if external_url:
            print(f"  External Dashboard URL: {external_url}")
        if resource_url:
            print(f"  Desktop URL:   {resource_url}")
        print("=" * 60)

        print("")
        print("Press Ctrl+C to exit and release the session.")
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print("\n\nInterrupted by user.")
    finally:
        if session is not None:
            print("Cleaning up session...")
            agent_bay.delete(session)
            print("Session cleanup completed.")

    print("")
    print("Session released.")


if __name__ == "__main__":
    main()
