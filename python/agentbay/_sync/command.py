from typing import Any, Dict, Optional

from .._common.exceptions import AgentBayError, CommandError
from .._common.logger import get_logger
from .._common.models.command import CommandResult
from .._common.models.response import ApiResponse
from .base_service import BaseService

# Initialize _logger for this module
_logger = get_logger("command")


class Command(BaseService):
    """
    Handles command execution operations in the AgentBay cloud environment.
    """

    def execute_command(
        self, command: str, timeout_ms: int = 60000
    ) -> CommandResult:
        """
        Execute a shell command with a timeout.

        Args:
            command: The shell command to execute.
            timeout_ms: The timeout for the command execution in milliseconds. Default is 60000ms (60s).

        Returns:
            CommandResult: Result object containing success status, execution
                output, and error message if any.

        Raises:
            CommandError: If the command execution fails.

        Example:
            ```python
            result = await session.command.execute_command("ls -la")
            print(result.output)
            ```
        """
        try:
            args = {"command": command, "timeout_ms": timeout_ms}
            result = self.session.call_mcp_tool("shell", args)
            _logger.debug(f"Execute command response: {result}")

            if result.success:
                return CommandResult(
                    request_id=result.request_id,
                    success=True,
                    output=result.data,
                )
            else:
                return CommandResult(
                    request_id=result.request_id,
                    success=False,
                    error_message=result.error_message or "Failed to execute command",
                )
        except Exception as e:
            return CommandResult(
                request_id="",
                success=False,
                error_message=f"Failed to execute command: {e}",
            )
