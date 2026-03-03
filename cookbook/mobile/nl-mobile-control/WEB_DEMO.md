## Web UI (FastAPI, Async)

This example creates an AgentBay mobile session and exposes a small web UI:
- Create session and open the cloud phone page (resource_url)
- Input a natural-language instruction
- The agent executes the instruction using mobile tools
- Poll and view execution logs + final answer in the web UI

### Prerequisites

- `AGENTBAY_API_KEY` is set
- `DASHSCOPE_API_KEY` is set (DashScope OpenAI-compatible)

Optional:

- `MOBILE_IMAGE_ID` (defaults to the Xiaohongshu preset image for demo)

### Run

From repo root:

```bash
python -m venv .venv
source .venv/bin/activate
pip install agentbay fastapi uvicorn
python cookbook/mobile/nl-mobile-control/server.py
```

Then open:

- Web UI: `http://127.0.0.1:8000`


