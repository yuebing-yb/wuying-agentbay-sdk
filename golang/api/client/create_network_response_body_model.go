// This file is auto-generated, don't edit it. Thanks.
package client

import (
	"github.com/alibabacloud-go/tea/dara"
)

type iCreateNetworkResponseBody interface {
	dara.Model
	String() string
	GoString() string
	SetCode(v string) *CreateNetworkResponseBody
	GetCode() *string
	SetData(v *CreateNetworkResponseBodyData) *CreateNetworkResponseBody
	GetData() *CreateNetworkResponseBodyData
	SetHttpStatusCode(v int32) *CreateNetworkResponseBody
	GetHttpStatusCode() *int32
	SetMessage(v string) *CreateNetworkResponseBody
	GetMessage() *string
	SetRequestId(v string) *CreateNetworkResponseBody
	GetRequestId() *string
	SetSuccess(v bool) *CreateNetworkResponseBody
	GetSuccess() *bool
}

type CreateNetworkResponseBody struct {
	Code           *string                        `json:"Code,omitempty" xml:"Code,omitempty"`
	Data           *CreateNetworkResponseBodyData `json:"Data,omitempty" xml:"Data,omitempty" type:"Struct"`
	HttpStatusCode *int32                         `json:"HttpStatusCode,omitempty" xml:"HttpStatusCode,omitempty"`
	Message        *string                        `json:"Message,omitempty" xml:"Message,omitempty"`
	RequestId      *string                        `json:"RequestId,omitempty" xml:"RequestId,omitempty"`
	Success        *bool                          `json:"Success,omitempty" xml:"Success,omitempty"`
}

func (s CreateNetworkResponseBody) String() string {
	return dara.Prettify(s)
}

func (s CreateNetworkResponseBody) GoString() string {
	return s.String()
}

func (s *CreateNetworkResponseBody) GetCode() *string {
	return s.Code
}

func (s *CreateNetworkResponseBody) GetData() *CreateNetworkResponseBodyData {
	return s.Data
}

func (s *CreateNetworkResponseBody) GetHttpStatusCode() *int32 {
	return s.HttpStatusCode
}

func (s *CreateNetworkResponseBody) GetMessage() *string {
	return s.Message
}

func (s *CreateNetworkResponseBody) GetRequestId() *string {
	return s.RequestId
}

func (s *CreateNetworkResponseBody) GetSuccess() *bool {
	return s.Success
}

func (s *CreateNetworkResponseBody) SetCode(v string) *CreateNetworkResponseBody {
	s.Code = &v
	return s
}

func (s *CreateNetworkResponseBody) SetData(v *CreateNetworkResponseBodyData) *CreateNetworkResponseBody {
	s.Data = v
	return s
}

func (s *CreateNetworkResponseBody) SetHttpStatusCode(v int32) *CreateNetworkResponseBody {
	s.HttpStatusCode = &v
	return s
}

func (s *CreateNetworkResponseBody) SetMessage(v string) *CreateNetworkResponseBody {
	s.Message = &v
	return s
}

func (s *CreateNetworkResponseBody) SetRequestId(v string) *CreateNetworkResponseBody {
	s.RequestId = &v
	return s
}

func (s *CreateNetworkResponseBody) SetSuccess(v bool) *CreateNetworkResponseBody {
	s.Success = &v
	return s
}

func (s *CreateNetworkResponseBody) Validate() error {
	if s.Data != nil {
		if err := s.Data.Validate(); err != nil {
			return err
		}
	}
	return nil
}

type CreateNetworkResponseBodyData struct {
	NetworkId    *string `json:"NetworkId,omitempty" xml:"NetworkId,omitempty"`
	NetworkToken *string `json:"NetworkToken,omitempty" xml:"NetworkToken,omitempty"`
}

func (s CreateNetworkResponseBodyData) String() string {
	return dara.Prettify(s)
}

func (s CreateNetworkResponseBodyData) GoString() string {
	return s.String()
}

func (s *CreateNetworkResponseBodyData) GetNetworkId() *string {
	return s.NetworkId
}

func (s *CreateNetworkResponseBodyData) GetNetworkToken() *string {
	return s.NetworkToken
}

func (s *CreateNetworkResponseBodyData) SetNetworkId(v string) *CreateNetworkResponseBodyData {
	s.NetworkId = &v
	return s
}

func (s *CreateNetworkResponseBodyData) SetNetworkToken(v string) *CreateNetworkResponseBodyData {
	s.NetworkToken = &v
	return s
}

func (s *CreateNetworkResponseBodyData) Validate() error {
	return dara.Validate(s)
}
