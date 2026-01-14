// This file is auto-generated, don't edit it. Thanks.
package client

import (
	"github.com/alibabacloud-go/tea/dara"
)

type iGetVolumeResponseBody interface {
	dara.Model
	String() string
	GoString() string
	SetCode(v string) *GetVolumeResponseBody
	GetCode() *string
	SetData(v *GetVolumeResponseBodyData) *GetVolumeResponseBody
	GetData() *GetVolumeResponseBodyData
	SetHttpStatusCode(v int32) *GetVolumeResponseBody
	GetHttpStatusCode() *int32
	SetMessage(v string) *GetVolumeResponseBody
	GetMessage() *string
	SetRequestId(v string) *GetVolumeResponseBody
	GetRequestId() *string
	SetSuccess(v bool) *GetVolumeResponseBody
	GetSuccess() *bool
}

type GetVolumeResponseBody struct {
	Code           *string                    `json:"Code,omitempty" xml:"Code,omitempty"`
	Data           *GetVolumeResponseBodyData `json:"Data,omitempty" xml:"Data,omitempty" type:"Struct"`
	HttpStatusCode *int32                     `json:"HttpStatusCode,omitempty" xml:"HttpStatusCode,omitempty"`
	Message        *string                    `json:"Message,omitempty" xml:"Message,omitempty"`
	RequestId      *string                    `json:"RequestId,omitempty" xml:"RequestId,omitempty"`
	Success        *bool                      `json:"Success,omitempty" xml:"Success,omitempty"`
}

func (s GetVolumeResponseBody) String() string {
	return dara.Prettify(s)
}

func (s GetVolumeResponseBody) GoString() string {
	return s.String()
}

func (s *GetVolumeResponseBody) GetCode() *string {
	return s.Code
}

func (s *GetVolumeResponseBody) GetData() *GetVolumeResponseBodyData {
	return s.Data
}

func (s *GetVolumeResponseBody) GetHttpStatusCode() *int32 {
	return s.HttpStatusCode
}

func (s *GetVolumeResponseBody) GetMessage() *string {
	return s.Message
}

func (s *GetVolumeResponseBody) GetRequestId() *string {
	return s.RequestId
}

func (s *GetVolumeResponseBody) GetSuccess() *bool {
	return s.Success
}

func (s *GetVolumeResponseBody) SetCode(v string) *GetVolumeResponseBody {
	s.Code = &v
	return s
}

func (s *GetVolumeResponseBody) SetData(v *GetVolumeResponseBodyData) *GetVolumeResponseBody {
	s.Data = v
	return s
}

func (s *GetVolumeResponseBody) SetHttpStatusCode(v int32) *GetVolumeResponseBody {
	s.HttpStatusCode = &v
	return s
}

func (s *GetVolumeResponseBody) SetMessage(v string) *GetVolumeResponseBody {
	s.Message = &v
	return s
}

func (s *GetVolumeResponseBody) SetRequestId(v string) *GetVolumeResponseBody {
	s.RequestId = &v
	return s
}

func (s *GetVolumeResponseBody) SetSuccess(v bool) *GetVolumeResponseBody {
	s.Success = &v
	return s
}

func (s *GetVolumeResponseBody) Validate() error {
	if s.Data != nil {
		if err := s.Data.Validate(); err != nil {
			return err
		}
	}
	return nil
}

type GetVolumeResponseBodyData struct {
	BelongingImageId *string `json:"BelongingImageId,omitempty" xml:"BelongingImageId,omitempty"`
	CreateTime       *string `json:"CreateTime,omitempty" xml:"CreateTime,omitempty"`
	Status           *string `json:"Status,omitempty" xml:"Status,omitempty"`
	VolumeId         *string `json:"VolumeId,omitempty" xml:"VolumeId,omitempty"`
	VolumeName       *string `json:"VolumeName,omitempty" xml:"VolumeName,omitempty"`
}

func (s GetVolumeResponseBodyData) String() string {
	return dara.Prettify(s)
}

func (s GetVolumeResponseBodyData) GoString() string {
	return s.String()
}

func (s *GetVolumeResponseBodyData) GetBelongingImageId() *string {
	return s.BelongingImageId
}

func (s *GetVolumeResponseBodyData) GetCreateTime() *string {
	return s.CreateTime
}

func (s *GetVolumeResponseBodyData) GetStatus() *string {
	return s.Status
}

func (s *GetVolumeResponseBodyData) GetVolumeId() *string {
	return s.VolumeId
}

func (s *GetVolumeResponseBodyData) GetVolumeName() *string {
	return s.VolumeName
}

func (s *GetVolumeResponseBodyData) SetBelongingImageId(v string) *GetVolumeResponseBodyData {
	s.BelongingImageId = &v
	return s
}

func (s *GetVolumeResponseBodyData) SetCreateTime(v string) *GetVolumeResponseBodyData {
	s.CreateTime = &v
	return s
}

func (s *GetVolumeResponseBodyData) SetStatus(v string) *GetVolumeResponseBodyData {
	s.Status = &v
	return s
}

func (s *GetVolumeResponseBodyData) SetVolumeId(v string) *GetVolumeResponseBodyData {
	s.VolumeId = &v
	return s
}

func (s *GetVolumeResponseBodyData) SetVolumeName(v string) *GetVolumeResponseBodyData {
	s.VolumeName = &v
	return s
}

func (s *GetVolumeResponseBodyData) Validate() error {
	return dara.Validate(s)
}
