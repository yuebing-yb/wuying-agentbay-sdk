// This file is auto-generated, don't edit it. Thanks.
package client

import (
	"github.com/alibabacloud-go/tea/dara"
)

type iCreateNetworkRequest interface {
	dara.Model
	String() string
	GoString() string
	SetAuthorization(v string) *CreateNetworkRequest
	GetAuthorization() *string
	SetNetworkId(v string) *CreateNetworkRequest
	GetNetworkId() *string
}

type CreateNetworkRequest struct {
	Authorization *string `json:"Authorization,omitempty" xml:"Authorization,omitempty"`
	NetworkId     *string `json:"NetworkId,omitempty" xml:"NetworkId,omitempty"`
}

func (s CreateNetworkRequest) String() string {
	return dara.Prettify(s)
}

func (s CreateNetworkRequest) GoString() string {
	return s.String()
}

func (s *CreateNetworkRequest) GetAuthorization() *string {
	return s.Authorization
}

func (s *CreateNetworkRequest) GetNetworkId() *string {
	return s.NetworkId
}

func (s *CreateNetworkRequest) SetAuthorization(v string) *CreateNetworkRequest {
	s.Authorization = &v
	return s
}

func (s *CreateNetworkRequest) SetNetworkId(v string) *CreateNetworkRequest {
	s.NetworkId = &v
	return s
}

func (s *CreateNetworkRequest) Validate() error {
	return dara.Validate(s)
}
