package agentbay_test

import (
	"errors"
	"testing"

	"github.com/aliyun/wuying-agentbay-sdk/golang/pkg/agentbay"
	"github.com/aliyun/wuying-agentbay-sdk/golang/pkg/agentbay/models"
	"github.com/aliyun/wuying-agentbay-sdk/golang/tests/pkg/unit/mock"
	"github.com/golang/mock/gomock"
	"github.com/stretchr/testify/assert"
)

// TestAgentBay_Pause tests AgentBay Pause method
func TestAgentBay_Pause(t *testing.T) {
	ctrl := gomock.NewController(t)
	defer ctrl.Finish()

	// Create mock AgentBay client
	mockAgentBay := mock.NewMockAgentBayInterface(ctrl)

	// Create a real session for testing
	client, _ := agentbay.NewAgentBay("test-api-key")
	testSession := agentbay.NewSession(client, "test-session-id")

	// Set expected behavior for successful pause
	expectedResult := &models.SessionPauseResult{
		ApiResponse: models.ApiResponse{
			RequestID: "test-request-id-agentbay",
		},
		Success: true,
		Status:  "PAUSED",
	}
	mockAgentBay.EXPECT().Pause(testSession, 600, 2.0).Return(expectedResult, nil)

	// Test Pause method call
	result, err := mockAgentBay.Pause(testSession, 600, 2.0)

	// Verify call success
	assert.NoError(t, err)
	assert.NotNil(t, result)
	assert.True(t, result.Success)
	assert.Equal(t, "PAUSED", result.Status)
	assert.Equal(t, "test-request-id-agentbay", result.RequestID)
}

// TestAgentBay_Pause_Error tests error handling in AgentBay Pause method
func TestAgentBay_Pause_Error(t *testing.T) {
	ctrl := gomock.NewController(t)
	defer ctrl.Finish()

	// Create mock AgentBay client
	mockAgentBay := mock.NewMockAgentBayInterface(ctrl)

	// Create a real session for testing
	client, _ := agentbay.NewAgentBay("test-api-key")
	testSession := agentbay.NewSession(client, "test-session-id")

	// Set expected behavior for error case
	expectedErr := errors.New("agentbay pause operation failed")
	mockAgentBay.EXPECT().Pause(testSession, 600, 2.0).Return(nil, expectedErr)

	// Test Pause method call with error
	result, err := mockAgentBay.Pause(testSession, 600, 2.0)

	// Verify error handling
	assert.Error(t, err)
	assert.Nil(t, result)
	assert.Equal(t, expectedErr, err)
}

// TestAgentBay_Pause_WithCustomParams tests AgentBay Pause method with custom parameters
func TestAgentBay_Pause_WithCustomParams(t *testing.T) {
	ctrl := gomock.NewController(t)
	defer ctrl.Finish()

	// Create mock AgentBay client
	mockAgentBay := mock.NewMockAgentBayInterface(ctrl)

	// Create a real session for testing
	client, _ := agentbay.NewAgentBay("test-api-key")
	testSession := agentbay.NewSession(client, "test-session-id")

	// Set expected behavior for successful pause with custom parameters
	expectedResult := &models.SessionPauseResult{
		ApiResponse: models.ApiResponse{
			RequestID: "test-request-id-agentbay-custom",
		},
		Success: true,
		Status:  "PAUSED",
	}
	mockAgentBay.EXPECT().Pause(testSession, 300, 1.5).Return(expectedResult, nil)

	// Test Pause method call with custom parameters
	result, err := mockAgentBay.Pause(testSession, 300, 1.5)

	// Verify call success
	assert.NoError(t, err)
	assert.NotNil(t, result)
	assert.True(t, result.Success)
	assert.Equal(t, "PAUSED", result.Status)
	assert.Equal(t, "test-request-id-agentbay-custom", result.RequestID)
}

// TestAgentBay_Resume tests AgentBay Resume method
func TestAgentBay_Resume(t *testing.T) {
	ctrl := gomock.NewController(t)
	defer ctrl.Finish()

	// Create mock AgentBay client
	mockAgentBay := mock.NewMockAgentBayInterface(ctrl)

	// Create a real session for testing
	client, _ := agentbay.NewAgentBay("test-api-key")
	testSession := agentbay.NewSession(client, "test-session-id")

	// Set expected behavior for successful resume
	expectedResult := &models.SessionResumeResult{
		ApiResponse: models.ApiResponse{
			RequestID: "test-request-id-resume-agentbay",
		},
		Success: true,
		Status:  "RUNNING",
	}
	mockAgentBay.EXPECT().Resume(testSession, 600, 2.0).Return(expectedResult, nil)

	// Test Resume method call
	result, err := mockAgentBay.Resume(testSession, 600, 2.0)

	// Verify call success
	assert.NoError(t, err)
	assert.NotNil(t, result)
	assert.True(t, result.Success)
	assert.Equal(t, "RUNNING", result.Status)
	assert.Equal(t, "test-request-id-resume-agentbay", result.RequestID)
}

// TestAgentBay_Resume_Error tests error handling in AgentBay Resume method
func TestAgentBay_Resume_Error(t *testing.T) {
	ctrl := gomock.NewController(t)
	defer ctrl.Finish()

	// Create mock AgentBay client
	mockAgentBay := mock.NewMockAgentBayInterface(ctrl)

	// Create a real session for testing
	client, _ := agentbay.NewAgentBay("test-api-key")
	testSession := agentbay.NewSession(client, "test-session-id")

	// Set expected behavior for error case
	expectedErr := errors.New("agentbay resume operation failed")
	mockAgentBay.EXPECT().Resume(testSession, 600, 2.0).Return(nil, expectedErr)

	// Test Resume method call with error
	result, err := mockAgentBay.Resume(testSession, 600, 2.0)

	// Verify error handling
	assert.Error(t, err)
	assert.Nil(t, result)
	assert.Equal(t, expectedErr, err)
}

// TestAgentBay_Resume_WithCustomParams tests AgentBay Resume method with custom parameters
func TestAgentBay_Resume_WithCustomParams(t *testing.T) {
	ctrl := gomock.NewController(t)
	defer ctrl.Finish()

	// Create mock AgentBay client
	mockAgentBay := mock.NewMockAgentBayInterface(ctrl)

	// Create a real session for testing
	client, _ := agentbay.NewAgentBay("test-api-key")
	testSession := agentbay.NewSession(client, "test-session-id")

	// Set expected behavior for successful resume with custom parameters
	expectedResult := &models.SessionResumeResult{
		ApiResponse: models.ApiResponse{
			RequestID: "test-request-id-resume-agentbay-custom",
		},
		Success: true,
		Status:  "RUNNING",
	}
	mockAgentBay.EXPECT().Resume(testSession, 300, 1.5).Return(expectedResult, nil)

	// Test Resume method call with custom parameters
	result, err := mockAgentBay.Resume(testSession, 300, 1.5)

	// Verify call success
	assert.NoError(t, err)
	assert.NotNil(t, result)
	assert.True(t, result.Success)
	assert.Equal(t, "RUNNING", result.Status)
	assert.Equal(t, "test-request-id-resume-agentbay-custom", result.RequestID)
}

// TestAgentBay_Pause_UnexpectedStateRunning tests Pause method with unexpected RUNNING state
func TestAgentBay_Pause_UnexpectedStateRunning(t *testing.T) {
	ctrl := gomock.NewController(t)
	defer ctrl.Finish()

	// Create mock AgentBay client
	mockAgentBay := mock.NewMockAgentBayInterface(ctrl)

	// Create a real session for testing
	client, _ := agentbay.NewAgentBay("test-api-key")
	testSession := agentbay.NewSession(client, "test-session-id")

	// Set expected behavior for pause with unexpected state
	expectedResult := &models.SessionPauseResult{
		ApiResponse: models.ApiResponse{
			RequestID: "test-request-id",
		},
		Success:      false,
		ErrorMessage: "Session pause failed: unexpected state 'RUNNING'",
		Status:       "RUNNING",
	}
	mockAgentBay.EXPECT().Pause(testSession, 600, 2.0).Return(expectedResult, nil)

	// Test Pause method call
	result, err := mockAgentBay.Pause(testSession, 600, 2.0)

	// Verify the result
	assert.NoError(t, err)
	assert.NotNil(t, result)
	assert.False(t, result.Success)
	assert.Equal(t, "RUNNING", result.Status)
	assert.Contains(t, result.ErrorMessage, "unexpected state")
	assert.Contains(t, result.ErrorMessage, "RUNNING")
}

// TestAgentBay_Pause_UnexpectedStateOther tests Pause method with unexpected OTHER state
func TestAgentBay_Pause_UnexpectedStateOther(t *testing.T) {
	ctrl := gomock.NewController(t)
	defer ctrl.Finish()

	// Create mock AgentBay client
	mockAgentBay := mock.NewMockAgentBayInterface(ctrl)

	// Create a real session for testing
	client, _ := agentbay.NewAgentBay("test-api-key")
	testSession := agentbay.NewSession(client, "test-session-id")

	// Set expected behavior for pause with unexpected state
	expectedResult := &models.SessionPauseResult{
		ApiResponse: models.ApiResponse{
			RequestID: "test-request-id",
		},
		Success:      false,
		ErrorMessage: "Session pause failed: unexpected state 'OTHER'",
		Status:       "OTHER",
	}
	mockAgentBay.EXPECT().Pause(testSession, 600, 2.0).Return(expectedResult, nil)

	// Test Pause method call
	result, err := mockAgentBay.Pause(testSession, 600, 2.0)

	// Verify the result
	assert.NoError(t, err)
	assert.NotNil(t, result)
	assert.False(t, result.Success)
	assert.Equal(t, "OTHER", result.Status)
	assert.Contains(t, result.ErrorMessage, "unexpected state")
	assert.Contains(t, result.ErrorMessage, "OTHER")
}

// TestAgentBay_Resume_UnexpectedStatePaused tests Resume method with unexpected PAUSED state
func TestAgentBay_Resume_UnexpectedStatePaused(t *testing.T) {
	ctrl := gomock.NewController(t)
	defer ctrl.Finish()

	// Create mock AgentBay client
	mockAgentBay := mock.NewMockAgentBayInterface(ctrl)

	// Create a real session for testing
	client, _ := agentbay.NewAgentBay("test-api-key")
	testSession := agentbay.NewSession(client, "test-session-id")

	// Set expected behavior for resume with unexpected state
	expectedResult := &models.SessionResumeResult{
		ApiResponse: models.ApiResponse{
			RequestID: "test-request-id",
		},
		Success:      false,
		ErrorMessage: "Session resume failed: unexpected state 'PAUSED'",
		Status:       "PAUSED",
	}
	mockAgentBay.EXPECT().Resume(testSession, 600, 2.0).Return(expectedResult, nil)

	// Test Resume method call
	result, err := mockAgentBay.Resume(testSession, 600, 2.0)

	// Verify the result
	assert.NoError(t, err)
	assert.NotNil(t, result)
	assert.False(t, result.Success)
	assert.Equal(t, "PAUSED", result.Status)
	assert.Contains(t, result.ErrorMessage, "unexpected state")
	assert.Contains(t, result.ErrorMessage, "PAUSED")
}

// TestAgentBay_Resume_UnexpectedStateUnknown tests Resume method with unexpected UNKNOWN state
func TestAgentBay_Resume_UnexpectedStateUnknown(t *testing.T) {
	ctrl := gomock.NewController(t)
	defer ctrl.Finish()

	// Create mock AgentBay client
	mockAgentBay := mock.NewMockAgentBayInterface(ctrl)

	// Create a real session for testing
	client, _ := agentbay.NewAgentBay("test-api-key")
	testSession := agentbay.NewSession(client, "test-session-id")

	// Set expected behavior for resume with unexpected state
	expectedResult := &models.SessionResumeResult{
		ApiResponse: models.ApiResponse{
			RequestID: "test-request-id",
		},
		Success:      false,
		ErrorMessage: "Session resume failed: unexpected state 'UNKNOWN'",
		Status:       "UNKNOWN",
	}
	mockAgentBay.EXPECT().Resume(testSession, 600, 2.0).Return(expectedResult, nil)

	// Test Resume method call
	result, err := mockAgentBay.Resume(testSession, 600, 2.0)

	// Verify the result
	assert.NoError(t, err)
	assert.NotNil(t, result)
	assert.False(t, result.Success)
	assert.Equal(t, "UNKNOWN", result.Status)
	assert.Contains(t, result.ErrorMessage, "unexpected state")
	assert.Contains(t, result.ErrorMessage, "UNKNOWN")
}
