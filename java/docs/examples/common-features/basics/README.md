# Common Features - Basics Examples

This directory contains Java examples demonstrating basic features of the AgentBay SDK.

## Examples

### 1. FileSystemExample.java
**Source**: [`../../../../agentbay/src/main/java/com/aliyun/agentbay/examples/FileSystemExample.java`](../../../../agentbay/src/main/java/com/aliyun/agentbay/examples/FileSystemExample.java)

Demonstrates comprehensive file system operations:
- Reading and writing files
- Directory listing and operations
- File information retrieval
- File editing and searching
- Multiple file operations
- Large file handling

**Key features demonstrated:**
```java
// Write a file
session.getFileSystem().writeFile("/tmp/test.txt", "Hello, World!");

// Read a file
String content = session.getFileSystem().readFile("/tmp/test.txt");

// List directory
ListDirectoryResult result = session.getFileSystem().listDirectory("/tmp");

// Edit file
session.getFileSystem().editFile("/tmp/test.txt", "old", "new");

// Search files
SearchFilesResult searchResult = session.getFileSystem().searchFiles(
    "/tmp", "*.txt", false
);
```

### 2. ContextSyncLifecycleExample.java
**Source**: [`../../../../agentbay/src/main/java/com/aliyun/agentbay/examples/ContextSyncLifecycleExample.java`](../../../../agentbay/src/main/java/com/aliyun/agentbay/examples/ContextSyncLifecycleExample.java)

Complete lifecycle management of context synchronization:
- Creating and managing contexts
- Synchronizing data across sessions
- Context lifecycle operations
- Data persistence patterns

**Key features demonstrated:**
```java
// Get or create a context
ContextResult contextResult = agentBay.getContext().get("my-context", true);

// Create context sync configuration
ContextSync sync = ContextSync.create(
    contextResult.getContext().getId(),
    "/tmp/data",
    SyncPolicy.defaultPolicy()
);

// Use in session
CreateSessionParams params = new CreateSessionParams();
params.setContextSyncs(Arrays.asList(sync));
Session session = agentBay.create(params).getSession();
```

### 3. SessionConfigurationExample.java
**Source**: [`../../../../agentbay/src/main/java/com/aliyun/agentbay/examples/SessionConfigurationExample.java`](../../../../agentbay/src/main/java/com/aliyun/agentbay/examples/SessionConfigurationExample.java)

Session creation and configuration patterns:
- Creating sessions with custom parameters
- Image selection and configuration
- Label management
- Session lifecycle management

**Key features demonstrated:**
```java
CreateSessionParams params = new CreateSessionParams();
params.setImageId("linux_latest");

Map<String, String> labels = new HashMap<>();
labels.put("project", "my-project");
params.setLabels(labels);

SessionResult result = agentBay.create(params);
```

### 4. LabelManagementExample.java
**Source**: [`../../../../agentbay/src/main/java/com/aliyun/agentbay/examples/LabelManagementExample.java`](../../../../agentbay/src/main/java/com/aliyun/agentbay/examples/LabelManagementExample.java)

Session labeling and filtering:
- Adding labels to sessions
- Filtering sessions by labels
- Label management best practices

### 5. ListSessionsExample.java
**Source**: [`../../../../agentbay/src/main/java/com/aliyun/agentbay/examples/ListSessionsExample.java`](../../../../agentbay/src/main/java/com/aliyun/agentbay/examples/ListSessionsExample.java)

Listing and managing multiple sessions:
- Listing all sessions
- Filtering by labels
- Pagination handling

### 6. DeleteFileExample.java
**Source**: [`../../../../agentbay/src/main/java/com/aliyun/agentbay/examples/DeleteFileExample.java`](../../../../agentbay/src/main/java/com/aliyun/agentbay/examples/DeleteFileExample.java)

File deletion operations:
- Single file deletion
- Directory deletion
- Error handling for file operations

### 7. FileTransferExample.java
**Source**: [`../../../../agentbay/src/main/java/com/aliyun/agentbay/examples/FileTransferExample.java`](../../../../agentbay/src/main/java/com/aliyun/agentbay/examples/FileTransferExample.java)

File upload and download:
- Uploading local files to session
- Downloading files from session
- Archive mode file transfer

## Running the Examples

### Prerequisites

1. Set your API key:
```bash
export AGENTBAY_API_KEY=your_api_key_here
```

2. Make sure you have the AgentBay SDK dependency in your project:
```xml
<dependency>
    <groupId>com.aliyun</groupId>
    <artifactId>agentbay</artifactId>
    <version>latest</version>
</dependency>
```

### Running from Source

Navigate to the SDK root directory and run:

```bash
cd java/agentbay
mvn compile exec:java -Dexec.mainClass="com.aliyun.agentbay.examples.FileSystemExample"
mvn compile exec:java -Dexec.mainClass="com.aliyun.agentbay.examples.ContextSyncLifecycleExample"
mvn compile exec:java -Dexec.mainClass="com.aliyun.agentbay.examples.SessionConfigurationExample"
```

Or compile and run directly:
```bash
cd java/agentbay/src/main/java
javac -cp "path/to/agentbay.jar" com/aliyun/agentbay/examples/FileSystemExample.java
java -cp ".:path/to/agentbay.jar" com.aliyun.agentbay.examples.FileSystemExample
```

## Common Patterns

### Session Creation and Cleanup
```java
AgentBay agentBay = new AgentBay();
Session session = null;

try {
    SessionResult result = agentBay.create();
    session = result.getSession();

    // Use session

} finally {
    if (session != null) {
        session.delete();
    }
}
```

### Error Handling
```java
try {
    FileReadResult result = session.getFileSystem().readFile("/path/to/file");
    if (result.isSuccess()) {
        String content = result.getContent();
        // Process content
    } else {
        System.err.println("Error: " + result.getMessage());
    }
} catch (AgentBayException e) {
    System.err.println("Exception: " + e.getMessage());
}
```

## Related Documentation

- [FileSystem API](../../../api/common-features/basics/filesystem.md)
- [Context API](../../../api/common-features/basics/context.md)
- [Session API](../../../api/common-features/basics/session.md)

## Troubleshooting

**Session creation fails:**
- Verify API key is set correctly
- Check network connectivity
- Ensure sufficient quota

**File operations fail:**
- Check file paths (must be absolute in session)
- Verify file permissions
- Ensure session is active

**Context sync not working:**
- Wait for sync to complete with `syncAndWait()`
- Check context exists and is accessible
- Verify sync policy configuration
