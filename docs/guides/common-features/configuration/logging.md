# Logging

Configure logging levels and output for your AgentBay application across all SDK languages.

## Quick Start

### Enable Debug Logging

**Python**
```python
from agentbay.logger import AgentBayLogger
AgentBayLogger.setup(level="DEBUG")
```

**Go**
```go
agentbay.SetLogLevel(agentbay.LOG_DEBUG)
```

**TypeScript**
```typescript
import { setLogLevel } from './path/to/logger';
setLogLevel('DEBUG');
```

### Set Log File

**Python**
```python
AgentBayLogger.setup(level="INFO", log_file="/path/to/app.log")
```

**Go**
```go
// Logs are written to stdout by default
// Configure file output in your application as needed
```

**TypeScript**
```typescript
// Logs output to console only
// Configure file output in your application as needed
```

## Log Levels

| Level | Usage | Priority |
|-------|-------|----------|
| **DEBUG** | Detailed information for debugging | Lowest |
| **INFO** | General operational information | Normal (default) |
| **WARN** | Warning messages for potential issues | Higher |
| **ERROR** | Error information | Highest |

### Set Log Level

**Python**
```python
AgentBayLogger.setup(level="DEBUG")  # or "INFO", "WARN", "ERROR"
```

**Go**
```go
agentbay.SetLogLevel(agentbay.LOG_DEBUG)
agentbay.SetLogLevel(agentbay.LOG_INFO)
agentbay.SetLogLevel(agentbay.LOG_WARN)
agentbay.SetLogLevel(agentbay.LOG_ERROR)
```

**TypeScript**
```typescript
setLogLevel('DEBUG');  // or 'TRACE', 'INFO', 'WARN', 'ERROR', 'FATAL'
```

## Environment Variables

Control logging behavior via environment variables:

| Variable | Values | Purpose |
|----------|--------|---------|
| `AGENTBAY_LOG_LEVEL` | DEBUG, INFO, WARN, ERROR | Set global log level (Python) |
| `LOG_LEVEL` | TRACE, DEBUG, INFO, WARN, ERROR, FATAL | Set global log level (TypeScript) |
| `FORCE_COLOR` | 1, true | Force colored output in non-TTY environments |
| `DISABLE_COLORS` | 1, true | Disable colored output (highest priority) |

### Priority Order

1. **DISABLE_COLORS** = '1' → Colors OFF
2. **FORCE_COLOR** = '1' → Colors ON
3. **TTY Detection** → Colors ON (terminal detected)
4. **IDE Detection** → Colors ON (VS Code, GoLand, IntelliJ detected)
5. **Default** → Colors OFF (files, CI/CD, pipes)

## Features

### Automatic Sensitive Data Masking

The SDK automatically masks:
- API keys and tokens
- Passwords
- Authorization headers
- Database secrets

Example: `api_key: "sk_live_abc1234567890"` → `api_key: "sk****90"`

### Python: File Rotation

Log files are automatically rotated when they exceed size limits:

```python
AgentBayLogger.setup(
    level="INFO",
    log_file="/path/to/app.log",
    rotation="10 MB",      # Rotate at 10 MB
    retention="30 days"    # Keep logs for 30 days
)
```

## Examples

### Development Setup

**Python**
```python
from agentbay import AgentBay
from agentbay.logger import AgentBayLogger

# Enable detailed logging
AgentBayLogger.setup(level="DEBUG", log_file="app.log")

client = AgentBay(api_key="your-api-key")
```

**Go**
```go
package main

import (
    "github.com/aliyun/wuying-agentbay-sdk/golang/pkg/agentbay"
)

func main() {
    agentbay.SetLogLevel(agentbay.LOG_DEBUG)
    // Your code here
}
```

**TypeScript**
```typescript
import { AgentBay } from '@aliyun/wuying-agentbay-sdk';
import { setLogLevel } from '@aliyun/wuying-agentbay-sdk/utils/logger';

setLogLevel('DEBUG');

const client = new AgentBay({ apiKey: 'your-api-key' });
```

### Production Setup

```bash
# Disable debug output
export AGENTBAY_LOG_LEVEL=INFO
export LOG_LEVEL=INFO

# Disable colors for log aggregation services
export DISABLE_COLORS=1

# Run your application
python main.py
```

## Common Questions

**Q: Where are log files stored?**
- Python: Default location is `python/agentbay.log` or use `log_file` parameter to customize
- Go: Output to stdout by default
- TypeScript: Output to console only

**Q: Why is DEBUG log level slower?**
- DEBUG level includes additional diagnostic information and network request details
- Use INFO level for production deployments

**Q: How do I see API calls and responses?**
- Enable DEBUG level to see detailed API call information
- Sensitive data like API keys are automatically masked

**Q: Do I need to configure logging?**
- No, logging works out-of-the-box with INFO level as default
- Configure only when you need DEBUG information or custom file output
