# AgentBay Python SDK API Reference

The AgentBay Python SDK provides a powerful interface for creating and managing cloud-based development environments programmatically. This reference documents all available APIs in both synchronous and asynchronous modes.

## Documentation Structure

This API reference is organized into three main sections:

- **[Synchronous API](#synchronous-api)** - Blocking operations for simple scripts and linear workflows
- **[Asynchronous API](#asynchronous-api)** - Non-blocking operations for high-performance concurrent tasks
- **[Common Classes](#common-classes)** - Shared types and utilities used by both APIs

> 💡 **New to AgentBay?** Start with our [Quick Start Guide](../../../docs/quickstart/README.md) or jump to [Quick Start Examples](#quick-start) below.

---

## Installation

Install the AgentBay Python SDK using pip:

```bash
pip install wuying-agentbay-sdk
```

Or using poetry:

```bash
poetry add wuying-agentbay-sdk
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

**Key Points**:
- Simple, straightforward code
- Operations execute sequentially
- Easy to understand and debug

### Asynchronous API

Ideal for high-performance applications with concurrent operations:

```python
import os
import asyncio
from agentbay import AsyncAgentBay

async def main():
    # Initialize client
    client = AsyncAgentBay(api_key=os.getenv("AGENTBAY_API_KEY"))

    # Create a session
    result = await client.create()
    if result.success:
        session = result.session
        print(f"Session created: {session.session_id}")

        # Execute a command
        cmd_result = await session.command.execute_command("echo 'Hello, AgentBay!'")
        print(f"Output: {cmd_result.output}")

        # Clean up
        await client.delete(session)

# Run the async function
asyncio.run(main())
```

**Key Points**:
- Use `async`/`await` keywords
- Enables concurrent operations
- 4-6x faster for parallel tasks

---

## API Overview

AgentBay provides identical functionality in both synchronous and asynchronous modes. Choose the mode that best fits your use case.

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

## When to Use Sync vs Async

### Use Synchronous API When:

✅ **Simple Scripts** - Writing one-off automation scripts

✅ **Linear Workflows** - Operations happen one after another

✅ **Learning** - Getting started with AgentBay

✅ **CLI Tools** - Building command-line applications

✅ **Low Concurrency** - Fewer than 10 concurrent operations

✅ **Code Simplicity** - Prioritizing easy-to-understand code

**Example Use Cases**:
- Data processing scripts
- Batch file operations
- System administration tasks
- Prototyping and testing

### Use Asynchronous API When:

⚡ **High Concurrency** - Need to handle 100+ operations simultaneously

⚡ **Web Applications** - Building with FastAPI, Django, or aiohttp

⚡ **Performance Critical** - Maximizing throughput is essential

⚡ **Real-Time Systems** - Need responsive, non-blocking operations

⚡ **Async Integration** - Working with other async libraries

⚡ **Resource Efficiency** - Minimizing memory and CPU usage

**Example Use Cases**:
- REST API backends
- Real-time monitoring systems
- Batch processing pipelines
- Multi-tenant applications

> 📖 **Detailed Comparison**: See our [Sync vs Async Guide](../../../docs/guides/common-features/sync-vs-async.md) for in-depth comparison and migration instructions.

---

## Performance Comparison

### Concurrent Operations Benchmark

**Scenario**: Creating and managing 10 sessions

| Mode | Execution Time | Performance |
|------|---------------|-------------|
| **Synchronous** (sequential) | ~15.2 seconds | Baseline |
| **Asynchronous** (concurrent) | ~2.8 seconds | **5.4x faster** ⚡ |

### Resource Usage

| Metric | Synchronous | Asynchronous |
|--------|-------------|--------------|
| **Memory per operation** | Higher (thread overhead) | Lower (shared event loop) |
| **CPU usage** | Higher (context switching) | Lower (single thread) |
| **Max concurrent operations** | ~1,000 | ~10,000+ |
| **Network connections** | One per thread | Reused efficiently |

### Real-World Example

```python
# Synchronous: Process 100 files sequentially
# Time: ~100 seconds (1 second per file)
for file in files:
    session = client.create().session
    result = session.file_system.read_file(file)
    process(result)
    client.delete(session)

# Asynchronous: Process 100 files concurrently
# Time: ~5-10 seconds (parallel processing)
async def process_file(file):
    session = (await client.create()).session
    result = await session.file_system.read_file(file)
    process(result)
    await client.delete(session)

await asyncio.gather(*[process_file(f) for f in files])
```

> ⚠️ **Note**: Performance gains are significant only for concurrent operations. For sequential tasks, both APIs perform similarly.

---

## Migration Guide

### From Synchronous to Asynchronous

Converting your code from sync to async is straightforward. Follow these steps:

#### Step 1: Update Imports

```python
# Before (Sync)
from agentbay import AgentBay, Session, Command

# After (Async)
from agentbay import AsyncAgentBay, AsyncSession, AsyncCommand
```

#### Step 2: Add async/await Keywords

```python
# Before (Sync)
def my_function():
    client = AgentBay()
    session = client.create().session
    result = session.command.execute_command("ls")
    client.delete(session)
    return result

# After (Async)
async def my_function():
    client = AsyncAgentBay()
    session = (await client.create()).session
    result = await session.command.execute_command("ls")
    await client.delete(session)
    return result
```

#### Step 3: Update Function Calls

```python
# Before (Sync)
result = my_function()

# After (Async) - from async context
result = await my_function()

# After (Async) - from sync context
import asyncio
result = asyncio.run(my_function())
```

#### Step 4: Leverage Concurrency

```python
# Async enables concurrent operations
import asyncio

async def process_multiple():
    client = AsyncAgentBay()

    # Create multiple sessions concurrently
    sessions = await asyncio.gather(*[
        client.create()
        for _ in range(5)
    ])

    # Process concurrently
    results = await asyncio.gather(*[
        s.session.command.execute_command("hostname")
        for s in sessions if s.success
    ])

    # Clean up concurrently
    await asyncio.gather(*[
        client.delete(s.session)
        for s in sessions if s.success
    ])

    return results
```

### From Asynchronous to Synchronous

Simply reverse the process:

1. Change `AsyncAgentBay` → `AgentBay` (and all `Async*` classes)
2. Remove all `await` keywords
3. Remove `async` from function definitions
4. Remove `asyncio.run()` and `asyncio.gather()` calls

> 📖 **Full Migration Guide**: See [Sync vs Async Guide](../../../docs/guides/common-features/sync-vs-async.md) for detailed migration instructions and best practices.

---

## Complete API Reference

### Synchronous API

All synchronous API classes (blocking operations):

- [AgentBay](sync/agentbay.md) - Main client for managing cloud environments
- [Session](sync/session.md) - Session lifecycle management
- [Command](sync/command.md) - Shell command execution
- [Context](sync/context.md) - Execution context management
- [ContextManager](sync/context-manager.md) - Advanced context operations
- [FileSystem](sync/filesystem.md) - File and directory operations
- [Agent](sync/agent.md) - AI-powered automation
- [OSS](sync/oss.md) - Object storage service
- [Browser](sync/browser.md) - Web browser automation
- [Extension](sync/extension.md) - Browser extension management
- [Code](sync/code.md) - Multi-language code execution
- [Computer](sync/computer.md) - Desktop automation
- [Mobile](sync/mobile.md) - Mobile device automation

### Asynchronous API

All asynchronous API classes (non-blocking operations):

- [AsyncAgentBay](async/async-agentbay.md) - Main async client
- [AsyncSession](async/async-session.md) - Async session management
- [AsyncCommand](async/async-command.md) - Async command execution
- [AsyncContext](async/async-context.md) - Async context management
- [AsyncContextManager](async/async-context-manager.md) - Async context operations
- [AsyncFileSystem](async/async-filesystem.md) - Async file operations
- [AsyncAgent](async/async-agent.md) - Async AI agent
- [AsyncOss](async/async-oss.md) - Async object storage
- [AsyncBrowser](async/async-browser.md) - Async browser automation
- [AsyncExtension](async/async-extension.md) - Async extension management
- [AsyncCode](async/async-code.md) - Async code execution
- [AsyncComputer](async/async-computer.md) - Async desktop automation
- [AsyncMobile](async/async-mobile.md) - Async mobile automation

### Common Classes

Shared classes used by both sync and async APIs:

- [Configuration](common/config.md) - SDK configuration (`Config`)
- [Exceptions](common/exceptions.md) - Error types (`AgentBayError`, `APIError`, `AuthenticationError`)
- [Logging](common/logging.md) - Logging utilities (`AgentBayLogger`, `get_logger`)
- [Context Sync](common/context-sync.md) - Context synchronization policies and strategies

---

## Related Resources

### Getting Started

- [Quick Start Guide](../../../docs/quickstart/README.md) - Get up and running in 5 minutes
- [First Session Tutorial](../../../docs/quickstart/first-session.md) - Create your first AgentBay session
- [Configuration Guide](../../../docs/quickstart/configuration.md) - Configure the SDK

### Feature Guides

- [Sync vs Async Guide](../../../docs/guides/common-features/sync-vs-async.md) - Detailed comparison and migration
- [Async Patterns](../../../docs/guides/common-features/async-patterns.md) - Best practices for async programming
- [Session Management](../../../docs/guides/common-features/basics/session-management.md) - Managing session lifecycle
- [Command Execution](../../../docs/guides/common-features/basics/command-execution.md) - Running shell commands
- [File Operations](../../../docs/guides/common-features/basics/file-operations.md) - Working with files
- [Data Persistence](../../../docs/guides/common-features/basics/data-persistence.md) - Context synchronization and data persistence

### Code Examples

- [Python Examples](../../examples/README.md) - Complete working examples

### Additional Resources

- [GitHub Repository](https://github.com/aliyun/wuying-agentbay-sdk)
- [Issue Tracker](https://github.com/aliyun/wuying-agentbay-sdk/issues)

---

**Note**: This documentation is auto-generated from source code. Run `python scripts/generate_api_docs.py` to regenerate.
