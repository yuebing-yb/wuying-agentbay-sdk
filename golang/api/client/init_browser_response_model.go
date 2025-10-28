// This file is auto-generated, don't edit it. Thanks.
package client

import (
	"github.com/alibabacloud-go/tea/dara"
)

type iInitBrowserResponse interface {
	dara.Model
	String() string
	GoString() string
	SetHeaders(v map[string]*string) *InitBrowserResponse
	GetHeaders() map[string]*string
	SetStatusCode(v int32) *InitBrowserResponse
	GetStatusCode() *int32
	SetBody(v *InitBrowserResponseBody) *InitBrowserResponse
	GetBody() *InitBrowserResponseBody
}

type InitBrowserResponse struct {
	Headers    map[string]*string       `json:"headers,omitempty" xml:"headers,omitempty"`
	StatusCode *int32                   `json:"statusCode,omitempty" xml:"statusCode,omitempty"`
	Body       *InitBrowserResponseBody `json:"body,omitempty" xml:"body,omitempty"`
}

func (s InitBrowserResponse) String() string {
	return dara.Prettify(s)
}

func (s InitBrowserResponse) GoString() string {
	return s.String()
}

func (s *InitBrowserResponse) GetHeaders() map[string]*string {
	return s.Headers
}

func (s *InitBrowserResponse) GetStatusCode() *int32 {
	return s.StatusCode
}

func (s *InitBrowserResponse) GetBody() *InitBrowserResponseBody {
	return s.Body
}

func (s *InitBrowserResponse) SetHeaders(v map[string]*string) *InitBrowserResponse {
	s.Headers = v
	return s
}

func (s *InitBrowserResponse) SetStatusCode(v int32) *InitBrowserResponse {
	s.StatusCode = &v
	return s
}

func (s *InitBrowserResponse) SetBody(v *InitBrowserResponseBody) *InitBrowserResponse {
	s.Body = v
	return s
}

func (s *InitBrowserResponse) Validate() error {
	return dara.Validate(s)
}

