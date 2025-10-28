# Browser API Reference

The Browser API provides methods for initializing and managing browser instances in the AgentBay cloud environment. It supports both headless and non-headless browsers with extensive configuration options including stealth mode, custom viewports, fingerprinting, proxies, and more.

## Overview

The Browser API is accessed through a session instance and provides methods for browser lifecycle management and connection to automation frameworks via Chrome DevTools Protocol (CDP).

```typescript
import { AgentBay, BrowserOptionClass } from '@wuying-org/agentbay-sdk';

// Access browser through session
const session = result.session;
const browserAPI = session.browser;
```

## Interfaces and Classes

### BrowserOption Interface

Type definition for browser configuration options.

```typescript
export interface BrowserOption {
  useStealth?: boolean;
  userAgent?: string;
  viewport?: BrowserViewport;
  screen?: BrowserScreen;
  fingerprint?: BrowserFingerprint;
  solveCaptchas?: boolean;
  proxies?: BrowserProxy[];
  extensionPath?: string;
  browserType?: 'chrome' | 'chromium' | undefined;
  cmdArgs?: string[];
  defaultNavigateUrl?: string;
}
```

**Properties:**

- `useStealth` (boolean | undefined): Enable stealth mode to avoid detection. Default: `undefined`
- `userAgent` (string | undefined): Custom user agent string. Default: `undefined`
- `viewport` (BrowserViewport | undefined): Browser viewport dimensions. Default: `undefined`
- `screen` (BrowserScreen | undefined): Screen dimensions. Default: `undefined`
- `fingerprint` (BrowserFingerprint | undefined): Fingerprint configuration. Default: `undefined`
- `solveCaptchas` (boolean | undefined): Auto-solve captchas. Default: `undefined`
- `proxies` (BrowserProxy[] | undefined): Proxy configurations (max 1). Default: `undefined`
- `extensionPath` (string | undefined): Path to extensions directory. Default: `undefined`
- `browserType` ('chrome' | 'chromium' | undefined): Browser type (computer use images only). Default: `undefined`
- `cmdArgs` (string[] | undefined): List of Chrome/Chromium command-line arguments to customize browser behavior. Default: `undefined`
- `defaultNavigateUrl` (string | undefined): URL that the browser automatically navigates to after initialization. Recommended to use Chrome internal pages (e.g., `"chrome://version/"`) to avoid timeout issues. Default: `undefined`

### BrowserOptionClass

Class implementation of BrowserOption with validation and serialization.

```typescript
export class BrowserOptionClass implements BrowserOption {
  useStealth?: boolean;
  userAgent?: string;
  viewport?: BrowserViewport;
  screen?: BrowserScreen;
  fingerprint?: BrowserFingerprint;
  solveCaptchas?: boolean;
  proxies?: BrowserProxy[];
  extensionPath?: string;
  browserType?: 'chrome' | 'chromium' | undefined;
  cmdArgs?: string[];
  defaultNavigateUrl?: string;

  constructor(
    useStealth = false,
    userAgent?: string,
    viewport?: BrowserViewport,
    screen?: BrowserScreen,
    fingerprint?: BrowserFingerprint,
    solveCaptchas = false,
    proxies?: BrowserProxy[],
    browserType?: 'chrome' | 'chromium',
    cmdArgs?: string[],
    defaultNavigateUrl?: string
  )
}
```

**Constructor Parameters:**

All parameters are optional with defaults:
- `useStealth`: `false`
- `solveCaptchas`: `false`
- `browserType`: `undefined`
- `cmdArgs`: `undefined`
- `defaultNavigateUrl`: `undefined`
- Other parameters: `undefined`

**Methods:**

#### toMap(): Record<string, any>

Converts BrowserOption to a plain object for API requests.

```typescript
toMap(): Record<string, any>
```

**Returns:**
- `Record<string, any>`: Object representation of the browser options

**Example:**
```typescript
const option = new BrowserOptionClass(true); // useStealth = true
const optionMap = option.toMap();
```

#### fromMap(m: Record<string, any>): BrowserOptionClass

Populates BrowserOption from a plain object.

```typescript
fromMap(m: Record<string, any> | null | undefined): BrowserOptionClass
```

**Parameters:**
- `m` (Record<string, any> | null | undefined): Object containing browser option data

**Returns:**
- `BrowserOptionClass`: Self (for method chaining)

**Example:**
```typescript
const option = new BrowserOptionClass();
option.fromMap({ useStealth: true, browserType: 'chrome' });
```

### BrowserViewport

Defines the browser viewport dimensions.

```typescript
export interface BrowserViewport {
  width: number;
  height: number;
}
```

**Common Viewport Sizes:**
```typescript
// Desktop
{ width: 1920, height: 1080 }
{ width: 1366, height: 768 }

// Laptop
{ width: 1440, height: 900 }

// Tablet
{ width: 1024, height: 768 }

// Mobile
{ width: 375, height: 667 }
{ width: 414, height: 896 }
```

### BrowserScreen

Defines the screen dimensions (usually same or larger than viewport).

```typescript
export interface BrowserScreen {
  width: number;
  height: number;
}
```

### BrowserFingerprint

Configuration for browser fingerprint randomization.

```typescript
export interface BrowserFingerprint {
  devices?: string[];
  operatingSystems?: string[];
  locales?: string[];
}
```

**Valid Values:**

- **devices**: `["desktop", "mobile"]`
- **operatingSystems**: `["windows", "macos", "linux", "android", "ios"]`
- **locales**: Standard locale strings (e.g., `["en-US", "zh-CN", "ja-JP"]`)

**Example:**
```typescript
const fingerprint: BrowserFingerprint = {
  devices: ["desktop"],
  operatingSystems: ["windows", "macos"],
  locales: ["en-US", "en-GB"]
};
```

### BrowserProxy / BrowserProxyClass

Configuration for browser proxy settings.

```typescript
export interface BrowserProxy {
  type: 'custom' | 'wuying';
  server?: string;
  username?: string;
  password?: string;
  strategy?: string;
  pollSize?: number;
}

export class BrowserProxyClass implements BrowserProxy {
  constructor(
    type: 'custom' | 'wuying',
    server?: string,
    username?: string,
    password?: string,
    strategy?: string,
    pollSize?: number
  )
}
```

**Proxy Types:**

1. **Custom Proxy** (`type: "custom"`):
   ```typescript
   const proxy = new BrowserProxyClass(
     'custom',
     'proxy.example.com:8080',
     'user',
     'pass'
   );
   
   // Or using interface
   const proxy: BrowserProxy = {
     type: 'custom',
     server: 'proxy.example.com:8080',
     username: 'user',
     password: 'pass'
   };
   ```

2. **WuYing Proxy** (`type: "wuying"`):
   - **Restricted Strategy**: Single dedicated IP
     ```typescript
     const proxy: BrowserProxy = {
       type: 'wuying',
       strategy: 'restricted'
     };
     ```
   
   - **Polling Strategy**: Rotating IP pool
     ```typescript
     const proxy: BrowserProxy = {
       type: 'wuying',
       strategy: 'polling',
       pollSize: 10
     };
     ```

**Validation Rules:**
- Maximum 1 proxy allowed in the `proxies` array
- `server` is required for `custom` type
- `strategy` is required for `wuying` type
- `pollSize` must be > 0 for `polling` strategy

## Browser Class

### Methods

#### initialize(option: BrowserOption | BrowserOptionClass): boolean

Initializes the browser with the given options (synchronous).

```typescript
initialize(option: BrowserOption | BrowserOptionClass): boolean
```

**Parameters:**
- `option` (BrowserOption | BrowserOptionClass): Browser configuration options

**Returns:**
- `boolean`: `true` if initialization was successful, `false` otherwise

**Throws:**
- `Error`: If browser option validation fails

**Example:**
```typescript
const option = new BrowserOptionClass(
  true,                                    // useStealth
  "Mozilla/5.0 (Macintosh; Intel...)",   // userAgent
  { width: 1920, height: 1080 },         // viewport
);

const success = session.browser.initialize(option);
if (!success) {
  throw new Error("Browser initialization failed");
}
```

#### initializeAsync(option: BrowserOption | BrowserOptionClass): Promise<boolean>

Initializes the browser with the given options (asynchronous).

```typescript
async initializeAsync(option: BrowserOption | BrowserOptionClass): Promise<boolean>
```

**Parameters:**
- `option` (BrowserOption | BrowserOptionClass): Browser configuration options

**Returns:**
- `Promise<boolean>`: Resolves to `true` if successful, `false` otherwise

**Throws:**
- `Error`: If browser option validation fails

**Example:**
```typescript
// Using BrowserOptionClass
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

const success = await session.browser.initializeAsync(option);
if (!success) {
  throw new Error("Browser initialization failed");
}

// Or using plain object
const success = await session.browser.initializeAsync({
  browserType: 'chrome',
  useStealth: true
});
```

#### getEndpointUrl(): string

Retrieves the CDP (Chrome DevTools Protocol) endpoint URL for connecting automation tools.

```typescript
getEndpointUrl(): string
```

**Returns:**
- `string`: The CDP WebSocket endpoint URL (e.g., `ws://host:port/devtools/browser/...`)

**Throws:**
- `Error`: If browser is not initialized

**Example:**
```typescript
const endpointUrl = session.browser.getEndpointUrl();

// Use with Playwright
import { chromium } from 'playwright';
const browser = await chromium.connectOverCDP(endpointUrl);
```

#### isInitialized(): boolean

Checks if the browser has been initialized.

```typescript
isInitialized(): boolean
```

**Returns:**
- `boolean`: `true` if the browser is initialized, `false` otherwise

**Example:**
```typescript
if (session.browser.isInitialized()) {
  console.log("Browser is ready");
} else {
  console.log("Browser needs initialization");
}
```

#### getOption(): BrowserOptionClass | null

Retrieves the current browser configuration.

```typescript
getOption(): BrowserOptionClass | null
```

**Returns:**
- `BrowserOptionClass | null`: The current browser configuration, or `null` if not initialized

**Example:**
```typescript
const option = session.browser.getOption();
if (option) {
  console.log(`Browser type: ${option.browserType}`);
}
```

## Complete Usage Example

### Basic Usage

```typescript
import { AgentBay, CreateSessionParams, BrowserOptionClass } from '@wuying-org/agentbay-sdk';
import { chromium } from 'playwright';

async function main() {
  // Initialize AgentBay
  const apiKey = process.env.AGENTBAY_API_KEY;
  if (!apiKey) {
    throw new Error("AGENTBAY_API_KEY not set");
  }
  const agentBay = new AgentBay(apiKey);

  // Create session
  const params = new CreateSessionParams({ imageId: 'browser_latest' });
  const result = await agentBay.create(params);
  if (!result.success || !result.session) {
    throw new Error("Failed to create session");
  }

  const session = result.session;

  try {
    // Initialize browser with default options
    const option = new BrowserOptionClass();
    const ok = await session.browser.initializeAsync(option);
    if (!ok) {
      throw new Error("Browser initialization failed");
    }

    // Get CDP endpoint
    const endpointUrl = session.browser.getEndpointUrl();

    // Connect with Playwright
    const browser = await chromium.connectOverCDP(endpointUrl);
    const context = browser.contexts()[0];
    const page = await context.newPage();

    // Navigate and interact
    await page.goto('https://example.com');
    const title = await page.title();
    console.log(`Page title: ${title}`);

    await browser.close();

  } finally {
    session.delete();
  }
}

main();
```

### Advanced Configuration

```typescript
import {
  BrowserOptionClass,
  BrowserProxyClass,
  BrowserViewport,
  BrowserScreen,
  BrowserFingerprint
} from '@wuying-org/agentbay-sdk';

// Create custom browser configuration
const option = new BrowserOptionClass(
  true,                                    // useStealth
  "Mozilla/5.0 (Windows NT 10.0...)",     // userAgent
  { width: 1920, height: 1080 },          // viewport
  { width: 1920, height: 1080 },          // screen
  {                                        // fingerprint
    devices: ["desktop"],
    operatingSystems: ["windows", "macos"],
    locales: ["en-US"]
  },
  false,                                   // solveCaptchas
  [new BrowserProxyClass(                  // proxies
    'custom',
    'proxy.example.com:8080',
    'username',
    'password'
  )],
  'chrome' as 'chrome',                    // browserType
  [                                        // cmdArgs
    '--disable-features=PrivacySandboxSettings4',
    '--disable-background-timer-throttling',
  ],
  'chrome://version/'                      // defaultNavigateUrl
);

// Or using plain object interface
const option = {
  useStealth: true,
  userAgent: "Mozilla/5.0 (Windows NT 10.0...)",
  viewport: { width: 1920, height: 1080 },
  screen: { width: 1920, height: 1080 },
  browserType: 'chrome' as 'chrome',
  cmdArgs: [
    '--disable-features=PrivacySandboxSettings4',
    '--disable-background-timer-throttling',
  ],
  defaultNavigateUrl: 'chrome://version/',
  fingerprint: {
    devices: ["desktop"],
    operatingSystems: ["windows", "macos"],
    locales: ["en-US"]
  },
  proxies: [{
    type: 'custom' as 'custom',
    server: 'proxy.example.com:8080',
    username: 'username',
    password: 'password'
  }]
};

// Initialize with custom options
const success = await session.browser.initializeAsync(option);
if (!success) {
  throw new Error("Failed to initialize browser");
}
```

## Error Handling

### Common Errors

1. **Browser Not Initialized**
   ```typescript
   try {
     const endpoint = session.browser.getEndpointUrl();
   } catch (error) {
     // Error: "Browser not initialized"
     console.error("Initialize browser before getting endpoint");
   }
   ```

2. **Invalid Configuration**
   ```typescript
   try {
     const option = new BrowserOptionClass(
       false, undefined, undefined, undefined, undefined, false, undefined,
       'firefox' as any  // Invalid browser type
     );
   } catch (error) {
     // Error: "browserType must be 'chrome' or 'chromium'"
     console.error(`Configuration error: ${error.message}`);
   }
   ```

3. **Multiple Proxies**
   ```typescript
   try {
     const option = new BrowserOptionClass(
       false, undefined, undefined, undefined, undefined, false,
       [proxy1, proxy2]  // Too many proxies
     );
   } catch (error) {
     // Error: "proxies list length must be limited to 1"
     console.error(`Too many proxies: ${error.message}`);
   }
   ```

### Best Practices

```typescript
// Check initialization status
if (!session.browser.isInitialized()) {
  console.log("Browser not initialized");
}

// Always use try-finally for cleanup
try {
  const ok = await session.browser.initializeAsync(option);
  if (!ok) {
    throw new Error("Initialization failed");
  }
  
  // Use the browser...
  
} finally {
  session.delete();
}

// Type safety with TypeScript
const option: BrowserOption = {
  browserType: 'chrome',  // Type-checked
  useStealth: true
};
```

## Browser Type Selection

> **Note:** The `browserType` property is only available for **computer use images**. For standard browser images, the browser type is determined by the image.

### Choosing Browser Type

```typescript
// Use Chrome (Google Chrome)
const option = new BrowserOptionClass(
  false, undefined, undefined, undefined, undefined, false, undefined,
  'chrome' as 'chrome'
);

// Or using object interface
const option: BrowserOption = { browserType: 'chrome' };

// Use Chromium (open-source)
const option: BrowserOption = { browserType: 'chromium' };

// Use default (undefined - let browser image decide)
const option = new BrowserOptionClass(); // browserType is undefined by default
```

### When to Use Each Type

**Chrome** (`'chrome'`):
- Need specific Chrome-only features
- Testing against actual Chrome browser
- Matching production Chrome environment

**Chromium** (`'chromium'`):
- Open-source preference
- Lighter resource usage
- Standard web automation

**Default** (`undefined`):
- Let the platform choose optimal browser
- Maximum compatibility
- Recommended for most use cases

## Integration with Automation Tools

### Playwright

```typescript
import { chromium } from 'playwright';

// Get endpoint
const endpointUrl = session.browser.getEndpointUrl();

// Connect Playwright
const browser = await chromium.connectOverCDP(endpointUrl);
const context = browser.contexts()[0];
const page = await context.newPage();

// Use page...

await browser.close();
```

### Puppeteer

```typescript
import puppeteer from 'puppeteer-core';

// Get endpoint
const endpointUrl = session.browser.getEndpointUrl();

// Connect Puppeteer
const browser = await puppeteer.connect({
  browserWSEndpoint: endpointUrl
});

const pages = await browser.pages();
const page = pages[0];

// Use page...

await browser.disconnect();
```

## PageUseAgent Integration

The Browser class includes an `agent` property for AI-powered browser automation.

```typescript
import { ActOptions } from '@wuying-org/agentbay-sdk';

// Use PageUseAgent for natural language actions
const actResult = await session.browser.agent.actAsync(
  new ActOptions({ action: "Click the sign in button" }),
  page
);

if (actResult.success) {
  console.log(`Action completed: ${actResult.message}`);
} else {
  console.log(`Action failed: ${actResult.message}`);
}
```

See the [PageUseAgent documentation](browser_agent.md) for more details.

## Performance Considerations

### Resource Usage

- **Stealth Mode**: Adds overhead for anti-detection measures
- **Fingerprinting**: Randomization has minimal performance impact
- **Proxies**: May add latency depending on proxy location
- **Extensions**: Each extension increases memory usage

### Optimization Tips

1. **Reuse Sessions**: Keep sessions alive for multiple operations
2. **Appropriate Viewport**: Use actual target viewport size
3. **Minimal Extensions**: Only load necessary extensions
4. **Async Operations**: Use `initializeAsync` for better concurrency

## Troubleshooting

### Browser Won't Initialize

```typescript
// Check session status
if (!result.success) {
  console.error(`Session creation failed: ${result.errorMessage}`);
}

// Verify image supports browser
const params = new CreateSessionParams({ imageId: 'browser_latest' });

// Check initialization
const success = await session.browser.initializeAsync(option);
console.log(`Initialization success: ${success}`);
```

### CDP Connection Fails

```typescript
// Ensure browser is initialized
if (!session.browser.isInitialized()) {
  throw new Error("Browser not initialized");
}

// Get and verify endpoint
const endpointUrl = session.browser.getEndpointUrl();
console.log(`Endpoint: ${endpointUrl}`);
```

### Configuration Issues

```typescript
// Check option values
const option = new BrowserOptionClass();
option.browserType = 'chrome';
console.log(`Browser type: ${option.browserType}`);
console.log(`Use stealth: ${option.useStealth}`);

// Type-safe validation
const validOption: BrowserOption = {
  browserType: 'chrome',  // TypeScript ensures valid value
  useStealth: true
};
```

## Type Definitions

### Complete Type Reference

```typescript
// Main interfaces
export interface BrowserOption { /* ... */ }
export interface BrowserViewport { /* ... */ }
export interface BrowserScreen { /* ... */ }
export interface BrowserFingerprint { /* ... */ }
export interface BrowserProxy { /* ... */ }

// Classes
export class BrowserOptionClass implements BrowserOption { /* ... */ }
export class BrowserProxyClass implements BrowserProxy { /* ... */ }

// Browser class
export class Browser {
  initialize(option: BrowserOption | BrowserOptionClass): boolean;
  initializeAsync(option: BrowserOption | BrowserOptionClass): Promise<boolean>;
  getEndpointUrl(): string;
  isInitialized(): boolean;
  getOption(): BrowserOptionClass | null;
  agent: BrowserAgent;
}
```

## See Also

- [Browser Use Guide](../../../../docs/guides/browser-use/README.md) - Complete guide with examples
- [Core Features](../../../../docs/guides/browser-use/core-features.md) - Essential browser features
- [Advanced Features](../../../../docs/guides/browser-use/advance-features.md) - Advanced configuration
- [Browser Examples](../../examples/browser-use/browser/README.md) - Runnable example code
- [PageUseAgent API](browser_agent.md) - AI-powered browser automation
- [Session Management](session.md) - Session lifecycle and management

