// This file is auto-generated, don't edit it. Thanks.
package client

import (
	"github.com/alibabacloud-go/tea/dara"
)

type iDescribeSessionContextsRequest interface {
	dara.Model
	String() string
	GoString() string
	SetAuthorization(v string) *DescribeSessionContextsRequest
	GetAuthorization() *string
	SetSessionId(v string) *DescribeSessionContextsRequest
	GetSessionId() *string
}

type DescribeSessionContextsRequest struct {
	Authorization *string `json:"Authorization,omitempty" xml:"Authorization,omitempty"`
	SessionId     *string `json:"SessionId,omitempty" xml:"SessionId,omitempty"`
}

func (s DescribeSessionContextsRequest) String() string {
	return dara.Prettify(s)
}

func (s DescribeSessionContextsRequest) GoString() string {
	return s.String()
}

func (s *DescribeSessionContextsRequest) GetAuthorization() *string {
	return s.Authorization
}

func (s *DescribeSessionContextsRequest) GetSessionId() *string {
	return s.SessionId
}

func (s *DescribeSessionContextsRequest) SetAuthorization(v string) *DescribeSessionContextsRequest {
	s.Authorization = &v
	return s
}

func (s *DescribeSessionContextsRequest) SetSessionId(v string) *DescribeSessionContextsRequest {
	s.SessionId = &v
	return s
}

func (s *DescribeSessionContextsRequest) Validate() error {
	return dara.Validate(s)
}
