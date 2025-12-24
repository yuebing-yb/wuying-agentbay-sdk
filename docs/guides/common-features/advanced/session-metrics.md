# Session Metrics (get_metrics)

`linux_latest` (and future images) provides an MCP tool named `get_metrics`. The SDK exposes it as a **Session API** that returns structured runtime metrics.

## What you can get

The current `get_metrics` response contains:

- `cpu_count`: CPU core count
- `cpu_used_pct`: CPU usage percentage
- `mem_total`, `mem_used`: memory total/used (bytes)
- `disk_total`, `disk_used`: disk total/used (bytes)
- `rx_rate_KBps`, `tx_rate_KBps`: network RX/TX rate (KB/s)
- `rx_used_KB`, `tx_used_KB`: network RX/TX total used (KB)
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

## TypeScript

```typescript
import { AgentBay } from "wuying-agentbay-sdk";

const agentBay = new AgentBay({ apiKey: process.env.AGENTBAY_API_KEY! });
const create = await agentBay.create({ imageId: "linux_latest" });
if (create.success && create.session) {
  const metrics = await create.session.getMetrics();
  console.log(metrics.data);
  await create.session.delete();
}
```

## Go

```go
package main

import (
	"fmt"
	"os"

	"github.com/aliyun/wuying-agentbay-sdk/golang/pkg/agentbay"
)

func main() {
	client, _ := agentbay.NewAgentBay(os.Getenv("AGENTBAY_API_KEY"), nil)
	create, _ := client.Create(agentbay.NewCreateSessionParams().WithImageId("linux_latest"))
	defer create.Session.Delete()

	metrics, _ := create.Session.GetMetrics()
	fmt.Println(metrics.Metrics.CpuUsedPct)
}
```


