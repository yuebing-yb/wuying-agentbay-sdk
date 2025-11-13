// This file is auto-generated, don't edit it. Thanks.
package client

import (
	"github.com/alibabacloud-go/tea/dara"
)

type iGetCdpLinkRequest interface {
	dara.Model
	String() string
	GoString() string
	SetAuthorization(v string) *GetCdpLinkRequest
	GetAuthorization() *string
	SetSessionId(v string) *GetCdpLinkRequest
	GetSessionId() *string
}

type GetCdpLinkRequest struct {
	Authorization *string `json:"Authorization,omitempty" xml:"Authorization,omitempty"`
	SessionId     *string `json:"SessionId,omitempty" xml:"SessionId,omitempty"`
}

func (s GetCdpLinkRequest) String() string {
	return dara.Prettify(s)
}

func (s GetCdpLinkRequest) GoString() string {
	return s.String()
}

func (s *GetCdpLinkRequest) GetAuthorization() *string {
	return s.Authorization
}

func (s *GetCdpLinkRequest) GetSessionId() *string {
	return s.SessionId
}

func (s *GetCdpLinkRequest) SetAuthorization(v string) *GetCdpLinkRequest {
	s.Authorization = &v
	return s
}

func (s *GetCdpLinkRequest) SetSessionId(v string) *GetCdpLinkRequest {
	s.SessionId = &v
	return s
}

func (s *GetCdpLinkRequest) Validate() error {
	return dara.Validate(s)
}
