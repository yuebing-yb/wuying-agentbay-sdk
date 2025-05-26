// This file is auto-generated, don't edit it. Thanks.
package client

import (
	"github.com/alibabacloud-go/tea/dara"
)

type iListMcpToolsRequest interface {
	dara.Model
	String() string
	GoString() string
	SetAuthorization(v string) *ListMcpToolsRequest
	GetAuthorization() *string
}

type ListMcpToolsRequest struct {
	Authorization *string `json:"Authorization,omitempty" xml:"Authorization,omitempty"`
}

func (s ListMcpToolsRequest) String() string {
	return dara.Prettify(s)
}

func (s ListMcpToolsRequest) GoString() string {
	return s.String()
}

func (s *ListMcpToolsRequest) GetAuthorization() *string {
	return s.Authorization
}

func (s *ListMcpToolsRequest) SetAuthorization(v string) *ListMcpToolsRequest {
	s.Authorization = &v
	return s
}

func (s *ListMcpToolsRequest) Validate() error {
	return dara.Validate(s)
}
