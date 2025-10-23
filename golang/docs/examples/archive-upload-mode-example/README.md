## Archive Upload Mode Context Sync Example

This directory contains examples demonstrating the Archive upload mode functionality for context synchronization in the AgentBay Go SDK.

## Overview

The Archive upload mode is designed for efficient file transfer by compressing files before uploading them to the context storage. This is particularly useful when:

- Working with large files
- Dealing with many files
- Optimizing bandwidth usage
- Reducing upload time for compressible content

## Files

### `main.go`

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

```go
// Configure sync policy with Archive upload mode
uploadPolicy := &agentbay.UploadPolicy{
    UploadMode: "Archive", // Set to Archive mode
}
syncPolicy := &agentbay.SyncPolicy{
    UploadPolicy: uploadPolicy,
}

// Create context sync with Archive mode
contextSync := &agentbay.ContextSync{
    ContextID: contextResult.ContextID,
    Path:      "/tmp/archive-mode-test",
    Policy:    syncPolicy,
}
```

### Session Creation with Context Sync

```go
sessionParams := agentbay.NewCreateSessionParams().
    WithLabels(map[string]string{
        "example":    fmt.Sprintf("archive-mode-%s", uniqueID),
        "type":       "archive-upload-demo",
        "uploadMode": "Archive",
    }).
    WithContextSync([]*agentbay.ContextSync{contextSync})

sessionResult, err := ab.Create(sessionParams)
```

### File Operations

```go
// Write file to context path
writeResult, err := session.FileSystem.WriteFile(filePath, fileContent, "overwrite")

// Get file information
fileInfoResult, err := session.FileSystem.GetFileInfo(filePath)
```

### Context Information Retrieval

```go
// Get context status information
infoResult, err := session.Context.Info()

// Display context status details
for index, status := range infoResult.ContextStatusData {
    fmt.Printf("Context ID: %s\n", status.ContextId)
    fmt.Printf("Path: %s\n", status.Path)
    fmt.Printf("Status: %s\n", status.Status)
    fmt.Printf("Task Type: %s\n", status.TaskType)
}
```

## Running the Example

### Prerequisites

1. **Environment Setup**: Set your AgentBay API key
   ```bash
   export AGENTBAY_API_KEY="your-api-key-here"
   ```

2. **Dependencies**: Ensure you have the Go modules downloaded
   ```bash
   go mod tidy
   ```

### Execution

```bash
# Navigate to the example directory
cd golang/docs/examples/archive-upload-mode-example

# Run the example
go run main.go
```

### Expected Output

The example will output detailed logs showing:

```
🚀 AgentBay Archive Upload Mode Context Sync Example
============================================================

📦 === Archive Upload Mode Context Sync Example ===

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

- [Context Sync Documentation](../../../guides/common-features/basics/data-persistence.md)
- [Session Management Guide](../../../guides/common-features/basics/session-management.md)
- [File Operations Guide](../../../guides/common-features/basics/file-operations.md)

## Troubleshooting

### Common Issues

1. **API Key Not Set**
   ```
   Warning: AGENTBAY_API_KEY environment variable not set
   ```
   **Solution**: Set the environment variable or update the API key in the code

2. **Context Creation Failed**
   ```
   context creation failed: [error message]
   ```
   **Solution**: Check your API key and network connectivity

3. **Session Creation Failed**
   ```
   session creation failed: [error message]
   ```
   **Solution**: Verify context sync configuration and try again

4. **File Operation Failed**
   ```
   file write failed: [error message]
   ```
   **Solution**: Check file path permissions and available disk space

## Support

For additional help:
- [GitHub Issues](https://github.com/aliyun/wuying-agentbay-sdk/issues)
- [Documentation Home](../../../README.md)