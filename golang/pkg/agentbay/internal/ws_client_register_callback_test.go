package internal

import (
	"net/http/httptest"
	"reflect"
	"testing"
	"time"

	"golang.org/x/net/websocket"
)

func TestWsClientRegisterCallback_ShouldRoutePushBySourceWhenTargetIsSDK(t *testing.T) {
	srv := httptest.NewServer(websocket.Handler(func(ws *websocket.Conn) {
		_ = websocket.JSON.Send(ws, map[string]interface{}{
			"invocationId": "push_1",
			"source":       "wuying_cdp_mcp_server",
			"target":       "SDK",
			"data":         `{"method":"notification","status":"ok"}`,
		})
		_ = ws.Close()
	}))
	defer srv.Close()

	wsURL := "ws" + srv.URL[len("http"):]

	client := NewWsClient(wsURL, "token_test", nil)

	gotCh := make(chan map[string]interface{}, 1)
	client.RegisterCallback("wuying_cdp_mcp_server", func(payload map[string]interface{}) {
		gotCh <- payload
	})

	if err := client.Connect(); err != nil {
		t.Fatalf("connect failed: %v", err)
	}
	defer func() { _ = client.Close() }()

	select {
	case got := <-gotCh:
		want := map[string]interface{}{
			"requestId": "push_1",
			"target":    "wuying_cdp_mcp_server",
			"data": map[string]interface{}{
				"method": "notification",
				"status": "ok",
			},
		}
		if !reflect.DeepEqual(got, want) {
			t.Fatalf("unexpected payload: got=%v want=%v", got, want)
		}
	case <-time.After(2 * time.Second):
		t.Fatalf("timeout waiting for push callback")
	}
}
