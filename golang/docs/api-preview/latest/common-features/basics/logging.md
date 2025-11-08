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
package main
import (
	"fmt"
	"os"
	"github.com/aliyun/wuying-agentbay-sdk/golang/pkg/agentbay"
)
func main() {

	// Set log level to DEBUG to see all messages

	agentbay.SetLogLevel(agentbay.LOG_DEBUG)
	client, err := agentbay.NewAgentBay(os.Getenv("AGENTBAY_API_KEY"), nil)
	if err != nil {
		fmt.Printf("Error: %v\n", err)
		os.Exit(1)
	}
	result, err := client.Create(nil)
	if err != nil {
		fmt.Printf("Error: %v\n", err)
		os.Exit(1)
	}
	session := result.Session
	defer session.Delete()

	// Change to INFO level to reduce verbosity

	agentbay.SetLogLevel(agentbay.LOG_INFO)

	// Continue with your operations

}
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
package main
import (
	"fmt"
	"os"
	"github.com/aliyun/wuying-agentbay-sdk/golang/pkg/agentbay"
)
func main() {

	// Configure file logging with rotation

	agentbay.SetupLogger(agentbay.LoggerConfig{
		Level:       "DEBUG",
		LogFile:     "/tmp/agentbay.log",
		MaxFileSize: "100 MB",
	})
	client, err := agentbay.NewAgentBay(os.Getenv("AGENTBAY_API_KEY"), nil)
	if err != nil {
		fmt.Printf("Error: %v\n", err)
		os.Exit(1)
	}
	result, err := client.Create(nil)
	if err != nil {
		fmt.Printf("Error: %v\n", err)
		os.Exit(1)
	}
	session := result.Session
	defer session.Delete()

	// All logs will be written to both console and file

}
```

### LogDebug

```go
func LogDebug(message string)
```

LogDebug logs a debug message

**Example:**

```go
package main
import (
	"fmt"
	"os"
	"github.com/aliyun/wuying-agentbay-sdk/golang/pkg/agentbay"
)
func main() {

	// Set log level to DEBUG to see debug messages

	agentbay.SetLogLevel(agentbay.LOG_DEBUG)
	client, err := agentbay.NewAgentBay(os.Getenv("AGENTBAY_API_KEY"), nil)
	if err != nil {
		fmt.Printf("Error: %v\n", err)
		os.Exit(1)
	}
	result, err := client.Create(nil)
	if err != nil {
		fmt.Printf("Error: %v\n", err)
		os.Exit(1)
	}
	session := result.Session
	defer session.Delete()

	// Log debug messages

	agentbay.LogDebug("Debugging session creation process")

	// Output: 🐛 Debugging session creation process

}
```

### LogInfo

```go
func LogInfo(message string)
```

LogInfo logs an informational message

**Example:**

```go
package main
import (
	"fmt"
	"os"
	"github.com/aliyun/wuying-agentbay-sdk/golang/pkg/agentbay"
)
func main() {

	// Set log level to INFO or DEBUG to see info messages

	agentbay.SetLogLevel(agentbay.LOG_INFO)
	client, err := agentbay.NewAgentBay(os.Getenv("AGENTBAY_API_KEY"), nil)
	if err != nil {
		fmt.Printf("Error: %v\n", err)
		os.Exit(1)
	}
	result, err := client.Create(nil)
	if err != nil {
		fmt.Printf("Error: %v\n", err)
		os.Exit(1)
	}
	session := result.Session
	defer session.Delete()

	// Log informational messages

	agentbay.LogInfo("Session created successfully")

	// Output: ℹ️  Session created successfully

}
```

### LogInfoWithColor

```go
func LogInfoWithColor(message string)
```

LogInfoWithColor logs an informational message with custom color

**Example:**

```go
package main
import (
	"fmt"
	"os"
	"github.com/aliyun/wuying-agentbay-sdk/golang/pkg/agentbay"
)
func main() {

	// Set log level to INFO or DEBUG to see colored messages

	agentbay.SetLogLevel(agentbay.LOG_INFO)
	client, err := agentbay.NewAgentBay(os.Getenv("AGENTBAY_API_KEY"), nil)
	if err != nil {
		fmt.Printf("Error: %v\n", err)
		os.Exit(1)
	}
	result, err := client.Create(nil)
	if err != nil {
		fmt.Printf("Error: %v\n", err)
		os.Exit(1)
	}
	session := result.Session
	defer session.Delete()

	// Log informational messages with color emphasis

	agentbay.LogInfoWithColor("Important: Session ready for use")

	// Output: ℹ️  Important: Session ready for use

}
```

### LogOperationError

```go
func LogOperationError(operation, errorMsg string, withStack bool)
```

LogOperationError logs an operation error with optional stack trace

**Example:**

```go
package main
import (
	"fmt"
	"os"
	"github.com/aliyun/wuying-agentbay-sdk/golang/pkg/agentbay"
)
func main() {
	client, err := agentbay.NewAgentBay(os.Getenv("AGENTBAY_API_KEY"), nil)
	if err != nil {
		fmt.Printf("Error: %v\n", err)
		os.Exit(1)
	}
	result, err := client.Create(nil)
	if err != nil {

		// Log operation errors

		agentbay.LogOperationError("Create Session", err.Error(), false)
		os.Exit(1)
	}
	session := result.Session
	defer session.Delete()

	// Output: ❌ Failed: Create Session

	// Output: 💥 Error: session creation failed

}
```

### LogAPICall

```go
func LogAPICall(apiName, requestParams string)
```

LogAPICall logs an API call with request parameters

**Example:**

```go
package main
import (
	"fmt"
	"os"
	"github.com/aliyun/wuying-agentbay-sdk/golang/pkg/agentbay"
)
func main() {

	// Set log level to DEBUG to see API calls

	agentbay.SetLogLevel(agentbay.LOG_DEBUG)
	client, err := agentbay.NewAgentBay(os.Getenv("AGENTBAY_API_KEY"), nil)
	if err != nil {
		fmt.Printf("Error: %v\n", err)
		os.Exit(1)
	}
	result, err := client.Create(nil)
	if err != nil {
		fmt.Printf("Error: %v\n", err)
		os.Exit(1)
	}
	session := result.Session
	defer session.Delete()

	// API calls are automatically logged by the SDK

	// Output: 🔗 API Call: create_session

}
```

### LogAPIResponseWithDetails

```go
func LogAPIResponseWithDetails(apiName, requestID string, success bool, keyFields map[string]interface{}, fullResponse string)
```

LogAPIResponseWithDetails logs a structured API response with key fields

**Example:**

```go
package main
import (
	"fmt"
	"os"
	"github.com/aliyun/wuying-agentbay-sdk/golang/pkg/agentbay"
)
func main() {

	// Set log level to DEBUG to see detailed responses

	agentbay.SetLogLevel(agentbay.LOG_DEBUG)
	client, err := agentbay.NewAgentBay(os.Getenv("AGENTBAY_API_KEY"), nil)
	if err != nil {
		fmt.Printf("Error: %v\n", err)
		os.Exit(1)
	}
	result, err := client.Create(nil)
	if err != nil {
		fmt.Printf("Error: %v\n", err)
		os.Exit(1)
	}
	session := result.Session
	defer session.Delete()

	// API responses are automatically logged by the SDK

	// Output: ✅ API Response: create_session, RequestId=xxx

}
```

### LogCodeExecutionOutput

```go
func LogCodeExecutionOutput(requestID, rawOutput string)
```

LogCodeExecutionOutput extracts and logs the actual code execution output from run_code response

**Example:**

```go
package main
import (
	"fmt"
	"os"
	"github.com/aliyun/wuying-agentbay-sdk/golang/pkg/agentbay"
)
func main() {

	// Set log level to INFO to see code execution output

	agentbay.SetLogLevel(agentbay.LOG_INFO)
	client, err := agentbay.NewAgentBay(os.Getenv("AGENTBAY_API_KEY"), nil)
	if err != nil {
		fmt.Printf("Error: %v\n", err)
		os.Exit(1)
	}
	result, err := client.Create(nil)
	if err != nil {
		fmt.Printf("Error: %v\n", err)
		os.Exit(1)
	}
	session := result.Session
	defer session.Delete()

	// Execute code in the session

	execResult, err := session.Code.RunCode("print('Hello from AgentBay')", "python")
	if err != nil {
		fmt.Printf("Error: %v\n", err)
		os.Exit(1)
	}
	fmt.Printf("Code execution completed: %v\n", execResult.Success)

	// Output: 📋 Code Execution Output (RequestID: xxx):

	// Output:    Hello from AgentBay

}
```

### MaskSensitiveData

```go
func MaskSensitiveData(data interface{}) interface{}
```

MaskSensitiveData recursively masks sensitive information in data structures

**Example:**

```go
package main
import (
	"fmt"
	"github.com/aliyun/wuying-agentbay-sdk/golang/pkg/agentbay"
)
func main() {

	// Create data with sensitive information

	data := map[string]interface{}{
		"api_key":    "sk_live_1234567890",
		"password":   "secret123",
		"auth_token": "Bearer xyz",
		"username":   "john_doe",
	}

	// Mask sensitive data

	masked := agentbay.MaskSensitiveData(data)
	fmt.Printf("Masked data: %v\n", masked)

	// Output: Masked data: map[api_key:sk****90 auth_token:Be****yz password:se****23 username:john_doe]

}
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
