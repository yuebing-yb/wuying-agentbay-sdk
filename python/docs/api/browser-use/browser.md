# Browser API Reference

## 🌐 Related Tutorial

- [Browser Use Guide](../../../../docs/guides/browser-use/README.md) - Complete guide to browser automation

## Overview

The Browser module provides comprehensive browser automation capabilities including navigation, element interaction,
screenshot capture, and content extraction. It enables automated testing and web scraping workflows.


## Requirements

- Requires `browser_latest` image for browser automation features



Browser automation operations for the AgentBay SDK.

Deprecated import path. Use instead:
    from agentbay import Browser  # Sync
    from agentbay import AsyncBrowser  # Async

## Best Practices

1. Wait for page load completion before interacting with elements
2. Use appropriate selectors (CSS, XPath) for reliable element identification
3. Handle navigation timeouts and errors gracefully
4. Take screenshots for debugging and verification
5. Clean up browser resources after automation tasks

## Related Resources

- [Session API Reference](../common-features/basics/session.md)

---

*Documentation generated automatically from source code using pydoc-markdown.*
