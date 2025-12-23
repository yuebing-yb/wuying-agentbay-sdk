// This file is auto-generated, don't edit it. Thanks.
package client

import (
	"github.com/alibabacloud-go/tea/dara"
)

type iGetSessionDetailResponse interface {
	dara.Model
	String() string
	GoString() string
	SetHeaders(v map[string]*string) *GetSessionDetailResponse
	GetHeaders() map[string]*string
	SetStatusCode(v int32) *GetSessionDetailResponse
	GetStatusCode() *int32
	SetBody(v *GetSessionDetailResponseBody) *GetSessionDetailResponse
	GetBody() *GetSessionDetailResponseBody
}

type GetSessionDetailResponse struct {
	Headers    map[string]*string            `json:"headers,omitempty" xml:"headers,omitempty"`
	StatusCode *int32                        `json:"statusCode,omitempty" xml:"statusCode,omitempty"`
	Body       *GetSessionDetailResponseBody `json:"body,omitempty" xml:"body,omitempty"`
}

func (s GetSessionDetailResponse) String() string {
	return dara.Prettify(s)
}

func (s GetSessionDetailResponse) GoString() string {
	return s.String()
}

func (s *GetSessionDetailResponse) GetHeaders() map[string]*string {
	return s.Headers
}

func (s *GetSessionDetailResponse) GetStatusCode() *int32 {
	return s.StatusCode
}

func (s *GetSessionDetailResponse) GetBody() *GetSessionDetailResponseBody {
	return s.Body
}

func (s *GetSessionDetailResponse) SetHeaders(v map[string]*string) *GetSessionDetailResponse {
	s.Headers = v
	return s
}

func (s *GetSessionDetailResponse) SetStatusCode(v int32) *GetSessionDetailResponse {
	s.StatusCode = &v
	return s
}

func (s *GetSessionDetailResponse) SetBody(v *GetSessionDetailResponseBody) *GetSessionDetailResponse {
	s.Body = v
	return s
}

func (s *GetSessionDetailResponse) Validate() error {
	if s.Body != nil {
		if err := s.Body.Validate(); err != nil {
			return err
		}
	}
	return nil
}


