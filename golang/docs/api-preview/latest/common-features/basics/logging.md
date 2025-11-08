# Logging API Reference

## 🚀 Related Tutorial

- [First Session Tutorial](../../../../../docs/quickstart/first-session.md) - Get started with creating your first AgentBay session

## Type LoggerConfig

```go
type LoggerConfig struct {
	Level		string
	LogFile		string
	MaxFileSize	string
	EnableConsole	*bool
}
```

LoggerConfig holds configuration for file logging

## Functions

### SetLogLevel

```go
func SetLogLevel(level int)
```

SetLogLevel sets the global log level

### GetLogLevel

```go
func GetLogLevel() int
```

GetLogLevel returns the current global log level

### SetupLogger

```go
func SetupLogger(config LoggerConfig)
```

SetupLogger configures the logger with file logging support

### LogDebug

```go
func LogDebug(message string)
```

LogDebug logs a debug message

### LogInfo

```go
func LogInfo(message string)
```

LogInfo logs an informational message

### LogInfoWithColor

```go
func LogInfoWithColor(message string)
```

LogInfoWithColor logs an informational message with custom color

### LogOperationError

```go
func LogOperationError(operation, errorMsg string, withStack bool)
```

LogOperationError logs an operation error with optional stack trace

### LogAPICall

```go
func LogAPICall(apiName, requestParams string)
```

LogAPICall logs an API call with request parameters

### LogAPIResponseWithDetails

```go
func LogAPIResponseWithDetails(apiName, requestID string, success bool, keyFields map[string]interface{}, fullResponse string)
```

LogAPIResponseWithDetails logs a structured API response with key fields

### LogCodeExecutionOutput

```go
func LogCodeExecutionOutput(requestID, rawOutput string)
```

LogCodeExecutionOutput extracts and logs the actual code execution output from run_code response

### MaskSensitiveData

```go
func MaskSensitiveData(data interface{}) interface{}
```

MaskSensitiveData recursively masks sensitive information in data structures

## Constants and Variables

### LOG_DEBUG, LOG_INFO, LOG_WARN, LOG_ERROR

```go
const (
	LOG_DEBUG	= iota
	LOG_INFO
	LOG_WARN
	LOG_ERROR
)
```

Log level constants

## Related Resources

- [Session API Reference](session.md)
- [Context API Reference](context.md)

---

*Documentation generated automatically from Go source code.*
