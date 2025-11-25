"""
Browser automation operations for the AgentBay SDK.

Deprecated import path. Use instead:
    from agentbay import Browser  # Sync
    from agentbay import AsyncBrowser  # Async
"""

from ._sync.browser import Browser, BrowserOption, BrowserViewport, BrowserScreen, BrowserFingerprint, BrowserProxy, BrowserFingerprintContext
from ._sync.browser_agent import BrowserAgent, ActOptions, ActResult, ObserveOptions, ObserveResult, ExtractOptions
from ._sync.fingerprint import BrowserFingerprintGenerator, FingerprintFormat

__all__ = [
    "Browser",
    "BrowserFingerprintContext",
    "BrowserOption",
    "BrowserViewport",
    "BrowserScreen",
    "BrowserFingerprint",
    "BrowserProxy",
    "BrowserAgent",
    "ActOptions",
    "ActResult",
    "ObserveOptions",
    "ObserveResult",
    "ExtractOptions",
    "BrowserFingerprintGenerator",
    "FingerprintFormat",
]

