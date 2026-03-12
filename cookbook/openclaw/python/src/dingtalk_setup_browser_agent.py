"""
DingTalk one-click setup using BrowserUseAgent.

Uses session.agent.browser.execute_task_and_wait with natural language tasks.
"""

import json
import logging
from typing import Optional, Tuple

from agentbay import BrowserOption

from .dingtalk_setup_common import (
    APP_DESC,
    APP_NAME,
    DINGTALK_OPEN_URL,
    DingtalkCredentialsSchema,
    ROBOT_DESC,
    ROBOT_INTRO,
    ROBOT_PREVIEW_IMAGE_PATH,
    VERSION_DESC,
)
from .models import SessionInfo

logger = logging.getLogger(__name__)


def start_dingtalk_setup(info: SessionInfo) -> Tuple[bool, str]:
    """
    Start DingTalk setup: open browser to open.dingtalk.com and show QR code.

    Returns (success, error_message).
    """
    session = info.session
    if not session:
        return False, "Session not found"

    try:
        if not hasattr(session, "agent") or not hasattr(session.agent, "browser"):
            return False, "当前镜像不支持 BrowserUseAgent，请手动配置钉钉凭证"

        agent = session.agent
        if not getattr(agent.browser, "initialized", False):
            ok = agent.browser.initialize(BrowserOption())
            if not ok:
                return False, "浏览器初始化失败"

        task = f"打开浏览器访问 {DINGTALK_OPEN_URL}。未登录时自动跳转到登录页，直接显示「扫码登录」和二维码，无需点击登录按钮。确认页面是否显示钉钉扫码登录界面。"
        result = agent.browser.execute_task_and_wait(
            task=task, timeout=60, use_vision=True
        )
        if not result.success:
            return False, result.error_message or "打开登录页失败"

        logger.info("Opened DingTalk open platform via BrowserUseAgent")
        return True, ""
    except Exception as e:
        logger.exception("Failed to start DingTalk setup (BrowserUseAgent)")
        try:
            cmd = f'bash -lc "nohup firefox \\"{DINGTALK_OPEN_URL}\\" >/dev/null 2>&1 &"'
            result = session.command.execute_command(cmd, timeout_ms=10000)
            if result.success:
                logger.info("Opened DingTalk in Firefox (fallback)")
                return True, ""
            return False, result.error_message or "打开浏览器失败"
        except Exception as e2:
            return False, str(e2)


def continue_dingtalk_setup(info: SessionInfo) -> Tuple[bool, Optional[str], Optional[str], str]:
    """
    Continue after user logged in: create app, extract credentials.

    Returns (success, client_id, client_secret, error).
    """
    session = info.session
    if not session:
        return False, None, None, "Session not found"

    task = f"""
当前浏览器应已打开钉钉开放平台且用户已登录。请按以下步骤操作：

1. 直接访问 https://open-dev.dingtalk.com/fe/app，点击「创建应用」
2. 填写应用名称：{APP_NAME}，应用描述：{APP_DESC}，点击保存
3. 确认应用创建成功：页面上应显示「{APP_NAME}」且已进入 fe/ai 应用详情页

4. 添加应用能力：左侧菜单选择「添加应用能力」，找到机器人卡片，点击「配置」
5. 找到机器人配置，点击 radio 开关，打开 radio 开关
6. 填写必填项 *机器人简介* 为「{ROBOT_INTRO}」，*机器人描述* 为「{ROBOT_DESC}」（带红色星号的为必填项）
7. 在「*机器人消息预览图」下方的文件上传组件（上传按钮或可点击上传区域）处，上传位于 {ROBOT_PREVIEW_IMAGE_PATH} 的文件。不要点击图片预览区域，要点击真正的上传输入框或上传按钮
8. 点击发布按钮。若出现「确认发布」弹窗，点击弹窗中的「发布」按钮

9. 版本管理与发布：左侧菜单点击「版本管理与发布」→ 点击「创建新版本」→ 填写必填项 *版本描述* 为「{VERSION_DESC}」→ 点击发布 → 若出现「确认发布」弹窗，点击「确认发布」按钮

10. 在左侧菜单选择「凭证与基础信息」
11. Client Secret 在页面上被脱敏显示，需点击旁边的复制按钮获取完整值。若有显示/查看/揭晓等按钮可展示完整密钥，先点击它
12. 点击 Client ID 和 Client Secret 的复制按钮后，将剪贴板中的 Client Secret 粘贴到页面中任意可编辑输入框（如应用描述、备注等），以便读取完整值
13. 从页面提取 Client ID（应用凭证区域）和 Client Secret（从粘贴了完整密钥的输入框），以 JSON 格式返回，确保 client_secret 为完整未脱敏的值
"""
    try:
        if not hasattr(session, "agent") or not hasattr(session.agent, "browser"):
            return False, None, None, "当前镜像不支持 BrowserUseAgent，请手动配置钉钉凭证"

        agent = session.agent
        if not getattr(agent.browser, "initialized", False):
            ok = agent.browser.initialize(BrowserOption())
            if not ok:
                return False, None, None, "浏览器初始化失败"

        result = agent.browser.execute_task_and_wait(
            task=task,
            timeout=180,
            use_vision=True,
            output_schema=DingtalkCredentialsSchema,
            full_page_screenshot=True,
        )
        if not result.success:
            return False, None, None, result.error_message or "自动化任务执行失败"

        data = result.task_result
        if data is None:
            return False, None, None, "未获取到任务结果"
        if isinstance(data, str):
            try:
                parsed = json.loads(data)
            except json.JSONDecodeError:
                parsed = {}
        else:
            parsed = data if isinstance(data, dict) else {}

        client_id = str(parsed.get("client_id") or parsed.get("clientId", "")).strip()
        client_secret = str(
            parsed.get("client_secret") or parsed.get("clientSecret", "")
        ).strip()
        if not client_id or not client_secret:
            return False, None, None, "未能从页面提取到 Client ID 或 Client Secret"

        logger.info("Extracted DingTalk credentials via BrowserUseAgent")
        return True, client_id, client_secret, ""
    except Exception as e:
        logger.exception("DingTalk setup failed (BrowserUseAgent)")
        return False, None, None, str(e)
