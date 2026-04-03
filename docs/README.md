# AgentBay SDK Documentation Center

> Complete documentation and development guides for the AgentBay SDK

## 📖 Getting Started

### New to AgentBay
- [Installation Guide](quickstart/installation.md) - SDK installation and environment setup
- [Basic Concepts](quickstart/basic-concepts.md) - Understand cloud environments and sessions
- [First Session](quickstart/first-session.md) - 5-minute quick start with hands-on examples


## 🔧 Feature Guides

- [Feature Guides Overview](guides/README.md) - Complete feature guides introduction

### Common Features (All Environments)
- [Common Features Guide](guides/common-features/README.md) - Features available across all environments

#### Basics
- [Session Management](guides/common-features/basics/session-management.md) - Cloud environment lifecycle management
- [Command Execution](guides/common-features/basics/command-execution.md) - Execute shell commands and scripts
- [File Operations](guides/common-features/basics/file-operations.md) - File upload, download, and management
- [Data Persistence](guides/common-features/basics/data-persistence.md) - Cross-session data storage

#### Advanced
- [Custom Images](guides/common-features/advanced/custom-images.md) - Create tailored environments with specific configurations
- [Session Link Access](guides/common-features/advanced/session-link-access.md) - Session connectivity and URL generation
- [Session Metrics](guides/common-features/advanced/session-metrics.md) - Retrieve runtime metrics via MCP
- [Network (Beta)](guides/common-features/advanced/network.md) - Share an isolated network across sessions
- [Agent Modules](guides/common-features/advanced/agent-modules.md) - AI-powered task automation
- [OSS Integration](guides/common-features/advanced/oss-integration.md) - Object Storage Service integration
- [Skills (Beta)](guides/common-features/advanced/skills.md) - Load reusable skill modules into sessions
- [Git Operations](guides/common-features/advanced/git-operations.md) - Git repository operations in cloud sessions

#### Configuration
- [SDK Configuration](guides/common-features/configuration/sdk-configuration.md) - Configuration options and settings
- [Logging](guides/common-features/configuration/logging.md) - Logging configuration and best practices

#### Use Cases
- [Use Cases Overview](guides/common-features/use-cases/README.md) - Common use case scenarios and implementations
- [Session Info Use Cases](guides/common-features/use-cases/session-info-use-cases.md) - Session information and connectivity patterns
- [Session Link Use Cases](guides/common-features/use-cases/session-link-use-cases.md) - Connect external tools to cloud sessions
- [Context Sync Use Case](guides/common-features/use-cases/context-sync-use-case.md) - Data persistence across sessions
- [Cross-Platform Persistence](guides/common-features/use-cases/cross-platform-persistence.md) - Cross-OS data persistence with MappingPolicy
- [Computer Linux All-in-One](guides/common-features/use-cases/computer-linux-all-in-one-sandbox-use-cases.md) - Combined UI and scripting in a single session

### Environment-Specific Features

#### [Browser Use](guides/browser-use/README.md)
Complete browser automation for web scraping, testing, and form filling.

- [Core Features](guides/browser-use/core-features.md) - Basic browser operations
- [Advanced Features](guides/browser-use/advance-features.md) - Advanced browser capabilities
- [Code Examples](guides/browser-use/code-example.md) - Practical code samples
- [Browser Extensions](guides/browser-use/browser-extensions.md) - Extension management
- [Browser Replay](guides/browser-use/browser-replay.md) - Session replay functionality
- [Integrations](guides/browser-use/integrations.md) - Third-party integrations

**Key Capabilities:**
- [Browser Context](guides/browser-use/core-features/browser-context.md) - Context management
- [Browser Proxies](guides/browser-use/core-features/browser-proxies.md) - Network proxy configuration
- [CAPTCHA Handling](guides/browser-use/core-features/captcha.md) - Automated CAPTCHA solving
- [Extension Support](guides/browser-use/core-features/extension.md) - Browser extension management
- [Browser Fingerprint](guides/browser-use/core-features/browser-fingerprint.md) - Simulate browser fingerprint
- [Browser Screenshot](guides/browser-use/core-features/browser-screenshot.md) - Screenshot capture and analysis
- [Browser Command Args](guides/browser-use/core-features/browser-command-args.md) - Custom browser launch arguments
- [Call for User](guides/browser-use/core-features/call-for-user.md) - User interaction requests
- [Browser Operator](guides/browser-use/advance-features/browser-operator.md) - AI-driven page operations
- [Browser Hybrid Usage](guides/browser-use/advance-features/browser-hybrid-usage.md) - Combine Operator, Agent, and Playwright

#### [Computer Use](guides/computer-use/README.md)
Windows desktop automation for application control and window management.

- [Computer Application Management](guides/computer-use/computer-application-management.md) - Application control and management
- [Computer UI Automation](guides/computer-use/computer-ui-automation.md) - Desktop UI interaction and automation
- [Window Management](guides/computer-use/window-management.md) - Window operations and focus management
- [Browser Capabilities by Image Type](guides/computer-use/browser-capabilities-by-image-type.md) - Understanding browser support across different images

**Key Capabilities:**
- Application Management (start, stop, list applications)
- Window Operations (maximize, minimize, resize, close)
- Focus Management
- Desktop Automation Workflows

#### [Mobile Use](guides/mobile-use/README.md)
Mobile UI automation for app testing and gesture-based interactions.

- [Mobile Application Management](guides/mobile-use/mobile-application-management.md) - Mobile app control and management
- [Mobile UI Automation](guides/mobile-use/mobile-ui-automation.md) - Mobile UI interaction and automation
- [Mobile Simulate](guides/mobile-use/mobile-simulate.md) - Simulate touch, swipe, and sensor events
- [ADB Connection](guides/mobile-use/adb-connection.md) - ADB connection and debugging capabilities
- [Mobile Session Configuration](guides/mobile-use/mobile-session-configuration.md) - Advanced mobile session configuration options

**Key Capabilities:**
- UI Element Detection
- Click Operations and Text Input
- Key Events and Swipe Gestures
- Screenshot Capture
- Mobile Application Management
- ADB Connection and Debugging

#### [CodeSpace](guides/codespace/README.md)
Development environment for code execution and scripting.

- [Code Execution](guides/codespace/code-execution.md) - Python and JavaScript code execution

**Key Capabilities:**
- Python and JavaScript Code Execution
- Shell Command Execution
- File System Operations
- Development Tools Integration
- Package Management (pip, npm, etc.)

#### Agent Module
An AI-powered Agent to complete tasks described in natural language

- [Agent Guide](guides/common-features/advanced/agent-modules.md) - Agent task execution guide

**Key Capabilities:**
- Office Automation: Word/Excel/PowerPoint automation
- File Operations: Create/Delete/Move/Copy files and folders
- Information Gathering: Gather information from the Internet
- Text Editing: Using notepad to edit text files

## 📚 API Reference

- [Python SDK](../python/README.md) - Python version documentation
- [TypeScript SDK](../typescript/README.md) - TypeScript version documentation
- [Golang SDK](../golang/README.md) - Golang version documentation
- [Java SDK](../java/README.md) - Java version documentation

## 🚀 Learning Paths

Choose the appropriate learning path based on your experience level:

### 🆕 Complete Beginners
Start from the basics and build your knowledge step by step:
1. [Basic Concepts](quickstart/basic-concepts.md) - Understand core concepts
2. [Installation Guide](quickstart/installation.md) - Environment setup
3. [First Session](quickstart/first-session.md) - Hands-on practice
4. [Feature Guides](guides/README.md) - Explore specific features as needed

### 🚀 Experienced Developers
Already familiar with browser automation, computer use, or mobile testing? Start here:

**Quick Start (5 minutes):**
1. [Installation](quickstart/installation.md) - Set up your preferred SDK (Python/TypeScript/Golang/Java)
2. Choose your environment based on your use case:
   - 🌐 [Browser Automation](guides/browser-use/README.md) - Web scraping, testing, form filling with stealth capabilities
   - 🖥️ [Computer/Windows Automation](guides/computer-use/README.md) - Desktop UI automation and window management
   - 📱 [Mobile Automation](guides/mobile-use/README.md) - Android UI testing and gesture automation
   - 💻 [CodeSpace](guides/codespace/README.md) - Cloud-based code execution environments

**What makes AgentBay different:**
- [Session Link](guides/common-features/advanced/session-link-access.md) - Direct URL access to services running in cloud sessions
- [Agent Modules](guides/common-features/advanced/agent-modules.md) - AI-powered automation capabilities

**Need more details?** See [Advanced Features](guides/common-features/advanced/README.md) or language-specific API docs: [Python](../python/README.md) | [TypeScript](../typescript/README.md) | [Golang](../golang/README.md) | [Java](../java/README.md)

## 📞 Getting Help

- [GitHub Issues](https://github.com/agentbay-ai/wuying-agentbay-sdk/issues) - Report bugs or request features

---

💡 **Tip**: We recommend starting with the [Quick Start Tutorial](quickstart/README.md), then exploring specific feature guides as needed.
