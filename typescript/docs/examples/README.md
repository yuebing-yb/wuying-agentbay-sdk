# TypeScript SDK Examples

This directory contains TypeScript examples demonstrating various features and capabilities of the AgentBay SDK.

## 📁 Directory Structure

The examples are organized by feature categories:

```
examples/
├── basic-usage.ts                 # Quick start single-file example
├── common-features/               # Features available across all environments
│   ├── basics/                    # Essential features
│   │   ├── session-creation/      # Session lifecycle management
│   │   ├── command-example/       # Command execution
│   │   ├── filesystem-example/    # File operations and monitoring
│   │   ├── context-management/    # Context creation and management
│   │   ├── data-persistence/      # Data persistence across sessions
│   │   ├── list_sessions/         # Session listing and filtering
│   │   └── get/                   # Session retrieval
│   └── advanced/                  # Advanced features
│       ├── agent-module-example/  # AI-powered automation
│       ├── vpc-session-example/   # Secure isolated network environments
│       └── archive-upload-mode-example/ # Archive upload mode
├── browser-use/                   # Browser automation (browser_latest)
│   ├── browser/                   # Browser automation examples
│   └── extension-example/         # Browser extension management
├── computer-use/                  # Windows desktop automation (windows_latest)
│   └── ui-example/                # UI automation
├── mobile-use/                    # Mobile UI automation (mobile_latest)
│   └── mobile-get-adb-url/        # ADB URL retrieval
└── codespace/                     # Code execution (code_latest)
    ├── automation/                # Automation workflows
    ├── enhanced_code/             # Enhanced runCode() output (logs/results/error)
    └── jupyter_context_persistence_r_java/ # Jupyter-like context persistence for R and Java
```

## 🚀 Quick Start

### Single-File Example

The fastest way to get started:

```bash
# Install dependencies
npm install wuying-agentbay-sdk

# Set your API key
export AGENTBAY_API_KEY=your_api_key_here

# Run the quick start example
npx ts-node basic-usage.ts
```

This example demonstrates:
- Initializing the AgentBay client
- Creating sessions
- Basic operations (commands, file operations)
- Session cleanup

## 📚 Feature Categories

### [Common Features](common-features/basics/command-example/README.md)

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

### [Browser Use](browser-use/browser/README.md)

Cloud-based browser automation with Playwright integration.

**Key Features:**
- Cookie and session persistence
- Stealth mode to avoid detection
- CAPTCHA handling capabilities
- Browser extension support
- Proxy configuration
- Custom viewport and fingerprinting


### [Mobile Use](mobile-use/mobile-get-adb-url/README.md)

Android mobile UI automation for app testing.

**Key Features:**
- ADB URL retrieval
- Mobile device connection
- Remote debugging

### [CodeSpace](codespace/automation/)

Cloud-based development environment for code execution.

**Key Features:**
- Automation workflows
- Shell command execution
- File system operations

## 📋 Prerequisites

### Basic Requirements

- Node.js 16 or later
- TypeScript 4.5 or later
- Valid `AGENTBAY_API_KEY` environment variable

### Installation

```bash
# Install the SDK
npm install wuying-agentbay-sdk

# For browser examples, install Playwright
npm install playwright
npx playwright install chromium

# Install TypeScript and ts-node (if not already installed)
npm install -D typescript ts-node @types/node
```

## 🎯 Running Examples

```bash
# Set your API key
export AGENTBAY_API_KEY=your_api_key_here

# Run any example with ts-node
npx ts-node basic-usage.ts
npx ts-node common-features/basics/session-creation/session-creation.ts

# Or compile and run
tsc basic-usage.ts
node basic-usage.js
```

## 💡 Common Patterns

### Basic Session Creation

```typescript
import { AgentBay, CreateSessionParams } from 'wuying-agentbay-sdk';

async function main() {
  // Initialize client
  const apiKey = process.env.AGENTBAY_API_KEY!;
  const agentBay = new AgentBay(apiKey);
  
  // Create session
  const params: CreateSessionParams = {
    imageId: 'linux_latest',
  };
  
  const result = await agentBay.create(params);
  
  if (result.success) {
    const session = result.session;
    console.log(`Session created: ${session.sessionId}`);
    
    // Use session...
    
    // Cleanup
    await agentBay.delete(session);
  }
}

main().catch(console.error);
```

### File Operations

```typescript
// Write file
await session.fileSystem.writeFile('/tmp/test.txt', 'content');

// Read file
const result = await session.fileSystem.readFile('/tmp/test.txt');
if (result.success) {
  console.log(result.content);
}
```

### Command Execution

```typescript
const result = await session.command.executeCommand('ls -la');
if (result.success) {
  console.log(result.output);
}
```

### Browser Automation

```typescript
import { BrowserOption } from 'wuying-agentbay-sdk';
import { chromium } from 'playwright';

// Initialize browser
const option = new BrowserOption();
await session.browser.initializeAsync(option);

// Connect Playwright
const endpointUrl = session.browser.getEndpointUrl();
const browser = await chromium.connectOverCDP(endpointUrl);
const context = browser.contexts()[0];
const page = await context.newPage();

// Automate...
await page.goto('https://example.com');

await browser.close();
```

## 🎓 Learning Path

### For Beginners

1. Start with [basic-usage.ts](basic-usage.ts)
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
2. **Error Handling**: Always check `result.success` before using data
3. **Async/Await**: Use async/await for cleaner asynchronous code
4. **Type Safety**: Leverage TypeScript's type system for better code quality
5. **Resource Limits**: Be aware of concurrent session limits

## 🔍 Example Index

### By Use Case

**Web Automation:**
- Browser stealth mode: `browser-use/browser/browser-stealth.ts`
- Cookie persistence: `browser-use/browser/browser-context-cookie-persistence.ts`
- CAPTCHA handling: `browser-use/browser/captcha_tongcheng.ts`

**Desktop Automation:**
- UI automation: `computer-use/ui-example/ui-example.ts`

**Mobile Automation:**
- ADB integration: `mobile-use/mobile-get-adb-url/index.ts`

**Code Execution:**
- Automation: `codespace/automation/automation-example.ts`
- Enhanced code result: `codespace/enhanced_code/index.ts`
- Jupyter-like context persistence (R/Java): `codespace/jupyter_context_persistence_r_java/index.ts`

**Data Management:**
- File operations: `common-features/basics/filesystem-example/filesystem-example.ts`
- Context management: `common-features/basics/context-management/context-management.ts`
- Data persistence: `common-features/basics/data-persistence/data-persistence.ts`

**Advanced Features:**
- AI Agent: `common-features/advanced/agent-module-example/agent-module-example.ts`
- VPC sessions: `common-features/advanced/vpc-session-example/vpc-session-example.ts`

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
npm install

# Clear cache and reinstall
rm -rf node_modules package-lock.json
npm install
```

### TypeScript Compilation Errors

If you get TypeScript errors:
```bash
# Ensure TypeScript is installed
npm install -D typescript

# Check TypeScript version
npx tsc --version

# Compile with type checking
npx tsc --noEmit
```

## 📚 Related Documentation

- [TypeScript SDK Documentation](../../)
- [API Reference](../api/)
- [Quick Start Guide](../../../docs/quickstart/README.md)
- [Feature Guides](../../../docs/guides/README.md)

## 🤝 Getting Help

- [GitHub Issues](https://github.com/aliyun/wuying-agentbay-sdk/issues)
- [Documentation](../../../docs/README.md)

---

💡 **Tip**: Start with `basic-usage.ts` for a quick overview, then explore category-specific examples based on your needs.

