"""
Shared types and constants for Feishu setup.
"""

import json
import logging
from typing import Optional, Tuple

from pydantic import BaseModel, Field

from agentbay import ActOptions

logger = logging.getLogger(__name__)

# 应用信息
APP_NAME = "AgentBay的小龙虾"
APP_DESC = "AgentBay 自动创建的机器人应用"
ROBOT_NAME = "龙虾虾AgentBay"  # 机器人名称
VERSION_DESC = "auto created by agentbay"  # 版本描述
VERSION_NUMBER = "1.0.0"  # 对用户展示的正式版本号

# 飞书开放平台 URL
FEISHU_OPEN_URL = "https://open.feishu.cn/app?lang=zh-CN"
FEISHU_APP_LIST_URL = "https://open.feishu.cn/app?lang=zh-CN"

# 批量导入权限的 JSON（用于批量导入/导出权限弹窗）
_PERMISSIONS_SCOPES = {
    "scopes": {
        "tenant": [
            "contact:user.base:readonly",
            "im:chat",
            "im:chat:read",
            "im:chat:update",
            "im:message",
            "im:message.group_at_msg:readonly",
            "im:message.p2p_msg:readonly",
            "im:message:send_as_bot",
        ],
        "user": [],
    }
}
PERMISSIONS_IMPORT_JSON = json.dumps(_PERMISSIONS_SCOPES, indent=2, ensure_ascii=False)

# 需要开通的 8 个权限（保留用于兼容）
REQUIRED_PERMISSIONS = [
    ("im:chat", "获取与发送单聊、群聊消息"),
    ("im:chat:read", "读取单聊、群聊消息"),
    ("im:chat:update", "更新单聊、群聊消息"),
    ("im:message", "获取与发送单聊、群聊消息"),
    ("im:message:send_as_bot", "以应用身份发消息"),
    ("im:message.group_at_msg:readonly", "获取群组中所有@机器人的消息"),
    ("im:message.p2p_msg:readonly", "获取用户发给机器人的单聊消息"),
    ("contact:user.base:readonly", "获取用户基本信息"),
]

# 本地 feishu.json 路径，用于存放凭证
FEISHU_JSON_PATH = "/tmp/feishu.json"
FEISHU_JSON_TEMPLATE = '{"app_id":"","app_secret":""}'


class LoginPageCheckSchema(BaseModel):
    """Schema for checking if current page is Feishu login page."""

    is_login_page: bool = Field(
        ...,
        description="True if page shows login button or QR code (飞书登录页特征)",
    )
    visible_login_text: str | None = Field(
        None,
        description="Visible login-related text",
    )


class AppCreationCheckSchema(BaseModel):
    """Schema for verifying app creation success."""

    has_app_name: bool = Field(
        ...,
        description=f"页面上是否显示应用名称「{APP_NAME}」",
    )
    is_on_app_detail: bool = Field(
        ...,
        description="当前是否在应用详情页（URL 包含 open.feishu.cn/app/xxx）",
    )


class FeishuCredentialsSchema(BaseModel):
    """Schema for extracting credentials from Feishu credential page."""

    app_id: str = Field(..., description="飞书应用 App ID")
    app_secret: str = Field(..., description="飞书应用 App Secret")


class PermissionCheckSchema(BaseModel):
    """Schema for checking if permissions are granted."""

    has_all_permissions: bool = Field(
        ...,
        description="是否已开通所有必需权限",
    )
    missing_permissions: list[str] = Field(
        default_factory=list,
        description="缺失的权限列表",
    )


def update_json_field(session, json_path: str, field: str) -> None:
    """从剪贴板读取内容，更新 feishu.json 的指定字段。使用 xclip/xsel + jq。"""
    cmd = (
        f"VAL=$(xclip -o 2>/dev/null || xsel -o 2>/dev/null) && "
        f"jq --arg v \"$VAL\" '.[\"{field}\"] = $v' {json_path} > {json_path}.tmp "
        f"&& mv {json_path}.tmp {json_path} 2>/dev/null || true"
    )
    session.command.execute_command(cmd, timeout_ms=5000)


def extract_feishu_credentials(session, operator) -> Tuple[bool, Optional[str], Optional[str], str]:
    """
    提取飞书凭证：复制 App ID/Secret 到剪贴板、写入 feishu.json 并读取。

    Returns (success, app_id, app_secret, error).
    """
    fs = session.file_system
    write_ok = fs.write_file(FEISHU_JSON_PATH, FEISHU_JSON_TEMPLATE)
    if not write_ok.success:
        return False, None, None, "创建 feishu.json 失败"

    # 点击 App ID 复制按钮
    r1 = operator.act(
        ActOptions(
            action="在「应用凭证」区域，找到 App ID，点击其旁边的复制按钮",
            use_vision=True,
        )
    )
    if not r1.success:
        return False, None, None, r1.message or "点击 App ID 复制按钮失败"

    update_json_field(session, FEISHU_JSON_PATH, "app_id")

    # 点击 App Secret 复制按钮（可能需要先点击查看按钮显示完整密钥）
    r2 = operator.act(
        ActOptions(
            action="在「应用凭证」区域，找到 App Secret，若有「查看」「显示」等按钮先点击显示完整密钥，然后点击复制按钮",
            use_vision=True,
        )
    )
    if not r2.success:
        return False, None, None, r2.message or "点击 App Secret 复制按钮失败"

    update_json_field(session, FEISHU_JSON_PATH, "app_secret")

    # 读取并解析凭证
    read_res = fs.read_file(FEISHU_JSON_PATH, format="text")
    if not read_res.success or not read_res.content:
        return False, None, None, "读取 feishu.json 失败"

    try:
        data = json.loads(read_res.content)
        app_id = (data.get("app_id") or "").strip()
        app_secret = (data.get("app_secret") or "").strip()
    except json.JSONDecodeError:
        return False, None, None, "feishu.json 格式错误"

    if not app_id or not app_secret:
        return False, None, None, "提取的凭证为空"

    logger.info("Extracted Feishu credentials")
    return True, app_id, app_secret, ""
