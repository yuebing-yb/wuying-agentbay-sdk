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

type WsClient struct {
	wsURL  string
	token  string
	logger DebugLogger

	mu       sync.Mutex
	conn     *websocket.Conn
	pending  map[string]*pendingStream
	closedCh chan struct{}
}

type pendingStream struct {
	onEvent OnEvent
	onEnd   OnEnd
	onError OnError
	endCh   chan map[string]interface{}
}

type WsStreamHandle struct {
	InvocationID string
	waitEnd      func() (map[string]interface{}, error)
}

func (h *WsStreamHandle) WaitEnd() (map[string]interface{}, error) {
	return h.waitEnd()
}

func NewWsClient(wsURL string, token string, logger DebugLogger) *WsClient {
	return &WsClient{
		wsURL:     wsURL,
		token:     token,
		logger:    logger,
		pending:   make(map[string]*pendingStream),
		closedCh:  make(chan struct{}),
	}
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

func (c *WsClient) CallStream(target string, data map[string]interface{}, onEvent OnEvent, onEnd OnEnd, onError OnError) (*WsStreamHandle, error) {
	if err := c.Connect(); err != nil {
		return nil, err
	}

	invocationID := newInvocationID()
	endCh := make(chan map[string]interface{}, 1)
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
			case d := <-endCh:
				return d, nil
			case <-time.After(5 * time.Minute):
				return nil, fmt.Errorf("timeout waiting for WS end event")
			}
		},
	}, nil
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
	if p == nil {
		return
	}

	source, _ := msg["source"].(string)
	dataAny, _ := msg["data"]

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
			p.endCh <- m
		} else {
			p.endCh <- map[string]interface{}{}
		}
		c.finishPending(invocationID)
		return
	}

	data, ok := dataAny.(map[string]interface{})
	if !ok {
		return
	}
	c.logFrame("<<", map[string]interface{}{"invocationId": invocationID, "source": source, "target": msg["target"], "data": data})

	if e, ok := data["error"].(string); ok && e != "" {
		err := fmt.Errorf("%s", e)
		if p.onError != nil {
			p.onError(invocationID, err)
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
		p.endCh <- data
		c.finishPending(invocationID)
		return
	}

	err := fmt.Errorf("unsupported phase: %v", data["phase"])
	if p.onError != nil {
		p.onError(invocationID, err)
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

