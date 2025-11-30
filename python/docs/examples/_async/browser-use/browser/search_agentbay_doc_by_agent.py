"""
示例：使用PageUse Agent的AgentBay接口访问阿里云并搜索“AgentBay帮助文档”
打开 https://www.aliyun.com
搜索“AgentBay帮助文档”，点击第一条搜索结果并进入“帮助文档”，滚动到页面底部
重点：全程使用 BrowserAgent API
"""

import os
import asyncio

from agentbay import AsyncAgentBay
from agentbay import CreateSessionParams
from agentbay._async.browser import BrowserOption
from agentbay._async.browser import ActOptions


async def main():
    # Get API key from environment variable
    api_key = os.getenv("AGENTBAY_API_KEY")
    if not api_key:
        print("Error: AGENTBAY_API_KEY environment variable not set")
        return

    # Initialize AgentBay client
    print("Initializing AgentBay client...")
    agent_bay = AsyncAgentBay(api_key=api_key)

    # Create a session
    print("Creating a new session...")
    params = CreateSessionParams(
        image_id="browser_latest",  # Specify the image ID
    )
    session_result = await agent_bay.create(params)

    if session_result.success:
        session = session_result.session
        print(f"Session created with ID: {session.session_id}")

        if await session.browser.initialize(BrowserOption()):
            print("Browser initialized successfully")
            agent = session.browser.agent

            await agent.navigate("https://www.aliyun.com")

            await agent.act(
                ActOptions(action="搜索框输入'AgentBay帮助文档'并回车")
            )
            await agent.act(ActOptions(action="点击搜索结果中的第一项"))
            await agent.act(ActOptions(action="点击'帮助文档'"))
            await agent.act(ActOptions(action="滚动页面到底部"))

            await asyncio.sleep(5)
        else:
            print("Failed to initialize browser")
        await agent_bay.delete(session)


if __name__ == "__main__":
    asyncio.run(main())
