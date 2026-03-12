"""
DingTalk one-click setup using Browser Operator (page_use_*).

Uses session.browser.operator: navigate, act, extract.
"""

import logging
from typing import Optional, Tuple

from agentbay import ActOptions, BrowserOption, ExtractOptions

from .dingtalk_setup_common import (
    APP_DESC,
    APP_NAME,
    DINGDING_JSON_PATH,
    DINGDING_JSON_TEMPLATE,
    DINGTALK_AI_PAGE_URL,
    DINGTALK_APP_URL,
    DINGTALK_OPEN_URL,
    AppCreationCheckSchema,
    LoginPageCheckSchema,
    ROBOT_DESC,
    ROBOT_INTRO,
    ROBOT_PREVIEW_IMAGE_PATH,
    VERSION_DESC,
    ensure_robot_preview_image,
    extract_dingtalk_credentials,
    update_json_field,
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
        if not hasattr(session, "browser") or not hasattr(session.browser, "operator"):
            return False, "当前镜像不支持 Browser Operator，请手动配置钉钉凭证"

        browser = session.browser
        if not browser.is_initialized():
            ok = browser.initialize(BrowserOption())
            if not ok:
                return False, "浏览器初始化失败"

        operator = browser.operator
        nav_result = operator.navigate(DINGTALK_OPEN_URL)
        if "failed" in nav_result.lower():
            return False, f"导航失败: {nav_result}"

        # # 未登录时自动跳转到登录页（login.dingtalk.com），直接显示扫码登录和二维码，无需点击登录按钮
        # # 使用 extract 抓取页面上是否有「扫码登录」「账号登录」等字样，判断是否为登录页
        # ok, check = operator.extract(
        #     ExtractOptions(
        #         instruction="抓取页面上是否显示「扫码登录」或「账号登录」等钉钉登录页特征文字。若有则 is_login_page 为 True。",
        #         schema=LoginPageCheckSchema,
        #         use_vision=True,
        #     )
        # )
        # if not ok or not check or not check.is_login_page:
        #     return False, "未检测到扫码登录页面（页面上应有「扫码登录」或「账号登录」字样）"

        logger.info("Opened DingTalk open platform via Browser Operator")
        return True, ""
    except Exception as e:
        logger.exception("Failed to start DingTalk setup (Browser Operator)")
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

    try:
        if not hasattr(session, "browser") or not hasattr(session.browser, "operator"):
            return False, None, None, "当前镜像不支持 Browser Operator，请手动配置钉钉凭证"

        browser = session.browser
        if not browser.is_initialized():
            ok = browser.initialize(BrowserOption())
            if not ok:
                return False, None, None, "浏览器初始化失败"

        operator = browser.operator

        # 诊断：Browser Operator 的 act 上传需通过 link_url 调用 MCP，需 JWT。若 token/link_url 为空会报 401
        token = getattr(session, "token", "") or (session.get_token() if hasattr(session, "get_token") else "")
        link_url = getattr(session, "link_url", "") or (session.get_link_url() if hasattr(session, "get_link_url") else "")
        logger.info(
            "[钉钉配置] Browser Operator: link_url=%s, token=%s (token 为空会导致上传时 Jwt is missing 401)",
            "有" if link_url else "空",
            "有" if token else "空",
        )
        if not token or not link_url:
            logger.warning(
                "[钉钉配置] session.token 或 link_url 为空！GetSession 可能未返回 Token/LinkUrl。"
                "新建 session 时 CreateSession 会返回；恢复 session 时需 GetSession 也返回，否则 MCP 调用会 401。"
            )
            # 尝试通过 GetSession 刷新以获取 token/link_url（适用于恢复的 session）
            agent_bay = getattr(info, "agent_bay", None)
            if agent_bay:
                try:
                    refresh_result = agent_bay.get(session.session_id)
                    if refresh_result.success and refresh_result.session:
                        session.token = str(getattr(refresh_result.session, "token", "") or "")
                        session.link_url = str(getattr(refresh_result.session, "link_url", "") or "")
                        if session.token and session.link_url:
                            logger.info("[钉钉配置] 已通过 GetSession 刷新 token/link_url")
                except Exception as e:
                    logger.warning("[钉钉配置] 刷新 session 失败: %s", e)

        # 步骤 5：直接访问应用列表页，点击创建应用
        nav_result = operator.navigate(DINGTALK_APP_URL)
        if "failed" in (nav_result or "").lower():
            return False, None, None, f"导航到应用列表页失败: {nav_result}"

        r1 = operator.act(
            ActOptions(action="点击创建应用", use_vision=True),
        )
        if not r1.success:
            return False, None, None, r1.message or "点击创建应用失败"

        r3 = operator.act(
            ActOptions(
                action=f"填写应用名称为{APP_NAME}，应用描述为{APP_DESC}，点击保存",
                use_vision=True,
            )
        )
        if not r3.success:
            return False, None, None, r3.message or "填写应用信息失败"

        # 检查应用是否创建成功：页面上有「龙虾虾ByAgentbay」且已进入 fe/ai 页面
        ok, check = operator.extract(
            ExtractOptions(
                instruction=(
                    f"抓取页面上是否显示应用名称「{APP_NAME}」，以及当前页面 URL 是否包含 "
                    f"open-dev.dingtalk.com/fe/ai（应用详情页）。"
                ),
                schema=AppCreationCheckSchema,
                use_vision=True,
            )
        )
        if not ok or not check or not check.has_app_name or not check.is_on_ai_page:
            return (
                False,
                None,
                None,
                f"应用创建验证失败：页面上未找到「{APP_NAME}」或未进入应用详情页 "
                f"({DINGTALK_AI_PAGE_URL})，请重试",
            )

        # 步骤 8-9：添加应用能力 → 机器人 → 配置（先于提取凭证）
        ensure_robot_preview_image(session)
        r4 = operator.act(
            ActOptions(
                action="选择「添加应用能力」，找到机器人卡片，点击「配置」",
                use_vision=True,
            )
        )
        if not r4.success:
            return False, None, None, r4.message or "添加应用能力-机器人配置失败"
        r4_radio = operator.act(
            ActOptions(
                action="找到机器人配置，点击 radio 开关，打开 radio 开关",
                use_vision=True,
            )
        )
        if not r4_radio.success:
            return False, None, None, r4_radio.message or "打开机器人 radio 开关失败"
        r4a = operator.act(
            ActOptions(
                action=(
                    f"填写必填项 *机器人简介 为「{ROBOT_INTRO}」，"
                    f"*机器人描述 为「{ROBOT_DESC}」（带红色星号的为必填项）"
                ),
                use_vision=True,
            )
        )
        if not r4a.success:
            return False, None, None, r4a.message or "填写机器人简介/描述失败"
        r4b = operator.act(
            ActOptions(
                action=(
                    f"在「*机器人消息预览图」下方的文件上传组件（上传按钮、可点击上传区域或 input type=file）处，"
                    f"上传位于 '{ROBOT_PREVIEW_IMAGE_PATH}' 的文件。"
                ),
                use_vision=True,
            )
        )
        if not r4b.success:
            return False, None, None, r4b.message or "上传机器人消息预览图失败"
        r4c = operator.act(
            ActOptions(
                action="点击发布按钮",
                use_vision=True,
            )
        )
        if not r4c.success:
            return False, None, None, r4c.message or "点击发布失败"
        r4c2 = operator.act(
            ActOptions(
                action=(
                    "出现「确认发布」弹窗，点击弹窗中的「发布」按钮"
                ),
                use_vision=True,
            )
        )
        if not r4c2.success:
            return False, None, None, r4c2.message or "二次确认发布失败"

        # 步骤 9：版本管理与发布（配置完机器人后、提取凭证前）
        r5a = operator.act(
            ActOptions(
                action="在左侧菜单点击「版本管理与发布」",
                use_vision=True,
            )
        )
        if not r5a.success:
            return False, None, None, r5a.message or "进入版本管理与发布失败"
        r5a2 = operator.act(
            ActOptions(
                action="点击「创建新版本」",
                use_vision=True,
            )
        )
        if not r5a2.success:
            return False, None, None, r5a2.message or "点击创建新版本失败"
        r5b = operator.act(
            ActOptions(
                action=f"填写必填项「*版本描述」 为「{VERSION_DESC}」",
                use_vision=True,
            )
        )
        if not r5b.success:
            return False, None, None, r5b.message or "填写版本描述失败"
        r5c = operator.act(
            ActOptions(
                action="点击发布按钮",
                use_vision=True,
            )
        )
        if not r5c.success:
            return False, None, None, r5c.message or "点击发布失败"
        r5d = operator.act(
            ActOptions(
                action="若出现「确认发布」弹窗，点击弹窗中的「确认发布」按钮",
                use_vision=True,
            )
        )
        if not r5d.success:
            return False, None, None, r5d.message or "二次确认发布失败"

        # 步骤 10：提取凭证（复用 common 中的提取逻辑）
        ok, client_id, client_secret, err = extract_dingtalk_credentials(session, operator)
        if not ok:
            return False, None, None, err or "提取凭证失败"

        logger.info("Extracted DingTalk credentials via Browser Operator")
        return True, client_id, client_secret, ""
    except Exception as e:
        logger.exception("DingTalk setup failed (Browser Operator)")
        return False, None, None, str(e)
