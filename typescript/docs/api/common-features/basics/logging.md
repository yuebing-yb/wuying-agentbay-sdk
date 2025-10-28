# TypeScript Logging Configuration

## Overview

The TypeScript SDK provides comprehensive logging with support for multiple log levels and automatic sensitive data masking.

## Setting Log Level

### Priority System (Highest to Lowest)

1. **Code-level setup** - `setLogLevel()` can be called after import
2. **Environment variables** - `LOG_LEVEL` or `AGENTBAY_LOG_LEVEL`
3. **.env file** - Automatically loaded from current directory or parent directories
4. **Default values** - INFO level

### Method 1: Environment Variable

**Option A: Using .env File (Recommended)**

Create a `.env` file in your project root:

```
# .env file
LOG_LEVEL=DEBUG
# or
AGENTBAY_LOG_LEVEL=DEBUG
```

The SDK automatically loads `.env` files from the current directory or parent directories.

**Option B: Command Line Environment Variable**

Set environment variables when running your script:

```bash
export LOG_LEVEL=DEBUG
npx ts-node script.ts
```

### Method 2: Code-Level Setup

```typescript
import { setLogLevel, getLogLevel } from '@aliyun/wuying-agentbay-sdk';

// Set log level - works at any time after import
setLogLevel('DEBUG');

// Check current level
const level = getLogLevel();
```

## Log Levels

| Level | Use Case |
|-------|----------|
| **DEBUG** | Development - see everything |
| **INFO** | Default - important events |
| **WARN** | Issues but not failures |
| **ERROR** | Only failures |

Filter rule: **Only logs at your level or HIGHER severity are shown**.

## Logging Functions

### Basic Logging

```typescript
import {
    logDebug,
    logInfo,
    logWarn,
    logError
} from '@aliyun/wuying-agentbay-sdk';

logDebug('Message with arguments', arg1, arg2);
logInfo('Information message');
logWarn('Warning message');
logError('Error message');
```

## File Logging

The TypeScript SDK supports logging to files with automatic rotation.

### Basic File Logging

```typescript
import { setupLogger } from '@aliyun/wuying-agentbay-sdk';

// Configure file logging
setupLogger({
    level: 'DEBUG',
    logFile: '/path/to/app.log'
});
```

### File Rotation

Configure automatic log file rotation when the file reaches a certain size:

```typescript
import { setupLogger } from '@aliyun/wuying-agentbay-sdk';

setupLogger({
    level: 'DEBUG',
    logFile: '/var/log/myapp.log',
    maxFileSize: '100 MB'  // Rotate when file reaches 100 MB
});
```

Supported size units:
- `KB` - Kilobytes
- `MB` - Megabytes (default)
- `GB` - Gigabytes

Default max file size is 10 MB if not specified. When rotation occurs, the current log file is renamed to `<filename>.1`.

### Console and File Logging

You can control whether logs are written to console and/or file:

```typescript
import { setupLogger } from '@aliyun/wuying-agentbay-sdk';

// Log to file only (disable console output)
setupLogger({
    level: 'DEBUG',
    logFile: '/var/log/app.log',
    enableConsole: false
});

// Log to both console and file (default)
setupLogger({
    level: 'DEBUG',
    logFile: '/var/log/app.log',
    enableConsole: true
});
```

### LoggerConfig Options

```typescript
interface LoggerConfig {
  level?: LogLevel;           // Log level: 'DEBUG' | 'INFO' | 'WARN' | 'ERROR'
  logFile?: string;           // Path to log file (undefined = no file logging)
  maxFileSize?: string;       // Max file size before rotation (e.g., "10 MB", "100 MB", "1 GB")
  enableConsole?: boolean;    // Enable/disable console output (default: true)
}
```

## Sensitive Data Masking

The SDK automatically masks sensitive information:

```typescript
import { maskSensitiveData } from '@aliyun/wuying-agentbay-sdk';

const data = {
    api_key: 'sk_live_1234567890',
    password: 'secret123',
    auth_token: 'Bearer xyz'
};

const masked = maskSensitiveData(data);
// Result: api_key masked, password masked, auth_token masked
```

Automatically masked fields:
- api_key, apikey, api-key
- password, passwd, pwd
- token, access_token, auth_token
- secret, private_key
- authorization

Custom fields can be masked by passing them as parameters:

```typescript
const masked = maskSensitiveData(data, ['custom_secret', 'ssn']);
```

## Environment Variable Support

The TypeScript SDK supports both `LOG_LEVEL` and `AGENTBAY_LOG_LEVEL` environment variables for configuration.

### .env File Auto-Loading

The SDK automatically searches for and loads `.env` files from:
1. Current working directory
2. Parent directories (recursive search up to root)
3. Git repository root (if found)

**Example `.env` file:**

```
# Logging configuration
LOG_LEVEL=DEBUG

# Or use the prefixed version
AGENTBAY_LOG_LEVEL=DEBUG

# API configuration
AGENTBAY_API_KEY=your_api_key_here
```

The SDK loads the `.env` file automatically on import, so you don't need any additional configuration code.

## Quick Reference

**Development (see everything)**:
```bash
export LOG_LEVEL=DEBUG
npx ts-node script.ts
```

**Testing (important events only)**:
```bash
npx ts-node test.ts
# Uses default INFO level
```

**Production (problems only)**:
```bash
export LOG_LEVEL=ERROR
node dist/index.js
```
