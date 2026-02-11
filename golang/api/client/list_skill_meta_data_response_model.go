// This file is auto-generated, don't edit it. Thanks.
package client

import (
	"github.com/alibabacloud-go/tea/dara"
)

type iListSkillMetaDataResponse interface {
	dara.Model
	String() string
	GoString() string
	SetHeaders(v map[string]*string) *ListSkillMetaDataResponse
	GetHeaders() map[string]*string
	SetStatusCode(v int32) *ListSkillMetaDataResponse
	GetStatusCode() *int32
	SetBody(v *ListSkillMetaDataResponseBody) *ListSkillMetaDataResponse
	GetBody() *ListSkillMetaDataResponseBody
}

type ListSkillMetaDataResponse struct {
	Headers    map[string]*string            `json:"headers,omitempty" xml:"headers,omitempty"`
	StatusCode *int32                        `json:"statusCode,omitempty" xml:"statusCode,omitempty"`
	Body       *ListSkillMetaDataResponseBody `json:"body,omitempty" xml:"body,omitempty"`
}

func (s ListSkillMetaDataResponse) String() string {
	return dara.Prettify(s)
}

func (s ListSkillMetaDataResponse) GoString() string {
	return s.String()
}

func (s *ListSkillMetaDataResponse) GetHeaders() map[string]*string {
	return s.Headers
}

func (s *ListSkillMetaDataResponse) GetStatusCode() *int32 {
	return s.StatusCode
}

func (s *ListSkillMetaDataResponse) GetBody() *ListSkillMetaDataResponseBody {
	return s.Body
}

func (s *ListSkillMetaDataResponse) SetHeaders(v map[string]*string) *ListSkillMetaDataResponse {
	s.Headers = v
	return s
}

func (s *ListSkillMetaDataResponse) SetStatusCode(v int32) *ListSkillMetaDataResponse {
	s.StatusCode = &v
	return s
}

func (s *ListSkillMetaDataResponse) SetBody(v *ListSkillMetaDataResponseBody) *ListSkillMetaDataResponse {
	s.Body = v
	return s
}

func (s *ListSkillMetaDataResponse) Validate() error {
	if s.Body != nil {
		if err := s.Body.Validate(); err != nil {
			return err
		}
	}
	return nil
}

