"""
OpenClaw configuration file generator.

Generates openclaw.json configuration based on user input parameters.
No API keys are hardcoded - all come from frontend input.
"""

import json
from typing import Optional, Tuple

# Same path as session_manager.CONFIG_PATH to avoid circular import
_OPENCLAW_CONFIG_PATH = "/home/wuying/.openclaw/openclaw.json"


def is_not_blank(s: Optional[str]) -> bool:
    """Check if string is not None and not empty."""
    return s is not None and s.strip() != ""


def read_existing_channel_credentials(session) -> Tuple[Optional[str], Optional[str], Optional[str], Optional[str]]:
    """
    Read existing DingTalk and Feishu credentials from openclaw.json in sandbox.
    Used when applying one platform's credentials to preserve the other's.

    Returns (dingtalk_client_id, dingtalk_client_secret, feishu_app_id, feishu_app_secret).
    """
    dingtalk_client_id = None
    dingtalk_client_secret = None
    feishu_app_id = None
    feishu_app_secret = None
    try:
        read_res = session.file_system.read_file(_OPENCLAW_CONFIG_PATH, format="text")
        if not read_res.success or not read_res.content:
            return dingtalk_client_id, dingtalk_client_secret, feishu_app_id, feishu_app_secret
        config = json.loads(read_res.content)
        channels = config.get("channels") or {}
        # DingTalk - only use if enabled (real credentials, not placeholders)
        dt = channels.get("dingtalk") or {}
        if dt.get("enabled") and is_not_blank(dt.get("clientId")) and is_not_blank(dt.get("clientSecret")):
            dingtalk_client_id = (dt.get("clientId") or "").strip()
            dingtalk_client_secret = (dt.get("clientSecret") or "").strip()
        # Feishu - only use if enabled
        fs = channels.get("feishu") or {}
        if fs.get("enabled") and is_not_blank(fs.get("appId")) and is_not_blank(fs.get("appSecret")):
            feishu_app_id = (fs.get("appId") or "").strip()
            feishu_app_secret = (fs.get("appSecret") or "").strip()
    except (json.JSONDecodeError, KeyError, TypeError):
        pass
    return dingtalk_client_id, dingtalk_client_secret, feishu_app_id, feishu_app_secret


def build_config(
    bailian_api_key: str,
    dingtalk_client_id: Optional[str] = None,
    dingtalk_client_secret: Optional[str] = None,
    feishu_app_id: Optional[str] = None,
    feishu_app_secret: Optional[str] = None,
    model_base_url: Optional[str] = None,
    model_id: Optional[str] = None,
) -> str:
    """
    Build openclaw.json configuration content.

    Args:
        bailian_api_key: Bailian API Key
        dingtalk_client_id: DingTalk Client ID (optional)
        dingtalk_client_secret: DingTalk Client Secret (optional)
        feishu_app_id: Feishu App ID (optional)
        feishu_app_secret: Feishu App Secret (optional)
        model_base_url: Model Base URL (optional)
        model_id: Model ID (optional)

    Returns:
        Configuration file JSON string
    """
    # Default values
    actual_base_url = (
        model_base_url
        if is_not_blank(model_base_url)
        else "https://dashscope.aliyuncs.com/compatible-mode/v1"
    )
    actual_model_id = (
        model_id if is_not_blank(model_id) else "qwen3-max-2026-01-23"
    )

    # Determine if channels are enabled
    feishu_enabled = is_not_blank(feishu_app_id) and is_not_blank(feishu_app_secret)
    dingtalk_enabled = is_not_blank(dingtalk_client_id) and is_not_blank(
        dingtalk_client_secret
    )

    config = {
        "meta": {
            "lastTouchedVersion": "2026.3.2",
            "lastTouchedAt": "2026-03-03T09:42:12.612Z",
        },
        "wizard": {
            "lastRunAt": "2026-03-03T09:42:12.553Z",
            "lastRunVersion": "2026.3.2",
            "lastRunCommand": "configure",
            "lastRunMode": "local",
        },
        "models": {
            "mode": "merge",
            "providers": {
                "bailian": {
                    "baseUrl": actual_base_url,
                    "apiKey": bailian_api_key,
                    "api": "openai-completions",
                    "models": [
                        {
                            "id": actual_model_id,
                            "name": actual_model_id,
                            "reasoning": False,
                            "input": ["text"],
                            "cost": {
                                "input": 0.0025,
                                "output": 0.01,
                                "cacheRead": 0,
                                "cacheWrite": 0,
                            },
                            "contextWindow": 262144,
                            "maxTokens": 65536,
                        }
                    ],
                }
            },
        },
        "agents": {
            "defaults": {
                "workspace": "/home/wuying/.openclaw/workspace",
                "model": {"primary": f"bailian/{actual_model_id}"},
                "models": {f"bailian/{actual_model_id}": {"alias": actual_model_id}},
                "compaction": {"mode": "safeguard"},
                "maxConcurrent": 4,
                "subagents": {"maxConcurrent": 8},
            }
        },
        "tools": {"profile": "messaging"},
        "messages": {"ackReactionScope": "group-mentions"},
        "commands": {
            "native": "auto",
            "nativeSkills": "auto",
            "restart": True,
            "ownerDisplay": "raw",
        },
        "session": {"dmScope": "per-channel-peer"},
        "channels": {
            "feishu": {
                "enabled": feishu_enabled,
                "appId": feishu_app_id if feishu_enabled else "feishu_app_id",
                "appSecret": feishu_app_secret if feishu_enabled else "feishu_app_secret",
                "connectionMode": "websocket",
                "domain": "feishu",
                "groupPolicy": "open",
            },
            "dingtalk": {
                "enabled": dingtalk_enabled,
                "clientId": dingtalk_client_id if dingtalk_enabled else "dingxxxx",
                "clientSecret": dingtalk_client_secret
                if dingtalk_enabled
                else "xxx-xxx-xxx",
                "dmPolicy": "open",
                "groupPolicy": "open",
                "messageType": "markdown",
            },
        },
        "gateway": {
            "port": 30100,
            "mode": "local",
            "bind": "lan",
            "controlUi": {
                "allowedOrigins": ["*"],
                "dangerouslyDisableDeviceAuth": True,
                "allowInsecureAuth": True,
            },
            "auth": {
                "mode": "token",
                "token": "4decb1b9ff4997825eb91e37bf28798e0af1f7f00c6b4b1c",
            },
            "tailscale": {"mode": "off", "resetOnExit": False},
            "nodes": {
                "denyCommands": [
                    "camera.snap",
                    "camera.clip",
                    "screen.record",
                    "contacts.add",
                    "calendar.add",
                    "reminders.add",
                    "sms.send",
                ]
            },
        },
        "plugins": {
            "load": {"paths": ["/opt/openclaw/openclaw-channel-dingtalk"]},
            "entries": {"dingtalk": {"enabled": True}},
            "installs": {
                "dingtalk": {
                    "source": "path",
                    "sourcePath": "/opt/openclaw/openclaw-channel-dingtalk",
                    "installPath": "/opt/openclaw/openclaw-channel-dingtalk",
                    "version": "3.1.4",
                    "installedAt": "2026-03-03T09:18:01.176Z",
                }
            },
        },
    }

    return json.dumps(config, indent=2, ensure_ascii=False)
