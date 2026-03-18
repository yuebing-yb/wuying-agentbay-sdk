// This file is auto-generated, don't edit it. Thanks.
package client

import (
	"github.com/alibabacloud-go/tea/dara"
)

type iGetSkillMetaDataRequest interface {
	dara.Model
	String() string
	GoString() string
	SetAuthorization(v string) *GetSkillMetaDataRequest
	GetAuthorization() *string
	SetImageId(v string) *GetSkillMetaDataRequest
	GetImageId() *string
	SetSkillGroupIds(v []*string) *GetSkillMetaDataRequest
	GetSkillGroupIds() []*string
}

type GetSkillMetaDataRequest struct {
	Authorization *string   `json:"Authorization,omitempty" xml:"Authorization,omitempty"`
	ImageId       *string   `json:"ImageId,omitempty" xml:"ImageId,omitempty"`
	SkillGroupIds []*string `json:"SkillGroupIds,omitempty" xml:"SkillGroupIds,omitempty" type:"Repeated"`
}

func (s GetSkillMetaDataRequest) String() string {
	return dara.Prettify(s)
}

func (s GetSkillMetaDataRequest) GoString() string {
	return s.String()
}

func (s *GetSkillMetaDataRequest) GetAuthorization() *string {
	return s.Authorization
}

func (s *GetSkillMetaDataRequest) GetImageId() *string {
	return s.ImageId
}

func (s *GetSkillMetaDataRequest) GetSkillGroupIds() []*string {
	return s.SkillGroupIds
}

func (s *GetSkillMetaDataRequest) SetAuthorization(v string) *GetSkillMetaDataRequest {
	s.Authorization = &v
	return s
}

func (s *GetSkillMetaDataRequest) SetImageId(v string) *GetSkillMetaDataRequest {
	s.ImageId = &v
	return s
}

func (s *GetSkillMetaDataRequest) SetSkillGroupIds(v []*string) *GetSkillMetaDataRequest {
	s.SkillGroupIds = v
	return s
}

func (s *GetSkillMetaDataRequest) Validate() error {
	return dara.Validate(s)
}
