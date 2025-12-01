# Migration Guide

Migrate from AgentBay Python SDK v0.12.x to v0.13.0+ with sync/async separated architecture.

## Overview

**Version Change**: v0.12.0 → v0.13.0+

In v0.12.x and earlier, the SDK used async APIs extensively. Starting from v0.13.0, the SDK provides separate sync (`AgentBay`) and async (`AsyncAgentBay`) APIs.

**Migration scope**: 69 async methods across 26 files need updating.

## Quick Migration Steps

### 1. Choose Your API

**For scripts/CLI**: Use sync API
```python
# Before (v0.12.x)
from agentbay import AgentBay
async with AgentBay() as agent_bay:
    # operations

# After (v0.13.0+)
from agentbay import AgentBay
agent_bay = AgentBay()
# operations
```

**For web servers**: Use async API
```python
# Before (v0.12.x)
from agentbay import AgentBay
async with AgentBay() as agent_bay:
    # operations

# After (v0.13.0+)
from agentbay import AsyncAgentBay
agent_bay = AsyncAgentBay()
# operations (still async)
```

### 2. Method Name Changes

Remove `_async` suffix from all method names:

```python
# Before (v0.12.x)
await session.browser.agent.navigate_async(url)
await session.command.execute_command("ls")

# After (v0.13.0+ sync)
session.browser.agent.navigate(url)
session.command.execute_command("ls")

# After (v0.13.0+ async)
await session.browser.agent.navigate(url)
await session.command.execute_command("ls")
```

## Complete Method Mapping

### Core Session Methods
```python
# v0.12.x → v0.13.0+
pause_async() → pause()
resume_async() → resume()
get_link_async() → get_link()
```

### Browser Methods
```python
# v0.12.x → v0.13.0+
initialize_async() → initialize()
navigate_async() → navigate()
screenshot_async() → screenshot()
act_async() → act()
observe_async() → observe()
extract_async() → extract()
close_async() → close()
```



### File System Methods
```python
# v0.12.x → v0.13.0+
upload_async() → upload()
download_async() → download()
```



## Error Handling Changes

### Sync API
```python
# Current sync approach
result = session.command.execute_command("ls")
if result.success:
    print(result.output)
else:
    print(f"Error: {result.error_message}")
```

### Async API
```python
# Current async approach
result = await session.command.execute_command("ls")
if result.success:
    print(result.output)
else:
    print(f"Error: {result.error_message}")
```

## Context Manager Changes

### v0.12.x Version
```python
# Context manager approach (deprecated in v0.13.0+)
async with AgentBay() as agent_bay:
    session = await agent_bay.create(params)
```

### v0.13.0+ Version
```python
# Sync approach
agent_bay = AgentBay()
result = agent_bay.create(params)
session = result.session
# ... use session
agent_bay.delete(session)

# Async approach
agent_bay = AsyncAgentBay()
result = await agent_bay.create(params)
session = result.session
# ... use session
await agent_bay.delete(session)
```

## Common Migration Patterns

### Pattern 1: Simple Script Migration
```python
# Before (v0.12.x)
import asyncio
from agentbay import AgentBay

async def main():
    async with AgentBay() as agent_bay:
        session = await agent_bay.create(params)
        result = await session.command.execute_command("ls")
        print(result.output)

asyncio.run(main())

# After (v0.13.0+ sync)
from agentbay import AgentBay

agent_bay = AgentBay()
result = agent_bay.create(params)
session = result.session
result = session.command.execute_command("ls")
print(result.output)
agent_bay.delete(session)
```

### Pattern 2: Web Server Migration
```python
# Before (v0.12.x)
async def handle_request():
    async with AgentBay() as agent_bay:
        session = await agent_bay.create(params)
        result = await session.command.execute_command(cmd)
        return result.output

# After (v0.13.0+ async)
async def handle_request():
    agent_bay = AsyncAgentBay()
    result = await agent_bay.create(params)
    session = result.session
    result = await session.command.execute_command(cmd)
    await agent_bay.delete(session)
    return result.output
```

## Validation Steps

After migration:

1. **Remove all `_async` suffixes** from method names
2. **Update imports** (`AgentBay` for sync, `AsyncAgentBay` for async)
3. **Test basic operations** (create session, run command, delete session)
4. **Verify error handling** uses `result.success` pattern
5. **Check context management** follows new patterns

## Notes

- **File operations** remain synchronous in both APIs
- **API compatibility** maintained except for async/sync differences
- **New features** available in current version not in backup
- **Performance** may differ due to architectural changes

For API comparison, see [Sync vs Async Guide](sync-vs-async.md).