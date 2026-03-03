// This file is auto-generated, don't edit it. Thanks.
package client

import (
	"github.com/alibabacloud-go/tea/dara"
)

type iRefreshSessionIdleTimeRequest interface {
	dara.Model
	String() string
	GoString() string
	SetAuthorization(v string) *RefreshSessionIdleTimeRequest
	GetAuthorization() *string
	SetSessionId(v string) *RefreshSessionIdleTimeRequest
	GetSessionId() *string
}

type RefreshSessionIdleTimeRequest struct {
	Authorization *string `json:"Authorization,omitempty" xml:"Authorization,omitempty"`
	SessionId     *string `json:"SessionId,omitempty" xml:"SessionId,omitempty"`
}

func (s RefreshSessionIdleTimeRequest) String() string {
	return dara.Prettify(s)
}

func (s RefreshSessionIdleTimeRequest) GoString() string {
	return s.String()
}

func (s *RefreshSessionIdleTimeRequest) GetAuthorization() *string {
	return s.Authorization
}

func (s *RefreshSessionIdleTimeRequest) GetSessionId() *string {
	return s.SessionId
}

func (s *RefreshSessionIdleTimeRequest) SetAuthorization(v string) *RefreshSessionIdleTimeRequest {
	s.Authorization = &v
	return s
}

func (s *RefreshSessionIdleTimeRequest) SetSessionId(v string) *RefreshSessionIdleTimeRequest {
	s.SessionId = &v
	return s
}

func (s *RefreshSessionIdleTimeRequest) Validate() error {
	return dara.Validate(s)
}

