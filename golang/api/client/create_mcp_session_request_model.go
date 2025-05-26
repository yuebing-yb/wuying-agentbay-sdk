// This file is auto-generated, don't edit it. Thanks.
package client

import (
	"github.com/alibabacloud-go/tea/dara"
)

type iCreateMcpSessionRequest interface {
	dara.Model
	String() string
	GoString() string
	SetAuthorization(v string) *CreateMcpSessionRequest
	GetAuthorization() *string
	SetExternalUserId(v string) *CreateMcpSessionRequest
	GetExternalUserId() *string
	SetSessionId(v string) *CreateMcpSessionRequest
	GetSessionId() *string
}

type CreateMcpSessionRequest struct {
	Authorization  *string `json:"Authorization,omitempty" xml:"Authorization,omitempty"`
	ExternalUserId *string `json:"ExternalUserId,omitempty" xml:"ExternalUserId,omitempty"`
	SessionId      *string `json:"SessionId,omitempty" xml:"SessionId,omitempty"`
}

func (s CreateMcpSessionRequest) String() string {
	return dara.Prettify(s)
}

func (s CreateMcpSessionRequest) GoString() string {
	return s.String()
}

func (s *CreateMcpSessionRequest) GetAuthorization() *string {
	return s.Authorization
}

func (s *CreateMcpSessionRequest) GetExternalUserId() *string {
	return s.ExternalUserId
}

func (s *CreateMcpSessionRequest) GetSessionId() *string {
	return s.SessionId
}

func (s *CreateMcpSessionRequest) SetAuthorization(v string) *CreateMcpSessionRequest {
	s.Authorization = &v
	return s
}

func (s *CreateMcpSessionRequest) SetExternalUserId(v string) *CreateMcpSessionRequest {
	s.ExternalUserId = &v
	return s
}

func (s *CreateMcpSessionRequest) SetSessionId(v string) *CreateMcpSessionRequest {
	s.SessionId = &v
	return s
}

func (s *CreateMcpSessionRequest) Validate() error {
	return dara.Validate(s)
}
