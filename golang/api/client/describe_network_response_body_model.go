// This file is auto-generated, don't edit it. Thanks.
package client

import (
	"github.com/alibabacloud-go/tea/dara"
)

type iDescribeNetworkResponseBody interface {
	dara.Model
	String() string
	GoString() string
	SetCode(v string) *DescribeNetworkResponseBody
	GetCode() *string
	SetData(v *DescribeNetworkResponseBodyData) *DescribeNetworkResponseBody
	GetData() *DescribeNetworkResponseBodyData
	SetHttpStatusCode(v int32) *DescribeNetworkResponseBody
	GetHttpStatusCode() *int32
	SetMessage(v string) *DescribeNetworkResponseBody
	GetMessage() *string
	SetRequestId(v string) *DescribeNetworkResponseBody
	GetRequestId() *string
	SetSuccess(v bool) *DescribeNetworkResponseBody
	GetSuccess() *bool
}

type DescribeNetworkResponseBody struct {
	Code           *string                          `json:"Code,omitempty" xml:"Code,omitempty"`
	Data           *DescribeNetworkResponseBodyData `json:"Data,omitempty" xml:"Data,omitempty" type:"Struct"`
	HttpStatusCode *int32                           `json:"HttpStatusCode,omitempty" xml:"HttpStatusCode,omitempty"`
	Message        *string                          `json:"Message,omitempty" xml:"Message,omitempty"`
	RequestId      *string                          `json:"RequestId,omitempty" xml:"RequestId,omitempty"`
	Success        *bool                            `json:"Success,omitempty" xml:"Success,omitempty"`
}

func (s DescribeNetworkResponseBody) String() string {
	return dara.Prettify(s)
}

func (s DescribeNetworkResponseBody) GoString() string {
	return s.String()
}

func (s *DescribeNetworkResponseBody) GetCode() *string {
	return s.Code
}

func (s *DescribeNetworkResponseBody) GetData() *DescribeNetworkResponseBodyData {
	return s.Data
}

func (s *DescribeNetworkResponseBody) GetHttpStatusCode() *int32 {
	return s.HttpStatusCode
}

func (s *DescribeNetworkResponseBody) GetMessage() *string {
	return s.Message
}

func (s *DescribeNetworkResponseBody) GetRequestId() *string {
	return s.RequestId
}

func (s *DescribeNetworkResponseBody) GetSuccess() *bool {
	return s.Success
}

func (s *DescribeNetworkResponseBody) SetCode(v string) *DescribeNetworkResponseBody {
	s.Code = &v
	return s
}

func (s *DescribeNetworkResponseBody) SetData(v *DescribeNetworkResponseBodyData) *DescribeNetworkResponseBody {
	s.Data = v
	return s
}

func (s *DescribeNetworkResponseBody) SetHttpStatusCode(v int32) *DescribeNetworkResponseBody {
	s.HttpStatusCode = &v
	return s
}

func (s *DescribeNetworkResponseBody) SetMessage(v string) *DescribeNetworkResponseBody {
	s.Message = &v
	return s
}

func (s *DescribeNetworkResponseBody) SetRequestId(v string) *DescribeNetworkResponseBody {
	s.RequestId = &v
	return s
}

func (s *DescribeNetworkResponseBody) SetSuccess(v bool) *DescribeNetworkResponseBody {
	s.Success = &v
	return s
}

func (s *DescribeNetworkResponseBody) Validate() error {
	if s.Data != nil {
		if err := s.Data.Validate(); err != nil {
			return err
		}
	}
	return nil
}

type DescribeNetworkResponseBodyData struct {
	Online *bool `json:"Online,omitempty" xml:"Online,omitempty"`
}

func (s DescribeNetworkResponseBodyData) String() string {
	return dara.Prettify(s)
}

func (s DescribeNetworkResponseBodyData) GoString() string {
	return s.String()
}

func (s *DescribeNetworkResponseBodyData) GetOnline() *bool {
	return s.Online
}

func (s *DescribeNetworkResponseBodyData) SetOnline(v bool) *DescribeNetworkResponseBodyData {
	s.Online = &v
	return s
}

func (s *DescribeNetworkResponseBodyData) Validate() error {
	return dara.Validate(s)
}
