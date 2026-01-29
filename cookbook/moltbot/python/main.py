import os
import shlex
import sys
from dataclasses import dataclass
from typing import Optional

from agentbay import AgentBay, CreateSessionParams


MOLTBOT_IMAGE_ID = "moltbot-linux-ubuntu-2204"
MOLTBOT_CONSOLE_URL = "http://127.0.0.1:30120"


@dataclass(frozen=True)
class MoltbotEnv:
    dashscope_api_key: Optional[str]
    dingtalk_client_id: Optional[str]
    dingtalk_client_secret: Optional[str]
    feishu_app_id: Optional[str]
    feishu_app_secret: Optional[str]


def _get_optional_env(name: str) -> Optional[str]:
    value = os.getenv(name)
    if value is None:
        return None
    value = value.strip()
    if not value:
        return None
    return value


def load_moltbot_env() -> MoltbotEnv:
    return MoltbotEnv(
        dashscope_api_key=_get_optional_env("DASHSCOPE_API_KEY"),
        dingtalk_client_id=_get_optional_env("DINGTALK_CLIENT_ID"),
        dingtalk_client_secret=_get_optional_env("DINGTALK_CLIENT_SECRET"),
        feishu_app_id=_get_optional_env("FEISHU_APP_ID"),
        feishu_app_secret=_get_optional_env("FEISHU_APP_SECRET"),
    )


def build_moltbot_config_command(env: MoltbotEnv, bot_cmd: str) -> Optional[str]:
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


def wait_for_ctrl_q() -> None:
    print("")
    print("Cloud Desktop is ready.")
    print("Press Ctrl+Q in this terminal to continue and release the session.")
    try:
        if not sys.stdin.isatty():
            while True:
                ch = sys.stdin.read(1)
                if not ch:
                    raise EOFError("stdin closed before hotkey was received")
                if ch == "\x11":
                    break
            return

        if os.name == "nt":
            import msvcrt

            while True:
                ch = msvcrt.getwch()
                if ch == "\x11":
                    break
            return

        import termios
        import tty

        fd = sys.stdin.fileno()
        old_settings = termios.tcgetattr(fd)
        try:
            tty.setraw(fd)
            while True:
                ch = sys.stdin.read(1)
                if ch == "\x11":
                    break
        finally:
            termios.tcsetattr(fd, termios.TCSADRAIN, old_settings)
    except Exception:
        print("Failed to read hotkey, falling back to Enter.")
        try:
            input("Press Enter to continue...")
        except EOFError:
            return


def execute_command(session, command: str, timeout_ms: int = 50000) -> None:
    print("")
    print(f"Executing: {command}")
    result = session.command.execute_command(command, timeout_ms=timeout_ms)
    if result.success:
        output = (result.output or "").strip()
        if output:
            print(output)
        return
    raise RuntimeError(result.error_message or "Command execution failed")


def detect_moltbot_command(session) -> str:
    cmd = "command -v moltbot >/dev/null 2>&1 && echo moltbot || echo clawdbot"
    result = session.command.execute_command(cmd, timeout_ms=50000)
    if not result.success:
        raise RuntimeError(result.error_message or "Failed to detect moltbot command")
    detected = (result.output or "").strip()
    if detected not in {"moltbot", "clawdbot"}:
        raise RuntimeError(f"Unexpected bot command detected: {detected!r}")
    return detected


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
            + "curl -fsS \"$URL\" >/dev/null 2>&1 && break; "
            + "elif command -v wget >/dev/null 2>&1; then "
            + "wget -qO- \"$URL\" >/dev/null 2>&1 && break; "
            + "else "
            + "sleep 6; break; "
            + "fi; "
            + "sleep 2; "
            + "done; "
            + "nohup firefox \"$URL\" >/dev/null 2>&1 &"
        )
    )
    execute_command(session, cmd)


def main() -> None:
    api_key = os.getenv("AGENTBAY_API_KEY")
    if api_key is None or not api_key.strip():
        print("Error: AGENTBAY_API_KEY environment variable not set")
        return

    env = load_moltbot_env()

    print("Initializing AgentBay client...")
    agent_bay = AgentBay(api_key=api_key.strip())

    session = None
    try:
        print(f"Creating session with image ID: {MOLTBOT_IMAGE_ID}")
        params = CreateSessionParams(image_id=MOLTBOT_IMAGE_ID)
        session_result = agent_bay.create(params)
        if not session_result.success:
            raise RuntimeError(session_result.error_message or "Failed to create session")

        session = session_result.session
        print(f"Session created successfully, Session ID: {session.session_id}")

        bot_cmd = detect_moltbot_command(session)
        print(f"Using bot command: {bot_cmd}")

        config_cmd = build_moltbot_config_command(env, bot_cmd=bot_cmd)
        if config_cmd:
            execute_command(session, config_cmd)
        else:
            print("")
            print(
                "No provider/channel credentials found in environment variables. "
                "Skipping Moltbot configuration."
            )

        open_console_with_delay(session, MOLTBOT_CONSOLE_URL)

        resource_url = (getattr(session, "resource_url", "") or "").strip()
        if resource_url:
            print("")
            print(f"Cloud Desktop URL: {resource_url}")
        else:
            print("")
            print("Cloud Desktop URL is not available (session.resource_url is empty).")

        wait_for_ctrl_q()
    finally:
        if session is not None:
            print("")
            print("Cleaning up session...")
            agent_bay.delete(session)
            print("Session cleanup completed.")


if __name__ == "__main__":
    main()
