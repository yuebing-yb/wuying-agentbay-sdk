// This file is auto-generated, don't edit it. Thanks.
package client

import (
	"github.com/alibabacloud-go/tea/dara"
)

type iGetAdbLinkRequest interface {
	dara.Model
	String() string
	GoString() string
	SetAuthorization(v string) *GetAdbLinkRequest
	GetAuthorization() *string
	SetOption(v string) *GetAdbLinkRequest
	GetOption() *string
	SetSessionId(v string) *GetAdbLinkRequest
	GetSessionId() *string
}

type GetAdbLinkRequest struct {
	Authorization *string `json:"Authorization,omitempty" xml:"Authorization,omitempty"`
	Option        *string `json:"Option,omitempty" xml:"Option,omitempty"`
	SessionId     *string `json:"SessionId,omitempty" xml:"SessionId,omitempty"`
}

func (s GetAdbLinkRequest) String() string {
	return dara.Prettify(s)
}

func (s GetAdbLinkRequest) GoString() string {
	return s.String()
}

func (s *GetAdbLinkRequest) GetAuthorization() *string {
	return s.Authorization
}

func (s *GetAdbLinkRequest) GetOption() *string {
	return s.Option
}

func (s *GetAdbLinkRequest) GetSessionId() *string {
	return s.SessionId
}

func (s *GetAdbLinkRequest) SetAuthorization(v string) *GetAdbLinkRequest {
	s.Authorization = &v
	return s
}

func (s *GetAdbLinkRequest) SetOption(v string) *GetAdbLinkRequest {
	s.Option = &v
	return s
}

func (s *GetAdbLinkRequest) SetSessionId(v string) *GetAdbLinkRequest {
	s.SessionId = &v
	return s
}

func (s *GetAdbLinkRequest) Validate() error {
	return dara.Validate(s)
}
