"""
Unified logging configuration for AgentBay SDK using loguru.

This module provides a centralized logging configuration with beautiful formatting
and structured output for different log levels.
"""

import sys
from pathlib import Path
from typing import Optional, Union, Dict, Any, List
from loguru import logger
import os
import re


# ANSI Color codes
COLOR_RESET = "\033[0m"
COLOR_GREEN = "\033[32m"
COLOR_BLUE = "\033[34m"
COLOR_CYAN = "\033[36m"


def colorize_log_message(record):
    """
    Colorize log messages based on content.
    API Calls are blue, Responses are green, Operations are cyan.
    This filter modifies the message in the record and returns True to accept it.
    """
    message = record["message"]

    # Check for API Call
    if "🔗 API Call" in message:
        # Wrap the entire message in blue
        record["message"] = f"{COLOR_BLUE}{message}{COLOR_RESET}"
    # Check for API Response (success)
    elif "✅ API Response" in message or "✅ Completed" in message:
        # Wrap the entire message in green
        record["message"] = f"{COLOR_GREEN}{message}{COLOR_RESET}"
    # Check for operations starting
    elif "🚀 Starting" in message:
        # Wrap in cyan
        record["message"] = f"{COLOR_CYAN}{message}{COLOR_RESET}"

    # Return True to accept the record
    return True


class AgentBayLogger:
    """AgentBay SDK Logger with beautiful formatting."""
    
    _initialized = False
    _log_level = "INFO"
    _log_file: Optional[Path] = None
    
    @classmethod
    def _should_use_colors(cls) -> bool:
        """
        Determine whether to use colors in console output.

        Priority:
        1. DISABLE_COLORS environment variable (explicit disable)
        2. FORCE_COLOR environment variable (explicit enable)
        3. TTY detection (terminal output)
        4. IDE environment detection (VS Code, GoLand, IntelliJ)
        5. Default: no colors (safe for file output, CI/CD, pipes)

        Returns:
            bool: True if colors should be used, False otherwise
        """
        # Priority 1: Explicit disable
        if os.getenv('DISABLE_COLORS') == '1':
            return False

        # Priority 2: Explicit enable via FORCE_COLOR
        force_color = os.getenv('FORCE_COLOR', '')
        if force_color and force_color != '0':
            return True

        # Priority 3: TTY detection
        if sys.stderr.isatty():
            return True

        # Priority 4: IDE environment detection
        if os.getenv('TERM_PROGRAM') == 'vscode':
            return True
        if os.getenv('GOLAND'):
            return True
        if os.getenv('IDEA_INITIAL_DIRECTORY'):
            return True

        # Default: no colors
        return False
    
    @classmethod
    def setup(
        cls,
        level: str = "INFO",
        log_file: Optional[Union[str, Path]] = None,
        enable_console: bool = True,
        enable_file: bool = True,
        rotation: Optional[str] = None,
        retention: str = "30 days",
        max_file_size: Optional[str] = None,
        colorize: Optional[bool] = None,
        force_reinit: bool = True
    ) -> None:
        """
        Setup the logger with custom configuration.

        This method should be called early in your application, before any logging occurs.
        By default, it will not reinitialize if already configured. Use force_reinit=True
        to override existing configuration.

        Args:
            level: Log level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
            log_file: Path to log file (optional)
            enable_console: Whether to enable console logging
            enable_file: Whether to enable file logging
            rotation: Log file rotation size (deprecated, use max_file_size)
            retention: Log file retention period
            max_file_size: Maximum log file size before rotation (e.g., "10 MB", "100 MB")
            colorize: Whether to use colors in console output (None = auto-detect)
            force_reinit: Force reinitialization even if already initialized (default: False)

        Example:
            >>> from agentbay.logger import AgentBayLogger
            >>> AgentBayLogger.setup(level="DEBUG", max_file_size="10 MB")
        """
        # Automatically reset if already initialized and force_reinit is True
        if cls._initialized and force_reinit:
            cls._initialized = False

        if cls._initialized:
            return

        # Remove default handler
        # Use try-except to handle cases where logger.remove() might fail
        # (e.g., in pytest environment where handlers might be managed externally)
        try:
            logger.remove()
        except Exception:
            # If removal fails, continue with setup
            # This can happen in test environments
            pass
        
        cls._log_level = level.upper()
        
        # Determine if colors should be used
        should_colorize = colorize if colorize is not None else cls._should_use_colors()
        
        # Console handler with beautiful formatting
        if enable_console:
            console_format = (
                "<green>{time:YYYY-MM-DD HH:mm:ss.SSS}</green> | "
                "<bold><blue>AgentBay</blue></bold> | "
                "<level>{level}</level> | "
                "<yellow>{process.id}:{thread.id}</yellow> | "
                "<cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> | "
                "<level>{message}</level>"
            )

            logger.add(
                sys.stderr,
                format=console_format,
                level=cls._log_level,
                colorize=should_colorize,
                filter=colorize_log_message,
                backtrace=True,
                diagnose=True
            )
        
        # File handler with structured formatting (no colors)
        if enable_file:
            if log_file:
                cls._log_file = Path(log_file) if isinstance(log_file, str) else log_file
            else:
                # Default log file path in python/ directory
                current_dir = Path(__file__).parent.parent  # Go up from agentbay/ to python/
                cls._log_file = current_dir / "agentbay.log"

            cls._log_file.parent.mkdir(parents=True, exist_ok=True)

            # Priority: max_file_size > rotation > default
            file_rotation = max_file_size if max_file_size is not None else (rotation if rotation is not None else "10 MB")

            file_format = (
                "{time:YYYY-MM-DD HH:mm:ss.SSS} | "
                "AgentBay | "
                "{level: <8} | "
                "{process.id}:{thread.id} | "
                "{name}:{function}:{line} | "
                "{message}"
            )

            logger.add(
                str(cls._log_file),
                format=file_format,
                level=cls._log_level,
                colorize=False,
                rotation=file_rotation,
                retention=retention,
                backtrace=True,
                diagnose=True
            )
        
        cls._initialized = True
    
    @classmethod
    def get_logger(cls, name: Optional[str] = None):
        """
        Get a logger instance.

        Args:
            name: Logger name (optional)

        Returns:
            Configured logger instance
        """
        if name:
            return logger.bind(name=name)
        return logger
    
    @classmethod
    def set_level(cls, level: str) -> None:
        """
        Set the logging level.
        
        Args:
            level: New log level
        """
        cls._log_level = level.upper()
        if cls._initialized:
            # Re-initialize with new level
            cls._initialized = False
            cls.setup(level=cls._log_level)


# Initialize the logger automatically on module import
# This provides immediate logging capability without explicit setup
# Read from environment variable if available, otherwise use INFO
_env_log_level = os.getenv("AGENTBAY_LOG_LEVEL", "INFO")
AgentBayLogger.setup(level=_env_log_level)


# Export convenience functions for the logger
def get_logger(name: str = "agentbay"):
    """
    Convenience function to get a named logger.

    Args:
        name: Logger name (defaults to "agentbay")

    Returns:
        Named logger instance
    """
    return AgentBayLogger.get_logger(name)


# Module-level logger for convenience functions
log = get_logger("agentbay")


# Sensitive field names for data masking
SENSITIVE_FIELDS = [
    'api_key', 'apikey', 'api-key',
    'password', 'passwd', 'pwd',
    'token', 'access_token', 'auth_token',
    'secret', 'private_key',
    'authorization',
]


def mask_sensitive_data(data: Any, fields: List[str] = None) -> Any:
    """
    Mask sensitive information in data structures.

    Args:
        data: Data to mask (dict, str, list, etc.)
        fields: Additional sensitive field names

    Returns:
        Masked data (deep copy)
    """
    if fields is None:
        fields = SENSITIVE_FIELDS

    if isinstance(data, dict):
        masked = {}
        for key, value in data.items():
            if any(field in key.lower() for field in fields):
                if isinstance(value, str) and len(value) > 4:
                    masked[key] = value[:2] + '****' + value[-2:]
                else:
                    masked[key] = '****'
            else:
                masked[key] = mask_sensitive_data(value, fields)
        return masked
    elif isinstance(data, list):
        return [mask_sensitive_data(item, fields) for item in data]
    elif isinstance(data, str):
        # Don't mask plain strings, only dict keys
        return data
    else:
        return data


# Compatibility functions for common logging patterns
def log_api_call(api_name: str, request_data: str = "") -> None:
    """Log API call with consistent formatting."""
    log.opt(depth=1).info(f"🔗 API Call: {api_name}")
    if request_data:
        log.opt(depth=1).info(f"  └─ {request_data}")


def log_api_response(response_data: str, success: bool = True) -> None:
    """Log API response with consistent formatting."""
    if success:
        log.opt(depth=1).info("✅ API Response received")
        log.opt(depth=1).debug(f"📥 Response: {response_data}")
    else:
        log.opt(depth=1).error("❌ API Response failed")
        log.opt(depth=1).error(f"📥 Response: {response_data}")


def log_api_response_with_details(
    api_name: str,
    request_id: str = "",
    success: bool = True,
    key_fields: Dict[str, Any] = None,
    full_response: str = ""
) -> None:
    """
    Log API response with key details at INFO level.

    Args:
        api_name: Name of the API being called
        request_id: Request ID from the response
        success: Whether the API call was successful
        key_fields: Dictionary of key business fields to log
        full_response: Full response body (logged at DEBUG level)
    """
    if success:
        # Main response line with API name and requestId
        main_info = f"✅ API Response: {api_name}"
        if request_id:
            main_info += f", RequestId={request_id}"
        log.opt(depth=1).info(main_info)

        # Log key fields on separate lines for better readability
        if key_fields:
            for key, value in key_fields.items():
                # Add green color to parameter lines
                param_line = f"{COLOR_GREEN}  └─ {key}={value}{COLOR_RESET}"
                log.opt(depth=1).info(param_line)

        if full_response:
            log.opt(depth=1).debug(f"📥 Full Response: {full_response}")
    else:
        log.opt(depth=1).error(f"❌ API Response Failed: {api_name}, RequestId={request_id}")
        if full_response:
            log.opt(depth=1).error(f"📥 Response: {full_response}")


def log_code_execution_output(request_id: str, raw_output: str) -> None:
    """
    Extract and log the actual code execution output from run_code response.
    
    Args:
        request_id: Request ID from the API response
        raw_output: Raw JSON output from the MCP tool
    """
    import json
    
    try:
        # Parse the JSON response to extract the actual code output
        response = json.loads(raw_output)
        
        # Extract text from all content items
        texts = []
        if isinstance(response, dict) and 'content' in response:
            for item in response.get('content', []):
                if isinstance(item, dict) and item.get('type') == 'text':
                    texts.append(item.get('text', ''))
        
        if not texts:
            return
        
        actual_output = ''.join(texts)
        
        # Format the output with a clear separator
        header = f"📋 Code Execution Output (RequestID: {request_id}):"
        colored_header = f"{COLOR_GREEN}{header}{COLOR_RESET}"
        
        log.opt(depth=1).info(colored_header)
        
        # Print each line with indentation
        lines = actual_output.rstrip('\n').split('\n')
        for line in lines:
            colored_line = f"{COLOR_GREEN}   {line}{COLOR_RESET}"
            log.opt(depth=1).info(colored_line)
            
    except (json.JSONDecodeError, KeyError, TypeError):
        # If parsing fails, just return without logging
        pass


def log_operation_start(operation: str, details: str = "") -> None:
    """Log the start of an operation."""
    log.opt(depth=1).info(f"🚀 Starting: {operation}")
    if details:
        log.opt(depth=1).debug(f"📋 Details: {details}")


def log_operation_success(operation: str, result: str = "") -> None:
    """Log successful operation completion."""
    log.opt(depth=1).info(f"✅ Completed: {operation}")
    if result:
        log.opt(depth=1).debug(f"📊 Result: {result}")


def log_operation_error(operation: str, error: str, exc_info: bool = False) -> None:
    """
    Log operation error with optional exception info.

    Args:
        operation: Name of the operation that failed
        error: Error message
        exc_info: Whether to include exception traceback
    """
    if exc_info:
        log.opt(depth=1).exception(f"❌ Failed: {operation}")
    else:
        log.opt(depth=1).error(f"❌ Failed: {operation}")
        log.opt(depth=1).error(f"💥 Error: {error}")


def log_warning(message: str, details: str = "") -> None:
    """Log warning with consistent formatting."""
    log.opt(depth=1).warning(f"⚠️  {message}")
    if details:
        log.opt(depth=1).warning(f"📝 Details: {details}")
