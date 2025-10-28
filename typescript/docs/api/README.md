# AgentBay TypeScript SDK API Reference

Complete API reference documentation for the AgentBay TypeScript SDK.

## 📚 Common Features

APIs available across all environments:

### Basics
- [**AgentBay**](common-features/basics/agentbay.md) - Main client for creating and managing sessions
- [**Session**](common-features/basics/session.md) - Session lifecycle and operations management
- [**Command**](common-features/basics/command.md) - Execute shell commands in cloud environments
- [**FileSystem**](common-features/basics/filesystem.md) - File and directory operations
- [**Context**](common-features/basics/context.md) - Data persistence and context management
- [**ContextManager**](common-features/basics/context-manager.md) - Context operations and file synchronization
- [**Logging**](common-features/basics/logging.md) - Logging configuration and management

### Advanced
- [**Agent**](common-features/advanced/agent.md) - AI agent integration and MCP tools
- [**OSS**](common-features/advanced/oss.md) - Object Storage Service integration

## 🚀 Environment-Specific Features

### Browser Use (`browser_latest`)
- [**Browser**](browser-use/browser.md) - Browser initialization and CDP connection
  - `initialize()` / `initializeAsync()` - Initialize browser with configuration options
  - `getEndpointUrl()` - Get CDP WebSocket endpoint for Playwright/Puppeteer connection
  - Options: Stealth mode, proxy (custom/wuying), fingerprint, viewport, CAPTCHA solving
  - AI Agent: `agent.act()`, `agent.observe()`, `agent.extract()` for natural language automation
- [**Extension**](browser-use/extension.md) - Browser extension management and deployment

### Computer Use (`windows_latest`, `linux_latest`)
- [**Computer**](computer-use/computer.md) - Desktop automation operations
  - Mouse: `clickMouse()`, `moveMouse()`, `dragMouse()`, `scroll()`, `getCursorPosition()`
  - Keyboard: `inputText()`, `pressKeys()`, `releaseKeys()`
  - Screen: `screenshot()`, `getScreenSize()`
  - Window: `listRootWindows()`, `getActiveWindow()`, `activateWindow()`, `closeWindow()`, `maximizeWindow()`, `minimizeWindow()`, `restoreWindow()`, `resizeWindow()`, `fullscreenWindow()`, `focusMode()`
  - Application: `getInstalledApps()`, `startApp()`, `listVisibleApps()`, `stopAppByPname()`, `stopAppByPid()`, `stopAppByCmd()`
- [**UI**](computer-use/ui.md) - ⚠️ Deprecated, use Computer or Mobile APIs instead
- [**Window**](computer-use/window.md) - ⚠️ Deprecated, use Computer API instead
- [**Application**](computer-use/application.md) - ⚠️ Deprecated, use Computer or Mobile APIs instead

### Mobile Use (`mobile_latest`)
- [**Mobile**](mobile-use/mobile.md) - Android mobile device automation
  - Touch: `tap()`, `swipe()`
  - Input: `inputText()`, `sendKey()` (with KeyCode constants)
  - UI Elements: `getClickableUiElements()`, `getAllUiElements()`
  - Application: `getInstalledApps()`, `startApp()`, `stopAppByCmd()`
  - Screen: `screenshot()`

### CodeSpace (`code_latest`)
- [**Code**](codespace/code.md) - Execute code in cloud environment
  - `runCode()` - Run Python or JavaScript code with timeout control
  - Supports: Python, JavaScript
  - Maximum execution time: 60 seconds (gateway limitation)

## 📘 Related Documentation

- [Feature Guides](../../../docs/guides/README.md) - Detailed usage guides and tutorials
- [Code Examples](../examples/README.md) - Complete example implementations
- [Quick Start](../../../docs/quickstart/README.md) - Get started in 5 minutes

---

**Need help?** Check out the [complete documentation](../../../docs/README.md) or [open an issue](https://github.com/aliyun/wuying-agentbay-sdk/issues).
