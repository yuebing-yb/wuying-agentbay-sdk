"""
示例：后台新增商品（表单填报）
打开管理后台
通过变量注入填写表单并提交
重点：ActOptions.variagentbayles 批量字段
"""

import asyncio
import os
from agentbay import AsyncAgentBay
from agentbay import CreateSessionParams
from agentbay import BrowserOption
from agentbay import ActOptions


async def main():
    api_key = os.getenv("AGENTBAY_API_KEY")
    if not api_key:
        print("Error: AGENTBAY_API_KEY not set")
        return
    agentbay = AsyncAgentBay(api_key=api_key)
    session_result = await agentbay.create(CreateSessionParams(image_id="browser_latest"))
    if not session_result.success or not session_result.session:
        print(f"Failed to create session: {session_result.error_message}")
        return
    session = session_result.session
    try:
        if not await session.browser.initialize(BrowserOption()):
            print("Browser init failed")
            return
        agent = session.browser.agent

        await agent.navigate("https://httpbin.org/forms/post")
        await agent.act(
            ActOptions(
                action="填写披萨订单表单并提交",
                variables={
                    "Customer name": "John Doe",
                    "Telephone": "1234567890", 
                    "E-mail address": "john@example.com",
                    "Pizza Size": "large",
                    "Pizza Toppings": "bacon,cheese",
                    "Delivery instructions": "Please ring the doorbell",
                },
            )
        )
        await asyncio.sleep(2)
    finally:
        try:
            await session.browser.agent.close()
        except Exception:
            pass
        await agentbay.delete(session)


if __name__ == "__main__":
    asyncio.run(main())
