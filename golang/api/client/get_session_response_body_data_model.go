// This file is auto-generated, don't edit it. Thanks.
package client

import (
	"github.com/alibabacloud-go/tea/dara"
)

type iGetSessionResponseBodyData interface {
	dara.Model
	String() string
	GoString() string
	SetAppInstanceId(v string) *GetSessionResponseBodyData
	GetAppInstanceId() *string
	SetHttpPort(v string) *GetSessionResponseBodyData
	GetHttpPort() *string
	SetNetworkInterfaceIp(v string) *GetSessionResponseBodyData
	GetNetworkInterfaceIp() *string
	SetResourceId(v string) *GetSessionResponseBodyData
	GetResourceId() *string
	SetResourceUrl(v string) *GetSessionResponseBodyData
	GetResourceUrl() *string
	SetSessionId(v string) *GetSessionResponseBodyData
	GetSessionId() *string
	SetStatus(v string) *GetSessionResponseBodyData
	GetStatus() *string
	SetSuccess(v bool) *GetSessionResponseBodyData
	GetSuccess() *bool
	SetToken(v string) *GetSessionResponseBodyData
	GetToken() *string
	SetVpcResource(v bool) *GetSessionResponseBodyData
	GetVpcResource() *bool
}

type GetSessionResponseBodyData struct {
	AppInstanceId      *string `json:"AppInstanceId,omitempty" xml:"AppInstanceId,omitempty"`
	HttpPort           *string `json:"HttpPort,omitempty" xml:"HttpPort,omitempty"`
	NetworkInterfaceIp *string `json:"NetworkInterfaceIp,omitempty" xml:"NetworkInterfaceIp,omitempty"`
	ResourceId         *string `json:"ResourceId,omitempty" xml:"ResourceId,omitempty"`
	ResourceUrl        *string `json:"ResourceUrl,omitempty" xml:"ResourceUrl,omitempty"`
	SessionId          *string `json:"SessionId,omitempty" xml:"SessionId,omitempty"`
	Status             *string `json:"Status,omitempty" xml:"Status,omitempty"`
	Success            *bool   `json:"Success,omitempty" xml:"Success,omitempty"`
	Token              *string `json:"Token,omitempty" xml:"Token,omitempty"`
	VpcResource        *bool   `json:"VpcResource,omitempty" xml:"VpcResource,omitempty"`
}

func (s GetSessionResponseBodyData) String() string {
	return dara.Prettify(s)
}

func (s GetSessionResponseBodyData) GoString() string {
	return s.String()
}

func (s *GetSessionResponseBodyData) GetAppInstanceId() *string {
	return s.AppInstanceId
}

func (s *GetSessionResponseBodyData) GetHttpPort() *string {
	return s.HttpPort
}

func (s *GetSessionResponseBodyData) GetNetworkInterfaceIp() *string {
	return s.NetworkInterfaceIp
}

func (s *GetSessionResponseBodyData) GetResourceId() *string {
	return s.ResourceId
}

func (s *GetSessionResponseBodyData) GetResourceUrl() *string {
	return s.ResourceUrl
}

func (s *GetSessionResponseBodyData) GetSessionId() *string {
	return s.SessionId
}

func (s *GetSessionResponseBodyData) GetStatus() *string {
	return s.Status
}

func (s *GetSessionResponseBodyData) GetSuccess() *bool {
	return s.Success
}

func (s *GetSessionResponseBodyData) GetToken() *string {
	return s.Token
}

func (s *GetSessionResponseBodyData) GetVpcResource() *bool {
	return s.VpcResource
}

func (s *GetSessionResponseBodyData) SetAppInstanceId(v string) *GetSessionResponseBodyData {
	s.AppInstanceId = &v
	return s
}

func (s *GetSessionResponseBodyData) SetHttpPort(v string) *GetSessionResponseBodyData {
	s.HttpPort = &v
	return s
}

func (s *GetSessionResponseBodyData) SetNetworkInterfaceIp(v string) *GetSessionResponseBodyData {
	s.NetworkInterfaceIp = &v
	return s
}

func (s *GetSessionResponseBodyData) SetResourceId(v string) *GetSessionResponseBodyData {
	s.ResourceId = &v
	return s
}

func (s *GetSessionResponseBodyData) SetResourceUrl(v string) *GetSessionResponseBodyData {
	s.ResourceUrl = &v
	return s
}

func (s *GetSessionResponseBodyData) SetSessionId(v string) *GetSessionResponseBodyData {
	s.SessionId = &v
	return s
}

func (s *GetSessionResponseBodyData) SetStatus(v string) *GetSessionResponseBodyData {
	s.Status = &v
	return s
}

func (s *GetSessionResponseBodyData) SetSuccess(v bool) *GetSessionResponseBodyData {
	s.Success = &v
	return s
}

func (s *GetSessionResponseBodyData) SetToken(v string) *GetSessionResponseBodyData {
	s.Token = &v
	return s
}

func (s *GetSessionResponseBodyData) SetVpcResource(v bool) *GetSessionResponseBodyData {
	s.VpcResource = &v
	return s
}

func (s *GetSessionResponseBodyData) Validate() error {
	return dara.Validate(s)
}