"""
OSS module for AgentBay.

Deprecated import path. Use instead:
    from agentbay import Oss  # Sync
    from agentbay import AsyncOss  # Async
"""

from .._sync.oss import Oss

__all__ = ["Oss"]
