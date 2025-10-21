# TypeScript Logging Configuration

## Overview

The TypeScript SDK provides comprehensive logging with support for multiple log levels, automatic sensitive data masking, and RequestID tracking for correlating log messages.

## Setting Log Level

### Priority System (Highest to Lowest)

1. **Code-level setup** - `setLogLevel()` can be called after import
2. **Environment variables** - `LOG_LEVEL` (MUST be set BEFORE import)
3. **Default values** - INFO level

### Method 1: Environment Variable (Must be BEFORE Import)

Set environment variables BEFORE your code runs:

```bash
export LOG_LEVEL=DEBUG
npx ts-node script.ts
```

**Critical**: Environment variables are read at module import time. Setting them after import has NO effect.

### Method 2: Code-Level Setup (After Import)

```typescript
import { setLogLevel, getLogLevel } from '@aliyun/wuying-agentbay-sdk';

// Set log level - works at any time after import
setLogLevel('DEBUG');

// Check current level
const level = getLogLevel();
```

### Method 3: Set in Entry Point BEFORE Import

```typescript
// MUST be before import
process.env.LOG_LEVEL = 'DEBUG';

import { setLogLevel } from '@aliyun/wuying-agentbay-sdk';
// Now this works with the environment variable value
setLogLevel('DEBUG');
```

## Log Levels

| Level | Use Case |
|-------|----------|
| **TRACE** | Very detailed diagnostic information |
| **DEBUG** | Detailed information for debugging |
| **INFO** | Default - important events |
| **WARN** | Issues but not failures |
| **ERROR** | Failures |
| **FATAL** | System is unusable |

Filter rule: **Only logs at your level or HIGHER severity are shown**.

## Logging Functions

### Basic Logging

```typescript
import {
    logTrace,
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

### RequestID Tracking

Track related log messages with RequestID:

```typescript
import {
    setRequestId,
    getRequestId,
    clearRequestId,
    logInfo
} from '@aliyun/wuying-agentbay-sdk';

// Set RequestID for correlation
setRequestId('req-12345-xyz');
logInfo('Processing request'); // Will include RequestID

// Get current RequestID
const id = getRequestId();

// Clear RequestID
clearRequestId();
logInfo('After clearing'); // No RequestID
```

## API Logging

### Enable/Disable API Logging

```typescript
import {
    setApiLogging
} from '@aliyun/wuying-agentbay-sdk';

// Enable API logging
setApiLogging(true);

// Disable API logging
setApiLogging(false);
```

### Environment Variable

```bash
export ENABLE_API_LOGGING=true
npx ts-node script.ts
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

## Important: Environment Variable Timing

### Why TypeScript Cannot Use AGENTBAY_LOG_LEVEL

TypeScript reads environment variables at **module import time**, not at runtime. This is a JavaScript/Node.js limitation:

```typescript
// ❌ This does NOT work:
process.env.LOG_LEVEL = 'DEBUG';  // Set after import starts
import { getLogLevel } from '@aliyun/wuying-agentbay-sdk';
console.log(getLogLevel());  // Still INFO, not DEBUG

// ✅ This DOES work:
// Set environment variable BEFORE Node.js starts:
// $ LOG_LEVEL=DEBUG npx ts-node script.ts
```

The environment variable is read during module initialization. After the module is loaded, changing the environment variable has no effect.

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
export LOG_LEVEL=WARN
node dist/index.js
```

**With RequestID tracking**:
```typescript
import { setRequestId, logInfo } from '@aliyun/wuying-agentbay-sdk';

setRequestId('req-user-123');
logInfo('Processing user request');

setRequestId('req-order-456');
logInfo('Processing order');

// Check logs to see request correlation
```
