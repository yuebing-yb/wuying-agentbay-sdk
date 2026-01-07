// This file is auto-generated, don't edit it. Thanks.
package client

import (
	"github.com/alibabacloud-go/tea/dara"
)

type iListVolumesResponseBody interface {
	dara.Model
	String() string
	GoString() string
	SetCode(v string) *ListVolumesResponseBody
	GetCode() *string
	SetData(v []*ListVolumesResponseBodyData) *ListVolumesResponseBody
	GetData() []*ListVolumesResponseBodyData
	SetHttpStatusCode(v int32) *ListVolumesResponseBody
	GetHttpStatusCode() *int32
	SetMaxResults(v int32) *ListVolumesResponseBody
	GetMaxResults() *int32
	SetMessage(v string) *ListVolumesResponseBody
	GetMessage() *string
	SetNextToken(v string) *ListVolumesResponseBody
	GetNextToken() *string
	SetRequestId(v string) *ListVolumesResponseBody
	GetRequestId() *string
	SetSuccess(v bool) *ListVolumesResponseBody
	GetSuccess() *bool
}

type ListVolumesResponseBody struct {
	Code           *string                        `json:"Code,omitempty" xml:"Code,omitempty"`
	Data           []*ListVolumesResponseBodyData `json:"Data,omitempty" xml:"Data,omitempty" type:"Repeated"`
	HttpStatusCode *int32                         `json:"HttpStatusCode,omitempty" xml:"HttpStatusCode,omitempty"`
	MaxResults     *int32                         `json:"MaxResults,omitempty" xml:"MaxResults,omitempty"`
	Message        *string                        `json:"Message,omitempty" xml:"Message,omitempty"`
	NextToken      *string                        `json:"NextToken,omitempty" xml:"NextToken,omitempty"`
	RequestId      *string                        `json:"RequestId,omitempty" xml:"RequestId,omitempty"`
	Success        *bool                          `json:"Success,omitempty" xml:"Success,omitempty"`
}

func (s ListVolumesResponseBody) String() string {
	return dara.Prettify(s)
}

func (s ListVolumesResponseBody) GoString() string {
	return s.String()
}

func (s *ListVolumesResponseBody) GetCode() *string {
	return s.Code
}

func (s *ListVolumesResponseBody) GetData() []*ListVolumesResponseBodyData {
	return s.Data
}

func (s *ListVolumesResponseBody) GetHttpStatusCode() *int32 {
	return s.HttpStatusCode
}

func (s *ListVolumesResponseBody) GetMaxResults() *int32 {
	return s.MaxResults
}

func (s *ListVolumesResponseBody) GetMessage() *string {
	return s.Message
}

func (s *ListVolumesResponseBody) GetNextToken() *string {
	return s.NextToken
}

func (s *ListVolumesResponseBody) GetRequestId() *string {
	return s.RequestId
}

func (s *ListVolumesResponseBody) GetSuccess() *bool {
	return s.Success
}

func (s *ListVolumesResponseBody) SetCode(v string) *ListVolumesResponseBody {
	s.Code = &v
	return s
}

func (s *ListVolumesResponseBody) SetData(v []*ListVolumesResponseBodyData) *ListVolumesResponseBody {
	s.Data = v
	return s
}

func (s *ListVolumesResponseBody) SetHttpStatusCode(v int32) *ListVolumesResponseBody {
	s.HttpStatusCode = &v
	return s
}

func (s *ListVolumesResponseBody) SetMaxResults(v int32) *ListVolumesResponseBody {
	s.MaxResults = &v
	return s
}

func (s *ListVolumesResponseBody) SetMessage(v string) *ListVolumesResponseBody {
	s.Message = &v
	return s
}

func (s *ListVolumesResponseBody) SetNextToken(v string) *ListVolumesResponseBody {
	s.NextToken = &v
	return s
}

func (s *ListVolumesResponseBody) SetRequestId(v string) *ListVolumesResponseBody {
	s.RequestId = &v
	return s
}

func (s *ListVolumesResponseBody) SetSuccess(v bool) *ListVolumesResponseBody {
	s.Success = &v
	return s
}

func (s *ListVolumesResponseBody) Validate() error {
	if s.Data != nil {
		for _, item := range s.Data {
			if item != nil {
				if err := item.Validate(); err != nil {
					return err
				}
			}
		}
	}
	return nil
}

type ListVolumesResponseBodyData struct {
	BelongingImageId *string `json:"BelongingImageId,omitempty" xml:"BelongingImageId,omitempty"`
	CreateTime       *string `json:"CreateTime,omitempty" xml:"CreateTime,omitempty"`
	Status           *string `json:"Status,omitempty" xml:"Status,omitempty"`
	VolumeId         *string `json:"VolumeId,omitempty" xml:"VolumeId,omitempty"`
	VolumeName       *string `json:"VolumeName,omitempty" xml:"VolumeName,omitempty"`
}

func (s ListVolumesResponseBodyData) String() string {
	return dara.Prettify(s)
}

func (s ListVolumesResponseBodyData) GoString() string {
	return s.String()
}

func (s *ListVolumesResponseBodyData) GetBelongingImageId() *string {
	return s.BelongingImageId
}

func (s *ListVolumesResponseBodyData) GetCreateTime() *string {
	return s.CreateTime
}

func (s *ListVolumesResponseBodyData) GetStatus() *string {
	return s.Status
}

func (s *ListVolumesResponseBodyData) GetVolumeId() *string {
	return s.VolumeId
}

func (s *ListVolumesResponseBodyData) GetVolumeName() *string {
	return s.VolumeName
}

func (s *ListVolumesResponseBodyData) SetBelongingImageId(v string) *ListVolumesResponseBodyData {
	s.BelongingImageId = &v
	return s
}

func (s *ListVolumesResponseBodyData) SetCreateTime(v string) *ListVolumesResponseBodyData {
	s.CreateTime = &v
	return s
}

func (s *ListVolumesResponseBodyData) SetStatus(v string) *ListVolumesResponseBodyData {
	s.Status = &v
	return s
}

func (s *ListVolumesResponseBodyData) SetVolumeId(v string) *ListVolumesResponseBodyData {
	s.VolumeId = &v
	return s
}

func (s *ListVolumesResponseBodyData) SetVolumeName(v string) *ListVolumesResponseBodyData {
	s.VolumeName = &v
	return s
}

func (s *ListVolumesResponseBodyData) Validate() error {
	return dara.Validate(s)
}
