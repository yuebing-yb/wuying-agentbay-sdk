"""
Command execution operations for the AgentBay SDK.

Deprecated import path. Use instead:
    from agentbay import Command  # Sync
    from agentbay import AsyncCommand  # Async
"""

from .._sync.command import Command, CommandResult
from .command_templates import (
    MOBILE_COMMAND_TEMPLATES,
    RESOLUTION_LOCK_TEMPLATE,
    APP_WHITELIST_TEMPLATE,
    APP_BLACKLIST_TEMPLATE
)

__all__ = [
    "Command",
    "CommandResult",
    "MOBILE_COMMAND_TEMPLATES",
    "RESOLUTION_LOCK_TEMPLATE",
    "APP_WHITELIST_TEMPLATE",
    "APP_BLACKLIST_TEMPLATE"
]
