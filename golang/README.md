# AgentBay SDK for Golang

> Execute commands, manipulate files, and run code in cloud environments

## 📦 Installation

```bash
go get github.com/aliyun/wuying-agentbay-sdk/golang/pkg/agentbay
```

## 🚀 Prerequisites

Before using the SDK, you need to:

1. Register an Alibaba Cloud account: [https://aliyun.com](https://aliyun.com)
2. Get API credentials: [AgentBay Console](https://agentbay.console.aliyun.com/service-management)
3. Set environment variable: `export AGENTBAY_API_KEY=your_api_key`

## 🚀 Quick Start
```go
package main

import (
    "fmt"
    "github.com/aliyun/wuying-agentbay-sdk/golang/pkg/agentbay"
)

func main() {
    // Create session
    client, err := agentbay.NewAgentBay("", nil)
    if err != nil {
        fmt.Printf("Initialization failed: %v\n", err)
        return
    }
    // Verified: ✓ Client initialized successfully

    result, err := client.Create(nil)
    if err != nil {
        fmt.Printf("Session creation failed: %v\n", err)
        return
    }
    // Verified: ✓ Session created with ID like "session-04bdwfj7u2a668axp"

    session := result.Session

    // Execute command
    cmdResult, err := session.Command.ExecuteCommand("ls -la")
    if err == nil {
        fmt.Printf("Command output: %s\n", cmdResult.Output)
    }
    // Verified: ✓ Command executed successfully
    // Sample output: "总计 100\ndrwxr-x--- 16 wuying wuying 4096..."

    // File operations
    session.FileSystem.WriteFile("/tmp/test.txt", "Hello World", "")
    fileResult, err := session.FileSystem.ReadFile("/tmp/test.txt")
    if err == nil {
        fmt.Printf("File content: %s\n", fileResult.Content)
    }
    // Verified: ✓ File written and read successfully
    // Output: "File content: Hello World"
}
```

## 📖 Complete Documentation

### 🆕 New Users
- [📚 Quick Start Tutorial](../docs/quickstart/README.md) - Get started in 5 minutes
- [🎯 Core Concepts](../docs/quickstart/basic-concepts.md) - Understanding cloud environments and sessions

### 🚀 Experienced Users
**Choose Your Cloud Environment:**
- 🌐 [Browser Use](../docs/guides/browser-use/README.md) - Web scraping, browser testing, form automation
- 🖥️ [Computer Use](../docs/guides/computer-use/README.md) - Windows desktop automation, UI testing
- 📱 [Mobile Use](../docs/guides/mobile-use/README.md) - Android UI testing, mobile app automation
- 💻 [CodeSpace](../docs/guides/codespace/README.md) - Code execution, development environments

**Additional Resources:**
- [📖 Feature Guides](../docs/guides/README.md) - Complete feature introduction
- [🔧 Go API Reference](docs/api/README.md) - Detailed API documentation
- [💻 Go Examples](docs/examples/README.md) - Complete example code
- [📋 Logging Configuration](../docs/guides/common-features/configuration/logging.md) - Configure logging levels and output

## 🔧 Core Features Quick Reference

### Session Management
```go
// Create session
result, _ := client.Create(nil)
session := result.Session
// Verified: ✓ Session created successfully
```

### File Operations
```go
// Read and write files
session.FileSystem.WriteFile("/path/file.txt", "content", "")
result, _ := session.FileSystem.ReadFile("/path/file.txt")
content := result.Content
// Verified: ✓ File operations work correctly
// Output: content contains the file's text content

// List directory
files, _ := session.FileSystem.ListDirectory("/path")
// Verified: ✓ Returns list of FileInfo objects
```

### Command Execution
```go
// Execute command
result, _ := session.Command.ExecuteCommand("go run script.go")
fmt.Println(result.Output)
// Verified: ✓ Command executed successfully
// Output contains the command's stdout
```

### Data Persistence
```go
// Create context
contextResult, _ := client.Context.Get("my-project", true)
context := contextResult.Context
// Verified: ✓ Context created or retrieved successfully

// Create session with context
policy := agentbay.NewSyncPolicy()
contextSync := agentbay.NewContextSync(context.ID, "/tmp/data", policy)
params := agentbay.NewCreateSessionParams().AddContextSyncConfig(contextSync)
sessionResult, _ := client.Create(params)
// Verified: ✓ Session created with context synchronization
// Data in /tmp/data will be synchronized to the context
```

## 🆘 Get Help

- [GitHub Issues](https://github.com/agentbay-ai/wuying-agentbay-sdk/issues)
- [Complete Documentation](../docs/README.md)

## 📄 License

This project is licensed under the Apache License 2.0 - see the [LICENSE](../LICENSE) file for details.
