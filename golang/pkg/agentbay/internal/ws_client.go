package internal

import (
	"encoding/json"
	"fmt"
	"net/http"
	"sync"
	"time"

	"golang.org/x/net/websocket"
)

type OnEvent func(invocationID string, data map[string]interface{})
type OnEnd func(invocationID string, data map[string]interface{})
type OnError func(invocationID string, err error)

type DebugLogger func(message string)

type PushCallback = func(payload map[string]interface{})

type endResult struct {
	data map[string]interface{}
	err  error
}

// WsCancelledError is returned when a stream is cancelled by the caller.
type WsCancelledError struct {
	InvocationID string
}

func (e *WsCancelledError) Error() string {
	return fmt.Sprintf("stream %s was cancelled by caller", e.InvocationID)
}

type WsClient struct {
	wsURL  string
	token  string
	logger DebugLogger

	mu        sync.Mutex
	conn      *websocket.Conn
	pending   map[string]*pendingStream
	closedCh  chan struct{}
	callbacks map[string]map[string]PushCallback
	nextCbID  uint64
}

type pendingStream struct {
	onEvent OnEvent
	onEnd   OnEnd
	onError OnError
	endCh   chan endResult
}

type WsStreamHandle struct {
	InvocationID string
	waitEnd      func() (map[string]interface{}, error)
	cancel       func() error
}

func (h *WsStreamHandle) WaitEnd() (map[string]interface{}, error) {
	return h.waitEnd()
}

func (h *WsStreamHandle) Cancel() error {
	if h.cancel == nil {
		return nil
	}
	return h.cancel()
}

func NewWsClient(wsURL string, token string, logger DebugLogger) *WsClient {
	return &WsClient{
		wsURL:     wsURL,
		token:     token,
		logger:    logger,
		pending:   make(map[string]*pendingStream),
		closedCh:  make(chan struct{}),
		callbacks: make(map[string]map[string]PushCallback),
	}
}

func (c *WsClient) RegisterCallback(target string, callback PushCallback) func() {
	if target == "" {
		panic("target must be a non-empty string")
	}
	if callback == nil {
		panic("callback must not be nil")
	}
	c.mu.Lock()
	c.nextCbID++
	id := fmt.Sprintf("%d", c.nextCbID)
	if c.callbacks[target] == nil {
		c.callbacks[target] = make(map[string]PushCallback)
	}
	c.callbacks[target][id] = callback
	c.mu.Unlock()
	return func() {
		c.mu.Lock()
		m := c.callbacks[target]
		if m != nil {
			delete(m, id)
			if len(m) == 0 {
				delete(c.callbacks, target)
			}
		}
		c.mu.Unlock()
	}
}

func (c *WsClient) UnregisterCallback(target string) {
	if target == "" {
		panic("target must be a non-empty string")
	}
	c.mu.Lock()
	delete(c.callbacks, target)
	c.mu.Unlock()
}

func (c *WsClient) Connect() error {
	c.mu.Lock()
	if c.conn != nil {
		c.mu.Unlock()
		return nil
	}
	c.mu.Unlock()

	cfg, err := websocket.NewConfig(c.wsURL, "http://localhost/")
	if err != nil {
		return err
	}
	cfg.Header = http.Header{}
	cfg.Header.Set("X-Access-Token", c.token)

	conn, err := websocket.DialConfig(cfg)
	if err != nil {
		return err
	}

	c.mu.Lock()
	c.conn = conn
	c.mu.Unlock()

	go c.recvLoop()
	return nil
}

func (c *WsClient) Close() error {
	c.mu.Lock()
	conn := c.conn
	c.conn = nil
	c.mu.Unlock()

	select {
	case <-c.closedCh:
	default:
		close(c.closedCh)
	}

	if conn != nil {
		_ = conn.Close()
	}
	c.failAllPending(fmt.Errorf("WS client closed"))
	return nil
}

// SendMessage sends a message to the target without expecting a response.
// Used for one-way notifications like browser callback messages.
//
// Parameters:
//   - target: The target service identifier
//   - data: The message data to send
//
// Returns an error if the connection is not established or sending fails.
func (c *WsClient) SendMessage(target string, data map[string]interface{}) error {
	if err := c.Connect(); err != nil {
		return err
	}

	invocationID := newInvocationID()

	c.mu.Lock()
	conn := c.conn
	c.mu.Unlock()

	if conn == nil {
		return fmt.Errorf("WS is not connected")
	}

	payload := map[string]interface{}{
		"invocationId": invocationID,
		"source":       "SDK",
		"target":       target,
		"data":         data,
	}

	c.logFrame(">>", payload)

	payloadBytes, err := json.Marshal(payload)
	if err != nil {
		return fmt.Errorf("failed to marshal payload: %w", err)
	}

	if err := websocket.Message.Send(conn, string(payloadBytes)); err != nil {
		return fmt.Errorf("failed to send message: %w", err)
	}

	return nil
}

func (c *WsClient) CallStream(target string, data map[string]interface{}, onEvent OnEvent, onEnd OnEnd, onError OnError) (*WsStreamHandle, error) {
	if err := c.Connect(); err != nil {
		return nil, err
	}

	invocationID := newInvocationID()
	endCh := make(chan endResult, 1)
	p := &pendingStream{
		onEvent: onEvent,
		onEnd:   onEnd,
		onError: onError,
		endCh:   endCh,
	}

	c.mu.Lock()
	c.pending[invocationID] = p
	conn := c.conn
	c.mu.Unlock()

	if conn == nil {
		c.mu.Lock()
		delete(c.pending, invocationID)
		c.mu.Unlock()
		return nil, fmt.Errorf("WS is not connected")
	}

	payload := map[string]interface{}{
		"invocationId": invocationID,
		"source":       "SDK",
		"target":       target,
		"data":         data,
	}
	c.logFrame(">>", payload)
	if err := websocket.JSON.Send(conn, payload); err != nil {
		c.mu.Lock()
		delete(c.pending, invocationID)
		c.mu.Unlock()
		return nil, err
	}

	return &WsStreamHandle{
		InvocationID: invocationID,
		waitEnd: func() (map[string]interface{}, error) {
			select {
			case <-c.closedCh:
				return nil, fmt.Errorf("WS connection closed")
			case r := <-endCh:
				if r.err != nil {
					return nil, r.err
				}
				return r.data, nil
			case <-time.After(5 * time.Minute):
				return nil, fmt.Errorf("timeout waiting for WS end event")
			}
		},
		cancel: func() error {
			c.cancelPending(invocationID)
			return nil
		},
	}, nil
}

func (c *WsClient) cancelPending(invocationID string) {
	c.mu.Lock()
	p := c.pending[invocationID]
	delete(c.pending, invocationID)
	c.mu.Unlock()
	if p == nil {
		return
	}
	err := &WsCancelledError{InvocationID: invocationID}
	if p.onError != nil {
		p.onError(invocationID, err)
	}
	select {
	case p.endCh <- endResult{err: err}:
	default:
	}
}

func (c *WsClient) recvLoop() {
	for {
		c.mu.Lock()
		conn := c.conn
		c.mu.Unlock()
		if conn == nil {
			return
		}

		var msg map[string]interface{}
		err := websocket.JSON.Receive(conn, &msg)
		if err != nil {
			_ = c.Close()
			return
		}
		c.handleIncoming(msg)
	}
}

func (c *WsClient) handleIncoming(msg map[string]interface{}) {
	invocationID, _ := msg["invocationId"].(string)
	if invocationID == "" {
		if rid, ok := msg["requestId"].(string); ok {
			invocationID = rid
		}
	}
	if invocationID == "" {
		return
	}

	c.mu.Lock()
	p := c.pending[invocationID]
	c.mu.Unlock()

	source, _ := msg["source"].(string)
	dataAny, _ := msg["data"]
	targetAny, _ := msg["target"]
	target, _ := targetAny.(string)

	if p == nil {
		routeTarget := target
		if routeTarget == "SDK" && source != "" && source != "SDK" {
			routeTarget = source
		}
		if routeTarget == "" {
			return
		}

		dataObj := map[string]interface{}(nil)
		if m, ok := dataAny.(map[string]interface{}); ok {
			dataObj = m
		} else if s, ok := dataAny.(string); ok && s != "" {
			var parsed map[string]interface{}
			if err := json.Unmarshal([]byte(s), &parsed); err != nil {
				return
			}
			if parsed == nil {
				return
			}
			dataObj = parsed
		} else {
			return
		}

		c.mu.Lock()
		cbMap := c.callbacks[routeTarget]
		callbacks := make([]PushCallback, 0, len(cbMap))
		for _, cb := range cbMap {
			callbacks = append(callbacks, cb)
		}
		c.mu.Unlock()
		if len(callbacks) == 0 {
			return
		}

		payload := map[string]interface{}{
			"requestId": invocationID,
			"target":    routeTarget,
			"data":      dataObj,
		}
		for _, cb := range callbacks {
			if cb != nil {
				cb(payload)
			}
		}
		return
	}

	if source == "WEBSOCKET_SERVER" {
		c.logFrame("<<", map[string]interface{}{"invocationId": invocationID, "source": source, "data": dataAny})
		errMsg := ""
		if e, ok := msg["error"].(string); ok && e != "" {
			errMsg = e
		}
		if errMsg == "" {
			if m, ok := dataAny.(map[string]interface{}); ok {
				if e, ok := m["error"].(string); ok && e != "" {
					errMsg = e
				}
			}
		}
		if errMsg != "" {
			err := fmt.Errorf("%s", errMsg)
			if p.onError != nil {
				p.onError(invocationID, err)
			}
			select {
			case p.endCh <- endResult{err: err}:
			default:
			}
			c.finishPending(invocationID)
			return
		}
		if p.onEnd != nil {
			if m, ok := dataAny.(map[string]interface{}); ok {
				p.onEnd(invocationID, m)
			} else {
				p.onEnd(invocationID, map[string]interface{}{})
			}
		}
		if m, ok := dataAny.(map[string]interface{}); ok {
			p.endCh <- endResult{data: m}
		} else {
			p.endCh <- endResult{data: map[string]interface{}{}}
		}
		c.finishPending(invocationID)
		return
	}

	data, ok := dataAny.(map[string]interface{})
	if !ok {
		if s, ok2 := dataAny.(string); ok2 && s != "" {
			var parsed map[string]interface{}
			if err := json.Unmarshal([]byte(s), &parsed); err != nil {
				return
			}
			data = parsed
		} else {
			return
		}
	}
	c.logFrame("<<", map[string]interface{}{"invocationId": invocationID, "source": source, "target": msg["target"], "data": data})

	if e, ok := data["error"].(string); ok && e != "" {
		err := fmt.Errorf("%s", e)
		if p.onError != nil {
			p.onError(invocationID, err)
		}
		select {
		case p.endCh <- endResult{err: err}:
		default:
		}
		c.finishPending(invocationID)
		return
	}

	phase, _ := data["phase"].(string)
	if phase == "event" {
		if p.onEvent != nil {
			p.onEvent(invocationID, data)
		}
		return
	}
	if phase == "end" {
		if p.onEnd != nil {
			p.onEnd(invocationID, data)
		}
		p.endCh <- endResult{data: data}
		c.finishPending(invocationID)
		return
	}

	err := fmt.Errorf("unsupported phase: %v", data["phase"])
	if p.onError != nil {
		p.onError(invocationID, err)
	}
	select {
	case p.endCh <- endResult{err: err}:
	default:
	}
	c.finishPending(invocationID)
}

func (c *WsClient) finishPending(invocationID string) {
	c.mu.Lock()
	delete(c.pending, invocationID)
	c.mu.Unlock()
}

func (c *WsClient) failAllPending(err error) {
	c.mu.Lock()
	items := make(map[string]*pendingStream, len(c.pending))
	for k, v := range c.pending {
		items[k] = v
	}
	c.pending = make(map[string]*pendingStream)
	c.mu.Unlock()

	for invocationID, p := range items {
		if p.onError != nil {
			p.onError(invocationID, err)
		}
		select {
		case p.endCh <- endResult{err: err}:
		default:
		}
	}
}

func (c *WsClient) logFrame(direction string, payload map[string]interface{}) {
	if c.logger == nil {
		return
	}
	raw, err := json.Marshal(payload)
	if err != nil {
		c.logger(fmt.Sprintf("WS %s %v", direction, payload))
		return
	}
	s := string(raw)
	if len(s) > 1200 {
		s = s[:1200] + "..."
	}
	c.logger(fmt.Sprintf("WS %s %s", direction, s))
}

func newInvocationID() string {
	return fmt.Sprintf("%d", time.Now().UnixNano())
}
