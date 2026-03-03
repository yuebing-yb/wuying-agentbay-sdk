# Browser Hybrid Usage Guide
⚠️ This is a BETA feature, use with caution.

In the context of AgentBay, there are three roles that can manipulate the browser to perform specific tasks, they are:

- [Browser Operator](browser-operator.md): Mainly about page operations with small parts of AI capability
- [Browser Agent](../../common-features/advanced/agent-modules.md): Performing tasks described in natural language with the capability of planning and execution
- [Playwright](https://playwright.dev): An open source browser automation framework, performs specific actions with API calls


## Comparison

| Features | Browser Operator | Browser Agent | Playwright |
|------|-----------------|---------------|------------|
| **Application scenarios** | General Tasks described in Natural language  | Page Operations, like extract, observe | API Calls，like goto url，Click | 
| **Capabilities**|Full AI capability of planning and execution| Parts of AI capability | No AI capability|

## Hybrid Usage
We provide a capability that allows these three roles to share the same browser instance, with the prerequisite that they all initialize the browser via session.browser.initialize() before performing any operations.

You can use the playwright, browser operator and browser agent as a combination to perform a specific task.
The playwright, browser operator and browser agent share and manipulate the same browser instance.

A typical hybrid usage:
- **Use Playwright to launch a remote browser**
- **Use Playwright to navigate to a specific website**
- **Use Browser Agent to perform a task described in natural language**
- **Use Browser Operator to extract information from the website**

This feature of hybrid usage is supported in Linux image and Browser image

## Hybrid Usage Example

```python
import os
import asyncio
from pydantic import BaseModel, Field
from playwright.async_api import async_playwright
from agentbay import AgentBay
from agentbay import CreateSessionParams
from agentbay import BrowserOption
from agentbay import BrowserOperator, ActOptions, ExtractOptions

class WeatherSchema(BaseModel):
    """Schema for weather query."""

    Weather: str
    City: str
    Temperature: str

class DummySchema(BaseModel):
    """Schema for page extraction."""

    title: str


async def main():
    agent_bay = AgentBay(api_key=os.getenv("AGENTBAY_API_KEY"))

    # Create a browser session
    params = CreateSessionParams(image_id="browser_latest")  # your image id
    session_result = agent_bay.create(params)
    if not session_result.success:
        print(f"Create session failed: {session_result.error_message}")
        return
    session = session_result.session

    # Initialize managed browser
    print("🚀 Browser initialization")
    await session.browser.initialize(BrowserOption())

    endpoint_url = await session.browser.get_endpoint_url()
    print("endpoint_url =", endpoint_url)

    async with async_playwright() as p:
        browser = await p.chromium.connect_over_cdp(endpoint_url)

        context = (
            browser.contexts[0]
            if browser.contexts
            else await browser.new_context()
        )
        page = await context.new_page()
        await page.goto("http://www.baidu.com")
        title = await page.title()
        assert title is not None
        print(f"Page title: {title}")
        await asyncio.sleep(15)
        task = "在百度查询上海天气"
        print("🚀 task of Query the weather in Shanghai")

        result = await session.agent.browser.execute_task_and_wait(
            task, 180, use_vision=False, output_schema=WeatherSchema
        )
        assert result.success
        assert result.request_id != ""
        assert result.error_message == ""
        logger.info(f"✅ result {result.task_result}")
        assert result.success

        result, obj = await session.browser.operator.extract(
            ExtractOptions(instruction="Extract the title", schema=DummySchema)
        )
        logger.info(f"✅ result of extract {result}\n{obj}")

        await page.close()
        await browser.close()

if __name__ == "__main__":
    asyncio.run(main())
```
