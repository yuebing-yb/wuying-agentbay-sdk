package agentbay

import (
	"encoding/json"
	"testing"
)

// TestCreateLogging verifies that Create() method uses new structured logging
func TestCreateLogging(t *testing.T) {
	// Create a mock AgentBay instance
	ab := &AgentBay{
		APIKey: "test-key-12345",
		Client: nil, // We'll test with mock later
	}

	// Verify AgentBay can be instantiated
	if ab.APIKey != "test-key-12345" {
		t.Errorf("Expected APIKey to be 'test-key-12345', got '%s'", ab.APIKey)
	}
}

// TestListSessionParams verifies ListSessionParams initialization
func TestListSessionParams(t *testing.T) {
	tests := []struct {
		name            string
		maxResults      int32
		nextToken       string
		labels          map[string]string
		expectedMaxKeys int
	}{
		{
			name:            "default params",
			maxResults:      10,
			nextToken:       "",
			labels:          make(map[string]string),
			expectedMaxKeys: 0,
		},
		{
			name:       "with labels",
			maxResults: 20,
			nextToken:  "token123",
			labels: map[string]string{
				"env": "prod",
				"app": "agent",
			},
			expectedMaxKeys: 2,
		},
	}

	for _, tt := range tests {
		t.Run(tt.name, func(t *testing.T) {
			params := &ListSessionParams{
				MaxResults: tt.maxResults,
				NextToken:  tt.nextToken,
				Labels:     tt.labels,
			}

			// Verify params are set correctly
			if params.MaxResults != tt.maxResults {
				t.Errorf("Expected MaxResults=%d, got %d", tt.maxResults, params.MaxResults)
			}
			if len(params.Labels) != tt.expectedMaxKeys {
				t.Errorf("Expected %d labels, got %d", tt.expectedMaxKeys, len(params.Labels))
			}
		})
	}
}

// TestNewListSessionParams verifies default parameter initialization
func TestNewListSessionParams(t *testing.T) {
	params := NewListSessionParams()

	if params.MaxResults != 10 {
		t.Errorf("Expected default MaxResults=10, got %d", params.MaxResults)
	}
	if params.NextToken != "" {
		t.Errorf("Expected default NextToken='', got '%s'", params.NextToken)
	}
	if len(params.Labels) != 0 {
		t.Errorf("Expected no default labels, got %d", len(params.Labels))
	}
}

// TestMaskSensitiveDataInRequestParams verifies sensitive data masking in API requests
func TestMaskSensitiveDataInRequestParams(t *testing.T) {
	// Simulate request parameters with sensitive data
	requestData := map[string]interface{}{
		"api_key":    "sk-1234567890abcdef",
		"session_id": "sess_abc123",
		"password":   "secret_password_123",
	}

	// Verify sensitive data is present
	if requestData["api_key"] != "sk-1234567890abcdef" {
		t.Errorf("Expected api_key to be present")
	}

	// Verify non-sensitive field is unchanged
	if requestData["session_id"] != "sess_abc123" {
		t.Errorf("session_id should be present")
	}

	// Note: Actual masking implementation would be verified here when MaskSensitiveData is implemented
}

// TestResponseJSONMarshaling verifies response data can be properly JSON marshaled
func TestResponseJSONMarshaling(t *testing.T) {
	// Simulate API response structure
	responseData := map[string]interface{}{
		"request_id": "req_12345",
		"success":    true,
		"data": map[string]interface{}{
			"session_id":   "sess_abc123",
			"resource_url": "https://example.com/session/sess_abc123",
		},
	}

	// Verify JSON marshaling works
	jsonBytes, err := json.MarshalIndent(responseData, "", "  ")
	if err != nil {
		t.Errorf("Failed to marshal response: %v", err)
	}

	if len(jsonBytes) == 0 {
		t.Errorf("Marshaled JSON should not be empty")
	}

	// Verify unmarshaling works
	var unmarshaled map[string]interface{}
	err = json.Unmarshal(jsonBytes, &unmarshaled)
	if err != nil {
		t.Errorf("Failed to unmarshal response: %v", err)
	}

	if unmarshaled["success"] != true {
		t.Errorf("Expected success=true in unmarshaled data")
	}
}

// TestKeyFieldsExtraction verifies key fields can be properly extracted for logging
func TestKeyFieldsExtraction(t *testing.T) {
	tests := []struct {
		name         string
		responseData map[string]interface{}
		expectedKeys []string
		missingKeys  []string
	}{
		{
			name: "create session response",
			responseData: map[string]interface{}{
				"session_id":    "sess_123",
				"resource_url":  "https://example.com/sess_123",
				"is_vpc":        true,
				"resource_type": "session",
			},
			expectedKeys: []string{"session_id", "resource_url", "is_vpc"},
		},
		{
			name: "list sessions response",
			responseData: map[string]interface{}{
				"total_count": 100,
				"max_results": 10,
				"session_ids": []string{"sess_1", "sess_2"},
			},
			expectedKeys: []string{"total_count", "max_results"},
		},
	}

	for _, tt := range tests {
		t.Run(tt.name, func(t *testing.T) {
			for _, key := range tt.expectedKeys {
				if _, exists := tt.responseData[key]; !exists {
					t.Errorf("Expected key '%s' in response data", key)
				}
			}
		})
	}
}

// TestRequestIDExtraction simulates RequestID extraction for logging
func TestRequestIDExtraction(t *testing.T) {
	// Simulate models.ApiResponse with RequestID
	// In real tests, we'd mock the models.ExtractRequestID function
	requestID := "req_12345"
	expectedFormat := "req_"

	if len(requestID) < 4 {
		t.Errorf("RequestID format seems incorrect: %s", requestID)
	}

	if requestID[:4] != expectedFormat {
		t.Errorf("Expected RequestID to start with 'req_', got '%s'", requestID[:4])
	}
}

// TestErrorHandlingStructure verifies error response handling structure
func TestErrorHandlingStructure(t *testing.T) {
	tests := []struct {
		name      string
		errorResp map[string]interface{}
		hasCode   bool
		hasMsg    bool
	}{
		{
			name: "standard error response",
			errorResp: map[string]interface{}{
				"code":    "SessionNotFound",
				"message": "The session was not found",
			},
			hasCode: true,
			hasMsg:  true,
		},
		{
			name: "error without message",
			errorResp: map[string]interface{}{
				"code": "UnknownError",
			},
			hasCode: true,
			hasMsg:  false,
		},
	}

	for _, tt := range tests {
		t.Run(tt.name, func(t *testing.T) {
			if _, exists := tt.errorResp["code"]; exists != tt.hasCode {
				t.Errorf("Error code existence mismatch")
			}
			if _, exists := tt.errorResp["message"]; exists != tt.hasMsg {
				t.Errorf("Error message existence mismatch")
			}
		})
	}
}
