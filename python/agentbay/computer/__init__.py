"""
Computer module for desktop UI automation.
Provides mouse, keyboard, window management, application management, and screen operations.
"""

from .computer import (
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
