// This file is auto-generated, don't edit it. Thanks.
package client

import (
	"github.com/alibabacloud-go/tea/dara"
)

type iGetSessionDetailRequest interface {
	dara.Model
	String() string
	GoString() string
	SetAuthorization(v string) *GetSessionDetailRequest
	GetAuthorization() *string
	SetSessionId(v string) *GetSessionDetailRequest
	GetSessionId() *string
}

type GetSessionDetailRequest struct {
	Authorization *string `json:"Authorization,omitempty" xml:"Authorization,omitempty"`
	SessionId     *string `json:"SessionId,omitempty" xml:"SessionId,omitempty"`
}

func (s GetSessionDetailRequest) String() string {
	return dara.Prettify(s)
}

func (s GetSessionDetailRequest) GoString() string {
	return s.String()
}

func (s *GetSessionDetailRequest) GetAuthorization() *string {
	return s.Authorization
}

func (s *GetSessionDetailRequest) GetSessionId() *string {
	return s.SessionId
}

func (s *GetSessionDetailRequest) SetAuthorization(v string) *GetSessionDetailRequest {
	s.Authorization = &v
	return s
}

func (s *GetSessionDetailRequest) SetSessionId(v string) *GetSessionDetailRequest {
	s.SessionId = &v
	return s
}

func (s *GetSessionDetailRequest) Validate() error {
	return dara.Validate(s)
}


