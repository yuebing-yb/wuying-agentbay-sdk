// This file is auto-generated, don't edit it. Thanks.
package client

import (
	"github.com/alibabacloud-go/tea/dara"
)

type iListSkillMetaDataResponseBody interface {
	dara.Model
	String() string
	GoString() string
	SetCode(v string) *ListSkillMetaDataResponseBody
	GetCode() *string
	SetData(v []*ListSkillMetaDataResponseBodyData) *ListSkillMetaDataResponseBody
	GetData() []*ListSkillMetaDataResponseBodyData
	SetHttpStatusCode(v int32) *ListSkillMetaDataResponseBody
	GetHttpStatusCode() *int32
	SetMessage(v string) *ListSkillMetaDataResponseBody
	GetMessage() *string
	SetRequestId(v string) *ListSkillMetaDataResponseBody
	GetRequestId() *string
	SetSuccess(v bool) *ListSkillMetaDataResponseBody
	GetSuccess() *bool
	SetTotalCount(v int32) *ListSkillMetaDataResponseBody
	GetTotalCount() *int32
}

type ListSkillMetaDataResponseBody struct {
	Code           *string                          `json:"Code,omitempty" xml:"Code,omitempty"`
	Data           []*ListSkillMetaDataResponseBodyData `json:"Data,omitempty" xml:"Data,omitempty" type:"Repeated"`
	HttpStatusCode *int32                           `json:"HttpStatusCode,omitempty" xml:"HttpStatusCode,omitempty"`
	Message        *string                          `json:"Message,omitempty" xml:"Message,omitempty"`
	RequestId      *string                          `json:"RequestId,omitempty" xml:"RequestId,omitempty"`
	Success        *bool                            `json:"Success,omitempty" xml:"Success,omitempty"`
	TotalCount     *int32                           `json:"TotalCount,omitempty" xml:"TotalCount,omitempty"`
}

func (s ListSkillMetaDataResponseBody) String() string {
	return dara.Prettify(s)
}

func (s ListSkillMetaDataResponseBody) GoString() string {
	return s.String()
}

func (s *ListSkillMetaDataResponseBody) GetCode() *string {
	return s.Code
}

func (s *ListSkillMetaDataResponseBody) GetData() []*ListSkillMetaDataResponseBodyData {
	return s.Data
}

func (s *ListSkillMetaDataResponseBody) GetHttpStatusCode() *int32 {
	return s.HttpStatusCode
}

func (s *ListSkillMetaDataResponseBody) GetMessage() *string {
	return s.Message
}

func (s *ListSkillMetaDataResponseBody) GetRequestId() *string {
	return s.RequestId
}

func (s *ListSkillMetaDataResponseBody) GetSuccess() *bool {
	return s.Success
}

func (s *ListSkillMetaDataResponseBody) GetTotalCount() *int32 {
	return s.TotalCount
}

func (s *ListSkillMetaDataResponseBody) SetCode(v string) *ListSkillMetaDataResponseBody {
	s.Code = &v
	return s
}

func (s *ListSkillMetaDataResponseBody) SetData(v []*ListSkillMetaDataResponseBodyData) *ListSkillMetaDataResponseBody {
	s.Data = v
	return s
}

func (s *ListSkillMetaDataResponseBody) SetHttpStatusCode(v int32) *ListSkillMetaDataResponseBody {
	s.HttpStatusCode = &v
	return s
}

func (s *ListSkillMetaDataResponseBody) SetMessage(v string) *ListSkillMetaDataResponseBody {
	s.Message = &v
	return s
}

func (s *ListSkillMetaDataResponseBody) SetRequestId(v string) *ListSkillMetaDataResponseBody {
	s.RequestId = &v
	return s
}

func (s *ListSkillMetaDataResponseBody) SetSuccess(v bool) *ListSkillMetaDataResponseBody {
	s.Success = &v
	return s
}

func (s *ListSkillMetaDataResponseBody) SetTotalCount(v int32) *ListSkillMetaDataResponseBody {
	s.TotalCount = &v
	return s
}

func (s *ListSkillMetaDataResponseBody) Validate() error {
	if s.Data != nil {
		for _, v := range s.Data {
			if v != nil {
				if err := v.Validate(); err != nil {
					return err
				}
			}
		}
	}
	return nil
}

type ListSkillMetaDataResponseBodyData struct {
	Description *string `json:"Description,omitempty" xml:"Description,omitempty"`
	Name        *string `json:"Name,omitempty" xml:"Name,omitempty"`
}

func (s ListSkillMetaDataResponseBodyData) String() string {
	return dara.Prettify(s)
}

func (s ListSkillMetaDataResponseBodyData) GoString() string {
	return s.String()
}

func (s *ListSkillMetaDataResponseBodyData) GetDescription() *string {
	return s.Description
}

func (s *ListSkillMetaDataResponseBodyData) GetName() *string {
	return s.Name
}

func (s *ListSkillMetaDataResponseBodyData) SetDescription(v string) *ListSkillMetaDataResponseBodyData {
	s.Description = &v
	return s
}

func (s *ListSkillMetaDataResponseBodyData) SetName(v string) *ListSkillMetaDataResponseBodyData {
	s.Name = &v
	return s
}

func (s *ListSkillMetaDataResponseBodyData) Validate() error {
	return dara.Validate(s)
}

