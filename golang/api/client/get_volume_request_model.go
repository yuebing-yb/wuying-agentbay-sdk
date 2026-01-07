// This file is auto-generated, don't edit it. Thanks.
package client

import (
	"github.com/alibabacloud-go/tea/dara"
)

type iGetVolumeRequest interface {
	dara.Model
	String() string
	GoString() string
	SetAllowCreate(v bool) *GetVolumeRequest
	GetAllowCreate() *bool
	SetAuthorization(v string) *GetVolumeRequest
	GetAuthorization() *string
	SetImageId(v string) *GetVolumeRequest
	GetImageId() *string
	SetVolumeName(v string) *GetVolumeRequest
	GetVolumeName() *string
}

type GetVolumeRequest struct {
	AllowCreate   *bool   `json:"AllowCreate,omitempty" xml:"AllowCreate,omitempty"`
	Authorization *string `json:"Authorization,omitempty" xml:"Authorization,omitempty"`
	ImageId       *string `json:"ImageId,omitempty" xml:"ImageId,omitempty"`
	VolumeName    *string `json:"VolumeName,omitempty" xml:"VolumeName,omitempty"`
}

func (s GetVolumeRequest) String() string {
	return dara.Prettify(s)
}

func (s GetVolumeRequest) GoString() string {
	return s.String()
}

func (s *GetVolumeRequest) GetAllowCreate() *bool {
	return s.AllowCreate
}

func (s *GetVolumeRequest) GetAuthorization() *string {
	return s.Authorization
}

func (s *GetVolumeRequest) GetImageId() *string {
	return s.ImageId
}

func (s *GetVolumeRequest) GetVolumeName() *string {
	return s.VolumeName
}

func (s *GetVolumeRequest) SetAllowCreate(v bool) *GetVolumeRequest {
	s.AllowCreate = &v
	return s
}

func (s *GetVolumeRequest) SetAuthorization(v string) *GetVolumeRequest {
	s.Authorization = &v
	return s
}

func (s *GetVolumeRequest) SetImageId(v string) *GetVolumeRequest {
	s.ImageId = &v
	return s
}

func (s *GetVolumeRequest) SetVolumeName(v string) *GetVolumeRequest {
	s.VolumeName = &v
	return s
}

func (s *GetVolumeRequest) Validate() error {
	return dara.Validate(s)
}
