// This file is auto-generated, don't edit it. Thanks.
package client

import (
	"github.com/alibabacloud-go/tea/dara"
)

type iGetSessionDetailResponseBody interface {
	dara.Model
	String() string
	GoString() string
	SetCode(v string) *GetSessionDetailResponseBody
	GetCode() *string
	SetData(v *GetSessionDetailResponseBodyData) *GetSessionDetailResponseBody
	GetData() *GetSessionDetailResponseBodyData
	SetHttpStatusCode(v int32) *GetSessionDetailResponseBody
	GetHttpStatusCode() *int32
	SetMessage(v string) *GetSessionDetailResponseBody
	GetMessage() *string
	SetRequestId(v string) *GetSessionDetailResponseBody
	GetRequestId() *string
	SetSuccess(v bool) *GetSessionDetailResponseBody
	GetSuccess() *bool
}

type GetSessionDetailResponseBody struct {
	Code           *string                           `json:"Code,omitempty" xml:"Code,omitempty"`
	Data           *GetSessionDetailResponseBodyData `json:"Data,omitempty" xml:"Data,omitempty" type:"Struct"`
	HttpStatusCode *int32                            `json:"HttpStatusCode,omitempty" xml:"HttpStatusCode,omitempty"`
	Message        *string                           `json:"Message,omitempty" xml:"Message,omitempty"`
	RequestId      *string                           `json:"RequestId,omitempty" xml:"RequestId,omitempty"`
	Success        *bool                             `json:"Success,omitempty" xml:"Success,omitempty"`
}

func (s GetSessionDetailResponseBody) String() string {
	return dara.Prettify(s)
}

func (s GetSessionDetailResponseBody) GoString() string {
	return s.String()
}

func (s *GetSessionDetailResponseBody) GetCode() *string {
	return s.Code
}

func (s *GetSessionDetailResponseBody) GetData() *GetSessionDetailResponseBodyData {
	return s.Data
}

func (s *GetSessionDetailResponseBody) GetHttpStatusCode() *int32 {
	return s.HttpStatusCode
}

func (s *GetSessionDetailResponseBody) GetMessage() *string {
	return s.Message
}

func (s *GetSessionDetailResponseBody) GetRequestId() *string {
	return s.RequestId
}

func (s *GetSessionDetailResponseBody) GetSuccess() *bool {
	return s.Success
}

func (s *GetSessionDetailResponseBody) SetCode(v string) *GetSessionDetailResponseBody {
	s.Code = &v
	return s
}

func (s *GetSessionDetailResponseBody) SetData(v *GetSessionDetailResponseBodyData) *GetSessionDetailResponseBody {
	s.Data = v
	return s
}

func (s *GetSessionDetailResponseBody) SetHttpStatusCode(v int32) *GetSessionDetailResponseBody {
	s.HttpStatusCode = &v
	return s
}

func (s *GetSessionDetailResponseBody) SetMessage(v string) *GetSessionDetailResponseBody {
	s.Message = &v
	return s
}

func (s *GetSessionDetailResponseBody) SetRequestId(v string) *GetSessionDetailResponseBody {
	s.RequestId = &v
	return s
}

func (s *GetSessionDetailResponseBody) SetSuccess(v bool) *GetSessionDetailResponseBody {
	s.Success = &v
	return s
}

func (s *GetSessionDetailResponseBody) Validate() error {
	if s.Data != nil {
		if err := s.Data.Validate(); err != nil {
			return err
		}
	}
	return nil
}

type GetSessionDetailResponseBodyData struct {
	Aliuid             *string `json:"Aliuid,omitempty" xml:"Aliuid,omitempty"`
	ApikeyId           *string `json:"ApikeyId,omitempty" xml:"ApikeyId,omitempty"`
	AppInstanceGroupId *string `json:"AppInstanceGroupId,omitempty" xml:"AppInstanceGroupId,omitempty"`
	AppInstanceId      *string `json:"AppInstanceId,omitempty" xml:"AppInstanceId,omitempty"`
	AppUserId          *string `json:"AppUserId,omitempty" xml:"AppUserId,omitempty"`
	BizType            *int32  `json:"BizType,omitempty" xml:"BizType,omitempty"`
	EndReason          *string `json:"EndReason,omitempty" xml:"EndReason,omitempty"`
	Id                 *int64  `json:"Id,omitempty" xml:"Id,omitempty"`
	ImageId            *string `json:"ImageId,omitempty" xml:"ImageId,omitempty"`
	ImageType          *string `json:"ImageType,omitempty" xml:"ImageType,omitempty"`
	IsDeleted          *int32  `json:"IsDeleted,omitempty" xml:"IsDeleted,omitempty"`
	PolicyId           *string `json:"PolicyId,omitempty" xml:"PolicyId,omitempty"`
	RegionId           *string `json:"RegionId,omitempty" xml:"RegionId,omitempty"`
	ResourceConfigId   *string `json:"ResourceConfigId,omitempty" xml:"ResourceConfigId,omitempty"`
	Status             *string `json:"Status,omitempty" xml:"Status,omitempty"`
}

func (s GetSessionDetailResponseBodyData) String() string {
	return dara.Prettify(s)
}

func (s GetSessionDetailResponseBodyData) GoString() string {
	return s.String()
}

func (s *GetSessionDetailResponseBodyData) GetAliuid() *string {
	return s.Aliuid
}

func (s *GetSessionDetailResponseBodyData) GetApikeyId() *string {
	return s.ApikeyId
}

func (s *GetSessionDetailResponseBodyData) GetAppInstanceGroupId() *string {
	return s.AppInstanceGroupId
}

func (s *GetSessionDetailResponseBodyData) GetAppInstanceId() *string {
	return s.AppInstanceId
}

func (s *GetSessionDetailResponseBodyData) GetAppUserId() *string {
	return s.AppUserId
}

func (s *GetSessionDetailResponseBodyData) GetBizType() *int32 {
	return s.BizType
}

func (s *GetSessionDetailResponseBodyData) GetEndReason() *string {
	return s.EndReason
}

func (s *GetSessionDetailResponseBodyData) GetId() *int64 {
	return s.Id
}

func (s *GetSessionDetailResponseBodyData) GetImageId() *string {
	return s.ImageId
}

func (s *GetSessionDetailResponseBodyData) GetImageType() *string {
	return s.ImageType
}

func (s *GetSessionDetailResponseBodyData) GetIsDeleted() *int32 {
	return s.IsDeleted
}

func (s *GetSessionDetailResponseBodyData) GetPolicyId() *string {
	return s.PolicyId
}

func (s *GetSessionDetailResponseBodyData) GetRegionId() *string {
	return s.RegionId
}

func (s *GetSessionDetailResponseBodyData) GetResourceConfigId() *string {
	return s.ResourceConfigId
}

func (s *GetSessionDetailResponseBodyData) GetStatus() *string {
	return s.Status
}

func (s *GetSessionDetailResponseBodyData) SetAliuid(v string) *GetSessionDetailResponseBodyData {
	s.Aliuid = &v
	return s
}

func (s *GetSessionDetailResponseBodyData) SetApikeyId(v string) *GetSessionDetailResponseBodyData {
	s.ApikeyId = &v
	return s
}

func (s *GetSessionDetailResponseBodyData) SetAppInstanceGroupId(v string) *GetSessionDetailResponseBodyData {
	s.AppInstanceGroupId = &v
	return s
}

func (s *GetSessionDetailResponseBodyData) SetAppInstanceId(v string) *GetSessionDetailResponseBodyData {
	s.AppInstanceId = &v
	return s
}

func (s *GetSessionDetailResponseBodyData) SetAppUserId(v string) *GetSessionDetailResponseBodyData {
	s.AppUserId = &v
	return s
}

func (s *GetSessionDetailResponseBodyData) SetBizType(v int32) *GetSessionDetailResponseBodyData {
	s.BizType = &v
	return s
}

func (s *GetSessionDetailResponseBodyData) SetEndReason(v string) *GetSessionDetailResponseBodyData {
	s.EndReason = &v
	return s
}

func (s *GetSessionDetailResponseBodyData) SetId(v int64) *GetSessionDetailResponseBodyData {
	s.Id = &v
	return s
}

func (s *GetSessionDetailResponseBodyData) SetImageId(v string) *GetSessionDetailResponseBodyData {
	s.ImageId = &v
	return s
}

func (s *GetSessionDetailResponseBodyData) SetImageType(v string) *GetSessionDetailResponseBodyData {
	s.ImageType = &v
	return s
}

func (s *GetSessionDetailResponseBodyData) SetIsDeleted(v int32) *GetSessionDetailResponseBodyData {
	s.IsDeleted = &v
	return s
}

func (s *GetSessionDetailResponseBodyData) SetPolicyId(v string) *GetSessionDetailResponseBodyData {
	s.PolicyId = &v
	return s
}

func (s *GetSessionDetailResponseBodyData) SetRegionId(v string) *GetSessionDetailResponseBodyData {
	s.RegionId = &v
	return s
}

func (s *GetSessionDetailResponseBodyData) SetResourceConfigId(v string) *GetSessionDetailResponseBodyData {
	s.ResourceConfigId = &v
	return s
}

func (s *GetSessionDetailResponseBodyData) SetStatus(v string) *GetSessionDetailResponseBodyData {
	s.Status = &v
	return s
}

func (s *GetSessionDetailResponseBodyData) Validate() error {
	return dara.Validate(s)
}


