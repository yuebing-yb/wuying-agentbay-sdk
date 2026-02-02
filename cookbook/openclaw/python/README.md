## What this cookbook does

This cookbook shows how to:

- Create a prebuilt OpenClaw session image on AgentBay
- Configure OpenClaw provider/channel credentials via remote shell commands
- Open OpenClaw console inside the cloud desktop
- Print the Cloud Desktop URL and pause so you can interact manually
- Continue only after a hotkey is detected, then release the session

## Prerequisites

Set environment variables before running:

- `AGENTBAY_API_KEY` (required)
- `DASHSCOPE_API_KEY` (optional, for model provider)
- `DINGTALK_CLIENT_ID` + `DINGTALK_CLIENT_SECRET` (optional, must be both set)
- `FEISHU_APP_ID` + `FEISHU_APP_SECRET` (optional, must be both set)

## Run

Use the existing virtual environment `./agentbay_example_env` at repo root, then run:

```bash
source ./agentbay_example_env/bin/activate
python cookbook/openclaw/python/main.py
```

## Notes

- **Image ID**: the script uses `moltbot-linux-ubuntu-2204`. Replace it if you have another OpenClaw image.
- **Hotkey**: after printing the Cloud Desktop URL, the script waits for **Ctrl+Q** in your terminal to continue and clean up the session.
- **Command name**: if the image still uses the old `moltbot` or `clawdbot` command, the script auto-detects and falls back to it.
- **Try it without credentials**: even if you don't set provider/channel env vars, you can still open the Cloud Desktop URL and visit `http://127.0.0.1:30120` in the cloud desktop browser for a quick hands-on experience.
