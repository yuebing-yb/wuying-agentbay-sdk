// This file is auto-generated, don't edit it. Thanks.
package client

import (
	"github.com/alibabacloud-go/tea/dara"
)

type iBindContextsResponse interface {
	dara.Model
	String() string
	GoString() string
	SetHeaders(v map[string]*string) *BindContextsResponse
	GetHeaders() map[string]*string
	SetStatusCode(v int32) *BindContextsResponse
	GetStatusCode() *int32
	SetBody(v *BindContextsResponseBody) *BindContextsResponse
	GetBody() *BindContextsResponseBody
}

type BindContextsResponse struct {
	Headers    map[string]*string        `json:"headers,omitempty" xml:"headers,omitempty"`
	StatusCode *int32                    `json:"statusCode,omitempty" xml:"statusCode,omitempty"`
	Body       *BindContextsResponseBody `json:"body,omitempty" xml:"body,omitempty"`
}

func (s BindContextsResponse) String() string {
	return dara.Prettify(s)
}

func (s BindContextsResponse) GoString() string {
	return s.String()
}

func (s *BindContextsResponse) GetHeaders() map[string]*string {
	return s.Headers
}

func (s *BindContextsResponse) GetStatusCode() *int32 {
	return s.StatusCode
}

func (s *BindContextsResponse) GetBody() *BindContextsResponseBody {
	return s.Body
}

func (s *BindContextsResponse) SetHeaders(v map[string]*string) *BindContextsResponse {
	s.Headers = v
	return s
}

func (s *BindContextsResponse) SetStatusCode(v int32) *BindContextsResponse {
	s.StatusCode = &v
	return s
}

func (s *BindContextsResponse) SetBody(v *BindContextsResponseBody) *BindContextsResponse {
	s.Body = v
	return s
}

func (s *BindContextsResponse) Validate() error {
	if s.Body != nil {
		if err := s.Body.Validate(); err != nil {
			return err
		}
	}
	return nil
}
