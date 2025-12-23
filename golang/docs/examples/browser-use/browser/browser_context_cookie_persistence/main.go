package main

import (
	"fmt"
	"os"
	"time"

	"github.com/aliyun/wuying-agentbay-sdk/golang/pkg/agentbay"
	"github.com/aliyun/wuying-agentbay-sdk/golang/pkg/agentbay/browser"
	"github.com/playwright-community/playwright-go"
)

func main() {
	apiKey := os.Getenv("AGENTBAY_API_KEY")
	if apiKey == "" {
		fmt.Println("Error: AGENTBAY_API_KEY environment variable not set")
		return
	}

	agentBay, err := agentbay.NewAgentBay(apiKey)
	if err != nil {
		fmt.Printf("Failed to create AgentBay client: %v\n", err)
		return
	}

	// Create a unique cloud context for browser persistence
	contextName := fmt.Sprintf("go-browser-cookie-demo-%d", time.Now().Unix())
	ctxResult, err := agentBay.Context.Get(contextName, true)
	if err != nil || ctxResult == nil || !ctxResult.Success || ctxResult.Context == nil {
		fmt.Printf("Failed to create context: %v\n", err)
		return
	}
	ctx := ctxResult.Context
	fmt.Printf("Context created: %s (ID=%s)\n", ctx.Name, ctx.ID)
	defer func() {
		_, _ = agentBay.Context.Delete(ctx)
	}()

	pw, err := playwright.Run()
	if err != nil {
		fmt.Printf("Failed to start Playwright: %v\n", err)
		return
	}
	defer func() {
		_ = pw.Stop()
	}()

	testDomain := "aliyun.com"
	testURL := "https://www.aliyun.com"
	testCookies := []playwright.OptionalCookie{
		{
			Name:     "demo_cookie_1",
			Value:    "demo_value_1",
			Domain:   playwright.String(testDomain),
			Path:     playwright.String("/"),
			HttpOnly: playwright.Bool(false),
			Secure:   playwright.Bool(false),
			Expires:  playwright.Float(float64(time.Now().Add(1 * time.Hour).Unix())),
		},
		{
			Name:     "demo_cookie_2",
			Value:    "demo_value_2",
			Domain:   playwright.String(testDomain),
			Path:     playwright.String("/"),
			HttpOnly: playwright.Bool(false),
			Secure:   playwright.Bool(false),
			Expires:  playwright.Float(float64(time.Now().Add(1 * time.Hour).Unix())),
		},
	}

	params := agentbay.NewCreateSessionParams().
		WithImageId("browser_latest").
		WithBrowserContext(agentbay.NewBrowserContext(ctx.ID).WithAutoUpload(true))

	fmt.Println("Creating first session with BrowserContext...")
	s1Result, err := agentBay.Create(params)
	if err != nil || s1Result == nil || !s1Result.Success || s1Result.Session == nil {
		fmt.Printf("Failed to create first session: %v\n", err)
		return
	}
	s1 := s1Result.Session

	fmt.Printf("First session created: %s\n", s1.SessionID)

	fmt.Println("Initializing browser and setting cookies...")
	ok, err := s1.Browser.Initialize(browser.NewBrowserOption())
	if err != nil || !ok {
		fmt.Printf("Failed to initialize browser: %v\n", err)
		_, _ = agentBay.Delete(s1, false)
		return
	}

	endpoint, err := s1.Browser.GetEndpointURL()
	if err != nil || endpoint == "" {
		fmt.Printf("Failed to get endpoint URL: %v\n", err)
		_, _ = agentBay.Delete(s1, false)
		return
	}

	remoteBrowser, err := pw.Chromium.ConnectOverCDP(endpoint)
	if err != nil {
		fmt.Printf("Failed to connect over CDP: %v\n", err)
		_, _ = agentBay.Delete(s1, false)
		return
	}

	func() {
		defer func() {
			_ = remoteBrowser.Close()
		}()

		pwCtx := remoteBrowser.Contexts()[0]
		page, err := pwCtx.NewPage()
		if err != nil {
			fmt.Printf("Failed to create page: %v\n", err)
			return
		}
		defer func() {
			_ = page.Close()
		}()

		_, err = page.Goto(testURL, playwright.PageGotoOptions{Timeout: playwright.Float(60000)})
		if err != nil {
			fmt.Printf("Failed to navigate: %v\n", err)
			return
		}

		err = pwCtx.AddCookies(testCookies)
		if err != nil {
			fmt.Printf("Failed to add cookies: %v\n", err)
			return
		}

		fmt.Println("Cookies added. Waiting for flush...")
		time.Sleep(2 * time.Second)
	}()

	_ = s1.Browser.Destroy()

	fmt.Println("Deleting first session with sync_context=true...")
	_, _ = agentBay.Delete(s1, true)

	time.Sleep(3 * time.Second)

	fmt.Println("Creating second session with same BrowserContext...")
	s2Result, err := agentBay.Create(params)
	if err != nil || s2Result == nil || !s2Result.Success || s2Result.Session == nil {
		fmt.Printf("Failed to create second session: %v\n", err)
		return
	}
	s2 := s2Result.Session
	defer func() {
		_, _ = agentBay.Delete(s2, true)
	}()

	ok, err = s2.Browser.Initialize(browser.NewBrowserOption())
	if err != nil || !ok {
		fmt.Printf("Failed to initialize browser in second session: %v\n", err)
		return
	}

	endpoint2, err := s2.Browser.GetEndpointURL()
	if err != nil || endpoint2 == "" {
		fmt.Printf("Failed to get endpoint URL (2nd session): %v\n", err)
		return
	}

	remoteBrowser2, err := pw.Chromium.ConnectOverCDP(endpoint2)
	if err != nil {
		fmt.Printf("Failed to connect over CDP (2nd session): %v\n", err)
		return
	}
	defer func() {
		_ = remoteBrowser2.Close()
	}()

	pwCtx2 := remoteBrowser2.Contexts()[0]
	cookies, err := pwCtx2.Cookies()
	if err != nil {
		fmt.Printf("Failed to read cookies: %v\n", err)
		return
	}

	found := map[string]string{}
	for _, c := range cookies {
		found[c.Name] = c.Value
	}

	fmt.Printf("Cookie demo_cookie_1=%s\n", found["demo_cookie_1"])
	fmt.Printf("Cookie demo_cookie_2=%s\n", found["demo_cookie_2"])
	fmt.Println("Done.")
}


