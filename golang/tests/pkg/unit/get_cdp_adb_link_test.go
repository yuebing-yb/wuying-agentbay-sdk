package agentbay_test

import (
	"testing"

	"github.com/alibabacloud-go/tea/dara"
	"github.com/aliyun/wuying-agentbay-sdk/golang/api/client"
	"github.com/stretchr/testify/assert"
	"github.com/stretchr/testify/mock"
)

// MockClient is a mock implementation of the Client
type MockGetCdpAdbLinkClient struct {
	mock.Mock
}

func (m *MockGetCdpAdbLinkClient) GetCdpLink(request *client.GetCdpLinkRequest) (*client.GetCdpLinkResponse, error) {
	args := m.Called(request)
	if args.Get(0) == nil {
		return nil, args.Error(1)
	}
	return args.Get(0).(*client.GetCdpLinkResponse), args.Error(1)
}

func (m *MockGetCdpAdbLinkClient) GetAdbLink(request *client.GetAdbLinkRequest) (*client.GetAdbLinkResponse, error) {
	args := m.Called(request)
	if args.Get(0) == nil {
		return nil, args.Error(1)
	}
	return args.Get(0).(*client.GetAdbLinkResponse), args.Error(1)
}

func TestGetCdpLink_Success(t *testing.T) {
	// Arrange
	mockClient := new(MockGetCdpAdbLinkClient)

	expectedURL := "ws://test.cdp.link"
	expectedRequestID := "req123"

	mockResponse := &client.GetCdpLinkResponse{
		Body: &client.GetCdpLinkResponseBody{
			Success:   dara.Bool(true),
			RequestId: dara.String(expectedRequestID),
			Data: &client.GetCdpLinkResponseBodyData{
				Url: dara.String(expectedURL),
			},
		},
	}

	request := &client.GetCdpLinkRequest{
		Authorization: dara.String("Bearer test_token"),
		SessionId:     dara.String("test_session_id"),
	}

	mockClient.On("GetCdpLink", request).Return(mockResponse, nil)

	// Act
	response, err := mockClient.GetCdpLink(request)

	// Assert
	assert.NoError(t, err)
	assert.NotNil(t, response)
	assert.NotNil(t, response.Body)
	assert.True(t, *response.Body.Success)
	assert.Equal(t, expectedURL, *response.Body.Data.Url)
	assert.Equal(t, expectedRequestID, *response.Body.RequestId)

	mockClient.AssertExpectations(t)
}

func TestGetCdpLink_Failure(t *testing.T) {
	// Arrange
	mockClient := new(MockGetCdpAdbLinkClient)

	mockResponse := &client.GetCdpLinkResponse{
		Body: &client.GetCdpLinkResponseBody{
			Success: dara.Bool(false),
			Message: dara.String("API error"),
		},
	}

	request := &client.GetCdpLinkRequest{
		Authorization: dara.String("Bearer test_token"),
		SessionId:     dara.String("invalid_session"),
	}

	mockClient.On("GetCdpLink", request).Return(mockResponse, nil)

	// Act
	response, err := mockClient.GetCdpLink(request)

	// Assert
	assert.NoError(t, err)
	assert.NotNil(t, response)
	assert.NotNil(t, response.Body)
	assert.False(t, *response.Body.Success)
	assert.Equal(t, "API error", *response.Body.Message)

	mockClient.AssertExpectations(t)
}

func TestGetAdbLink_Success(t *testing.T) {
	// Arrange
	mockClient := new(MockGetCdpAdbLinkClient)

	expectedURL := "adb://test.adb.link:5555"
	expectedRequestID := "req456"

	mockResponse := &client.GetAdbLinkResponse{
		Body: &client.GetAdbLinkResponseBody{
			Success:   dara.Bool(true),
			RequestId: dara.String(expectedRequestID),
			Data: &client.GetAdbLinkResponseBodyData{
				Url: dara.String(expectedURL),
			},
		},
	}

	request := &client.GetAdbLinkRequest{
		Authorization: dara.String("Bearer test_token"),
		SessionId:     dara.String("test_session_id"),
		Option:        dara.String(`{"adbkey_pub":"test-public-key"}`),
	}

	mockClient.On("GetAdbLink", request).Return(mockResponse, nil)

	// Act
	response, err := mockClient.GetAdbLink(request)

	// Assert
	assert.NoError(t, err)
	assert.NotNil(t, response)
	assert.NotNil(t, response.Body)
	assert.True(t, *response.Body.Success)
	assert.Equal(t, expectedURL, *response.Body.Data.Url)
	assert.Equal(t, expectedRequestID, *response.Body.RequestId)

	mockClient.AssertExpectations(t)
}

func TestGetAdbLink_Failure(t *testing.T) {
	// Arrange
	mockClient := new(MockGetCdpAdbLinkClient)

	mockResponse := &client.GetAdbLinkResponse{
		Body: &client.GetAdbLinkResponseBody{
			Success: dara.Bool(false),
			Message: dara.String("API error"),
		},
	}

	request := &client.GetAdbLinkRequest{
		Authorization: dara.String("Bearer test_token"),
		SessionId:     dara.String("invalid_session"),
		Option:        dara.String(`{"adbkey_pub":"test-key"}`),
	}

	mockClient.On("GetAdbLink", request).Return(mockResponse, nil)

	// Act
	response, err := mockClient.GetAdbLink(request)

	// Assert
	assert.NoError(t, err)
	assert.NotNil(t, response)
	assert.NotNil(t, response.Body)
	assert.False(t, *response.Body.Success)
	assert.Equal(t, "API error", *response.Body.Message)

	mockClient.AssertExpectations(t)
}
