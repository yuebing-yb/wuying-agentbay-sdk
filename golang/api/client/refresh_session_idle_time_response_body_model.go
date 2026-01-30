// This file is auto-generated, don't edit it. Thanks.
package client

import (
	"github.com/alibabacloud-go/tea/dara"
)

type iRefreshSessionIdleTimeResponseBody interface {
	dara.Model
	String() string
	GoString() string
	SetCode(v string) *RefreshSessionIdleTimeResponseBody
	GetCode() *string
	SetData(v interface{}) *RefreshSessionIdleTimeResponseBody
	GetData() interface{}
	SetHttpStatusCode(v int32) *RefreshSessionIdleTimeResponseBody
	GetHttpStatusCode() *int32
	SetMessage(v string) *RefreshSessionIdleTimeResponseBody
	GetMessage() *string
	SetRequestId(v string) *RefreshSessionIdleTimeResponseBody
	GetRequestId() *string
	SetSuccess(v bool) *RefreshSessionIdleTimeResponseBody
	GetSuccess() *bool
}

type RefreshSessionIdleTimeResponseBody struct {
	Code           *string     `json:"Code,omitempty" xml:"Code,omitempty"`
	Data           interface{} `json:"Data,omitempty" xml:"Data,omitempty"`
	HttpStatusCode *int32      `json:"HttpStatusCode,omitempty" xml:"HttpStatusCode,omitempty"`
	Message        *string     `json:"Message,omitempty" xml:"Message,omitempty"`
	RequestId      *string     `json:"RequestId,omitempty" xml:"RequestId,omitempty"`
	Success        *bool       `json:"Success,omitempty" xml:"Success,omitempty"`
}

func (s RefreshSessionIdleTimeResponseBody) String() string {
	return dara.Prettify(s)
}

func (s RefreshSessionIdleTimeResponseBody) GoString() string {
	return s.String()
}

func (s *RefreshSessionIdleTimeResponseBody) GetCode() *string {
	return s.Code
}

func (s *RefreshSessionIdleTimeResponseBody) GetData() interface{} {
	return s.Data
}

func (s *RefreshSessionIdleTimeResponseBody) GetHttpStatusCode() *int32 {
	return s.HttpStatusCode
}

func (s *RefreshSessionIdleTimeResponseBody) GetMessage() *string {
	return s.Message
}

func (s *RefreshSessionIdleTimeResponseBody) GetRequestId() *string {
	return s.RequestId
}

func (s *RefreshSessionIdleTimeResponseBody) GetSuccess() *bool {
	return s.Success
}

func (s *RefreshSessionIdleTimeResponseBody) SetCode(v string) *RefreshSessionIdleTimeResponseBody {
	s.Code = &v
	return s
}

func (s *RefreshSessionIdleTimeResponseBody) SetData(v interface{}) *RefreshSessionIdleTimeResponseBody {
	s.Data = v
	return s
}

func (s *RefreshSessionIdleTimeResponseBody) SetHttpStatusCode(v int32) *RefreshSessionIdleTimeResponseBody {
	s.HttpStatusCode = &v
	return s
}

func (s *RefreshSessionIdleTimeResponseBody) SetMessage(v string) *RefreshSessionIdleTimeResponseBody {
	s.Message = &v
	return s
}

func (s *RefreshSessionIdleTimeResponseBody) SetRequestId(v string) *RefreshSessionIdleTimeResponseBody {
	s.RequestId = &v
	return s
}

func (s *RefreshSessionIdleTimeResponseBody) SetSuccess(v bool) *RefreshSessionIdleTimeResponseBody {
	s.Success = &v
	return s
}

func (s *RefreshSessionIdleTimeResponseBody) Validate() error {
	return dara.Validate(s)
}

