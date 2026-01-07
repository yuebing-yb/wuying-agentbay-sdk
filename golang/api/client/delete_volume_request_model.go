// This file is auto-generated, don't edit it. Thanks.
package client

import (
	"github.com/alibabacloud-go/tea/dara"
)

type iDeleteVolumeRequest interface {
	dara.Model
	String() string
	GoString() string
	SetAuthorization(v string) *DeleteVolumeRequest
	GetAuthorization() *string
	SetVolumeId(v string) *DeleteVolumeRequest
	GetVolumeId() *string
}

type DeleteVolumeRequest struct {
	Authorization *string `json:"Authorization,omitempty" xml:"Authorization,omitempty"`
	// This parameter is required.
	VolumeId *string `json:"VolumeId,omitempty" xml:"VolumeId,omitempty"`
}

func (s DeleteVolumeRequest) String() string {
	return dara.Prettify(s)
}

func (s DeleteVolumeRequest) GoString() string {
	return s.String()
}

func (s *DeleteVolumeRequest) GetAuthorization() *string {
	return s.Authorization
}

func (s *DeleteVolumeRequest) GetVolumeId() *string {
	return s.VolumeId
}

func (s *DeleteVolumeRequest) SetAuthorization(v string) *DeleteVolumeRequest {
	s.Authorization = &v
	return s
}

func (s *DeleteVolumeRequest) SetVolumeId(v string) *DeleteVolumeRequest {
	s.VolumeId = &v
	return s
}

func (s *DeleteVolumeRequest) Validate() error {
	return dara.Validate(s)
}
