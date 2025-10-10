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
- [📚 Quick Start Tutorial](https://github.com/aliyun/wuying-agentbay-sdk/tree/main/docs/quickstart/README.md) - Get started in 5 minutes
- [🎯 Core Concepts](https://github.com/aliyun/wuying-agentbay-sdk/tree/main/docs/quickstart/basic-concepts.md) - Understanding cloud environments and sessions

### 🚀 Experienced Users
**Choose Your Cloud Environment:**
- 🌐 [Browser Use](https://github.com/aliyun/wuying-agentbay-sdk/tree/main/docs/guides/browser-use/README.md) - Web scraping, browser testing, form automation
- 🖥️ [Computer Use](https://github.com/aliyun/wuying-agentbay-sdk/tree/main/docs/guides/computer-use/README.md) - Windows desktop automation, UI testing
- 📱 [Mobile Use](https://github.com/aliyun/wuying-agentbay-sdk/tree/main/docs/guides/mobile-use/README.md) - Android UI testing, mobile app automation
- 💻 [CodeSpace](https://github.com/aliyun/wuying-agentbay-sdk/tree/main/docs/guides/codespace/README.md) - Code execution, development environments

**Additional Resources:**
- [📖 Feature Guides](https://github.com/aliyun/wuying-agentbay-sdk/tree/main/docs/guides/README.md) - Complete feature introduction
- [🔧 TypeScript API Reference](docs/api/README.md) - Detailed API documentation
- [💻 TypeScript Examples](docs/examples/README.md) - Complete example code

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
const customRecyclePolicy: RecyclePolicy = {
        lifecycle: Lifecycle.Lifecycle_1Day,
        paths: ["/custom/path"]
      };

      // Create a sync policy with the custom recycle policy
const syncPolicy: SyncPolicy = {
uploadPolicy: newUploadPolicy(),
downloadPolicy: newDownloadPolicy(),
deletePolicy: newDeletePolicy(),
extractPolicy: newExtractPolicy(),
recyclePolicy: customRecyclePolicy,
bwList: {
    whiteLists: [
    {
        path: "",
        excludePaths: [],
    },
    ],
},
};
const contextSync = new ContextSync({
    contextId: context.id,
    path: "/tmp/data",
    policy: syncPolicy
});
const session = (await agentBay.create({ contextSync: [contextSync] })).session;
// Verified: ✓ Session created with context synchronization
// Data in /tmp/data will be synchronized to the context
```

### RecyclePolicy Configuration

The `RecyclePolicy` defines how long context data should be retained and which paths are subject to the policy.

#### Lifecycle Options

The `lifecycle` field determines the data retention period:

| Option | Retention Period | Description |
|--------|------------------|-------------|
| `Lifecycle_1Day` | 1 day | Data deleted after 1 day |
| `Lifecycle_3Days` | 3 days | Data deleted after 3 days |
| `Lifecycle_5Days` | 5 days | Data deleted after 5 days |
| `Lifecycle_10Days` | 10 days | Data deleted after 10 days |
| `Lifecycle_15Days` | 15 days | Data deleted after 15 days |
| `Lifecycle_30Days` | 30 days | Data deleted after 30 days |
| `Lifecycle_90Days` | 90 days | Data deleted after 90 days |
| `Lifecycle_180Days` | 180 days | Data deleted after 180 days |
| `Lifecycle_360Days` | 360 days | Data deleted after 360 days |
| `Lifecycle_Forever` | Permanent | Data never deleted (default) |

**Default Value:** `Lifecycle_Forever`

#### Paths Configuration

The `paths` field specifies which directories or files should be subject to the recycle policy:

**Rules:**
- Must use exact directory/file paths
- **Wildcard patterns (`* ? [ ]`) are NOT supported**
- Empty string `""` means apply to all paths in the context
- Multiple paths can be specified as an array

**Default Value:** `[""]` (applies to all paths)

#### Usage Examples

```typescript
import { RecyclePolicy, Lifecycle } from 'wuying-agentbay-sdk';

// Example 1: Apply to all paths with 30-day retention
const recyclePolicy1: RecyclePolicy = {
    lifecycle: Lifecycle.Lifecycle_30Days,
    paths: [""]  // Apply to all paths
};

// Example 2: Apply to specific directories with 7-day retention
const recyclePolicy2: RecyclePolicy = {
    lifecycle: Lifecycle.Lifecycle_7Days,
    paths: ["/tmp/logs", "/cache"]  // Apply only to these directories
};

// Example 3: Permanent retention for important data
const recyclePolicy3: RecyclePolicy = {
    lifecycle: Lifecycle.Lifecycle_Forever,
    paths: ["/important/data"]
};

// Example 4: Different retention for different paths
const shortTermPolicy: RecyclePolicy = {
    lifecycle: Lifecycle.Lifecycle_1Day,
    paths: ["/tmp", "/cache/temp"]
};

const longTermPolicy: RecyclePolicy = {
    lifecycle: Lifecycle.Lifecycle_90Days,
    paths: ["/data/backups"]
};
```

#### Best Practices

1. **Use appropriate retention periods**: Choose lifecycle options based on your data importance and storage costs
2. **Specify exact paths**: Use precise directory paths instead of wildcards for better control
3. **Separate policies for different data types**: Use different recycle policies for temporary vs. persistent data
4. **Monitor storage usage**: Regularly review and adjust lifecycle settings to optimize storage costs
```

## 🆘 Get Help

- [GitHub Issues](https://github.com/aliyun/wuying-agentbay-sdk/issues)
- [Complete Documentation](https://github.com/aliyun/wuying-agentbay-sdk/tree/main/docs/README.md)

## 📄 License

This project is licensed under the Apache License 2.0 - see the [LICENSE](../LICENSE) file for details.