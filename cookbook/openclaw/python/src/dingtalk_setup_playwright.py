"""
DingTalk one-click setup using Playwright.

Uses session.browser + Playwright CDP for deterministic browser automation.
Browser/Playwright instances are cached in start_dingtalk_setup and reused by
continue_dingtalk_setup.
"""

import base64
import logging
import struct
import threading
import time
from dataclasses import dataclass
from typing import Dict, Optional, Tuple

from agentbay import ActOptions, BrowserOption
from playwright.sync_api import sync_playwright, Browser, Page, TimeoutError as PlaywrightTimeout

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
    ROBOT_PREVIEW_PNG_B64,
    VERSION_DESC,
    extract_dingtalk_credentials,
)
from .models import SessionInfo

logger = logging.getLogger(__name__)

DEFAULT_TIMEOUT = 15000
NAV_TIMEOUT = 30000


@dataclass
class _DingtalkBrowserContext:
    """Cached browser context for DingTalk setup flow."""

    browser_svc: object
    playwright: object
    pw_browser: Browser
    page: Page


# session_id -> _DingtalkBrowserContext
_dingtalk_browser_cache: Dict[str, _DingtalkBrowserContext] = {}
# session_id -> thread_id (Playwright 必须在创建它的线程中 close/stop)
_dingtalk_browser_threads: Dict[str, int] = {}


def _connect_and_build_context(
    browser_svc, info: SessionInfo
) -> Tuple[Optional[_DingtalkBrowserContext], str]:
    """Connect to CDP and build context. Raises on connection failure."""
    endpoint_url = browser_svc.get_endpoint_url()
    if not endpoint_url:
        return None, "获取浏览器 CDP 端点失败"
    playwright = sync_playwright().start()
    try:
        pw_browser = playwright.chromium.connect_over_cdp(endpoint_url)
        context = pw_browser.contexts[0] if pw_browser.contexts else pw_browser.new_context()
        page = context.pages[0] if context.pages else context.new_page()
        page.set_default_timeout(DEFAULT_TIMEOUT)
        page.set_default_navigation_timeout(NAV_TIMEOUT)
        ctx = _DingtalkBrowserContext(
            browser_svc=browser_svc,
            playwright=playwright,
            pw_browser=pw_browser,
            page=page,
        )
        _dingtalk_browser_cache[info.session_id] = ctx
        _dingtalk_browser_threads[info.session_id] = threading.current_thread().ident
        return ctx, ""
    except Exception:
        try:
            playwright.stop()
        except Exception:
            pass
        raise


def _acquire_browser_context(info: SessionInfo) -> Tuple[Optional[_DingtalkBrowserContext], str]:
    """
    Create browser_svc, playwright, pw_browser, page and cache them.
    On TargetClosedError (browser was closed), re-initialize browser_svc and retry once.
    Returns (context, error_message). error_message non-empty on failure.
    """
    session = info.session
    if not session:
        return None, "Session not found"
    if not hasattr(session, "browser"):
        return None, "当前镜像不支持浏览器"
    browser_svc = session.browser
    if not browser_svc.is_initialized():
        ok = browser_svc.initialize(BrowserOption())
        if not ok:
            return None, "浏览器初始化失败"

    for attempt in range(2):
        try:
            return _connect_and_build_context(browser_svc, info)
        except Exception as e:
            err_msg = str(e)
            is_target_closed = (
                "Target" in err_msg and "closed" in err_msg
            ) or "TargetClosedError" in type(e).__name__
            if is_target_closed and attempt == 0:
                logger.warning(
                    "[钉钉配置] 浏览器连接已关闭，尝试重新初始化并重连 (attempt %d): %s",
                    attempt + 1,
                    err_msg,
                )
                clear_dingtalk_browser_cache(info.session_id)
                ok = browser_svc.initialize(BrowserOption())
                if not ok:
                    logger.error("[钉钉配置] 重新初始化浏览器失败")
                    return None, "浏览器已关闭，重新初始化失败"
                continue
            logger.exception("[钉钉配置] 创建浏览器连接失败: %s", e)
            return None, str(e)
    return None, "创建浏览器连接失败"


def get_playwright_page_for_credentials(info: SessionInfo) -> Tuple[Optional[Page], str]:
    """
    通过 CDP 获取 Playwright page，供 credential 提取使用。
    browser_operator 流程复用此函数以获取 page。
    """
    ctx, err = _get_browser_context(info)
    if not ctx:
        return None, err or "获取页面失败"
    return ctx.page, ""


def _get_browser_context(info: SessionInfo) -> Tuple[Optional[_DingtalkBrowserContext], str]:
    """
    Get cached browser context or create if not exists.
    If cached connection is dead (is_connected=False), clear cache and re-acquire.
    Returns (context, error_message).
    """
    ctx = _dingtalk_browser_cache.get(info.session_id)
    if ctx is not None:
        try:
            if getattr(ctx.pw_browser, "is_connected", lambda: True)():
                return ctx, ""
        except Exception:
            pass
        logger.info("[钉钉配置] 缓存连接已断开，重新获取浏览器上下文")
        clear_dingtalk_browser_cache(info.session_id)
    return _acquire_browser_context(info)


def clear_dingtalk_browser_cache(session_id: str) -> None:
    """Close and clear cached browser context for session.
    Playwright 必须在创建它的线程中 close/stop，跨线程调用会报 Cannot switch to a different thread。
    若当前不在创建线程，仅移除缓存，不执行 close/stop。
    """
    ctx = _dingtalk_browser_cache.pop(session_id, None)
    creator_thread_id = _dingtalk_browser_threads.pop(session_id, None)
    if ctx is not None:
        if threading.current_thread().ident == creator_thread_id:
            try:
                ctx.pw_browser.close()
            except Exception as e:
                logger.warning("[钉钉配置] 关闭 pw_browser 失败: %s", e)
            try:
                ctx.playwright.stop()
            except Exception as e:
                logger.warning("[钉钉配置] 停止 playwright 失败: %s", e)
        else:
            logger.debug(
                "[钉钉配置] 清除缓存时不在创建线程（当前=%s, 创建=%s），跳过 close/stop",
                threading.current_thread().ident,
                creator_thread_id,
            )


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
    Creates and caches browser_svc + pw_browser for reuse by continue_dingtalk_setup.

    Returns (success, error_message).
    """
    session = info.session
    if not session:
        return False, "Session not found"

    try:
        ctx, err = _acquire_browser_context(info)
        if ctx is None:
            if "不支持浏览器" in err:
                try:
                    cmd = f'bash -lc "nohup firefox \\"{DINGTALK_OPEN_URL}\\" >/dev/null 2>&1 &"'
                    result = session.command.execute_command(cmd, timeout_ms=10000)
                    if result.success:
                        logger.info("Opened DingTalk in Firefox (fallback)")
                        return True, ""
                    return False, result.error_message or "打开浏览器失败"
                except Exception as e2:
                    return False, str(e2)
            return False, err or "当前镜像不支持浏览器，请手动配置钉钉凭证"

        ctx.page.goto(DINGTALK_OPEN_URL, timeout=NAV_TIMEOUT)
        ctx.page.wait_for_load_state("domcontentloaded", timeout=DEFAULT_TIMEOUT)
        logger.info("Opened DingTalk open platform via Playwright (cached for subsequent steps)")
        return True, ""
    except Exception as e:
        logger.exception("Failed to start DingTalk setup (Playwright)")
        clear_dingtalk_browser_cache(info.session_id)
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
    使用 start_dingtalk_setup 缓存的 browser 实例；若未缓存则自动创建并缓存。

    Returns (success, client_id, client_secret, error).
    """
    session = info.session
    if not session:
        logger.error("[钉钉配置] Session not found")
        return False, None, None, "Session not found"

    try:
        logger.info("[钉钉配置] 开始继续配置流程")
        browser_ctx, err = _get_browser_context(info)
        if browser_ctx is None:
            logger.error("[钉钉配置] %s", err)
            return False, None, None, err or "当前镜像不支持浏览器，请手动配置钉钉凭证"
        logger.info("[钉钉配置] 浏览器已就绪 (使用缓存实例)")

        page = browser_ctx.page
        browser_svc = browser_ctx.browser_svc

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
        # 获取 class=app-content-container 的 div 元素，在此元素内获取 iframe，即为机器人配置页面
        robot_frame = None
        try:
            fl = page.frame_locator("div.app-content-container >> iframe")
            fl.locator("div", has_text="机器人配置").first.wait_for(
                state="visible", timeout=3000
            )
            robot_frame = fl
            logger.info("找到机器人配置 iframe (app-content-container 内)")
        except PlaywrightTimeout:
            logger.error("[钉钉配置] 步骤8失败: 未找到机器人配置 iframe")
            return False, None, None, "未找到机器人配置 iframe"
        frame_ctx = robot_frame

        # 点击机器人配置开关
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
        if not _fill_by_label(frame_ctx, "机器人简介", ROBOT_INTRO):
            if not _fill_by_placeholder(frame_ctx, "机器人简介", ROBOT_INTRO):
                try:
                    frame_ctx.locator("textarea").first.fill(ROBOT_INTRO)
                except PlaywrightTimeout:
                    logger.warning("[钉钉配置] 填写机器人简介失败，跳过")
        logger.info("[钉钉配置] 已填写机器人简介")
        if not _fill_by_label(frame_ctx, "机器人描述", ROBOT_DESC):
            if not _fill_by_placeholder(frame_ctx, "机器人描述", ROBOT_DESC):
                try:
                    textareas = frame_ctx.locator("textarea")
                    if textareas.count() >= 2:
                        textareas.nth(1).fill(ROBOT_DESC)
                    else:
                        textareas.first.fill(ROBOT_DESC)
                except PlaywrightTimeout:
                    logger.warning("[钉钉配置] 填写机器人描述失败，跳过")
        logger.info("[钉钉配置] 已填写机器人描述")

        # 上传预览图：Playwright 在本地运行，无法访问沙箱内路径，使用 base64 解码后的 bytes 直接上传
        try:
            preview_bytes = base64.b64decode(ROBOT_PREVIEW_PNG_B64)
            robot_frame.locator("input#innerMsgRobot_previewMediaId[type='file']").set_input_files(
                files=[{"name": "robot_preview.png", "mimeType": "image/png", "buffer": preview_bytes}]
            )
            logger.info("[钉钉配置] 预览图上传成功")
        except PlaywrightTimeout:
            logger.warning("[钉钉配置] 上传预览图失败，跳过")

        # 点击发布：在 iframe 内找到 type=submit 的 button 并点击
        try:
            robot_frame.locator("button[type='submit']").click(timeout=DEFAULT_TIMEOUT)
            logger.info("[钉钉配置] 已点击发布按钮")
            time.sleep(0.5)
            # 确认发布弹窗：在 iframe 内找到 ant-modal-content，在其内点击 ant-btn-primary 按钮
            robot_frame.locator("div.ant-modal-content").locator("button.ant-btn-primary[type='button']").click(timeout=DEFAULT_TIMEOUT)
            logger.info("[钉钉配置] 步骤8成功: 已点击确认发布")
        except PlaywrightTimeout:
            logger.warning("[钉钉配置] 步骤8: 点击发布失败，继续执行版本管理与发布")
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

        # 点击保存：找到 button[type='button'] 且子元素为 <span>保存</span> 的按钮
        try:
            page.locator('button[type="button"]:has(span:has-text("保存"))').click(timeout=DEFAULT_TIMEOUT)
            logger.info("[钉钉配置] 已点击保存按钮")
        except PlaywrightTimeout:
            logger.error("[钉钉配置] 步骤9失败: 版本发布失败")
            return False, None, None, "未找到保存按钮"
        time.sleep(0.5)
        # 确认发布弹窗：dtd-modal-content > dtd-modal-confirm-btns 内的两个 button，点击最后一个
        try:
            page.locator("div.dtd-modal-content div.dtd-modal-confirm-btns button[type='button']").last.click(timeout=DEFAULT_TIMEOUT)
            logger.info("[钉钉配置] 步骤9成功: 版本已发布")
        except PlaywrightTimeout:
            logger.error("[钉钉配置] 步骤9失败: 二次确认发布失败")
            return False, None, None, "未找到确认发布按钮"
        time.sleep(3)

        # 步骤 10：提取凭证（使用 Playwright 定位器点击复制按钮）
        logger.info("[钉钉配置] 步骤10: 提取凭证")
        if not _click_by_text(page, "凭证与基础信息"):
            logger.error("[钉钉配置] 步骤10失败: 点击凭证与基础信息失败")
            return False, None, None, "点击凭证与基础信息失败"

        ok, client_id, client_secret, err = extract_dingtalk_credentials(session, page)
        if not ok:
            logger.error("[钉钉配置] 步骤10失败: %s", err)
            return False, None, None, err or "提取凭证失败"

        logger.info("[钉钉配置] 步骤10成功: 凭证已提取")
        logger.info("[钉钉配置] 全部步骤完成，配置成功")
        return True, client_id, client_secret, ""

    except PlaywrightTimeout as e:
        logger.exception("Playwright timeout: %s", e)
        return False, None, None, f"操作超时: {e}"
    except Exception as e:
        logger.exception("DingTalk setup failed (Playwright)")
        return False, None, None, str(e)
