// This file is auto-generated, don't edit it. Thanks.
package client

import (
	"github.com/alibabacloud-go/tea/dara"
)

type iClearContextResponseBody interface {
	dara.Model
	String() string
	GoString() string
	SetCode(v string) *ClearContextResponseBody
	GetCode() *string
	SetHttpStatusCode(v int32) *ClearContextResponseBody
	GetHttpStatusCode() *int32
	SetMessage(v string) *ClearContextResponseBody
	GetMessage() *string
	SetRequestId(v string) *ClearContextResponseBody
	GetRequestId() *string
	SetSuccess(v bool) *ClearContextResponseBody
	GetSuccess() *bool
}

type ClearContextResponseBody struct {
	Code           *string `json:"Code,omitempty" xml:"Code,omitempty"`
	HttpStatusCode *int32  `json:"HttpStatusCode,omitempty" xml:"HttpStatusCode,omitempty"`
	Message        *string `json:"Message,omitempty" xml:"Message,omitempty"`
	RequestId      *string `json:"RequestId,omitempty" xml:"RequestId,omitempty"`
	Success        *bool   `json:"Success,omitempty" xml:"Success,omitempty"`
}

func (s ClearContextResponseBody) String() string {
	return dara.Prettify(s)
}

func (s ClearContextResponseBody) GoString() string {
	return s.String()
}

func (s *ClearContextResponseBody) GetCode() *string {
	return s.Code
}

func (s *ClearContextResponseBody) GetHttpStatusCode() *int32 {
	return s.HttpStatusCode
}

func (s *ClearContextResponseBody) GetMessage() *string {
	return s.Message
}

func (s *ClearContextResponseBody) GetRequestId() *string {
	return s.RequestId
}

func (s *ClearContextResponseBody) GetSuccess() *bool {
	return s.Success
}

func (s *ClearContextResponseBody) SetCode(v string) *ClearContextResponseBody {
	s.Code = &v
	return s
}

func (s *ClearContextResponseBody) SetHttpStatusCode(v int32) *ClearContextResponseBody {
	s.HttpStatusCode = &v
	return s
}

func (s *ClearContextResponseBody) SetMessage(v string) *ClearContextResponseBody {
	s.Message = &v
	return s
}

func (s *ClearContextResponseBody) SetRequestId(v string) *ClearContextResponseBody {
	s.RequestId = &v
	return s
}

func (s *ClearContextResponseBody) SetSuccess(v bool) *ClearContextResponseBody {
	s.Success = &v
	return s
}

func (s *ClearContextResponseBody) Validate() error {
	return dara.Validate(s)
}
