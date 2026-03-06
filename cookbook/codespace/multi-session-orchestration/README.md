# Multi-Session Orchestration

Run multiple independent tasks concurrently using separate cloud sessions to achieve significant speedup over sequential execution.

## What You'll Build

A Python script that demonstrates the performance advantage of concurrent session management — running 3 computational tasks in parallel instead of one-by-one.

**Measured results:**

| Mode | Time | Tasks |
|------|------|-------|
| Sequential | 7.9s | 3/3 succeeded |
| **Concurrent** | **2.6s** | **3/3 succeeded** |
| **Speedup** | **3.0x** | Time saved: 5.3s |

## Prerequisites

- Python 3.8+
- An AgentBay API key ([Get one here](https://agentbay.wuying.com))

```bash
pip install wuying-agentbay-sdk
export AGENTBAY_API_KEY=your_api_key_here
```

## Quick Start

```bash
cd cookbook/codespace/multi-session-orchestration
python python/main.py
```

## How It Works

### The Core Pattern

Each task gets its own isolated cloud session. Tasks run in parallel using `asyncio.gather`.

```python
async def run_task(agent_bay, task_name, code):
    """One session per task: create → run → cleanup."""
    result = await agent_bay.create(CreateSessionParams(image_id="code_latest"))
    session = result.session
    try:
        r = await session.code.run_code(code, "python", 30)
        return {"task": task_name, "output": "\n".join(r.logs.stdout)}
    finally:
        await session.delete()
```

### Sequential vs Concurrent

```python
# Sequential: tasks run one after another
for name, code in tasks:
    result = await run_task(agent_bay, name, code)

# Concurrent: all tasks run at the same time
results = await asyncio.gather(
    *[run_task(agent_bay, name, code) for name, code in tasks]
)
```

### Sample Output

```
Sequential Execution
  'Prime Numbers': Create: 1.1s | Exec: 0.3s | Total: 1.4s
  'System Info':   Create: 0.8s | Exec: 0.2s | Total: 1.0s
  'Statistics':    Create: 0.8s | Exec: 0.2s | Total: 1.0s

Concurrent Execution
  'Prime Numbers': Create: 0.8s | Exec: 0.2s | Total: 1.0s
  'System Info':   Create: 0.8s | Exec: 0.2s | Total: 1.0s
  'Statistics':    Create: 0.8s | Exec: 0.2s | Total: 1.1s

Results: Sequential 7.9s → Concurrent 2.6s (3.0x speedup)
```

## When to Use This Pattern

- **Data processing**: Run analysis on different datasets simultaneously
- **Testing**: Execute test suites against multiple environments in parallel
- **Web scraping**: Scrape multiple sites concurrently (combine with Browser cookbook)
- **Batch jobs**: Process a queue of independent tasks efficiently

## Key Considerations

- **Concurrency limits**: Cloud environments may have limits on simultaneous sessions. Use `asyncio.Semaphore` to throttle:

```python
semaphore = asyncio.Semaphore(5)  # max 5 concurrent sessions

async def run_task_throttled(agent_bay, name, code):
    async with semaphore:
        return await run_task(agent_bay, name, code)
```

- **Error handling**: Use `return_exceptions=True` in `asyncio.gather` to prevent one failure from cancelling all tasks:

```python
results = await asyncio.gather(*tasks, return_exceptions=True)
for r in results:
    if isinstance(r, Exception):
        print(f"Task failed: {r}")
```

- **Session cleanup**: Always use `try/finally` to ensure sessions are deleted, even on errors.

## Next Steps

- Combine with Browser module for concurrent web scraping
- Add result aggregation across multiple sessions
- Implement retry logic for transient failures
- Use session labels to track and manage concurrent sessions
