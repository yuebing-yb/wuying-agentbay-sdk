"""
示例：在同一浏览器会话中混用 Playwright(连接与新页面监听)与 PageUse Agent(动作执行与页面内容提取)
用 Playwright 导航与监听新页面
用 PageUse Agent 执行动作（搜索、点击、滚动）
重点：演示 PageUse Agent 与 Playwright 混排；焦点/页面以传入的 page 为准
注意：新页面打开后，将 Playwright 的 new_page 传入 Agent(page=new_page), 确保两者指向同一页面
"""

import os
import asyncio

from agentbay import AgentBay
from agentbay.session_params import CreateSessionParams
from agentbay.browser.browser import BrowserOption
from agentbay.browser.browser_agent import ActOptions
from playwright.async_api import async_playwright


async def main():
    api_key = os.getenv("AGENTBAY_API_KEY")
    agent_bay = AgentBay(api_key=api_key)
    session = agent_bay.create(CreateSessionParams(image_id="browser_latest")).session
    try:
        assert await session.browser.initialize_async(BrowserOption())
        agent = session.browser.agent

        endpoint_url = session.browser.get_endpoint_url()
        async with async_playwright() as p:
            playwright_browser = await p.chromium.connect_over_cdp(endpoint_url)
            context = (
                playwright_browser.contexts[0]
                if playwright_browser.contexts
                else await playwright_browser.new_context()
            )
            page = await context.new_page()

            # 先用 Playwright 导航
            await page.goto("https://www.aliyun.com", wait_until="domcontentloaded")

            # 让 Agent 跟上当前 Playwright 页面（显式传 page）
            await agent.act_async(
                ActOptions(action="搜索框输入'AgentBay帮助文档'并回车"), page=page
            )

            # 等待搜索结果加载
            await page.wait_for_timeout(2000)

            # 点击搜索结果（在同一页面导航）
            await agent.act_async(
                ActOptions(action="点击搜索结果中的第一项"),
                page=page,
            )

            # 等待页面导航完成
            await page.wait_for_load_state("domcontentloaded", timeout=60000)

            # 在当前页面上继续用 Agent
            await agent.act_async(ActOptions(action="滚动页面到底部"), page=page)

            print("Successfully completed browser automation with mixed Playwright and PageUse Agent")

            await playwright_browser.close()
    finally:
        agent_bay.delete(session)


if __name__ == "__main__":
    asyncio.run(main())
