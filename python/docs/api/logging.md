# Python Logging Configuration

## Overview

The Python SDK uses `loguru` for comprehensive logging with support for console output, file logging, and automatic sensitive data masking.

## Setting Log Level

### Priority System (Highest to Lowest)

1. **setup() method** - Most reliable way to set log level
2. **Environment variables** - `AGENTBAY_LOG_LEVEL`
3. **Default values** - INFO level

### Method 1: Using setup() (Recommended)

Use the `setup()` method to configure logging:

```python
from agentbay.logger import AgentBayLogger, get_logger

# Configure logging level
AgentBayLogger.setup(level="DEBUG")

logger = get_logger("my_app")
logger.debug("Now in debug mode")  # This will appear
```

### Method 2: Environment Variable

Set before running your script:

```bash
export AGENTBAY_LOG_LEVEL=DEBUG
python your_script.py
```

### Method 3: Change Level During Runtime

Use `set_level()` to change level while program is running:

```python
from agentbay.logger import AgentBayLogger

# Change level at runtime
AgentBayLogger.set_level("WARNING")
```

**Note**: `set_level()` automatically reinitializes the logger with the new level.

## Log Levels

| Level | Use Case |
|-------|----------|
| **DEBUG** | Development - see everything |
| **INFO** | Default - important events |
| **WARNING** | Issues but not failures |
| **ERROR** | Only failures |

Filter rule: **Only logs at your level or HIGHER severity are shown**.

## File Logging

Python SDK logs to a file by default.

### Default Log File

```
python/agentbay.log
```

### Custom Log File Location

```python
from agentbay.logger import AgentBayLogger, get_logger

# Configure custom log file location
AgentBayLogger.setup(
    level="DEBUG",
    log_file="/custom/path/app.log"
)

logger = get_logger("app")
```

### File Rotation and Retention

Configure automatic log file rotation:

```python
from agentbay.logger import AgentBayLogger

AgentBayLogger.setup(
    level="DEBUG",
    log_file="/var/log/myapp.log",
    rotation="100 MB",     # Rotate when file reaches 100 MB
    retention="30 days"    # Keep logs for 30 days
)
```

## Sensitive Data Masking

The SDK automatically masks sensitive information:

```python
from agentbay.logger import mask_sensitive_data

data = {
    "api_key": "sk_live_1234567890",
    "password": "secret123",
    "auth_token": "Bearer xyz"
}

masked = mask_sensitive_data(data)
# Result: api_key masked, password masked, auth_token masked
```

Automatically masked fields:
- api_key, apikey, api-key
- password, passwd, pwd
- token, access_token, auth_token
- secret, private_key
- authorization

Custom fields can also be masked by passing them as parameters.

## Quick Reference

**Development (see everything)**:
```bash
export AGENTBAY_LOG_LEVEL=DEBUG
python main.py
```

**Testing (important events only)**:
```bash
python test_suite.py
# Uses default INFO level
```

**Production (problems only)**:
```bash
export AGENTBAY_LOG_LEVEL=WARNING
python app.py
```

**Debugging with file output**:
```python
from agentbay.logger import AgentBayLogger, get_logger

AgentBayLogger.setup(
    level="DEBUG",
    log_file="/var/log/debug.log",
    enable_console=False
)
logger = get_logger("app")
```
