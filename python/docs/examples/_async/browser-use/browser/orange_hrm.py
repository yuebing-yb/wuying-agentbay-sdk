"""
示例：企业 HR 管理系统（OrangeHRM）自动化
功能：实现自动登录系统、进入 PIM 员工管理模块、录入新员工信息，并提取生成的员工 ID。
重点：使用 agent.login 自动注入凭据、通过 agent.act 执行多步流程编排、以及利用 agent.extract 进行结构化数据提取。
"""

import asyncio
import os
import json
from pydantic import BaseModel, Field
from agentbay import AsyncAgentBay as AgentBay
from agentbay import CreateSessionParams, BrowserOption, ActOptions, ExtractOptions


class EmployeeProfile(BaseModel):
    full_name: str = Field(..., description="Full name of the employee")
    employee_id: str = Field(..., description="The ID assigned to the employee")


async def main():
    api_key = os.getenv("AGENTBAY_API_KEY")
    skill_id = os.getenv("AGENTBAY_SKILL_ID")

    agent_bay = AgentBay(api_key=api_key)
    params = CreateSessionParams(image_id="browser_latest")
    session_result = await agent_bay.create(params)
    session = session_result.session

    try:
        await session.browser.initialize(BrowserOption())
        operator = session.browser.operator

        await operator.navigate("https://opensource-demo.orangehrmlive.com/")

        login_config = json.dumps({"api_key": api_key, "skill_id": skill_id})
        login_result = await operator.login(login_config=login_config)
        if not login_result.success:
            print(f"Login failed: {login_result.message}")
            return

        await operator.act(ActOptions(action="点击左侧菜单的 'PIM'"))
        await operator.act(ActOptions(action="点击 'Add Employee'"))
        await operator.act(
            ActOptions(action="输入 First Name 'Agent', Last Name 'Bay'，点击 'Save'")
        )

        await asyncio.sleep(2)

        ok, extraction = await operator.extract(
            ExtractOptions(
                instruction="提取保存后的员工姓名和ID信息", schema=EmployeeProfile
            )
        )

        if ok:
            print(f"Created: {extraction.full_name} ID: {extraction.employee_id}")

    finally:
        await operator.close()
        await agent_bay.delete(session)


if __name__ == "__main__":
    asyncio.run(main())
