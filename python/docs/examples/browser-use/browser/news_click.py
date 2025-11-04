"""
示例：在同一浏览器会话中混用 Playwright(连接与新页面监听)与 PageUse Agent(智能动作执行与网页抽取)
打开百度首页点击“新闻”并校验标题
重点：演示 PageUse Agent 与 Playwright 混排；通过显式传入 page 保持两者对齐，验证导航期间的焦点同步
"""

import os
import asyncio
import logging

from playwright.async_api import async_playwright
from pydantic import BaseModel

from agentbay import AgentBay
from agentbay.session_params import CreateSessionParams
from agentbay.browser.browser import BrowserOption, Browser
from agentbay.browser.browser_agent import ActOptions, ActResult, ExtractOptions


class DummySchema(BaseModel):
    title: str


class TestRunner:
    def __init__(self, session, logger):
        self.session = session
        self.logger = logger

    async def test_click_action(self):
        """测试点击动作"""
        browser = self.session.browser
        assert isinstance(browser, Browser), "浏览器实例类型错误"
        assert browser.initialize(BrowserOption()), "浏览器初始化失败"

        endpoint_url = browser.get_endpoint_url()
        assert endpoint_url is not None, "无法获取浏览器端点URL"

        async with async_playwright() as p:
            playwright_browser = await p.chromium.connect_over_cdp(endpoint_url)
            assert playwright_browser is not None, "无法连接到浏览器"
            context = playwright_browser.contexts[0]
            page = await context.new_page()
            await page.goto("http://www.baidu.com", wait_until="networkidle")

            async with page.context.expect_page() as new_page_info:
                action_str = "点击页面顶部的'新闻'链接"

                act_result = await browser.agent.act_async(
                    ActOptions(action=action_str), page=page
                )
                self.logger.info("点击动作结果: %s", act_result)
                self.logger.info("resource_url: %s", self.session.resource_url)
                new_page = await new_page_info.value
                title = await new_page.title()
                self.logger.info("new_page_url: %s title %s", new_page.url, title)

                assert isinstance(act_result, ActResult), "返回结果类型错误"
                assert act_result.success, f"点击失败: {act_result.message}"

                await new_page.wait_for_load_state("networkidle")
                await new_page.wait_for_timeout(1000)

                result, objs = await browser.agent.extract_async(
                    ExtractOptions(instruction="提取页面标题", schema=DummySchema),
                    page=new_page,
                )
                self.logger.info("result = %s", result)
                self.logger.info("objs = %s", objs)

                assert result
                assert "新闻" in objs.title

                await new_page.close()


async def main():
    api_key = os.getenv("AGENTBAY_API_KEY")
    if not api_key:
        print("Error: AGENTBAY_API_KEY not set")
        return

    logging.basicConfig(level=logging.INFO)
    logger = logging.getLogger("runner")

    agent_bay = AgentBay(api_key=api_key)
    params = CreateSessionParams(image_id="browser_latest")
    session_result = agent_bay.create(params)
    if not session_result.success:
        print("Create session failed")
        return
    session = session_result.session

    try:
        await session.browser.initialize_async(BrowserOption())

        runner = TestRunner(session=session, logger=logger)
        await runner.test_click_action()
    finally:
        agent_bay.delete(session)


if __name__ == "__main__":
    asyncio.run(main())
