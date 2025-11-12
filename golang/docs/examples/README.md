# Golang SDK Examples

This directory contains Golang examples demonstrating various features and capabilities of the AgentBay SDK.

## 📁 Directory Structure

The examples are organized by feature categories:

```
examples/
├── basic_usage/                   # Quick start example
├── common-features/               # Features available across all environments
│   ├── basics/                    # Essential features
│   │   ├── session_creation/      # Session lifecycle management
│   │   ├── session_params/        # Session parameter configuration
│   │   ├── command_example/       # Command execution
│   │   ├── filesystem_example/    # File operations
│   │   ├── watch_directory_example/ # Directory monitoring
│   │   ├── context_management/    # Context creation and management
│   │   ├── context_sync_example/  # Context synchronization
│   │   ├── context_sync_demo/     # Context sync demonstration
│   │   ├── data_persistence/      # Data persistence across sessions
│   │   ├── recycle_policy/        # Recycle policy configuration
│   │   ├── list_sessions/         # Session listing and filtering
│   │   └── get/                   # Session retrieval
│   └── advanced/                  # Advanced features
│       ├── agent_module/          # AI-powered automation
│       ├── vpc_session/           # Secure isolated network environments
│       └── archive-upload-mode-example/ # Archive upload mode
├── browser-use/                   # Browser automation (browser_latest)
│   └── browser/                   # Browser automation examples
├── computer-use/                  # Windows desktop automation (windows_latest)
│   ├── application_window/        # Application and window management
│   └── ui_example/                # UI automation
├── mobile-use/                    # Mobile UI automation (mobile_latest)
│   └── mobile_get_adb_url/        # ADB URL retrieval
└── codespace/                     # Code execution (code_latest)
    ├── code_example/              # Code execution example
    └── automation/                # Automation workflows
```

## 🚀 Quick Start

### Single-File Example

The fastest way to get started:

```bash
# Set your API key
export AGENTBAY_API_KEY=your_api_key_here

# Run the quick start example
cd basic_usage
go run main.go
```

This example demonstrates:
- Initializing the AgentBay client
- Creating sessions
- Basic operations (commands, file operations)
- Session cleanup

## 📚 Feature Categories

### [Common Features](common-features/)

Features available across all environment types (browser, computer, mobile, codespace).

**Basics:**
- **Session Management**: Create, configure, and manage cloud sessions
- **Command Execution**: Execute shell commands in cloud environments
- **File Operations**: Read, write, and manage files
- **Context Management**: Persistent data storage across sessions
- **Data Persistence**: Cross-session data sharing and synchronization

**Advanced:**
- **Agent Module**: AI-powered task automation with natural language
- **VPC Sessions**: Secure isolated network environments
- **Archive Upload**: Archive upload mode configuration

### [Browser Use](browser-use/)

Cloud-based browser automation with Playwright integration.

**Key Features:**
- Custom browser configuration
- Command line arguments
- Browser type selection
- Stealth mode and fingerprinting


### [Mobile Use](mobile-use/)

Android mobile UI automation for app testing.

**Key Features:**
- ADB URL retrieval
- Mobile device connection
- Remote debugging

### [CodeSpace](codespace/)

Cloud-based development environment for code execution.

**Key Features:**
- Code execution
- Automation workflows
- Shell command execution

## 📋 Prerequisites

### Basic Requirements

- Go 1.19 or later
- Valid `AGENTBAY_API_KEY` environment variable

### Installation

```bash
# Clone the repository
git clone https://github.com/aliyun/wuying-agentbay-sdk.git
cd wuying-agentbay-sdk/golang

# Install dependencies
go mod download
```

## 🎯 Running Examples

```bash
# Set your API key
export AGENTBAY_API_KEY=your_api_key_here

# Run any example
cd docs/examples/basic_usage
go run main.go

# Or run from any example directory
cd docs/examples/common-features/basics/session_creation
go run main.go
```

## 💡 Common Patterns

### Basic Session Creation

```go
package main

import (
    "context"
    "fmt"
    "os"
    
    "github.com/aliyun/wuying-agentbay-sdk/golang/pkg/agentbay"
)

func main() {
    // Initialize client
    apiKey := os.Getenv("AGENTBAY_API_KEY")
    client := agentbay.NewClient(apiKey)
    
    // Create session
    ctx := context.Background()
    params := &agentbay.CreateSessionParams{
        ImageID: "linux_latest",
    }
    
    result, err := client.Create(ctx, params)
    if err != nil {
        panic(err)
    }
    
    session := result.Session
    fmt.Printf("Session created: %s\n", session.SessionID)
    
    // Use session...
    
    // Cleanup
    defer client.Delete(ctx, session.SessionID)
}
```

### File Operations

```go
// Write file
err := session.FileSystem.WriteFile(ctx, "/tmp/test.txt", []byte("content"))

// Read file
content, err := session.FileSystem.ReadFile(ctx, "/tmp/test.txt")
if err == nil {
    fmt.Println(string(content))
}
```

### Command Execution

```go
result, err := session.Command.Execute(ctx, "ls -la")
if err == nil {
    fmt.Println(result.Output)
}
```

## 🎓 Learning Path

### For Beginners

1. Start with [basic_usage](basic_usage/)
2. Explore [Common Features - Basics](common-features/basics/)
3. Try environment-specific examples based on your use case

### For Experienced Developers

1. Review [Common Features](common-features/) for SDK capabilities
2. Jump to your specific environment:
   - [Browser Use](browser-use/) for web automation
   - [Mobile Use](mobile-use/) for mobile automation
   - [CodeSpace](codespace/) for code execution
3. Explore [Advanced Features](common-features/advanced/) for integrations

## 📖 Best Practices

1. **Always Clean Up**: Delete sessions when done to free resources
2. **Error Handling**: Always check errors before using results
3. **Context Usage**: Use context for cancellation and timeouts
4. **Resource Limits**: Be aware of concurrent session limits
5. **Defer Cleanup**: Use `defer` for session cleanup

## 🔍 Example Index

### By Use Case

**Web Automation:**
- Browser configuration: `browser-use/browser/custom_browser_config.go`
- Browser command args: `browser-use/browser/browser_command_args.go`

**Desktop Automation:**
- Application management: `computer-use/application_window/main.go`
- UI automation: `computer-use/ui_example/main.go`

**Mobile Automation:**
- ADB integration: `mobile-use/mobile_get_adb_url/main.go`

**Code Execution:**
- Code execution: `codespace/code_example/main.go`
- Automation: `codespace/automation/main.go`

**Data Management:**
- File operations: `common-features/basics/filesystem_example/main.go`
- Context management: `common-features/basics/context_management/main.go`
- Data persistence: `common-features/basics/data_persistence/main.go`

**Advanced Features:**
- AI Agent: `common-features/advanced/agent_module/main.go`
- VPC sessions: `common-features/advanced/vpc_session/main.go`

## 🆘 Troubleshooting

### Resource Creation Delay

If you see "The system is creating resources" message:
- Wait 90 seconds and retry
- This is normal for resource initialization

### API Key Issues

Ensure your API key is properly set:
```bash
export AGENTBAY_API_KEY=your_api_key_here
# Verify
echo $AGENTBAY_API_KEY
```

### Module Issues

If you get module errors:
```bash
# Ensure dependencies are installed
go mod download

# Update dependencies
go mod tidy
```

## 📚 Related Documentation

- [Golang SDK Documentation](../../)
- [API Reference](../api/)
- [Quick Start Guide](../../../docs/quickstart/README.md)
- [Feature Guides](../../../docs/guides/README.md)

## 🤝 Getting Help

- [GitHub Issues](https://github.com/aliyun/wuying-agentbay-sdk/issues)
- [Documentation](../../../docs/README.md)

---

💡 **Tip**: Start with `basic_usage/` for a quick overview, then explore category-specific examples based on your needs.

