// This file is auto-generated, don't edit it. Thanks.
package client

import (
	"github.com/alibabacloud-go/tea/dara"
)

type iGetSkillMetaDataShrinkRequest interface {
	dara.Model
	String() string
	GoString() string
	SetAuthorization(v string) *GetSkillMetaDataShrinkRequest
	GetAuthorization() *string
	SetImageId(v string) *GetSkillMetaDataShrinkRequest
	GetImageId() *string
	SetSkillGroupIdsShrink(v string) *GetSkillMetaDataShrinkRequest
	GetSkillGroupIdsShrink() *string
}

type GetSkillMetaDataShrinkRequest struct {
	Authorization      *string `json:"Authorization,omitempty" xml:"Authorization,omitempty"`
	ImageId            *string `json:"ImageId,omitempty" xml:"ImageId,omitempty"`
	SkillGroupIdsShrink *string `json:"SkillGroupIds,omitempty" xml:"SkillGroupIds,omitempty"`
}

func (s GetSkillMetaDataShrinkRequest) String() string {
	return dara.Prettify(s)
}

func (s GetSkillMetaDataShrinkRequest) GoString() string {
	return s.String()
}

func (s *GetSkillMetaDataShrinkRequest) GetAuthorization() *string {
	return s.Authorization
}

func (s *GetSkillMetaDataShrinkRequest) GetImageId() *string {
	return s.ImageId
}

func (s *GetSkillMetaDataShrinkRequest) GetSkillGroupIdsShrink() *string {
	return s.SkillGroupIdsShrink
}

func (s *GetSkillMetaDataShrinkRequest) SetAuthorization(v string) *GetSkillMetaDataShrinkRequest {
	s.Authorization = &v
	return s
}

func (s *GetSkillMetaDataShrinkRequest) SetImageId(v string) *GetSkillMetaDataShrinkRequest {
	s.ImageId = &v
	return s
}

func (s *GetSkillMetaDataShrinkRequest) SetSkillGroupIdsShrink(v string) *GetSkillMetaDataShrinkRequest {
	s.SkillGroupIdsShrink = &v
	return s
}

func (s *GetSkillMetaDataShrinkRequest) Validate() error {
	return dara.Validate(s)
}
