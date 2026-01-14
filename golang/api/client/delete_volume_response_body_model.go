// This file is auto-generated, don't edit it. Thanks.
package client

import (
	"github.com/alibabacloud-go/tea/dara"
)

type iDeleteVolumeResponseBody interface {
	dara.Model
	String() string
	GoString() string
	SetCode(v string) *DeleteVolumeResponseBody
	GetCode() *string
	SetHttpStatusCode(v int32) *DeleteVolumeResponseBody
	GetHttpStatusCode() *int32
	SetMessage(v string) *DeleteVolumeResponseBody
	GetMessage() *string
	SetRequestId(v string) *DeleteVolumeResponseBody
	GetRequestId() *string
	SetSuccess(v bool) *DeleteVolumeResponseBody
	GetSuccess() *bool
}

type DeleteVolumeResponseBody struct {
	Code           *string `json:"Code,omitempty" xml:"Code,omitempty"`
	HttpStatusCode *int32  `json:"HttpStatusCode,omitempty" xml:"HttpStatusCode,omitempty"`
	Message        *string `json:"Message,omitempty" xml:"Message,omitempty"`
	RequestId      *string `json:"RequestId,omitempty" xml:"RequestId,omitempty"`
	Success        *bool   `json:"Success,omitempty" xml:"Success,omitempty"`
}

func (s DeleteVolumeResponseBody) String() string {
	return dara.Prettify(s)
}

func (s DeleteVolumeResponseBody) GoString() string {
	return s.String()
}

func (s *DeleteVolumeResponseBody) GetCode() *string {
	return s.Code
}

func (s *DeleteVolumeResponseBody) GetHttpStatusCode() *int32 {
	return s.HttpStatusCode
}

func (s *DeleteVolumeResponseBody) GetMessage() *string {
	return s.Message
}

func (s *DeleteVolumeResponseBody) GetRequestId() *string {
	return s.RequestId
}

func (s *DeleteVolumeResponseBody) GetSuccess() *bool {
	return s.Success
}

func (s *DeleteVolumeResponseBody) SetCode(v string) *DeleteVolumeResponseBody {
	s.Code = &v
	return s
}

func (s *DeleteVolumeResponseBody) SetHttpStatusCode(v int32) *DeleteVolumeResponseBody {
	s.HttpStatusCode = &v
	return s
}

func (s *DeleteVolumeResponseBody) SetMessage(v string) *DeleteVolumeResponseBody {
	s.Message = &v
	return s
}

func (s *DeleteVolumeResponseBody) SetRequestId(v string) *DeleteVolumeResponseBody {
	s.RequestId = &v
	return s
}

func (s *DeleteVolumeResponseBody) SetSuccess(v bool) *DeleteVolumeResponseBody {
	s.Success = &v
	return s
}

func (s *DeleteVolumeResponseBody) Validate() error {
	return dara.Validate(s)
}
