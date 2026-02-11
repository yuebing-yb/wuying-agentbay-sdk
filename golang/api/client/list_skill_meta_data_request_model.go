// This file is auto-generated, don't edit it. Thanks.
package client

import (
	"github.com/alibabacloud-go/tea/dara"
)

type iListSkillMetaDataRequest interface {
	dara.Model
	String() string
	GoString() string
	SetAuthorization(v string) *ListSkillMetaDataRequest
	GetAuthorization() *string
}

type ListSkillMetaDataRequest struct {
	Authorization *string `json:"Authorization,omitempty" xml:"Authorization,omitempty"`
}

func (s ListSkillMetaDataRequest) String() string {
	return dara.Prettify(s)
}

func (s ListSkillMetaDataRequest) GoString() string {
	return s.String()
}

func (s *ListSkillMetaDataRequest) GetAuthorization() *string {
	return s.Authorization
}

func (s *ListSkillMetaDataRequest) SetAuthorization(v string) *ListSkillMetaDataRequest {
	s.Authorization = &v
	return s
}

func (s *ListSkillMetaDataRequest) Validate() error {
	return dara.Validate(s)
}

