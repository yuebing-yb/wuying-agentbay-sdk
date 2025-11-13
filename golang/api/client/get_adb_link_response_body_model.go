// This file is auto-generated, don't edit it. Thanks.
package client

import (
	"github.com/alibabacloud-go/tea/dara"
)

type iGetAdbLinkResponseBody interface {
	dara.Model
	String() string
	GoString() string
	SetCode(v string) *GetAdbLinkResponseBody
	GetCode() *string
	SetData(v *GetAdbLinkResponseBodyData) *GetAdbLinkResponseBody
	GetData() *GetAdbLinkResponseBodyData
	SetHttpStatusCode(v int32) *GetAdbLinkResponseBody
	GetHttpStatusCode() *int32
	SetMessage(v string) *GetAdbLinkResponseBody
	GetMessage() *string
	SetRequestId(v string) *GetAdbLinkResponseBody
	GetRequestId() *string
	SetSuccess(v bool) *GetAdbLinkResponseBody
	GetSuccess() *bool
}

type GetAdbLinkResponseBody struct {
	Code           *string                     `json:"Code,omitempty" xml:"Code,omitempty"`
	Data           *GetAdbLinkResponseBodyData `json:"Data,omitempty" xml:"Data,omitempty" type:"Struct"`
	HttpStatusCode *int32                      `json:"HttpStatusCode,omitempty" xml:"HttpStatusCode,omitempty"`
	Message        *string                     `json:"Message,omitempty" xml:"Message,omitempty"`
	RequestId      *string                     `json:"RequestId,omitempty" xml:"RequestId,omitempty"`
	Success        *bool                       `json:"Success,omitempty" xml:"Success,omitempty"`
}

func (s GetAdbLinkResponseBody) String() string {
	return dara.Prettify(s)
}

func (s GetAdbLinkResponseBody) GoString() string {
	return s.String()
}

func (s *GetAdbLinkResponseBody) GetCode() *string {
	return s.Code
}

func (s *GetAdbLinkResponseBody) GetData() *GetAdbLinkResponseBodyData {
	return s.Data
}

func (s *GetAdbLinkResponseBody) GetHttpStatusCode() *int32 {
	return s.HttpStatusCode
}

func (s *GetAdbLinkResponseBody) GetMessage() *string {
	return s.Message
}

func (s *GetAdbLinkResponseBody) GetRequestId() *string {
	return s.RequestId
}

func (s *GetAdbLinkResponseBody) GetSuccess() *bool {
	return s.Success
}

func (s *GetAdbLinkResponseBody) SetCode(v string) *GetAdbLinkResponseBody {
	s.Code = &v
	return s
}

func (s *GetAdbLinkResponseBody) SetData(v *GetAdbLinkResponseBodyData) *GetAdbLinkResponseBody {
	s.Data = v
	return s
}

func (s *GetAdbLinkResponseBody) SetHttpStatusCode(v int32) *GetAdbLinkResponseBody {
	s.HttpStatusCode = &v
	return s
}

func (s *GetAdbLinkResponseBody) SetMessage(v string) *GetAdbLinkResponseBody {
	s.Message = &v
	return s
}

func (s *GetAdbLinkResponseBody) SetRequestId(v string) *GetAdbLinkResponseBody {
	s.RequestId = &v
	return s
}

func (s *GetAdbLinkResponseBody) SetSuccess(v bool) *GetAdbLinkResponseBody {
	s.Success = &v
	return s
}

func (s *GetAdbLinkResponseBody) Validate() error {
	if s.Data != nil {
		if err := s.Data.Validate(); err != nil {
			return err
		}
	}
	return nil
}

type GetAdbLinkResponseBodyData struct {
	Url *string `json:"Url,omitempty" xml:"Url,omitempty"`
}

func (s GetAdbLinkResponseBodyData) String() string {
	return dara.Prettify(s)
}

func (s GetAdbLinkResponseBodyData) GoString() string {
	return s.String()
}

func (s *GetAdbLinkResponseBodyData) GetUrl() *string {
	return s.Url
}

func (s *GetAdbLinkResponseBodyData) SetUrl(v string) *GetAdbLinkResponseBodyData {
	s.Url = &v
	return s
}

func (s *GetAdbLinkResponseBodyData) Validate() error {
	return dara.Validate(s)
}
