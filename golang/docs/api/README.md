# AgentBay Golang SDK API Reference

Complete API reference documentation for the AgentBay Golang SDK.

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
  - `Initialize()` / `InitializeAsync()` - Initialize browser with configuration options
  - `GetEndpointURL()` - Get CDP WebSocket endpoint for Playwright/Puppeteer connection
  - Options: Stealth mode, proxy (custom/wuying), fingerprint, viewport, CAPTCHA solving
  - AI Agent: `Agent.Act()`, `Agent.Observe()`, `Agent.Extract()` for natural language automation

### Computer Use (`windows_latest`, `linux_latest`)
- [**Computer**](computer-use/computer.md) - Desktop automation operations
  - Mouse: `ClickMouse()`, `MoveMouse()`, `DragMouse()`, `Scroll()`, `GetCursorPosition()`
  - Keyboard: `InputText()`, `PressKeys()`, `ReleaseKeys()`
  - Screen: `Screenshot()`, `GetScreenSize()`
  - Window: `ListRootWindows()`, `GetActiveWindow()`, `ActivateWindow()`, `CloseWindow()`, `MaximizeWindow()`, `MinimizeWindow()`, `RestoreWindow()`, `ResizeWindow()`, `FullscreenWindow()`, `FocusMode()`
  - Application: `GetInstalledApps()`, `StartApp()`, `ListVisibleApps()`, `StopAppByPname()`, `StopAppByPid()`, `StopAppByCmd()`
- [**UI**](computer-use/ui.md) - ⚠️ Deprecated, use Computer or Mobile APIs instead
- [**Window**](computer-use/window.md) - ⚠️ Deprecated, use Computer API instead
- [**Application**](computer-use/application.md) - ⚠️ Deprecated, use Computer or Mobile APIs instead

### Mobile Use (`mobile_latest`)
- [**Mobile**](mobile-use/mobile.md) - Android mobile device automation
  - Touch: `Tap()`, `Swipe()`
  - Input: `InputText()`, `SendKey()` (with KeyCode constants)
  - UI Elements: `GetClickableUIElements()`, `GetAllUIElements()`
  - Application: `GetInstalledApps()`, `StartApp()`, `StopAppByCmd()`
  - Screen: `Screenshot()`

### CodeSpace (`code_latest`)
- [**Code**](codespace/code.md) - Execute code in cloud environment
  - `RunCode()` - Run Python or JavaScript code with timeout control
  - Supports: Python, JavaScript
  - Maximum execution time: 60 seconds (gateway limitation)

## 📘 Related Documentation

- [Feature Guides](../../../docs/guides/README.md) - Detailed usage guides and tutorials
- [Code Examples](../examples/README.md) - Complete example implementations
- [Quick Start](../../../docs/quickstart/README.md) - Get started in 5 minutes

---

**Need help?** Check out the [complete documentation](../../../docs/README.md) or [open an issue](https://github.com/aliyun/wuying-agentbay-sdk/issues).
