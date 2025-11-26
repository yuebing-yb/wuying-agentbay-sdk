# Async Patterns Guide

This guide covers common asynchronous programming patterns when using the AgentBay Python SDK's async API.

## 📋 Table of Contents

- [Overview](#overview)
- [Async Context Managers](#async-context-managers)
- [Error Handling](#error-handling)
- [Concurrent Operations](#concurrent-operations)
- [Resource Cleanup](#resource-cleanup)
- [Timeout Handling](#timeout-handling)
- [Retry Mechanisms](#retry-mechanisms)
- [Rate Limiting](#rate-limiting)
- [Best Practices](#best-practices)

## 🎯 Overview

The async API in AgentBay SDK allows you to write efficient, non-blocking code that can handle multiple operations concurrently. This guide demonstrates common patterns and best practices for async programming with AgentBay.

### When to Use Async Patterns

- **High Concurrency**: Need to manage multiple sessions or operations simultaneously
- **I/O-Bound Operations**: Working with network requests, file operations, or external APIs
- **Web Applications**: Building async web services with FastAPI, aiohttp, or Django async views
- **Real-time Systems**: Applications requiring responsive, non-blocking behavior

## 🔧 Async Context Managers

### Basic Pattern

While AgentBay doesn't provide built-in async context managers, you can create your own:

```python
import asyncio
from agentbay import AsyncAgentBay

class AsyncSessionManager:
    def __init__(self, agent_bay):
        self.agent_bay = agent_bay
        self.session = None

    async def __aenter__(self):
        result = await self.agent_bay.create()
        if not result.success:
            raise Exception(f"Failed to create session: {result.error_message}")
        self.session = result.session
        return self.session

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        if self.session:
            await self.agent_bay.delete(self.session)
        return False

# Usage
async def main():
    agent_bay = AsyncAgentBay()
    async with AsyncSessionManager(agent_bay) as session:
        result = await session.command.execute_command("echo 'Hello'")
        print(result.output)

asyncio.run(main())
```

### Session Pool Pattern

```python
import asyncio
from agentbay import AsyncAgentBay
from asyncio import Queue

class AsyncSessionPool:
    def __init__(self, agent_bay, pool_size=5):
        self.agent_bay = agent_bay
        self.pool_size = pool_size
        self.pool = Queue(maxsize=pool_size)
        self._initialized = False

    async def initialize(self):
        """Pre-create sessions in the pool"""
        if self._initialized:
            return

        sessions = await asyncio.gather(*[
            self.agent_bay.create()
            for _ in range(self.pool_size)
        ])

        for result in sessions:
            if result.success:
                await self.pool.put(result.session)

        self._initialized = True

    async def acquire(self):
        """Get a session from the pool"""
        if not self._initialized:
            await self.initialize()
        return await self.pool.get()

    async def release(self, session):
        """Return a session to the pool"""
        await self.pool.put(session)

    async def cleanup(self):
        """Clean up all sessions in the pool"""
        while not self.pool.empty():
            session = await self.pool.get()
            await self.agent_bay.delete(session)

# Usage
async def main():
    agent_bay = AsyncAgentBay()
    pool = AsyncSessionPool(agent_bay, pool_size=3)

    try:
        # Use sessions from pool
        session = await pool.acquire()
        result = await session.command.execute_command("echo 'Hello'")
        print(result.output)
        await pool.release(session)
    finally:
        await pool.cleanup()

asyncio.run(main())
```

## ⚠️ Error Handling

### Try-Except Pattern

```python
async def safe_execute_command(session, command):
    """Execute command with proper error handling"""
    try:
        result = await session.command.execute_command(command)
        if result.success:
            return result.output
        else:
            print(f"Command failed: {result.error_message}")
            return None
    except Exception as e:
        print(f"Exception occurred: {e}")
        return None

async def main():
    agent_bay = AsyncAgentBay()
    session = (await agent_bay.create()).session

    try:
        output = await safe_execute_command(session, "ls -la")
        if output:
            print(output)
    finally:
        await agent_bay.delete(session)

asyncio.run(main())
```

### Exception Groups (Python 3.11+)

```python
async def main():
    agent_bay = AsyncAgentBay()

    async def create_and_use_session(task_id):
        session = (await agent_bay.create()).session
        try:
            result = await session.command.execute_command(f"echo 'Task {task_id}'")
            if not result.success:
                raise Exception(f"Task {task_id} failed: {result.error_message}")
            return result.output
        finally:
            await agent_bay.delete(session)

    try:
        results = await asyncio.gather(
            create_and_use_session(1),
            create_and_use_session(2),
            create_and_use_session(3),
            return_exceptions=True  # Return exceptions instead of raising
        )

        for i, result in enumerate(results, 1):
            if isinstance(result, Exception):
                print(f"Task {i} failed: {result}")
            else:
                print(f"Task {i} succeeded: {result.strip()}")
    except Exception as e:
        print(f"Unexpected error: {e}")

asyncio.run(main())
```

## 🚀 Concurrent Operations

### Parallel Session Creation

```python
async def main():
    agent_bay = AsyncAgentBay()

    # Create multiple sessions concurrently
    session_results = await asyncio.gather(*[
        agent_bay.create()
        for _ in range(5)
    ])

    sessions = [r.session for r in session_results if r.success]
    print(f"Created {len(sessions)} sessions concurrently")

    # Use sessions concurrently
    results = await asyncio.gather(*[
        session.command.execute_command("hostname")
        for session in sessions
    ])

    for i, result in enumerate(results, 1):
        if result.success:
            print(f"Session {i}: {result.output.strip()}")

    # Clean up concurrently
    await asyncio.gather(*[
        agent_bay.delete(session)
        for session in sessions
    ])

asyncio.run(main())
```

### Task Queue Pattern

```python
import asyncio
from agentbay import AsyncAgentBay

class AsyncTaskQueue:
    def __init__(self, max_concurrent=5):
        self.queue = asyncio.Queue()
        self.semaphore = asyncio.Semaphore(max_concurrent)
        self.agent_bay = AsyncAgentBay()
        self.results = []

    async def add_task(self, command):
        """Add a task to the queue"""
        await self.queue.put(command)

    async def process_task(self):
        """Process a single task"""
        while True:
            try:
                command = await asyncio.wait_for(
                    self.queue.get(),
                    timeout=1.0
                )
            except asyncio.TimeoutError:
                break

            async with self.semaphore:
                session = (await self.agent_bay.create()).session
                try:
                    result = await session.command.execute_command(command)
                    self.results.append({
                        'command': command,
                        'output': result.output if result.success else None,
                        'error': result.error_message if not result.success else None
                    })
                finally:
                    await self.agent_bay.delete(session)

            self.queue.task_done()

    async def run(self, num_workers=3):
        """Run the task queue with multiple workers"""
        workers = [
            asyncio.create_task(self.process_task())
            for _ in range(num_workers)
        ]

        await self.queue.join()

        for worker in workers:
            worker.cancel()

        await asyncio.gather(*workers, return_exceptions=True)

# Usage
async def main():
    queue = AsyncTaskQueue(max_concurrent=3)

    # Add tasks
    commands = [
        "echo 'Task 1'",
        "echo 'Task 2'",
        "echo 'Task 3'",
        "echo 'Task 4'",
        "echo 'Task 5'"
    ]

    for cmd in commands:
        await queue.add_task(cmd)

    # Process tasks
    await queue.run(num_workers=2)

    # Print results
    for result in queue.results:
        print(f"{result['command']}: {result['output'].strip() if result['output'] else result['error']}")

asyncio.run(main())
```

## 🧹 Resource Cleanup

### Proper Cleanup Pattern

```python
async def main():
    agent_bay = AsyncAgentBay()
    sessions = []

    try:
        # Create sessions
        for i in range(3):
            result = await agent_bay.create()
            if result.success:
                sessions.append(result.session)

        # Use sessions
        results = await asyncio.gather(*[
            session.command.execute_command("echo 'Hello'")
            for session in sessions
        ])

        for result in results:
            if result.success:
                print(result.output.strip())

    except Exception as e:
        print(f"Error: {e}")
    finally:
        # Always clean up sessions
        if sessions:
            await asyncio.gather(*[
                agent_bay.delete(session)
                for session in sessions
            ], return_exceptions=True)

asyncio.run(main())
```

### Graceful Shutdown

```python
import signal
import asyncio
from agentbay import AsyncAgentBay

class GracefulShutdown:
    def __init__(self):
        self.agent_bay = AsyncAgentBay()
        self.sessions = []
        self.shutdown_event = asyncio.Event()

    def signal_handler(self, signum, frame):
        """Handle shutdown signals"""
        print(f"\nReceived signal {signum}, shutting down gracefully...")
        self.shutdown_event.set()

    async def cleanup(self):
        """Clean up all resources"""
        if self.sessions:
            print(f"Cleaning up {len(self.sessions)} sessions...")
            await asyncio.gather(*[
                self.agent_bay.delete(session)
                for session in self.sessions
            ], return_exceptions=True)
            self.sessions.clear()

    async def run(self):
        """Main application loop"""
        # Register signal handlers
        signal.signal(signal.SIGINT, self.signal_handler)
        signal.signal(signal.SIGTERM, self.signal_handler)

        try:
            # Create sessions
            for i in range(3):
                result = await self.agent_bay.create()
                if result.success:
                    self.sessions.append(result.session)

            # Main work loop
            while not self.shutdown_event.is_set():
                # Do work
                await asyncio.sleep(1)

        finally:
            await self.cleanup()

# Usage
async def main():
    app = GracefulShutdown()
    await app.run()

asyncio.run(main())
```

## ⏱️ Timeout Handling

### Operation Timeout

```python
async def execute_with_timeout(session, command, timeout=10.0):
    """Execute command with timeout"""
    try:
        result = await asyncio.wait_for(
            session.command.execute_command(command),
            timeout=timeout
        )
        return result
    except asyncio.TimeoutError:
        print(f"Command timed out after {timeout} seconds")
        return None

async def main():
    agent_bay = AsyncAgentBay()
    session = (await agent_bay.create()).session

    try:
        # This will timeout
        result = await execute_with_timeout(
            session,
            "sleep 20",
            timeout=5.0
        )

        if result and result.success:
            print(result.output)
    finally:
        await agent_bay.delete(session)

asyncio.run(main())
```

### Multiple Operations with Timeout

```python
async def main():
    agent_bay = AsyncAgentBay()

    async def create_and_execute(task_id):
        session = (await agent_bay.create()).session
        try:
            result = await session.command.execute_command(f"echo 'Task {task_id}'")
            return result.output if result.success else None
        finally:
            await agent_bay.delete(session)

    try:
        # All tasks must complete within 30 seconds
        results = await asyncio.wait_for(
            asyncio.gather(*[
                create_and_execute(i)
                for i in range(5)
            ]),
            timeout=30.0
        )

        for i, result in enumerate(results, 1):
            if result:
                print(f"Task {i}: {result.strip()}")
    except asyncio.TimeoutError:
        print("Operations timed out")

asyncio.run(main())
```

## 🔄 Retry Mechanisms

### Exponential Backoff

```python
async def retry_with_backoff(func, max_retries=3, base_delay=1.0):
    """Retry function with exponential backoff"""
    for attempt in range(max_retries):
        try:
            return await func()
        except Exception as e:
            if attempt == max_retries - 1:
                raise

            delay = base_delay * (2 ** attempt)
            print(f"Attempt {attempt + 1} failed: {e}")
            print(f"Retrying in {delay} seconds...")
            await asyncio.sleep(delay)

async def main():
    agent_bay = AsyncAgentBay()

    async def create_session():
        result = await agent_bay.create()
        if not result.success:
            raise Exception(result.error_message)
        return result.session

    try:
        session = await retry_with_backoff(create_session, max_retries=3)
        print(f"Session created: {session.session_id}")
        await agent_bay.delete(session)
    except Exception as e:
        print(f"Failed after retries: {e}")

asyncio.run(main())
```

## 🚦 Rate Limiting

### Token Bucket Pattern

```python
import time
import asyncio
from agentbay import AsyncAgentBay

class RateLimiter:
    def __init__(self, rate, per):
        """
        rate: number of operations
        per: time period in seconds
        """
        self.rate = rate
        self.per = per
        self.allowance = rate
        self.last_check = time.time()

    async def acquire(self):
        """Wait if necessary to stay within rate limit"""
        current = time.time()
        time_passed = current - self.last_check
        self.last_check = current
        self.allowance += time_passed * (self.rate / self.per)

        if self.allowance > self.rate:
            self.allowance = self.rate

        if self.allowance < 1.0:
            sleep_time = (1.0 - self.allowance) * (self.per / self.rate)
            await asyncio.sleep(sleep_time)
            self.allowance = 0.0
        else:
            self.allowance -= 1.0

# Usage
async def main():
    agent_bay = AsyncAgentBay()
    limiter = RateLimiter(rate=5, per=1.0)  # 5 operations per second

    async def rate_limited_create():
        await limiter.acquire()
        return await agent_bay.create()

    # Create 10 sessions with rate limiting
    start = time.time()
    results = await asyncio.gather(*[
        rate_limited_create()
        for _ in range(10)
    ])
    elapsed = time.time() - start

    sessions = [r.session for r in results if r.success]
    print(f"Created {len(sessions)} sessions in {elapsed:.2f} seconds")

    # Cleanup
    await asyncio.gather(*[
        agent_bay.delete(session)
        for session in sessions
    ])

asyncio.run(main())
```

## ✅ Best Practices

### 1. Always Use Finally for Cleanup

```python
async def main():
    agent_bay = AsyncAgentBay()
    session = None

    try:
        session = (await agent_bay.create()).session
        # Do work
    finally:
        if session:
            await agent_bay.delete(session)
```

### 2. Use Semaphores to Limit Concurrency

```python
async def main():
    agent_bay = AsyncAgentBay()
    semaphore = asyncio.Semaphore(5)  # Max 5 concurrent operations

    async def limited_operation(task_id):
        async with semaphore:
            session = (await agent_bay.create()).session
            try:
                result = await session.command.execute_command(f"echo 'Task {task_id}'")
                return result.output
            finally:
                await agent_bay.delete(session)

    results = await asyncio.gather(*[
        limited_operation(i)
        for i in range(20)
    ])
```

### 3. Handle Exceptions in Gather

```python
async def main():
    agent_bay = AsyncAgentBay()

    results = await asyncio.gather(
        agent_bay.create(),
        agent_bay.create(),
        agent_bay.create(),
        return_exceptions=True  # Don't fail all if one fails
    )

    for i, result in enumerate(results, 1):
        if isinstance(result, Exception):
            print(f"Session {i} failed: {result}")
        elif result.success:
            print(f"Session {i} created: {result.session.session_id}")
            await agent_bay.delete(result.session)
```

### 4. Use Timeouts

```python
async def main():
    agent_bay = AsyncAgentBay()

    try:
        result = await asyncio.wait_for(
            agent_bay.create(),
            timeout=30.0
        )
        if result.success:
            await agent_bay.delete(result.session)
    except asyncio.TimeoutError:
        print("Operation timed out")
```

### 5. Batch Operations

```python
async def main():
    agent_bay = AsyncAgentBay()

    # Create sessions in batches
    batch_size = 5
    all_sessions = []

    for i in range(0, 20, batch_size):
        batch_results = await asyncio.gather(*[
            agent_bay.create()
            for _ in range(batch_size)
        ])
        sessions = [r.session for r in batch_results if r.success]
        all_sessions.extend(sessions)

    print(f"Created {len(all_sessions)} sessions in batches")

    # Cleanup
    await asyncio.gather(*[
        agent_bay.delete(session)
        for session in all_sessions
    ])
```

## 📚 Related Documentation

- [Sync vs Async Guide](sync-vs-async.md) - Comprehensive comparison and decision guide
- [Session Management](basics/session-management.md) - Session lifecycle and management
- [Command Execution](basics/command-execution.md) - Command execution patterns

## 🆘 Getting Help

- [GitHub Issues](https://github.com/aliyun/wuying-agentbay-sdk/issues)
- [Documentation Home](../README.md)

Happy async programming with AgentBay! 🚀

