"""
Code execution operations for the AgentBay SDK.

Deprecated import path. Use instead:
    from agentbay import Code  # Sync
    from agentbay import AsyncCode  # Async
"""

from .._sync.code import Code, CodeExecutionResult

__all__ = ["Code", "CodeExecutionResult"]
