"""
Mobile module for mobile device UI automation and configuration.
Provides touch operations, UI element interactions, application management, screenshot capabilities,
and mobile environment configuration operations.

Deprecated import path. Use instead:
    from agentbay import Mobile  # Sync
    from agentbay import AsyncMobile  # Async
"""

from ._sync.mobile import Mobile, KeyCode, UIElementListResult

__all__ = ["Mobile", "KeyCode", "UIElementListResult"]

