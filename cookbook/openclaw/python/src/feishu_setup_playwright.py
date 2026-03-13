"""
Feishu one-click setup using Playwright.

Uses session.browser + Playwright CDP for deterministic browser automation.
Browser/Playwright instances are cached in start_feishu_setup and reused by
continue_feishu_setup and configure_feishu_event_subscription.

Uses async Playwright API to run correctly inside asyncio event loop.
"""

import json
import logging
import time
from dataclasses import dataclass
from typing import Dict, Optional, Tuple

from agentbay import BrowserOption
from playwright.async_api import async_playwright, Browser, Page, TimeoutError as PlaywrightTimeout

from .feishu_setup_common import (
    APP_DESC,
    APP_NAME,
    FEISHU_JSON_PATH,
    FEISHU_JSON_TEMPLATE,
    FEISHU_OPEN_URL,
    PERMISSIONS_IMPORT_JSON,
    REQUIRED_PERMISSIONS,
    ROBOT_NAME,
    VERSION_DESC,
    VERSION_NUMBER,
    update_json_field,
)
from .models import SessionInfo

logger = logging.getLogger(__name__)

DEFAULT_TIMEOUT = 15000
NAV_TIMEOUT = 30000


@dataclass
class _FeishuBrowserContext:
    """Cached browser context for Feishu setup flow."""

    browser_svc: object
    playwright: object
    pw_browser: Browser
    page: Page


# session_id -> _FeishuBrowserContext
_feishu_browser_cache: Dict[str, _FeishuBrowserContext] = {}


async def _connect_and_build_context(
    browser_svc, info: SessionInfo
) -> Tuple[Optional[_FeishuBrowserContext], str]:
    """Connect to CDP and build context. Raises on connection failure."""
    endpoint_url = browser_svc.get_endpoint_url()
    if not endpoint_url:
        return None, "获取浏览器 CDP 端点失败"
    playwright = await async_playwright().start()
    try:
        pw_browser = await playwright.chromium.connect_over_cdp(endpoint_url)
        context = pw_browser.contexts[0] if pw_browser.contexts else await pw_browser.new_context()
        page = context.pages[0] if context.pages else await context.new_page()
        page.set_default_timeout(DEFAULT_TIMEOUT)
        page.set_default_navigation_timeout(NAV_TIMEOUT)
        ctx = _FeishuBrowserContext(
            browser_svc=browser_svc,
            playwright=playwright,
            pw_browser=pw_browser,
            page=page,
        )
        _feishu_browser_cache[info.session_id] = ctx
        return ctx, ""
    except Exception:
        try:
            await playwright.stop()
        except Exception:
            pass
        raise


async def _acquire_browser_context(info: SessionInfo) -> Tuple[Optional[_FeishuBrowserContext], str]:
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
            return await _connect_and_build_context(browser_svc, info)
        except Exception as e:
            err_msg = str(e)
            is_target_closed = (
                "Target" in err_msg and "closed" in err_msg
            ) or "TargetClosedError" in type(e).__name__
            if is_target_closed and attempt == 0:
                logger.warning(
                    "[飞书配置] 浏览器连接已关闭，尝试重新初始化并重连 (attempt %d): %s",
                    attempt + 1,
                    err_msg,
                )
                await clear_feishu_browser_cache(info.session_id)
                ok = browser_svc.initialize(BrowserOption())
                if not ok:
                    logger.error("[飞书配置] 重新初始化浏览器失败")
                    return None, "浏览器已关闭，重新初始化失败"
                continue
            logger.exception("[飞书配置] 创建浏览器连接失败: %s", e)
            return None, str(e)
    return None, "创建浏览器连接失败"


async def _get_browser_context(info: SessionInfo) -> Tuple[Optional[_FeishuBrowserContext], str]:
    """
    Get cached browser context or create if not exists.
    If cached connection is dead (is_connected=False), clear cache and re-acquire.
    Returns (context, error_message).
    """
    ctx = _feishu_browser_cache.get(info.session_id)
    if ctx is not None:
        try:
            if getattr(ctx.pw_browser, "is_connected", lambda: True)():
                return ctx, ""
        except Exception:
            pass
        logger.info("[飞书配置] 缓存连接已断开，重新获取浏览器上下文")
        await clear_feishu_browser_cache(info.session_id)
    return await _acquire_browser_context(info)


async def clear_feishu_browser_cache(session_id: str) -> None:
    """Close and clear cached browser context for session."""
    ctx = _feishu_browser_cache.pop(session_id, None)
    if ctx is not None:
        try:
            await ctx.pw_browser.close()
        except Exception as e:
            logger.warning("[飞书配置] 关闭 pw_browser 失败: %s", e)
        try:
            await ctx.playwright.stop()
        except Exception as e:
            logger.warning("[飞书配置] 停止 playwright 失败: %s", e)


async def _click_by_text(page, text: str, timeout: int = DEFAULT_TIMEOUT) -> bool:
    """点击包含指定文本的元素。"""
    try:
        loc = page.get_by_text(text, exact=False).first
        await loc.wait_for(state="visible", timeout=timeout)
        await loc.click(timeout=timeout)
        return True
    except PlaywrightTimeout:
        return False


async def _click_by_role(page, role: str, name: str, timeout: int = DEFAULT_TIMEOUT) -> bool:
    """点击指定角色的元素。"""
    try:
        loc = page.get_by_role(role, name=name).first
        await loc.wait_for(state="visible", timeout=timeout)
        await loc.click(timeout=timeout)
        return True
    except PlaywrightTimeout:
        return False


async def _fill_by_placeholder(page, placeholder: str, value: str) -> bool:
    """根据 placeholder 查找输入框并填写。"""
    try:
        loc = page.get_by_placeholder(placeholder)
        await loc.wait_for(state="visible", timeout=DEFAULT_TIMEOUT)
        await loc.fill(value, timeout=DEFAULT_TIMEOUT)
        return True
    except PlaywrightTimeout:
        return False


async def _fill_by_label(page, label: str, value: str) -> bool:
    """根据 label 查找表单控件并填写。"""
    try:
        loc = page.get_by_label(label).first
        await loc.wait_for(state="visible", timeout=DEFAULT_TIMEOUT)
        await loc.fill(value, timeout=DEFAULT_TIMEOUT)
        return True
    except (PlaywrightTimeout, Exception):
        return False


async def _click_menu_li_by_id_contains(page, id_pattern: str, timeout: int = DEFAULT_TIMEOUT) -> bool:
    """点击 data-menu-id 属性包含指定模式的 li 元素。"""
    try:
        loc = page.locator(f"li[data-menu-id*='{id_pattern}']").first
        await loc.wait_for(state="visible", timeout=timeout)
        await loc.click(timeout=timeout)
        return True
    except PlaywrightTimeout:
        return False


async def _extract_credentials(page, session) -> Tuple[bool, Optional[str], Optional[str], str]:
    """
    步骤13：提取凭证。点击凭证与基础信息菜单，复制 App ID 与 App Secret 到 feishu.json。

    Returns:
        (success, app_id, app_secret, error_message)
    """
    logger.info("[飞书配置] 步骤13: 提取凭证")
    if not await _click_menu_li_by_id_contains(page, "/baseinfo"):
        logger.error("[飞书配置] 步骤13失败: 点击凭证与基础信息菜单失败")
        return False, None, None, "点击凭证与基础信息菜单失败"
    try:
        await page.wait_for_url("**/open.feishu.cn/app/**/baseinfo**", timeout=10000)
    except PlaywrightTimeout:
        logger.error("[飞书配置] 步骤13失败: 未进入凭证与基础信息页面")
        return False, None, None, "未进入凭证与基础信息页面"

    fs = session.file_system
    write_ok = fs.write_file(FEISHU_JSON_PATH, FEISHU_JSON_TEMPLATE)
    if not write_ok.success:
        logger.error("[飞书配置] 步骤13失败: 创建 feishu.json 失败")
        return False, None, None, "创建 feishu.json 失败"

    copy_btns = page.locator("div.secret-code__btns")
    try:
        await copy_btns.nth(0).click(timeout=DEFAULT_TIMEOUT)
    except PlaywrightTimeout:
        logger.error("[飞书配置] 步骤13失败: 点击 App ID 复制按钮失败")
        return False, None, None, "点击 App ID 复制按钮失败"
    time.sleep(0.3)
    update_json_field(session, FEISHU_JSON_PATH, "app_id")

    try:
        await copy_btns.nth(1).locator("span").first.click(timeout=DEFAULT_TIMEOUT)
    except PlaywrightTimeout:
        logger.error("[飞书配置] 步骤13失败: 点击 App Secret 复制按钮失败")
        return False, None, None, "点击 App Secret 复制按钮失败"
    time.sleep(0.3)
    update_json_field(session, FEISHU_JSON_PATH, "app_secret")

    read_res = fs.read_file(FEISHU_JSON_PATH, format="text")
    if not read_res.success or not read_res.content:
        logger.error("[飞书配置] 步骤13失败: 读取 feishu.json 失败")
        return False, None, None, "读取 feishu.json 失败"
    try:
        data = json.loads(read_res.content)
        app_id = (data.get("app_id") or "").strip()
        app_secret = (data.get("app_secret") or "").strip()
    except json.JSONDecodeError:
        logger.error("[飞书配置] 步骤13失败: feishu.json 格式错误")
        return False, None, None, "feishu.json 格式错误"
    if not app_id or not app_secret:
        logger.error("[飞书配置] 步骤13失败: 提取的凭证为空")
        return False, None, None, "提取的凭证为空"

    logger.info("[飞书配置] 步骤13成功: 凭证已提取")
    return True, app_id, app_secret, ""


async def _configure_event_subscription_and_add_event(page, _browser_svc) -> bool:
    """
    步骤9+10：配置事件订阅（使用长连接）并添加接收消息事件。
    1. 进入事件与回调页面，在「事件配置」区域选择「使用长连接接收事件」并保存
    2. 在「已添加事件」区域，点击「添加事件」，搜索并添加 im.message.receive_v1
    """
    logger.info("[飞书配置] 步骤9+10: 配置事件订阅并添加接收消息事件")
    if not await _click_menu_li_by_id_contains(page, "/event"):
        logger.error("[飞书配置] 步骤9失败: 点击事件与回调菜单失败")
        return False
    try:
        await page.wait_for_url("**/open.feishu.cn/app/**/event**", timeout=10000)
    except PlaywrightTimeout:
        logger.error("[飞书配置] 步骤9失败: 未进入事件与回调页面")
        return False

    # 点击页面关闭可能出现的弹窗
    try:
        await page.click("body", position={"x": 10, "y": 10}, timeout=3000)
        time.sleep(0.3)
    except PlaywrightTimeout:
        pass

    # 步骤9：找到包含「订阅方式」的父元素，在其内点击 button[type=button]
    try:
        text_elem = page.get_by_text("订阅方式", exact=False).first
        await text_elem.wait_for(state="visible", timeout=DEFAULT_TIMEOUT)
        parent = text_elem.locator("xpath=ancestor::*[.//button[@type='button']][1]")
        button = parent.locator("button[type='button']").first
        await button.wait_for(state="visible", timeout=DEFAULT_TIMEOUT)
        await button.click(timeout=DEFAULT_TIMEOUT)
    except PlaywrightTimeout as e:
        logger.warning("[飞书配置] 步骤9: 配置事件订阅失败: %s", e)
        return False

    # 步骤9：点击保存按钮
    try:
        await page.locator("button[type='button']").filter(has_text="保存").first.click(timeout=DEFAULT_TIMEOUT)
        logger.info("[飞书配置] 步骤9成功: 事件订阅已配置为长连接并保存")
    except PlaywrightTimeout as e:
        logger.warning("[飞书配置] 步骤9: 点击保存按钮失败: %s", e)
        return False
    time.sleep(0.5)

    # 步骤10：添加接收消息事件
    try:
        await page.locator("button[type='button']").filter(has_text="添加事件").first.click(timeout=DEFAULT_TIMEOUT)
        time.sleep(0.5)
        dialog = page.locator("div.ud__dialog__content")
        input_loc = dialog.locator("input[placeholder*='搜索']")
        await input_loc.first.fill("im.message.receive_v1", timeout=DEFAULT_TIMEOUT)
        time.sleep(0.5)
        checkbox_loc = dialog.locator("input[type='checkbox']")
        await checkbox_loc.first.click(timeout=DEFAULT_TIMEOUT)
        time.sleep(0.5)
        confirm_btn = dialog.locator("button[type='button']").filter(has_text="添加")
        await confirm_btn.first.click(timeout=DEFAULT_TIMEOUT)
        time.sleep(1)
    except PlaywrightTimeout as e:
        logger.warning("[飞书配置] 步骤10: 添加事件失败: %s", e)
        return False
    logger.info("[飞书配置] 步骤10成功: 已添加接收消息事件")
    time.sleep(1)
    return True


async def _configure_version_and_publish(page: Page) -> Tuple[bool, str]:
    """
    步骤12：版本管理与发布。
    点击 data-menu-id 包含 /version 的 li，创建版本、填写版本号与说明、保存并确认发布。

    Returns (success, error_message).
    """
    logger.info("[飞书配置] 步骤12: 版本管理与发布")
    if not await _click_menu_li_by_id_contains(page, "/version"):
        return False, "点击版本管理与发布菜单失败"
    try:
        await page.wait_for_url("**/open.feishu.cn/app/**/version**", timeout=10000)
    except PlaywrightTimeout:
        return False, "未进入版本管理页面"

    try:
        await page.locator("button[type='button']").filter(has_text="创建版本").first.click(timeout=DEFAULT_TIMEOUT)
    except PlaywrightTimeout:
        logger.warning("[飞书配置] 步骤12: 点击创建版本失败，尝试继续")
    time.sleep(1)

    # 填写版本号（input）
    await page.locator("input[placeholder*='对用户展示的正式版本号']").first.fill(VERSION_NUMBER, timeout=DEFAULT_TIMEOUT)

    # 填写版本说明（textarea）
    await page.locator("textarea[placeholder*='该内容将展示在应用的更新日志中']").first.fill(VERSION_DESC, timeout=DEFAULT_TIMEOUT)

    # 点击保存
    try:
        await page.locator("button[type='button']").filter(has_text="保存").first.click(timeout=DEFAULT_TIMEOUT)
    except PlaywrightTimeout:
        logger.warning("[飞书配置] 步骤12: 点击保存失败")
    time.sleep(0.5)

    # 点击确认发布（在确认弹窗 ud__confirm__content 内）
    try:
        confirm_content = page.locator("div.ud__confirm__content")
        await confirm_content.locator("button[type='button']").filter(has_text="确认发布").first.click(timeout=DEFAULT_TIMEOUT)
        logger.info("[飞书配置] 步骤12成功: 版本已发布")
    except PlaywrightTimeout:
        logger.warning("[飞书配置] 步骤12: 点击确认发布失败")
    time.sleep(3)
    return True, ""


async def _configure_callback_subscription(page, _browser_svc) -> bool:
    """
    步骤11：配置回调订阅（使用长连接）。
    找到 class=ud__overflow__item 且 style="order:1;" 的 div 元素，并点击。
    """
    logger.info("[飞书配置] 步骤11: 配置回调订阅")
    try:
        await page.locator("div.ud__overflow").first.click(timeout=DEFAULT_TIMEOUT)
        # 获取 div.ud__overflow 下的三个class=ud__overflow__item 的 div 元素，并点击第二个item div
        items = page.locator("div.ud__overflow").first.locator("div.ud__overflow__item")
        if await items.count() != 3:
            logger.error("[飞书配置] 步骤11: 未找到三个 ud__overflow__item 元素")
            return False
        await items.nth(1).click(timeout=DEFAULT_TIMEOUT)
    except PlaywrightTimeout as e:
        logger.warning("[飞书配置] 步骤11: 配置回调订阅失败: %s", e)
        return False
    logger.info("[飞书配置] 步骤11成功: 已点击回调配置")
    time.sleep(0.5)

    # 找到包含「订阅方式」的父元素，在其内点击 button[type=button]
    try:
        text_elem = page.get_by_text("订阅方式", exact=False).first
        await text_elem.wait_for(state="visible", timeout=DEFAULT_TIMEOUT)
        parent = text_elem.locator("xpath=ancestor::*[.//button[@type='button']][1]")
        button = parent.locator("button[type='button']").first
        await button.wait_for(state="visible", timeout=DEFAULT_TIMEOUT)
        await button.click(timeout=DEFAULT_TIMEOUT)
    except PlaywrightTimeout as e:
        logger.warning("[飞书配置] 步骤9: 配置事件订阅失败: %s", e)
        return False

    # 找到 button type=button 且内容为「保存」的按钮，点击它
    try:
        await page.locator("button[type='button']").filter(has_text="保存").first.click(timeout=DEFAULT_TIMEOUT)
        logger.info("[飞书配置] 步骤9成功: 事件订阅已配置为长连接并保存")
    except PlaywrightTimeout as e:
        logger.warning("[飞书配置] 步骤9: 点击保存按钮失败: %s", e)
        return False
    time.sleep(0.5)
    return True


async def configure_feishu_event_subscription(info: SessionInfo) -> Tuple[bool, str]:
    """
    在自动应用到配置成功后执行：配置事件订阅与回调（步骤9+10、11）、版本管理与发布（步骤12）。
    必须先启动 Gateway（含长连接客户端）后才能保存成功。
    使用 start_feishu_setup 缓存的 browser 实例。

    Returns (success, error_message).
    """
    ctx, err = await _get_browser_context(info)
    if ctx is None:
        return False, err or "Session not found"

    try:
        if not await _configure_event_subscription_and_add_event(ctx.page, ctx.browser_svc):
            return False, "配置事件订阅或添加接收消息事件失败"
        if not await _configure_callback_subscription(ctx.page, ctx.browser_svc):
            return False, "配置回调订阅失败"
        ok_step12, err_step12 = await _configure_version_and_publish(ctx.page)
        if not ok_step12:
            return False, err_step12 or "版本管理与发布失败"

        logger.info("[飞书配置] 事件订阅、回调与版本发布配置完成")
        return True, ""
    except PlaywrightTimeout as e:
        logger.exception("[飞书配置] 配置事件订阅超时: %s", e)
        return False, f"操作超时: {e}"
    except Exception as e:
        logger.exception("[飞书配置] 配置事件订阅失败")
        return False, str(e)


async def start_feishu_setup(info: SessionInfo) -> Tuple[bool, str]:
    """
    Start Feishu setup: open browser to open.feishu.cn and show QR code.
    Creates and caches browser_svc + pw_browser for reuse by continue_feishu_setup
    and configure_feishu_event_subscription.

    Returns (success, error_message).
    """
    session = info.session
    if not session:
        return False, "Session not found"

    try:
        ctx, err = await _acquire_browser_context(info)
        if ctx is None:
            if "不支持浏览器" in err:
                try:
                    cmd = f'bash -lc "nohup firefox \\"{FEISHU_OPEN_URL}\\" >/dev/null 2>&1 &"'
                    result = session.command.execute_command(cmd, timeout_ms=10000)
                    if result.success:
                        logger.info("Opened Feishu in Firefox (fallback)")
                        return True, ""
                    return False, result.error_message or "打开浏览器失败"
                except Exception as e2:
                    return False, str(e2)
            return False, err or "当前镜像不支持浏览器，请手动配置飞书凭证"

        await ctx.page.goto(FEISHU_OPEN_URL, timeout=NAV_TIMEOUT)
        await ctx.page.wait_for_load_state("domcontentloaded", timeout=DEFAULT_TIMEOUT)
        logger.info("Opened Feishu open platform via Playwright (cached for subsequent steps)")
        return True, ""
    except Exception as e:
        logger.exception("Failed to start Feishu setup (Playwright)")
        await clear_feishu_browser_cache(info.session_id)
        try:
            cmd = f'bash -lc "nohup firefox \\"{FEISHU_OPEN_URL}\\" >/dev/null 2>&1 &"'
            result = session.command.execute_command(cmd, timeout_ms=10000)
            if result.success:
                logger.info("Opened Feishu in Firefox (fallback)")
                return True, ""
            return False, result.error_message or "打开浏览器失败"
        except Exception as e2:
            return False, str(e2)


async def continue_feishu_setup(info: SessionInfo) -> Tuple[bool, Optional[str], Optional[str], str]:
    """
    Continue after user logged in: create app, configure permissions, extract credentials.
    使用 start_feishu_setup 缓存的 browser 实例；若未缓存则自动创建并缓存。

    Returns (success, app_id, app_secret, error).
    """
    session = info.session
    if not session:
        logger.error("[飞书配置] Session not found")
        return False, None, None, "Session not found"

    try:
        logger.info("[飞书配置] 开始继续配置流程")
        ctx, err = await _get_browser_context(info)
        if ctx is None:
            logger.error("[飞书配置] %s", err)
            return False, None, None, err or "当前镜像不支持浏览器，请手动配置飞书凭证"
        logger.info("[飞书配置] 浏览器已就绪 (使用缓存实例)")

        page = ctx.page

        # 步骤 5：创建企业自建应用
        logger.info("[飞书配置] 步骤5: 创建企业自建应用")
        try:
            await page.locator("button[type='button']").filter(has_text="创建企业自建应用").first.click(timeout=DEFAULT_TIMEOUT)
        except PlaywrightTimeout:
            logger.error("[飞书配置] 步骤5失败: 点击创建企业自建应用失败")
            return False, None, None, "点击创建企业自建应用失败"
        logger.info("[飞书配置] 步骤5: 已点击创建企业自建应用")
        time.sleep(0.5)

        # 步骤 6：填写应用信息（在弹窗 div.ud__dialog__content 内定位）
        logger.info("[飞书配置] 步骤6: 填写应用信息")
        dialog = page.locator("div.ud__dialog__content")
        input_loc = dialog.locator("input.ud__native-input")
        await input_loc.first.fill(APP_NAME)
        logger.info("[飞书配置] 步骤6: 已填写应用名称")

        await dialog.locator("textarea").first.fill(APP_DESC)
        logger.info("[飞书配置] 步骤6: 已填写应用描述")

        # 点击 dialog 内 type=button 且内容为「创建」的按钮
        try:
            await dialog.locator("button[type='button']").filter(has_text="创建").first.click(timeout=DEFAULT_TIMEOUT)
        except PlaywrightTimeout:
            logger.error("[飞书配置] 步骤6失败: 点击创建按钮失败")
            return False, None, None, "点击创建按钮失败"
        logger.info("[飞书配置] 步骤6成功: 已填写应用信息并创建")

        # 验证是否进入应用能力页
        try:
            await page.wait_for_url("**/open.feishu.cn/app/**/capability/**", timeout=10000)
        except PlaywrightTimeout:
            pass
        if "/capability/" not in page.url:
            logger.warning("[飞书配置] 未检测到应用能力页 URL，继续执行")
        else:
            logger.info("[飞书配置] 已进入应用能力页")

        # 步骤 7：添加机器人能力
        logger.info("[飞书配置] 步骤7: 添加机器人能力")
        try:
            tabs_content = page.locator(".ud__tabs__content")
            first_card = tabs_content.locator(".ud__card").first
            await first_card.locator("button[type='button']").filter(has_text="添加").first.click(timeout=DEFAULT_TIMEOUT)
            logger.info("[飞书配置] 步骤7成功: 已添加机器人能力")
        except PlaywrightTimeout:
            logger.error("[飞书配置] 步骤7失败: 点击机器人添加按钮失败")
            return False, None, None, "点击机器人添加按钮失败"
        try:
            await page.wait_for_url("**/open.feishu.cn/app/**/bot**", timeout=10000)
        except PlaywrightTimeout:
            logger.error("[飞书配置] 步骤7失败: 未进入机器人配置页面")
            return False, None, None, "未进入机器人配置页面"
        time.sleep(1)

        # 步骤 8：开通权限（点击 data-menu-id 包含 /auth 的 li，进入权限页）
        logger.info("[飞书配置] 步骤8: 开通权限")
        if not await _click_menu_li_by_id_contains(page, "/auth"):
            logger.error("[飞书配置] 步骤8失败: 点击权限管理菜单失败")
            return False, None, None, "点击权限管理菜单失败"
        try:
            await page.wait_for_url("**/open.feishu.cn/app/**/auth**", timeout=10000)
        except PlaywrightTimeout:
            logger.error("[飞书配置] 步骤8失败: 未进入权限管理页面")
            return False, None, None, "未进入权限管理页面"

        # 点击「批量导入/导出权限」按钮
        try:
            await page.locator("button[type='button']").filter(has_text="批量导入/导出权限").first.click(timeout=DEFAULT_TIMEOUT)
        except PlaywrightTimeout:
            logger.error("[飞书配置] 步骤8失败: 点击批量导入/导出权限按钮失败")
            return False, None, None, "点击批量导入/导出权限按钮失败"
        time.sleep(0.5)

        # 在弹窗内清空并填入权限 JSON
        try:
            logger.info("[飞书配置] 步骤8.1: 等待权限弹窗...")
            perm_dialog = page.locator("div.ud__dialog__content")
            await perm_dialog.wait_for(state="visible", timeout=DEFAULT_TIMEOUT)
            logger.info("[飞书配置] 步骤8.2: 点击「恢复默认值」清空...")
            await perm_dialog.locator("button[type='button']").filter(has_text="恢复默认值").first.click(timeout=DEFAULT_TIMEOUT)
            time.sleep(0.5)
            logger.info("[飞书配置] 步骤8.3: 定位 Monaco 编辑器并点击最后一行...")
            editor_view = perm_dialog.locator("div.view-lines.monaco-mouse-cursor-text").first
            await editor_view.locator(".view-line").last.click(timeout=DEFAULT_TIMEOUT)
            logger.info("[飞书配置] 步骤8.4: Backspace 清空编辑器...")
            for _ in range(160):
                await page.keyboard.press("Backspace")
            time.sleep(0.1)
            logger.info("[飞书配置] 步骤8.5: 填入权限 JSON...")
            await page.keyboard.insert_text(PERMISSIONS_IMPORT_JSON)
            logger.info("[飞书配置] 步骤8.6: 删除 Monaco 自动补全多余字符...")
            await page.keyboard.press("Backspace")
            time.sleep(0.5)
            logger.info("[飞书配置] 步骤8.7: 点击「下一步，确认新增权限」...")
            await perm_dialog.locator("button[type='button']").filter(has_text="下一步，确认新增权限").first.click(timeout=DEFAULT_TIMEOUT)
            logger.info("[飞书配置] 步骤8.8: 点击「申请开通」...")
            await perm_dialog.locator("button[type='button']").filter(has_text="申请开通").first.click(timeout=DEFAULT_TIMEOUT)
            logger.info("[飞书配置] 步骤8: 已填入批量导入权限 JSON")
        except PlaywrightTimeout as e:
            logger.error("[飞书配置] 步骤8失败: 在弹窗内填写权限 JSON 失败 (最后成功步骤见上方日志) - %s", e)
            return False, None, None, "在弹窗内填写权限 JSON 失败"
        time.sleep(1)

        # 点击 drawer 底部的「确认」或「确定」按钮（配置权限数据范围）
        try:
            footer = page.locator("div.ud__drawer__footer").first
            await footer.wait_for(state="visible", timeout=5000)
            confirm_btn = footer.locator("button[type='button']").filter(has_text="确认")
            await confirm_btn.first.click(timeout=DEFAULT_TIMEOUT)
            logger.info("[飞书配置] 步骤8完成: 权限配置")
        except PlaywrightTimeout:
            logger.warning("[飞书配置] 步骤8: 未找到确认按钮，继续执行")
        time.sleep(1)

        # 步骤 9、10、11、12（事件订阅、回调、版本发布）在自动应用到配置成功后执行，见 configure_feishu_event_subscription

        # 步骤 13：提取凭证
        ok, app_id, app_secret, err = await _extract_credentials(page, session)
        if not ok:
            return False, None, None, err
        logger.info("[飞书配置] 全部步骤完成，配置成功")
        return True, app_id, app_secret, ""

    except PlaywrightTimeout as e:
        logger.exception("Playwright timeout: %s", e)
        return False, None, None, f"操作超时: {e}"
    except Exception as e:
        logger.exception("Feishu setup failed (Playwright)")
        return False, None, None, str(e)
