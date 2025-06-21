import json
from typing import Dict, Any, Optional, Union
from dataclasses import dataclass

from agentbay.api.models import CallMcpToolRequest
from agentbay.exceptions import CommandError


@dataclass
class CommandResult:
    """
    Represents the result of a command execution.

    Attributes:
        output (str): The output of the command execution.
        exit_code (Optional[int]): The exit code of the command. None if not available.
        duration_ms (Optional[int]): The duration of the command execution in milliseconds. None if not available.
    """
    output: str
    exit_code: Optional[int] = None
    duration_ms: Optional[int] = None


@dataclass
class CodeExecutionResult:
    """
    Represents the result of code execution.

    Attributes:
        output (str): The output of the code execution.
        duration_ms (Optional[int]): The duration of the code execution in milliseconds. None if not available.
        memory_kb (Optional[int]): The memory usage of the code execution in kilobytes. None if not available.
    """
    output: str
    duration_ms: Optional[int] = None
    memory_kb: Optional[int] = None


class Command:
    """
    Handles command execution operations in the AgentBay cloud environment.
    """

    def __init__(self, session):
        """
        Initialize a Command object.

        Args:
            session: The Session instance that this Command belongs to.
        """
        self.session = session

    def _call_mcp_tool(self, name: str, args: Dict[str, Any]) -> Any:
        """
        Internal helper to call MCP tool and handle errors.

        Args:
            name (str): The name of the tool to call.
            args (Dict[str, Any]): The arguments to pass to the tool.

        Returns:
            Any: The response from the tool.

        Raises:
            CommandError: If the tool call fails.
        """
        try:
            args_json = json.dumps(args, ensure_ascii=False)
            request = CallMcpToolRequest(
                authorization=f"Bearer {self.session.get_api_key()}",
                session_id=self.session.get_session_id(),
                name=name,
                args=args_json,
            )
            response = self.session.get_client().call_mcp_tool(request)
            response_map = response.to_map()
            if not response_map:
                raise CommandError("Invalid response format")
            body = response_map.get("body", {})
            print("response_map =", body)
            if not body:
                raise CommandError("Invalid response body")
            return self._parse_response_body(body)
        except (KeyError, TypeError, ValueError) as e:
            raise CommandError(f"Failed to parse MCP tool response: {e}")
        except Exception as e:
            raise CommandError(f"Failed to call MCP tool {name}: {e}")

    def _parse_response_body(self, body: Dict[str, Any]) -> Any:
        """
        Parses the response body from the MCP tool.

        Args:
            body (Dict[str, Any]): The response body.

        Returns:
            Any: The parsed content.

        Raises:
            CommandError: If the response contains errors or is invalid.
        """
        try:
            if body.get("Data", {}).get("isError", False):
                error_content = body.get("Data", {}).get("content", [])
                print("error_content =", error_content)
                error_message = "; ".join(
                    item.get("text", "Unknown error")
                    for item in error_content
                    if isinstance(item, dict)
                )
                raise CommandError(f"Error in response: {error_message}")

            response_data = body.get("Data", {})
            if not response_data:
                raise CommandError("No data field in response")

            # Handle 'content' field for other methods
            content = response_data.get("content", [])
            if not content or not isinstance(content, list):
                raise CommandError("No content found in response")

            content_item = content[0]
            json_text = content_item.get("text")
            return json_text
        except Exception as e:
            raise CommandError(f"{e}")

    def _parse_command_result(self, text: str) -> CommandResult:
        """
        Parse a JSON string into a CommandResult object.

        Args:
            text (str): The JSON string to parse.

        Returns:
            CommandResult: The parsed command result.
        """
        try:
            data = json.loads(text)
            return CommandResult(
                output=data.get("output", text),
                exit_code=data.get("exit_code"),
                duration_ms=data.get("duration_ms"),
            )
        except json.JSONDecodeError:
            # If parsing fails, just use the text as output
            return CommandResult(output=text)

    def _parse_code_execution_result(self, text: str) -> CodeExecutionResult:
        """
        Parse a JSON string into a CodeExecutionResult object.

        Args:
            text (str): The JSON string to parse.

        Returns:
            CodeExecutionResult: The parsed code execution result.
        """
        try:
            data = json.loads(text)
            return CodeExecutionResult(
                output=data.get("output", text),
                duration_ms=data.get("duration_ms"),
                memory_kb=data.get("memory_kb"),
            )
        except json.JSONDecodeError:
            # If parsing fails, just use the text as output
            return CodeExecutionResult(output=text)

    def execute_command(self, command: str, timeout_ms: int = 1000) -> CommandResult:
        """
        Execute a command in the cloud environment with a specified timeout.

        Args:
            command: The command to execute.
            timeout_ms: The timeout for the command execution in milliseconds. Default is 1000ms.

        Returns:
            CommandResult: The result of the command execution.
        """
        try:
            args = {"command": command, "timeout_ms": timeout_ms}

            response = self._call_mcp_tool("shell", args)
            print(f"Command executed response: {response}")
            return self._parse_command_result(response)
        except Exception as e:
            raise CommandError(f"Failed to execute command: {e}")

    def run_code(self, code: str, language: str, timeout_s: int = 300) -> CodeExecutionResult:
        """
        Execute code in the specified language with a timeout.

        Args:
            code: The code to execute.
            language: The programming language of the code. Must be either 'python' or 'javascript'.
            timeout_s: The timeout for the code execution in seconds. Default is 300s.

        Returns:
            CodeExecutionResult: The result of the code execution.

        Raises:
            CommandError: If the code execution fails or if an unsupported language is specified.
        """
        try:
            # Validate language
            if language not in ["python", "javascript"]:
                raise CommandError(f"Unsupported language: {language}. Supported languages are 'python' and 'javascript'")

            args = {"code": code, "language": language, "timeout_s": timeout_s}
            response = self._call_mcp_tool("run_code", args)
            print(f"Run code response: {response}")
            return self._parse_code_execution_result(response)
        except Exception as e:
            raise CommandError(f"Failed to execute code: {e}")
