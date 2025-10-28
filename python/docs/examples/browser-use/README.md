# Browser Use Examples

This directory contains examples demonstrating browser automation capabilities in AgentBay SDK.

## Overview

Browser Use environment (`browser_latest` image) provides cloud-based browser automation with:
- Playwright integration for browser control
- Stealth mode to avoid detection
- Cookie and session persistence
- CAPTCHA handling capabilities
- Browser extension support
- AI-powered automation

## Directory Structure

```
browser-use/
├── browser/        # Browser automation examples
└── extension/      # Browser extension management examples
```

## Browser Examples

### Core Features

#### browser_context_cookie_persistence.py
Cookie persistence across multiple sessions:
- Creating sessions with Browser Context
- Setting cookies manually using Playwright
- Deleting sessions with context synchronization
- Verifying cookie persistence in new sessions

#### browser_stealth.py
Stealth mode to avoid bot detection:
- Browser fingerprint randomization
- Anti-detection techniques
- Stealth configuration options

#### browser_viewport.py
Custom viewport configuration:
- Setting custom screen resolutions
- Device emulation
- Responsive testing

#### browser_proxies.py
Proxy configuration for network routing:
- HTTP/HTTPS proxy setup
- SOCKS proxy support
- Authentication configuration

#### browser_type_example.py
Browser type selection:
- Chrome browser usage
- Chromium browser usage
- Default browser configuration

#### browser_command_args.py
Custom browser launch arguments:
- Performance optimization
- Feature flags
- Security settings

#### browser_replay.py
Session replay functionality:
- Recording browser sessions
- Replaying recorded sessions
- Session state restoration

### AI-Powered Automation

#### search_agentbay_doc.py
Manual browser automation with Playwright:
- Direct Playwright interactions
- Element selection and interaction
- Search operations

#### search_agentbay_doc_by_agent.py
AI-powered automation using Agent module:
- Natural language commands
- AI-driven element detection
- Simplified complex interactions

### Real-World Use Cases

#### Game Automation
- **game_2048.py**: 2048 game automation
- **game_sudoku.py**: Sudoku game automation
- **sudoku_solver.py**: Advanced Sudoku solving

#### E-commerce and Business
- **admin_add_product.py**: Product management automation
- **shop_inspector.py**: E-commerce shop inspection
- **expense_upload_invoices.py**: Invoice upload automation
- **gv_quick_buy_seat.py**: Quick seat booking

#### Web Interaction
- **visit_aliyun.py**: Basic website navigation
- **alimeeting_availability.py**: Meeting availability checking
- **call_for_user_jd.py**: JD.com user interaction
- **mini_max.py**: MiniMax platform automation

#### CAPTCHA Handling
- **captcha_tongcheng.py**: CAPTCHA solving example

## Extension Examples

### basic_extension_usage.py
Loading and using browser extensions:
- Extension installation
- Extension configuration
- Using extensions in automation

### extension_development_workflow.py
Extension development patterns:
- Development mode setup
- Testing extensions
- Debugging workflows

### extension_testing_automation.py
Automated extension testing:
- Test automation for extensions
- Validation workflows
- CI/CD integration

## Prerequisites

1. **Install Python SDK**:
   ```bash
   pip install wuying-agentbay-sdk
   ```

2. **Install Playwright**:
   ```bash
   pip install playwright
   playwright install chromium
   ```

3. **Set API Key**:
   ```bash
   export AGENTBAY_API_KEY=your_api_key_here
   ```

## Quick Start

### Basic Browser Automation

```python
import asyncio
from agentbay import AgentBay
from agentbay.session_params import CreateSessionParams
from agentbay.browser.browser import BrowserOption
from playwright.async_api import async_playwright

async def main():
    # Create session
    agent_bay = AgentBay(api_key="your_api_key")
    params = CreateSessionParams(image_id="browser_latest")
    result = agent_bay.create(params)
    session = result.session
    
    # Initialize browser
    option = BrowserOption()
    await session.browser.initialize_async(option)
    
    # Connect Playwright
    endpoint_url = session.browser.get_endpoint_url()
    async with async_playwright() as p:
        browser = await p.chromium.connect_over_cdp(endpoint_url)
        context = browser.contexts[0]
        page = await context.new_page()
        
        # Automate...
        await page.goto("https://example.com")
        
        await browser.close()
    
    # Cleanup
    agent_bay.delete(session)

asyncio.run(main())
```

### AI-Powered Automation

```python
# Use Agent for intelligent automation
result = await session.browser.agent.act_async(
    "Search for AgentBay on the page and click the first result"
)
```

## Browser Type Selection

```python
from agentbay.browser.browser import BrowserOption

# Use Chrome
option = BrowserOption(browser_type="chrome")
await session.browser.initialize_async(option)

# Use Chromium
option = BrowserOption(browser_type="chromium")
await session.browser.initialize_async(option)

# Use default
option = BrowserOption()
await session.browser.initialize_async(option)
```

## Stealth Configuration

```python
from agentbay.browser.browser import (
    BrowserOption,
    BrowserViewport,
    BrowserFingerprint
)

option = BrowserOption(
    browser_type="chrome",
    use_stealth=True,
    viewport=BrowserViewport(1920, 1080),
    fingerprint=BrowserFingerprint(
        devices=["desktop"],
        operating_systems=["windows", "macos"],
        locales=["en-US"]
    )
)
```

## Cookie Persistence

```python
from agentbay.session_params import BrowserContext

# Create browser context
context_result = agent_bay.context.get("my-browser-context", create=True)

browser_context = BrowserContext(
    context_id=context_result.context.id,
    auto_upload=True
)

params = CreateSessionParams(
    image_id="browser_latest",
    browser_context=browser_context
)

# Cookies will persist across sessions
```

## Best Practices

1. **Always use context synchronization**: When deleting sessions with important browser data, use `sync_context=True`
2. **Proper cleanup**: Always delete sessions and contexts when done
3. **Error handling**: Implement proper error handling for network and browser operations
4. **Resource management**: Close browser connections properly
5. **Unique context names**: Use unique context names to avoid conflicts
6. **Stealth mode**: Use stealth mode for production web scraping
7. **Rate limiting**: Respect website rate limits and robots.txt

## Common Patterns

### Error Handling

```python
try:
    success = await session.browser.initialize_async(option)
    if not success:
        raise RuntimeError("Initialization failed")
    
    # Use browser...
    
except Exception as e:
    print(f"Error: {e}")
finally:
    agent_bay.delete(session)
```

### Waiting for Elements

```python
# Wait for element
await page.wait_for_selector("#my-element", timeout=5000)

# Wait for navigation
await page.wait_for_load_state("networkidle")
```

### Taking Screenshots

```python
# Full page screenshot
await page.screenshot(path="screenshot.png", full_page=True)

# Element screenshot
element = await page.query_selector("#my-element")
await element.screenshot(path="element.png")
```

## Browser Context vs Regular Sessions

| Feature | Regular Browser Session | Browser Context Session |
|---------|------------------------|-------------------------|
| Cookie Persistence | No, cookies lost after session ends | Yes, cookies persist across sessions |
| Setup Complexity | Simple | Requires context creation |
| Use Case | One-time automation | Multi-session workflows |
| Data Synchronization | None | Automatic with `auto_upload=True` |

## API Methods Used

| Method | Purpose |
|--------|---------|
| `session.browser.initialize_async()` | Initialize browser with options |
| `session.browser.get_endpoint_url()` | Get CDP endpoint for Playwright |
| `session.browser.agent.act_async()` | AI-powered browser automation |
| `session.browser.close()` | Close browser connection |

## Related Documentation

- [Browser Use Guide](../../../../docs/guides/browser-use/README.md)
- [Core Features](../../../../docs/guides/browser-use/core-features.md)
- [Advanced Features](../../../../docs/guides/browser-use/advance-features.md)
- [Browser Extensions](../../../../docs/guides/browser-use/browser-extensions.md)
- [Browser Replay](../../../../docs/guides/browser-use/browser-replay.md)

## Troubleshooting

### Browser Initialization Failed

If browser fails to initialize:
- Check session is created successfully
- Verify image_id is `browser_latest`
- Wait a few seconds after session creation

### Playwright Connection Issues

If Playwright can't connect:
- Verify endpoint URL is correct
- Check network connectivity
- Ensure Playwright is installed: `playwright install chromium`

### Cookie Persistence Not Working

Ensure you're using Browser Context:
- Create context with `agent_bay.context.get()`
- Use `BrowserContext` in session params
- Delete session with `sync_context=True`

### Detection by Websites

If websites detect automation:
- Enable stealth mode: `use_stealth=True`
- Randomize fingerprints
- Add delays between actions
- Use residential proxies

