import json
from typing import Optional, Tuple

from agentbay.api.models import CallMcpToolRequest
from agentbay.exceptions import CommandError


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

    def execute_command(self, command: str, timeout_ms: int = 1000) -> str:
        """
        Execute a command in the cloud environment with a specified timeout.

        Args:
            command: The command to execute.
            timeout_ms: The timeout for the command execution in milliseconds. Default is 1000ms.

        Returns:
            Dict[str, Any]: The result of the command execution.
        """
        try:
            args = {"command": command, "timeout_ms": timeout_ms}
            args_json = json.dumps(args, ensure_ascii=False)

            request = CallMcpToolRequest(
                authorization=f"Bearer {self.session.get_api_key()}",
                session_id=self.session.get_session_id(),
                name="shell",
                args=args_json,
            )
            print("request =", request)
            response = self.session.get_client().call_mcp_tool(request)
            print("response =", response)
            content_array = (
                response.to_map().get("body", {}).get("Data", {}).get("content")
            )

            if not isinstance(content_array, list):
                raise CommandError("content field not found or not an array")

            full_text = ""
            for item in content_array:
                if not isinstance(item, dict):
                    continue
                text = item.get("text")
                if isinstance(text, str):
                    full_text += text + "\n"
            return full_text
        except Exception as e:
            raise CommandError(f"Failed to execute command: {e}")
            
    def run_code(self, code: str, language: str, timeout_s: int = 300) -> str:
        """
        Execute code in the specified language with a timeout.

        Args:
            code: The code to execute.
            language: The programming language of the code. Must be either 'python' or 'javascript'.
            timeout_s: The timeout for the code execution in seconds. Default is 300s.

        Returns:
            str: The output of the code execution.

        Raises:
            CommandError: If the code execution fails or if an unsupported language is specified.
        """
        try:
            # Validate language
            if language not in ["python", "javascript"]:
                raise CommandError(f"Unsupported language: {language}. Supported languages are 'python' and 'javascript'")
                
            args = {"code": code, "language": language, "timeout_s": timeout_s}
            args_json = json.dumps(args, ensure_ascii=False)

            request = CallMcpToolRequest(
                authorization=f"Bearer {self.session.get_api_key()}",
                session_id=self.session.get_session_id(),
                name="run_code",
                args=args_json,
            )
            print("request =", request)
            response = self.session.get_client().call_mcp_tool(request)
            print("response =", response)
            
            data = response.to_map().get("body", {}).get("Data", {})
            output = data.get("output")
            
            if not isinstance(output, str):
                raise CommandError("output field not found or not a string")
                
            return output
        except Exception as e:
            raise CommandError(f"Failed to execute code: {e}")
