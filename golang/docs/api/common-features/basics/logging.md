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

**Example:**

```go
agentbay.SetLogLevel(agentbay.LOG_DEBUG)
```

### GetLogLevel

```go
func GetLogLevel() int
```

GetLogLevel returns the current global log level

**Example:**

```go
package main
import (
	"fmt"
	"github.com/aliyun/wuying-agentbay-sdk/golang/pkg/agentbay"
)
func main() {

	// Set log level to DEBUG

	agentbay.SetLogLevel(agentbay.LOG_DEBUG)

	// Check current level

	currentLevel := agentbay.GetLogLevel()
	fmt.Printf("Current log level: %d\n", currentLevel)
}
```

### SetupLogger

```go
func SetupLogger(config LoggerConfig)
```

SetupLogger configures the logger with file logging support

**Example:**

```go
config := agentbay.LoggerConfig{Level: "DEBUG", LogFile: "/tmp/agentbay.log"}
agentbay.SetupLogger(config)
```

### LogDebug

```go
func LogDebug(message string)
```

LogDebug logs a debug message

**Example:**

```go
agentbay.LogDebug("Processing request parameters")
```

### LogInfo

```go
func LogInfo(message string)
```

LogInfo logs an informational message

**Example:**

```go
agentbay.LogInfo("Session created successfully")
```

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
