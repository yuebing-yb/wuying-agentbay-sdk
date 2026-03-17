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
		panic("AGENTBAY_API_KEY environment variable not set")
	}

	client, err := agentbay.NewAgentBay(apiKey, nil)
	if err != nil {
		panic(err)
	}

	created, err := client.Create(agentbay.NewCreateSessionParams())
	if err != nil {
		panic(err)
	}
	if created == nil || created.Session == nil {
		panic("create session returned nil session")
	}
	session := created.Session
	defer func() { _, _ = session.Delete(false) }()

	wsClientAny, err := session.GetWsClient()
	if err != nil {
		panic(err)
	}
	type wsPushClient interface {
		RegisterCallback(target string, callback func(payload map[string]interface{})) func()
		Close() error
	}
	wsClient, ok := wsClientAny.(wsPushClient)
	if !ok {
		panic(fmt.Errorf("unexpected ws client type: %T", wsClientAny))
	}
	defer func() { _ = wsClient.Close() }()

	pushCh := make(chan map[string]interface{}, 1)
	wsClient.RegisterCallback("wuying_cdp_mcp_server", func(payload map[string]interface{}) {
		select {
		case pushCh <- payload:
		default:
		}
	})

	opt := browser.NewBrowserOption()
	opt.UseStealth = true
	opt.SolveCaptchas = true
	initialized, err := session.Browser.Initialize(opt)
	if err != nil {
		panic(err)
	}
	if !initialized {
		panic("failed to initialize browser")
	}
	endpointURL, err := session.Browser.GetEndpointURL()
	if err != nil {
		panic(err)
	}

	pw, err := playwright.Run()
	if err != nil {
		panic(err)
	}
	defer func() { _ = pw.Stop() }()

	remote, err := pw.Chromium.ConnectOverCDP(endpointURL)
	if err != nil {
		panic(err)
	}
	defer func() { _ = remote.Close() }()

	ctxs := remote.Contexts()
	if len(ctxs) == 0 {
		panic("no browser contexts")
	}
	page, err := ctxs[0].NewPage()
	if err != nil {
		panic(err)
	}
	defer func() { _ = page.Close() }()

	_, err = page.Goto("https://passport.ly.com/Passport/GetPassword", playwright.PageGotoOptions{
		WaitUntil: playwright.WaitUntilStateDomcontentloaded,
	})
	if err != nil {
		panic(err)
	}
	input, err := page.WaitForSelector("#name_in", playwright.PageWaitForSelectorOptions{Timeout: playwright.Float(10000)})
	if err != nil {
		panic(err)
	}
	_ = input.Click()
	_ = input.Fill("")
	_ = input.Type("13000000000")
	page.WaitForTimeout(1000)
	_ = page.Click("#next_step1")

	fmt.Println("Waiting for backend push...")
	select {
	case payload := <-pushCh:
		fmt.Printf("WS PUSH: %v\n", payload)
	case <-time.After(180 * time.Second):
		panic("timeout waiting for ws push")
	}
}
