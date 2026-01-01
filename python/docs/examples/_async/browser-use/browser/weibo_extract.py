"""
示例：社交媒体（微博）页面总结与分析
功能：访问微博、使用自动凭据注入登录、并对当前页面进行总结分析
重点：agent.login 自动登录 + agent.extract 内容提取总结
"""

import asyncio
import os
import json
from typing import List
from pydantic import BaseModel, Field
from agentbay import AsyncAgentBay as AgentBay
from agentbay import CreateSessionParams
from agentbay import BrowserOption
from agentbay import ActOptions, ExtractOptions


class WeiboPost(BaseModel):
    username: str = Field(..., description="用户名")
    content: str = Field(..., description="博文内容")
    timestamp: str = Field(..., description="发布时间")
    likes: int = Field(default=0, description="点赞数")


class WeiboResult(BaseModel):
    posts: List[WeiboPost] = Field(default_factory=list)


async def main():
    api_key = os.getenv("AGENTBAY_API_KEY")
    skill_id = os.getenv("AGENTBAY_SKILL_ID")
    skill_id = "AGENTBAY_SKILL_ID"

    if not api_key or not skill_id:
        print("Please set AGENTBAY_API_KEY and AGENTBAY_SKILL_ID")
        return

    agent_bay = AgentBay(api_key=api_key)
    params = CreateSessionParams(image_id="browser_latest")
    session_result = await agent_bay.create(params)

    if not session_result.success or not session_result.session:
        print(f"Failed to create session: {session_result.error_message}")
        return

    session = session_result.session

    try:
        browser_option = BrowserOption(
            use_stealth=True,
            solve_captchas=True,
        )
        await session.browser.initialize(browser_option)
        operator = session.browser.operator

        await operator.navigate("https://weibo.com")
        await operator.act(ActOptions(action=f"点击登录"))
        await operator.act(ActOptions(action=f"点击账号登录"))

        login_config = json.dumps({"api_key": api_key, "skill_id": skill_id})
        login_result = await operator.login(login_config=login_config)
        if not login_result.success:
            print(f"Login failed: {login_result.message}")
            return

        print("Login successful, starting search...")

        search_keyword = "人工智能"
        await operator.act(ActOptions(action=f"在搜索框输入{search_keyword}并回车"))
        ok, extraction = await operator.extract(
            ExtractOptions(
                instruction=f"提取页面上关于{search_keyword}的所有博文信息，包括用户名、内容、时间、点赞数",
                schema=WeiboResult,
            )
        )
        if ok and extraction:
            print(f"Successfully extracted {len(extraction.posts)} posts.")
            for post in extraction.posts:
                print(f"[{post.username}]: {post.content[:50]}... ({post.likes} likes)")
        else:
            print("Extraction failed or returned no data.")

    except Exception as e:
        print(f"An error occurred: {e}")
    finally:
        await operator.close()
        await agent_bay.delete(session)


if __name__ == "__main__":
    asyncio.run(main())
