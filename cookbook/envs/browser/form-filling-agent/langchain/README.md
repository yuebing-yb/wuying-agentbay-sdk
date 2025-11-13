# LangChain Integration

This directory contains the LangChain-specific integration for the form-filling agent.

## Sample Output

When the agent successfully fills a form, you will see output similar to the following:

```
Creating LangChain form filling agent...
Creating AgentBay browser session...
[DATE] [TIME] | AgentBay | INFO | [PID]:[TID] | agentbay.context:get:400 | 🔗 API Call: GetContext
[DATE] [TIME] | AgentBay | INFO | [PID]:[TID] | agentbay.context:get:400 |   └─ AllowCreate=True, Name=[CONTEXT_NAME]
[DATE] [TIME] | AgentBay | INFO | [PID]:[TID] | agentbay.context:get:413 | ✅ API Response received
[DATE] [TIME] | AgentBay | INFO | [PID]:[TID] | agentbay.agentbay:create:400 | Adding context sync for file transfer operations: ContextSync(context_id='[CONTEXT_ID]', path='[PATH]', policy=None)
[DATE] [TIME] | AgentBay | INFO | [PID]:[TID] | agentbay.agentbay:create:625 | ✅ API Response: CreateSession, RequestId=[REQUEST_ID]
...
[DATE] [TIME] | AgentBay | INFO | [PID]:[TID] | agentbay.session:_call_mcp_tool_api:1063 | ✅ API Response: CallMcpTool, RequestId=[REQUEST_ID]
[DATE] [TIME] | AgentBay | INFO | [PID]:[TID] | agentbay.session:_call_mcp_tool_api:1063 |   └─ tool=page_use_screenshot
[browser_screenshot] Output: {"success": true, "message": "Screenshot captured successfully", "file_path": "[FILE_PATH]"}
Final result: I have successfully completed all the requested steps:
1. Navigated to [URL]
2. Opened the time selector and selected "最近10年" (Last 10 years)
3. Waited for [TIME_S] seconds
4. Clicked on the Line chart icon
5. Waited another [TIME_S] seconds
6. Saved a screenshot of the resulting page to [FILE_PATH]
The screenshot has been saved successfully and shows the statistical data in line chart format for the last 10 years as requested.
```

## Setup

### 1. Create Virtual Environment

First, create a virtual environment to isolate project dependencies:

```bash
# Create virtual environment
python -m venv form-filling-agent-env

# Activate virtual environment
# On Windows:
form-filling-agent-env\Scripts\activate
# On macOS/Linux:
source form-filling-agent-env/bin/activate
```

### 2. Install Dependencies

Install the required packages:

```bash
# Update pip
pip install --upgrade pip
```

You can install dependencies using the requirements file:

```bash
pip install -r requirements.txt
```

### 3. Configure Environment Variables

Create a `.env` file in the folder of form-filling-agent/ with your API keys:

```env
# AgentBay API Key (required)
AGENTBAY_API_KEY=your_actual_api_key_here

# DashScope (Alibaba Cloud) API Key for Qwen LLM (required for LangChain orchestration)
DASHSCOPE_API_KEY=your_qwen_api_key_here

# Optional: specify which Qwen model to use (default: qwen-plus)
DASHSCOPE_MODEL=qwen-plus
```

You can get your Agent-Bay API key from the Agent-Bay platform dashboard:
1. Visit [Agent-Bay Console](https://agentbay.console.aliyun.com/service-management)
2. Sign up or log in to your Alibaba Cloud account
3. Navigate to the Service Management section
4. Create a new API KEY or select an existing one
5. Copy the API Key and paste it as the value of `AGENTBAY_API_KEY` in your `.env` file

For the DashScope API key, you need to register on the Alibaba Cloud DashScope platform:
1. Visit [DashScope Platform](https://bailian.console.aliyun.com/#/home)
2. Sign up or log in to your account
3. Navigate to the API Key management section
4. Copy the API Key and paste it as the value of `DASHSCOPE_API_KEY` in your `.env` file
5. You can specify which model to use by setting the `DASHSCOPE_MODEL` environment variable in your `.env` file.

## Structure

- [src/](./src/): Contains the LangChain-specific implementation
- [README.md](./README.md): This documentation file

## Integration Details

The LangChain integration uses the core functionality from the [common](../common/) directory and wraps it in LangChain-specific components.

This demonstrates how to:
1. Use LangChain agents with Agent-Bay SDK
2. Structure the code to separate core functionality from framework-specific integration
3. Maintain clean separation of concerns between core logic and framework integration
4. Orchestrate form filling tasks using LangChain's agent framework

## LangChain Orchestration

The form filling agent can be orchestrated using LangChain's agent framework. This provides a more flexible way to interact with the form filling functionality:

1. **Tool-based approach**: The agent exposes tools for analyzing forms, setting filling instructions, and executing the filling process
2. **Natural language interface**: Users can interact with the agent using natural language commands
3. **Sequential workflow**: The agent can automatically determine the correct sequence of operations

### Available Tools

1. `analyze_form`: Analyze a form and suggest filling instructions
2. `fill_form_fields`: Prepare to fill form fields with provided instructions
3. `execute_form_filling`: Execute the form filling process

### Running the Example Script

To run the LangChain orchestration example:

```bash
cd YOUR_PREFIX_PATH/cookbook/envs/browser/form-filling-agent/langchain/
python src/form_filling_agent_example.py
```

This example script demonstrates:
1. Creating a LangChain form filling agent
2. Analyzing a form and suggesting filling instructions
3. Filling the form with custom data
4. Executing the form filling process

## Troubleshooting

If you encounter issues:

1. Ensure your API key is correct and properly set in the `.env` file
2. Check that you have network connectivity to Agent-Bay services
3. Verify that all required packages are installed:
   ```bash
   pip list | grep -E "(wuying-agentbay-sdk|langchain)"
   ```
4. Check that you've activated your virtual environment before running the scripts