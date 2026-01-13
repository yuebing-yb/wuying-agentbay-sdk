# Session Metrics (get_metrics)

`linux_latest` (and future images) provides an MCP tool named `get_metrics`. The SDK exposes it as a **Session API** that returns structured runtime metrics.

## What you can get

The current `get_metrics` response contains:

- `cpu_count`: CPU core count
- `cpu_used_pct`: CPU usage percentage
- `mem_total`, `mem_used`: memory total/used (bytes)
- `disk_total`, `disk_used`: disk total/used (bytes)
- `rx_rate_kbyte_per_s`, `tx_rate_kbyte_per_s`: network RX/TX rate (kbyte/s)
- `rx_used_kbyte`, `tx_used_kbyte`: network RX/TX total used (kbyte)
- `timestamp`: RFC3339-like timestamp string (with timezone offset)

## Python

```python
import asyncio
from agentbay import AsyncAgentBay, CreateSessionParams


async def main() -> None:
    agent_bay = AsyncAgentBay()
    create = await agent_bay.create(CreateSessionParams(image_id="linux_latest"))
    session = create.session
    try:
        result = await session.get_metrics()
        print(result.metrics.cpu_used_pct, result.metrics.mem_used)
    finally:
        await session.delete()


if __name__ == "__main__":
    asyncio.run(main())
```
