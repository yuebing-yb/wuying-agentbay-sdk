"""
Command module data models.
"""

from .response import ApiResponse


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
            output (str, optional): The command execution output (stdout).
            error_message (str, optional): Error message if the operation failed (stderr or system error).
        """
        super().__init__(request_id)
        self.success = success
        self.output = output
        self.error_message = error_message

