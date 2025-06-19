# TypeScript SDK for Wuying AgentBay

This directory contains the TypeScript implementation of the Wuying AgentBay SDK.

## Prerequisites

- Node.js (v14 or later)
- npm (v6 or later)

## Installation

### For Development

Clone the repository and install dependencies:

```bash
git clone https://github.com/aliyun/wuying-agentbay-sdk.git
cd wuying-agentbay-sdk/typescript
npm install
```

### For Usage in Your Project

```bash
npm install wuying-agentbay-sdk
```

## Development Scripts

- **Build the project**:
  ```bash
  npm run build
  ```

- **Run tests**:
  ```bash
  npm test
  ```

- **Lint the code**:
  ```bash
  npm run lint
  ```

- **Format the code**:
  ```bash
  npm run format
  ```

## Running Examples

You can run the example file using ts-node:

```bash
npx ts-node examples/basic-usage.ts
```

## TypeScript-Specific Usage

```typescript
import { AgentBay } from 'wuying-agentbay-sdk';

async function main() {
  // Initialize with API key
  const agentBay = new AgentBay({ apiKey: 'your_api_key' });
  
  try {
    // Create a session with labels
    const session = await agentBay.create({
      labels: {
        purpose: 'demo',
        environment: 'development'
      }
    });
    log(`Session created with ID: ${session.sessionId}`);
    
    // Execute a command
    const result = await session.command.executeCommand('ls -la');
    log(`Command result: ${result}`);
    
    // Read a file
    const content = await session.filesystem.readFile('/path/to/file.txt');
    log(`File content: ${content}`);
    
    // Get installed applications
    const apps = await session.application.getInstalledApps(true, false, true);
    log(`Found ${apps.length} installed applications`);
    
    // List visible applications
    const processes = await session.application.listVisibleApps();
    log(`Found ${processes.length} visible applications`);
    
    // List root windows
    const windows = await session.window.listRootWindows();
    log(`Found ${windows.length} root windows`);
    
    // Get active window
    const activeWindow = await session.window.getActiveWindow();
    log(`Active window: ${activeWindow.title}`);
    
    // Get session labels
    const labels = await session.getLabels();
    log(`Session labels: ${JSON.stringify(labels)}`);
    
    // List sessions by labels
    const filteredSessions = await agentBay.listByLabels({
      purpose: 'demo'
    });
    log(`Found ${filteredSessions.length} matching sessions`);
    
    // Clean up
    await agentBay.delete(session);
    log('Session deleted successfully');
  } catch (error) {
    logError('Error:', error);
  }
}

main();
```

For more detailed documentation, please refer to the main [README](../README.md) and [SDK Documentation](../docs/README.md) in the project root.
