# Volume (Beta)

The Volume feature provides **block storage volumes (data disks)** that can be managed independently and mounted into sessions.

Typical use cases include sharing large datasets, persisting build artifacts, and reusing environment state across multiple sessions.

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

v = agent.beta_volume.get(name="demo-volume", image_id="linux_latest", create=True)
if not v.success:
    raise RuntimeError(v.error_message)

params = CreateSessionParams(image_id="linux_latest", volume=v.volume.id)
session = agent.create(params).session

session.command.execute_command("ls -la")
session.delete()
```

## Best practices

1. Use descriptive volume names and keep a mapping between name and `volumeId`.
2. Prefer mounting volumes at session creation time for predictable behavior.
3. Always validate `success` and handle `errorMessage` for volume operations.
4. Clean up sessions after use.

