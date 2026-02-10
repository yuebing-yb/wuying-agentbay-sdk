package agentbay

import (
	"fmt"

	"github.com/aliyun/wuying-agentbay-sdk/golang/pkg/agentbay/internal"
)

// WsCancelledError is returned when a WS stream is cancelled by the caller.
type WsCancelledError = internal.WsCancelledError

type WsOnEvent func(invocationID string, data map[string]interface{})
type WsOnEnd func(invocationID string, data map[string]interface{})
type WsOnError func(invocationID string, err error)

// WsStreamHandle is a public wrapper for WS streaming handles.
type WsStreamHandle struct {
	InvocationID string
	waitEnd      func() (map[string]interface{}, error)
	cancel       func() error
}

func (h *WsStreamHandle) WaitEnd() (map[string]interface{}, error) {
	if h == nil || h.waitEnd == nil {
		return nil, fmt.Errorf("nil ws stream handle")
	}
	return h.waitEnd()
}

func (h *WsStreamHandle) Cancel() error {
	if h == nil || h.cancel == nil {
		return nil
	}
	return h.cancel()
}

// WsStreamingClient provides access to low-level WS streaming APIs.
// This is primarily intended for end-to-end validation and advanced usage.
type WsStreamingClient interface {
	CallStream(
		target string,
		data map[string]interface{},
		onEvent WsOnEvent,
		onEnd WsOnEnd,
		onError WsOnError,
	) (*WsStreamHandle, error)
	Close() error
}

type wsStreamingClientAdapter struct {
	inner *internal.WsClient
}

func (c *wsStreamingClientAdapter) Close() error {
	return c.inner.Close()
}

func (c *wsStreamingClientAdapter) CallStream(
	target string,
	data map[string]interface{},
	onEvent WsOnEvent,
	onEnd WsOnEnd,
	onError WsOnError,
) (*WsStreamHandle, error) {
	h, err := c.inner.CallStream(
		target,
		data,
		internal.OnEvent(onEvent),
		internal.OnEnd(onEnd),
		internal.OnError(onError),
	)
	if err != nil {
		return nil, err
	}
	return &WsStreamHandle{
		InvocationID: h.InvocationID,
		waitEnd: func() (map[string]interface{}, error) {
			return h.WaitEnd()
		},
		cancel: func() error {
			return h.Cancel()
		},
	}, nil
}

// GetStreamingWsClient returns a WS streaming client for this session.
func (s *Session) GetStreamingWsClient() (WsStreamingClient, error) {
	if s.WsUrl == "" {
		return nil, fmt.Errorf("ws url is not available for this session")
	}
	if s.Token == "" {
		return nil, fmt.Errorf("token is not available for WS connection")
	}
	if s.wsClient == nil {
		s.wsClient = internal.NewWsClient(s.WsUrl, s.Token, LogDebug)
	}
	if err := s.wsClient.Connect(); err != nil {
		return nil, err
	}
	return &wsStreamingClientAdapter{inner: s.wsClient}, nil
}

