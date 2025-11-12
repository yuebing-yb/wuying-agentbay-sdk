// This file is auto-generated, don't edit it. Thanks.
package client

import (
	"github.com/alibabacloud-go/tea/dara"
)

type iGetCdpLinkResponseBody interface {
	dara.Model
	String() string
	GoString() string
	SetCode(v string) *GetCdpLinkResponseBody
	GetCode() *string
	SetData(v *GetCdpLinkResponseBodyData) *GetCdpLinkResponseBody
	GetData() *GetCdpLinkResponseBodyData
	SetHttpStatusCode(v int32) *GetCdpLinkResponseBody
	GetHttpStatusCode() *int32
	SetMessage(v string) *GetCdpLinkResponseBody
	GetMessage() *string
	SetRequestId(v string) *GetCdpLinkResponseBody
	GetRequestId() *string
	SetSuccess(v bool) *GetCdpLinkResponseBody
	GetSuccess() *bool
}

type GetCdpLinkResponseBody struct {
	Code           *string                     `json:"Code,omitempty" xml:"Code,omitempty"`
	Data           *GetCdpLinkResponseBodyData `json:"Data,omitempty" xml:"Data,omitempty" type:"Struct"`
	HttpStatusCode *int32                      `json:"HttpStatusCode,omitempty" xml:"HttpStatusCode,omitempty"`
	Message        *string                     `json:"Message,omitempty" xml:"Message,omitempty"`
	RequestId      *string                     `json:"RequestId,omitempty" xml:"RequestId,omitempty"`
	Success        *bool                       `json:"Success,omitempty" xml:"Success,omitempty"`
}

func (s GetCdpLinkResponseBody) String() string {
	return dara.Prettify(s)
}

func (s GetCdpLinkResponseBody) GoString() string {
	return s.String()
}

func (s *GetCdpLinkResponseBody) GetCode() *string {
	return s.Code
}

func (s *GetCdpLinkResponseBody) GetData() *GetCdpLinkResponseBodyData {
	return s.Data
}

func (s *GetCdpLinkResponseBody) GetHttpStatusCode() *int32 {
	return s.HttpStatusCode
}

func (s *GetCdpLinkResponseBody) GetMessage() *string {
	return s.Message
}

func (s *GetCdpLinkResponseBody) GetRequestId() *string {
	return s.RequestId
}

func (s *GetCdpLinkResponseBody) GetSuccess() *bool {
	return s.Success
}

func (s *GetCdpLinkResponseBody) SetCode(v string) *GetCdpLinkResponseBody {
	s.Code = &v
	return s
}

func (s *GetCdpLinkResponseBody) SetData(v *GetCdpLinkResponseBodyData) *GetCdpLinkResponseBody {
	s.Data = v
	return s
}

func (s *GetCdpLinkResponseBody) SetHttpStatusCode(v int32) *GetCdpLinkResponseBody {
	s.HttpStatusCode = &v
	return s
}

func (s *GetCdpLinkResponseBody) SetMessage(v string) *GetCdpLinkResponseBody {
	s.Message = &v
	return s
}

func (s *GetCdpLinkResponseBody) SetRequestId(v string) *GetCdpLinkResponseBody {
	s.RequestId = &v
	return s
}

func (s *GetCdpLinkResponseBody) SetSuccess(v bool) *GetCdpLinkResponseBody {
	s.Success = &v
	return s
}

func (s *GetCdpLinkResponseBody) Validate() error {
	if s.Data != nil {
		if err := s.Data.Validate(); err != nil {
			return err
		}
	}
	return nil
}

type GetCdpLinkResponseBodyData struct {
	Url *string `json:"Url,omitempty" xml:"Url,omitempty"`
}

func (s GetCdpLinkResponseBodyData) String() string {
	return dara.Prettify(s)
}

func (s GetCdpLinkResponseBodyData) GoString() string {
	return s.String()
}

func (s *GetCdpLinkResponseBodyData) GetUrl() *string {
	return s.Url
}

func (s *GetCdpLinkResponseBodyData) SetUrl(v string) *GetCdpLinkResponseBodyData {
	s.Url = &v
	return s
}

func (s *GetCdpLinkResponseBodyData) Validate() error {
	return dara.Validate(s)
}
