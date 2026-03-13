package integration_test

import (
	"os"
	"testing"
	"time"

	"github.com/aliyun/wuying-agentbay-sdk/golang/pkg/agentbay"
	"github.com/aliyun/wuying-agentbay-sdk/golang/tests/pkg/agentbay/testutil"
)

func TestWsStreamCancelE2E(t *testing.T) {
	apiKey := testutil.GetTestAPIKey(t)
	ab, err := agentbay.NewAgentBay(apiKey)
	if err != nil {
		t.Fatalf("Error initializing AgentBay client: %v", err)
	}

	imageID := "imgc-0ab5taki2khozz0p8"
	if v := os.Getenv("AGENTBAY_WS_IMAGE_ID"); v != "" {
		imageID = v
	}
	params := agentbay.NewCreateSessionParams().WithImageId(imageID)
	sessionResult, err := ab.Create(params)
	if err != nil {
		t.Fatalf("Error creating session: %v", err)
	}
	session := sessionResult.Session
	defer func() {
		_, _ = ab.Delete(session)
	}()

	wsClient, err := session.GetStreamingWsClient()
	if err != nil {
		t.Fatalf("Error getting WS client: %v", err)
	}
	defer func() {
		_ = wsClient.Close()
	}()

	target := "wuying_codespace"
	for _, tool := range session.McpTools {
		if tool.GetName() == "run_code" && tool.GetServer() != "" {
			target = tool.GetServer()
			break
		}
	}

	events := []map[string]interface{}{}
	ends := []map[string]interface{}{}
	errors := []error{}

	onEvent := func(_invocationID string, data map[string]interface{}) {
		events = append(events, data)
	}
	onEnd := func(_invocationID string, data map[string]interface{}) {
		ends = append(ends, data)
	}
	onError := func(_invocationID string, err error) {
		errors = append(errors, err)
	}

	handle, err := wsClient.CallStream(target, map[string]interface{}{
		"method": "run_code",
		"mode":   "stream",
		"params": map[string]interface{}{
			"language": "python",
			"timeoutS": 60,
			"code": "import time\n" +
				"print(0)\n" +
				"time.sleep(10)\n" +
				"print(1)\n",
		},
	}, onEvent, onEnd, onError)
	if err != nil {
		t.Fatalf("call stream error: %v", err)
	}

	time.Sleep(500 * time.Millisecond)
	if err := handle.Cancel(); err != nil {
		t.Fatalf("cancel error: %v", err)
	}

	type waitRes struct {
		data map[string]interface{}
		err  error
	}
	resCh := make(chan waitRes, 1)
	go func() {
		d, e := handle.WaitEnd()
		resCh <- waitRes{data: d, err: e}
	}()

	select {
	case r := <-resCh:
		if r.err == nil {
			t.Fatalf("expected WsCancelledError, got nil err data=%v", r.data)
		}
		if _, ok := r.err.(*agentbay.WsCancelledError); !ok {
			t.Fatalf("expected WsCancelledError, got %T: %v", r.err, r.err)
		}
	case <-time.After(2 * time.Second):
		t.Fatalf("timeout waiting for WaitEnd after cancel")
	}

	if len(ends) != 0 {
		t.Fatalf("unexpected onEnd after cancel: ends=%v events=%v errors=%v", ends, events, errors)
	}
	if len(errors) != 1 {
		t.Fatalf("expected exactly 1 onError, got=%v", errors)
	}
	if _, ok := errors[0].(*agentbay.WsCancelledError); !ok {
		t.Fatalf("expected onError WsCancelledError, got %T: %v", errors[0], errors[0])
	}
}
