// This file is auto-generated, don't edit it. Thanks.
package client

import (
	"github.com/alibabacloud-go/tea/dara"
)

type iGetContextRequest interface {
	dara.Model
	String() string
	GoString() string
	SetAllowCreate(v bool) *GetContextRequest
	GetAllowCreate() *bool
	SetAuthorization(v string) *GetContextRequest
	GetAuthorization() *string
	SetContextId(v string) *GetContextRequest
	GetContextId() *string
	SetName(v string) *GetContextRequest
	GetName() *string
	SetLoginRegionId(v string) *GetContextRequest
	GetLoginRegionId() *string
}

type GetContextRequest struct {
	AllowCreate   *bool   `json:"AllowCreate,omitempty" xml:"AllowCreate,omitempty"`
	Authorization *string `json:"Authorization,omitempty" xml:"Authorization,omitempty"`
	ContextId     *string `json:"ContextId,omitempty" xml:"ContextId,omitempty"`
	Name          *string `json:"Name,omitempty" xml:"Name,omitempty"`
	LoginRegionId *string `json:"LoginRegionId,omitempty" xml:"LoginRegionId,omitempty"`
}

func (s GetContextRequest) String() string {
	return dara.Prettify(s)
}

func (s GetContextRequest) GoString() string {
	return s.String()
}

func (s *GetContextRequest) GetAllowCreate() *bool {
	return s.AllowCreate
}

func (s *GetContextRequest) GetAuthorization() *string {
	return s.Authorization
}

func (s *GetContextRequest) GetContextId() *string {
	return s.ContextId
}


func (s *GetContextRequest) GetName() *string {
	return s.Name
}

func (s *GetContextRequest) SetAllowCreate(v bool) *GetContextRequest {
	s.AllowCreate = &v
	return s
}

func (s *GetContextRequest) SetAuthorization(v string) *GetContextRequest {
	s.Authorization = &v
	return s
}

func (s *GetContextRequest) SetContextId(v string) *GetContextRequest {
	s.ContextId = &v
	return s
}

func (s *GetContextRequest) SetName(v string) *GetContextRequest {
	s.Name = &v
	return s
}

func (s *GetContextRequest) GetLoginRegionId() *string {
	return s.LoginRegionId
}

func (s *GetContextRequest) SetLoginRegionId(v string) *GetContextRequest {
	s.LoginRegionId = &v
	return s
}

func (s *GetContextRequest) Validate() error {
	return dara.Validate(s)
}
