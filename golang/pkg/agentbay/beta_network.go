package agentbay

import (
	"fmt"
	"strings"
	"time"

	"github.com/alibabacloud-go/tea/tea"
	mcp "github.com/aliyun/wuying-agentbay-sdk/golang/api/client"
	"github.com/aliyun/wuying-agentbay-sdk/golang/pkg/agentbay/models"
)

// BetaNetworkResult wraps beta network bind token result and RequestID.
type BetaNetworkResult struct {
	models.ApiResponse
	Success      bool
	NetworkId    string
	NetworkToken string
	ErrorMessage string
}

// BetaNetworkStatusResult wraps beta network status result and RequestID.
type BetaNetworkStatusResult struct {
	models.ApiResponse
	Success      bool
	Online       bool
	ErrorMessage string
}

// BetaNetworkService provides beta methods to manage networks.
type BetaNetworkService struct {
	AgentBay *AgentBay
}

// BetaGetNetworkBindToken creates a network (or reuses provided networkId) and returns networkId + networkToken.
func (ns *BetaNetworkService) BetaGetNetworkBindToken(networkId string) (*BetaNetworkResult, error) {
	request := &mcp.CreateNetworkRequest{
		Authorization: tea.String("Bearer " + ns.AgentBay.APIKey),
	}
	if networkId != "" {
		request.NetworkId = tea.String(networkId)
	}

	maxAttempts := 3
	delay := 200 * time.Millisecond
	var resp *mcp.CreateNetworkResponse
	var err error
	for attempt := 1; attempt <= maxAttempts; attempt++ {
		resp, err = ns.AgentBay.Client.CreateNetwork(request)
		if err == nil {
			break
		}
		if attempt < maxAttempts {
			errStr := err.Error()
			if strings.Contains(errStr, "ServiceUnavailable") || strings.Contains(errStr, "503") {
				time.Sleep(delay)
				delay *= 2
				continue
			}
		}
	}

	requestID := models.ExtractRequestID(resp)
	if err != nil {
		return &BetaNetworkResult{
			ApiResponse:  models.ApiResponse{RequestID: requestID},
			Success:      false,
			ErrorMessage: fmt.Sprintf("Failed to create network: %v", err),
		}, nil
	}

	if resp == nil || resp.Body == nil {
		return &BetaNetworkResult{
			ApiResponse:  models.ApiResponse{RequestID: requestID},
			Success:      false,
			ErrorMessage: "Invalid response from CreateNetwork API",
		}, nil
	}

	body := resp.Body
	if body.Success == nil || !*body.Success {
		errorMsg := "Unknown error"
		if body.Message != nil {
			errorMsg = *body.Message
		}
		if body.Code != nil {
			errorMsg = fmt.Sprintf("[%s] %s", *body.Code, errorMsg)
		}
		return &BetaNetworkResult{
			ApiResponse:  models.ApiResponse{RequestID: requestID},
			Success:      false,
			ErrorMessage: errorMsg,
		}, nil
	}

	if body.Data == nil {
		return &BetaNetworkResult{
			ApiResponse:  models.ApiResponse{RequestID: requestID},
			Success:      false,
			ErrorMessage: "Network data not found in response",
		}, nil
	}

	createdNetworkID := ""
	if body.Data.NetworkId != nil {
		createdNetworkID = *body.Data.NetworkId
	}
	networkToken := ""
	if body.Data.NetworkToken != nil {
		networkToken = *body.Data.NetworkToken
	}

	return &BetaNetworkResult{
		ApiResponse:  models.ApiResponse{RequestID: requestID},
		Success:      true,
		NetworkId:    createdNetworkID,
		NetworkToken: networkToken,
		ErrorMessage: "",
	}, nil
}

// BetaDescribe queries beta network status (online/offline).
func (ns *BetaNetworkService) BetaDescribe(networkId string) (*BetaNetworkStatusResult, error) {
	if networkId == "" {
		return &BetaNetworkStatusResult{
			ApiResponse:  models.ApiResponse{RequestID: ""},
			Success:      false,
			Online:       false,
			ErrorMessage: "network_id is required",
		}, nil
	}

	request := &mcp.DescribeNetworkRequest{
		Authorization: tea.String("Bearer " + ns.AgentBay.APIKey),
		NetworkId:     tea.String(networkId),
	}

	maxAttempts := 3
	delay := 200 * time.Millisecond
	var resp *mcp.DescribeNetworkResponse
	var err error
	for attempt := 1; attempt <= maxAttempts; attempt++ {
		resp, err = ns.AgentBay.Client.DescribeNetwork(request)
		if err == nil {
			break
		}
		if attempt < maxAttempts {
			errStr := err.Error()
			if strings.Contains(errStr, "ServiceUnavailable") || strings.Contains(errStr, "503") {
				time.Sleep(delay)
				delay *= 2
				continue
			}
		}
	}

	requestID := models.ExtractRequestID(resp)
	if err != nil {
		errorStr := err.Error()
		if strings.Contains(errorStr, "NotFound") {
			return &BetaNetworkStatusResult{
				ApiResponse:  models.ApiResponse{RequestID: requestID},
				Success:      false,
				Online:       false,
				ErrorMessage: fmt.Sprintf("Network %s not found", networkId),
			}, nil
		}
		return &BetaNetworkStatusResult{
			ApiResponse:  models.ApiResponse{RequestID: requestID},
			Success:      false,
			Online:       false,
			ErrorMessage: fmt.Sprintf("Failed to describe network: %v", err),
		}, nil
	}

	if resp == nil || resp.Body == nil {
		return &BetaNetworkStatusResult{
			ApiResponse:  models.ApiResponse{RequestID: requestID},
			Success:      false,
			Online:       false,
			ErrorMessage: "Invalid response from DescribeNetwork API",
		}, nil
	}

	body := resp.Body
	if body.Success == nil || !*body.Success {
		errorMsg := "Unknown error"
		if body.Message != nil {
			errorMsg = *body.Message
		}
		if body.Code != nil {
			errorMsg = fmt.Sprintf("[%s] %s", *body.Code, errorMsg)
		}
		return &BetaNetworkStatusResult{
			ApiResponse:  models.ApiResponse{RequestID: requestID},
			Success:      false,
			Online:       false,
			ErrorMessage: errorMsg,
		}, nil
	}

	online := false
	if body.Data != nil && body.Data.Online != nil {
		online = *body.Data.Online
	}
	return &BetaNetworkStatusResult{
		ApiResponse:  models.ApiResponse{RequestID: requestID},
		Success:      true,
		Online:       online,
		ErrorMessage: "",
	}, nil
}
