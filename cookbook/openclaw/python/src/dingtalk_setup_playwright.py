"""
DingTalk one-click setup using Playwright.

Uses session.browser + Playwright CDP for deterministic browser automation.
"""

import base64
import logging
import struct
import time
from typing import Optional, Tuple

from agentbay import ActOptions, BrowserOption
from playwright.sync_api import sync_playwright, TimeoutError as PlaywrightTimeout

from .dingtalk_setup_common import (
    APP_DESC,
    APP_NAME,
    DINGDING_JSON_PATH,
    DINGDING_JSON_TEMPLATE,
    DINGTALK_AI_PAGE_URL,
    DINGTALK_APP_URL,
    DINGTALK_OPEN_URL,
    ROBOT_DESC,
    ROBOT_INTRO,
    ROBOT_PREVIEW_IMAGE_PATH,
    ROBOT_PREVIEW_PNG_B64,
    VERSION_DESC,
    ensure_robot_preview_image,
    extract_dingtalk_credentials,
)
from .models import SessionInfo

logger = logging.getLogger(__name__)

DEFAULT_TIMEOUT = 15000
NAV_TIMEOUT = 30000


def _click_by_text(page, text: str, timeout: int = DEFAULT_TIMEOUT) -> bool:
    """点击包含指定文本的元素。"""
    try:
        loc = page.get_by_text(text, exact=False).first
        loc.wait_for(state="visible", timeout=timeout)
        loc.click(timeout=timeout)
        return True
    except PlaywrightTimeout:
        return False


def _fill_by_placeholder(page, placeholder: str, value: str) -> bool:
    """根据 placeholder 查找输入框并填写。"""
    try:
        loc = page.get_by_placeholder(placeholder)
        loc.wait_for(state="visible", timeout=DEFAULT_TIMEOUT)
        loc.fill(value, timeout=DEFAULT_TIMEOUT)
        return True
    except PlaywrightTimeout:
        return False


def _fill_by_label(page, label: str, value: str) -> bool:
    """根据 label 查找表单控件并填写。多个匹配时取第一个（如中英文双语表单项）。"""
    try:
        loc = page.get_by_label(label).first
        loc.wait_for(state="visible", timeout=DEFAULT_TIMEOUT)
        loc.fill(value, timeout=DEFAULT_TIMEOUT)
        return True
    except (PlaywrightTimeout, Exception):
        return False  # 含 strict mode violation（多元素匹配）等，由调用方兜底


def start_dingtalk_setup(info: SessionInfo) -> Tuple[bool, str]:
    """
    Start DingTalk setup: open browser to open.dingtalk.com and show QR code.

    Returns (success, error_message).
    """
    session = info.session
    if not session:
        return False, "Session not found"

    try:
        if not hasattr(session, "browser"):
            return False, "当前镜像不支持浏览器，请手动配置钉钉凭证"

        browser_svc = session.browser
        if not browser_svc.is_initialized():
            ok = browser_svc.initialize(BrowserOption())
            if not ok:
                return False, "浏览器初始化失败"

        endpoint_url = browser_svc.get_endpoint_url()
        if not endpoint_url:
            return False, "获取浏览器 CDP 端点失败"

        with sync_playwright() as p:
            pw_browser = p.chromium.connect_over_cdp(endpoint_url)
            try:
                context = pw_browser.contexts[0] if pw_browser.contexts else pw_browser.new_context()
                page = context.pages[0] if context.pages else context.new_page()
                page.goto(DINGTALK_OPEN_URL, timeout=NAV_TIMEOUT)
                page.wait_for_load_state("domcontentloaded", timeout=DEFAULT_TIMEOUT)
                logger.info("Opened DingTalk open platform via Playwright")
            finally:
                pw_browser.close()

        return True, ""
    except Exception as e:
        logger.exception("Failed to start DingTalk setup (Playwright)")
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
        logger.error("[钉钉配置] Session not found")
        return False, None, None, "Session not found"

    try:
        logger.info("[钉钉配置] 开始继续配置流程")
        if not hasattr(session, "browser"):
            logger.error("[钉钉配置] 当前镜像不支持浏览器")
            return False, None, None, "当前镜像不支持浏览器，请手动配置钉钉凭证"

        browser_svc = session.browser
        if not browser_svc.is_initialized():
            ok = browser_svc.initialize(BrowserOption())
            if not ok:
                logger.error("[钉钉配置] 浏览器初始化失败")
                return False, None, None, "浏览器初始化失败"
        logger.info("[钉钉配置] 浏览器已就绪")

        endpoint_url = browser_svc.get_endpoint_url()
        if not endpoint_url:
            logger.error("[钉钉配置] 获取 CDP 端点失败")
            return False, None, None, "获取浏览器 CDP 端点失败"

        with sync_playwright() as p:
            pw_browser = p.chromium.connect_over_cdp(endpoint_url)
            logger.info("[钉钉配置] 已连接浏览器 CDP")
            try:
                context = pw_browser.contexts[0] if pw_browser.contexts else pw_browser.new_context()
                page = context.pages[0] if context.pages else context.new_page()
                page.set_default_timeout(DEFAULT_TIMEOUT)
                page.set_default_navigation_timeout(NAV_TIMEOUT)

                # 步骤 5：访问应用列表页，点击创建应用
                logger.info("[钉钉配置] 步骤5: 访问应用列表页 %s", DINGTALK_APP_URL)
                page.goto(DINGTALK_APP_URL, wait_until="domcontentloaded")
                time.sleep(1)
                if not _click_by_text(page, "创建应用"):
                    logger.error("[钉钉配置] 步骤5失败: 点击创建应用失败")
                    return False, None, None, "点击创建应用失败"
                logger.info("[钉钉配置] 步骤5成功: 已点击创建应用")
                time.sleep(0.5)

                # 步骤 6：填写应用信息（创建应用弹窗）
                logger.info("[钉钉配置] 步骤6: 填写应用信息")
                filled_name = _fill_by_label(page, "应用名称", APP_NAME)
                if not filled_name:
                    filled_name = _fill_by_placeholder(page, "应用名称", APP_NAME)
                if not filled_name:
                    name_inputs = page.locator('input[placeholder*="应用名称"]')
                    if name_inputs.count() > 0:
                        name_inputs.first.fill(APP_NAME)
                        filled_name = True
                if not filled_name:
                    page.locator("input").first.fill(APP_NAME)
                filled_desc = _fill_by_label(page, "应用描述", APP_DESC)
                if not filled_desc:
                    filled_desc = _fill_by_placeholder(page, "应用描述", APP_DESC)
                if not filled_desc and page.locator("textarea").count() > 0:
                    page.locator("textarea").first.fill(APP_DESC)
                if not _click_by_text(page, "保存"):
                    logger.error("[钉钉配置] 步骤6失败: 点击保存失败")
                    return False, None, None, "点击保存失败"
                logger.info("[钉钉配置] 步骤6成功: 已填写应用信息并保存")

                # 校验：进入 fe/ai 应用详情页
                try:
                    page.wait_for_url("**/fe/ai**", timeout=10000)
                except PlaywrightTimeout:
                    pass
                if "fe/ai" not in page.url:
                    logger.error("[钉钉配置] 校验失败: 未进入应用详情页, url=%s", page.url)
                    return (
                        False, None, None,
                        f"应用创建验证失败：未进入应用详情页 ({DINGTALK_AI_PAGE_URL})"
                    )
                logger.info("[钉钉配置] 校验成功: 已进入应用详情页")

                # 步骤 7-8：添加应用能力 → 机器人配置
                logger.info("[钉钉配置] 步骤7: 添加应用能力")
                if not _click_by_text(page, "添加应用能力"):
                    logger.error("[钉钉配置] 步骤7失败: 点击添加应用能力失败")
                    return False, None, None, "点击添加应用能力失败"

                # 获取所有「添加」按钮，取最后一个（机器人卡片）
                add_btns = page.get_by_role("button", name="添加")
                if add_btns.count() == 0:
                    add_btns = page.get_by_text("添加", exact=False)
                if add_btns.count() == 0:
                    logger.error("[钉钉配置] 步骤7失败: 未找到「添加」按钮")
                    return False, None, None, "未找到「添加」按钮"
                add_btns.last.scroll_into_view_if_needed(timeout=DEFAULT_TIMEOUT)
                add_btns.last.click(timeout=DEFAULT_TIMEOUT)
                logger.info("[钉钉配置] 步骤7成功: 已点击机器人卡片的添加按钮")
                time.sleep(0.5)  # 等待跳转/弹窗加载

                # 机器人配置、简介、描述、发布等均在 iframe 内
                logger.info("[钉钉配置] 步骤8: 在 iframe 内配置机器人")
                robot_frame = None
                for i in range(page.locator("iframe").count()):
                    try:
                        fl = page.frame_locator("iframe").nth(i)
                        fl.locator("div", has_text="机器人配置").first.wait_for(
                            state="visible", timeout=3000
                        )
                        robot_frame = fl
                        logger.info("找到机器人配置 iframe #%d", i)
                        break
                    except PlaywrightTimeout:
                        continue
                if robot_frame is None:
                    logger.warning("[钉钉配置] 未找到机器人配置 iframe，将使用主页面")
                ctx = robot_frame if robot_frame is not None else page

                # 点击机器人配置开关
                if robot_frame is not None:
                    try:
                        robot_config_div = robot_frame.locator(
                            "div", has_text="机器人配置"
                        ).first
                        switch_btn = robot_config_div.locator('[role="switch"]').first
                        if not switch_btn.is_checked():
                            switch_btn.click()
                            logger.info("[钉钉配置] 已打开机器人配置开关")
                    except PlaywrightTimeout:
                        logger.warning("[钉钉配置] 未找到机器人配置开关，跳过")
                time.sleep(0.5)

                # 填写机器人简介、描述（在 iframe 内，均有必填 * label）
                if not _fill_by_label(ctx, "机器人简介", ROBOT_INTRO):
                    if not _fill_by_placeholder(ctx, "机器人简介", ROBOT_INTRO):
                        try:
                            ctx.locator("textarea").first.fill(ROBOT_INTRO)
                        except PlaywrightTimeout:
                            logger.warning("[钉钉配置] 填写机器人简介失败，跳过")
                logger.info("[钉钉配置] 已填写机器人简介")
                if not _fill_by_label(ctx, "机器人描述", ROBOT_DESC):
                    if not _fill_by_placeholder(ctx, "机器人描述", ROBOT_DESC):
                        try:
                            textareas = ctx.locator("textarea")
                            if textareas.count() >= 2:
                                textareas.nth(1).fill(ROBOT_DESC)
                            else:
                                textareas.first.fill(ROBOT_DESC)
                        except PlaywrightTimeout:
                            logger.warning("[钉钉配置] 填写机器人描述失败，跳过")
                logger.info("[钉钉配置] 已填写机器人描述")

                # 先确保沙箱内有预览图文件
                ensure_robot_preview_image(session)
                logger.info("[钉钉配置] 预览图已写入沙箱: %s", ROBOT_PREVIEW_IMAGE_PATH)

                # 使用 Browser Operator 的 act 方法上传（通过沙箱内文件路径）
                operator = browser_svc.operator
                upload_result = operator.act(
                    ActOptions(
                        action=(
                            f"在「*机器人消息预览图」下方的文件上传组件（上传按钮、可点击上传区域或 input type=file）处，"
                            f"上传位于 '{ROBOT_PREVIEW_IMAGE_PATH}' 的文件。"
                        ),
                        use_vision=True,
                    )
                )
                if upload_result.success:
                    logger.info("[钉钉配置] Browser Operator 上传预览图成功: %s", upload_result.message)
                else:
                    logger.warning("[钉钉配置] Browser Operator 上传预览图失败: %s", upload_result.message)

                # 点击发布：使用 Browser Operator（与 browser_operator 流程一致）
                r4c = browser_svc.operator.act(
                    ActOptions(action="点击发布按钮", use_vision=True)
                )
                if not r4c.success:
                    logger.warning("[钉钉配置] 步骤8: 点击发布失败，继续执行版本管理与发布: %s", r4c.message)
                else:
                    time.sleep(0.5)
                    r4c2 = browser_svc.operator.act(
                        ActOptions(
                            action="出现「确认发布」弹窗，点击弹窗中的「发布」按钮",
                            use_vision=True,
                        )
                    )
                    if r4c2.success:
                        logger.info("[钉钉配置] 步骤8成功: 已点击发布")
                    time.sleep(1)

                # 步骤 9：版本管理与发布
                logger.info("[钉钉配置] 步骤9: 版本管理与发布")
                if not _click_by_text(page, "版本管理与发布"):
                    logger.error("[钉钉配置] 步骤9失败: 点击版本管理与发布失败")
                    return False, None, None, "点击版本管理与发布失败"
                time.sleep(0.5)
                if not _click_by_text(page, "创建新版本"):
                    logger.error("[钉钉配置] 步骤9失败: 点击创建新版本失败")
                    return False, None, None, "点击创建新版本失败"
                time.sleep(0.5)
                if not _fill_by_placeholder(page, "版本描述", VERSION_DESC):
                    try:
                        ver_section = page.locator("text=版本描述").first
                        ver_section.locator("..").locator("input, textarea").first.fill(VERSION_DESC)
                    except Exception:
                        page.locator("input, textarea").first.fill(VERSION_DESC)

                # 点击保存、确认发布：使用 Browser Operator（与 browser_operator 流程一致）
                r5c = browser_svc.operator.act(
                    ActOptions(action="点击发布按钮", use_vision=True)
                )
                if not r5c.success:
                    logger.error("[钉钉配置] 步骤9失败: 版本发布失败: %s", r5c.message)
                    return False, None, None, r5c.message or "版本发布失败"
                time.sleep(0.5)
                r5d = browser_svc.operator.act(
                    ActOptions(
                        action="若出现「确认发布」弹窗，点击弹窗中的「确认发布」按钮",
                        use_vision=True,
                    )
                )
                if not r5d.success:
                    logger.error("[钉钉配置] 步骤9失败: 二次确认发布失败: %s", r5d.message)
                    return False, None, None, r5d.message or "二次确认发布失败"
                logger.info("[钉钉配置] 步骤9成功: 版本已发布")
                time.sleep(2)

                # 步骤 10：提取凭证（复用 common 中的提取逻辑，使用 operator.act）
                logger.info("[钉钉配置] 步骤10: 提取凭证")
                if not _click_by_text(page, "凭证与基础信息"):
                    logger.error("[钉钉配置] 步骤10失败: 点击凭证与基础信息失败")
                    return False, None, None, "点击凭证与基础信息失败"
                
                ok, client_id, client_secret, err = extract_dingtalk_credentials(
                    session, browser_svc.operator
                )
                if not ok:
                    logger.error("[钉钉配置] 步骤10失败: %s", err)
                    return False, None, None, err or "提取凭证失败"

                logger.info("[钉钉配置] 步骤10成功: 凭证已提取")
                logger.info("[钉钉配置] 全部步骤完成，配置成功")
                return True, client_id, client_secret, ""

            finally:
                pw_browser.close()

    except PlaywrightTimeout as e:
        logger.exception("Playwright timeout: %s", e)
        return False, None, None, f"操作超时: {e}"
    except Exception as e:
        logger.exception("DingTalk setup failed (Playwright)")
        return False, None, None, str(e)
