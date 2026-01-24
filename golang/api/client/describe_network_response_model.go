// This file is auto-generated, don't edit it. Thanks.
package client

import (
	"github.com/alibabacloud-go/tea/dara"
)

type iDescribeNetworkResponse interface {
	dara.Model
	String() string
	GoString() string
	SetHeaders(v map[string]*string) *DescribeNetworkResponse
	GetHeaders() map[string]*string
	SetStatusCode(v int32) *DescribeNetworkResponse
	GetStatusCode() *int32
	SetBody(v *DescribeNetworkResponseBody) *DescribeNetworkResponse
	GetBody() *DescribeNetworkResponseBody
}

type DescribeNetworkResponse struct {
	Headers    map[string]*string           `json:"headers,omitempty" xml:"headers,omitempty"`
	StatusCode *int32                       `json:"statusCode,omitempty" xml:"statusCode,omitempty"`
	Body       *DescribeNetworkResponseBody `json:"body,omitempty" xml:"body,omitempty"`
}

func (s DescribeNetworkResponse) String() string {
	return dara.Prettify(s)
}

func (s DescribeNetworkResponse) GoString() string {
	return s.String()
}

func (s *DescribeNetworkResponse) GetHeaders() map[string]*string {
	return s.Headers
}

func (s *DescribeNetworkResponse) GetStatusCode() *int32 {
	return s.StatusCode
}

func (s *DescribeNetworkResponse) GetBody() *DescribeNetworkResponseBody {
	return s.Body
}

func (s *DescribeNetworkResponse) SetHeaders(v map[string]*string) *DescribeNetworkResponse {
	s.Headers = v
	return s
}

func (s *DescribeNetworkResponse) SetStatusCode(v int32) *DescribeNetworkResponse {
	s.StatusCode = &v
	return s
}

func (s *DescribeNetworkResponse) SetBody(v *DescribeNetworkResponseBody) *DescribeNetworkResponse {
	s.Body = v
	return s
}

func (s *DescribeNetworkResponse) Validate() error {
	if s.Body != nil {
		if err := s.Body.Validate(); err != nil {
			return err
		}
	}
	return nil
}
