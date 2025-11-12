// This file is auto-generated, don't edit it. Thanks.
package client

import (
	"github.com/alibabacloud-go/tea/dara"
)

type iGetCdpLinkResponse interface {
	dara.Model
	String() string
	GoString() string
	SetHeaders(v map[string]*string) *GetCdpLinkResponse
	GetHeaders() map[string]*string
	SetStatusCode(v int32) *GetCdpLinkResponse
	GetStatusCode() *int32
	SetBody(v *GetCdpLinkResponseBody) *GetCdpLinkResponse
	GetBody() *GetCdpLinkResponseBody
}

type GetCdpLinkResponse struct {
	Headers    map[string]*string      `json:"headers,omitempty" xml:"headers,omitempty"`
	StatusCode *int32                  `json:"statusCode,omitempty" xml:"statusCode,omitempty"`
	Body       *GetCdpLinkResponseBody `json:"body,omitempty" xml:"body,omitempty"`
}

func (s GetCdpLinkResponse) String() string {
	return dara.Prettify(s)
}

func (s GetCdpLinkResponse) GoString() string {
	return s.String()
}

func (s *GetCdpLinkResponse) GetHeaders() map[string]*string {
	return s.Headers
}

func (s *GetCdpLinkResponse) GetStatusCode() *int32 {
	return s.StatusCode
}

func (s *GetCdpLinkResponse) GetBody() *GetCdpLinkResponseBody {
	return s.Body
}

func (s *GetCdpLinkResponse) SetHeaders(v map[string]*string) *GetCdpLinkResponse {
	s.Headers = v
	return s
}

func (s *GetCdpLinkResponse) SetStatusCode(v int32) *GetCdpLinkResponse {
	s.StatusCode = &v
	return s
}

func (s *GetCdpLinkResponse) SetBody(v *GetCdpLinkResponseBody) *GetCdpLinkResponse {
	s.Body = v
	return s
}

func (s *GetCdpLinkResponse) Validate() error {
	if s.Body != nil {
		if err := s.Body.Validate(); err != nil {
			return err
		}
	}
	return nil
}
