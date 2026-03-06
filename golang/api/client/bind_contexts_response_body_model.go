// This file is auto-generated, don't edit it. Thanks.
package client

import (
	"github.com/alibabacloud-go/tea/dara"
)

type iBindContextsResponseBody interface {
	dara.Model
	String() string
	GoString() string
	SetCode(v string) *BindContextsResponseBody
	GetCode() *string
	SetHttpStatusCode(v int32) *BindContextsResponseBody
	GetHttpStatusCode() *int32
	SetMessage(v string) *BindContextsResponseBody
	GetMessage() *string
	SetRequestId(v string) *BindContextsResponseBody
	GetRequestId() *string
	SetSuccess(v bool) *BindContextsResponseBody
	GetSuccess() *bool
}

type BindContextsResponseBody struct {
	Code           *string `json:"Code,omitempty" xml:"Code,omitempty"`
	HttpStatusCode *int32  `json:"HttpStatusCode,omitempty" xml:"HttpStatusCode,omitempty"`
	Message        *string `json:"Message,omitempty" xml:"Message,omitempty"`
	RequestId      *string `json:"RequestId,omitempty" xml:"RequestId,omitempty"`
	Success        *bool   `json:"Success,omitempty" xml:"Success,omitempty"`
}

func (s BindContextsResponseBody) String() string {
	return dara.Prettify(s)
}

func (s BindContextsResponseBody) GoString() string {
	return s.String()
}

func (s *BindContextsResponseBody) GetCode() *string {
	return s.Code
}

func (s *BindContextsResponseBody) GetHttpStatusCode() *int32 {
	return s.HttpStatusCode
}

func (s *BindContextsResponseBody) GetMessage() *string {
	return s.Message
}

func (s *BindContextsResponseBody) GetRequestId() *string {
	return s.RequestId
}

func (s *BindContextsResponseBody) GetSuccess() *bool {
	return s.Success
}

func (s *BindContextsResponseBody) SetCode(v string) *BindContextsResponseBody {
	s.Code = &v
	return s
}

func (s *BindContextsResponseBody) SetHttpStatusCode(v int32) *BindContextsResponseBody {
	s.HttpStatusCode = &v
	return s
}

func (s *BindContextsResponseBody) SetMessage(v string) *BindContextsResponseBody {
	s.Message = &v
	return s
}

func (s *BindContextsResponseBody) SetRequestId(v string) *BindContextsResponseBody {
	s.RequestId = &v
	return s
}

func (s *BindContextsResponseBody) SetSuccess(v bool) *BindContextsResponseBody {
	s.Success = &v
	return s
}

func (s *BindContextsResponseBody) Validate() error {
	return dara.Validate(s)
}
