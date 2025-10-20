/**
 * Utility functions for structured logging with multiple levels, API tracking,
 * sensitive data masking, and RequestID management.
 */

/**
 * Log level type
 */
export type LogLevel = 'DEBUG' | 'INFO' | 'WARNING' | 'ERROR';

/**
 * RequestID storage for tracking across API calls
 */
let currentRequestId = '';

/**
 * Sensitive field names for data masking
 */
const SENSITIVE_FIELDS = [
  'api_key', 'apikey', 'api-key',
  'password', 'passwd', 'pwd',
  'token', 'access_token', 'auth_token',
  'secret', 'private_key', 'authorization',
];

/**
 * Get emoji for log level
 */
function getLogLevelEmoji(level: LogLevel): string {
  switch (level) {
    case 'DEBUG':
      return '🐛 DEBUG';
    case 'INFO':
      return 'ℹ️  INFO';
    case 'WARNING':
      return '⚠️  WARNING';
    case 'ERROR':
      return '❌ ERROR';
    default:
      return level;
  }
}

/**
 * Format log message with level and RequestID
 */
function formatLogMessage(level: LogLevel, message: string): string {
  let formattedMessage = `${getLogLevelEmoji(level)}: ${message}`;
  if (currentRequestId) {
    formattedMessage += ` [RequestId=${currentRequestId}]`;
  }
  return formattedMessage;
}

/**
 * Mask sensitive information in data structures
 * @param data Data to mask (dict, str, list, etc.)
 * @param fields Additional sensitive field names
 * @returns Masked data (deep copy)
 */
export function maskSensitiveData(data: any, fields?: string[]): any {
  const sensitiveFields = fields || SENSITIVE_FIELDS;
  const visitedObjects = new WeakSet();

  function mask(obj: any): any {
    if (obj === null || obj === undefined) {
      return obj;
    }

    if (typeof obj === 'object') {
      if (visitedObjects.has(obj)) {
        return '[Circular]';
      }
      visitedObjects.add(obj);

      if (Array.isArray(obj)) {
        return obj.map(item => mask(item));
      }

      const masked: any = {};
      for (const key in obj) {
        if (Object.prototype.hasOwnProperty.call(obj, key)) {
          const value = obj[key];
          if (sensitiveFields.some(field => key.toLowerCase().includes(field.toLowerCase()))) {
            if (typeof value === 'string' && value.length > 4) {
              masked[key] = value.substring(0, 2) + '****' + value.substring(value.length - 2);
            } else {
              masked[key] = '****';
            }
          } else {
            masked[key] = mask(value);
          }
        }
      }
      return masked;
    }

    if (typeof obj === 'string') {
      return obj;
    }

    return obj;
  }

  return mask(data);
}

/**
 * Set the RequestID for tracking
 * @param requestId The RequestID to set
 */
export function setRequestId(requestId: string): void {
  currentRequestId = requestId;
}

/**
 * Get the current RequestID
 * @returns The current RequestID or empty string
 */
export function getRequestId(): string {
  return currentRequestId;
}

/**
 * Clear the current RequestID
 */
export function clearRequestId(): void {
  currentRequestId = '';
}

/**
 * Log a message without the log prefix and file location
 * @param message The message to log
 * @param args Optional arguments to log
 */
export function log(message: string, ...args: any[]): void {
  process.stdout.write(message + "\n");

  if (args.length > 0) {
    for (const arg of args) {
      if (typeof arg === "object" && arg !== null) {
        process.stdout.write(JSON.stringify(arg, null, 2) + "\n");
      } else if (arg !== null && arg !== undefined) {
        process.stdout.write(String(arg) + "\n");
      }
    }
  }
}

/**
 * Log an info level message
 * @param message The message to log
 * @param args Optional arguments to log
 */
export function logInfo(message: string, ...args: any[]): void {
  const formattedMessage = formatLogMessage('INFO', message);
  process.stdout.write(formattedMessage + "\n");

  if (args.length > 0) {
    for (const arg of args) {
      if (typeof arg === "object" && arg !== null) {
        process.stdout.write(JSON.stringify(arg, null, 2) + "\n");
      } else if (arg !== null && arg !== undefined) {
        process.stdout.write(String(arg) + "\n");
      }
    }
  }
}

/**
 * Log a debug level message
 * @param message The message to log
 * @param args Optional arguments to log
 */
export function logDebug(message: string, ...args: any[]): void {
  const formattedMessage = formatLogMessage('DEBUG', message);
  process.stdout.write(formattedMessage + "\n");

  if (args.length > 0) {
    for (const arg of args) {
      if (typeof arg === "object" && arg !== null) {
        process.stdout.write(JSON.stringify(arg, null, 2) + "\n");
      } else if (arg !== null && arg !== undefined) {
        process.stdout.write(String(arg) + "\n");
      }
    }
  }
}

/**
 * Log a warning level message
 * @param message The message to log
 * @param args Optional arguments to log
 */
export function logWarn(message: string, ...args: any[]): void {
  const formattedMessage = formatLogMessage('WARNING', message);
  process.stdout.write(formattedMessage + "\n");

  if (args.length > 0) {
    for (const arg of args) {
      if (typeof arg === "object" && arg !== null) {
        process.stdout.write(JSON.stringify(arg, null, 2) + "\n");
      } else if (arg !== null && arg !== undefined) {
        process.stdout.write(String(arg) + "\n");
      }
    }
  }
}

/**
 * Log an error message with optional error object
 * @param message The error message to log
 * @param error Optional error object
 */
export function logError(message: string, error?: any): void {
  const formattedMessage = formatLogMessage('ERROR', message);
  process.stderr.write(formattedMessage + "\n");

  if (error) {
    if (error instanceof Error) {
      process.stderr.write(`${error.message}\n`);
      if (error.stack) {
        process.stderr.write(`Stack Trace:\n${error.stack}\n`);
      }
    } else if (typeof error === "object") {
      process.stderr.write(JSON.stringify(error, null, 2) + "\n");
    } else {
      process.stderr.write(String(error) + "\n");
    }
  }
}

/**
 * Log an API call
 * @param apiName Name of the API being called
 * @param requestData Optional request data to log at DEBUG level
 */
export function logAPICall(apiName: string, requestData?: any): void {
  const message = `🔗 API Call: ${apiName}`;
  logInfo(message);

  if (requestData) {
    const maskedData = maskSensitiveData(requestData);
    logDebug(`📤 Request: ${JSON.stringify(maskedData)}`);
  }
}

/**
 * Log an API response with key details at INFO level
 * @param apiName Name of the API being called
 * @param requestId Request ID from the response
 * @param success Whether the API call was successful
 * @param keyFields Dictionary of key business fields to log
 * @param fullResponse Full response body (logged at DEBUG level)
 */
export function logAPIResponseWithDetails(
  apiName: string,
  requestId?: string,
  success = true,
  keyFields?: Record<string, any>,
  fullResponse?: string
): void {
  if (success) {
    let mainMessage = `✅ API Response: ${apiName}`;
    if (requestId) {
      mainMessage += `, RequestId=${requestId}`;
    }
    logInfo(mainMessage);

    if (keyFields) {
      for (const [key, value] of Object.entries(keyFields)) {
        const maskedValue = maskSensitiveData({ [key]: value });
        logInfo(`  └─ ${key}=${maskedValue[key]}`);
      }
    }

    if (fullResponse) {
      logDebug(`📥 Full Response: ${fullResponse}`);
    }
  } else {
    let errorMessage = `❌ API Response Failed: ${apiName}`;
    if (requestId) {
      errorMessage += `, RequestId=${requestId}`;
    }
    logError(errorMessage);

    if (fullResponse) {
      logError(`📥 Response: ${fullResponse}`);
    }
  }
}

/**
 * Log operation start
 * @param operation Name of the operation
 * @param details Optional operation details
 */
export function logOperationStart(operation: string, details?: string): void {
  const message = `🚀 Starting: ${operation}`;
  logInfo(message);

  if (details) {
    logDebug(`📋 Details: ${details}`);
  }
}

/**
 * Log operation success
 * @param operation Name of the operation
 * @param result Optional operation result
 */
export function logOperationSuccess(operation: string, result?: string): void {
  const message = `✅ Completed: ${operation}`;
  logInfo(message);

  if (result) {
    logDebug(`📊 Result: ${result}`);
  }
}

/**
 * Log operation error
 * @param operation Name of the operation that failed
 * @param error Error message or error object
 * @param includeStackTrace Whether to include stack trace
 */
export function logOperationError(
  operation: string,
  error: string | Error,
  includeStackTrace = false
): void {
  const message = `❌ Failed: ${operation}`;

  if (typeof error === 'string') {
    logError(message, new Error(error));
  } else if (error instanceof Error) {
    if (includeStackTrace) {
      logError(message, error);
    } else {
      logError(message, error.message);
    }
  } else {
    logError(message, String(error));
  }
}
