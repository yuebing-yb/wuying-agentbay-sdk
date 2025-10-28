package agentbay

import (
	"encoding/json"
	"strings"
	"testing"
)

// TestLogAPICall verifies LogAPICall produces correct formatted output
func TestLogAPICall(t *testing.T) {
	tests := []struct {
		name    string
		apiName string
		params  string
	}{
		{
			name:    "basic API call",
			apiName: "CreateSession",
			params:  "ImageId=linux_latest, IsVpc=true",
		},
		{
			name:    "empty params",
			apiName: "ListSessions",
			params:  "",
		},
	}

	for _, tt := range tests {
		t.Run(tt.name, func(t *testing.T) {
			// Just verify it doesn't panic
			LogAPICall(tt.apiName, tt.params)
		})
	}
}

// TestLogAPIResponseWithDetailsSuccess verifies successful API response logging
func TestLogAPIResponseWithDetailsSuccess(t *testing.T) {
	keyFields := map[string]interface{}{
		"session_id":   "sess_123456",
		"resource_url": "https://example.com/session/sess_123456",
		"is_vpc":       true,
	}

	responseBody := map[string]interface{}{
		"success": true,
		"data": map[string]interface{}{
			"session_id": "sess_123456",
		},
	}
	fullResponse, _ := json.Marshal(responseBody)

	// Verify it doesn't panic with valid inputs
	LogAPIResponseWithDetails("CreateSession", "req_12345", true, keyFields, string(fullResponse))
}

// TestLogAPIResponseWithDetailsFailure verifies failed API response logging
func TestLogAPIResponseWithDetailsFailure(t *testing.T) {
	responseBody := map[string]interface{}{
		"success": false,
		"code":    "SessionNotFound",
		"message": "Session not found",
	}
	fullResponse, _ := json.Marshal(responseBody)

	// Verify it doesn't panic with error response
	LogAPIResponseWithDetails("GetSession", "req_67890", false, nil, string(fullResponse))
}

// TestLogOperationErrorWithoutStack verifies error logging without stack trace
func TestLogOperationErrorWithoutStack(t *testing.T) {
	// Verify it doesn't panic
	LogOperationError("CreateSession", "Network timeout", false)
}

// TestLogOperationErrorWithStack verifies error logging with stack trace
func TestLogOperationErrorWithStack(t *testing.T) {
	// Verify it doesn't panic
	LogOperationError("DeleteSession", "Permission denied", true)
}

// TestMaskSensitiveDataWithMapApiKey verifies API key masking in maps
func TestMaskSensitiveDataWithMapApiKey(t *testing.T) {
	data := map[string]interface{}{
		"api_key": "sk-1234567890abcdef",
		"user":    "john@example.com",
	}

	masked := MaskSensitiveData(data).(map[string]interface{})

	// Verify API key is masked (first 2 + **** + last 2)
	if masked["api_key"] != "sk****ef" {
		t.Errorf("expected 'sk****ef', got '%v'", masked["api_key"])
	}

	// Verify non-sensitive data is unchanged
	if masked["user"] != "john@example.com" {
		t.Errorf("expected 'john@example.com', got '%v'", masked["user"])
	}
}

// TestMaskSensitiveDataWithPassword verifies password masking
func TestMaskSensitiveDataWithPassword(t *testing.T) {
	data := map[string]interface{}{
		"password": "mysecretpassword123",
		"username": "admin",
	}

	masked := MaskSensitiveData(data).(map[string]interface{})

	// Verify password is masked (first 2 + **** + last 2)
	if masked["password"] != "my****23" {
		t.Errorf("expected 'my****23', got '%v'", masked["password"])
	}

	// Verify username is unchanged
	if masked["username"] != "admin" {
		t.Errorf("expected 'admin', got '%v'", masked["username"])
	}
}

// TestMaskSensitiveDataWithToken verifies token masking
func TestMaskSensitiveDataWithToken(t *testing.T) {
	data := map[string]interface{}{
		"access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9",
		"user_id":      "user_12345",
	}

	masked := MaskSensitiveData(data).(map[string]interface{})

	// Verify token is masked
	if !strings.Contains(masked["access_token"].(string), "****") {
		t.Errorf("token should be masked, got '%v'", masked["access_token"])
	}

	// Verify user_id is unchanged
	if masked["user_id"] != "user_12345" {
		t.Errorf("expected 'user_12345', got '%v'", masked["user_id"])
	}
}

// TestMaskSensitiveDataWithNestedStructure verifies recursive masking
func TestMaskSensitiveDataWithNestedStructure(t *testing.T) {
	data := map[string]interface{}{
		"user": map[string]interface{}{
			"name":     "John",
			"password": "secret123",
		},
		"api_key": "key_abcdef123456",
	}

	masked := MaskSensitiveData(data).(map[string]interface{})
	userMasked := masked["user"].(map[string]interface{})

	// Verify nested password is masked (first 2 + **** + last 2)
	if userMasked["password"] != "se****23" {
		t.Errorf("expected 'se****23', got '%v'", userMasked["password"])
	}

	// Verify nested name is unchanged
	if userMasked["name"] != "John" {
		t.Errorf("expected 'John', got '%v'", userMasked["name"])
	}

	// Verify top-level api_key is masked (first 2 + **** + last 2)
	if masked["api_key"] != "ke****56" {
		t.Errorf("expected 'ke****56', got '%v'", masked["api_key"])
	}
}

// TestMaskSensitiveDataWithArray verifies masking in arrays
func TestMaskSensitiveDataWithArray(t *testing.T) {
	data := []interface{}{
		map[string]interface{}{
			"api_key": "key_111111",
			"name":    "item1",
		},
		map[string]interface{}{
			"api_key": "key_222222",
			"name":    "item2",
		},
	}

	masked := MaskSensitiveData(data).([]interface{})

	// Verify first item's api_key is masked (first 2 + **** + last 2)
	first := masked[0].(map[string]interface{})
	if first["api_key"] != "ke****11" {
		t.Errorf("expected 'ke****11', got '%v'", first["api_key"])
	}

	// Verify second item's api_key is masked (first 2 + **** + last 2)
	second := masked[1].(map[string]interface{})
	if second["api_key"] != "ke****22" {
		t.Errorf("expected 'ke****22', got '%v'", second["api_key"])
	}
}

// TestMaskSensitiveDataWithShortSecret verifies masking of short sensitive values
func TestMaskSensitiveDataWithShortSecret(t *testing.T) {
	data := map[string]interface{}{
		"secret": "abc",   // Less than 5 chars
		"token":  "12345", // Exactly 5 chars
	}

	masked := MaskSensitiveData(data).(map[string]interface{})

	// Verify short secret is masked completely
	if masked["secret"] != "****" {
		t.Errorf("expected '****', got '%v'", masked["secret"])
	}

	// Verify 5-char token is masked (first 2 + **** + last 2)
	if masked["token"] != "12****45" {
		t.Errorf("expected '12****45', got '%v'", masked["token"])
	}
}

// TestMaskSensitiveDataPreservesNonSensitive verifies non-sensitive data is unchanged
func TestMaskSensitiveDataPreservesNonSensitive(t *testing.T) {
	data := map[string]interface{}{
		"user_id":      12345,
		"session_id":   "sess_abc123",
		"resource_url": "https://example.com",
		"total_count":  100,
		"is_vpc":       true,
	}

	masked := MaskSensitiveData(data).(map[string]interface{})

	// Verify all non-sensitive data is unchanged
	tests := []struct {
		key      string
		expected interface{}
	}{
		{"user_id", 12345},
		{"session_id", "sess_abc123"},
		{"resource_url", "https://example.com"},
		{"total_count", 100},
		{"is_vpc", true},
	}

	for _, tt := range tests {
		if masked[tt.key] != tt.expected {
			t.Errorf("expected %v for key %s, got %v", tt.expected, tt.key, masked[tt.key])
		}
	}
}

// TestIsSensitiveField verifies the sensitive field detection
func TestIsSensitiveField(t *testing.T) {
	tests := []struct {
		field    string
		expected bool
	}{
		{"api_key", true},
		{"apikey", true},
		{"api-key", true},
		{"password", true},
		{"passwd", true},
		{"token", true},
		{"access_token", true},
		{"secret", true},
		{"session_id", false},
		{"user_name", false},
		{"resource_url", false},
		{"Authorization", true},
		{"AUTHORIZATION", true},
	}

	for _, tt := range tests {
		result := isSensitiveField(tt.field, SENSITIVE_FIELDS)
		if result != tt.expected {
			t.Errorf("isSensitiveField(%q) = %v, want %v", tt.field, result, tt.expected)
		}
	}
}

// TestLogLevelControl tests the log level control functionality
func TestLogLevelControl(t *testing.T) {
	// Save original log level
	originalLevel := GetLogLevel()
	defer SetLogLevel(originalLevel)

	// Test 1: Default log level is INFO
	if GetLogLevel() != LOG_INFO {
		t.Errorf("Expected default log level to be LOG_INFO, got %d", GetLogLevel())
	}

	// Test 2: Set log level to DEBUG
	SetLogLevel(LOG_DEBUG)
	if GetLogLevel() != LOG_DEBUG {
		t.Errorf("Expected log level to be LOG_DEBUG, got %d", GetLogLevel())
	}

	// Test 3: Set log level to WARN
	SetLogLevel(LOG_WARN)
	if GetLogLevel() != LOG_WARN {
		t.Errorf("Expected log level to be LOG_WARN, got %d", GetLogLevel())
	}

	// Test 4: Set log level to ERROR
	SetLogLevel(LOG_ERROR)
	if GetLogLevel() != LOG_ERROR {
		t.Errorf("Expected log level to be LOG_ERROR, got %d", GetLogLevel())
	}

	// Test 5: Invalid log level should not change
	SetLogLevel(999)
	if GetLogLevel() != LOG_ERROR {
		t.Errorf("Expected log level to remain LOG_ERROR after invalid set, got %d", GetLogLevel())
	}

	// Test 6: Reset to DEBUG and verify LogAPICall output
	t.Log("\n--- Test 6: LogAPICall at DEBUG level (should print Request) ---")
	SetLogLevel(LOG_DEBUG)
	LogAPICall("TestAPI", `{"param":"value"}`)

	// Test 7: Set to INFO and verify LogAPICall output
	t.Log("\n--- Test 7: LogAPICall at INFO level (Request should not print) ---")
	SetLogLevel(LOG_INFO)
	LogAPICall("TestAPI", `{"param":"value"}`)

	// Test 8: LogAPIResponseWithDetails at DEBUG level
	t.Log("\n--- Test 8: LogAPIResponseWithDetails at DEBUG level (Full Response should print) ---")
	SetLogLevel(LOG_DEBUG)
	keyFields := map[string]interface{}{
		"session_id": "session-12345",
		"status":     "running",
	}
	LogAPIResponseWithDetails("CreateSession", "req-123", true, keyFields, `{"status":200,"data":{"id":"123"}}`)

	// Test 9: LogAPIResponseWithDetails at INFO level
	t.Log("\n--- Test 9: LogAPIResponseWithDetails at INFO level (Full Response should not print) ---")
	SetLogLevel(LOG_INFO)
	LogAPIResponseWithDetails("CreateSession", "req-123", true, keyFields, `{"status":200,"data":{"id":"123"}}`)

	// Test 10: LogAPIResponseWithDetails at WARN level (should not print anything)
	t.Log("\n--- Test 10: LogAPIResponseWithDetails at WARN level (nothing should print) ---")
	SetLogLevel(LOG_WARN)
	LogAPIResponseWithDetails("CreateSession", "req-123", true, keyFields, `{"status":200,"data":{"id":"123"}}`)

	t.Log("\n--- All log level control tests completed ---")
}

// TestLogLevelConstants verifies log level constants
func TestLogLevelConstants(t *testing.T) {
	if LOG_DEBUG != 0 {
		t.Errorf("Expected LOG_DEBUG to be 0, got %d", LOG_DEBUG)
	}
	if LOG_INFO != 1 {
		t.Errorf("Expected LOG_INFO to be 1, got %d", LOG_INFO)
	}
	if LOG_WARN != 2 {
		t.Errorf("Expected LOG_WARN to be 2, got %d", LOG_WARN)
	}
	if LOG_ERROR != 3 {
		t.Errorf("Expected LOG_ERROR to be 3, got %d", LOG_ERROR)
	}
}
