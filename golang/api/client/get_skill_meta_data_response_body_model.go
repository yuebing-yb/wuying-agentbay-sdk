// This file is auto-generated, don't edit it. Thanks.
package client

import (
	"github.com/alibabacloud-go/tea/dara"
)

type iGetSkillMetaDataResponseBody interface {
	dara.Model
	String() string
	GoString() string
	SetCode(v string) *GetSkillMetaDataResponseBody
	GetCode() *string
	SetData(v *GetSkillMetaDataResponseBodyData) *GetSkillMetaDataResponseBody
	GetData() *GetSkillMetaDataResponseBodyData
	SetHttpStatusCode(v int32) *GetSkillMetaDataResponseBody
	GetHttpStatusCode() *int32
	SetMessage(v string) *GetSkillMetaDataResponseBody
	GetMessage() *string
	SetRequestId(v string) *GetSkillMetaDataResponseBody
	GetRequestId() *string
	SetSuccess(v bool) *GetSkillMetaDataResponseBody
	GetSuccess() *bool
	SetTotalCount(v int32) *GetSkillMetaDataResponseBody
	GetTotalCount() *int32
}

type GetSkillMetaDataResponseBody struct {
	Code           *string                           `json:"Code,omitempty" xml:"Code,omitempty"`
	Data           *GetSkillMetaDataResponseBodyData `json:"Data,omitempty" xml:"Data,omitempty" type:"Struct"`
	HttpStatusCode *int32                            `json:"HttpStatusCode,omitempty" xml:"HttpStatusCode,omitempty"`
	Message        *string                           `json:"Message,omitempty" xml:"Message,omitempty"`
	RequestId      *string                           `json:"RequestId,omitempty" xml:"RequestId,omitempty"`
	Success        *bool                             `json:"Success,omitempty" xml:"Success,omitempty"`
	TotalCount     *int32                            `json:"TotalCount,omitempty" xml:"TotalCount,omitempty"`
}

func (s GetSkillMetaDataResponseBody) String() string {
	return dara.Prettify(s)
}

func (s GetSkillMetaDataResponseBody) GoString() string {
	return s.String()
}

func (s *GetSkillMetaDataResponseBody) GetCode() *string {
	return s.Code
}

func (s *GetSkillMetaDataResponseBody) GetData() *GetSkillMetaDataResponseBodyData {
	return s.Data
}

func (s *GetSkillMetaDataResponseBody) GetHttpStatusCode() *int32 {
	return s.HttpStatusCode
}

func (s *GetSkillMetaDataResponseBody) GetMessage() *string {
	return s.Message
}

func (s *GetSkillMetaDataResponseBody) GetRequestId() *string {
	return s.RequestId
}

func (s *GetSkillMetaDataResponseBody) GetSuccess() *bool {
	return s.Success
}

func (s *GetSkillMetaDataResponseBody) GetTotalCount() *int32 {
	return s.TotalCount
}

func (s *GetSkillMetaDataResponseBody) SetCode(v string) *GetSkillMetaDataResponseBody {
	s.Code = &v
	return s
}

func (s *GetSkillMetaDataResponseBody) SetData(v *GetSkillMetaDataResponseBodyData) *GetSkillMetaDataResponseBody {
	s.Data = v
	return s
}

func (s *GetSkillMetaDataResponseBody) SetHttpStatusCode(v int32) *GetSkillMetaDataResponseBody {
	s.HttpStatusCode = &v
	return s
}

func (s *GetSkillMetaDataResponseBody) SetMessage(v string) *GetSkillMetaDataResponseBody {
	s.Message = &v
	return s
}

func (s *GetSkillMetaDataResponseBody) SetRequestId(v string) *GetSkillMetaDataResponseBody {
	s.RequestId = &v
	return s
}

func (s *GetSkillMetaDataResponseBody) SetSuccess(v bool) *GetSkillMetaDataResponseBody {
	s.Success = &v
	return s
}

func (s *GetSkillMetaDataResponseBody) SetTotalCount(v int32) *GetSkillMetaDataResponseBody {
	s.TotalCount = &v
	return s
}

func (s *GetSkillMetaDataResponseBody) Validate() error {
	if s.Data != nil {
		if err := s.Data.Validate(); err != nil {
			return err
		}
	}
	return nil
}

type GetSkillMetaDataResponseBodyData struct {
	MetaDataList []*GetSkillMetaDataResponseBodyDataMetaDataList `json:"MetaDataList,omitempty" xml:"MetaDataList,omitempty" type:"Repeated"`
	SkillPath    *string                                         `json:"SkillPath,omitempty" xml:"SkillPath,omitempty"`
}

func (s GetSkillMetaDataResponseBodyData) String() string {
	return dara.Prettify(s)
}

func (s GetSkillMetaDataResponseBodyData) GoString() string {
	return s.String()
}

func (s *GetSkillMetaDataResponseBodyData) GetMetaDataList() []*GetSkillMetaDataResponseBodyDataMetaDataList {
	return s.MetaDataList
}

func (s *GetSkillMetaDataResponseBodyData) GetSkillPath() *string {
	return s.SkillPath
}

func (s *GetSkillMetaDataResponseBodyData) SetMetaDataList(v []*GetSkillMetaDataResponseBodyDataMetaDataList) *GetSkillMetaDataResponseBodyData {
	s.MetaDataList = v
	return s
}

func (s *GetSkillMetaDataResponseBodyData) SetSkillPath(v string) *GetSkillMetaDataResponseBodyData {
	s.SkillPath = &v
	return s
}

func (s *GetSkillMetaDataResponseBodyData) Validate() error {
	if s.MetaDataList != nil {
		for _, item := range s.MetaDataList {
			if item != nil {
				if err := item.Validate(); err != nil {
					return err
				}
			}
		}
	}
	return nil
}

type GetSkillMetaDataResponseBodyDataMetaDataList struct {
	Description *string `json:"Description,omitempty" xml:"Description,omitempty"`
	Name        *string `json:"Name,omitempty" xml:"Name,omitempty"`
}

func (s GetSkillMetaDataResponseBodyDataMetaDataList) String() string {
	return dara.Prettify(s)
}

func (s GetSkillMetaDataResponseBodyDataMetaDataList) GoString() string {
	return s.String()
}

func (s *GetSkillMetaDataResponseBodyDataMetaDataList) GetDescription() *string {
	return s.Description
}

func (s *GetSkillMetaDataResponseBodyDataMetaDataList) GetName() *string {
	return s.Name
}

func (s *GetSkillMetaDataResponseBodyDataMetaDataList) SetDescription(v string) *GetSkillMetaDataResponseBodyDataMetaDataList {
	s.Description = &v
	return s
}

func (s *GetSkillMetaDataResponseBodyDataMetaDataList) SetName(v string) *GetSkillMetaDataResponseBodyDataMetaDataList {
	s.Name = &v
	return s
}

func (s *GetSkillMetaDataResponseBodyDataMetaDataList) Validate() error {
	return dara.Validate(s)
}
