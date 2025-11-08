from agentbay.api.base_service import BaseService
from agentbay.exceptions import AgentBayError, CommandError
from agentbay.model import ApiResponse
from agentbay.logger import get_logger

# Initialize logger for this module
logger = get_logger("code")


class CodeExecutionResult(ApiResponse):
    """Result of code execution operations."""

    def __init__(
        self,
        request_id: str = "",
        success: bool = False,
        result: str = "",
        error_message: str = "",
    ):
        """
        Initialize a CodeExecutionResult.

        Args:
            request_id (str, optional): Unique identifier for the API request.
            success (bool, optional): Whether the operation was successful.
            result (str, optional): The execution result.
            error_message (str, optional): Error message if the operation failed.
        """
        super().__init__(request_id)
        self.success = success
        self.result = result
        self.error_message = error_message


class Code(BaseService):
    """
    Handles code execution operations in the AgentBay cloud environment.
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

    def run_code(
        self, code: str, language: str, timeout_s: int = 60
    ) -> CodeExecutionResult:
        """
        Execute code in the specified language with a timeout.

        Args:
            code: The code to execute.
            language: The programming language of the code. Must be either 'python'
                or 'javascript'.
            timeout_s: The timeout for the code execution in seconds. Default is 60s.
                Note: Due to gateway limitations, each request cannot exceed 60 seconds.

        Returns:
            CodeExecutionResult: Result object containing success status, execution
                result, and error message if any.

        Raises:
            CommandError: If the code execution fails or if an unsupported language is
                specified.

        Important:
            The `run_code` method requires a session created with the `code_latest`
            image to function properly. If you encounter errors indicating that the
            tool is not found, make sure to create your session with
            `image_id="code_latest"` in the `CreateSessionParams`.

        Example:
            Execute Python and JavaScript code in a code execution environment::

                from agentbay import AgentBay
                from agentbay.session_params import CreateSessionParams

                agent_bay = AgentBay(api_key="your_api_key")

                def execute_code_example():
                    try:
                        # Create a session with code_latest image
                        params = CreateSessionParams(image_id="code_latest")
                        session_result = agent_bay.create(params)
                        if not session_result.success:
                            print(f"Failed to create session: {session_result.error_message}")
                            return

                        session = session_result.session

                        # Execute Python code
                        python_code = \"\"\"
                print("Hello from Python!")
                result = 2 + 3
                print(f"Result: {result}")
                \"\"\"

                        code_result = session.code.run_code(python_code, "python")
                        if code_result.success:
                            print(f"Python code output:\\n{code_result.result}")
                            # Expected output:
                            # Hello from Python!
                            # Result: 5
                        else:
                            print(f"Code execution failed: {code_result.error_message}")

                        # Execute JavaScript code
                        js_code = \"\"\"
                console.log("Hello from JavaScript!");
                const result = 2 + 3;
                console.log("Result:", result);
                \"\"\"

                        js_result = session.code.run_code(js_code, "javascript", timeout_s=30)
                        if js_result.success:
                            print(f"JavaScript code output:\\n{js_result.result}")
                            # Expected output:
                            # Hello from JavaScript!
                            # Result: 5
                        else:
                            print(f"Code execution failed: {js_result.error_message}")

                        session.delete()
                    except Exception as e:
                        print(f"Error: {e}")

                execute_code_example()
        """
        try:
            # Validate language
            if language not in ["python", "javascript"]:
                return CodeExecutionResult(
                    request_id="",
                    success=False,
                    error_message=f"Unsupported language: {language}. Supported "
                    "languages are 'python' and 'javascript'",
                )

            args = {"code": code, "language": language, "timeout_s": timeout_s}
            result = self.session.call_mcp_tool("run_code", args)
            logger.debug(f"Run code response: {result}")

            if result.success:
                return CodeExecutionResult(
                    request_id=result.request_id,
                    success=True,
                    result=result.data,
                )
            else:
                return CodeExecutionResult(
                    request_id=result.request_id,
                    success=False,
                    error_message=result.error_message or "Failed to run code",
                )
        except CommandError as e:
            return CodeExecutionResult(
                request_id="", success=False, error_message=str(e)
            )
        except Exception as e:
            return CodeExecutionResult(
                request_id="",
                success=False,
                error_message=f"Failed to run code: {e}",
            ) 