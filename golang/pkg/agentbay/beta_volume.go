package agentbay

import (
	"encoding/json"
	"fmt"

	"github.com/alibabacloud-go/tea/tea"
	mcp "github.com/aliyun/wuying-agentbay-sdk/golang/api/client"
	"github.com/aliyun/wuying-agentbay-sdk/golang/pkg/agentbay/models"
)

// Volume represents a block storage volume (data disk).
// Note: This is a beta feature and may change in future releases.
type Volume struct {
	ID               string
	Name             string
	BelongingImageId string
	Status           string
	CreatedAt        string
}

// BetaVolumeResult wraps volume operation result and RequestID.
type BetaVolumeResult struct {
	models.ApiResponse
	Success      bool
	Volume       *Volume
	ErrorMessage string
}

// BetaVolumeListResult wraps volume list result and RequestID.
type BetaVolumeListResult struct {
	models.ApiResponse
	Success      bool
	Volumes      []*Volume
	NextToken    string
	MaxResults   int32
	TotalCount   int32
	ErrorMessage string
}

// BetaOperationResult is a generic operation result (for delete).
type BetaOperationResult struct {
	models.ApiResponse
	Success      bool
	ErrorMessage string
}

// BetaVolumeService provides beta methods to manage volumes.
type BetaVolumeService struct {
	AgentBay *AgentBay
}

// BetaGetByName gets a volume by name. If create is true, creates the volume if it doesn't exist.
// imageID is required to match the underlying Aliyun SDK request.
func (vs *BetaVolumeService) BetaGetByName(name string, imageID string, create bool) (*BetaVolumeResult, error) {
	if name == "" {
		return nil, fmt.Errorf("name is required")
	}
	if imageID == "" {
		return nil, fmt.Errorf("imageID is required")
	}

	req := &mcp.GetVolumeRequest{
		Authorization: tea.String("Bearer " + vs.AgentBay.APIKey),
		AllowCreate:   tea.Bool(create),
		ImageId:       tea.String(imageID),
		VolumeName:    tea.String(name),
	}

	logAPICall("GetVolume(beta)", fmt.Sprintf("VolumeName=%s, AllowCreate=%t, ImageId=%s", name, create, imageID))
	resp, err := vs.AgentBay.Client.GetVolume(req)
	requestID := models.ExtractRequestID(resp)
	if err != nil {
		logOperationError("GetVolume(beta)", err.Error(), true)
		return &BetaVolumeResult{
			ApiResponse:  models.WithRequestID(requestID),
			Success:      false,
			Volume:       nil,
			ErrorMessage: fmt.Sprintf("Failed to get volume: %v", err),
		}, nil
	}

	if resp == nil || resp.Body == nil {
		return &BetaVolumeResult{
			ApiResponse:  models.WithRequestID(requestID),
			Success:      false,
			Volume:       nil,
			ErrorMessage: "Empty response body",
		}, nil
	}

	success := tea.BoolValue(resp.Body.Success)
	if !success && resp.Body.Code != nil {
		code := tea.StringValue(resp.Body.Code)
		message := tea.StringValue(resp.Body.Message)
		if message == "" {
			message = "Unknown error"
		}
		respJSON, _ := json.MarshalIndent(resp.Body, "", "  ")
		logAPIResponseWithDetails("GetVolume(beta)", requestID, false, nil, string(respJSON))
		return &BetaVolumeResult{
			ApiResponse:  models.WithRequestID(requestID),
			Success:      false,
			Volume:       nil,
			ErrorMessage: fmt.Sprintf("[%s] %s", code, message),
		}, nil
	}

	if resp.Body.Data == nil || resp.Body.Data.VolumeId == nil {
		respJSON, _ := json.MarshalIndent(resp.Body, "", "  ")
		logAPIResponseWithDetails("GetVolume(beta)", requestID, false, nil, string(respJSON))
		return &BetaVolumeResult{
			ApiResponse:  models.WithRequestID(requestID),
			Success:      false,
			Volume:       nil,
			ErrorMessage: "VolumeId not found in response",
		}, nil
	}

	vol := &Volume{
		ID:               tea.StringValue(resp.Body.Data.VolumeId),
		Name:             tea.StringValue(resp.Body.Data.VolumeName),
		BelongingImageId: tea.StringValue(resp.Body.Data.BelongingImageId),
		Status:           tea.StringValue(resp.Body.Data.Status),
		CreatedAt:        tea.StringValue(resp.Body.Data.CreateTime),
	}

	keyFields := map[string]interface{}{
		"volume_id":   vol.ID,
		"volume_name": vol.Name,
		"image_id":    vol.BelongingImageId,
	}
	respJSON, _ := json.MarshalIndent(resp.Body, "", "  ")
	logAPIResponseWithDetails("GetVolume(beta)", requestID, true, keyFields, string(respJSON))

	return &BetaVolumeResult{
		ApiResponse:  models.WithRequestID(requestID),
		Success:      true,
		Volume:       vol,
		ErrorMessage: "",
	}, nil
}

// BetaGetByID gets a volume by ID via ListVolumes(VolumeIds=[id]).
// imageID is required to match the underlying Aliyun SDK request.
func (vs *BetaVolumeService) BetaGetByID(volumeID string, imageID string) (*BetaVolumeResult, error) {
	if volumeID == "" {
		return nil, fmt.Errorf("volumeID is required")
	}
	if imageID == "" {
		return nil, fmt.Errorf("imageID is required")
	}
	idPtr := tea.String(volumeID)
	listResult, err := vs.BetaList(&BetaListVolumesParams{
		ImageID:    imageID,
		MaxResults: 10,
		VolumeIds:  []*string{idPtr},
	})
	if err != nil {
		return nil, err
	}
	if !listResult.Success {
		return &BetaVolumeResult{
			ApiResponse:  listResult.ApiResponse,
			Success:      false,
			Volume:       nil,
			ErrorMessage: listResult.ErrorMessage,
		}, nil
	}
	if len(listResult.Volumes) == 0 {
		return &BetaVolumeResult{
			ApiResponse:  listResult.ApiResponse,
			Success:      false,
			Volume:       nil,
			ErrorMessage: "Volume not found",
		}, nil
	}
	return &BetaVolumeResult{
		ApiResponse:  listResult.ApiResponse,
		Success:      true,
		Volume:       listResult.Volumes[0],
		ErrorMessage: "",
	}, nil
}

// BetaListVolumesParams contains parameters for listing volumes.
type BetaListVolumesParams struct {
	ImageID    string
	MaxResults int32
	NextToken  string
	VolumeIds  []*string
	VolumeName string
}

// BetaList lists volumes.
// imageID is required to match the underlying Aliyun SDK request.
func (vs *BetaVolumeService) BetaList(params *BetaListVolumesParams) (*BetaVolumeListResult, error) {
	if params == nil {
		params = &BetaListVolumesParams{MaxResults: 10}
	}
	if params.ImageID == "" {
		return nil, fmt.Errorf("imageID is required")
	}
	if params.MaxResults <= 0 {
		params.MaxResults = 10
	}

	req := &mcp.ListVolumesRequest{
		Authorization: tea.String("Bearer " + vs.AgentBay.APIKey),
		ImageId:       tea.String(params.ImageID),
		MaxResults:    tea.Int32(params.MaxResults),
	}
	if params.NextToken != "" {
		req.NextToken = tea.String(params.NextToken)
	}
	if params.VolumeIds != nil && len(params.VolumeIds) > 0 {
		req.VolumeIds = params.VolumeIds
	}
	if params.VolumeName != "" {
		req.VolumeName = tea.String(params.VolumeName)
	}

	logAPICall("ListVolumes(beta)", fmt.Sprintf("ImageId=%s, MaxResults=%d", params.ImageID, params.MaxResults))
	resp, err := vs.AgentBay.Client.ListVolumes(req)
	requestID := models.ExtractRequestID(resp)
	if err != nil {
		logOperationError("ListVolumes(beta)", err.Error(), true)
		return &BetaVolumeListResult{
			ApiResponse:  models.WithRequestID(requestID),
			Success:      false,
			Volumes:      []*Volume{},
			ErrorMessage: fmt.Sprintf("Failed to list volumes: %v", err),
		}, nil
	}

	if resp == nil || resp.Body == nil {
		return &BetaVolumeListResult{
			ApiResponse:  models.WithRequestID(requestID),
			Success:      false,
			Volumes:      []*Volume{},
			ErrorMessage: "Empty response body",
		}, nil
	}

	success := tea.BoolValue(resp.Body.Success)
	if !success && resp.Body.Code != nil {
		code := tea.StringValue(resp.Body.Code)
		message := tea.StringValue(resp.Body.Message)
		if message == "" {
			message = "Unknown error"
		}
		respJSON, _ := json.MarshalIndent(resp.Body, "", "  ")
		logAPIResponseWithDetails("ListVolumes(beta)", requestID, false, nil, string(respJSON))
		return &BetaVolumeListResult{
			ApiResponse:  models.WithRequestID(requestID),
			Success:      false,
			Volumes:      []*Volume{},
			ErrorMessage: fmt.Sprintf("[%s] %s", code, message),
		}, nil
	}

	volumes := []*Volume{}
	if resp.Body.Data != nil {
		for _, it := range resp.Body.Data {
			if it == nil {
				continue
			}
			volumes = append(volumes, &Volume{
				ID:               tea.StringValue(it.VolumeId),
				Name:             tea.StringValue(it.VolumeName),
				BelongingImageId: tea.StringValue(it.BelongingImageId),
				Status:           tea.StringValue(it.Status),
				CreatedAt:        tea.StringValue(it.CreateTime),
			})
		}
	}

	nextToken := tea.StringValue(resp.Body.NextToken)
	maxResults := params.MaxResults
	if resp.Body.MaxResults != nil {
		maxResults = tea.Int32Value(resp.Body.MaxResults)
	}

	keyFields := map[string]interface{}{
		"image_id":      params.ImageID,
		"volume_count":  len(volumes),
		"max_results":   maxResults,
		"total_count":   len(volumes),
		"has_next_page": nextToken != "",
	}
	respJSON, _ := json.MarshalIndent(resp.Body, "", "  ")
	logAPIResponseWithDetails("ListVolumes(beta)", requestID, true, keyFields, string(respJSON))

	return &BetaVolumeListResult{
		ApiResponse:  models.WithRequestID(requestID),
		Success:      true,
		Volumes:      volumes,
		NextToken:    nextToken,
		MaxResults:   maxResults,
		TotalCount:   int32(len(volumes)),
		ErrorMessage: "",
	}, nil
}

// BetaDelete deletes a volume by ID.
func (vs *BetaVolumeService) BetaDelete(volumeID string) (*BetaOperationResult, error) {
	if volumeID == "" {
		return nil, fmt.Errorf("volumeID is required")
	}

	req := &mcp.DeleteVolumeRequest{
		Authorization: tea.String("Bearer " + vs.AgentBay.APIKey),
		VolumeId:      tea.String(volumeID),
	}

	logAPICall("DeleteVolume(beta)", fmt.Sprintf("VolumeId=%s", volumeID))
	resp, err := vs.AgentBay.Client.DeleteVolume(req)
	requestID := models.ExtractRequestID(resp)
	if err != nil {
		logOperationError("DeleteVolume(beta)", err.Error(), true)
		return &BetaOperationResult{
			ApiResponse:  models.WithRequestID(requestID),
			Success:      false,
			ErrorMessage: fmt.Sprintf("Failed to delete volume: %v", err),
		}, nil
	}

	if resp == nil || resp.Body == nil {
		return &BetaOperationResult{
			ApiResponse:  models.WithRequestID(requestID),
			Success:      false,
			ErrorMessage: "Empty response body",
		}, nil
	}

	success := tea.BoolValue(resp.Body.Success)
	if !success && resp.Body.Code != nil {
		code := tea.StringValue(resp.Body.Code)
		message := tea.StringValue(resp.Body.Message)
		if message == "" {
			message = "Unknown error"
		}
		respJSON, _ := json.MarshalIndent(resp.Body, "", "  ")
		logAPIResponseWithDetails("DeleteVolume(beta)", requestID, false, nil, string(respJSON))
		return &BetaOperationResult{
			ApiResponse:  models.WithRequestID(requestID),
			Success:      false,
			ErrorMessage: fmt.Sprintf("[%s] %s", code, message),
		}, nil
	}

	respJSON, _ := json.MarshalIndent(resp.Body, "", "  ")
	logAPIResponseWithDetails("DeleteVolume(beta)", requestID, true, map[string]interface{}{"volume_id": volumeID}, string(respJSON))

	return &BetaOperationResult{
		ApiResponse:  models.WithRequestID(requestID),
		Success:      true,
		ErrorMessage: "",
	}, nil
}
