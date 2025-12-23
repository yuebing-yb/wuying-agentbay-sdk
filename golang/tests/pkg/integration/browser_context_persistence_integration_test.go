package integration

import (
	"fmt"
	"os"
	"strings"
	"testing"
	"time"

	"github.com/aliyun/wuying-agentbay-sdk/golang/pkg/agentbay"
	"github.com/aliyun/wuying-agentbay-sdk/golang/pkg/agentbay/browser"
	"github.com/playwright-community/playwright-go"
	"github.com/stretchr/testify/require"
)

func connectOverCDPWithRetry(pw *playwright.Playwright, endpoint string, maxRetries int) (playwright.Browser, error) {
	var lastErr error
	for i := 0; i < maxRetries; i++ {
		b, err := pw.Chromium.ConnectOverCDP(endpoint)
		if err == nil {
			return b, nil
		}
		lastErr = err

		// Transient network/proxy readiness issues sometimes surface as EBADF.
		errStr := err.Error()
		if strings.Contains(errStr, "EBADF") || strings.Contains(errStr, "ECONNREFUSED") || strings.Contains(errStr, "ETIMEDOUT") {
			time.Sleep(1200 * time.Millisecond)
			continue
		}
		return nil, err
	}
	return nil, lastErr
}

func TestBrowserContext_CookiePersistence_Integration(t *testing.T) {
	apiKey := os.Getenv("AGENTBAY_API_KEY")
	if apiKey == "" {
		t.Skip("Skipping integration test: AGENTBAY_API_KEY not set")
	}
	if os.Getenv("CI") != "" {
		t.Skip("Skipping integration test in CI")
	}

	agentBay, err := agentbay.NewAgentBay(apiKey)
	require.NoError(t, err)

	// Create a unique cloud context for browser persistence
	contextName := fmt.Sprintf("go-browser-context-%d", time.Now().Unix())
	ctxResult, err := agentBay.Context.Get(contextName, true)
	require.NoError(t, err)
	require.NotNil(t, ctxResult)
	require.True(t, ctxResult.Success)
	require.NotNil(t, ctxResult.Context)

	ctx := ctxResult.Context
	t.Logf("Created context: %s (ID=%s)", ctx.Name, ctx.ID)
	defer func() {
		_, _ = agentBay.Context.Delete(ctx)
	}()

	// Start Playwright once for this test
	pw, err := playwright.Run()
	require.NoError(t, err)
	defer func() {
		_ = pw.Stop()
	}()

	testDomain := "baidu.com"
	testURL := "https://www.baidu.com"
	testCookies := []playwright.OptionalCookie{
		{
			Name:     "myCookie",
			Value:    "cookieValue",
			Domain:   playwright.String(testDomain),
			Path:     playwright.String("/"),
			HttpOnly: playwright.Bool(false),
			Secure:   playwright.Bool(false),
			Expires:  playwright.Float(float64(time.Now().Add(1 * time.Hour).Unix())),
		},
		{
			Name:     "test_cookie_2",
			Value:    "test_value_2",
			Domain:   playwright.String(testDomain),
			Path:     playwright.String("/"),
			HttpOnly: playwright.Bool(false),
			Secure:   playwright.Bool(false),
			Expires:  playwright.Float(float64(time.Now().Add(1 * time.Hour).Unix())),
		},
	}

	// Session #1: set cookies
	params := agentbay.NewCreateSessionParams().
		WithImageId("browser_latest").
		WithBrowserContext(agentbay.NewBrowserContext(ctx.ID).WithAutoUpload(true))

	s1Result, err := agentBay.Create(params)
	require.NoError(t, err)
	require.True(t, s1Result.Success)
	require.NotNil(t, s1Result.Session)
	s1 := s1Result.Session

	func() {
		defer func() {
			_, _ = agentBay.Delete(s1, true)
		}()

		ok, err := s1.Browser.Initialize(browser.NewBrowserOption())
		require.NoError(t, err)
		require.True(t, ok)

		endpoint, err := s1.Browser.GetEndpointURL()
		require.NoError(t, err)
		require.NotEmpty(t, endpoint)

		remoteBrowser, err := connectOverCDPWithRetry(pw, endpoint, 5)
		require.NoError(t, err)
		defer func() {
			_ = remoteBrowser.Close()
		}()

		pwCtx := remoteBrowser.Contexts()[0]
		page, err := pwCtx.NewPage()
		require.NoError(t, err)
		defer func() {
			_ = page.Close()
		}()

		_, err = page.Goto(testURL, playwright.PageGotoOptions{Timeout: playwright.Float(60000)})
		require.NoError(t, err)

		// Add cookies after navigating (required by Chromium)
		err = pwCtx.AddCookies(testCookies)
		require.NoError(t, err)

		// Give Chromium a moment to flush to disk
		time.Sleep(2 * time.Second)

		// Stop chrome explicitly to ensure persistence on disk before sync/upload
		_ = s1.Browser.Destroy()
	}()

	// Wait for sync completion on backend side
	time.Sleep(3 * time.Second)

	// Session #2: verify cookies persisted
	s2Result, err := agentBay.Create(params)
	require.NoError(t, err)
	require.True(t, s2Result.Success)
	require.NotNil(t, s2Result.Session)
	s2 := s2Result.Session
	defer func() {
		_, _ = agentBay.Delete(s2, true)
	}()

	ok, err := s2.Browser.Initialize(browser.NewBrowserOption())
	require.NoError(t, err)
	require.True(t, ok)

	endpoint2, err := s2.Browser.GetEndpointURL()
	require.NoError(t, err)
	require.NotEmpty(t, endpoint2)

	remoteBrowser2, err := connectOverCDPWithRetry(pw, endpoint2, 5)
	require.NoError(t, err)
	defer func() {
		_ = remoteBrowser2.Close()
	}()

	pwCtx2 := remoteBrowser2.Contexts()[0]
	cookies, err := pwCtx2.Cookies()
	require.NoError(t, err)

	cookieMap := map[string]string{}
	for _, c := range cookies {
		cookieMap[c.Name] = c.Value
	}

	require.Equal(t, "cookieValue", cookieMap["myCookie"])
	require.Equal(t, "test_value_2", cookieMap["test_cookie_2"])
}
