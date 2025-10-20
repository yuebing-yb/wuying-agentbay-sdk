package agentbay

import (
	"encoding/json"
	"fmt"
	"regexp"
	"runtime/debug"
	"strings"
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

// LogAPICall logs an API call with request parameters
func LogAPICall(apiName, requestParams string) {
	if GlobalLogLevel > LOG_INFO {
		return
	}

	fmt.Printf("%s📞 API Call: %s%s\n", ColorBlue, apiName, ColorReset)

	if requestParams != "" && GlobalLogLevel <= LOG_DEBUG {
		fmt.Printf("   Request: %s\n", requestParams)
	}
}

// LogAPIResponseWithDetails logs a structured API response with key fields
func LogAPIResponseWithDetails(apiName, requestID string, success bool, keyFields map[string]interface{}, fullResponse string) {
	if GlobalLogLevel > LOG_INFO {
		return
	}

	if success {
		mainInfo := fmt.Sprintf("%s✅ API Response: %s", ColorGreen, apiName)
		if requestID != "" {
			mainInfo += fmt.Sprintf(", RequestId=%s", requestID)
		}
		fmt.Printf("%s%s\n", mainInfo, ColorReset)

		if keyFields != nil && len(keyFields) > 0 {
			for key, value := range keyFields {
				fmt.Printf("   └─ %s=%v\n", key, value)
			}
		}

		if fullResponse != "" && GlobalLogLevel <= LOG_DEBUG {
			fmt.Printf("%s📥 Full Response: %s%s\n", ColorBlue, fullResponse, ColorReset)
		}
	} else {
		mainInfo := fmt.Sprintf("%s❌ API Response Failed: %s", ColorRed, apiName)
		if requestID != "" {
			mainInfo += fmt.Sprintf(", RequestId=%s", requestID)
		}
		fmt.Printf("%s%s\n", mainInfo, ColorReset)

		if fullResponse != "" && GlobalLogLevel <= LOG_DEBUG {
			fmt.Printf("%s📥 Response: %s%s\n", ColorRed, fullResponse, ColorReset)
		}
	}
}

// LogOperationError logs an operation error with optional stack trace
func LogOperationError(operation, errorMsg string, withStack bool) {
	if GlobalLogLevel > LOG_ERROR {
		return
	}

	fmt.Printf("%s❌ Failed: %s%s\n", ColorRed, operation, ColorReset)
	fmt.Printf("%s💥 Error: %s%s\n", ColorRed, errorMsg, ColorReset)

	if withStack {
		stack := debug.Stack()
		fmt.Printf("%s[Stack Trace]:\n%s%s\n", ColorRed, string(stack), ColorReset)
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
