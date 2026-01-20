# Volume (Beta)

The Volume feature provides **block storage volumes (data disks)** that can be managed independently and mounted into sessions.

Typical use cases include sharing large datasets, persisting build artifacts, and reusing environment state across multiple sessions.

## Limitations and access

- This feature currently supports **Mobile Use** scenarios only.
- Volume is currently in **beta**. Both functionality and APIs may change in future releases.
- Volume currently works only with **custom images**. In the examples below, use placeholders like `image_xxx` to represent a custom `imageId`.
- Volume is currently available via **allowlist**. To request access, email `agentbay_dev@alibabacloud.com`.

## Concepts

- **Volume**: A block storage resource identified by `volumeId`.
- **Mount during session creation**: You can attach a volume to a session by providing `volumeId` (or equivalent) in session creation parameters.
- **Image scoping**: Some SDK operations require `imageId` to match the underlying API requirements.

## Examples

### Python

```python
import os
from agentbay import AgentBay, CreateSessionParams

agent = AgentBay(api_key=os.environ["AGENTBAY_API_KEY"])

v = agent.beta_volume.get(name="demo-volume", image_id="image_xxx", create=True)
if not v.success:
    raise RuntimeError(v.error_message)

params = CreateSessionParams(image_id="image_xxx", beta_volume=v.volume.id)
session = agent.create(params).session

session.command.execute_command("ls -la")
session.delete()
```
