# AgentBay Python SDK API Reference

Complete API reference for the AgentBay Python SDK. Available in both synchronous and asynchronous modes.

> 💡 **New to AgentBay?** Start with our [Quick Start Guide](../../../docs/quickstart/README.md).

## Installation

```bash
pip install wuying-agentbay-sdk
```

**Requirements**: Python 3.10+

---

## Quick Start

### Synchronous API

Perfect for simple scripts and linear workflows:

```python
import os
from agentbay import AgentBay

# Initialize client
client = AgentBay(api_key=os.getenv("AGENTBAY_API_KEY"))

# Create a session
result = client.create()
if result.success:
    session = result.session
    print(f"Session created: {session.session_id}")

    # Execute a command
    cmd_result = session.command.execute_command("echo 'Hello, AgentBay!'")
    print(f"Output: {cmd_result.output}")

    # Clean up
    client.delete(session)
```

### Asynchronous API

For concurrent operations, use `async`/`await`:

```python
import os
import asyncio
from agentbay import AsyncAgentBay

async def main():
    client = AsyncAgentBay(api_key=os.getenv("AGENTBAY_API_KEY"))
    result = await client.create()
    if result.success:
        session = result.session
        cmd_result = await session.command.execute_command("echo 'Hello, AgentBay!'")
        print(f"Output: {cmd_result.output}")
        await client.delete(session)

asyncio.run(main())
```

---

## API Reference

| Feature | Synchronous API | Asynchronous API | Description |
|---------|----------------|------------------|-------------|
| **Main Client** | [AgentBay](sync/agentbay.md) | [AsyncAgentBay](async/async-agentbay.md) | Create and manage cloud environments |
| **Session Management** | [Session](sync/session.md) | [AsyncSession](async/async-session.md) | Manage environment lifecycle |
| **Command Execution** | [Command](sync/command.md) | [AsyncCommand](async/async-command.md) | Execute shell commands |
| **File Operations** | [FileSystem](sync/filesystem.md) | [AsyncFileSystem](async/async-filesystem.md) | Read, write, and manage files |
| **Context Management** | [Context](sync/context.md) | [AsyncContext](async/async-context.md) | Manage execution contexts |
| **Context Manager** | [ContextManager](sync/context-manager.md) | [AsyncContextManager](async/async-context-manager.md) | Advanced context operations |
| **AI Agent** | [Agent](sync/agent.md) | [AsyncAgent](async/async-agent.md) | AI-powered automation |
| **Object Storage** | [OSS](sync/oss.md) | [AsyncOss](async/async-oss.md) | Cloud storage operations |
| **Browser Automation** | [Browser](sync/browser.md) | [AsyncBrowser](async/async-browser.md) | Web browser control |
| **Browser Extensions** | [Extension](sync/extension.md) | [AsyncExtension](async/async-extension.md) | Manage browser extensions |
| **Code Execution** | [Code](sync/code.md) | [AsyncCode](async/async-code.md) | Run code in various languages |
| **Computer Use** | [Computer](sync/computer.md) | [AsyncComputer](async/async-computer.md) | Desktop automation |
| **Mobile Automation** | [Mobile](sync/mobile.md) | [AsyncMobile](async/async-mobile.md) | Mobile device control |

### Common Classes

These classes are shared by both synchronous and asynchronous APIs:

- [Configuration](common/config.md) - SDK configuration and settings
- [Exceptions](common/exceptions.md) - Error types and handling
- [Logging](common/logging.md) - Logging utilities
- [Context Sync](common/context-sync.md) - Context synchronization policies

---

## Sync vs Async

**Use Synchronous API** for:
- Simple scripts and CLI tools
- Linear workflows
- Learning and prototyping

**Use Asynchronous API** for:
- Web applications (FastAPI, Django)
- High concurrency (100+ operations)
- Performance-critical applications

> 📖 See [Sync vs Async Guide](../../../docs/guides/common-features/sync-vs-async.md) for detailed comparison and [Async Patterns](../../../docs/guides/common-features/async-patterns.md) for best practices.

---

## Migration: Sync to Async

```python
# 1. Update imports
from agentbay import AsyncAgentBay  # was: AgentBay

# 2. Add async/await
async def my_function():  # was: def my_function()
    client = AsyncAgentBay()
    session = (await client.create()).session  # was: client.create().session
    result = await session.command.execute_command("ls")  # add await
    await client.delete(session)  # add await

# 3. Run with asyncio
asyncio.run(my_function())
```

> 📖 Full migration guide: [Sync vs Async Guide](../../../docs/guides/common-features/sync-vs-async.md)

---

## Related Resources

- [Quick Start Guide](../../../docs/quickstart/README.md)
- [Feature Guides](../../../docs/guides/README.md)
- [Python Examples](../../examples/README.md)
- [GitHub Repository](https://github.com/aliyun/wuying-agentbay-sdk)

---

**Note**: This documentation is auto-generated from source code. Run `python scripts/generate_api_docs.py` to regenerate.
