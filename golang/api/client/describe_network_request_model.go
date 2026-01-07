// This file is auto-generated, don't edit it. Thanks.
package client

import (
	"github.com/alibabacloud-go/tea/dara"
)

type iDescribeNetworkRequest interface {
	dara.Model
	String() string
	GoString() string
	SetAuthorization(v string) *DescribeNetworkRequest
	GetAuthorization() *string
	SetNetworkId(v string) *DescribeNetworkRequest
	GetNetworkId() *string
}

type DescribeNetworkRequest struct {
	Authorization *string `json:"Authorization,omitempty" xml:"Authorization,omitempty"`
	NetworkId     *string `json:"NetworkId,omitempty" xml:"NetworkId,omitempty"`
}

func (s DescribeNetworkRequest) String() string {
	return dara.Prettify(s)
}

func (s DescribeNetworkRequest) GoString() string {
	return s.String()
}

func (s *DescribeNetworkRequest) GetAuthorization() *string {
	return s.Authorization
}

func (s *DescribeNetworkRequest) GetNetworkId() *string {
	return s.NetworkId
}

func (s *DescribeNetworkRequest) SetAuthorization(v string) *DescribeNetworkRequest {
	s.Authorization = &v
	return s
}

func (s *DescribeNetworkRequest) SetNetworkId(v string) *DescribeNetworkRequest {
	s.NetworkId = &v
	return s
}

func (s *DescribeNetworkRequest) Validate() error {
	return dara.Validate(s)
}
