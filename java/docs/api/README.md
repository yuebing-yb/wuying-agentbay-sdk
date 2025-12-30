# AgentBay Java SDK API Reference

Complete API documentation for all classes and methods in the AgentBay Java SDK.

## 📖 Quick Links

| Category | APIs | Description |
|----------|------|-------------|
| **Core** | [AgentBay](common-features/basics/agentbay.md), [Session](common-features/basics/session.md) | Main client and session management |
| **File Operations** | [FileSystem](common-features/basics/filesystem.md), [Command](common-features/basics/command.md) | File and command operations |
| **Data Persistence** | [Context](common-features/basics/context.md), [ContextSync](common-features/basics/context-sync.md) | Context management and synchronization |
| **Browser** | [Browser](browser-use/browser.md) | Web automation with Playwright |
| **Mobile** | [Mobile](mobile-use/mobile.md), [MobileSimulate](mobile-use/mobile-simulate.md) | Mobile device automation and simulation |
| **Computer** | [Computer](computer-use/computer.md) | Windows desktop automation |
| **Code Execution** | [Code](codespace/code.md) | Execute Python, JavaScript code |
| **Storage** | [OSS](common-features/advanced/oss.md), [Network](common-features/advanced/network.md) | Object storage and network integration |
| **Configuration** | [Session Params](common-features/basics/session-params.md) | Session configuration parameters |

## 📚 API Documentation by Category

### Core APIs

**AgentBay Client:**
- [AgentBay](common-features/basics/agentbay.md) - `com.aliyun.agentbay.AgentBay`
  - Main client class for creating and managing sessions
  - Methods: `create()`, `delete()`, `list()`, `get()`

**Session Management:**
- [Session](common-features/basics/session.md) - `com.aliyun.agentbay.session.Session`
  - Represents a cloud environment instance
  - Access to all session capabilities (command, filesystem, browser, etc.)

### File and Command Operations

- [Command](common-features/basics/command.md) - `com.aliyun.agentbay.command.Command`
  - Execute shell commands in sessions
  - Methods: `executeCommand(String command)`, `executeCommand(String command, int timeout)`

- [FileSystem](common-features/basics/filesystem.md) - `com.aliyun.agentbay.filesystem.FileSystem`
  - Read, write, search, and manage files
  - Methods: `readFile()`, `writeFile()`, `listDirectory()`, `searchFiles()`, `editFile()`

### Data Persistence

- [Context](common-features/basics/context.md) - `com.aliyun.agentbay.context.Context`
  - Manage persistent contexts for data storage
  - Methods: `get()`, `delete()`, `list()`, `sync()`, `syncAndWait()`

- [ContextSync](common-features/basics/context-sync.md) - `com.aliyun.agentbay.context.ContextSync`
  - Configure context synchronization policies
  - Static methods: `create()`, `defaultPolicy()`

### Browser Automation

- [Browser](browser-use/browser.md) - `com.aliyun.agentbay.browser.Browser`
  - Initialize and control browsers
  - Playwright integration for web automation
  - Methods: `init()`, `getBrowser()`, `getCdpUrl()`

### Mobile Automation

- [Mobile](mobile-use/mobile.md) - `com.aliyun.agentbay.mobile.Mobile`
  - Mobile device UI automation
  - Methods: `tap()`, `swipe()`, `inputText()`, `sendKey()`, `screenshot()`, `startApp()`, `stopApp()`

- [MobileSimulate](mobile-use/mobile-simulate.md) - `com.aliyun.agentbay.mobile.MobileSimulate`
  - Simulate different mobile devices
  - Methods: `uploadMobileInfo()`, `setSimulateMode()`

### Computer/Desktop Automation

- [Computer](computer-use/computer.md) - `com.aliyun.agentbay.computer.Computer`
  - Windows desktop application management
  - Methods: `startApp()`, `stopAppByPID()`, `stopAppByPName()`, `listVisibleApps()`, `getInstalledApps()`

### Code Execution

- [Code](codespace/code.md) - `com.aliyun.agentbay.code.Code`
  - Execute Python, JavaScript, R, Java, and other languages
  - Methods: `runCode(String code, String language)`, `runCode(String code, String language, int timeout)`, `execute(String code, String language)`

### Storage and Network

- [OSS](common-features/advanced/oss.md) - `com.aliyun.agentbay.oss.Oss`
  - Alibaba Cloud Object Storage integration
  - Methods: `init()`, `upload()`, `download()`

- [Network](common-features/advanced/network.md) - `com.aliyun.agentbay.network.Network`
  - Network configuration and management
  - Methods for VPC and network setup

### Configuration

- [Session Params](common-features/basics/session-params.md) - `com.aliyun.agentbay.session.CreateSessionParams`
  - Configure session creation parameters
  - Properties: `imageId`, `labels`, `contextSyncs`, `browserContext`, `extraConfigs`, `policyId`, `enableBrowserReplay`

## 🎯 Quick Start by Use Case

### File Operations
```java
AgentBay agentBay = new AgentBay();
Session session = agentBay.create().getSession();

// Write and read files
session.getFileSystem().writeFile("/tmp/test.txt", "Hello");
String content = session.getFileSystem().readFile("/tmp/test.txt");
```
📖 See: [FileSystem API](common-features/basics/filesystem.md)

### Command Execution
```java
CommandResult result = session.getCommand().executeCommand("ls -la");
System.out.println(result.getOutput());
```
📖 See: [Command API](common-features/basics/command.md)

### Browser Automation
```java
session.getBrowser().init();
Browser browser = session.getBrowser().getBrowser();
Page page = browser.newContext().newPage();
page.navigate("https://example.com");
```
📖 See: [Browser API](browser-use/browser.md)

### Mobile Automation
```java
session.getMobile().tap(500, 800);
session.getMobile().swipe(500, 1000, 500, 500);
session.getMobile().inputText("Hello");
```
📖 See: [Mobile API](mobile-use/mobile.md)

### Data Persistence
```java
ContextResult contextResult = agentBay.getContext().get("my-context", true);
ContextSync sync = ContextSync.create(contextResult.getContext().getId(),
    "/tmp/data", SyncPolicy.defaultPolicy());

CreateSessionParams params = new CreateSessionParams();
params.setContextSyncs(Arrays.asList(sync));
Session session = agentBay.create(params).getSession();
```
📖 See: [Context API](common-features/basics/context.md), [ContextSync API](common-features/basics/context-sync.md)

## 📦 Package Structure

```
com.aliyun.agentbay
├── AgentBay                    # Main client
├── session
│   ├── Session                 # Session management
│   └── CreateSessionParams     # Session configuration
├── command
│   └── Command                 # Command execution
├── filesystem
│   └── FileSystem              # File operations
├── context
│   ├── Context                 # Context management
│   └── ContextSync             # Context synchronization
├── browser
│   └── Browser                 # Browser automation
├── mobile
│   ├── Mobile                  # Mobile automation
│   └── MobileSimulate          # Device simulation
├── computer
│   └── Computer                # Desktop automation
├── code
│   └── Code                    # Code execution
├── oss
│   └── Oss                     # Object storage
├── network
│   └── Network                 # Network management
└── model
    ├── ExtraConfigs            # Advanced configs
    └── Result classes          # Result types
```

## 🔍 Finding the Right API

**I want to...**
- **Create a session** → [AgentBay.create()](common-features/basics/agentbay.md)
- **Execute commands** → [Command.executeCommand()](common-features/basics/command.md)
- **Read/write files** → [FileSystem](common-features/basics/filesystem.md)
- **Persist data** → [Context](common-features/basics/context.md) + [ContextSync](common-features/basics/context-sync.md)
- **Automate browser** → [Browser](browser-use/browser.md)
- **Control mobile device** → [Mobile](mobile-use/mobile.md)
- **Manage desktop apps** → [Computer](computer-use/computer.md)
- **Run code** → [Code.runCode()](codespace/code.md)
- **Configure session** → [Session Params](common-features/basics/session-params.md)

## 📖 Related Documentation

- [Examples](../examples/README.md) - Practical code examples
- [Guides](../guides/README.md) - Feature guides and tutorials
- [Java README](../../README.md) - SDK overview and quick start
- [Main Documentation](../../../docs/README.md) - Platform documentation

## 🔄 Documentation Maintenance

This documentation is maintained manually. If you notice any discrepancies with the actual API implementation, please:
1. Report an issue on [GitHub Issues](https://github.com/aliyun/wuying-agentbay-sdk/issues)
2. Submit a pull request with corrections

## 💡 Tips

- All methods return Result objects - always check `result.isSuccess()` before accessing data
- Sessions must be explicitly deleted with `session.delete()` or `agentBay.delete(session)`
- Use try-finally blocks to ensure proper resource cleanup
- Context synchronization is asynchronous - use `syncAndWait()` for blocking behavior

