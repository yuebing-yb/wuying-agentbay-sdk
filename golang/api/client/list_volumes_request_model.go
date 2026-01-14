// This file is auto-generated, don't edit it. Thanks.
package client

import (
	"github.com/alibabacloud-go/tea/dara"
)

type iListVolumesRequest interface {
	dara.Model
	String() string
	GoString() string
	SetAuthorization(v string) *ListVolumesRequest
	GetAuthorization() *string
	SetImageId(v string) *ListVolumesRequest
	GetImageId() *string
	SetMaxResults(v int32) *ListVolumesRequest
	GetMaxResults() *int32
	SetNextToken(v string) *ListVolumesRequest
	GetNextToken() *string
	SetVolumeIds(v []*string) *ListVolumesRequest
	GetVolumeIds() []*string
	SetVolumeName(v string) *ListVolumesRequest
	GetVolumeName() *string
}

type ListVolumesRequest struct {
	Authorization *string   `json:"Authorization,omitempty" xml:"Authorization,omitempty"`
	ImageId       *string   `json:"ImageId,omitempty" xml:"ImageId,omitempty"`
	MaxResults    *int32    `json:"MaxResults,omitempty" xml:"MaxResults,omitempty"`
	NextToken     *string   `json:"NextToken,omitempty" xml:"NextToken,omitempty"`
	VolumeIds     []*string `json:"VolumeIds,omitempty" xml:"VolumeIds,omitempty" type:"Repeated"`
	VolumeName    *string   `json:"VolumeName,omitempty" xml:"VolumeName,omitempty"`
}

func (s ListVolumesRequest) String() string {
	return dara.Prettify(s)
}

func (s ListVolumesRequest) GoString() string {
	return s.String()
}

func (s *ListVolumesRequest) GetAuthorization() *string {
	return s.Authorization
}

func (s *ListVolumesRequest) GetImageId() *string {
	return s.ImageId
}

func (s *ListVolumesRequest) GetMaxResults() *int32 {
	return s.MaxResults
}

func (s *ListVolumesRequest) GetNextToken() *string {
	return s.NextToken
}

func (s *ListVolumesRequest) GetVolumeIds() []*string {
	return s.VolumeIds
}

func (s *ListVolumesRequest) GetVolumeName() *string {
	return s.VolumeName
}

func (s *ListVolumesRequest) SetAuthorization(v string) *ListVolumesRequest {
	s.Authorization = &v
	return s
}

func (s *ListVolumesRequest) SetImageId(v string) *ListVolumesRequest {
	s.ImageId = &v
	return s
}

func (s *ListVolumesRequest) SetMaxResults(v int32) *ListVolumesRequest {
	s.MaxResults = &v
	return s
}

func (s *ListVolumesRequest) SetNextToken(v string) *ListVolumesRequest {
	s.NextToken = &v
	return s
}

func (s *ListVolumesRequest) SetVolumeIds(v []*string) *ListVolumesRequest {
	s.VolumeIds = v
	return s
}

func (s *ListVolumesRequest) SetVolumeName(v string) *ListVolumesRequest {
	s.VolumeName = &v
	return s
}

func (s *ListVolumesRequest) Validate() error {
	return dara.Validate(s)
}
