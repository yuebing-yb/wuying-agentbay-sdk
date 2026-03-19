# Agent Modules

Agent modules are specialized AI task execution units running in AgentBay windows environment to execute tasks described in natural language.

> **💡 Async API Support**: This guide uses synchronous API. For async patterns, see [Async Agent API](../../../../python/docs/api/async/async-agent.md).

## 🤖 Agent Module Overview

Agent modules are specialized AI task execution units running in AgentBay windows/linux environment to execute tasks described in natural language. 
The task to be executed can be as simple as "Create a word document, input some words and save the document.", in which only one application is involved, or as complex as "Find out the current weather in New York City by Google/Baidu, and write the weather report to a word document, send the word document to a specific email address", in which multiple applications are involved.

Currently, there are three types of agents: ComputerUseAgent, BrowserUseAgent, and MobileUseAgent.
- 🖥️ ComputerUseAgent module is designed for tasks that involve multiple applications。
- 🌐 BrowserUseAgent module is designed for tasks that involve specifically web browsers
- 📱 MobileUseAgent module is designed for tasks that involve mobile device automation.

The agents are capable of understanding user instructions, planning task execution steps, operating various applications, and managing files and folders on the computer or mobile devices.

> **⚠️ Note**: Currently, for agent services (including ComputerUseAgent, BrowserUseAgent, and MobileUseAgent), we do not provide services for overseas users registered with **alibabacloud.com**.

## System Image Support

Agent Module functionality is currently only available on specific system images:

| System Image | Agent Module Support | Available APIs | Supported Agent |
|-------------|---------------------|----------------|----------|
| `windows_latest` | ✅ Supported | `execute_task`, `get_task_status`, `terminate_task` | ComputerUseAgent |
| `linux_latest` | ✅ Supported | `execute_task`, `get_task_status`, `terminate_task` | BrowserUseAgent(⚠️BETA) |
| `mobile_latest` | ✅ Supported | `execute_task`, `get_task_status`, `terminate_task` | MobileUseAgent |
| `browser_latest` | ✅ Supported | `execute_task`, `get_task_status`, `terminate_task` | BrowserUseAgent(⚠️BETA) |
| `code_latest` | ❌ Not Supported | - |  - |

**Important:** When using ComputerUseAgent Module features, you must create sessions with `image_id="windows_latest"` to ensure the required MCP tools are available. When using BrowserUseAgent Module features, you must create sessions with `image_id="linux_latest"`. When using MobileUseAgent Module features, you must create sessions with `image_id="mobile_latest"`.

**NOTE:** ⚠️ BrowserUseAgent is still in beta. Please use with caution.

## Creating Agent Sessions

```python
from agentbay import AgentBay, CreateSessionParams
from pydantic import BaseModel

agent_bay = AgentBay()

# Create a session for Agent module usage
agent_params = CreateSessionParams(
    image_id="windows_latest",
    labels={"project": "ai-agent"}
)

result = agent_bay.create(agent_params)
if result.success:
    agent_session = result.session
    print(f"Session created with ID: {agent_session.session_id}")
else:
    print(f"Session creation failed: {result.error_message}")
```

## Agent Capabilities
- Office Automation: Word/Excel/PowerPoint automation
- File Operations: Create/Delete/Move/Copy files and folders
- Information Processing: 
    - Gather information from webpages
    - Extract information from a web page
    - Fill forms in a web page
- Text Editing: Using notepad to edit (Read/Write/Edit) text file

### Task Execution
#### ComputerUseAgent
```python
# Execute a task using natural language
task_description = "Create a text file named hello.txt in C:\\Temp"
execution_result = agent_session.agent.computer.execute_task_and_wait(task_description, timeout=180)

if execution_result.success:
    print("Task completed successfully!")
    print(f"Task ID: {execution_result.task_id}")
    print(f"Task status: {execution_result.task_status}")
else:
    print(f"Task failed: {execution_result.error_message}")
```

#### BrowserUseAgent
```python
# Execute a task using natural language
class OutputSchema(BaseModel):
    """Schema for task result."""
    city: str
    temperature:str
    weather:str

task_description = "Navigate to baidu.com and query the weather in Beijing"
execution_result = agent_session.agent.browser.execute_task_and_wait(
    task=task_description,
    timeout=180,
    use_vision=False,
    output_schema=OutputSchema
    full_page_screenshot=False
)

if execution_result.success:
    print("Task completed successfully!")
    print(f"Task ID: {execution_result.task_id}")
    print(f"Task status: {execution_result.task_status}")
else:
    print(f"Task failed: {execution_result.error_message}")
```

#### MobileUseAgent
```python
# Execute a task using natural language
task_description = "Open WeChat app and send a message"
execution_result = agent_session.agent.mobile.execute_task_and_wait(
    task_description,
    timeout=180,
    max_steps=100
)

if execution_result.success:
    print("Task completed successfully!")
    print(f"Task ID: {execution_result.task_id}")
    print(f"Task status: {execution_result.task_status}")
    print(f"Task result: {execution_result.task_result}")
else:
    print(f"Task failed: {execution_result.error_message}")
```

## Agent Streaming Output (Beta)

MobileUseAgent supports real-time streaming output via WebSocket, allowing you to receive reasoning steps, content updates, tool calls, and error events as they happen during task execution.

### Streaming with Callbacks

```python
from agentbay import AgentBay, CreateSessionParams

agent_bay = AgentBay()
result = agent_bay.create(CreateSessionParams(image_id="mobile_latest"))
session = result.session

def on_reasoning(event):
    print(f"[Reasoning] {event.content}")

def on_content(event):
    print(f"[Content] {event.content}")

def on_error(event):
    print(f"[Error] {event.error}")

execution_result = session.agent.mobile.execute_task_and_wait(
    task="Open the Settings app and check the device name",
    timeout=180,
    on_reasoning=on_reasoning,
    on_content=on_content,
    on_error=on_error,
)

print(f"Success: {execution_result.success}")
print(f"Result: {execution_result.task_result}")

session.delete()
```

### Using TaskExecution Handle

For more control, use `execute_task` to get a `TaskExecution` handle that supports deferred waiting:

```python
execution = await session.agent.mobile.execute_task(
    task="Take a screenshot of the home screen",
    on_content=lambda e: print(e.content),
)

# Do other work while the task runs...

result = await execution.wait(timeout=120)
```

### Human-in-the-Loop

The `on_call_for_user` callback enables interactive workflows where the agent can request user input:

```python
def handle_user_call(event):
    print(f"Agent asks: {event.content}")
    return "Yes, please continue"

execution_result = session.agent.mobile.execute_task_and_wait(
    task="Install an app and confirm permissions",
    timeout=300,
    on_call_for_user=handle_user_call,
)
```

> **Note**: Agent streaming is currently available for MobileUseAgent only. Streaming requires a WebSocket connection which is automatically managed by the SDK.

For language-specific streaming examples, see:
- [Python (Async)](../../../../python/docs/examples/_async/mobile-use/mobile_agent_streaming.py) | [Python (Sync)](../../../../python/docs/examples/_sync/mobile-use/mobile_agent_streaming.py)
- [TypeScript](../../../../typescript/docs/examples/mobile-use/mobile-agent-streaming.ts)
- [Golang](../../../../golang/docs/examples/mobile-use/mobile_agent_streaming/main.go)
- [Java](../../../../java/agentbay/src/main/java/com/aliyun/agentbay/examples/MobileAgentStreamingExample.java)

## 📚 Related Resources

- [Session Management Guide](../basics/session-management.md)
- [Data Persistence Guide](../basics/data-persistence.md)

## 🆘 Getting Help

If you encounter issues with Agent modules:

1. Check the [Documentation](../../README.md) for detailed information
2. Search [GitHub Issues](https://github.com/agentbay-ai/wuying-agentbay-sdk/issues) for similar problems
3. Contact support with detailed error information and reproduction steps
4. Please refer to the [BrowserUseAgent Example](../../../../python/docs/examples/_async/common-features/advanced/agent_module/browser_use_agent.py) to see how to use the Agent.
5. Please refer to the [ComputerUseAgent Example](../../../../python/docs/examples/_async/common-features/advanced/agent_module/computer_use_agent.py) to see how to use the Agent.
6. Please refer to the [Agent API Definition](../../../../python/docs/api/async/async-agent.md) for more details.
