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
from agentbay.async_api import BrowserOption, ActOptions


async def main():
    api_key = os.getenv("AGENTBAY_API_KEY")
    if not api_key:
        print("Error: AGENTBAY_API_KEY not set")
        return
    agentbay = AsyncAgentBay(api_key=api_key)
    session_result = await agentbay.create(CreateSessionParams(image_id="browser_latest"))
    session = session_result.session
    try:
        if not await session.browser.initialize(BrowserOption()):
            print("Browser init failed")
            return
        agent = session.browser.agent

        await agent.navigate("http://116.62.195.152:3000")
        await agent.act(ActOptions(action="帮我添加商品"))
        await agent.act(
            ActOptions(
                action="填写表单",
                variables={
                    "商品": "iPhone 16 Pro",
                    "品牌": "iphone",
                    "价格": "7999.0",
                    "URL": "https://streaming-tests-h5.oss-cn-hangzhou.aliyuncs.com/image/iPhone-16-Pro.jpg",
                    "描述": "6.3英寸显示，A18 Pro，4800万像素摄像头，120Hz ProMotion",
                    "库存": "230.0",
                },
            )
        )
        await agent.act(ActOptions(action="点击提交/保存按钮"))
        await asyncio.sleep(2)
    finally:
        try:
            await session.browser.agent.close()
        except Exception:
            pass
        await agentbay.delete(session)


if __name__ == "__main__":
    asyncio.run(main())
