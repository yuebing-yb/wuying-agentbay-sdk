## Natural Language Mobile Control (Cookbook)

This cookbook example provides two ways to control a cloud phone with natural language:

- **CLI / LangChain agent (async)**: generic mobile tools + optional app presets
- **Web UI (FastAPI)**: create a session, preview the cloud phone (iframe), type instructions, and watch results live

> **Looking for a simpler approach?** Check out [nl-mobile-agent](../nl-mobile-agent/) which uses AgentBay's built-in mobile agent — no LangChain or DASHSCOPE_API_KEY required.

### Prerequisites

- `AGENTBAY_API_KEY`
- `DASHSCOPE_API_KEY` (DashScope OpenAI-compatible)

Optional:

- `MOBILE_IMAGE_ID` (defaults to a demo image id)
- `DASHSCOPE_MODEL` (default: `qwen3-max`)

### Install Dependencies

```bash
pip install agentbay langchain-openai langgraph python-dotenv requests anyio
```

For the Web UI, also install:

```bash
pip install fastapi uvicorn
```

### Run (Web UI)

From repo root:

```bash
export AGENTBAY_API_KEY=your_api_key
export DASHSCOPE_API_KEY=your_dashscope_key
python cookbook/mobile/nl-mobile-control/server.py
```

Open: `http://127.0.0.1:8000`

### Run (CLI)

From repo root:

```bash
export AGENTBAY_API_KEY=your_api_key
export DASHSCOPE_API_KEY=your_dashscope_key
cd cookbook/mobile/nl-mobile-control/langchain
python src/nl_mobile_agent_example.py
```


