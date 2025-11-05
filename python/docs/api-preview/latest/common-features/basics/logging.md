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

- `level` - Log level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
- `log_file` - Path to log file (optional)
- `enable_console` - Whether to enable console logging
- `enable_file` - Whether to enable file logging
- `rotation` - Log file rotation size (deprecated, use max_file_size)
- `retention` - Log file retention period
- `max_file_size` - Maximum log file size before rotation (e.g., "10 MB", "100 MB")
- `colorize` - Whether to use colors in console output (None = auto-detect)
- `force_reinit` - Force reinitialization even if already initialized (default: False)
  

**Example**:

  >>> from agentbay.logger import AgentBayLogger
  >>> AgentBayLogger.setup(level="DEBUG", max_file_size="10 MB")

#### get\_logger

```python
@classmethod
def get_logger(cls, name: Optional[str] = None)
```

Get a logger instance.

**Arguments**:

- `name` - Logger name (optional)
  

**Returns**:

  Configured logger instance

#### set\_level

```python
@classmethod
def set_level(cls, level: str) -> None
```

Set the logging level.

**Arguments**:

- `level` - New log level

#### get\_logger

```python
def get_logger(name: str = "agentbay")
```

Convenience function to get a named logger.

**Arguments**:

- `name` - Logger name (defaults to "agentbay")
  

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

- `data` - Data to mask (dict, str, list, etc.)
- `fields` - Additional sensitive field names
  

**Returns**:

  Masked data (deep copy)

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

- `api_name` - Name of the API being called
- `request_id` - Request ID from the response
- `success` - Whether the API call was successful
- `key_fields` - Dictionary of key business fields to log
- `full_response` - Full response body (logged at DEBUG level)

#### log\_code\_execution\_output

```python
def log_code_execution_output(request_id: str, raw_output: str) -> None
```

Extract and log the actual code execution output from run_code response.

**Arguments**:

- `request_id` - Request ID from the API response
- `raw_output` - Raw JSON output from the MCP tool

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

- `operation` - Name of the operation that failed
- `error` - Error message
- `exc_info` - Whether to include exception traceback

#### log\_warning

```python
def log_warning(message: str, details: str = "") -> None
```

Log warning with consistent formatting.

---

*Documentation generated automatically from source code using pydoc-markdown.*
