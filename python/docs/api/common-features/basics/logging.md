# Logging API Reference

Unified logging configuration for AgentBay SDK using loguru.

This module provides a centralized logging configuration with beautiful formatting
and structured output for different log levels.

#### COLOR\_RESET

```python
COLOR_RESET = "\033[0m"
```

#### COLOR\_GREEN

```python
COLOR_GREEN = "\033[32m"
```

#### COLOR\_BLUE

```python
COLOR_BLUE = "\033[34m"
```

#### COLOR\_CYAN

```python
COLOR_CYAN = "\033[36m"
```

#### colorize\_log\_message

```python
def colorize_log_message(record)
```

Colorize log messages based on content.
API Calls are blue, Responses are green, Operations are cyan.
This filter modifies the message in the record and returns True to accept it.

## AgentBayLogger Objects

```python
class AgentBayLogger()
```

AgentBay SDK Logger with beautiful formatting.

#### setup

```python
@classmethod
def setup(cls,
          level: str = "INFO",
          log_file: Optional[Union[str, Path]] = None,
          enable_console: bool = True,
          enable_file: bool = True,
          rotation: Optional[str] = None,
          retention: str = "30 days",
          max_file_size: Optional[str] = None,
          colorize: Optional[bool] = None,
          force_reinit: bool = True) -> None
```

Setup the logger with custom configuration.

This method should be called early in your application, before any logging occurs.
By default, it will not reinitialize if already configured. Use force_reinit=True
to override existing configuration.

**Arguments**:

    level: Log level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
    log_file: Path to log file (optional)
    enable_console: Whether to enable console logging
    enable_file: Whether to enable file logging
    rotation: Log file rotation size (deprecated, use max_file_size)
    retention: Log file retention period
    max_file_size: Maximum log file size before rotation (e.g., "10 MB", "100 MB")
    colorize: Whether to use colors in console output (None = auto-detect)
    force_reinit: Force reinitialization even if already initialized (default: False)
  

**Example**:

  Configure logging for different scenarios
  

```python
from agentbay.logger import AgentBayLogger, get_logger

# Basic setup with debug level
AgentBayLogger.setup(level="DEBUG")
logger = get_logger("app")
logger.debug("Debug mode enabled")
# Output: Debug mode enabled

# Setup with custom log file and rotation
AgentBayLogger.setup(
level="INFO",
log_file="/var/log/agentbay/app.log",
max_file_size="50 MB",
retention="7 days"
)
logger = get_logger("app")
logger.info("Application started with file logging")
# Output: Application started with file logging
# Also written to /var/log/agentbay/app.log

# Console-only logging without colors (for CI/CD)
AgentBayLogger.setup(
level="WARNING",
enable_file=False,
colorize=False
)
logger = get_logger("ci")
logger.warning("This is a warning in CI environment")
# Output: This is a warning in CI environment (no colors)

# File-only logging (no console output)
AgentBayLogger.setup(
level="DEBUG",
log_file="/tmp/debug.log",
enable_console=False,
enable_file=True
)
logger = get_logger("debug")
logger.debug("This only appears in the log file")
# No console output, but written to /tmp/debug.log

```

#### get\_logger

```python
@classmethod
def get_logger(cls, name: Optional[str] = None)
```

Get a logger instance.

**Arguments**:

    name: Logger name (optional)
  

**Returns**:

  Configured logger instance

#### set\_level

```python
@classmethod
def set_level(cls, level: str) -> None
```

Set the logging level.

**Arguments**:

    level: New log level
  

**Example**:

  Change log level during runtime
  

```python
from agentbay.logger import AgentBayLogger, get_logger

# Start with INFO level
AgentBayLogger.setup(level="INFO")
logger = get_logger("app")

logger.info("This will appear")
# Output: This will appear
logger.debug("This won't appear")
# No output (DEBUG < INFO)

# Change to DEBUG level at runtime
AgentBayLogger.set_level("DEBUG")
logger.debug("Now debug messages appear")
# Output: Now debug messages appear

# Change to WARNING level
AgentBayLogger.set_level("WARNING")
logger.info("This won't appear anymore")
# No output (INFO < WARNING)
logger.warning("But warnings still appear")
# Output: But warnings still appear

```

#### get\_logger

```python
def get_logger(name: str = "agentbay")
```

Convenience function to get a named logger.

**Arguments**:

    name: Logger name (defaults to "agentbay")
  

**Returns**:

  Named logger instance

#### log

```python
log = get_logger("agentbay")
```

#### SENSITIVE\_FIELDS

```python
SENSITIVE_FIELDS = [
    'api_key',
    'apikey',
    'api-key',
    'password',
    'passwd',
    ' ...
```

#### mask\_sensitive\_data

```python
def mask_sensitive_data(data: Any, fields: List[str] = None) -> Any
```

Mask sensitive information in data structures.

**Arguments**:

    data: Data to mask (dict, str, list, etc.)
    fields: Additional sensitive field names
  

**Returns**:

  Masked data (deep copy)
  

**Example**:

  Mask sensitive information in various data structures
  

```python
from agentbay.logger import mask_sensitive_data

# Mask API keys and passwords in a dictionary
user_data = {
  "username": "john_doe",
  "password": "secret123",
  "api_key": "sk_live_1234567890abcdef",
  "email": "john@example.com"
}
masked = mask_sensitive_data(user_data)
print(masked)
# Output: {'username': 'john_doe', 'password': '****', 'api_key': 'sk****ef', 'email': 'john@example.com'}

# Mask nested dictionaries
config = {
  "database": {
  "host": "localhost",
  "password": "db_password_123"
},
  "auth": {
  "token": "Bearer xyz123abc456"
}
}
masked_config = mask_sensitive_data(config)
print(masked_config)
# Output: {'database': {'host': 'localhost', 'password': '****'}, 'auth': {'token': 'Be****56'}}

# Mask with custom field names
custom_data = {
  "user_id": "12345",
  "credit_card": "1234-5678-9012-3456",
  "ssn": "123-45-6789"
}
masked_custom = mask_sensitive_data(custom_data, fields=['credit_card', 'ssn'])
print(masked_custom)
# Output: {'user_id': '12345', 'credit_card': '12****56', 'ssn': '12****89'}

# Mask lists containing sensitive data
user_list = [
  {"name": "Alice", "api_key": "key_alice_123"},
  {"name": "Bob", "api_key": "key_bob_456"}
]
masked_list = mask_sensitive_data(user_list)
print(masked_list)
# Output: [{'name': 'Alice', 'api_key': 'ke****23'}, {'name': 'Bob', 'api_key': 'ke****56'}]

```

#### log\_api\_call

```python
def log_api_call(api_name: str, request_data: str = "") -> None
```

Log API call with consistent formatting.

#### log\_api\_response

```python
def log_api_response(response_data: str, success: bool = True) -> None
```

Log API response with consistent formatting.

#### log\_api\_response\_with\_details

```python
def log_api_response_with_details(api_name: str,
                                  request_id: str = "",
                                  success: bool = True,
                                  key_fields: Dict[str, Any] = None,
                                  full_response: str = "") -> None
```

Log API response with key details at INFO level.

**Arguments**:

    api_name: Name of the API being called
    request_id: Request ID from the response
    success: Whether the API call was successful
    key_fields: Dictionary of key business fields to log
    full_response: Full response body (logged at DEBUG level)

#### log\_code\_execution\_output

```python
def log_code_execution_output(request_id: str, raw_output: str) -> None
```

Extract and log the actual code execution output from run_code response.

**Arguments**:

    request_id: Request ID from the API response
    raw_output: Raw JSON output from the MCP tool

#### log\_operation\_start

```python
def log_operation_start(operation: str, details: str = "") -> None
```

Log the start of an operation.

#### log\_operation\_success

```python
def log_operation_success(operation: str, result: str = "") -> None
```

Log successful operation completion.

#### log\_operation\_error

```python
def log_operation_error(operation: str,
                        error: str,
                        exc_info: bool = False) -> None
```

Log operation error with optional exception info.

**Arguments**:

    operation: Name of the operation that failed
    error: Error message
    exc_info: Whether to include exception traceback

#### log\_warning

```python
def log_warning(message: str, details: str = "") -> None
```

Log warning with consistent formatting.

#### log\_info\_with\_color

```python
def log_info_with_color(message: str, color: str = "\033[31m") -> None
```

Log an INFO level message with custom color.

**Arguments**:

    message: Message to log
    color: ANSI color code (default is red: [31m)

---

*Documentation generated automatically from source code using pydoc-markdown.*
