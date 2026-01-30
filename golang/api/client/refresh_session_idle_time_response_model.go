// This file is auto-generated, don't edit it. Thanks.
package client

import (
	"github.com/alibabacloud-go/tea/dara"
)

type iRefreshSessionIdleTimeResponse interface {
	dara.Model
	String() string
	GoString() string
	SetHeaders(v map[string]*string) *RefreshSessionIdleTimeResponse
	GetHeaders() map[string]*string
	SetStatusCode(v int32) *RefreshSessionIdleTimeResponse
	GetStatusCode() *int32
	SetBody(v *RefreshSessionIdleTimeResponseBody) *RefreshSessionIdleTimeResponse
	GetBody() *RefreshSessionIdleTimeResponseBody
}

type RefreshSessionIdleTimeResponse struct {
	Headers    map[string]*string                  `json:"headers,omitempty" xml:"headers,omitempty"`
	StatusCode *int32                              `json:"statusCode,omitempty" xml:"statusCode,omitempty"`
	Body       *RefreshSessionIdleTimeResponseBody `json:"body,omitempty" xml:"body,omitempty"`
}

func (s RefreshSessionIdleTimeResponse) String() string {
	return dara.Prettify(s)
}

func (s RefreshSessionIdleTimeResponse) GoString() string {
	return s.String()
}

func (s *RefreshSessionIdleTimeResponse) GetHeaders() map[string]*string {
	return s.Headers
}

func (s *RefreshSessionIdleTimeResponse) GetStatusCode() *int32 {
	return s.StatusCode
}

func (s *RefreshSessionIdleTimeResponse) GetBody() *RefreshSessionIdleTimeResponseBody {
	return s.Body
}

func (s *RefreshSessionIdleTimeResponse) SetHeaders(v map[string]*string) *RefreshSessionIdleTimeResponse {
	s.Headers = v
	return s
}

func (s *RefreshSessionIdleTimeResponse) SetStatusCode(v int32) *RefreshSessionIdleTimeResponse {
	s.StatusCode = &v
	return s
}

func (s *RefreshSessionIdleTimeResponse) SetBody(v *RefreshSessionIdleTimeResponseBody) *RefreshSessionIdleTimeResponse {
	s.Body = v
	return s
}

func (s *RefreshSessionIdleTimeResponse) Validate() error {
	if s.Body != nil {
		if err := s.Body.Validate(); err != nil {
			return err
		}
	}
	return nil
}

