package agentbay_test

import (
	"testing"

	"github.com/alibabacloud-go/tea/tea"
	"github.com/aliyun/wuying-agentbay-sdk/golang/api/client"
	"github.com/aliyun/wuying-agentbay-sdk/golang/pkg/agentbay"
	"github.com/stretchr/testify/assert"
)

func TestParseGetSkillMetaDataResponse_Success(t *testing.T) {
	body := &client.GetSkillMetaDataResponseBody{
		Success: tea.Bool(true),
		Data: &client.GetSkillMetaDataResponseBodyData{
			SkillPath: tea.String("/home/wuying/skills"),
			MetaDataList: []*client.GetSkillMetaDataResponseBodyDataMetaDataList{
				{Name: tea.String("pdf"), Description: tea.String("PDF processing skill")},
				{Name: tea.String("docx"), Description: tea.String("Word document skill")},
			},
		},
	}

	result, err := agentbay.ParseGetSkillMetaDataResponse(body)

	assert.NoError(t, err)
	assert.NotNil(t, result)
	assert.Equal(t, "/home/wuying/skills", result.SkillsRootPath)
	assert.Len(t, result.Skills, 2)
	assert.Equal(t, "pdf", result.Skills[0].Name)
	assert.Equal(t, "PDF processing skill", result.Skills[0].Description)
	assert.Equal(t, "docx", result.Skills[1].Name)
	assert.Equal(t, "Word document skill", result.Skills[1].Description)
}

func TestParseGetSkillMetaDataResponse_PassesGroupIds(t *testing.T) {
	body := &client.GetSkillMetaDataResponseBody{
		Success: tea.Bool(true),
		Data: &client.GetSkillMetaDataResponseBodyData{
			SkillPath:    tea.String("/skills"),
			MetaDataList: []*client.GetSkillMetaDataResponseBodyDataMetaDataList{},
		},
	}

	result, err := agentbay.ParseGetSkillMetaDataResponse(body)

	assert.NoError(t, err)
	assert.NotNil(t, result)
	assert.Equal(t, "/skills", result.SkillsRootPath)
	assert.Empty(t, result.Skills)
}

func TestParseGetSkillMetaDataResponse_APIFailure(t *testing.T) {
	body := &client.GetSkillMetaDataResponseBody{
		Success: tea.Bool(false),
		Code:    tea.String("InvalidRequest"),
		Message: tea.String("Bad group id"),
	}

	result, err := agentbay.ParseGetSkillMetaDataResponse(body)

	assert.Error(t, err)
	assert.Nil(t, result)
	assert.Contains(t, err.Error(), "GetSkillMetaData failed")
	assert.Contains(t, err.Error(), "InvalidRequest")
	assert.Contains(t, err.Error(), "Bad group id")
}

func TestParseGetSkillMetaDataResponse_SkipsEmptyNames(t *testing.T) {
	body := &client.GetSkillMetaDataResponseBody{
		Success: tea.Bool(true),
		Data: &client.GetSkillMetaDataResponseBodyData{
			SkillPath: tea.String("/skills"),
			MetaDataList: []*client.GetSkillMetaDataResponseBodyDataMetaDataList{
				{Name: tea.String(""), Description: tea.String("Should be skipped")},
				{Name: tea.String("valid-skill"), Description: tea.String("Valid")},
			},
		},
	}

	result, err := agentbay.ParseGetSkillMetaDataResponse(body)

	assert.NoError(t, err)
	assert.NotNil(t, result)
	assert.Len(t, result.Skills, 1)
	assert.Equal(t, "valid-skill", result.Skills[0].Name)
	assert.Equal(t, "Valid", result.Skills[0].Description)
}

func TestParseGetSkillMetaDataResponse_NilBody(t *testing.T) {
	result, err := agentbay.ParseGetSkillMetaDataResponse(nil)

	assert.Error(t, err)
	assert.Nil(t, result)
	assert.Contains(t, err.Error(), "missing response body")
}

func TestParseGetSkillMetaDataResponse_NilData(t *testing.T) {
	body := &client.GetSkillMetaDataResponseBody{
		Success: tea.Bool(true),
		Data:    nil,
	}

	result, err := agentbay.ParseGetSkillMetaDataResponse(body)

	assert.Error(t, err)
	assert.Nil(t, result)
	assert.Contains(t, err.Error(), "invalid Data field")
}

func TestParseGetSkillMetaDataResponse_EmptyMetaDataList(t *testing.T) {
	body := &client.GetSkillMetaDataResponseBody{
		Success: tea.Bool(true),
		Data: &client.GetSkillMetaDataResponseBodyData{
			SkillPath:    tea.String("/skills"),
			MetaDataList: nil,
		},
	}

	result, err := agentbay.ParseGetSkillMetaDataResponse(body)

	assert.NoError(t, err)
	assert.NotNil(t, result)
	assert.Len(t, result.Skills, 0)
	assert.Equal(t, "/skills", result.SkillsRootPath)
}
