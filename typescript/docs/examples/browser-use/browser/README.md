# TypeScript Browser Examples

This directory contains TypeScript examples demonstrating browser automation capabilities of the AgentBay SDK.

## Prerequisites

1. **Install TypeScript SDK**:
   ```bash
   npm install @wuying-org/agentbay-sdk
   ```

2. **Install Playwright**:
   ```bash
   npm install playwright
   npx playwright install chromium
   ```

3. **Set API Key**:
   ```bash
   export AGENTBAY_API_KEY=your_api_key_here
   ```

## Examples

### 1. basic-usage.ts

A basic example showing how to:
- Create a session with a browser-enabled image
- Initialize the browser with default options
- Connect to the browser using Playwright over CDP
- Navigate to a website and interact with it
- Proper cleanup of resources

**Run:**
```bash
ts-node basic-usage.ts
```

**Key Features:**
- Session creation and management
- Browser initialization
- CDP connection with Playwright
- Basic navigation
- Resource cleanup

### 2. browser-viewport.ts

Demonstrates custom viewport and screen configuration:
- Setting custom user agent
- Configuring viewport dimensions
- Setting screen dimensions
- Verifying browser configuration

**Run:**
```bash
ts-node browser-viewport.ts
```

**Key Features:**
- Custom user agent
- Viewport configuration
- Screen dimensions
- Configuration verification

### 3. browser-fingerprint-xxx.ts

Shows how to configure browser fingerprinting:
- Three construction methods: random generation, custom configuration, and local fingerprint sync
- Fingerprint persistence capabilities across sessions

**Run:**
```bash
ts-node browser-fingerprint-xxx.ts
```

### 4. browser-proxies.ts

Demonstrates proxy configuration:
- Custom proxy setup
- WuYing proxy strategies (restricted/polling)
- Proxy authentication

**Run:**
```bash
ts-node browser-proxies.ts
```

**Key Features:**
- Custom proxy configuration
- WuYing proxy integration
- Proxy authentication
- IP rotation strategies

### 5. browser-context-cookie-persistence.ts

Demonstrates cookie persistence across sessions:
- Creating sessions with Browser Context
- Setting cookies manually using Playwright
- Deleting sessions with context synchronization
- Verifying cookie persistence in new sessions

**Run:**
```bash
ts-node browser-context-cookie-persistence.ts
```

**Key Features:**
- Browser Context configuration
- Cookie persistence
- Cross-session data sharing
- Resource cleanup

### 6. browser-type-example.ts

Comprehensive example demonstrating browser type selection:
- Chrome browser initialization
- Chromium browser initialization
- Default browser (undefined) usage
- Browser configuration verification
- Type-safe TypeScript patterns

**Run:**
```bash
# Run full example (tests all browser types)
ts-node browser-type-example.ts

# Run quick example (Chrome only)
ts-node browser-type-example.ts --quick

# Run type-safe example (demonstrates TypeScript types)
ts-node browser-type-example.ts --type-safe
```

**Key Features:**
- Browser type selection for Chrome, Chromium, and default
- TypeScript type safety demonstration
- Configuration validation
- Browser detection and verification
- Multiple usage patterns (BrowserOptionClass vs plain object)
- Command-line options for different test modes

### 7. Game Automation Examples

**run-2048.ts** and **run-sudoku.ts** demonstrate:
- Complex interaction patterns
- Agent-based automation for games
- Advanced browser control
- AI-powered game solving

**Run:**
```bash
ts-node run-2048.ts
ts-node run-sudoku.ts
```

### 8. screenshot-example.ts

An example demonstrating screenshot capabilities:
- Creating a browser session with AgentBay
- Using Playwright to connect to the browser instance
- Taking screenshots using direct Playwright integration (Uint8Array data)
- Saving screenshots to local files
- Customizing screenshot options (full page, image format, quality)

**Run:**
```bash
ts-node screenshot-example.ts
```

**Expected Output:**
```
📸 AgentBay Browser Screenshot Demo (TypeScript)
==================================================
Initializing AgentBay client...
Creating a new session...
Session created with ID: sess-xxxxx
Browser initialized successfully
Endpoint URL: ws://...
📸 Taking screenshot...
ℹ️  Note: Screenshot functionality requires Playwright TypeScript integration
✅ Browser screenshot demo completed

🧹 Cleaning up session sess-xxxxx...
✅ Session deleted successfully
```

## Browser Type Selection

When using computer use images, you can choose between Chrome and Chromium:

```typescript
import { BrowserOptionClass } from '@wuying-org/agentbay-sdk';

// Use Chrome
const option = new BrowserOptionClass(
  false,  // useStealth
  undefined,  // userAgent
  undefined,  // viewport
  undefined,  // screen
  undefined,  // fingerprint
  false,  // solveCaptchas
  undefined,  // proxies
  'chrome' as 'chrome'  // browserType
);

// Or use plain object
const option = { browserType: 'chrome' as 'chrome' };

// Use Chromium
const option = { browserType: 'chromium' as 'chromium' };

// Use default (undefined - let image decide)
const option = new BrowserOptionClass();
```

## Common Patterns

### Basic Browser Initialization

```typescript
import { AgentBay, CreateSessionParams, BrowserOptionClass } from '@wuying-org/agentbay-sdk';

const agentBay = new AgentBay(process.env.AGENTBAY_API_KEY!);
const params = new CreateSessionParams({ imageId: 'browser_latest' });
const result = await agentBay.create(params);

if (!result.success || !result.session) {
  throw new Error("Failed to create session");
}

const session = result.session;
const option = new BrowserOptionClass();
const success = await session.browser.initializeAsync(option);

if (!success) {
  throw new Error("Browser initialization failed");
}
```

### Connecting Playwright

```typescript
import { chromium } from 'playwright';

const endpointUrl = session.browser.getEndpointUrl();
const browser = await chromium.connectOverCDP(endpointUrl);
const context = browser.contexts()[0];
const page = await context.newPage();

// Use page...

await browser.close();
session.delete();
```

### Error Handling

```typescript
try {
  const success = await session.browser.initializeAsync(option);
  if (!success) {
    throw new Error("Initialization failed");
  }
  
  // Use browser...
  
} catch (error) {
  console.error(`Error: ${error.message}`);
} finally {
  session.delete();
}
```

### Type-Safe Configuration

```typescript
import { BrowserOption } from '@wuying-org/agentbay-sdk';

const option: BrowserOption = {
  browserType: 'chrome',  // Type-checked
  useStealth: true,
  viewport: { width: 1920, height: 1080 },
  fingerprint: {
    devices: ["desktop"],
    operatingSystems: ["windows", "macos"],
    locales: ["en-US"]
  }
};
```

## Troubleshooting

### "AGENTBAY_API_KEY not set"

Set your API key:
```bash
export AGENTBAY_API_KEY=your_api_key_here
```

### "Browser not initialized"

Ensure the browser is initialized before connecting:
```typescript
if (!session.browser.isInitialized()) {
  throw new Error("Browser must be initialized first");
}
```

### "Failed to connect over CDP"

Check that the browser initialization was successful:
```typescript
const success = await session.browser.initializeAsync(option);
console.log(`Initialization success: ${success}`);
```

### TypeScript Compilation Errors

Ensure you have the correct types:
```bash
npm install --save-dev @types/node
```

## Additional Resources

- [Browser API Reference](../../../api/browser-use/browser.md)
- [Browser Use Guide](../../../../../docs/guides/browser-use/README.md)
- [Core Features](../../../../../docs/guides/browser-use/core-features.md)
- [Advanced Features](../../../../../docs/guides/browser-use/advance-features.md)
- [Playwright Documentation](https://playwright.dev/docs/intro)

## Example Output

### Successful Execution

```
Creating session...
Session created: sess-xxxxx
Initializing browser...
Browser initialized successfully
CDP endpoint: ws://...
Connecting to browser...
Page title: Example Domain
Browser automation completed
Session deleted
```

### With Custom Configuration

```
Initializing browser with custom configuration...
User Agent: Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7)...
Viewport: 1920 x 1080
Screen: 1920 x 1080
Configuration verified successfully
```