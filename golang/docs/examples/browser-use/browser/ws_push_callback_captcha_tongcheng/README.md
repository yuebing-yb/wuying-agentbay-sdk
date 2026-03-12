# WS push callback (captcha) example

This example demonstrates how to receive backend push notifications via the session WebSocket.

It will:

- Create a browser session
- Connect to the session WS client
- Register a callback for target `wuying_cdp_mcp_server`
- Trigger a captcha flow on Tongcheng and wait for a backend push message

## Prerequisites

- Set environment variable `AGENTBAY_API_KEY`

## Run

```bash
cd golang
go run ./docs/examples/browser-use/browser/ws_push_callback_captcha_tongcheng
```

