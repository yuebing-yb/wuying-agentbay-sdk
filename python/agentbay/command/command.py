from agentbay.api.base_service import BaseService
from agentbay.exceptions import AgentBayError, CommandError
from agentbay.model import ApiResponse


class CommandResult(ApiResponse):
    """Result of command execution operations."""

    def __init__(
        self,
        request_id: str = "",
        success: bool = False,
        output: str = "",
        error_message: str = "",
    ):
        """
        Initialize a CommandResult.

        Args:
            request_id (str, optional): Unique identifier for the API request.
            success (bool, optional): Whether the operation was successful.
            output (str, optional): The command output.
            error_message (str, optional): Error message if the operation failed.
        """
        super().__init__(request_id)
        self.success = success
        self.output = output
        self.error_message = error_message





class Command(BaseService):
    """
    Handles command execution operations in the AgentBay cloud environment.
    """

    def _handle_error(self, e):
        """
        Convert AgentBayError to CommandError for compatibility.

        Args:
            e (Exception): The exception to convert.

        Returns:
            CommandError: The converted exception.
        """
        if isinstance(e, CommandError):
            return e
        if isinstance(e, AgentBayError):
            return CommandError(str(e))
        return e

    def execute_command(self, command: str, timeout_ms: int = 1000) -> CommandResult:
        """
        Execute a shell command in the cloud environment with a specified timeout.

        Args:
            command (str): The shell command to execute.
            timeout_ms (int, optional): The timeout for the command execution in milliseconds.
                Defaults to 1000 (1 second).

        Returns:
            CommandResult: Result object containing success status, command output, and error message if any.
                - success (bool): True if the operation succeeded
                - output (str): The command output (stdout and stderr combined)
                - request_id (str): Unique identifier for this API request
                - error_message (str): Error description (if success is False)

        Raises:
            CommandError: If the command execution fails.

        Example:
            ```python
            from agentbay import AgentBay

            # Initialize and create session
            agent_bay = AgentBay(api_key="your_api_key")
            result = agent_bay.create()
            if result.success:
                session = result.session

                # Execute a simple command
                cmd_result = session.command.execute_command("echo 'Hello, World!'")
                if cmd_result.success:
                    print(f"Command output: {cmd_result.output}")
                    # Output: Command output: Hello, World!
                    print(f"Request ID: {cmd_result.request_id}")
                    # Output: Request ID: 9E3F4A5B-2C6D-7E8F-9A0B-1C2D3E4F5A6B

                # Execute a command with custom timeout (5 seconds)
                cmd_result = session.command.execute_command("sleep 2 && echo 'Done'", timeout_ms=5000)
                if cmd_result.success:
                    print(f"Command output: {cmd_result.output}")
                    # Output: Command output: Done

                # Execute a command that lists files
                cmd_result = session.command.execute_command("ls -la /tmp")
                if cmd_result.success:
                    print(f"Directory listing:\n{cmd_result.output}")

                # Handle command timeout
                cmd_result = session.command.execute_command("sleep 10", timeout_ms=1000)
                if not cmd_result.success:
                    print(f"Error: {cmd_result.error_message}")
                    # Output: Error: Command execution timed out

                # Clean up
                session.delete()
            ```

        Note:
            - Commands are executed in a Linux shell environment
            - Default timeout is 1 second (1000ms)
            - Output includes both stdout and stderr
            - Long-running commands may timeout if timeout_ms is too small

        See Also:
            Command.execute_command_async
        """
        try:
            args = {"command": command, "timeout_ms": timeout_ms}

            result = self.session.call_mcp_tool("shell", args)

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
        except CommandError as e:
            return CommandResult(request_id="", success=False, error_message=str(e))
        except Exception as e:
            return CommandResult(
                request_id="",
                success=False,
                error_message=f"Failed to execute command: {e}",
            )


