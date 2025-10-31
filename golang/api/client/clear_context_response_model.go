// This file is auto-generated, don't edit it. Thanks.
package client

import (
	"github.com/alibabacloud-go/tea/dara"
)

type iClearContextResponse interface {
	dara.Model
	String() string
	GoString() string
	SetHeaders(v map[string]*string) *ClearContextResponse
	GetHeaders() map[string]*string
	SetStatusCode(v int32) *ClearContextResponse
	GetStatusCode() *int32
	SetBody(v *ClearContextResponseBody) *ClearContextResponse
	GetBody() *ClearContextResponseBody
}

type ClearContextResponse struct {
	Headers    map[string]*string        `json:"headers,omitempty" xml:"headers,omitempty"`
	StatusCode *int32                    `json:"statusCode,omitempty" xml:"statusCode,omitempty"`
	Body       *ClearContextResponseBody `json:"body,omitempty" xml:"body,omitempty"`
}

func (s ClearContextResponse) String() string {
	return dara.Prettify(s)
}

func (s ClearContextResponse) GoString() string {
	return s.String()
}

func (s *ClearContextResponse) GetHeaders() map[string]*string {
	return s.Headers
}

func (s *ClearContextResponse) GetStatusCode() *int32 {
	return s.StatusCode
}

func (s *ClearContextResponse) GetBody() *ClearContextResponseBody {
	return s.Body
}

func (s *ClearContextResponse) SetHeaders(v map[string]*string) *ClearContextResponse {
	s.Headers = v
	return s
}

func (s *ClearContextResponse) SetStatusCode(v int32) *ClearContextResponse {
	s.StatusCode = &v
	return s
}

func (s *ClearContextResponse) SetBody(v *ClearContextResponseBody) *ClearContextResponse {
	s.Body = v
	return s
}

func (s *ClearContextResponse) Validate() error {
	if s.Body != nil {
		if err := s.Body.Validate(); err != nil {
			return err
		}
	}
	return nil
}
