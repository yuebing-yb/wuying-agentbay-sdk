# Logging API Reference

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

### Deprecated

```go
func Deprecated(reason, replacement, version string)
```

Deprecated marks a function or method as deprecated and emits a warning

### DeprecatedFunc

```go
func DeprecatedFunc(reason, replacement, version string) func()
```

DeprecatedFunc is a helper function to mark functions as deprecated Usage: defer
DeprecatedFunc("reason", "replacement", "version")()

### DeprecatedMethod

```go
func DeprecatedMethod(methodName, reason, replacement, version string) func()
```

DeprecatedMethod is a helper function to mark methods as deprecated Usage: defer
DeprecatedMethod("MethodName", "reason", "replacement", "version")()

### FindDotEnvFile

```go
func FindDotEnvFile(startPath string) string
```

FindDotEnvFile searches for .env file upward from startPath. Search order: 1. Current working
directory 2. Parent directories (up to root) 3. Git repository root (if found)

Args:


startPath: Starting directory for search (empty string means current directory)

Returns:


Path to .env file if found, empty string otherwise

### GetLogLevel

```go
func GetLogLevel() int
```

GetLogLevel returns the current global log level

### LoadDotEnvWithFallback

```go
func LoadDotEnvWithFallback(customEnvPath string)
```

LoadDotEnvWithFallback loads .env file with improved search strategy.

Args:


customEnvPath: Custom path to .env file (empty string means search upward)

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

### LogOperationError

```go
func LogOperationError(operation, errorMsg string, withStack bool)
```

LogOperationError logs an operation error with optional stack trace

### MaskSensitiveData

```go
func MaskSensitiveData(data interface{}) interface{}
```

MaskSensitiveData recursively masks sensitive information in data structures

### SetDeprecationConfig

```go
func SetDeprecationConfig(config *DeprecationConfig)
```

SetDeprecationConfig sets the global deprecation configuration

### SetLogLevel

```go
func SetLogLevel(level int)
```

SetLogLevel sets the global log level

### SetupLogger

```go
func SetupLogger(config LoggerConfig)
```

SetupLogger configures the logger with file logging support

### TestCreateLogging

```go
func TestCreateLogging(t *testing.T)
```

TestCreateLogging verifies that Create() method uses new structured logging

### TestErrorHandlingStructure

```go
func TestErrorHandlingStructure(t *testing.T)
```

TestErrorHandlingStructure verifies error response handling structure

### TestIsSensitiveField

```go
func TestIsSensitiveField(t *testing.T)
```

TestIsSensitiveField verifies the sensitive field detection

### TestKeyFieldsExtraction

```go
func TestKeyFieldsExtraction(t *testing.T)
```

TestKeyFieldsExtraction verifies key fields can be properly extracted for logging

### TestListSessionParams

```go
func TestListSessionParams(t *testing.T)
```

TestListSessionParams verifies ListSessionParams initialization

### TestLogAPICall

```go
func TestLogAPICall(t *testing.T)
```

TestLogAPICall verifies LogAPICall produces correct formatted output

### TestLogAPIResponseWithDetailsFailure

```go
func TestLogAPIResponseWithDetailsFailure(t *testing.T)
```

TestLogAPIResponseWithDetailsFailure verifies failed API response logging

### TestLogAPIResponseWithDetailsSuccess

```go
func TestLogAPIResponseWithDetailsSuccess(t *testing.T)
```

TestLogAPIResponseWithDetailsSuccess verifies successful API response logging

### TestLogLevelConstants

```go
func TestLogLevelConstants(t *testing.T)
```

TestLogLevelConstants verifies log level constants

### TestLogLevelControl

```go
func TestLogLevelControl(t *testing.T)
```

TestLogLevelControl tests the log level control functionality

### TestLogOperationErrorWithStack

```go
func TestLogOperationErrorWithStack(t *testing.T)
```

TestLogOperationErrorWithStack verifies error logging with stack trace

### TestLogOperationErrorWithoutStack

```go
func TestLogOperationErrorWithoutStack(t *testing.T)
```

TestLogOperationErrorWithoutStack verifies error logging without stack trace

### TestMaskSensitiveDataInRequestParams

```go
func TestMaskSensitiveDataInRequestParams(t *testing.T)
```

TestMaskSensitiveDataInRequestParams verifies sensitive data masking in API requests

### TestMaskSensitiveDataPreservesNonSensitive

```go
func TestMaskSensitiveDataPreservesNonSensitive(t *testing.T)
```

TestMaskSensitiveDataPreservesNonSensitive verifies non-sensitive data is unchanged

### TestMaskSensitiveDataWithArray

```go
func TestMaskSensitiveDataWithArray(t *testing.T)
```

TestMaskSensitiveDataWithArray verifies masking in arrays

### TestMaskSensitiveDataWithMapApiKey

```go
func TestMaskSensitiveDataWithMapApiKey(t *testing.T)
```

TestMaskSensitiveDataWithMapApiKey verifies API key masking in maps

### TestMaskSensitiveDataWithNestedStructure

```go
func TestMaskSensitiveDataWithNestedStructure(t *testing.T)
```

TestMaskSensitiveDataWithNestedStructure verifies recursive masking

### TestMaskSensitiveDataWithPassword

```go
func TestMaskSensitiveDataWithPassword(t *testing.T)
```

TestMaskSensitiveDataWithPassword verifies password masking

### TestMaskSensitiveDataWithShortSecret

```go
func TestMaskSensitiveDataWithShortSecret(t *testing.T)
```

TestMaskSensitiveDataWithShortSecret verifies masking of short sensitive values

### TestMaskSensitiveDataWithToken

```go
func TestMaskSensitiveDataWithToken(t *testing.T)
```

TestMaskSensitiveDataWithToken verifies token masking

### TestNewListSessionParams

```go
func TestNewListSessionParams(t *testing.T)
```

TestNewListSessionParams verifies default parameter initialization

### TestRequestIDExtraction

```go
func TestRequestIDExtraction(t *testing.T)
```

TestRequestIDExtraction simulates RequestID extraction for logging

### TestResponseJSONMarshaling

```go
func TestResponseJSONMarshaling(t *testing.T)
```

TestResponseJSONMarshaling verifies response data can be properly JSON marshaled

### containsWildcard

```go
func containsWildcard(path string) bool
```

### getColorCodes

```go
func getColorCodes() (reset, green, red, yellow, blue string)
```

getColorCodes returns ANSI color codes based on environment detection

### getVersion

```go
func getVersion() string
```

getVersion attempts to read version from Go module info Returns the version from go.mod or a default
fallback

### init

```go
func init()
```

Initialize log level from environment variable

### isIDEEnvironment

```go
func isIDEEnvironment() bool
```

isIDEEnvironment detects if running in an IDE that supports ANSI colors

### isReleaseVersion

```go
func isReleaseVersion() bool
```

isReleaseVersion checks if this is a release build Returns true only if the SDK is installed from
GitHub (github.com/aliyun/wuying-agentbay-sdk/golang) Returns false if: 1. Developing the SDK
locally (main module) 2. Installed via go.mod replace from internal source (code.alibaba-inc.com) 3.
Installed from a pseudo-version

### isSensitiveField

```go
func isSensitiveField(fieldName string, sensitiveFields []string) bool
```

### isValidLifecycle

```go
func isValidLifecycle(lifecycle Lifecycle) bool
```

isValidLifecycle checks if the given lifecycle value is valid

### isValidUploadMode

```go
func isValidUploadMode(uploadMode UploadMode) bool
```

isValidUploadMode checks if the given uploadMode value is valid

### maskSensitiveDataInternal

```go
func maskSensitiveDataInternal(data interface{}, fields []string) interface{}
```

### maskSensitiveDataString

```go
func maskSensitiveDataString(jsonStr string) string
```

maskSensitiveDataString masks sensitive information in a JSON string

### maskSensitiveDataWithRegex

```go
func maskSensitiveDataWithRegex(str string) string
```

maskSensitiveDataWithRegex masks sensitive data using regex patterns

### parseFileSize

```go
func parseFileSize(sizeStr string) int64
```

parseFileSize parses size string like "10 MB" to bytes

### parseLogLevel

```go
func parseLogLevel(levelStr string) int
```

parseLogLevel converts string to log level constant

### validateSyncPolicy

```go
func validateSyncPolicy(policy *SyncPolicy) error
```

### writeToFile

```go
func writeToFile(message string)
```

writeToFile writes a message to the log file with rotation

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

---

*Documentation generated automatically from Go source code.*
