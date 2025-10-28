// This file is auto-generated, don't edit it. Thanks.
package client

import (
	"github.com/alibabacloud-go/tea/dara"
)

type iInitBrowserRequest interface {
	dara.Model
	String() string
	GoString() string
	SetAuthorization(v string) *InitBrowserRequest
	GetAuthorization() *string
	SetSessionId(v string) *InitBrowserRequest
	GetSessionId() *string
	SetPersistentPath(v string) *InitBrowserRequest
	GetPersistentPath() *string
	SetBrowserOption(v map[string]interface{}) *InitBrowserRequest
	GetBrowserOption() map[string]interface{}
}

type InitBrowserRequest struct {
	Authorization  *string                `json:"Authorization,omitempty" xml:"Authorization,omitempty"`
	SessionId      *string                `json:"SessionId,omitempty" xml:"SessionId,omitempty"`
	PersistentPath *string                `json:"PersistentPath,omitempty" xml:"PersistentPath,omitempty"`
	BrowserOption  map[string]interface{} `json:"BrowserOption,omitempty" xml:"BrowserOption,omitempty"`
}

func (s InitBrowserRequest) String() string {
	return dara.Prettify(s)
}

func (s InitBrowserRequest) GoString() string {
	return s.String()
}

func (s *InitBrowserRequest) GetAuthorization() *string {
	return s.Authorization
}

func (s *InitBrowserRequest) GetSessionId() *string {
	return s.SessionId
}

func (s *InitBrowserRequest) GetPersistentPath() *string {
	return s.PersistentPath
}

func (s *InitBrowserRequest) GetBrowserOption() map[string]interface{} {
	return s.BrowserOption
}

func (s *InitBrowserRequest) SetAuthorization(v string) *InitBrowserRequest {
	s.Authorization = &v
	return s
}

func (s *InitBrowserRequest) SetSessionId(v string) *InitBrowserRequest {
	s.SessionId = &v
	return s
}

func (s *InitBrowserRequest) SetPersistentPath(v string) *InitBrowserRequest {
	s.PersistentPath = &v
	return s
}

func (s *InitBrowserRequest) SetBrowserOption(v map[string]interface{}) *InitBrowserRequest {
	s.BrowserOption = v
	return s
}

func (s *InitBrowserRequest) Validate() error {
	return dara.Validate(s)
}

