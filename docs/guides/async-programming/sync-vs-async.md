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
 
For a detailed guide on migrating between synchronous and asynchronous APIs, including step-by-step instructions and code transformation patterns, please refer to the [Migration Guide](migration.md).

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
 
For comprehensive best practices, patterns, and error handling strategies for the Async API, please refer to the [Async Patterns Guide](async-patterns.md).

## Common Patterns
 
For common asynchronous programming patterns such as Session Pools, Task Queues, and Retry Mechanisms, please refer to the [Async Patterns Guide](async-patterns.md).

## Troubleshooting
 
For common issues, pitfalls, and performance debugging tips, please refer to the [Migration Guide - Common Pitfalls](migration.md#common-pitfalls) and [Async Patterns - Error Handling](async-patterns.md#error-handling).

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

