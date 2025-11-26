# Command Execution Guide

This guide covers command execution capabilities in AgentBay SDK. The command module allows you to execute shell commands and system operations in cloud sessions with both synchronous and asynchronous APIs.

## 📋 Table of Contents

- [Overview](#overview)
- [Basic Command Execution](#basic-command-execution)
- [Command with Timeout](#command-with-timeout)
- [Working with Command Output](#working-with-command-output)
- [Advanced Patterns](#advanced-patterns)
- [Choosing Sync vs Async](#choosing-sync-vs-async)

<a id="overview"></a>
## 🎯 Overview

The `session.command` module provides programmatic access to execute shell commands in cloud sessions. This is useful for:

- **System Operations** - Run shell commands, manage processes
- **Environment Setup** - Install packages, configure environments
- **File Processing** - Use command-line tools for file operations
- **Automation** - Automate complex workflows

### Command Module Features

- ✅ Synchronous and asynchronous command execution
- ✅ Timeout support
- ✅ Output and error capture
- ✅ Exit code handling

<a id="basic-command-execution"></a>
## 💻 Basic Command Execution

### Simple Commands (Sync)

```python
from agentbay import AgentBay

agent_bay = AgentBay(api_key="your-api-key")
result = agent_bay.create()

if result.success:
    session = result.session

    cmd_result = session.command.execute_command("ls -la /tmp")
    if cmd_result.success:
        print("Output:", cmd_result.output)
    else:
        print("Command failed:", cmd_result.error_message)

    agent_bay.delete(session)
else:
    print("Failed to create session:", result.error_message)

# Output example:
# Output: total 140
# drwxrwxrwt 21 root   root    4096 Oct  2 14:57 .
# drwxr-xr-x 19 root   root    4096 Oct  2 14:20 ..
# -rw-------  1 root   root       0 Oct  2 14:20 example.lock
# srwxr-xr-x  1 root   root       0 Oct  2 14:20 service.sock
# ...
```

### Simple Commands (Async)

```python
import asyncio
from agentbay import AsyncAgentBay

async def main():
    agent_bay = AsyncAgentBay(api_key="your-api-key")
    result = await agent_bay.create()

    if result.success:
        session = result.session

        cmd_result = await session.command.execute_command("ls -la /tmp")
        if cmd_result.success:
            print("Output:", cmd_result.output)
        else:
            print("Command failed:", cmd_result.error_message)

        await agent_bay.delete(session)
    else:
        print("Failed to create session:", result.error_message)

asyncio.run(main())

# Output example:
# Output: total 140
# drwxrwxrwt 21 root   root    4096 Oct  2 14:57 .
# drwxr-xr-x 19 root   root    4096 Oct  2 14:20 ..
# ...
```

### Command with Arguments (Sync)

```python
session = agent_bay.create().session

commands = [
    "echo 'Hello from cloud'",
    "pwd",
    "whoami",
    "uname -a"
]

for cmd in commands:
    result = session.command.execute_command(cmd)
    if result.success:
        print(f"{cmd} -> {result.output.strip()}")
    else:
        print(f"{cmd} failed: {result.error_message}")

agent_bay.delete(session)

# Output example:
# echo 'Hello from cloud' -> Hello from cloud
# pwd -> /home/user
# whoami -> user
# uname -a -> Linux hostname 5.15.0-125-generic #135-Ubuntu SMP x86_64 x86_64 x86_64 GNU/Linux
```

### Command with Arguments (Async)

```python
async def main():
    agent_bay = AsyncAgentBay()
    session = (await agent_bay.create()).session

    commands = [
        "echo 'Hello from cloud'",
        "pwd",
        "whoami",
        "uname -a"
    ]

    for cmd in commands:
        result = await session.command.execute_command(cmd)
        if result.success:
            print(f"{cmd} -> {result.output.strip()}")
        else:
            print(f"{cmd} failed: {result.error_message}")

    await agent_bay.delete(session)

asyncio.run(main())
```

### Concurrent Command Execution (Async Only)

One of the key benefits of the async API is the ability to execute multiple commands concurrently:

```python
async def main():
    agent_bay = AsyncAgentBay()
    session = (await agent_bay.create()).session

    # Execute multiple commands concurrently
    commands = [
        "sleep 2 && echo 'Command 1 done'",
        "sleep 2 && echo 'Command 2 done'",
        "sleep 2 && echo 'Command 3 done'"
    ]

    # This takes ~2 seconds instead of ~6 seconds
    results = await asyncio.gather(*[
        session.command.execute_command(cmd)
        for cmd in commands
    ])

    for i, result in enumerate(results, 1):
        if result.success:
            print(f"Command {i}: {result.output.strip()}")

    await agent_bay.delete(session)

asyncio.run(main())

# Output (all commands complete in ~2 seconds):
# Command 1: Command 1 done
# Command 2: Command 2 done
# Command 3: Command 3 done
```

<a id="command-with-timeout"></a>
## ⏱️ Command with Timeout

### Setting Execution Timeout (Sync)

```python
session = agent_bay.create().session

# Command completes within timeout
result = session.command.execute_command("sleep 3", timeout_ms=5000)
if result.success:
    print("Command completed within timeout")
else:
    print("Command timed out or failed:", result.error_message)

# Command exceeds timeout
result = session.command.execute_command("sleep 10", timeout_ms=2000)
if result.success:
    print("Command completed")
else:
    print("Command timed out:", result.error_message)

agent_bay.delete(session)

# Output example:
# Command completed within timeout
# Command timed out: Error in response: Execution failed. Error code:-1 Error message: [timeout]
```

### Setting Execution Timeout (Async)

```python
async def main():
    agent_bay = AsyncAgentBay()
    session = (await agent_bay.create()).session

    # Command completes within timeout
    result = await session.command.execute_command("sleep 3", timeout_ms=5000)
    if result.success:
        print("Command completed within timeout")
    else:
        print("Command timed out or failed:", result.error_message)

    # Command exceeds timeout
    result = await session.command.execute_command("sleep 10", timeout_ms=2000)
    if result.success:
        print("Command completed")
    else:
        print("Command timed out:", result.error_message)

    await agent_bay.delete(session)

asyncio.run(main())
```

### Async Timeout with asyncio

You can also use asyncio's timeout functionality:

```python
async def main():
    agent_bay = AsyncAgentBay()
    session = (await agent_bay.create()).session

    try:
        # Use asyncio.wait_for for timeout
        result = await asyncio.wait_for(
            session.command.execute_command("sleep 10"),
            timeout=5.0  # 5 seconds
        )
        print("Command completed:", result.output)
    except asyncio.TimeoutError:
        print("Command timed out after 5 seconds")
    finally:
        await agent_bay.delete(session)

asyncio.run(main())
```

<a id="working-with-command-output"></a>
## 📤 Working with Command Output

### Capturing Output (Sync)

```python
session = agent_bay.create().session

result = session.command.execute_command("df -h")
if result.success:
    print("Full output:")
    print(result.output)

    lines = result.output.strip().split('\n')
    print(f"Found {len(lines)} filesystems")
else:
    print("Command failed:", result.error_message)

agent_bay.delete(session)

# Output example:
# Full output:
# Filesystem      Size  Used Avail Use% Mounted on
# tmpfs           756M  2.9M  753M   1% /run
# /dev/vda3        99G   23G   72G  24% /
# tmpfs           3.7G     0  3.7G   0% /dev/shm
# tmpfs           5.0M     0  5.0M   0% /run/lock
# ...
# Found 8 filesystems
```

### Capturing Output (Async)

```python
async def main():
    agent_bay = AsyncAgentBay()
    session = (await agent_bay.create()).session

    result = await session.command.execute_command("df -h")
    if result.success:
        print("Full output:")
        print(result.output)

        lines = result.output.strip().split('\n')
        print(f"Found {len(lines)} filesystems")
    else:
        print("Command failed:", result.error_message)

    await agent_bay.delete(session)

asyncio.run(main())
```

<a id="advanced-patterns"></a>
## 🔧 Advanced Patterns

### Command Chaining (Sync)

```python
session = agent_bay.create().session

result = session.command.execute_command(
    "mkdir -p /tmp/test && cd /tmp/test && echo 'Hello' > file.txt && cat file.txt"
)
if result.success:
    print("Output:", result.output)

agent_bay.delete(session)

# Output example:
# Output: Hello
```

### Command Chaining (Async)

```python
async def main():
    agent_bay = AsyncAgentBay()
    session = (await agent_bay.create()).session

    result = await session.command.execute_command(
        "mkdir -p /tmp/test && cd /tmp/test && echo 'Hello' > file.txt && cat file.txt"
    )
    if result.success:
        print("Output:", result.output)

    await agent_bay.delete(session)

asyncio.run(main())
```

### Pipeline Pattern (Async)

Execute a series of dependent commands efficiently:

```python
async def main():
    agent_bay = AsyncAgentBay()
    session = (await agent_bay.create()).session

    # Setup
    await session.command.execute_command("mkdir -p /tmp/pipeline")

    # Execute pipeline
    commands = [
        "echo 'Step 1: Creating file' && echo 'data' > /tmp/pipeline/input.txt",
        "echo 'Step 2: Processing' && cat /tmp/pipeline/input.txt | tr 'a-z' 'A-Z' > /tmp/pipeline/output.txt",
        "echo 'Step 3: Result' && cat /tmp/pipeline/output.txt"
    ]

    for cmd in commands:
        result = await session.command.execute_command(cmd)
        if result.success:
            print(result.output.strip())

    await agent_bay.delete(session)

asyncio.run(main())

# Output:
# Step 1: Creating file
# Step 2: Processing
# Step 3: Result
# DATA
```

### Parallel Processing (Async)

Process multiple independent tasks concurrently:

```python
async def process_file(session, filename):
    """Process a single file"""
    cmd = f"wc -l /tmp/{filename}"
    result = await session.command.execute_command(cmd)
    if result.success:
        return f"{filename}: {result.output.strip()}"
    return f"{filename}: failed"

async def main():
    agent_bay = AsyncAgentBay()
    session = (await agent_bay.create()).session

    # Create test files
    for i in range(5):
        await session.command.execute_command(
            f"seq 1 {(i+1)*10} > /tmp/file{i}.txt"
        )

    # Process all files concurrently
    files = [f"file{i}.txt" for i in range(5)]
    results = await asyncio.gather(*[
        process_file(session, f)
        for f in files
    ])

    for result in results:
        print(result)

    await agent_bay.delete(session)

asyncio.run(main())

# Output:
# file0.txt: 10 /tmp/file0.txt
# file1.txt: 20 /tmp/file1.txt
# file2.txt: 30 /tmp/file2.txt
# file3.txt: 40 /tmp/file3.txt
# file4.txt: 50 /tmp/file4.txt
```

<a id="choosing-sync-vs-async"></a>
## 🔄 Choosing Sync vs Async

### Use Sync API When:

- ✅ Writing simple scripts or CLI tools
- ✅ Commands must execute sequentially
- ✅ Learning AgentBay for the first time
- ✅ Code simplicity is more important than performance

### Use Async API When:

- ✅ Building web applications (FastAPI, Django async)
- ✅ Need to execute multiple commands concurrently
- ✅ Working with I/O-bound operations
- ✅ Performance and scalability are critical

### Performance Comparison

**Sequential Execution (5 commands, 1 second each)**:
- Sync API: ~5 seconds
- Async API (sequential): ~5 seconds
- Async API (concurrent): ~1 second

**Recommendation**: For command execution, async API shines when you need to run multiple commands concurrently. For single commands or sequential workflows, both APIs perform similarly.

## 📚 Related Documentation

- [Sync vs Async Guide](../sync-vs-async.md) - Comprehensive comparison and decision guide
- [Code Execution (CodeSpace)](../../codespace/code-execution.md) - Python, JavaScript code execution
- [File Operations](file-operations.md) - File handling and management
- [Session Management](session-management.md) - Session lifecycle

## 🆘 Getting Help

- [GitHub Issues](https://github.com/aliyun/wuying-agentbay-sdk/issues)
- [Documentation Home](../README.md)

Happy automating with AgentBay! 🚀
