import os
import sys
from typing import Optional

from .exceptions import AgentBayError


class InternalOnlyError(AgentBayError):
    """Raised when an internal-only API is called externally."""


def _find_external_caller_module_name() -> Optional[str]:
    """
    Returns the first caller module name that is not inside the `agentbay` package.

    This is a best-effort guard to prevent SDK users from calling internal APIs.
    It is not a security boundary.
    """
    try:
        frame = sys._getframe(2)
    except ValueError:
        return None

    while frame is not None:
        module_name = frame.f_globals.get("__name__", "")
        if module_name and not module_name.startswith("agentbay."):
            return module_name
        frame = frame.f_back
    return None


def assert_internal_access(api_name: str) -> None:
    """
    Guard for internal-only SDK APIs.

    If `AGENTBAY_SDK_INTERNAL_TESTING=1` is set, this guard is bypassed.
    """
    if os.getenv("AGENTBAY_SDK_INTERNAL_TESTING") == "1":
        return

    external_module = _find_external_caller_module_name()
    if external_module is None:
        return
    raise InternalOnlyError(
        f"{api_name} is for internal SDK use only (caller={external_module})"
    )

