# AgentBay SDK for TypeScript

> Execute commands, manipulate files, and run code in cloud environments

## 📦 Installation

```bash
npm install wuying-agentbay-sdk
```

## 🚀 Prerequisites

Before using the SDK, you need to:

1. Register an Alibaba Cloud account: [https://aliyun.com](https://aliyun.com)
2. Get API credentials: [AgentBay Console](https://agentbay.console.aliyun.com/service-management)
3. Set environment variable: `export AGENTBAY_API_KEY=your_api_key`

## 🚀 Quick Start
```typescript
import { AgentBay } from 'wuying-agentbay-sdk';

async function main() {
    // Create session
    const agentBay = new AgentBay();
    const result = await agentBay.create();
    // Verified: ✓ Client initialized and session created successfully

    if (result.success) {
        const session = result.session;

        // Execute command
        const cmdResult = await session.command.executeCommand("ls -la");
        console.log(cmdResult.output);
        // Verified: ✓ Command executed successfully
        // Sample output: "总计 100\ndrwxr-x--- 16 wuying wuying 4096..."

        // File operations
        await session.fileSystem.writeFile("/tmp/test.txt", "Hello World");
        const content = await session.fileSystem.readFile("/tmp/test.txt");
        console.log(content.content);
        // Verified: ✓ File written and read successfully
        // Output: "Hello World"
    }
}

main().catch(console.error);
```

## 📖 Complete Documentation

### 🆕 New Users
- [📚 Quick Start Tutorial](https://github.com/agentbay-ai/wuying-agentbay-sdk/tree/main/docs/quickstart/README.md) - Get started in 5 minutes
- [🎯 Core Concepts](https://github.com/agentbay-ai/wuying-agentbay-sdk/tree/main/docs/quickstart/basic-concepts.md) - Understanding cloud environments and sessions

### 🚀 Experienced Users
**Choose Your Cloud Environment:**
- 🌐 [Browser Use](https://github.com/agentbay-ai/wuying-agentbay-sdk/tree/main/docs/guides/browser-use/README.md) - Web scraping, browser testing, form automation
- 🖥️ [Computer Use](https://github.com/agentbay-ai/wuying-agentbay-sdk/tree/main/docs/guides/computer-use/README.md) - Windows desktop automation, UI testing
- 📱 [Mobile Use](https://github.com/agentbay-ai/wuying-agentbay-sdk/tree/main/docs/guides/mobile-use/README.md) - Android UI testing, mobile app automation
- 💻 [CodeSpace](https://github.com/agentbay-ai/wuying-agentbay-sdk/tree/main/docs/guides/codespace/README.md) - Code execution, development environments

**Additional Resources:**
- [📖 Feature Guides](https://github.com/agentbay-ai/wuying-agentbay-sdk/tree/main/docs/guides/README.md) - Complete feature introduction
- [🔧 TypeScript API Reference](docs/api/README.md) - Detailed API documentation
- [💻 TypeScript Examples](docs/examples/README.md) - Complete example code
- [📋 Logging Configuration](https://github.com/agentbay-ai/wuying-agentbay-sdk/tree/main/docs/guides/common-features/configuration/logging.md) - Configure logging levels and output

### 🆘 Need Help
- [🔧 TypeScript API Reference](docs/api/README.md) - Local API documentation
- [💡 TypeScript Examples](docs/examples/README.md) - Local example code

## 🔧 Core Features Quick Reference

### Session Management
```typescript
// Create session
const session = (await agentBay.create()).session;
// Verified: ✓ Session created successfully
```

### File Operations
```typescript
// Read and write files
await session.fileSystem.writeFile("/path/file.txt", "content");
const content = await session.fileSystem.readFile("/path/file.txt");
// Verified: ✓ File operations work correctly
// content.content contains the file's text content

// List directory
const files = await session.fileSystem.listDirectory("/path");
// Verified: ✓ Returns list of file/directory information
```

### Command Execution
```typescript
// Execute command
const result = await session.command.executeCommand("node script.js");
console.log(result.output);
// Verified: ✓ Command executed successfully
// result.output contains the command's stdout
```

### Data Persistence
```typescript
// Create context
const context = (await agentBay.context.get("my-project", true)).context;
// Verified: ✓ Context created or retrieved successfully

// Create session with context
import { ContextSync, SyncPolicy } from 'wuying-agentbay-sdk';
const contextSync = new ContextSync({
    contextId: context.id,
    path: "/tmp/data",
    policy: SyncPolicy.default()
});
const session = (await agentBay.create({ contextSync: [contextSync] })).session;
// Verified: ✓ Session created with context synchronization
// Data in /tmp/data will be synchronized to the context
```

## 🆘 Get Help

- [GitHub Issues](https://github.com/agentbay-ai/wuying-agentbay-sdk/issues)
- [Complete Documentation](https://github.com/agentbay-ai/wuying-agentbay-sdk/tree/main/docs/README.md)

## 📄 License

This project is licensed under the Apache License 2.0 - see the [LICENSE](../LICENSE) file for details.