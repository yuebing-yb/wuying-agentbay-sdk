# AgentBay SDK

> The AgentBay SDK provides a comprehensive suite of tools for efficient interaction with AgentBay cloud environments, enabling you to create and manage cloud sessions, execute commands, operate files, and interact with user interfaces.

## 📦 Installation

| Language | Install Command | Documentation |
|----------|----------------|---------------|
| Python | `pip install wuying-agentbay-sdk` | [Python Docs](python/README.md) |
| TypeScript | `npm install wuying-agentbay-sdk` | [TypeScript Docs](typescript/README.md) |
| Golang | `go get github.com/aliyun/wuying-agentbay-sdk/golang/pkg/agentbay` | [Golang Docs](golang/README.md) |

## 🚀 Prerequisites

Before using the SDK, you need to:

1. Register an Alibaba Cloud account: [https://aliyun.com](https://aliyun.com)
2. Get APIKEY credentials: [AgentBay Console](https://agentbay.console.aliyun.com/service-management)
3. Set environment variable:
   - For Linux/MacOS:
```bash
    export AGENTBAY_API_KEY=your_api_key_here
```
   - For Windows:
```cmd
    setx AGENTBAY_API_KEY your_api_key_here
```

## 🚀 Quick Start

### Python
```python
from agentbay import AgentBay

# Create session and execute command
agent_bay = AgentBay()
session_result = agent_bay.create()
session = session_result.session
result = session.command.execute_command("echo 'Hello AgentBay'")
print(result.output)  # Hello AgentBay

# Clean up
agent_bay.delete(session)
```

### TypeScript
```typescript
import { AgentBay } from 'wuying-agentbay-sdk';

// Create session and execute command
const agentBay = new AgentBay();
const sessionResult = await agentBay.create();
const session = sessionResult.session;
const result = await session.command.executeCommand("echo 'Hello AgentBay'");
console.log(result.output);  // Hello AgentBay

// Clean up
await agentBay.delete(session);
```

### Golang
```go
import "github.com/aliyun/wuying-agentbay-sdk/golang/pkg/agentbay"

// Create session and execute command
client, err := agentbay.NewAgentBay("", nil)
if err != nil {
    fmt.Printf("Failed to initialize AgentBay client: %v\n", err)
    return
}

sessionResult, err := client.Create(nil)
if err != nil {
    fmt.Printf("Failed to create session: %v\n", err)
    return
}

session := sessionResult.Session
result, err := session.Command.ExecuteCommand("echo 'Hello AgentBay'")
if err != nil {
    fmt.Printf("Failed to execute command: %v\n", err)
    return
}
fmt.Println(result.Output)  // Hello AgentBay

// Clean up
_, err = client.Delete(session, false)
if err != nil {
    fmt.Printf("Failed to delete session: %v\n", err)
    return
}
```

## 📚 Documentation

**[Complete Documentation](docs/README.md)** - Full guides, tutorials, and API references

### 👋 Choose Your Learning Path

**🆕 New Users** - If you're new to AgentBay or cloud development:
- [Quick Start Tutorial](docs/quickstart/README.md) - Get started in 5 minutes
- [Core Concepts](docs/quickstart/basic-concepts.md) - Understand cloud environments and sessions

**🚀 Experienced Users** - Already familiar with browser automation, computer use, or mobile testing:
- Choose your environment:
  - 🌐 [Browser Automation](docs/guides/browser-use/README.md) - Web scraping, testing, form filling with stealth capabilities
  - 🖥️ [Computer/Windows Automation](docs/guides/computer-use/README.md) - Desktop UI automation and window management
  - 📱 [Mobile Automation](docs/guides/mobile-use/README.md) - Android UI testing and gesture automation
  - 💻 [CodeSpace](docs/guides/codespace/README.md) - Cloud-based code execution environments
- [Feature Guides](docs/guides/README.md) - Complete feature introduction
- API Reference - Core API quick lookup
  - [Python API Reference](python/docs/api/README.md)
  - [TypeScript API Reference](typescript/docs/api/README.md)
  - [Golang API Reference](golang/docs/api/README.md)
- [Cookbook](cookbook/README.md) - Real-world examples and recipes

## 🔧 Core Features

### 🎛️ Session Management
- **Session Creation & Lifecycle** - Create, manage, and delete cloud environments
- **Environment Configuration** - Configure SDK settings, regions, and endpoints  
- **Session Monitoring** - Monitor session status and health validation

### 🛠️ Common Modules
- **Command Execution** - Execute Shell commands in cloud environments
- **File Operations** - Upload, download, and manage cloud files
- **Data Persistence** - Save and retrieve data across sessions
- **Context Management** - Synchronize data and maintain state

### 🎯 Scenario-Based Features
- **Computer Use** - General automation and desktop operations
- **Browser Use** - Web automation, scraping, and browser control  
- **CodeSpace** - Code execution and development environment
- **Mobile Use** - Mobile device simulation and control

### ♻️ RecyclePolicy Configuration

The `RecyclePolicy` defines how long context data should be retained and which paths are subject to the policy. It is used within the `SyncPolicy` when creating sessions with context synchronization.

#### Lifecycle Options

The `lifecycle` field determines the data retention period:

| Option | Retention Period | Description |
|--------|------------------|-------------|
| `LIFECYCLE_1DAY` | 1 day | Data deleted after 1 day |
| `LIFECYCLE_3DAYS` | 3 days | Data deleted after 3 days |
| `LIFECYCLE_5DAYS` | 5 days | Data deleted after 5 days |
| `LIFECYCLE_10DAYS` | 10 days | Data deleted after 10 days |
| `LIFECYCLE_15DAYS` | 15 days | Data deleted after 15 days |
| `LIFECYCLE_30DAYS` | 30 days | Data deleted after 30 days |
| `LIFECYCLE_90DAYS` | 90 days | Data deleted after 90 days |
| `LIFECYCLE_180DAYS` | 180 days | Data deleted after 180 days |
| `LIFECYCLE_360DAYS` | 360 days | Data deleted after 360 days |
| `LIFECYCLE_FOREVER` | Permanent | Data never deleted (default) |

**Default Value:** `LIFECYCLE_FOREVER`

#### Paths Configuration

The `paths` field specifies which directories or files should be subject to the recycle policy:

**Rules:**
- Must use exact directory/file paths
- **Wildcard patterns (`* ? [ ]`) are NOT supported**
- Empty string `""` means apply to all paths in the context
- Multiple paths can be specified as a list

**Default Value:** `[""]` (applies to all paths)

#### Usage Examples

##### Python
```python
from agentbay import AgentBay
from agentbay.session_params import CreateSessionParams
from agentbay.context_sync import ContextSync, SyncPolicy, RecyclePolicy, Lifecycle

# Create recycle policy with 30-day retention
recycle_policy = RecyclePolicy(
    lifecycle=Lifecycle.LIFECYCLE_30DAYS,
    paths=[""]  # Apply to all paths
)

# Create session with custom recycle policy
sync_policy = SyncPolicy(
    recycle_policy=recycle_policy
)
context_sync = ContextSync(
    context_id="my-project-context",
    path="/tmp/data",
    policy=sync_policy
)
params = CreateSessionParams(context_syncs=[context_sync])

agent_bay = AgentBay()
result = agent_bay.create(params)
```

##### TypeScript
```typescript
import { AgentBay, CreateSessionParams, ContextSync, SyncPolicy, RecyclePolicy, Lifecycle } from 'wuying-agentbay-sdk';

// Create recycle policy with 30-day retention
const recyclePolicy = new RecyclePolicy({
    lifecycle: Lifecycle.LIFECYCLE_30DAYS,
    paths: [""]  // Apply to all paths
});

// Create session with custom recycle policy
const syncPolicy = new SyncPolicy({
    recyclePolicy: recyclePolicy
});
const contextSync = new ContextSync({
    contextId: "my-project-context",
    path: "/tmp/data",
    policy: syncPolicy
});
const params = new CreateSessionParams({
    contextSyncs: [contextSync]
});

const agentBay = new AgentBay();
const result = await agentBay.create(params);
```

##### Golang
```go
import "github.com/aliyun/wuying-agentbay-sdk/golang/pkg/agentbay"

// Create recycle policy with 30-day retention
recyclePolicy := agentbay.NewRecyclePolicy().
    SetLifecycle(agentbay.LIFECYCLE_30DAYS).
    SetPaths([]string{""})  // Apply to all paths

// Create session with custom recycle policy
syncPolicy := agentbay.NewSyncPolicy().SetRecyclePolicy(recyclePolicy)
contextSync := agentbay.NewContextSync("my-project-context", "/tmp/data", syncPolicy)
params := agentbay.NewCreateSessionParams().AddContextSyncConfig(contextSync)

client, _ := agentbay.NewAgentBay("", nil)
result, _ := client.Create(params)
```

##### Best Practices

1. **Use appropriate retention periods**: Choose lifecycle options based on your data importance and storage costs
2. **Specify exact paths**: Use precise directory paths instead of wildcards for better control
3. **Separate policies for different data types**: Use different recycle policies for temporary vs. persistent data
4. **Monitor storage usage**: Regularly review and adjust lifecycle settings to optimize storage costs
5. **Test path validation**: Ensure your paths don't contain wildcard characters (`* ? [ ]`) as they are not supported

## 🆘 Get Help

- [GitHub Issues](https://github.com/aliyun/wuying-agentbay-sdk/issues)

## 📄 License

This project is licensed under the Apache License 2.0 - see the [LICENSE](LICENSE) file for details.