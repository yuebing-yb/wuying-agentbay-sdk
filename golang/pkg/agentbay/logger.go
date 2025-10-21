package agentbay

import (
	"encoding/json"
	"fmt"
	"os"
	"regexp"
	"runtime/debug"
	"strings"
	"syscall"
)

// Log level constants
const (
	LOG_DEBUG = iota
	LOG_INFO
	LOG_WARN
	LOG_ERROR
)

// Color constants for terminal output
const (
	ColorReset  = "\033[0m"
	ColorGreen  = "\033[32m"
	ColorRed    = "\033[31m"
	ColorYellow = "\033[33m"
	ColorBlue   = "\033[34m"
)

// Global log level (default is LOG_INFO)
var GlobalLogLevel = LOG_INFO

// Sensitive field names for data masking
var SENSITIVE_FIELDS = []string{
	"api_key", "apikey", "api-key",
	"password", "passwd", "pwd",
	"token", "access_token", "auth_token",
	"secret", "private_key",
	"authorization",
}

// Initialize log level from environment variable
func init() {
	if levelStr := os.Getenv("AGENTBAY_LOG_LEVEL"); levelStr != "" {
		level := parseLogLevel(levelStr)
		SetLogLevel(level)
	}
}

// parseLogLevel converts string to log level constant
func parseLogLevel(levelStr string) int {
	switch strings.ToUpper(levelStr) {
	case "DEBUG":
		return LOG_DEBUG
	case "INFO":
		return LOG_INFO
	case "WARNING", "WARN":
		return LOG_WARN
	case "ERROR":
		return LOG_ERROR
	default:
		return LOG_INFO // Default to INFO
	}
}

// SetLogLevel sets the global log level
func SetLogLevel(level int) {
	if level >= LOG_DEBUG && level <= LOG_ERROR {
		GlobalLogLevel = level
	}
}

// GetLogLevel returns the current global log level
func GetLogLevel() int {
	return GlobalLogLevel
}

// isTerminal checks if the output is going to a terminal
func isTerminal(fd uintptr) bool {
	// Try to get terminal attributes - succeeds only if fd is a terminal
	_, _, err := syscall.Syscall(syscall.SYS_IOCTL, fd, syscall.TIOCGETA, 0)
	return err == 0
}

// getColorCodes returns ANSI color codes based on environment detection
func getColorCodes() (reset, green, red, yellow, blue string) {
	// Priority 1: Check if stdout is a real terminal (TTY)
	// This is the most reliable indicator of an interactive environment
	if isTerminal(os.Stdout.Fd()) {
		return ColorReset, ColorGreen, ColorRed, ColorYellow, ColorBlue
	}

	// Priority 2: Check FORCE_COLOR environment variable for explicit control
	// Users can set this to explicitly enable colors in non-TTY environments
	if os.Getenv("FORCE_COLOR") != "" {
		return ColorReset, ColorGreen, ColorRed, ColorYellow, ColorBlue
	}

	// Priority 3: Check if we're in an IDE environment
	// IDEs can display ANSI colors in their output pane even without TTY
	if isIDEEnvironment() {
		return ColorReset, ColorGreen, ColorRed, ColorYellow, ColorBlue
	}

	// Default: No colors - suitable for file output, CI/CD, and pipes
	return "", "", "", "", ""
}

// isIDEEnvironment detects if running in an IDE that supports ANSI colors
func isIDEEnvironment() bool {
	// Check for common IDE environment variables
	// VS Code
	if os.Getenv("TERM_PROGRAM") == "vscode" {
		return true
	}
	// GoLand / IntelliJ IDEA
	if os.Getenv("GOLAND") != "" {
		return true
	}
	if os.Getenv("IDEA_INITIAL_DIRECTORY") != "" {
		return true
	}
	// Generic IDE detection - TERM set to common IDE values
	term := os.Getenv("TERM")
	if term == "xterm-256color" || term == "xterm" || term == "screen" || term == "screen-256color" {
		return true
	}
	// Check if running via IDE test runner environment variable
	if os.Getenv("GO_TEST_IDE") != "" {
		return true
	}

	// Don't auto-enable colors for TERM=dumb or unknown environments
	return false
}

// LogAPICall logs an API call with request parameters
func LogAPICall(apiName, requestParams string) {
	if GlobalLogLevel > LOG_INFO {
		return
	}

	reset, _, _, _, blue := getColorCodes()
	// Use blue color for the entire message to match Python's consistent coloring
	fmt.Printf("%s🔗 API Call: %s%s\n", blue, apiName, reset)

	if requestParams != "" && GlobalLogLevel <= LOG_DEBUG {
		fmt.Printf("   Request: %s\n", requestParams)
	}
}

// LogAPIResponseWithDetails logs a structured API response with key fields
func LogAPIResponseWithDetails(apiName, requestID string, success bool, keyFields map[string]interface{}, fullResponse string) {
	if GlobalLogLevel > LOG_INFO {
		return
	}

	reset, green, red, _, blue := getColorCodes()

	if success {
		mainInfo := fmt.Sprintf("%s✅ API Response: %s", green, apiName)
		if requestID != "" {
			mainInfo += fmt.Sprintf(", RequestId=%s", requestID)
		}
		fmt.Printf("%s%s\n", mainInfo, reset)

		if keyFields != nil && len(keyFields) > 0 {
			for key, value := range keyFields {
				// Color parameter lines with green to match response color
				fmt.Printf("%s   └─ %s=%v%s\n", green, key, value, reset)
			}
		}

		if fullResponse != "" && GlobalLogLevel <= LOG_DEBUG {
			fmt.Printf("%s📥 Full Response: %s%s\n", blue, fullResponse, reset)
		}
	} else {
		mainInfo := fmt.Sprintf("%s❌ API Response Failed: %s", red, apiName)
		if requestID != "" {
			mainInfo += fmt.Sprintf(", RequestId=%s", requestID)
		}
		fmt.Printf("%s%s\n", mainInfo, reset)

		if fullResponse != "" && GlobalLogLevel <= LOG_DEBUG {
			fmt.Printf("%s📥 Response: %s%s\n", red, fullResponse, reset)
		}
	}
}

// LogOperationError logs an operation error with optional stack trace
func LogOperationError(operation, errorMsg string, withStack bool) {
	if GlobalLogLevel > LOG_ERROR {
		return
	}

	reset, _, red, _, _ := getColorCodes()
	fmt.Printf("%s❌ Failed: %s%s\n", red, operation, reset)
	fmt.Printf("%s💥 Error: %s%s\n", red, errorMsg, reset)

	if withStack {
		stack := debug.Stack()
		fmt.Printf("%s[Stack Trace]:\n%s%s\n", red, string(stack), reset)
	}
}

// MaskSensitiveData recursively masks sensitive information in data structures
func MaskSensitiveData(data interface{}) interface{} {
	return maskSensitiveDataInternal(data, SENSITIVE_FIELDS)
}

func maskSensitiveDataInternal(data interface{}, fields []string) interface{} {
	switch v := data.(type) {
	case map[string]interface{}:
		masked := make(map[string]interface{})
		for key, value := range v {
			if isSensitiveField(key, fields) {
				if str, ok := value.(string); ok && len(str) > 4 {
					// Keep first 2 and last 2 chars, mask the middle
					masked[key] = str[:2] + "****" + str[len(str)-2:]
				} else {
					masked[key] = "****"
				}
			} else {
				masked[key] = maskSensitiveDataInternal(value, fields)
			}
		}
		return masked

	case []interface{}:
		masked := make([]interface{}, len(v))
		for i, item := range v {
			masked[i] = maskSensitiveDataInternal(item, fields)
		}
		return masked

	case string:
		// Don't mask plain strings, only dict keys
		return v

	default:
		return data
	}
}

func isSensitiveField(fieldName string, sensitiveFields []string) bool {
	lowerField := strings.ToLower(fieldName)
	for _, field := range sensitiveFields {
		if strings.Contains(lowerField, field) {
			return true
		}
	}
	return false
}

// maskSensitiveDataString masks sensitive information in a JSON string
func maskSensitiveDataString(jsonStr string) string {
	var data map[string]interface{}
	if err := json.Unmarshal([]byte(jsonStr), &data); err != nil {
		// If not JSON, try regex masking
		return maskSensitiveDataWithRegex(jsonStr)
	}

	masked := MaskSensitiveData(data)
	if result, err := json.Marshal(masked); err == nil {
		return string(result)
	}

	return jsonStr
}

// maskSensitiveDataWithRegex masks sensitive data using regex patterns
func maskSensitiveDataWithRegex(str string) string {
	patterns := []string{
		`(api[_-]?key=)[^\s&,}]+`,
		`(password=)[^\s&,}]+`,
		`(token=)[^\s&,}]+`,
		`(authorization:\s*)[^\s,}]+`,
	}

	result := str
	for _, pattern := range patterns {
		re := regexp.MustCompile("(?i)" + pattern)
		result = re.ReplaceAllString(result, "$1****")
	}

	return result
}
