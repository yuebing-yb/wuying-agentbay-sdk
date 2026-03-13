package integration

import (
	"os"
	"testing"
	"time"

	"github.com/aliyun/wuying-agentbay-sdk/golang/pkg/agentbay"
	"github.com/aliyun/wuying-agentbay-sdk/golang/pkg/agentbay/browser"
	"github.com/playwright-community/playwright-go"
)

func TestWsRegisterCallback_ShouldReceiveCaptchaPush(t *testing.T) {
	apiKey := os.Getenv("AGENTBAY_API_KEY")
	if apiKey == "" {
		t.Skip("AGENTBAY_API_KEY environment variable not set")
	}

	client, err := agentbay.NewAgentBay(apiKey, nil)
	if err != nil {
		t.Fatalf("new agentbay: %v", err)
	}

	created, err := client.Create(agentbay.NewCreateSessionParams())
	if err != nil {
		t.Fatalf("create session: %v", err)
	}
	if created == nil || created.Session == nil {
		t.Fatalf("create session returned nil session")
	}
	session := created.Session
	defer func() { _, _ = session.Delete(false) }()

	wsClientAny, err := session.GetWsClient()
	if err != nil {
		t.Fatalf("get ws client: %v", err)
	}
	type wsPushClient interface {
		RegisterCallback(target string, callback func(payload map[string]interface{})) func()
		Close() error
	}
	wsClient, ok := wsClientAny.(wsPushClient)
	if !ok {
		t.Fatalf("unexpected ws client type: %T", wsClientAny)
	}
	defer func() { _ = wsClient.Close() }()

	gotCh := make(chan map[string]interface{}, 1)
	wsClient.RegisterCallback("wuying_cdp_mcp_server", func(payload map[string]interface{}) {
		select {
		case gotCh <- payload:
		default:
		}
	})

	opt := browser.NewBrowserOption()
	opt.UseStealth = true
	opt.SolveCaptchas = true
	initialized, err := session.Browser.Initialize(opt)
	if err != nil {
		t.Fatalf("init browser: %v", err)
	}
	if !initialized {
		t.Fatalf("init browser returned false")
	}
	endpointURL, err := session.Browser.GetEndpointURL()
	if err != nil {
		t.Fatalf("get endpoint url: %v", err)
	}

	pw, err := playwright.Run()
	if err != nil {
		t.Fatalf("playwright run: %v", err)
	}
	defer func() { _ = pw.Stop() }()

	remote, err := pw.Chromium.ConnectOverCDP(endpointURL)
	if err != nil {
		t.Fatalf("connect over cdp: %v", err)
	}
	defer func() { _ = remote.Close() }()

	ctxs := remote.Contexts()
	if len(ctxs) == 0 {
		t.Fatalf("no browser contexts")
	}
	page, err := ctxs[0].NewPage()
	if err != nil {
		t.Fatalf("new page: %v", err)
	}
	defer func() { _ = page.Close() }()

	_, err = page.Goto("https://passport.ly.com/Passport/GetPassword", playwright.PageGotoOptions{
		WaitUntil: playwright.WaitUntilStateDomcontentloaded,
	})
	if err != nil {
		t.Fatalf("goto: %v", err)
	}
	input, err := page.WaitForSelector("#name_in", playwright.PageWaitForSelectorOptions{Timeout: playwright.Float(10000)})
	if err != nil {
		t.Fatalf("wait selector: %v", err)
	}
	_ = input.Click()
	_ = input.Fill("")
	_ = input.Type("13000000000")
	page.WaitForTimeout(1000)
	_ = page.Click("#next_step1")

	select {
	case payload := <-gotCh:
		if payload == nil {
			t.Fatalf("nil payload")
		}
		if payload["target"] != "wuying_cdp_mcp_server" {
			t.Fatalf("unexpected payload target: %v", payload["target"])
		}
		data, _ := payload["data"].(map[string]interface{})
		if data == nil {
			t.Fatalf("payload.data is not object: %v", payload["data"])
		}
		codeAny := data["code"]
		code, _ := codeAny.(float64)
		if code != 201 && code != 202 {
			t.Fatalf("unexpected data.code: %v", codeAny)
		}
	case <-time.After(180 * time.Second):
		t.Fatalf("timeout waiting for ws push")
	}
}
