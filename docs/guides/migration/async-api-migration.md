# Async API Migration Guide

This guide helps you migrate your code between synchronous and asynchronous AgentBay SDK APIs.

## 📋 Table of Contents

- [Overview](#overview)
- [Sync to Async Migration](#sync-to-async-migration)
- [Async to Sync Migration](#async-to-sync-migration)
- [Common Pitfalls](#common-pitfalls)
- [Code Transformation Patterns](#code-transformation-patterns)
- [Performance Improvements](#performance-improvements)

## 🎯 Overview

The AgentBay Python SDK provides both synchronous (`AgentBay`) and asynchronous (`AsyncAgentBay`) APIs. This guide covers:

- When and why to migrate
- Step-by-step migration process
- Common patterns and transformations
- Performance considerations

### When to Migrate

**Migrate to Async When:**
- Building web applications (FastAPI, Django async)
- Need to handle 100+ concurrent operations
- Performance bottlenecks in I/O operations
- Integrating with async frameworks

**Migrate to Sync When:**
- Simplifying codebase
- Building CLI tools or scripts
- Sequential operations are sufficient
- Team lacks async experience

## 🔄 Sync to Async Migration

### Step 1: Change Imports

**Before (Sync):**
```python
from agentbay import AgentBay
```

**After (Async):**
```python
import asyncio
from agentbay import AsyncAgentBay
```

### Step 2: Update Client Initialization

**Before (Sync):**
```python
agent_bay = AgentBay(api_key="your-api-key")
```

**After (Async):**
```python
agent_bay = AsyncAgentBay(api_key="your-api-key")
```

### Step 3: Add async/await Keywords

**Before (Sync):**
```python
def create_session():
    agent_bay = AgentBay()
    result = agent_bay.create()
    if result.success:
        session = result.session
        cmd_result = session.command.execute_command("echo 'Hello'")
        print(cmd_result.output)
        agent_bay.delete(session)
```

**After (Async):**
```python
async def create_session():
    agent_bay = AsyncAgentBay()
    result = await agent_bay.create()
    if result.success:
        session = result.session
        cmd_result = await session.command.execute_command("echo 'Hello'")
        print(cmd_result.output)
        await agent_bay.delete(session)
```

### Step 4: Update Function Calls

**Before (Sync):**
```python
create_session()
```

**After (Async):**
```python
# If calling from non-async code
asyncio.run(create_session())

# If calling from async code
await create_session()
```

### Complete Example

**Before (Sync):**
```python
from agentbay import AgentBay

def process_data():
    agent_bay = AgentBay()
    session = agent_bay.create().session

    # Upload file
    session.file_system.write_file("/tmp/data.txt", "Hello World")

    # Execute command
    result = session.command.execute_command("cat /tmp/data.txt")
    print(result.output)

    # Cleanup
    agent_bay.delete(session)

if __name__ == "__main__":
    process_data()
```

**After (Async):**
```python
import asyncio
from agentbay import AsyncAgentBay

async def process_data():
    agent_bay = AsyncAgentBay()
    session = (await agent_bay.create()).session

    # Upload file (Note: file operations are currently sync)
    session.file_system.write_file("/tmp/data.txt", "Hello World")

    # Execute command
    result = await session.command.execute_command("cat /tmp/data.txt")
    print(result.output)

    # Cleanup
    await agent_bay.delete(session)

if __name__ == "__main__":
    asyncio.run(process_data())
```

## 🔙 Async to Sync Migration

### Step 1: Change Imports

**Before (Async):**
```python
import asyncio
from agentbay import AsyncAgentBay
```

**After (Sync):**
```python
from agentbay import AgentBay
```

### Step 2: Remove async/await Keywords

**Before (Async):**
```python
async def create_session():
    agent_bay = AsyncAgentBay()
    result = await agent_bay.create()
    if result.success:
        session = result.session
        await agent_bay.delete(session)
```

**After (Sync):**
```python
def create_session():
    agent_bay = AgentBay()
    result = agent_bay.create()
    if result.success:
        session = result.session
        agent_bay.delete(session)
```

### Step 3: Update Function Calls

**Before (Async):**
```python
asyncio.run(create_session())
```

**After (Sync):**
```python
create_session()
```

### Step 4: Replace Concurrent Operations

**Before (Async):**
```python
async def main():
    agent_bay = AsyncAgentBay()

    # Concurrent operations
    results = await asyncio.gather(*[
        agent_bay.create()
        for _ in range(5)
    ])

    sessions = [r.session for r in results if r.success]
```

**After (Sync):**
```python
def main():
    agent_bay = AgentBay()

    # Sequential operations
    sessions = []
    for _ in range(5):
        result = agent_bay.create()
        if result.success:
            sessions.append(result.session)
```

## ⚠️ Common Pitfalls

### 1. Forgetting await

**❌ Wrong:**
```python
async def main():
    agent_bay = AsyncAgentBay()
    result = agent_bay.create()  # Missing await!
```

**✅ Correct:**
```python
async def main():
    agent_bay = AsyncAgentBay()
    result = await agent_bay.create()
```

### 2. Mixing Sync and Async

**❌ Wrong:**
```python
def sync_function():
    agent_bay = AsyncAgentBay()
    result = await agent_bay.create()  # Can't use await in sync function!
```

**✅ Correct:**
```python
async def async_function():
    agent_bay = AsyncAgentBay()
    result = await agent_bay.create()

def sync_wrapper():
    asyncio.run(async_function())
```

### 3. File Operations in Async

**⚠️ Note:** File system operations (`write_file`, `read_file`) are currently synchronous even in `AsyncAgentBay`.

**Current Behavior:**
```python
async def main():
    agent_bay = AsyncAgentBay()
    session = (await agent_bay.create()).session

    # These are synchronous (no await needed)
    session.file_system.write_file("/tmp/file.txt", "content")
    result = session.file_system.read_file("/tmp/file.txt")

    await agent_bay.delete(session)
```

**Workaround for Truly Async File Operations:**
```python
async def main():
    agent_bay = AsyncAgentBay()
    session = (await agent_bay.create()).session

    # Use command-based approach
    import base64
    content = "Hello World"
    encoded = base64.b64encode(content.encode()).decode()
    await session.command.execute_command(
        f"echo '{encoded}' | base64 -d > /tmp/file.txt"
    )

    await agent_bay.delete(session)
```

### 4. Event Loop Issues

**❌ Wrong:**
```python
loop = asyncio.get_event_loop()
loop.run_until_complete(main())
loop.run_until_complete(another_main())  # May fail
```

**✅ Correct:**
```python
asyncio.run(main())
asyncio.run(another_main())

# Or use single event loop
async def combined():
    await main()
    await another_main()

asyncio.run(combined())
```

## 🔧 Code Transformation Patterns

### Pattern 1: Sequential to Concurrent

**Before (Sync - Sequential):**
```python
def process_multiple():
    agent_bay = AgentBay()

    for i in range(5):
        session = agent_bay.create().session
        result = session.command.execute_command(f"echo 'Task {i}'")
        print(result.output)
        agent_bay.delete(session)
```

**After (Async - Concurrent):**
```python
async def process_multiple():
    agent_bay = AsyncAgentBay()

    async def process_task(i):
        session = (await agent_bay.create()).session
        result = await session.command.execute_command(f"echo 'Task {i}'")
        print(result.output)
        await agent_bay.delete(session)

    await asyncio.gather(*[process_task(i) for i in range(5)])
```

### Pattern 2: Error Handling

**Before (Sync):**
```python
def create_session():
    agent_bay = AgentBay()
    try:
        result = agent_bay.create()
        if result.success:
            session = result.session
            # Use session
            agent_bay.delete(session)
    except Exception as e:
        print(f"Error: {e}")
```

**After (Async):**
```python
async def create_session():
    agent_bay = AsyncAgentBay()
    try:
        result = await agent_bay.create()
        if result.success:
            session = result.session
            # Use session
            await agent_bay.delete(session)
    except Exception as e:
        print(f"Error: {e}")
```

### Pattern 3: Context Management

**Before (Sync):**
```python
def use_session():
    agent_bay = AgentBay()
    session = agent_bay.create().session
    try:
        # Use session
        result = session.command.execute_command("echo 'Hello'")
        return result.output
    finally:
        agent_bay.delete(session)
```

**After (Async):**
```python
async def use_session():
    agent_bay = AsyncAgentBay()
    session = (await agent_bay.create()).session
    try:
        # Use session
        result = await session.command.execute_command("echo 'Hello'")
        return result.output
    finally:
        await agent_bay.delete(session)
```

### Pattern 4: Batch Processing

**Before (Sync):**
```python
def batch_process(items):
    agent_bay = AgentBay()
    session = agent_bay.create().session

    results = []
    for item in items:
        result = session.command.execute_command(f"process {item}")
        results.append(result.output)

    agent_bay.delete(session)
    return results
```

**After (Async - Concurrent):**
```python
async def batch_process(items):
    agent_bay = AsyncAgentBay()
    session = (await agent_bay.create()).session

    # Process all items concurrently
    results = await asyncio.gather(*[
        session.command.execute_command(f"process {item}")
        for item in items
    ])

    await agent_bay.delete(session)
    return [r.output for r in results if r.success]
```

## 📊 Performance Improvements

### Benchmark: Sequential vs Concurrent

**Scenario:** Create 10 sessions and execute a command in each

**Sync (Sequential):**
```python
import time
from agentbay import AgentBay

def benchmark_sync():
    agent_bay = AgentBay()
    start = time.time()

    for i in range(10):
        session = agent_bay.create().session
        session.command.execute_command(f"echo 'Task {i}'")
        agent_bay.delete(session)

    elapsed = time.time() - start
    print(f"Sync: {elapsed:.2f} seconds")

# Result: ~30-40 seconds (sequential)
```

**Async (Concurrent):**
```python
import time
import asyncio
from agentbay import AsyncAgentBay

async def benchmark_async():
    agent_bay = AsyncAgentBay()
    start = time.time()

    async def process(i):
        session = (await agent_bay.create()).session
        await session.command.execute_command(f"echo 'Task {i}'")
        await agent_bay.delete(session)

    await asyncio.gather(*[process(i) for i in range(10)])

    elapsed = time.time() - start
    print(f"Async: {elapsed:.2f} seconds")

# Result: ~5-8 seconds (concurrent)
```

**Performance Gain:** 4-6x faster for concurrent operations

### When You'll See Performance Improvements

- **High Concurrency**: 10+ concurrent operations
- **I/O-Bound**: Network requests, file operations
- **Long-Running**: Operations taking > 1 second each

### When You Won't See Improvements

- **Single Operations**: No concurrency benefit
- **CPU-Bound**: Computation-heavy tasks
- **Sequential Logic**: Operations must run in order

## ✅ Migration Checklist

### Pre-Migration

- [ ] Identify performance bottlenecks
- [ ] Determine if async is needed
- [ ] Review team's async experience
- [ ] Plan migration strategy

### During Migration

- [ ] Update imports
- [ ] Add async/await keywords
- [ ] Update function calls
- [ ] Handle file operations
- [ ] Add proper error handling
- [ ] Test thoroughly

### Post-Migration

- [ ] Measure performance improvements
- [ ] Update documentation
- [ ] Train team on async patterns
- [ ] Monitor for issues

## 📚 Related Documentation

- [Sync vs Async Guide](../common-features/sync-vs-async.md) - Comprehensive comparison
- [Async Patterns](../common-features/async-patterns.md) - Common async patterns
- [Session Management](../common-features/basics/session-management.md) - Session lifecycle

## 🆘 Getting Help

- [GitHub Issues](https://github.com/aliyun/wuying-agentbay-sdk/issues)
- [Documentation Home](../../README.md)

Happy migrating! 🚀

