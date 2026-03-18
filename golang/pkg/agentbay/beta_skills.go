package agentbay

import (
	"fmt"
	"strings"
	"time"

	"github.com/alibabacloud-go/tea/tea"
	mcp "github.com/aliyun/wuying-agentbay-sdk/golang/api/client"
)

// SkillMetadataItem represents official skill metadata returned by GetSkillMetaData or ListSkillMetaData.
type SkillMetadataItem struct {
	Name        string
	Description string
}

// SkillsMetadataResult contains skills list and root path from GetSkillMetaData.
type SkillsMetadataResult struct {
	Skills         []SkillMetadataItem
	SkillsRootPath string
}

// GetMetadataOptions provides optional filtering for GetMetadata.
type GetMetadataOptions struct {
	ImageID    string
	SkillNames []string
}

// BetaSkillsService provides beta methods to list and get official skills metadata.
type BetaSkillsService struct {
	AgentBay *AgentBay
}

// GetMetadata fetches skills metadata via POP Action GetSkillMetaData.
// Returns SkillsMetadataResult with skills list and skillsRootPath.
func (s *BetaSkillsService) GetMetadata(opts ...GetMetadataOptions) (*SkillsMetadataResult, error) {
	opt := GetMetadataOptions{}
	if len(opts) > 0 {
		opt = opts[0]
	}

	request := &mcp.GetSkillMetaDataRequest{
		Authorization: tea.String("Bearer " + s.AgentBay.APIKey),
	}
	if opt.ImageID != "" {
		request.ImageId = tea.String(opt.ImageID)
	}
	if len(opt.SkillNames) > 0 {
		skillPtrs := make([]*string, len(opt.SkillNames))
		for i, name := range opt.SkillNames {
			skillPtrs[i] = tea.String(name)
		}
		request.SkillGroupIds = skillPtrs
	}

	maxAttempts := 3
	delay := 200 * time.Millisecond
	var resp *mcp.GetSkillMetaDataResponse
	var err error
	for attempt := 1; attempt <= maxAttempts; attempt++ {
		resp, err = s.AgentBay.Client.GetSkillMetaData(request)
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
	if err != nil {
		return nil, fmt.Errorf("GetSkillMetaData failed: %w", err)
	}
	if resp == nil || resp.Body == nil {
		return nil, fmt.Errorf("GetSkillMetaData failed: missing response body")
	}

	return ParseGetSkillMetaDataResponse(resp.Body)
}

// ParseGetSkillMetaDataResponse parses GetSkillMetaDataResponseBody into SkillsMetadataResult.
// Exported for unit testing.
func ParseGetSkillMetaDataResponse(body *mcp.GetSkillMetaDataResponseBody) (*SkillsMetadataResult, error) {
	if body == nil {
		return nil, fmt.Errorf("GetSkillMetaData failed: missing response body")
	}
	if body.Success == nil || !*body.Success {
		msg := ""
		if body.Message != nil {
			msg = *body.Message
		}
		code := ""
		if body.Code != nil {
			code = *body.Code
		}
		if code != "" {
			return nil, fmt.Errorf("GetSkillMetaData failed: [%s] %s", code, msg)
		}
		if msg == "" {
			msg = "Unknown error"
		}
		return nil, fmt.Errorf("GetSkillMetaData failed: %s", msg)
	}

	data := body.Data
	if data == nil {
		return nil, fmt.Errorf("GetSkillMetaData failed: invalid Data field")
	}

	skillPath := ""
	if data.SkillPath != nil {
		skillPath = *data.SkillPath
	}

	items := make([]SkillMetadataItem, 0)
	if data.MetaDataList != nil {
		for _, raw := range data.MetaDataList {
			if raw == nil {
				continue
			}
			name := strings.TrimSpace(tea.StringValue(raw.Name))
			if name == "" {
				continue
			}
			desc := tea.StringValue(raw.Description)
			items = append(items, SkillMetadataItem{
				Name:        name,
				Description: desc,
			})
		}
	}

	return &SkillsMetadataResult{
		Skills:         items,
		SkillsRootPath: skillPath,
	}, nil
}

// ListMetadata lists official skills metadata via POP Action ListSkillMetaData.
//
// Deprecated: Use GetMetadata instead, which returns both skills and skillsRootPath.
func (s *BetaSkillsService) ListMetadata() ([]SkillMetadataItem, error) {
	request := &mcp.ListSkillMetaDataRequest{
		Authorization: tea.String("Bearer " + s.AgentBay.APIKey),
	}

	maxAttempts := 3
	delay := 200 * time.Millisecond
	var resp *mcp.ListSkillMetaDataResponse
	var err error
	for attempt := 1; attempt <= maxAttempts; attempt++ {
		resp, err = s.AgentBay.Client.ListSkillMetaData(request)
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
	if err != nil {
		return nil, fmt.Errorf("ListSkillMetaData failed: %w", err)
	}
	if resp == nil || resp.Body == nil {
		return nil, fmt.Errorf("ListSkillMetaData failed: missing response body")
	}

	body := resp.Body
	if body.Success == nil || !*body.Success {
		msg := ""
		if body.Message != nil {
			msg = *body.Message
		}
		code := ""
		if body.Code != nil {
			code = *body.Code
		}
		if code != "" {
			return nil, fmt.Errorf("ListSkillMetaData failed: [%s] %s", code, msg)
		}
		if msg == "" {
			msg = "Unknown error"
		}
		return nil, fmt.Errorf("ListSkillMetaData failed: %s", msg)
	}

	data := body.Data
	if data == nil {
		return nil, fmt.Errorf("ListSkillMetaData failed: invalid Data field")
	}

	items := make([]SkillMetadataItem, 0, len(data))
	for _, raw := range data {
		if raw == nil {
			continue
		}
		name := strings.TrimSpace(tea.StringValue(raw.Name))
		if name == "" {
			continue
		}
		desc := tea.StringValue(raw.Description)
		items = append(items, SkillMetadataItem{
			Name:        name,
			Description: desc,
		})
	}
	return items, nil
}
