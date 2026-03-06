// This file is auto-generated, don't edit it. Thanks.
package client

import (
	"github.com/alibabacloud-go/tea/dara"
)

type iDescribeSessionContextsResponse interface {
	dara.Model
	String() string
	GoString() string
	SetHeaders(v map[string]*string) *DescribeSessionContextsResponse
	GetHeaders() map[string]*string
	SetStatusCode(v int32) *DescribeSessionContextsResponse
	GetStatusCode() *int32
	SetBody(v *DescribeSessionContextsResponseBody) *DescribeSessionContextsResponse
	GetBody() *DescribeSessionContextsResponseBody
}

type DescribeSessionContextsResponse struct {
	Headers    map[string]*string                   `json:"headers,omitempty" xml:"headers,omitempty"`
	StatusCode *int32                               `json:"statusCode,omitempty" xml:"statusCode,omitempty"`
	Body       *DescribeSessionContextsResponseBody `json:"body,omitempty" xml:"body,omitempty"`
}

func (s DescribeSessionContextsResponse) String() string {
	return dara.Prettify(s)
}

func (s DescribeSessionContextsResponse) GoString() string {
	return s.String()
}

func (s *DescribeSessionContextsResponse) GetHeaders() map[string]*string {
	return s.Headers
}

func (s *DescribeSessionContextsResponse) GetStatusCode() *int32 {
	return s.StatusCode
}

func (s *DescribeSessionContextsResponse) GetBody() *DescribeSessionContextsResponseBody {
	return s.Body
}

func (s *DescribeSessionContextsResponse) SetHeaders(v map[string]*string) *DescribeSessionContextsResponse {
	s.Headers = v
	return s
}

func (s *DescribeSessionContextsResponse) SetStatusCode(v int32) *DescribeSessionContextsResponse {
	s.StatusCode = &v
	return s
}

func (s *DescribeSessionContextsResponse) SetBody(v *DescribeSessionContextsResponseBody) *DescribeSessionContextsResponse {
	s.Body = v
	return s
}

func (s *DescribeSessionContextsResponse) Validate() error {
	if s.Body != nil {
		if err := s.Body.Validate(); err != nil {
			return err
		}
	}
	return nil
}
