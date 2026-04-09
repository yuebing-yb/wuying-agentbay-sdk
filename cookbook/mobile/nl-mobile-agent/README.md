## NL Mobile Agent (Cookbook)

Control a cloud phone with natural language using AgentBay's **built-in mobile agent** (`session.agent.mobile`).

Unlike the [nl-mobile-control](../nl-mobile-control/) cookbook which builds a custom LangChain agent with 16 self-defined tools, this cookbook uses the **platform-hosted agent** — no external LLM keys or LangChain dependencies required. Just pass a natural language task and the platform handles everything.

### How It Works

```
User (natural language task)
   └──> session.agent.mobile.execute_task_and_wait(task, ...)
           └──> Platform-hosted mobile agent (wuying_mobile_agent)
                   └──> Executes actions on the cloud phone
                           └──> Returns result + optional streaming events
```

### Files

| File | Description |
|---|---|
| `examples/basic_task.py` | Simplest example (~60 lines): execute a task and print the result |
| `examples/streaming_task.py` | Streaming example: real-time callbacks for reasoning, tool calls, and results |
| `server.py` | FastAPI web backend with SSE streaming |
| `web/index.html` | Dark-themed web UI with real-time agent event stream |

### Prerequisites

- Python 3.9+
- `AGENTBAY_API_KEY` environment variable

```bash
export AGENTBAY_API_KEY=your_api_key_here
```

Optional environment variables:

| Variable | Default | Description |
|---|---|---|
| `MOBILE_IMAGE_ID` | `mobile_latest` | Cloud phone image to use |
| `MOBILE_TASK` | `Open the Settings app` | Default task for CLI examples |
| `MOBILE_MAX_STEPS` | `50` | Max agent steps per task |
| `MOBILE_TIMEOUT` | `180` | Task timeout in seconds |

### Run (CLI — Basic)

```bash
pip install agentbay
python cookbook/mobile/nl-mobile-agent/examples/basic_task.py
```

Custom task:

```bash
MOBILE_TASK="Open Chrome and search for weather" python cookbook/mobile/nl-mobile-agent/examples/basic_task.py
```

Sample output:

```
Session created: s-04poml0x0l0agk8e0
Executing task: Open the Settings app

Task completed:
  Success: True
  Status:  completed
  Result:  {"status":"success"}

Session cleaned up
```

### Run (CLI — Streaming)

```bash
python cookbook/mobile/nl-mobile-agent/examples/streaming_task.py
```

Sample output (real-time events appear as the agent works):

```
[Content] I'll open the Settings app for you using the automator tool.
[ToolCall] automator({"task": "Open the Settings app"})
[Reasoning] 用户希望打开设置应用。设置图标位于第四行的第二个位置。
[ToolCall] click({"action": "click", "coordinate": [378, 886]})
[ToolResult] click -> {'isError': False, ...}
[Reasoning] 设置应用已经成功打开，显示了网络、设备、应用等选项。
[Content] The Settings app has been successfully opened.

Task completed:
  Success: True
  Status:  finished
  Result:  The Settings app has been successfully opened.
```

### Run (Web UI)

```bash
pip install agentbay fastapi uvicorn
python cookbook/mobile/nl-mobile-agent/server.py
```

Open `http://127.0.0.1:8000` in your browser. The web UI provides:

1. **Create Session** — creates a cloud phone session
2. **Cloud Phone Preview** — iframe showing the live phone screen (or use "Open in new tab")
3. **Task Input** — type a natural language instruction and click "Run Agent"
4. **Agent Stream** — real-time log of agent reasoning, tool calls, and results via SSE

### Comparison with nl-mobile-control

| | nl-mobile-control | nl-mobile-agent (this) |
|---|---|---|
| Agent | Local LangGraph ReAct | Platform-hosted |
| LLM key | DASHSCOPE_API_KEY required | Not needed |
| Dependencies | langchain, langgraph, langchain-openai | agentbay only |
| Tool chain | 16 custom @tool functions | Platform built-in |
| Code complexity | ~1000+ lines core | ~60 lines per example |
| Streaming | Polling ToolMessage | WebSocket + SSE |
| Customizability | Full control over tools & prompts | Task-level control |
