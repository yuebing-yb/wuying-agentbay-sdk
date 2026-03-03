# Archive Upload Mode Context Sync Example

This directory contains examples demonstrating the Archive upload mode functionality for context synchronization in the AgentBay SDK.

## Overview

The Archive upload mode is designed for efficient file transfer by compressing files before uploading them to the context storage. This is particularly useful when:

- Working with large files
- Dealing with many files
- Optimizing bandwidth usage
- Reducing upload time for compressible content

## Files

### `archive-upload-mode-example.ts`

A comprehensive example that demonstrates:

1. **Context Creation**: Creating a context for Archive upload mode
2. **Sync Policy Configuration**: Setting up sync policy with Archive uploadMode
3. **Session Management**: Creating and managing sessions with context sync
4. **File Operations**: Writing files to the context path
5. **Context Info**: Retrieving context status information
6. **File Verification**: Verifying file information and properties
7. **Cleanup**: Proper session cleanup and error handling

## Key Features Demonstrated

### Archive Upload Mode Configuration

```typescript
// Configure sync policy with Archive upload mode
const syncPolicy = newSyncPolicy();
syncPolicy.uploadPolicy!.uploadMode = "Archive"; // Set to Archive mode

// Create context sync with Archive mode
const contextSync = newContextSync(
  contextId,
  "/tmp/archive-mode-test",
  syncPolicy
);
```

### Session Creation with Context Sync

```typescript
const sessionParams = {
  labels: {
    example: `archive-mode-${uniqueId}`,
    type: "archive-upload-demo",
    uploadMode: "Archive"
  },
  contextSync: [contextSync]
};

const sessionResult = await agentBay.create(sessionParams);
```

### File Operations

```typescript
const fileSystem = new FileSystem(session);

// Write file to context path
const writeResult = await fileSystem.writeFile(filePath, fileContent, "overwrite");

// Get file information
const fileInfoResult = await fileSystem.getFileInfo(filePath);
```

### Context Information Retrieval

```typescript
// Get context status information
const infoResult = await session.context.info();

// Display context status details
infoResult.contextStatusData.forEach((status, index) => {
  console.log(`Context ID: ${status.contextId}`);
  console.log(`Path: ${status.path}`);
  console.log(`Status: ${status.status}`);
  console.log(`Task Type: ${status.taskType}`);
});
```

## Running the Example

### Prerequisites

1. **Environment Setup**: Set your AgentBay API key
   ```bash
   export AGENTBAY_API_KEY="your-api-key-here"
   ```

2. **Dependencies**: Ensure you have the AgentBay SDK installed
   ```bash
   npm install
   ```

### Execution

```bash
# Navigate to the project root
cd /path/to/wuying-agentbay-sdk

# Run the example
npx ts-node docs/example/archive-upload-mode-example.ts
```

### Expected Output

The example will output detailed logs showing:

```
🚀 Archive Upload Mode Context Sync Example
============================================================

📦 Step 1: Creating context for Archive upload mode...
✅ Context created successfully!
   Context ID: ctx_xxxxx
   Request ID: req_xxxxx

⚙️  Step 2: Configuring sync policy with Archive upload mode...
✅ Sync policy configured with uploadMode: Archive

🔧 Step 3: Creating context sync configuration...
✅ Context sync created:
   Context ID: ctx_xxxxx
   Path: /tmp/archive-mode-test
   Upload Mode: Archive

🏗️  Step 4: Creating session with Archive mode context sync...
✅ Session created successfully!
   Session ID: sess_xxxxx
   Request ID: req_xxxxx
   App Instance ID: app_xxxxx

📝 Step 5: Creating test files in Archive mode context...
📄 Creating file: /tmp/archive-mode-test/test-file-5kb.txt
📊 File content size: 5120 bytes
✅ File write successful!
   Request ID: req_xxxxx

📊 Step 6: Testing context info functionality...
✅ Context info retrieved successfully!
   Request ID: req_xxxxx
   Context status data count: X

📋 Context status details:
   [0] Context ID: ctx_xxxxx
       Path: /tmp/archive-mode-test
       Status: Success
       Task Type: upload

🔍 Step 7: Verifying file information...
✅ File info retrieved successfully!
   Request ID: req_xxxxx
📄 File details:
   Size: 5120 bytes
   Is Directory: false
   Modified Time: 2025-10-22T09:52:00Z
   Mode: 644

🎉 Archive upload mode example completed successfully!
✅ All operations completed without errors.

🧹 Step 8: Cleaning up session...
✅ Session deleted successfully!
   Success: true
   Request ID: req_xxxxx
```

## Related Documentation

- [Context Sync Documentation](../../../../../../docs/guides/common-features/basics/data-persistence.md)
- [Session Management Guide](../../../../../../docs/guides/common-features/basics/session-management.md)
- [File Operations Guide](../../../../../../docs/guides/common-features/basics/file-operations.md)

## Troubleshooting

### Common Issues

1. **API Key Not Set**
   ```
   Warning: AGENTBAY_API_KEY environment variable not set
   ```
   **Solution**: Set the environment variable or update the API key in the code

2. **Context Creation Failed**
   ```
   Context creation failed: [error message]
   ```
   **Solution**: Check your API key and network connectivity

3. **Session Creation Failed**
   ```
   Session creation failed: [error message]
   ```
   **Solution**: Verify context sync configuration and try again

4. **File Operation Failed**
   ```
   File write failed: [error message]
   ```
   **Solution**: Check file path permissions and available disk space

## Support

For additional help:
- [GitHub Issues](https://github.com/agentbay-ai/wuying-agentbay-sdk/issues)
- [Documentation Home](../../../../../../README.md)