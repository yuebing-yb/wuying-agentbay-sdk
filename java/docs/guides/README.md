# AgentBay Java SDK Guides

Complete guides for using the AgentBay Java SDK effectively.

## 📚 Getting Started

- [Quick Start](../../README.md#-quick-start) - Get up and running in 5 minutes
- [Core Concepts](../../../docs/guides/README.md) - Understand sessions, contexts, and cloud environments

## 🎯 Feature Guides

### Common Features

**Basics:**
- [Session Management](../../../docs/guides/common-features/basics/session-management.md) - Create, list, pause, and delete sessions
- [Data Persistence](../../../docs/guides/common-features/basics/data-persistence.md) - Context synchronization and data persistence
- [File Operations](../api/common-features/basics/filesystem.md) - Read, write, and manage files in cloud environments

**Advanced:**
- [VPC Sessions](../../../docs/guides/common-features/advanced/vpc-sessions.md) - Connect sessions to your VPC network
- [OSS Integration](../../../docs/guides/common-features/advanced/oss-integration.md) - Object storage integration
- [Custom Images](../../../docs/guides/common-features/advanced/custom-images.md) - Use custom Docker images

**Configuration:**
- [Logging Configuration](../../../docs/guides/common-features/configuration/logging.md) - Configure logging levels and output
- [Session Configuration](../api/session-configuration-parameters.md) - Complete session parameter reference
- [Extra Configs Guide](../EXTRA_CONFIGS_GUIDE.md) - Advanced mobile and browser configurations

### Environment-Specific Guides

**Browser Use:**
- [Browser Use Overview](../../../docs/guides/browser-use/README.md) - Web automation and testing
- [Core Features](../../../docs/guides/browser-use/core-features.md) - Browser automation capabilities
- [Browser Extensions](../../../docs/guides/browser-use/browser-extensions.md) - Extension testing and development
- [Advanced Features](../../../docs/guides/browser-use/advance-features.md) - Browser agents and automation

**Mobile Use:**
- [Mobile Use Overview](../../../docs/guides/mobile-use/README.md) - Android device automation
- [Mobile UI Automation](../../../docs/guides/mobile-use/mobile-ui-automation.md) - Touch, swipe, and gesture automation
- [Mobile Device Management](../../../docs/guides/mobile-use/mobile-application-management.md) - Install, start, stop apps
- [ADB Connection](../../../docs/guides/mobile-use/adb-connection.md) - Connect via ADB for debugging
- [Mobile Device Simulation](../../../docs/guides/mobile-use/mobile-simulate.md) - Simulate different device models

**Computer Use:**
- [Computer Use Overview](../../../docs/guides/computer-use/README.md) - Windows desktop automation
- [Computer UI Automation](../../../docs/guides/computer-use/computer-ui-automation.md) - Desktop UI interaction
- [Window Management](../../../docs/guides/computer-use/window-management.md) - Manage application windows
- [Computer Application Management](../../../docs/guides/computer-use/computer-application-management.md) - Start/stop desktop apps

**CodeSpace:**
- [CodeSpace Overview](../../../docs/guides/codespace/README.md) - Code execution environments
- [Code Execution](../api/codespace/code.md) - Run Python, JavaScript, and more

## 💻 Examples

Comprehensive examples demonstrating SDK capabilities:

- [Example Index](../examples/README.md) - Complete list of runnable examples
- [Basic Examples](../examples/README.md#core-features) - File operations, session management
- [Browser Examples](../examples/README.md#browser-automation) - Playwright integration, browser automation
- [Mobile Examples](../examples/README.md#mobile-use--mobile-automation) - Mobile UI automation, ADB connection
- [Computer Examples](../examples/README.md#computer-use--application-management) - Desktop app management

## 🔍 API Reference

Detailed API documentation for all SDK classes:

- [API Documentation](../api/README.md) - Complete API reference
- [AgentBay Client](../api/common-features/basics/agentbay.md) - Main client class
- [Session](../api/common-features/basics/session.md) - Session management
- [Command](../api/common-features/basics/command.md) - Execute commands
- [FileSystem](../api/common-features/basics/filesystem.md) - File operations
- [Context](../api/common-features/basics/context.md) - Context management
- [Browser](../api/browser-use/browser.md) - Browser automation
- [Mobile](../api/mobile-use/mobile.md) - Mobile automation
- [Computer](../api/computer-use/computer.md) - Computer automation

## 🎓 Use Cases

Learn how to solve real-world problems:

- [Session Info Use Cases](../../../docs/guides/common-features/use-cases/session-info-use-cases.md) - Get session URLs, credentials, and info
- [Session Link Use Cases](../../../docs/guides/common-features/use-cases/session-link-use-cases.md) - Share session access with team members
- [Cross-Platform Persistence](../../../docs/guides/common-features/use-cases/cross-platform-persistence.md) - Share data across different environments

## 🤝 Best Practices

### Error Handling

Always check result success status:

```java
SessionResult result = agentBay.create(params);
if (result.isSuccess()) {
    Session session = result.getSession();
    // Use session
} else {
    System.err.println("Error: " + result.getErrorMessage());
}
```

### Resource Cleanup

Always clean up sessions:

```java
Session session = null;
try {
    session = agentBay.create().getSession();
    // Use session
} finally {
    if (session != null) {
        session.delete();
    }
}
```

### Context Synchronization

Sync context before deleting session to persist data:

```java
// Sync context and wait for completion
session.getContext().syncAndWait();

// Delete session with context sync enabled
agentBay.delete(session, true);  // sync_context=true
```

## 📖 Additional Resources

- [Java README](../../README.md) - SDK overview and quick start
- [Main Documentation](../../../docs/README.md) - Complete platform documentation
- [GitHub Issues](https://github.com/aliyun/wuying-agentbay-sdk/issues) - Report issues and get support

## 🚀 Next Steps

1. **New to AgentBay?** Start with the [Quick Start](../../README.md#-quick-start)
2. **Need examples?** Browse the [Example Index](../examples/README.md)
3. **Looking for specific features?** Check the [API Reference](../api/README.md)
4. **Want to understand concepts?** Read the [Feature Guides](../../../docs/guides/README.md)
