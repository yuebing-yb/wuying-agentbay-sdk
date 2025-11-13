// This file is auto-generated, don't edit it. Thanks.
package client

import (
	"github.com/alibabacloud-go/tea/dara"
)

type iGetAdbLinkResponse interface {
	dara.Model
	String() string
	GoString() string
	SetHeaders(v map[string]*string) *GetAdbLinkResponse
	GetHeaders() map[string]*string
	SetStatusCode(v int32) *GetAdbLinkResponse
	GetStatusCode() *int32
	SetBody(v *GetAdbLinkResponseBody) *GetAdbLinkResponse
	GetBody() *GetAdbLinkResponseBody
}

type GetAdbLinkResponse struct {
	Headers    map[string]*string      `json:"headers,omitempty" xml:"headers,omitempty"`
	StatusCode *int32                  `json:"statusCode,omitempty" xml:"statusCode,omitempty"`
	Body       *GetAdbLinkResponseBody `json:"body,omitempty" xml:"body,omitempty"`
}

func (s GetAdbLinkResponse) String() string {
	return dara.Prettify(s)
}

func (s GetAdbLinkResponse) GoString() string {
	return s.String()
}

func (s *GetAdbLinkResponse) GetHeaders() map[string]*string {
	return s.Headers
}

func (s *GetAdbLinkResponse) GetStatusCode() *int32 {
	return s.StatusCode
}

func (s *GetAdbLinkResponse) GetBody() *GetAdbLinkResponseBody {
	return s.Body
}

func (s *GetAdbLinkResponse) SetHeaders(v map[string]*string) *GetAdbLinkResponse {
	s.Headers = v
	return s
}

func (s *GetAdbLinkResponse) SetStatusCode(v int32) *GetAdbLinkResponse {
	s.StatusCode = &v
	return s
}

func (s *GetAdbLinkResponse) SetBody(v *GetAdbLinkResponseBody) *GetAdbLinkResponse {
	s.Body = v
	return s
}

func (s *GetAdbLinkResponse) Validate() error {
	if s.Body != nil {
		if err := s.Body.Validate(); err != nil {
			return err
		}
	}
	return nil
}
