# Browser Use Examples

This directory contains Java examples demonstrating browser automation with Playwright integration in AgentBay sessions.

## Examples

### 1. PlaywrightExample.java
**Source**: [`../../../agentbay/src/main/java/com/aliyun/agentbay/examples/PlaywrightExample.java`](../../../agentbay/src/main/java/com/aliyun/agentbay/examples/PlaywrightExample.java)

Basic Playwright browser automation:
- Initializing browser in session
- Page navigation and interaction
- Element selection and manipulation
- Taking screenshots

**Key features demonstrated:**
```java
// Initialize browser
session.getBrowser().init();
Browser browser = session.getBrowser().getBrowser();

// Create page and navigate
Page page = browser.newContext().newPage();
page.navigate("https://example.com");

// Interact with elements
page.locator("#button").click();
page.fill("input[name='search']", "query");
```

### 2. BrowserContextExample.java
**Source**: [`../../../agentbay/src/main/java/com/aliyun/agentbay/examples/BrowserContextExample.java`](../../../agentbay/src/main/java/com/aliyun/agentbay/examples/BrowserContextExample.java)

Persistent browser context management:
- Creating browser contexts
- Context persistence across sessions
- Cookie and storage management
- Context lifecycle

**Key features demonstrated:**
```java
// Create browser context configuration
BrowserContext browserContext = new BrowserContext();
browserContext.setContextId("my-browser-context");

CreateSessionParams params = new CreateSessionParams();
params.setBrowserContext(browserContext);

Session session = agentBay.create(params).getSession();
```

### 3. BrowserContextLoginPersistenceExample.java
**Source**: [`../../../agentbay/src/main/java/com/aliyun/agentbay/examples/BrowserContextLoginPersistenceExample.java`](../../../agentbay/src/main/java/com/aliyun/agentbay/examples/BrowserContextLoginPersistenceExample.java)

Login state persistence across sessions:
- Logging into websites
- Saving login state
- Reusing authenticated sessions
- Cookie persistence

**Key features demonstrated:**
```java
// First session: Login
session1.getBrowser().init();
Page page = browser.newContext().newPage();
page.navigate("https://example.com/login");
page.fill("input[name='username']", "user");
page.fill("input[name='password']", "pass");
page.click("button[type='submit']");

// Second session with same context: Already logged in
Session session2 = agentBay.create(paramsWithSameContext).getSession();
// Browser context automatically restored
```

### 4. BrowserAgentAsyncExample.java
**Source**: [`../../../agentbay/src/main/java/com/aliyun/agentbay/examples/BrowserAgentAsyncExample.java`](../../../agentbay/src/main/java/com/aliyun/agentbay/examples/BrowserAgentAsyncExample.java)

Asynchronous browser automation:
- Async browser operations
- Parallel page handling
- Non-blocking navigation
- Concurrent browser tasks

### 5. VisitAliyunExample.java
**Source**: [`../../../agentbay/src/main/java/com/aliyun/agentbay/examples/VisitAliyunExample.java`](../../../agentbay/src/main/java/com/aliyun/agentbay/examples/VisitAliyunExample.java)

Real-world browser automation example:
- Navigating to Alibaba Cloud website
- Interacting with dynamic content
- Data extraction from web pages

### 6. Game2048Example.java
**Source**: [`../../../agentbay/src/main/java/com/aliyun/agentbay/examples/Game2048Example.java`](../../../agentbay/src/main/java/com/aliyun/agentbay/examples/Game2048Example.java)

Advanced browser interaction:
- Complex game automation
- Real-time decision making
- Advanced element interaction

## Running the Examples

### Prerequisites

1. Set your API key:
```bash
export AGENTBAY_API_KEY=your_api_key_here
```

2. Ensure you have Playwright dependencies in your project:
```xml
<dependency>
    <groupId>com.microsoft.playwright</groupId>
    <artifactId>playwright</artifactId>
    <version>1.40.0</version>
</dependency>
```

### Running from Maven

```bash
cd java/agentbay
mvn compile exec:java -Dexec.mainClass="com.aliyun.agentbay.examples.PlaywrightExample"
mvn compile exec:java -Dexec.mainClass="com.aliyun.agentbay.examples.BrowserContextExample"
```

## Common Patterns

### Basic Browser Initialization
```java
// Create session with browser support
CreateSessionParams params = new CreateSessionParams();
params.setImageId("browser_latest");

Session session = agentBay.create(params).getSession();

// Initialize browser
session.getBrowser().init();
Browser browser = session.getBrowser().getBrowser();
```

### Persistent Browser Context
```java
// Configure persistent context
BrowserContext browserContext = new BrowserContext();
browserContext.setContextId("my-persistent-context");

CreateSessionParams params = new CreateSessionParams();
params.setBrowserContext(browserContext);
params.setImageId("browser_latest");

Session session = agentBay.create(params).getSession();
```

### Page Navigation and Interaction
```java
// Create browser context and page
BrowserContext context = browser.newContext();
Page page = context.newPage();

// Navigate
page.navigate("https://example.com");

// Wait for elements
page.waitForSelector("#content");

// Interact
page.click("button#submit");
page.fill("input[name='email']", "user@example.com");

// Get content
String title = page.title();
String content = page.content();

// Screenshot
page.screenshot(new Page.ScreenshotOptions().setPath(Paths.get("/tmp/screenshot.png")));
```

### Browser Replay
```java
// Enable browser recording
CreateSessionParams params = new CreateSessionParams();
params.setImageId("browser_latest");
params.setEnableBrowserReplay(true);  // Default is true

Session session = agentBay.create(params).getSession();
// All browser actions will be recorded
```

## Related Documentation

- [Browser API](../../api/browser-use/browser.md)
- [Playwright Documentation](https://playwright.dev/java/)

## Troubleshooting

**Browser initialization fails:**
- Ensure image is "browser_latest"
- Check session is active
- Verify network connectivity

**Elements not found:**
- Use `page.waitForSelector()` before interaction
- Check element selectors are correct
- Verify page has loaded completely

**Context persistence not working:**
- Use consistent `contextId` across sessions
- Ensure context is synced before session deletion
- Check context storage limits

**Replay not recording:**
- Verify `enableBrowserReplay` is true (default)
- Check session was created with browser image
- Ensure browser was initialized properly
