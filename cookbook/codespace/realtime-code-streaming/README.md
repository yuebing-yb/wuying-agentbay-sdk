# Real-time Code Streaming (Beta)

Execute code in the cloud and receive output in real-time via WebSocket callbacks — see results as they're produced, not after execution completes.

## What You'll Build

Three demos showcasing the streaming code execution API:

1. **Real-time Progress Monitoring** — Watch a multi-step pipeline execute live
2. **Streaming Data Analysis** — See statistical results build incrementally
3. **Streaming vs Non-Streaming Comparison** — Measure the first-output latency improvement

**Key metric**: First output arrives in 0.3s with streaming, vs 2.7s with non-streaming — a **2.7s improvement** in perceived responsiveness.

## Prerequisites

- Python 3.8+
- An AgentBay API key with access to a WebSocket-enabled image

```bash
pip install wuying-agentbay-sdk
export AGENTBAY_API_KEY=your_api_key_here
```

## Quick Start

```bash
cd cookbook/codespace/realtime-code-streaming
python python/main.py
```

## How It Works

### The Streaming API

Pass `stream_beta=True` and callback functions to `run_code()`:

```python
result = await session.code.run_code(
    code="print('hello')",
    language="python",
    timeout_s=60,
    stream_beta=True,
    on_stdout=lambda chunk: print(f"[STDOUT] {chunk}"),
    on_stderr=lambda chunk: print(f"[STDERR] {chunk}"),
    on_error=lambda err: print(f"[ERROR] {err}"),
)
```

- `on_stdout(chunk)`: Called each time new stdout output is produced
- `on_stderr(chunk)`: Called each time new stderr output is produced
- `on_error(err)`: Called when a WebSocket error occurs
- The function still returns an `EnhancedCodeExecutionResult` when execution completes

### Demo 1: Progress Monitoring

Track a multi-step pipeline with real-time status updates:

```
  [0.3s] [1/5] Connecting to database...
  [0.8s]   ✓ Done (0.5s)
  [0.8s] [2/5] Loading dataset (1M rows)...
  [1.6s]   ✓ Done (0.8s)
  [1.6s] [3/5] Running analysis...
  [2.6s]   ✓ Done (1.0s)
  ...
  Time to first chunk: 0.30s
```

### Demo 3: Streaming vs Non-Streaming

The same code, two modes — streaming delivers the first output immediately:

```
  [Non-Streaming] Output delivered at 2.7s (all at once)
  [Streaming]     First chunk at 0.0s (total 2.5s)
  → First-output latency improvement: 2.7s earlier
```

## When to Use Streaming

| Scenario | Non-Streaming | Streaming |
|----------|--------------|-----------|
| Quick computation | ✅ Simpler | Unnecessary overhead |
| Long-running tasks | ❌ Wait for completion | ✅ Real-time progress |
| Interactive UI | ❌ Blocking UX | ✅ Responsive updates |
| Log monitoring | ❌ No live updates | ✅ Live log output |
| Data pipelines | ❌ Black box | ✅ Observable steps |

## Limitations

- **Beta feature**: The streaming API is in beta and may change
- **Python only**: Streaming currently works with `language="python"` (shell scripts are not supported)
- **Image requirement**: Requires a session with `ws_url` — not all images support this
- **Stderr**: Currently, stderr output may be mixed into the stdout channel

## Next Steps

- Build a web UI that displays streaming code output in real-time
- Combine with AI code generation for an interactive coding assistant
- Use streaming for long-running data processing pipelines with progress bars
