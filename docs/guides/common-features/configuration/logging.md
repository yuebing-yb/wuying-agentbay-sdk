# Logging Configuration Guide

This guide shows how to configure logging in AgentBay SDK. Each language has its own documentation with specific details.

## Quick Links

- **[Python Logging Guide](../../../../python/docs/api/logging.md)** - Setup, configuration, and file logging
- **[Go Logging Guide](../../../../golang/docs/api/logging.md)** - Environment variables and code-level configuration
- **[TypeScript Logging Guide](../../../../typescript/docs/api/logging.md)** - Import-time setup and RequestID tracking

---

## Overview

All AgentBay SDKs provide:
- Multiple log levels (DEBUG, INFO, WARNING/WARN, ERROR)
- Environment variable configuration (AGENTBAY_LOG_LEVEL or LOG_LEVEL)
- Code-level setup
- Automatic sensitive data masking
- Color output detection

### Priority System (All Languages)

Log levels are applied in this order (highest to lowest):

1. **Code-level setup** (set in your code)
2. **Environment variables** (AGENTBAY_LOG_LEVEL)
3. **Default values** (INFO level)

---

## Python Example

### Set Log Level via Environment Variable

```bash
export AGENTBAY_LOG_LEVEL=DEBUG
python your_script.py
```

### Set Log Level in Code

```python
from agentbay.logger import AgentBayLogger, get_logger

# Set before first get_logger() call
AgentBayLogger._log_level = "DEBUG"

logger = get_logger("my_app")
logger.debug("Debug message")
logger.info("Info message")
```

### Available Log Levels

| Level | Use Case |
|-------|----------|
| **DEBUG** | Development - see everything |
| **INFO** | Default - important events |
| **WARNING** | Issues but not failures |
| **ERROR** | Only failures |

### File Logging (Python Only)

Python SDK writes logs to `python/agentbay.log` by default.

```python
from agentbay.logger import AgentBayLogger

# Configure file logging
AgentBayLogger._initialized = False
AgentBayLogger.setup(
    level="DEBUG",
    log_file="/var/log/myapp.log",
    rotation="100 MB",
    retention="30 days"
)
```

---

## Sensitive Data Masking

All SDKs automatically mask sensitive information:

- API keys, tokens, passwords
- Authorization headers
- Private keys

No configuration needed - it works automatically.

---

## For Language-Specific Details

See the documentation in each language directory:

- **Python**: `/python/docs/api/logging.md`
- **Go**: `/golang/docs/api/logging.md`
- **TypeScript**: `/typescript/docs/api/logging.md`

Each guide includes:
- Complete setup instructions
- All configuration options
- Code examples
- API reference
