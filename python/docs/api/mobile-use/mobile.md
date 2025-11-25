# Mobile API Reference

## 📱 Related Tutorial

- [Mobile Use Guide](../../../../docs/guides/mobile-use/README.md) - Automate mobile applications

## Overview

The Mobile module provides mobile device automation capabilities including touch gestures,
text input, app management, and screenshot capture. It supports Android device automation.


## Requirements

- Requires `mobile_latest` image for mobile automation features



Mobile module for mobile device UI automation and configuration.
Provides touch operations, UI element interactions, application management, screenshot capabilities,
and mobile environment configuration operations.

Deprecated import path. Use instead:
    from agentbay import Mobile  # Sync
    from agentbay import AsyncMobile  # Async

## Best Practices

1. Verify element coordinates before tap operations
2. Use appropriate swipe durations for smooth gestures
3. Wait for UI elements to load before interaction
4. Take screenshots for verification and debugging
5. Handle app installation and uninstallation properly
6. Configure app whitelists/blacklists for security

## Related Resources

- [Session API Reference](../common-features/basics/session.md)

---

*Documentation generated automatically from source code using pydoc-markdown.*
