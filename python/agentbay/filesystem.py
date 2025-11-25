"""
Filesystem operations for the AgentBay SDK.

Deprecated import path. Use instead:
    from agentbay import FileSystem  # Sync
    from agentbay import AsyncFileSystem  # Async
"""

from ._sync.filesystem import FileSystem

__all__ = ["FileSystem"]

