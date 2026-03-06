// This file is auto-generated, don't edit it. Thanks.
package client

import (
	"github.com/alibabacloud-go/tea/dara"
)

type iBindContextsShrinkRequest interface {
	dara.Model
	String() string
	GoString() string
	SetAuthorization(v string) *BindContextsShrinkRequest
	GetAuthorization() *string
	SetPersistenceDataListShrink(v string) *BindContextsShrinkRequest
	GetPersistenceDataListShrink() *string
	SetSessionId(v string) *BindContextsShrinkRequest
	GetSessionId() *string
}

type BindContextsShrinkRequest struct {
	Authorization             *string `json:"Authorization,omitempty" xml:"Authorization,omitempty"`
	PersistenceDataListShrink *string `json:"PersistenceDataList,omitempty" xml:"PersistenceDataList,omitempty"`
	SessionId                 *string `json:"SessionId,omitempty" xml:"SessionId,omitempty"`
}

func (s BindContextsShrinkRequest) String() string {
	return dara.Prettify(s)
}

func (s BindContextsShrinkRequest) GoString() string {
	return s.String()
}

func (s *BindContextsShrinkRequest) GetAuthorization() *string {
	return s.Authorization
}

func (s *BindContextsShrinkRequest) GetPersistenceDataListShrink() *string {
	return s.PersistenceDataListShrink
}

func (s *BindContextsShrinkRequest) GetSessionId() *string {
	return s.SessionId
}

func (s *BindContextsShrinkRequest) SetAuthorization(v string) *BindContextsShrinkRequest {
	s.Authorization = &v
	return s
}

func (s *BindContextsShrinkRequest) SetPersistenceDataListShrink(v string) *BindContextsShrinkRequest {
	s.PersistenceDataListShrink = &v
	return s
}

func (s *BindContextsShrinkRequest) SetSessionId(v string) *BindContextsShrinkRequest {
	s.SessionId = &v
	return s
}

func (s *BindContextsShrinkRequest) Validate() error {
	return dara.Validate(s)
}
