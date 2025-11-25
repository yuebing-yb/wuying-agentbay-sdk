"""
Agent operations for the AgentBay SDK.

Deprecated import path. Use instead:
    from agentbay import Agent  # Sync
    from agentbay import AsyncAgent  # Async
"""

from ._sync.agent import Agent, ExecutionResult, QueryResult

__all__ = [
    "Agent",
    "ExecutionResult",
    "QueryResult",
]

