# Context Sync Best Practices

This guide explains how to use Context Sync effectively in the AgentBay SDK, helping you implement efficient and reliable data persistence across sessions.

## Overview

Context Sync is the core feature for data persistence in the AgentBay SDK. It allows you to automatically synchronize files from your session to cloud storage and restore them in new sessions.

## Core Concepts

### The Relationship Between Context, ContextSync, and Session

```
Context (Persistent Storage)    ContextSync (Sync Config)        Session (Execution Environment)
┌─────────────────┐            ┌────────────────────┐            ┌─────────────────┐
│ ID: SdkCtx-xxx  │───────────►│ ContextID          │───────────►│ Mount Path      │
│ Name: my-ctx    │            │ Path: /home/wuying │            │ /home/wuying    │
│ Cloud Storage   │            │ Policy: Sync Rules │            │ in Session      │
└─────────────────┘            └────────────────────┘            └─────────────────┘
```

## Best Practices

### 1. Use Meaningful Names When Creating Contexts

```go
// ✅ Recommended: Use meaningful, identifiable names
contextResult, err := ab.Context.Get("project-alpha-workspace", true)
contextResult, err := ab.Context.Get("user-alice-config", true)

// ❌ Avoid: Using random or meaningless names
contextResult, err := ab.Context.Get("ctx-123", true)
contextResult, err := ab.Context.Get("test", true)
```

> **Important Note**: The same context cannot be used across different API keys or regions. Even if you use the same context name with a different API key or region, you will get a different context.

### 2. Configure Sync Policies Appropriately

#### Standard Workflow Configuration (Recommended)

Suitable for most scenarios, automatically downloads and uploads data:

```go
// Standard sync policy - Auto download and upload
syncPolicy := &agentbay.SyncPolicy{
    UploadPolicy: &agentbay.UploadPolicy{
        AutoUpload:     true,
        UploadStrategy: agentbay.UploadBeforeResourceRelease,
        UploadMode:     agentbay.UploadModeFile,
    },
    DownloadPolicy: &agentbay.DownloadPolicy{
        AutoDownload:     true,
        DownloadStrategy: agentbay.DownloadAsync,
    },
    DeletePolicy: &agentbay.DeletePolicy{
        SyncLocalFile: true,
    },
}
```

#### Large File Scenario Configuration

When syncing large files or many files, use compression mode:

```go
// Large file scenario - Use Archive compression mode
syncPolicy := &agentbay.SyncPolicy{
    UploadPolicy: &agentbay.UploadPolicy{
        AutoUpload:     true,
        UploadStrategy: agentbay.UploadBeforeResourceRelease,
        UploadMode:     agentbay.UploadModeArchive, // Enable compression on upload
    },
    ExtractPolicy: &agentbay.ExtractPolicy{
        Extract:                true,  // Auto-extract on download
        DeleteSrcFile:          true,
        ExtractToCurrentFolder: true,
    },
}
```

> **Important Note**: 
> - If files in your persistence directory continuously grow in quantity and size, enable compression mode from the start
> - Switching between compression and non-compression modes is not currently supported; evaluate your use case before initialization

#### Read-Only Data Scenario

When a session only needs to read data without writing back:

```go
// Read-only scenario - Download only, no upload
syncPolicy := &agentbay.SyncPolicy{
    UploadPolicy: &agentbay.UploadPolicy{
        AutoUpload: false,
    },
    DownloadPolicy: &agentbay.DownloadPolicy{
        AutoDownload:     true,
        DownloadStrategy: agentbay.DownloadAsync,
    },
}
```

### 3. Use Whitelists to Control Sync Scope

Only sync necessary directories, exclude unnecessary files:

```go
// Use whitelist for precise sync scope control
bwList := &agentbay.BWList{
    WhiteLists: []*agentbay.WhiteList{
        {
            Path:         "/src",           // Sync src directory only
            ExcludePaths: []string{"/node_modules", "/dist"}, // Exclude build artifacts
        },
        {
            Path: "/config", // Sync config directory
        },
    },
}

syncPolicy := &agentbay.SyncPolicy{
    UploadPolicy:   uploadPolicy,
    DownloadPolicy: downloadPolicy,
    BWList:         bwList,
}
```

> **Important Note**:
> - Whitelist paths are relative to the mount point
> - Wildcard patterns (like `*.json`, `/data/*`) are not supported
> - Use exact directory paths

### 4. Select Mount Paths Correctly

```go
// ✅ Recommended: Use directories with write permissions
// Linux environment
contextSync, _ := agentbay.NewContextSync(context.ID, "/home/wuying", syncPolicy)
contextSync, _ := agentbay.NewContextSync(context.ID, "/tmp/workspace", syncPolicy)

// Windows environment
contextSync, _ := agentbay.NewContextSync(context.ID, "C:\\Users\\Administrator\\Downloads", syncPolicy)

// ❌ Avoid: System directories or directories without permissions
contextSync, _ := agentbay.NewContextSync(context.ID, "/workspace", syncPolicy)  // May lack permissions
contextSync, _ := agentbay.NewContextSync(context.ID, "/opt", syncPolicy)        // System directory
```

### 5. Ensure Data Sync Completes When Deleting Sessions

```go
// ✅ Recommended: Use AutoUpload=true to ensure full sync before session release
syncPolicy := &agentbay.SyncPolicy{
    UploadPolicy: &agentbay.UploadPolicy{
        AutoUpload: true,
    },
}
```

### 6. File Expiration Mechanism

```go
// Configure file auto-expiration policy
syncPolicy := &agentbay.SyncPolicy{
    RecyclePolicy: &agentbay.RecyclePolicy{
        Lifecycle: agentbay.Lifecycle30Days, // Auto-expire files unmodified for 30 days
        Paths:     []string{""}, // Scope of expiration (subdirectories of sync path); applies to entire sync directory if not configured
    },
}
```

## Complete Examples

### Scenario 1: Standard Workflow 📝

**Use Cases**:
- Persist dev environment configs (IDE settings, environment variables, packages)
- Sync small projects (documents, configs, limited code)
- Save user preferences

**Characteristics**: Few files, small individual size, frequent read/write

#### Golang

```go
package main

import (
    "fmt"
    "log"
    "github.com/aliyun/wuying-agentbay-sdk/golang/pkg/agentbay"
)

func main() {
    // 1. Initialize client
    ab, err := agentbay.NewAgentBay("your-api-key")
    if err != nil {
        log.Fatalf("Failed to create AgentBay client: %v", err)
    }

    // 2. Create or get Context
    contextResult, err := ab.Context.Get("my-project-workspace", true)
    if err != nil {
        log.Fatalf("Error getting context: %v", err)
    }
    context := contextResult.Context
    fmt.Printf("Context: %s (ID: %s)\n", context.Name, context.ID)

    // 3. Configure sync policy - Standard mode
    syncPolicy := &agentbay.SyncPolicy{
        UploadPolicy: &agentbay.UploadPolicy{
            AutoUpload:     true,
            UploadStrategy: agentbay.UploadBeforeResourceRelease,
            UploadMode:     agentbay.UploadModeFile,  // File mode for small files
        },
        DownloadPolicy: &agentbay.DownloadPolicy{
            AutoDownload:     true,
            DownloadStrategy: agentbay.DownloadAsync,
        },
        DeletePolicy: &agentbay.DeletePolicy{
            SyncLocalFile: true,
        },
    }

    // 4. Create ContextSync config
    contextSync, _ := agentbay.NewContextSync(context.ID, "/home/wuying/workspace", syncPolicy)

    // 5. Create session
    sessionParams := agentbay.NewCreateSessionParams()
    sessionParams.AddContextSyncConfig(contextSync)
    sessionParams.WithImageId("linux_latest")

    sessionResult, err := ab.Create(sessionParams)
    if err != nil {
        log.Fatalf("Error creating session: %v", err)
    }
    session := sessionResult.Session
    fmt.Printf("Session created: %s\n", session.SessionID)

    // 6. Work in the session...

    // 7. Delete session (data syncs automatically)
    ab.Delete(session, true)
}
```

#### Python

```python
from agentbay import (
    AgentBay, CreateSessionParams, ContextSync,
    SyncPolicy, UploadPolicy, DownloadPolicy, DeletePolicy,
    UploadMode, UploadStrategy, DownloadStrategy,
)

# 1. Initialize client
ab = AgentBay(api_key="your-api-key")

# 2. Create or get Context
context = ab.context.get("my-project-workspace", create=True).context

# 3. Configure sync policy - Standard mode
sync_policy = SyncPolicy(
    upload_policy=UploadPolicy(
        auto_upload=True,
        upload_strategy=UploadStrategy.BEFORE_RESOURCE_RELEASE,
        upload_mode=UploadMode.FILE,  # File mode for small files
    ),
    download_policy=DownloadPolicy(
        auto_download=True,
        download_strategy=DownloadStrategy.ASYNC,
    ),
    delete_policy=DeletePolicy(sync_local_file=True),
)

# 4. Create ContextSync config
context_sync = ContextSync.new(context.id, "/home/wuying/workspace", sync_policy)

# 5. Create session
session = ab.create(CreateSessionParams(
    image_id="linux_latest",
    context_syncs=[context_sync],
)).session

# 6. Work in the session...

# 7. Delete session (data syncs automatically)
ab.delete(session, sync_context=True)
```

#### TypeScript

```typescript
import {
  AgentBay, CreateSessionParams, ContextSync,
  SyncPolicy, UploadMode, UploadStrategy, DownloadStrategy,
} from "wuying-agentbay-sdk";

async function main() {
  // 1. Initialize client
  const ab = new AgentBay({ apiKey: "your-api-key" });

  // 2. Create or get Context
  const context = (await ab.context.get("my-project-workspace", true)).context!;

  // 3. Configure sync policy - Standard mode
  const syncPolicy: SyncPolicy = {
    uploadPolicy: {
      autoUpload: true,
      uploadStrategy: UploadStrategy.BEFORE_RESOURCE_RELEASE,
      uploadMode: UploadMode.FILE,  // File mode for small files
    },
    downloadPolicy: {
      autoDownload: true,
      downloadStrategy: DownloadStrategy.ASYNC,
    },
    deletePolicy: { syncLocalFile: true },
  };

  // 4. Create ContextSync config
  const contextSync = ContextSync.new(context.id, "/home/wuying/workspace", syncPolicy);

  // 5. Create session
  const sessionParams = new CreateSessionParams();
  sessionParams.addContextSyncConfig(contextSync);
  sessionParams.withImageId("linux_latest");
  const session = (await ab.create(sessionParams)).session!;

  // 6. Work in the session...

  // 7. Delete session (data syncs automatically)
  await ab.delete(session, true);
}

main().catch(console.error);
```

---

### Scenario 2: Large File Compression Mode 📦

**Use Cases**:
- Persist ML model files (weights, training datasets)
- Sync large code repos (many sources, assets)
- Archive log files (app logs, system logs)
- Persist browser user data (cache, cookies, history)
- Persist mobile app configuration (login state, app cache)

**Characteristics**: Many files, complex directory structure, large total size, high transfer efficiency needed

**Important Notes**:
- Compression and non-compression modes cannot be dynamically switched; evaluate your use case before initialization
- If files continuously grow in quantity and size, enable compression mode from the start

#### Golang

```go
package main

import (
    "fmt"
    "log"
    "github.com/aliyun/wuying-agentbay-sdk/golang/pkg/agentbay"
)

func main() {
    ab, err := agentbay.NewAgentBay("your-api-key")
    if err != nil {
        log.Fatalf("Failed to create AgentBay client: %v", err)
    }

    // Create Context for storing browser user data
    contextResult, err := ab.Context.Get("browser-user-data", true)
    if err != nil {
        log.Fatalf("Error getting context: %v", err)
    }
    context := contextResult.Context

    // Configure compression mode sync policy
    syncPolicy := &agentbay.SyncPolicy{
        UploadPolicy: &agentbay.UploadPolicy{
            AutoUpload:     true,
            UploadStrategy: agentbay.UploadBeforeResourceRelease,
            UploadMode:     agentbay.UploadModeArchive,  // Compression mode for many files
        },
        DownloadPolicy: &agentbay.DownloadPolicy{
            AutoDownload:     true,
            DownloadStrategy: agentbay.DownloadAsync,
        },
        ExtractPolicy: &agentbay.ExtractPolicy{
            Extract:                true,   // Auto-extract on download
            DeleteSrcFile:          true,   // Delete archive after extraction
            ExtractToCurrentFolder: true,   // Extract to current directory
        },
        DeletePolicy: &agentbay.DeletePolicy{
            SyncLocalFile: true,
        },
    }

    // Mount to browser user data directory
    contextSync, _ := agentbay.NewContextSync(
        context.ID,
        "/home/wuying/.config/google-chrome",  // Chrome user data directory
        syncPolicy,
    )

    sessionParams := agentbay.NewCreateSessionParams()
    sessionParams.AddContextSyncConfig(contextSync)
    sessionParams.WithImageId("linux_latest")

    sessionResult, err := ab.Create(sessionParams)
    if err != nil {
        log.Fatalf("Error creating session: %v", err)
    }
    session := sessionResult.Session
    fmt.Printf("Session created: %s\n", session.SessionID)

    // Browser operations complete, user data auto-compresses on upload
    // ...

    // Delete session, triggering data compression and upload
    deleteResult, err := ab.Delete(session, true)
    if err != nil {
        log.Printf("Error: %v", err)
    } else {
        fmt.Printf("Session deleted, browser data archived (RequestID: %s)\n", deleteResult.RequestID)
    }
}
```

#### Python

```python
from agentbay import (
    AgentBay, CreateSessionParams, ContextSync,
    SyncPolicy, UploadPolicy, DownloadPolicy, DeletePolicy, ExtractPolicy,
    UploadMode, UploadStrategy, DownloadStrategy,
)

ab = AgentBay(api_key="your-api-key")

# Create Context for storing browser user data
context = ab.context.get("browser-user-data", create=True).context

# Configure compression mode sync policy
sync_policy = SyncPolicy(
    upload_policy=UploadPolicy(
        auto_upload=True,
        upload_strategy=UploadStrategy.BEFORE_RESOURCE_RELEASE,
        upload_mode=UploadMode.ARCHIVE,  # Compression mode for many files
    ),
    download_policy=DownloadPolicy(
        auto_download=True,
        download_strategy=DownloadStrategy.ASYNC,
    ),
    extract_policy=ExtractPolicy(
        extract=True,                   # Auto-extract on download
        delete_src_file=True,           # Delete archive after extraction
        extract_to_current_folder=True, # Extract to current directory
    ),
    delete_policy=DeletePolicy(sync_local_file=True),
)

# Mount to browser user data directory
context_sync = ContextSync.new(
    context.id,
    "/home/wuying/.config/google-chrome",  # Chrome user data directory
    sync_policy,
)

session = ab.create(CreateSessionParams(
    image_id="linux_latest",
    context_syncs=[context_sync],
)).session

# Browser operations complete, user data auto-compresses on upload
# ...

# Delete session, triggering data compression and upload
ab.delete(session, sync_context=True)
print("Session deleted, browser data archived")
```

#### TypeScript

```typescript
import {
  AgentBay, CreateSessionParams, ContextSync,
  SyncPolicy, UploadMode, UploadStrategy, DownloadStrategy,
} from "wuying-agentbay-sdk";

async function main() {
  const ab = new AgentBay({ apiKey: "your-api-key" });

  // Create Context for storing browser user data
  const context = (await ab.context.get("browser-user-data", true)).context!;

  // Configure compression mode sync policy
  const syncPolicy: SyncPolicy = {
    uploadPolicy: {
      autoUpload: true,
      uploadStrategy: UploadStrategy.BEFORE_RESOURCE_RELEASE,
      uploadMode: UploadMode.ARCHIVE,  // Compression mode for many files
    },
    downloadPolicy: {
      autoDownload: true,
      downloadStrategy: DownloadStrategy.ASYNC,
    },
    extractPolicy: {
      extract: true,                  // Auto-extract on download
      deleteSrcFile: true,            // Delete archive after extraction
      extractToCurrentFolder: true,   // Extract to current directory
    },
    deletePolicy: { syncLocalFile: true },
  };

  // Mount to browser user data directory
  const contextSync = ContextSync.new(
    context.id,
    "/home/wuying/.config/google-chrome",  // Chrome user data directory
    syncPolicy,
  );

  const sessionParams = new CreateSessionParams();
  sessionParams.addContextSyncConfig(contextSync);
  sessionParams.withImageId("linux_latest");
  const session = (await ab.create(sessionParams)).session!;

  // Browser operations complete, user data auto-compresses on upload
  // ...

  // Delete session, triggering data compression and upload
  await ab.delete(session, true);
  console.log("Session deleted, browser data archived");
}

main().catch(console.error);
```

## FAQ & Troubleshooting

### Issue 1: Data Not Persisting 💾

**Symptom**: Files don't exist when creating a new session.

**Cause**: Data wasn't fully synced before session deletion.

**Solution**:
```go
// Ensure sync_context=true
ab.Delete(session, true)

// Or manually sync before deletion
session.Context.Sync()
ab.Delete(session, false)
```

### Issue 2: Permission Denied Error ❌

**Symptom**: Permission error when creating files.

**Solution**: Use a directory with write permissions as the mount point:
```go
// Linux
contextSync, _ := agentbay.NewContextSync(context.ID, "/home/wuying", syncPolicy)

// Windows  
contextSync, _ := agentbay.NewContextSync(context.ID, "C:\\Users\\Administrator\\Downloads", syncPolicy)
```

### Issue 3: Whitelist Configuration Not Working 🔍

**Symptom**: Files not syncing despite whitelist configuration.

**Cause**: Whitelist paths use wildcards or absolute paths.

**Solution**:
```go
// ❌ Wrong: Wildcard usage
WhiteList{Path: "*.json"}
WhiteList{Path: "/src/*"}

// ❌ Wrong: Absolute paths
WhiteList{Path: "/home/wuying/src"} // When mount point is /home/wuying

// ✅ Correct: Relative paths
WhiteList{Path: "/src"}  // Relative to mount point
WhiteList{Path: "/config"}
```

## Related Resources

- [Data Persistence Guide](../basics/data-persistence.md)
- [Session Management](../basics/session-management.md)
- [Cross-Platform Persistence](./cross-platform-persistence.md)
