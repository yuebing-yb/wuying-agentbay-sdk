// This file is auto-generated, don't edit it. Thanks.
package client

import (
	"github.com/alibabacloud-go/tea/dara"
)

type iDescribeSessionContextsResponseBody interface {
	dara.Model
	String() string
	GoString() string
	SetCode(v string) *DescribeSessionContextsResponseBody
	GetCode() *string
	SetData(v []*DescribeSessionContextsResponseBodyData) *DescribeSessionContextsResponseBody
	GetData() []*DescribeSessionContextsResponseBodyData
	SetHttpStatusCode(v int32) *DescribeSessionContextsResponseBody
	GetHttpStatusCode() *int32
	SetMessage(v string) *DescribeSessionContextsResponseBody
	GetMessage() *string
	SetRequestId(v string) *DescribeSessionContextsResponseBody
	GetRequestId() *string
	SetSuccess(v bool) *DescribeSessionContextsResponseBody
	GetSuccess() *bool
}

type DescribeSessionContextsResponseBody struct {
	Code           *string                                    `json:"Code,omitempty" xml:"Code,omitempty"`
	Data           []*DescribeSessionContextsResponseBodyData `json:"Data,omitempty" xml:"Data,omitempty" type:"Repeated"`
	HttpStatusCode *int32                                     `json:"HttpStatusCode,omitempty" xml:"HttpStatusCode,omitempty"`
	Message        *string                                    `json:"Message,omitempty" xml:"Message,omitempty"`
	RequestId      *string                                    `json:"RequestId,omitempty" xml:"RequestId,omitempty"`
	Success        *bool                                      `json:"Success,omitempty" xml:"Success,omitempty"`
}

func (s DescribeSessionContextsResponseBody) String() string {
	return dara.Prettify(s)
}

func (s DescribeSessionContextsResponseBody) GoString() string {
	return s.String()
}

func (s *DescribeSessionContextsResponseBody) GetCode() *string {
	return s.Code
}

func (s *DescribeSessionContextsResponseBody) GetData() []*DescribeSessionContextsResponseBodyData {
	return s.Data
}

func (s *DescribeSessionContextsResponseBody) GetHttpStatusCode() *int32 {
	return s.HttpStatusCode
}

func (s *DescribeSessionContextsResponseBody) GetMessage() *string {
	return s.Message
}

func (s *DescribeSessionContextsResponseBody) GetRequestId() *string {
	return s.RequestId
}

func (s *DescribeSessionContextsResponseBody) GetSuccess() *bool {
	return s.Success
}

func (s *DescribeSessionContextsResponseBody) SetCode(v string) *DescribeSessionContextsResponseBody {
	s.Code = &v
	return s
}

func (s *DescribeSessionContextsResponseBody) SetData(v []*DescribeSessionContextsResponseBodyData) *DescribeSessionContextsResponseBody {
	s.Data = v
	return s
}

func (s *DescribeSessionContextsResponseBody) SetHttpStatusCode(v int32) *DescribeSessionContextsResponseBody {
	s.HttpStatusCode = &v
	return s
}

func (s *DescribeSessionContextsResponseBody) SetMessage(v string) *DescribeSessionContextsResponseBody {
	s.Message = &v
	return s
}

func (s *DescribeSessionContextsResponseBody) SetRequestId(v string) *DescribeSessionContextsResponseBody {
	s.RequestId = &v
	return s
}

func (s *DescribeSessionContextsResponseBody) SetSuccess(v bool) *DescribeSessionContextsResponseBody {
	s.Success = &v
	return s
}

func (s *DescribeSessionContextsResponseBody) Validate() error {
	if s.Data != nil {
		for _, item := range s.Data {
			if item != nil {
				if err := item.Validate(); err != nil {
					return err
				}
			}
		}
	}
	return nil
}

type DescribeSessionContextsResponseBodyData struct {
	BindTime    *string `json:"BindTime,omitempty" xml:"BindTime,omitempty"`
	ContextId   *string `json:"ContextId,omitempty" xml:"ContextId,omitempty"`
	ContextName *string `json:"ContextName,omitempty" xml:"ContextName,omitempty"`
	Path        *string `json:"Path,omitempty" xml:"Path,omitempty"`
	Policy      *string `json:"Policy,omitempty" xml:"Policy,omitempty"`
}

func (s DescribeSessionContextsResponseBodyData) String() string {
	return dara.Prettify(s)
}

func (s DescribeSessionContextsResponseBodyData) GoString() string {
	return s.String()
}

func (s *DescribeSessionContextsResponseBodyData) GetBindTime() *string {
	return s.BindTime
}

func (s *DescribeSessionContextsResponseBodyData) GetContextId() *string {
	return s.ContextId
}

func (s *DescribeSessionContextsResponseBodyData) GetContextName() *string {
	return s.ContextName
}

func (s *DescribeSessionContextsResponseBodyData) GetPath() *string {
	return s.Path
}

func (s *DescribeSessionContextsResponseBodyData) GetPolicy() *string {
	return s.Policy
}

func (s *DescribeSessionContextsResponseBodyData) SetBindTime(v string) *DescribeSessionContextsResponseBodyData {
	s.BindTime = &v
	return s
}

func (s *DescribeSessionContextsResponseBodyData) SetContextId(v string) *DescribeSessionContextsResponseBodyData {
	s.ContextId = &v
	return s
}

func (s *DescribeSessionContextsResponseBodyData) SetContextName(v string) *DescribeSessionContextsResponseBodyData {
	s.ContextName = &v
	return s
}

func (s *DescribeSessionContextsResponseBodyData) SetPath(v string) *DescribeSessionContextsResponseBodyData {
	s.Path = &v
	return s
}

func (s *DescribeSessionContextsResponseBodyData) SetPolicy(v string) *DescribeSessionContextsResponseBodyData {
	s.Policy = &v
	return s
}

func (s *DescribeSessionContextsResponseBodyData) Validate() error {
	return dara.Validate(s)
}
