"""
Browser Agent module for AI-driven browser automation.

Deprecated import path. Use instead:
    from agentbay.browser import BrowserAgent, ActOptions, ActResult, etc.
"""

from .._sync.browser_agent import (
    BrowserAgent,
    ActOptions,
    ActResult,
    ObserveOptions,
    ObserveResult,
    ExtractOptions
)

__all__ = [
    "BrowserAgent",
    "ActOptions",
    "ActResult",
    "ObserveOptions",
    "ObserveResult",
    "ExtractOptions"
]

