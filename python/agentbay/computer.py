"""
Computer module for desktop UI automation.
Provides mouse, keyboard, window management, application management, and screen operations.

Deprecated import path. Use instead:
    from agentbay import Computer  # Sync
    from agentbay import AsyncComputer  # Async
"""

from ._sync.computer import (
    Computer,
    MouseButton,
    ScrollDirection,
    InstalledApp,
    Process,
    Window,
    InstalledAppListResult,
    ProcessListResult,
    AppOperationResult,
    WindowListResult,
    WindowInfoResult,
)

__all__ = [
    "Computer",
    "MouseButton",
    "ScrollDirection",
    "InstalledApp",
    "Process",
    "Window",
    "InstalledAppListResult",
    "ProcessListResult",
    "AppOperationResult",
    "WindowListResult",
    "WindowInfoResult",
]

