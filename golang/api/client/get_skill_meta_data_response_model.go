// This file is auto-generated, don't edit it. Thanks.
package client

import (
	"github.com/alibabacloud-go/tea/dara"
)

type iGetSkillMetaDataResponse interface {
	dara.Model
	String() string
	GoString() string
	SetHeaders(v map[string]*string) *GetSkillMetaDataResponse
	GetHeaders() map[string]*string
	SetStatusCode(v int32) *GetSkillMetaDataResponse
	GetStatusCode() *int32
	SetBody(v *GetSkillMetaDataResponseBody) *GetSkillMetaDataResponse
	GetBody() *GetSkillMetaDataResponseBody
}

type GetSkillMetaDataResponse struct {
	Headers    map[string]*string            `json:"headers,omitempty" xml:"headers,omitempty"`
	StatusCode *int32                        `json:"statusCode,omitempty" xml:"statusCode,omitempty"`
	Body       *GetSkillMetaDataResponseBody `json:"body,omitempty" xml:"body,omitempty"`
}

func (s GetSkillMetaDataResponse) String() string {
	return dara.Prettify(s)
}

func (s GetSkillMetaDataResponse) GoString() string {
	return s.String()
}

func (s *GetSkillMetaDataResponse) GetHeaders() map[string]*string {
	return s.Headers
}

func (s *GetSkillMetaDataResponse) GetStatusCode() *int32 {
	return s.StatusCode
}

func (s *GetSkillMetaDataResponse) GetBody() *GetSkillMetaDataResponseBody {
	return s.Body
}

func (s *GetSkillMetaDataResponse) SetHeaders(v map[string]*string) *GetSkillMetaDataResponse {
	s.Headers = v
	return s
}

func (s *GetSkillMetaDataResponse) SetStatusCode(v int32) *GetSkillMetaDataResponse {
	s.StatusCode = &v
	return s
}

func (s *GetSkillMetaDataResponse) SetBody(v *GetSkillMetaDataResponseBody) *GetSkillMetaDataResponse {
	s.Body = v
	return s
}

func (s *GetSkillMetaDataResponse) Validate() error {
	if s.Body != nil {
		if err := s.Body.Validate(); err != nil {
			return err
		}
	}
	return nil
}
