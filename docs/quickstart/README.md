# Quick Start Guide for Beginners

Welcome to AgentBay SDK! This guide provides a step-by-step learning path for users new to cloud development.

> **Multi-language support:** This quickstart uses **Python** for code examples. The concepts are identical across all supported languages — only the syntax differs. For language-specific guides, see: [Python](../../python/README.md) | [TypeScript](../../typescript/README.md) | [Golang](../../golang/README.md) | [Java](../../java/README.md)

## 🎯 Learning Objectives

After completing this quick start guide, you will be able to:
- Understand AgentBay's core concepts
- Install the SDK in your preferred language
- Create your first cloud session
- Perform basic file and command operations in the cloud
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
- Quick verification (30 seconds)
- Cloud data processing example

### Step 4: Explore Your Language (5 minutes)
- Dive into your language-specific SDK docs
- [Python](../../python/README.md) | [TypeScript](../../typescript/README.md) | [Golang](../../golang/README.md) | [Java](../../java/README.md)

## 🔄 Sync vs Async APIs (Python)

> **Note:** This section applies to the **Python SDK** only. TypeScript uses async/await by default, and Golang/Java use synchronous APIs.

The Python SDK provides both synchronous (`AgentBay`) and asynchronous (`AsyncAgentBay`) APIs:

| Your Situation | Recommended API |
|----------------|-----------------|
| Learning, scripts, CLI tools | **Sync** (`AgentBay`) |
| Web apps, high concurrency | **Async** (`AsyncAgentBay`) |

**Start with the synchronous API** — it's simpler and all quickstart examples use it. See the [Python SDK docs](../../python/README.md) for async examples.

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

- [GitHub Issues](https://github.com/agentbay-ai/wuying-agentbay-sdk/issues)
- [Documentation](../README.md)

## 💡 Tips

- **Concepts are language-agnostic** — the quickstart uses Python, but the same workflow applies to all SDKs
- **Each step includes runnable code examples** — try them yourself for the best learning experience
- **Don't worry if you don't understand everything at first** — learning takes time
- **The community is here to help!** — don't hesitate to ask questions

## 📊 Learning Progress Checklist

- [ ] Completed environment setup
- [ ] Understood basic concepts
- [ ] Created first session
- [ ] Ran commands and file operations in the cloud
- [ ] Ready to explore advanced features

**Congratulations!** Once you've completed these steps, you're ready to build amazing applications with AgentBay! 🎉
