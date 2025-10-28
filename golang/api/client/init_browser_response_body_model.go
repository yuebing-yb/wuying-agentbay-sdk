// This file is auto-generated, don't edit it. Thanks.
package client

import (
	"github.com/alibabacloud-go/tea/dara"
)

type iInitBrowserResponseBody interface {
	dara.Model
	String() string
	GoString() string
	SetCode(v string) *InitBrowserResponseBody
	GetCode() *string
	SetData(v *InitBrowserResponseBodyData) *InitBrowserResponseBody
	GetData() *InitBrowserResponseBodyData
	SetHttpStatusCode(v int32) *InitBrowserResponseBody
	GetHttpStatusCode() *int32
	SetMessage(v string) *InitBrowserResponseBody
	GetMessage() *string
	SetRequestId(v string) *InitBrowserResponseBody
	GetRequestId() *string
	SetSuccess(v bool) *InitBrowserResponseBody
	GetSuccess() *bool
}

type InitBrowserResponseBodyData struct {
	Port *int32 `json:"Port,omitempty" xml:"Port,omitempty"`
}

type InitBrowserResponseBody struct {
	Code           *string                      `json:"Code,omitempty" xml:"Code,omitempty"`
	Data           *InitBrowserResponseBodyData `json:"Data,omitempty" xml:"Data,omitempty"`
	HttpStatusCode *int32                       `json:"HttpStatusCode,omitempty" xml:"HttpStatusCode,omitempty"`
	Message        *string                      `json:"Message,omitempty" xml:"Message,omitempty"`
	RequestId      *string                      `json:"RequestId,omitempty" xml:"RequestId,omitempty"`
	Success        *bool                        `json:"Success,omitempty" xml:"Success,omitempty"`
}

func (s InitBrowserResponseBody) String() string {
	return dara.Prettify(s)
}

func (s InitBrowserResponseBody) GoString() string {
	return s.String()
}

func (s *InitBrowserResponseBody) GetCode() *string {
	return s.Code
}

func (s *InitBrowserResponseBody) GetData() *InitBrowserResponseBodyData {
	return s.Data
}

func (s *InitBrowserResponseBody) GetHttpStatusCode() *int32 {
	return s.HttpStatusCode
}

func (s *InitBrowserResponseBody) GetMessage() *string {
	return s.Message
}

func (s *InitBrowserResponseBody) GetRequestId() *string {
	return s.RequestId
}

func (s *InitBrowserResponseBody) GetSuccess() *bool {
	return s.Success
}

func (s *InitBrowserResponseBody) SetCode(v string) *InitBrowserResponseBody {
	s.Code = &v
	return s
}

func (s *InitBrowserResponseBody) SetData(v *InitBrowserResponseBodyData) *InitBrowserResponseBody {
	s.Data = v
	return s
}

func (s *InitBrowserResponseBody) SetHttpStatusCode(v int32) *InitBrowserResponseBody {
	s.HttpStatusCode = &v
	return s
}

func (s *InitBrowserResponseBody) SetMessage(v string) *InitBrowserResponseBody {
	s.Message = &v
	return s
}

func (s *InitBrowserResponseBody) SetRequestId(v string) *InitBrowserResponseBody {
	s.RequestId = &v
	return s
}

func (s *InitBrowserResponseBody) SetSuccess(v bool) *InitBrowserResponseBody {
	s.Success = &v
	return s
}

func (s *InitBrowserResponseBody) Validate() error {
	return dara.Validate(s)
}

