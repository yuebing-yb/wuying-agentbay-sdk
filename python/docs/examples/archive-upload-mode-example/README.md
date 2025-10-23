# Archive Upload Mode Context Sync Example

This directory contains examples demonstrating the Archive upload mode functionality for context synchronization in the AgentBay SDK.

## Overview

The Archive upload mode is designed for efficient file transfer by compressing files before uploading them to the context storage. This is particularly useful when:

- Working with large files
- Dealing with many files
- Optimizing bandwidth usage
- Reducing upload time for compressible content

## Files

### `main.py`

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

```python
# Configure sync policy with Archive upload mode
upload_policy = UploadPolicy(upload_mode="Archive")
sync_policy = SyncPolicy(upload_policy=upload_policy)

# Create context sync with Archive mode
context_sync = ContextSync(
    context_id=context_result.context_id,
    path="/tmp/archive-mode-test",
    policy=sync_policy
)
```

### Session Creation with Context Sync

```python
session_params = CreateSessionParams(
    labels={
        "example": f"archive-mode-{unique_id}",
        "type": "archive-upload-demo",
        "uploadMode": "Archive"
    },
    context_syncs=[context_sync]
)

session_result = agent_bay.create(session_params)
```

### File Operations

```python
# Write file to context path
write_result = session.file_system.write_file(file_path, file_content, mode="overwrite")

# Get file information
file_info_result = session.file_system.get_file_info(file_path)
```

### Context Information Retrieval

```python
# Get context status information
info_result = session.context.info()

# Display context status details
for index, status in enumerate(info_result.context_status_data):
    print(f"Context ID: {status.context_id}")
    print(f"Path: {status.path}")
    print(f"Status: {status.status}")
    print(f"Task Type: {status.task_type}")
```

## Running the Example

### Prerequisites

1. **Environment Setup**: Set your AgentBay API key
   ```bash
   export AGENTBAY_API_KEY="your-api-key-here"
   ```

2. **Dependencies**: Ensure you have the AgentBay SDK installed
   ```bash
   pip install wuying-agentbay-sdk-test
   ```

### Execution

```bash
# Navigate to the python directory
cd python

# Run the example
python docs/examples/archive-upload-mode-example/main.py
```

### Expected Output

The example will output detailed logs showing:

```
🚀 AgentBay Archive Upload Mode Context Sync Example
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
- [GitHub Issues](https://github.com/aliyun/wuying-agentbay-sdk/issues)
- [Documentation Home](../../../README.md)