# Quick Start Guide for Beginners

Welcome to AgentBay SDK! This guide provides a step-by-step learning path for users new to cloud development.

## 🎯 Learning Objectives

After completing this quick start guide, you will be able to:
- Understand AgentBay's core concepts
- Create your first cloud session (both sync and async)
- Perform basic file and command operations in the cloud
- Choose between synchronous and asynchronous APIs
- Learn how to save and reuse your work

## 📚 Learning Path (Estimated 30 minutes)

### Step 1: Environment Setup (5 minutes)
- [Installation and Configuration](installation.md)
- Get API key
- Verify installation

### Step 2: Core Concepts (10 minutes)
- [Understanding Basic Concepts](basic-concepts.md)
- What is a cloud session?
- Differences between sessions and local environments
- Data persistence concepts

### Step 3: First Program (10 minutes)
- [Create Your First Session](first-session.md)
- Quick verification (30 seconds) - Sync & Async
- Cloud data processing example - Sync & Async
- Understanding the differences

### Step 4: Choosing Your API Style (5 minutes)
- When to use synchronous API
- When to use asynchronous API
- Performance considerations

## 🔄 Synchronous vs Asynchronous APIs

AgentBay provides both synchronous and asynchronous APIs. Here's a quick comparison to help you choose:

### Synchronous API (Recommended for Beginners)

**Best for:**
- Learning AgentBay
- Scripts and automation
- CLI tools
- Simple, sequential tasks

**Example:**
```python
from agentbay import AgentBay

agent_bay = AgentBay()
session = agent_bay.create().session
result = session.command.execute_command("echo 'Hello'")
print(result.output)
agent_bay.delete(session)
```

### Asynchronous API

**Best for:**
- Web applications (FastAPI, Django async views)
- High-concurrency scenarios
- Real-time systems
- Processing multiple tasks simultaneously

**Example:**
```python
import asyncio
from agentbay import AsyncAgentBay

async def main():
    agent_bay = AsyncAgentBay()
    session = (await agent_bay.create()).session
    result = await session.command.execute_command("echo 'Hello'")
    print(result.output)
    await agent_bay.delete(session)

asyncio.run(main())
```

### Quick Decision Guide

| Your Situation | Recommended API |
|----------------|-----------------|
| Just learning AgentBay | **Sync** |
| Building a script or CLI tool | **Sync** |
| Building a web application | **Async** |
| Need to handle 100+ concurrent operations | **Async** |
| Simple automation tasks | **Sync** |
| Real-time data processing | **Async** |


## 🚀 Next Steps After Completion

### Core Features
- **[Session Management](../guides/common-features/basics/session-management.md)** - Advanced session patterns
- **[File Operations](../guides/common-features/basics/file-operations.md)** - Upload, download, and manage files
- **[Command Execution](../guides/codespace/code-execution.md)** - Run shell commands and code
- **[Data Persistence](../guides/common-features/basics/data-persistence.md)** - Save and reuse your work

### Advanced Topics
- **[Browser Automation](../guides/computer-use/computer-ui-automation.md)** - Web scraping and testing
- **[Mobile Testing](../guides/mobile-use/mobile-ui-automation.md)** - Android app automation

### Explore More
- Check out the [Feature Guides](../guides/README.md) to learn about complete functionality
- Explore [Use Cases](../guides/common-features/use-cases/README.md) for practical application examples
- Join community discussions

## ❓ Having Issues?

- [GitHub Issues](https://github.com/aliyun/wuying-agentbay-sdk/issues)
- [Documentation](../README.md)

## 💡 Tips

- **Start with Sync API** - It's simpler and easier to understand for beginners
- **Each step includes complete code examples** - Both sync and async versions where applicable
- **Don't worry if you don't understand everything at first** - Learning takes time
- **The community is here to help!** - Don't hesitate to ask questions
- **Try the examples yourself** - Hands-on practice is the best way to learn

## 📊 Learning Progress Checklist

- [ ] Completed environment setup
- [ ] Understood basic concepts
- [ ] Created first session (sync)
- [ ] Tried async version (optional for beginners)
- [ ] Understand when to use sync vs async
- [ ] Ready to explore advanced features

**Congratulations!** Once you've completed these steps, you're ready to build amazing applications with AgentBay! 🎉
