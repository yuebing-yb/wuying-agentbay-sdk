// ci-stable
package integration

import (
	"fmt"
	"io"
	"net/http"
	"os"
	"testing"
	"time"

	"github.com/aliyun/wuying-agentbay-sdk/golang/pkg/agentbay"
	"github.com/stretchr/testify/require"
)

func createTempFileWithZeros(sizeMB int) (string, error) {
	f, err := os.CreateTemp("", "agentbay-beta-wait-*.bin")
	if err != nil {
		return "", err
	}
	defer func() { _ = f.Close() }()

	chunk := make([]byte, 1024*1024)
	for i := 0; i < sizeMB; i++ {
		if _, err := f.Write(chunk); err != nil {
			_ = os.Remove(f.Name())
			return "", err
		}
	}
	return f.Name(), nil
}

func uploadFileWithRetries(t *testing.T, uploadURL, localPath string, maxAttempts int) {
	t.Helper()
	client := &http.Client{Timeout: 300 * time.Second}

	var lastErr error
	for attempt := 1; attempt <= maxAttempts; attempt++ {
		f, err := os.Open(localPath)
		if err != nil {
			lastErr = err
			break
		}

		req, err := http.NewRequest(http.MethodPut, uploadURL, f)
		if err != nil {
			_ = f.Close()
			lastErr = err
			break
		}

		resp, err := client.Do(req)
		_ = f.Close()
		if err == nil && resp != nil {
			_, _ = io.Copy(io.Discard, resp.Body)
			_ = resp.Body.Close()
		}
		if err == nil && resp != nil && (resp.StatusCode == 200 || resp.StatusCode == 204) {
			return
		}

		if err != nil {
			lastErr = err
		} else if resp != nil {
			lastErr = fmt.Errorf("upload failed: status=%d", resp.StatusCode)
		} else {
			lastErr = fmt.Errorf("upload failed: empty response")
		}

		if attempt < maxAttempts {
			time.Sleep(time.Duration(minInt(1<<attempt, 10)) * time.Second)
		}
	}
	require.NoError(t, lastErr, "Upload failed after retries")
}

func minInt(a, b int) int {
	if a < b {
		return a
	}
	return b
}

func assertDownloadTerminalSuccess(t *testing.T, s *agentbay.Session, contextID string, label string) {
	t.Helper()
	info, err := s.Context.InfoWithParams(contextID, "", "download")
	require.NoError(t, err, "%s: failed to get context info", label)
	require.True(t, info.Success, "%s: context info not success: %s", label, info.ErrorMessage)

	statuses := make([]string, 0)
	for _, it := range info.ContextStatusData {
		if it.ContextId == contextID {
			statuses = append(statuses, it.Status)
		}
	}
	require.NotEmpty(t, statuses, "%s: expected at least one download status entry", label)
	for _, st := range statuses {
		require.True(t, st == "Success" || st == "Failed", "%s: non-terminal status=%s", label, st)
		require.NotEqual(t, "Failed", st, "%s: download failed", label)
	}
}

func waitDownloadTerminalSuccess(t *testing.T, s *agentbay.Session, contextID string, timeout time.Duration) {
	t.Helper()
	deadline := time.Now().Add(timeout)
	var lastStatuses []string
	for time.Now().Before(deadline) {
		info, err := s.Context.InfoWithParams(contextID, "", "download")
		require.NoError(t, err)
		require.True(t, info.Success, "context info not success: %s", info.ErrorMessage)
		statuses := make([]string, 0)
		for _, it := range info.ContextStatusData {
			if it.ContextId == contextID {
				statuses = append(statuses, it.Status)
			}
		}
		if len(statuses) > 0 {
			lastStatuses = statuses
		}
		if len(statuses) > 0 {
			allTerminal := true
			for _, st := range statuses {
				if st != "Success" && st != "Failed" {
					allTerminal = false
					break
				}
			}
			if allTerminal {
				for _, st := range statuses {
					require.NotEqual(t, "Failed", st, "download failed: statuses=%v", statuses)
				}
				return
			}
		}
		time.Sleep(2 * time.Second)
	}
	require.Failf(t, "download did not complete", "lastStatuses=%v", lastStatuses)
}

func TestCreateSessionBetaWaitForCompletionFlagIntegration(t *testing.T) {
	apiKey := os.Getenv("AGENTBAY_API_KEY")
	if apiKey == "" || os.Getenv("CI") != "" {
		t.Skip("Skipping integration test: No API key available or running in CI")
	}

	ab, err := agentbay.NewAgentBay(apiKey)
	require.NoError(t, err)

	unique := time.Now().UnixNano()
	ctxName1 := fmt.Sprintf("test-beta-wait-flag-1-%d", unique)
	ctxName2 := fmt.Sprintf("test-beta-wait-flag-2-%d", unique)

	ctxRes1, err := ab.Context.Get(ctxName1, true)
	require.NoError(t, err)
	require.True(t, ctxRes1.Success)
	require.NotNil(t, ctxRes1.Context)

	ctxRes2, err := ab.Context.Get(ctxName2, true)
	require.NoError(t, err)
	require.True(t, ctxRes2.Success)
	require.NotNil(t, ctxRes2.Context)

	ctx1 := ctxRes1.Context
	ctx2 := ctxRes2.Context

	defer func() {
		_, _ = ab.Context.Delete(ctx1)
		_, _ = ab.Context.Delete(ctx2)
	}()

	mount1 := "/tmp/beta-wait-flag-1"
	mount2 := "/tmp/beta-wait-flag-2"
	sizeMB := 200

	tempPath, err := createTempFileWithZeros(sizeMB)
	require.NoError(t, err)
	defer func() { _ = os.Remove(tempPath) }()

	up1, err := ab.Context.GetFileUploadUrl(ctx1.ID, fmt.Sprintf("%s/large.bin", mount1))
	require.NoError(t, err)
	require.True(t, up1.Success)
	require.NotEmpty(t, up1.Url)
	uploadFileWithRetries(t, up1.Url, tempPath, 5)

	up2, err := ab.Context.GetFileUploadUrl(ctx2.ID, fmt.Sprintf("%s/large.bin", mount2))
	require.NoError(t, err)
	require.True(t, up2.Success)
	require.NotEmpty(t, up2.Url)
	uploadFileWithRetries(t, up2.Url, tempPath, 5)

	imageID := "linux_latest"

	waitBothParams := agentbay.NewCreateSessionParams().
		WithImageId(imageID).
		WithLabels(map[string]string{"test": "beta-wait-flag", "mode": "wait-both"}).
		WithContextSync([]*agentbay.ContextSync{
			{ContextID: ctx1.ID, Path: mount1, Policy: agentbay.NewSyncPolicy()},
			{ContextID: ctx2.ID, Path: mount2, Policy: agentbay.NewSyncPolicy()},
		})

	t0 := time.Now()
	waitBothRes, err := ab.Create(waitBothParams)
	tWaitBoth := time.Since(t0)
	require.NoError(t, err)
	require.True(t, waitBothRes.Success)
	require.NotNil(t, waitBothRes.Session)
	sessionWaitBoth := waitBothRes.Session
	defer func() { _, _ = sessionWaitBoth.Delete(false) }()
	assertDownloadTerminalSuccess(t, sessionWaitBoth, ctx1.ID, "wait-both ctx1")
	assertDownloadTerminalSuccess(t, sessionWaitBoth, ctx2.ID, "wait-both ctx2")

	waitOneParams := agentbay.NewCreateSessionParams().
		WithImageId(imageID).
		WithLabels(map[string]string{"test": "beta-wait-flag", "mode": "wait-one"}).
		WithContextSync([]*agentbay.ContextSync{
			{ContextID: ctx1.ID, Path: mount1, Policy: agentbay.NewSyncPolicy()},
			(&agentbay.ContextSync{ContextID: ctx2.ID, Path: mount2, Policy: agentbay.NewSyncPolicy()}).WithBetaWaitForCompletion(false),
		})

	t1 := time.Now()
	waitOneRes, err := ab.Create(waitOneParams)
	tWaitOne := time.Since(t1)
	require.NoError(t, err)
	require.True(t, waitOneRes.Success)
	require.NotNil(t, waitOneRes.Session)
	sessionWaitOne := waitOneRes.Session
	defer func() { _, _ = sessionWaitOne.Delete(false) }()
	assertDownloadTerminalSuccess(t, sessionWaitOne, ctx1.ID, "wait-one ctx1")
	waitDownloadTerminalSuccess(t, sessionWaitOne, ctx2.ID, 4*time.Minute)

	waitNoneParams := agentbay.NewCreateSessionParams().
		WithImageId(imageID).
		WithLabels(map[string]string{"test": "beta-wait-flag", "mode": "wait-none"}).
		WithContextSync([]*agentbay.ContextSync{
			(&agentbay.ContextSync{ContextID: ctx1.ID, Path: mount1, Policy: agentbay.NewSyncPolicy()}).WithBetaWaitForCompletion(false),
			(&agentbay.ContextSync{ContextID: ctx2.ID, Path: mount2, Policy: agentbay.NewSyncPolicy()}).WithBetaWaitForCompletion(false),
		})

	t2 := time.Now()
	waitNoneRes, err := ab.Create(waitNoneParams)
	tWaitNone := time.Since(t2)
	require.NoError(t, err)
	require.True(t, waitNoneRes.Success)
	require.NotNil(t, waitNoneRes.Session)
	sessionWaitNone := waitNoneRes.Session
	defer func() { _, _ = sessionWaitNone.Delete(false) }()
	waitDownloadTerminalSuccess(t, sessionWaitNone, ctx1.ID, 4*time.Minute)
	waitDownloadTerminalSuccess(t, sessionWaitNone, ctx2.ID, 4*time.Minute)

	t.Logf("Create() durations: wait-both=%s wait-one=%s wait-none=%s", tWaitBoth, tWaitOne, tWaitNone)
}
