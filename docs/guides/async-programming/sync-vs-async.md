# Synchronous vs Asynchronous API Guide

This guide helps you choose between the synchronous and asynchronous APIs in the AgentBay Python SDK and shows you how to use each effectively.

## Table of Contents

- [Quick Comparison](#quick-comparison)
- [When to Use Sync API](#when-to-use-sync-api)
- [When to Use Async API](#when-to-use-async-api)
- [Performance Considerations](#performance-considerations)
- [Migration Guide](#migration-guide)
- [Best Practices](#best-practices)
- [Common Patterns](#common-patterns)
- [Troubleshooting](#troubleshooting)

## Quick Comparison

| Aspect | Sync API (`AgentBay`) | Async API (`AsyncAgentBay`) |
|--------|----------------------|----------------------------|
| **Import** | `from agentbay import AgentBay` | `from agentbay import AsyncAgentBay` |
| **Execution Model** | Blocking, sequential | Non-blocking, concurrent |
| **Best For** | Scripts, CLI tools, simple automation | Web servers, high-concurrency apps |
| **Concurrency** | One operation at a time | Multiple operations simultaneously |
| **Learning Curve** | Simple, straightforward | Requires async/await knowledge |
| **Thread Safety** | One thread per operation | Single thread, event loop |
| **Error Handling** | Try/except | Try/except with async context |
| **Resource Usage** | Higher (one thread per operation) | Lower (single thread, event loop) |

## When to Use Sync API

### Ideal Use Cases

#### 1. Simple Scripts and Automation

Use sync API when writing straightforward automation scripts that process tasks sequentially.

**Example: Batch File Processing**

```python
from agentbay import AgentBay, CreateSessionParams

def process_files(file_list):
    agent_bay = AgentBay()
    session = agent_bay.create(CreateSessionParams(image_id="code_latest")).session
    
    results = []
    for file_path in file_list:
        # Read file
        content = session.file_system.read_file(file_path)
        
        # Process
        processed = content.content.upper()
        
        # Write back
        session.file_system.write_file(f"{file_path}.processed", processed)
        results.append(f"Processed: {file_path}")
    
    agent_bay.delete(session)
    return results

# Usage
files = ["/tmp/file1.txt", "/tmp/file2.txt", "/tmp/file3.txt"]
results = process_files(files)
for result in results:
    print(result)
```

#### 2. Command-Line Tools

Perfect for CLI applications where operations happen one after another.

**Example: CLI Tool**

```python
import argparse
from agentbay import AgentBay, CreateSessionParams

def main():
    parser = argparse.ArgumentParser(description='Run code in AgentBay')
    parser.add_argument('code', help='Code to execute')
    parser.add_argument('--language', default='python', help='Programming language')
    args = parser.parse_args()
    
    agent_bay = AgentBay()
    session = agent_bay.create(CreateSessionParams(image_id="code_latest")).session
    
    result = session.code.run_code(args.code, args.language)
    
    if result.success:
        print(result.result)
    else:
        print(f"Error: {result.error_message}")
    
    agent_bay.delete(session)

if __name__ == "__main__":
    main()
```

#### 3. Learning and Prototyping

When you're learning AgentBay or quickly prototyping ideas, sync API is easier to understand.

**Example: Quick Prototype**

```python
from agentbay import AgentBay

# Simple and straightforward
agent_bay = AgentBay()
session = agent_bay.create().session

# Execute command
result = session.command.execute_command("echo 'Hello World'")
print(result.output)

# Clean up
agent_bay.delete(session)
```

### Advantages

- **Simplicity**: Code reads top-to-bottom, easy to understand
- **Debugging**: Simpler stack traces, easier to debug
- **No async complexity**: No need to understand event loops, coroutines, or async/await
- **Immediate results**: Each operation completes before moving to the next

### Limitations

- **Blocking**: Each operation blocks until complete
- **No concurrency**: Can't run multiple operations simultaneously
- **Resource intensive**: Uses more threads for concurrent operations

## When to Use Async API

### Ideal Use Cases

#### 1. Web Applications

Use async API in web frameworks like FastAPI, Django (async views), or aiohttp.

**Example: FastAPI Endpoint**

```python
from fastapi import FastAPI
from agentbay import AsyncAgentBay, CreateSessionParams

app = FastAPI()
agent_bay = AsyncAgentBay()

@app.post("/execute")
async def execute_code(code: str, language: str = "python"):
    session = (await agent_bay.create(CreateSessionParams(image_id="code_latest"))).session
    
    try:
        result = await session.code.run_code(code, language)
        return {
            "success": result.success,
            "result": result.result if result.success else result.error_message
        }
    finally:
        await agent_bay.delete(session)
```

#### 2. High-Concurrency Applications

When you need to handle many operations simultaneously.

**Example: Concurrent Task Processing**

```python
import asyncio
from agentbay import AsyncAgentBay, CreateSessionParams

async def process_task(task_id: str, code: str):
    agent_bay = AsyncAgentBay()
    session = (await agent_bay.create(CreateSessionParams(image_id="code_latest"))).session
    
    result = await session.code.run_code(code, "python")
    
    await agent_bay.delete(session)
    return {"task_id": task_id, "result": result.result}

async def process_multiple_tasks(tasks):
    # Process all tasks concurrently
    results = await asyncio.gather(*[
        process_task(task["id"], task["code"])
        for task in tasks
    ])
    return results

# Usage
async def main():
    tasks = [
        {"id": "task1", "code": "print('Task 1')"},
        {"id": "task2", "code": "print('Task 2')"},
        {"id": "task3", "code": "print('Task 3')"},
    ]
    
    results = await process_multiple_tasks(tasks)
    for result in results:
        print(f"{result['task_id']}: {result['result']}")

asyncio.run(main())
```

#### 3. Real-Time Systems

Applications that need to respond quickly without blocking.

**Example: Real-Time Monitoring**

```python
import asyncio
from agentbay import AsyncAgentBay, CreateSessionParams

async def monitor_session(session_id: str, agent_bay: AsyncAgentBay):
    """Monitor a session's status"""
    while True:
        # Check session status (non-blocking)
        info = await agent_bay.get(session_id)
        
        if info.success:
            print(f"Session {session_id}: Active")
        else:
            print(f"Session {session_id}: Terminated")
            break
        
        # Wait before next check (allows other tasks to run)
        await asyncio.sleep(5)

async def main():
    agent_bay = AsyncAgentBay()
    
    # Create multiple sessions
    sessions = []
    for i in range(3):
        result = await agent_bay.create(CreateSessionParams(image_id="code_latest"))
        sessions.append(result.session)
    
    # Monitor all sessions concurrently
    await asyncio.gather(*[
        monitor_session(session.session_id, agent_bay)
        for session in sessions
    ])

asyncio.run(main())
```

### Advantages

- **High concurrency**: Handle thousands of operations simultaneously
- **Non-blocking**: Operations don't block the event loop
- **Resource efficient**: Single thread handles many operations
- **Scalability**: Better performance under high load

### Limitations

- **Complexity**: Requires understanding of async/await
- **Debugging**: Async stack traces can be harder to read
- **Compatibility**: Must use async-compatible libraries

## Performance Considerations

### Throughput Comparison

**Scenario: Execute 10 tasks**

#### Sync API (Sequential)
```python
# Time: ~10 seconds (1 second per task)
from agentbay import AgentBay, CreateSessionParams

agent_bay = AgentBay()
for i in range(10):
    session = agent_bay.create(CreateSessionParams(image_id="code_latest")).session
    result = session.code.run_code(f"print('Task {i}')", "python")
    agent_bay.delete(session)
```

#### Async API (Concurrent)
```python
# Time: ~1-2 seconds (all tasks run concurrently)
import asyncio
from agentbay import AsyncAgentBay, CreateSessionParams

async def run_task(i):
    agent_bay = AsyncAgentBay()
    session = (await agent_bay.create(CreateSessionParams(image_id="code_latest"))).session
    result = await session.code.run_code(f"print('Task {i}')", "python")
    await agent_bay.delete(session)
    return result

async def main():
    await asyncio.gather(*[run_task(i) for i in range(10)])

asyncio.run(main())
```

### Resource Usage

| Metric | Sync API | Async API |
|--------|----------|-----------|
| **Memory per operation** | Higher (thread overhead) | Lower (shared event loop) |
| **CPU usage** | Higher (context switching) | Lower (single thread) |
| **Network connections** | One per thread | Reused efficiently |
| **Scalability limit** | ~1000 concurrent ops | ~10,000+ concurrent ops |

### When Performance Matters

- **Use Async** if you need to:
  - Handle > 100 concurrent operations
  - Minimize latency in web applications
  - Maximize throughput with limited resources

- **Use Sync** if you:
  - Have < 10 concurrent operations
  - Prioritize code simplicity
  - Are building one-off scripts

## Migration Guide

### Converting Sync to Async

#### Step 1: Change Imports

```python
# Before (Sync)
from agentbay import AgentBay

# After (Async)
from agentbay import AsyncAgentBay
```

#### Step 2: Add async/await

```python
# Before (Sync)
def my_function():
    agent_bay = AgentBay()
    session = agent_bay.create().session
    result = session.code.run_code("code", "python")
    agent_bay.delete(session)
    return result

# After (Async)
async def my_function():
    agent_bay = AsyncAgentBay()
    session = (await agent_bay.create()).session
    result = await session.code.run_code("code", "python")
    await agent_bay.delete(session)
    return result
```

#### Step 3: Update Function Calls

```python
# Before (Sync)
result = my_function()

# After (Async)
result = await my_function()

# Or if calling from non-async code:
import asyncio
result = asyncio.run(my_function())
```

### Converting Async to Sync

Simply reverse the process:

1. Change `AsyncAgentBay` to `AgentBay`
2. Remove all `await` keywords
3. Remove `async` from function definitions
4. Remove `asyncio.run()` calls

## Best Practices

### Sync API Best Practices

#### 1. Use Context Managers (When Available)

```python
from agentbay import AgentBay

agent_bay = AgentBay()
session = agent_bay.create().session

try:
    # Your operations
    result = session.code.run_code("code", "python")
finally:
    # Always clean up
    agent_bay.delete(session)
```

#### 2. Handle Errors Gracefully

```python
from agentbay import AgentBay
from agentbay.exceptions import AgentBayError

agent_bay = AgentBay()

try:
    session = agent_bay.create().session
    result = session.code.run_code("code", "python")
    
    if not result.success:
        print(f"Execution failed: {result.error_message}")
    
except AgentBayError as e:
    print(f"AgentBay error: {e}")
except Exception as e:
    print(f"Unexpected error: {e}")
finally:
    if 'session' in locals():
        agent_bay.delete(session)
```

#### 3. Reuse Sessions

```python
from agentbay import AgentBay

agent_bay = AgentBay()
session = agent_bay.create().session

# Reuse session for multiple operations
for i in range(10):
    result = session.code.run_code(f"print({i})", "python")
    print(result.result)

agent_bay.delete(session)
```

### Async API Best Practices

#### 1. Use asyncio.gather for Concurrent Operations

```python
import asyncio
from agentbay import AsyncAgentBay

async def main():
    agent_bay = AsyncAgentBay()
    
    # Create multiple sessions concurrently
    sessions = await asyncio.gather(*[
        agent_bay.create()
        for _ in range(3)
    ])
    
    # Use sessions...
    
    # Clean up concurrently
    await asyncio.gather(*[
        agent_bay.delete(s.session)
        for s in sessions if s.success
    ])

asyncio.run(main())
```

#### 2. Handle Timeouts

```python
import asyncio
from agentbay import AsyncAgentBay

async def run_with_timeout():
    agent_bay = AsyncAgentBay()
    session = (await agent_bay.create()).session
    
    try:
        # Set timeout for operation
        result = await asyncio.wait_for(
            session.code.run_code("import time; time.sleep(100)", "python"),
            timeout=10.0
        )
    except asyncio.TimeoutError:
        print("Operation timed out")
    finally:
        await agent_bay.delete(session)

asyncio.run(run_with_timeout())
```

#### 3. Use Semaphores to Limit Concurrency

```python
import asyncio
from agentbay import AsyncAgentBay, CreateSessionParams

async def run_task(semaphore, task_id):
    async with semaphore:
        agent_bay = AsyncAgentBay()
        session = (await agent_bay.create(CreateSessionParams(image_id="code_latest"))).session
        
        result = await session.code.run_code(f"print('Task {task_id}')", "python")
        
        await agent_bay.delete(session)
        return result

async def main():
    # Limit to 5 concurrent operations
    semaphore = asyncio.Semaphore(5)
    
    tasks = [run_task(semaphore, i) for i in range(20)]
    results = await asyncio.gather(*tasks)
    
    print(f"Completed {len(results)} tasks")

asyncio.run(main())
```

## Common Patterns

### Pattern 1: Session Pool (Sync)

```python
from agentbay import AgentBay
from queue import Queue

class SessionPool:
    def __init__(self, size=5):
        self.agent_bay = AgentBay()
        self.pool = Queue(maxsize=size)
        
        # Pre-create sessions
        for _ in range(size):
            session = self.agent_bay.create().session
            self.pool.put(session)
    
    def execute(self, code, language="python"):
        session = self.pool.get()
        try:
            result = session.code.run_code(code, language)
            return result
        finally:
            self.pool.put(session)
    
    def cleanup(self):
        while not self.pool.empty():
            session = self.pool.get()
            self.agent_bay.delete(session)

# Usage
pool = SessionPool(size=3)
try:
    for i in range(10):
        result = pool.execute(f"print({i})")
        print(result.result)
finally:
    pool.cleanup()
```

### Pattern 2: Async Task Queue

```python
import asyncio
from agentbay import AsyncAgentBay, CreateSessionParams

class AsyncTaskQueue:
    def __init__(self, max_concurrent=5):
        self.queue = asyncio.Queue()
        self.semaphore = asyncio.Semaphore(max_concurrent)
        self.agent_bay = AsyncAgentBay()
    
    async def add_task(self, code, language="python"):
        await self.queue.put((code, language))
    
    async def process_task(self):
        while True:
            code, language = await self.queue.get()
            
            async with self.semaphore:
                session = (await self.agent_bay.create(
                    CreateSessionParams(image_id="code_latest")
                )).session
                
                try:
                    result = await session.code.run_code(code, language)
                    print(f"Result: {result.result}")
                finally:
                    await self.agent_bay.delete(session)
            
            self.queue.task_done()
    
    async def run(self, num_workers=3):
        workers = [
            asyncio.create_task(self.process_task())
            for _ in range(num_workers)
        ]
        
        await self.queue.join()
        
        for worker in workers:
            worker.cancel()

# Usage
async def main():
    queue = AsyncTaskQueue(max_concurrent=5)
    
    # Add tasks
    for i in range(10):
        await queue.add_task(f"print('Task {i}')")
    
    # Process tasks
    await queue.run(num_workers=3)

asyncio.run(main())
```

### Pattern 3: Retry with Exponential Backoff

```python
import asyncio
from agentbay import AsyncAgentBay, CreateSessionParams

async def retry_with_backoff(func, max_retries=3, base_delay=1):
    for attempt in range(max_retries):
        try:
            return await func()
        except Exception as e:
            if attempt == max_retries - 1:
                raise
            
            delay = base_delay * (2 ** attempt)
            print(f"Attempt {attempt + 1} failed, retrying in {delay}s...")
            await asyncio.sleep(delay)

async def create_session_with_retry():
    agent_bay = AsyncAgentBay()
    
    async def create():
        result = await agent_bay.create(CreateSessionParams(image_id="code_latest"))
        if not result.success:
            raise Exception(result.error_message)
        return result.session
    
    return await retry_with_backoff(create, max_retries=3)

# Usage
async def main():
    session = await create_session_with_retry()
    print(f"Session created: {session.session_id}")
    
    agent_bay = AsyncAgentBay()
    await agent_bay.delete(session)

asyncio.run(main())
```

## Troubleshooting

### Common Issues

#### Issue 1: "RuntimeWarning: coroutine was never awaited"

**Problem**: Forgot to use `await` with async function.

```python
# Wrong
result = session.code.run_code("code", "python")  # Missing await

# Correct
result = await session.code.run_code("code", "python")
```

#### Issue 2: "Cannot call async function from sync context"

**Problem**: Trying to call async function without asyncio.run().

```python
# Wrong
async def my_func():
    pass

my_func()  # This doesn't work

# Correct
import asyncio
asyncio.run(my_func())
```

#### Issue 3: File Operations Not Working in Async

**Known Limitation**: `write_file` and `read_file` are not fully async in current SDK version.

```python
# Current workaround: Don't use await
session.file_system.write_file("/tmp/file.txt", "content")
content = session.file_system.read_file("/tmp/file.txt")

# Or use command execution
await session.command.execute_command("echo 'content' > /tmp/file.txt")
```

#### Issue 4: "Event loop is closed"

**Problem**: Trying to reuse closed event loop.

```python
# Wrong
loop = asyncio.get_event_loop()
loop.run_until_complete(my_func())
loop.run_until_complete(another_func())  # May fail

# Correct
asyncio.run(my_func())
asyncio.run(another_func())

# Or use single event loop
async def main():
    await my_func()
    await another_func()

asyncio.run(main())
```

### Performance Debugging

#### Measure Async Performance

```python
import asyncio
import time
from agentbay import AsyncAgentBay, CreateSessionParams

async def measure_performance():
    agent_bay = AsyncAgentBay()
    
    # Sequential
    start = time.time()
    for i in range(5):
        session = (await agent_bay.create(CreateSessionParams(image_id="code_latest"))).session
        await agent_bay.delete(session)
    sequential_time = time.time() - start
    
    # Concurrent
    start = time.time()
    async def create_and_delete():
        session = (await agent_bay.create(CreateSessionParams(image_id="code_latest"))).session
        await agent_bay.delete(session)
    
    await asyncio.gather(*[create_and_delete() for _ in range(5)])
    concurrent_time = time.time() - start
    
    print(f"Sequential: {sequential_time:.2f}s")
    print(f"Concurrent: {concurrent_time:.2f}s")
    print(f"Speedup: {sequential_time/concurrent_time:.2f}x")

asyncio.run(measure_performance())
```

## Summary

### Quick Decision Guide

**Choose Sync API if:**
- ✓ Building scripts or CLI tools
- ✓ Processing tasks sequentially
- ✓ Learning AgentBay
- ✓ Simplicity is priority
- ✓ < 10 concurrent operations

**Choose Async API if:**
- ✓ Building web applications
- ✓ Need high concurrency (> 100 ops)
- ✓ Performance is critical
- ✓ Using async frameworks (FastAPI, aiohttp)
- ✓ Building real-time systems

### Key Takeaways

1. **Both APIs are fully featured** - Choose based on your use case, not features
2. **Async is not always faster** - Only benefits concurrent operations
3. **Start simple** - Use sync API first, migrate to async if needed
4. **Test performance** - Measure actual performance in your use case
5. **Mix carefully** - Don't mix sync and async code without proper bridges

## Related Documentation

- [Session Management](basics/session-management.md)
- [Command Execution](basics/command-execution.md)
- [File Operations](basics/file-operations.md)
- [Python API Reference](../../api/README.md)
- [Python Examples](../../examples/README.md)

## Need Help?

- [GitHub Issues](https://github.com/aliyun/wuying-agentbay-sdk/issues)
- [Documentation](../../README.md)

