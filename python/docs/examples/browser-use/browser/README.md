# Python Browser Examples

This directory contains Python examples demonstrating browser automation capabilities of the AgentBay SDK.

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

## Examples

### 1. browser_context_cookie_persistence.py
Demonstrates how to use Browser Context to persist cookies across multiple sessions. This example shows:
- Creating sessions with Browser Context
- Setting cookies manually using Playwright
- Deleting sessions with context synchronization (`sync_context=True`)
- Verifying cookie persistence in new sessions
- Complete cleanup of resources

**Key features demonstrated:**
- Browser Context configuration with `auto_upload=True`
- Manual cookie setting and verification
- Cross-session cookie persistence
- Proper resource cleanup

### 2. search_agentbay_doc.py
Demonstrates basic browser automation using direct Playwright interactions:
- Connecting to AgentBay browser via CDP
- Manual element selection and interaction
- Search operations on websites

### 3. search_agentbay_doc_by_agent.py
Shows how to use the Agent module for intelligent browser automation:
- Using natural language commands with `session.browser.agent.act_async()`
- AI-powered element detection and interaction
- Simplified automation for complex web interactions

### 4. visit_aliyun.py
Basic browser usage example showing:
- Browser initialization
- Simple page navigation
- Basic browser operations

### 5. browser_type_example.py

Comprehensive example demonstrating browser type selection:
- Chrome browser initialization
- Chromium browser initialization
- Default browser (None) usage
- Browser configuration verification
- Side-by-side comparison of browser types

**Run:**
```bash
# Run full example (tests all browser types)
python browser_type_example.py

# Run quick example (Chrome only)
python browser_type_example.py --quick
```

**Key features demonstrated:**
- Browser type selection for Chrome, Chromium, and default
- Configuration validation
- Browser detection and verification
- Command-line options for different test modes

### 6. run_2048.py & run_sudoku.py
Game automation examples demonstrating:
- Complex interaction patterns
- Agent-based automation for games
- Advanced browser control

## Browser Type Selection

When using computer use images, you can choose between Chrome and Chromium:

```python
from agentbay.browser.browser import BrowserOption

# Use Chrome (Google Chrome)
option = BrowserOption(browser_type="chrome")
await session.browser.initialize_async(option)

# Use Chromium (open-source)
option = BrowserOption(browser_type="chromium")
await session.browser.initialize_async(option)

# Use default (None - let browser image decide)
option = BrowserOption()
await session.browser.initialize_async(option)
```

## Running the Examples

1. Install required dependencies:
```bash
pip install wuying-agentbay-sdk playwright
playwright install chromium
```

2. Set your API key:
```bash
export AGENTBAY_API_KEY=your_api_key_here
```

3. Run any example:
```bash
python browser_context_cookie_persistence.py
python search_agentbay_doc.py
# ... etc
```

## Common Patterns

### Basic Browser Initialization

```python
import asyncio
from agentbay import AgentBay
from agentbay.session_params import CreateSessionParams
from agentbay.browser.browser import BrowserOption

async def main():
    api_key = os.getenv("AGENTBAY_API_KEY")
    agent_bay = AgentBay(api_key=api_key)
    
    params = CreateSessionParams(image_id="browser_latest")
    result = agent_bay.create(params)
    
    if not result.success:
        raise RuntimeError(f"Failed to create session: {result.error_message}")
    
    session = result.session
    option = BrowserOption()
    success = await session.browser.initialize_async(option)
    
    if not success:
        raise RuntimeError("Browser initialization failed")

asyncio.run(main())
```

### Connecting Playwright

```python
from playwright.async_api import async_playwright

endpoint_url = session.browser.get_endpoint_url()

async with async_playwright() as p:
    browser = await p.chromium.connect_over_cdp(endpoint_url)
    context = browser.contexts[0]
    page = await context.new_page()
    
    # Use page...
    
    await browser.close()

session.delete()
```

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
    session.delete()
```

### Custom Configuration

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

## Browser Context vs Regular Browser Sessions

| Feature | Regular Browser Session | Browser Context Session |
|---------|------------------------|-------------------------|
| Cookie Persistence | No, cookies lost after session ends | Yes, cookies persist across sessions |
| Setup Complexity | Simple | Requires context creation |
| Use Case | One-time automation | Multi-session workflows |
| Data Synchronization | None | Automatic with `auto_upload=True` |

## Best Practices

1. **Always use context synchronization**: When deleting sessions with important browser data, use `sync_context=True`
2. **Proper cleanup**: Always delete sessions and contexts when done
3. **Error handling**: Implement proper error handling for network and browser operations
4. **Resource management**: Close browser connections properly
5. **Unique context names**: Use unique context names to avoid conflicts

## Related Documentation

- [Browser Extension Examples](../extension/README.md) - Dedicated extension management examples
- [Browser Automation Guide](../../../guides/browser-automation.md)
- [Browser Context Tutorial](../../../tutorials/browser-context.md)
- [Context Management Guide](../../../guides/context-management.md)
- [API Reference - Browser](../../../api-reference/python/browser.md) 