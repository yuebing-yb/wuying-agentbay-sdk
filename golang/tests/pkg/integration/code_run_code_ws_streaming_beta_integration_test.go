package integration_test

import (
	"os"
	"strings"
	"testing"
	"time"

	"github.com/aliyun/wuying-agentbay-sdk/golang/pkg/agentbay"
	"github.com/aliyun/wuying-agentbay-sdk/golang/tests/pkg/agentbay/testutil"
)

func TestRunCodeWsStreamingBetaE2E(t *testing.T) {
	// Streaming API temporarily disabled; will be re-enabled in a future release
	t.Skip("Streaming API temporarily disabled; will be re-enabled in a future release")
	apiKey := testutil.GetTestAPIKey(t)
	ab, err := agentbay.NewAgentBay(apiKey)
	if err != nil {
		t.Fatalf("Error initializing AgentBay client: %v", err)
	}

	imageID := "imgc-0ab5ta4n2htfrppyw"
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

	stdoutChunks := []string{}
	stdoutTimes := []time.Time{}
	errors := []string{}

	onStdout := func(chunk string) {
		stdoutChunks = append(stdoutChunks, chunk)
		stdoutTimes = append(stdoutTimes, time.Now())
	}
	onError := func(err error) {
		errors = append(errors, err.Error())
	}

	start := time.Now()
	// Note: streaming API temporarily disabled; this test is skipped.
	// When re-enabled, use the exported RunCodeStreamBetaOptions type.
	r, err := session.Code.RunCode(
		"import time\n"+
			"print('hello', flush=True)\n"+
			"time.sleep(1.0)\n"+
			"print(2, flush=True)\n",
		"python",
		60,
	)
	_ = onStdout
	_ = onError
	end := time.Now()
	if err != nil {
		t.Fatalf("run code streaming error: %v", err)
	}

	if len(errors) != 0 {
		t.Fatalf("expected no errors, got=%v, stdout=%v", errors, stdoutChunks)
	}
	if !r.Success {
		t.Fatalf("expected success, error_message=%s, stdout=%v", r.ErrorMessage, stdoutChunks)
	}

	if len(stdoutChunks) < 2 {
		t.Fatalf("expected >=2 stdout events, got=%d: %v", len(stdoutChunks), stdoutChunks)
	}
	if end.Sub(start) < 1*time.Second {
		t.Fatalf("expected duration >=1.0s, got=%s", end.Sub(start))
	}

	joined := strings.Join(stdoutChunks, "")
	if !strings.Contains(joined, "hello") {
		t.Fatalf("expected stdout contains hello, got=%q", joined)
	}
	if !strings.Contains(joined, "2") {
		t.Fatalf("expected stdout contains 2, got=%q", joined)
	}

	var helloT *time.Time
	var twoT *time.Time
	for i, chunk := range stdoutChunks {
		tm := stdoutTimes[i]
		if helloT == nil && strings.Contains(chunk, "hello") {
			helloT = &tm
		}
		if twoT == nil && strings.Contains(chunk, "2") {
			twoT = &tm
		}
	}
	if helloT == nil {
		t.Fatalf("hello not observed in stdout events: %v", stdoutChunks)
	}
	if twoT == nil {
		t.Fatalf("2 not observed in stdout events: %v", stdoutChunks)
	}
	if twoT.Sub(*helloT) < 800*time.Millisecond {
		t.Fatalf("stdout did not behave like streaming; delta=%s chunks=%v", twoT.Sub(*helloT), stdoutChunks)
	}
}

