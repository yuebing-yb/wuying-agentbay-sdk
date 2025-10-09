// This file is auto-generated, don't edit it. Thanks.
package client

import (
	"github.com/alibabacloud-go/tea/dara"
)

type iGetSessionResponseBody interface {
	dara.Model
	String() string
	GoString() string
	SetCode(v string) *GetSessionResponseBody
	GetCode() *string
	SetData(v *GetSessionResponseBodyData) *GetSessionResponseBody
	GetData() *GetSessionResponseBodyData
	SetHttpStatusCode(v int32) *GetSessionResponseBody
	GetHttpStatusCode() *int32
	SetMessage(v string) *GetSessionResponseBody
	GetMessage() *string
	SetRequestId(v string) *GetSessionResponseBody
	GetRequestId() *string
	SetSuccess(v bool) *GetSessionResponseBody
	GetSuccess() *bool
}

type GetSessionResponseBody struct {
	Code           *string                     `json:"Code,omitempty" xml:"Code,omitempty"`
	Data           *GetSessionResponseBodyData `json:"Data,omitempty" xml:"Data,omitempty" type:"Struct"`
	HttpStatusCode *int32                      `json:"HttpStatusCode,omitempty" xml:"HttpStatusCode,omitempty"`
	Message        *string                     `json:"Message,omitempty" xml:"Message,omitempty"`
	RequestId      *string                     `json:"RequestId,omitempty" xml:"RequestId,omitempty"`
	Success        *bool                       `json:"Success,omitempty" xml:"Success,omitempty"`
}

func (s GetSessionResponseBody) String() string {
	return dara.Prettify(s)
}

func (s GetSessionResponseBody) GoString() string {
	return s.String()
}

func (s *GetSessionResponseBody) GetCode() *string {
	return s.Code
}

func (s *GetSessionResponseBody) GetData() *GetSessionResponseBodyData {
	return s.Data
}

func (s *GetSessionResponseBody) GetHttpStatusCode() *int32 {
	return s.HttpStatusCode
}

func (s *GetSessionResponseBody) GetMessage() *string {
	return s.Message
}

func (s *GetSessionResponseBody) GetRequestId() *string {
	return s.RequestId
}

func (s *GetSessionResponseBody) GetSuccess() *bool {
	return s.Success
}

func (s *GetSessionResponseBody) SetCode(v string) *GetSessionResponseBody {
	s.Code = &v
	return s
}

func (s *GetSessionResponseBody) SetData(v *GetSessionResponseBodyData) *GetSessionResponseBody {
	s.Data = v
	return s
}

func (s *GetSessionResponseBody) SetHttpStatusCode(v int32) *GetSessionResponseBody {
	s.HttpStatusCode = &v
	return s
}

func (s *GetSessionResponseBody) SetMessage(v string) *GetSessionResponseBody {
	s.Message = &v
	return s
}

func (s *GetSessionResponseBody) SetRequestId(v string) *GetSessionResponseBody {
	s.RequestId = &v
	return s
}

func (s *GetSessionResponseBody) SetSuccess(v bool) *GetSessionResponseBody {
	s.Success = &v
	return s
}

func (s *GetSessionResponseBody) Validate() error {
	return dara.Validate(s)
}

type GetSessionResponseBodyData struct {
	AppInstanceId *string `json:"AppInstanceId,omitempty" xml:"AppInstanceId,omitempty"`
	ResourceId    *string `json:"ResourceId,omitempty" xml:"ResourceId,omitempty"`
	SessionId     *string `json:"SessionId,omitempty" xml:"SessionId,omitempty"`
	Success       *bool   `json:"Success,omitempty" xml:"Success,omitempty"`
}

func (s GetSessionResponseBodyData) String() string {
	return dara.Prettify(s)
}

func (s GetSessionResponseBodyData) GoString() string {
	return s.String()
}

func (s *GetSessionResponseBodyData) GetAppInstanceId() *string {
	return s.AppInstanceId
}

func (s *GetSessionResponseBodyData) GetResourceId() *string {
	return s.ResourceId
}

func (s *GetSessionResponseBodyData) GetSessionId() *string {
	return s.SessionId
}

func (s *GetSessionResponseBodyData) GetSuccess() *bool {
	return s.Success
}

func (s *GetSessionResponseBodyData) SetAppInstanceId(v string) *GetSessionResponseBodyData {
	s.AppInstanceId = &v
	return s
}

func (s *GetSessionResponseBodyData) SetResourceId(v string) *GetSessionResponseBodyData {
	s.ResourceId = &v
	return s
}

func (s *GetSessionResponseBodyData) SetSessionId(v string) *GetSessionResponseBodyData {
	s.SessionId = &v
	return s
}

func (s *GetSessionResponseBodyData) SetSuccess(v bool) *GetSessionResponseBodyData {
	s.Success = &v
	return s
}

func (s *GetSessionResponseBodyData) Validate() error {
	return dara.Validate(s)
}
