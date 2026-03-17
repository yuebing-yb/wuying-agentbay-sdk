package agentbay

import (
	"fmt"
	"strings"
	"time"

	"github.com/alibabacloud-go/tea/tea"
	mcp "github.com/aliyun/wuying-agentbay-sdk/golang/api/client"
)

// SkillMetadataItem represents official skill metadata returned by ListSkillMetaData.
type SkillMetadataItem struct {
	Name        string
	Description string
}

// BetaSkillsService provides beta methods to list official skills metadata.
type BetaSkillsService struct {
	AgentBay *AgentBay
}

// ListMetadata lists official skills metadata via POP Action ListSkillMetaData.
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
