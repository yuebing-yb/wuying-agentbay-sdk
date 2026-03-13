"""
Shared types and constants for DingTalk setup.
"""

import json
import logging
from typing import Optional, Tuple

from pydantic import BaseModel, Field

from agentbay import ActOptions

logger = logging.getLogger(__name__)

APP_NAME = "龙虾虾ByAgentBay"
APP_DESC = "AgentBay的小龙虾"
ROBOT_INTRO = "龙虾虾AgentBay"  # 机器人简介
ROBOT_DESC = "AgentBay的小龙虾"  # 机器人描述
VERSION_DESC = "auto created by agentbay"  # 版本描述（版本管理与发布）
DINGTALK_OPEN_URL = "https://open-dev.dingtalk.com"
DINGTALK_APP_URL = "https://open-dev.dingtalk.com/fe/app"  # 应用列表页，点击创建应用
DINGTALK_AI_PAGE_URL = "https://open-dev.dingtalk.com/fe/ai"  # 应用详情页（创建成功后）


class LoginPageCheckSchema(BaseModel):
    """Schema for checking if current page is DingTalk login page."""

    is_login_page: bool = Field(
        ...,
        description="True if page shows 扫码登录 or 账号登录 tab/label (钉钉登录页特征)",
    )
    visible_login_text: str | None = Field(
        None,
        description="Visible login-related text, e.g. 扫码登录 or 账号登录",
    )


class AppCreationCheckSchema(BaseModel):
    """Schema for verifying app creation success."""

    has_app_name: bool = Field(
        ...,
        description="页面上是否显示应用名称「龙虾虾ByAgentBay」",
    )
    is_on_ai_page: bool = Field(
        ...,
        description="当前是否在 fe/ai 应用详情页（URL 包含 open-dev.dingtalk.com/fe/ai）",
    )


class DingtalkCredentialsSchema(BaseModel):
    """Schema for extracting credentials from DingTalk credential page."""

    client_id: str = Field(..., description="钉钉应用 Client ID")
    client_secret: str = Field(..., description="钉钉应用 Client Secret")


# 本地 dingding.json 路径，用于存放凭证
DINGDING_JSON_PATH = "/tmp/dingding.json"
DINGDING_JSON_TEMPLATE = '{"client_id":"","client_secret":""}'

# 沙箱内机器人消息预览图占位路径（100x100 蓝色 PNG，符合钉钉图片要求）
ROBOT_PREVIEW_IMAGE_PATH = "/home/wuying/图片/robot_preview.png"

# base64 编码的 100x100 蓝色 PNG（符合钉钉要求：小于 240x240）
ROBOT_PREVIEW_PNG_B64 = (
    "iVBORw0KGgoAAAANSUhEUgAAAGQAAABkCAIAAAD/gAIDAAAAoklEQVR42u3QMQ0AAAgDsGnDG44R"
    "gAU+niZV0FQPR1EgS5YsWbJkKZAlS5YsWbJkKZAlS5YsWbIUyJIlS5YsWQpkyZIlS5YsBbJkyZIl"
    "S5YCWbJkyZIlS4EsWbJkyZKlQJYsWbJkyVIgS5YsWbJkKZAlS5YsWbIUyJIlS5YsWQpkyZIlS5Ys"
    "BbJkyZIlS5YCWbJkyZIlS4EsWbJkyZKlQJYsWbJkyVIgS9a3BYxYnJ7kVIaDAAAAAElFTkSuQmCC"
)


def ensure_robot_preview_image(session) -> bool:
    """在沙箱内创建机器人消息预览图占位文件，供 act/playwright 上传使用。"""
    session.command.execute_command("mkdir -p /home/wuying/图片", timeout_ms=3000)
    cmd = f"echo '{ROBOT_PREVIEW_PNG_B64}' | base64 -d > {ROBOT_PREVIEW_IMAGE_PATH} 2>/dev/null || true"
    result = session.command.execute_command(cmd, timeout_ms=3000)
    return result.success


def update_json_field(session, json_path: str, field: str) -> None:
    """从剪贴板读取内容，更新 dingding.json 的指定字段。使用 xclip/xsel + jq。"""
    cmd = (
        f"VAL=$(xclip -o 2>/dev/null || xsel -o 2>/dev/null) && "
        f"jq --arg v \"$VAL\" '.[\"{field}\"] = $v' {json_path} > {json_path}.tmp "
        f"&& mv {json_path}.tmp {json_path} 2>/dev/null || true"
    )
    session.command.execute_command(cmd, timeout_ms=5000)


def extract_dingtalk_credentials(session, operator) -> Tuple[bool, Optional[str], Optional[str], str]:
    """
    提取钉钉凭证：复制 Client ID/Secret 到剪贴板、写入 dingding.json 并读取。
    供 browser_operator 与 playwright 复用。

    Returns (success, client_id, client_secret, error).
    """
    # r5 = operator.act(
    #     ActOptions(
    #         action="在左侧菜单选择「凭证与基础信息」",
    #         use_vision=True,
    #     )
    # )
    # if not r5.success:
    #     return False, None, None, r5.message or "进入凭证页面失败"

    fs = session.file_system
    write_ok = fs.write_file(DINGDING_JSON_PATH, DINGDING_JSON_TEMPLATE)
    if not write_ok.success:
        return False, None, None, "创建 dingding.json 失败"

    r6 = operator.act(
        ActOptions(
            action="点击 Client ID 右边的复制按钮，将 Client ID 复制到剪贴板",
            use_vision=True,
        )
    )
    if not r6.success:
        return False, None, None, r6.message or "点击 Client ID 复制按钮失败"

    update_json_field(session, DINGDING_JSON_PATH, "client_id")

    r7 = operator.act(
        ActOptions(
            action="点击 Client Secret 右边的复制按钮，将完整密钥复制到剪贴板。若有显示、查看、揭晓等按钮可展示完整密钥，先点击它。",
            use_vision=True,
        )
    )
    if not r7.success:
        return False, None, None, r7.message or "点击 Client Secret 复制按钮失败"

    update_json_field(session, DINGDING_JSON_PATH, "client_secret")

    session.command.execute_command(
        f"gedit {DINGDING_JSON_PATH} 2>/dev/null & || xed {DINGDING_JSON_PATH} 2>/dev/null & || true",
        timeout_ms=2000,
    )

    read_res = fs.read_file(DINGDING_JSON_PATH, format="text")
    if not read_res.success or not read_res.content:
        return False, None, None, "读取 dingding.json 失败"

    try:
        data = json.loads(read_res.content)
        client_id = (data.get("client_id") or "").strip()
        client_secret = (data.get("client_secret") or "").strip()
    except json.JSONDecodeError:
        return False, None, None, "dingding.json 格式错误"

    if not client_id or not client_secret:
        return False, None, None, "提取的凭证为空"

    logger.info("Extracted DingTalk credentials")
    return True, client_id, client_secret, ""
