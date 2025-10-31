// This file is auto-generated, don't edit it. Thanks.
package client

import (
	"github.com/alibabacloud-go/tea/dara"
)

type iClearContextRequest interface {
	dara.Model
	String() string
	GoString() string
	SetAuthorization(v string) *ClearContextRequest
	GetAuthorization() *string
	SetId(v string) *ClearContextRequest
	GetId() *string
}

type ClearContextRequest struct {
	Authorization *string `json:"Authorization,omitempty" xml:"Authorization,omitempty"`
	Id            *string `json:"Id,omitempty" xml:"Id,omitempty"`
}

func (s ClearContextRequest) String() string {
	return dara.Prettify(s)
}

func (s ClearContextRequest) GoString() string {
	return s.String()
}

func (s *ClearContextRequest) GetAuthorization() *string {
	return s.Authorization
}

func (s *ClearContextRequest) GetId() *string {
	return s.Id
}

func (s *ClearContextRequest) SetAuthorization(v string) *ClearContextRequest {
	s.Authorization = &v
	return s
}

func (s *ClearContextRequest) SetId(v string) *ClearContextRequest {
	s.Id = &v
	return s
}

func (s *ClearContextRequest) Validate() error {
	return dara.Validate(s)
}
