# Go Logging Configuration

## Overview

The Go SDK provides simple and efficient logging with support for multiple log levels, automatic sensitive data masking, and color detection for terminal output.

## Setting Log Level

### Priority System (Highest to Lowest)

1. **Code-level setup** - `agentbay.SetLogLevel()` can be called at any time
2. **Environment variables** - `AGENTBAY_LOG_LEVEL`
3. **Default values** - INFO level

### Method 1: Environment Variable

Set before running your program:

```bash
export AGENTBAY_LOG_LEVEL=DEBUG
go run main.go
```

### Method 2: Code-Level Setup (Can be done anytime)

Set in your code - this overrides environment variables:

```go
import "github.com/aliyun/wuying-agentbay-sdk/golang/pkg/agentbay"

// Set in your code - has priority over environment variable
agentbay.SetLogLevel(agentbay.LOG_DEBUG)

// Check current level
currentLevel := agentbay.GetLogLevel()
```

**Important**: `SetLogLevel()` can be called at any time and will take priority over environment variables.

## Log Levels

| Constant | Level | Use Case |
|----------|-------|----------|
| **LOG_DEBUG** | 0 | Development - see everything |
| **LOG_INFO** | 1 | Default - important events |
| **LOG_WARN** | 2 | Issues but not failures |
| **LOG_ERROR** | 3 | Only failures |

Filter rule: **Only logs at your level or HIGHER severity are shown**.

## API Reference

### SetLogLevel

```go
agentbay.SetLogLevel(level int)
```

Set the global log level. Valid levels: LOG_DEBUG, LOG_INFO, LOG_WARN, LOG_ERROR.

### GetLogLevel

```go
level := agentbay.GetLogLevel() // Returns int
```

Get the current log level.

## Sensitive Data Masking

The SDK automatically masks sensitive information:

```go
data := map[string]interface{}{
    "api_key": "sk_live_1234567890",
    "password": "secret123",
    "auth_token": "Bearer xyz",
}

masked := agentbay.MaskSensitiveData(data)
// Result: api_key masked, password masked, auth_token masked
```

Automatically masked fields:
- api_key, apikey, api-key
- password, passwd, pwd
- token, access_token, auth_token
- secret, private_key
- authorization

## Quick Reference

**Development (see everything)**:
```bash
export AGENTBAY_LOG_LEVEL=DEBUG
go run main.go
```

**Testing (important events only)**:
```bash
go run main.go
# Uses default INFO level
```

**Production (problems only)**:
```bash
export AGENTBAY_LOG_LEVEL=WARN
go run main.go
```

**Runtime control**:
```go
package main

import (
    "github.com/aliyun/wuying-agentbay-sdk/golang/pkg/agentbay"
)

func main() {
    // Set to DEBUG initially
    agentbay.SetLogLevel(agentbay.LOG_DEBUG)

    // Later in the program
    agentbay.SetLogLevel(agentbay.LOG_WARN)
}
```
