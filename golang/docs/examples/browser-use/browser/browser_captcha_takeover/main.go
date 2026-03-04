package main

import (
	"fmt"
	"os"
	"sync"
	"time"

	"github.com/aliyun/wuying-agentbay-sdk/golang/pkg/agentbay"
	agentbaybrowser "github.com/aliyun/wuying-agentbay-sdk/golang/pkg/agentbay/browser"
	"github.com/playwright-community/playwright-go"
)

// Event implements a simple event mechanism similar to asyncio.Event
type Event struct {
	mu    sync.Mutex
	cond  *sync.Cond
	isSet bool
}

func NewEvent() *Event {
	e := &Event{}
	e.cond = sync.NewCond(&e.mu)
	return e
}

func (e *Event) Set() {
	e.mu.Lock()
	defer e.mu.Unlock()
	e.isSet = true
	e.cond.Broadcast()
}

func (e *Event) Wait(timeout time.Duration) bool {
	e.mu.Lock()
	defer e.mu.Unlock()

	if e.isSet {
		return true
	}

	done := make(chan struct{})
	go func() {
		e.mu.Lock()
		e.cond.Wait()
		e.mu.Unlock()
		close(done)
	}()

	select {
	case <-done:
		return true
	case <-time.After(timeout):
		return false
	}
}

var (
	captchaSolvedSuccess    = false
	shouldTakeover          = false
	takeoverNotifyID        *int
	maxCaptchaDetectTimeout = 5.0
	maxTakeoverTimeout      = 180.0
	captchaDetectEvent      = NewEvent()
	mu                      sync.Mutex
)

func onBrowserCallback(msg *agentbaybrowser.BrowserNotifyMessage) {
	fmt.Printf("on_browser_callback: %v, %v, %v, %v, %v, %v\n",
		msg.Type, msg.ID, msg.Code, msg.Message, msg.Action, msg.ExtraParams)

	if msg.Type != nil && *msg.Type == "call-for-user" {
		action := msg.Action
		extraParams := msg.ExtraParams

		if action != nil && *action == "takeover" {
			mu.Lock()
			shouldTakeover = true
			takeoverNotifyID = msg.ID
			if waitTime, ok := extraParams["max_wait_time"].(float64); ok {
				maxTakeoverTimeout = waitTime
			}
			mu.Unlock()

			fmt.Printf("Captcha takeover notification received, notify_id: %v, max wait time: %.1fs\n",
				takeoverNotifyID, maxTakeoverTimeout)
			captchaDetectEvent.Set()
		}
	}
}

func main() {
	apiKey := os.Getenv("AGENTBAY_API_KEY")
	if apiKey == "" {
		fmt.Println("Error: AGENTBAY_API_KEY environment variable is required")
		return
	}

	client, err := agentbay.NewAgentBay(apiKey)
	if err != nil {
		fmt.Printf("Failed to create AgentBay client: %v\n", err)
		return
	}

	params := &agentbay.CreateSessionParams{
		ImageId: "browser_latest",
	}
	sessionResult, err := client.Create(params)
	if err != nil {
		fmt.Printf("Failed to create session: %v\n", err)
		return
	}

	if !sessionResult.Success || sessionResult.Session == nil {
		fmt.Println("Failed to create session")
		return
	}

	session := sessionResult.Session
	takeoverURL := session.ResourceUrl
	defer func() {
		fmt.Println("🗑️ Deleting session")
		client.Delete(session)
	}()

	_, err = session.Browser.RegisterCallback(onBrowserCallback)
	if err != nil {
		fmt.Printf("Failed to register callback: %v\n", err)
		return
	}

	browserOption := agentbaybrowser.NewBrowserOption()
	browserOption.UseStealth = true
	browserOption.SolveCaptchas = false
	browserOption.CallForUser = true

	initialized, err := session.Browser.Initialize(browserOption)
	if err != nil || !initialized {
		fmt.Printf("Failed to initialize browser: %v\n", err)
		return
	}

	endpointURL, err := session.Browser.GetEndpointURL()
	if err != nil {
		fmt.Printf("Failed to get endpoint URL: %v\n", err)
		return
	}
	fmt.Printf("🌐 Browser endpoint URL: %s\n", endpointURL)

	time.Sleep(2 * time.Second)

	pw, err := playwright.Run()
	if err != nil {
		fmt.Printf("Failed to start playwright: %v\n", err)
		return
	}
	defer pw.Stop()

	browserInstance, err := pw.Chromium.ConnectOverCDP(endpointURL)
	if err != nil {
		fmt.Printf("Failed to connect to browser: %v\n", err)
		return
	}

	contexts := browserInstance.Contexts()
	if len(contexts) == 0 {
		fmt.Println("No browser contexts available")
		return
	}

	page, err := contexts[0].NewPage()
	if err != nil {
		fmt.Printf("Failed to create new page: %v\n", err)
		return
	}

	fmt.Println("🚀 Navigating to jd.com...")
	_, err = page.Goto("https://aq.jd.com/process/findPwd?s=1")
	if err != nil {
		fmt.Printf("Failed to navigate: %v\n", err)
		return
	}

	fmt.Println("📱 fill phone number...")
	err = page.Fill("input.field[placeholder=\"请输入账号名/邮箱/已验证手机号\"]", "13000000000")
	if err != nil {
		fmt.Printf("Failed to fill phone number: %v\n", err)
		return
	}
	time.Sleep(2 * time.Second)

	fmt.Println("🖱️ click next step button...")
	err = page.Click("button.btn-check-defaut.btn-xl")
	if err != nil {
		fmt.Printf("Failed to click button: %v\n", err)
		return
	}
	fmt.Println("🔑 Captcha triggered, waiting for takeover notification...")

	detected := captchaDetectEvent.Wait(time.Duration(maxCaptchaDetectTimeout * float64(time.Second)))

	if !detected {
		fmt.Println("⏰ No captcha detected within timeout, continuing...")
	} else {
		mu.Lock()
		takeover := shouldTakeover
		mu.Unlock()

		if takeover {
			fmt.Println("⏰ Captcha should takeover...")
			fmt.Println("🌍 Please manually take over the task by URL: ", takeoverURL)

			mu.Lock()
			timeout := maxTakeoverTimeout
			mu.Unlock()

			fmt.Printf("Waiting for user task over completed or timeout, timeout: %.1fs\n", timeout)
			time.Sleep(time.Duration(timeout * float64(time.Second)))

			mu.Lock()
			notifyID := takeoverNotifyID
			mu.Unlock()

			if notifyID != nil {
				_, _ = session.Browser.SendTakeoverDone(*notifyID)
			}
			fmt.Println("✅ User task over completed...")
		} else {
			fmt.Println("✅ Captcha solved...")
		}
	}

	fmt.Println("📸 Taking screenshot...")
	_, err = page.Screenshot(playwright.PageScreenshotOptions{
		Path: playwright.String("captcha.png"),
	})
	if err != nil {
		fmt.Printf("Failed to take screenshot: %v\n", err)
	} else {
		fmt.Println("✅ Screenshot taken...")
	}

	fmt.Println("🔍 Checking for authentication success...")
	successButton, err := page.WaitForSelector("button.btn-check-succ:has-text(\"认证成功\")", playwright.PageWaitForSelectorOptions{
		Timeout: playwright.Float(5000),
	})

	if err == nil && successButton != nil {
		fmt.Println("✅ Authentication successful - '认证成功' button found!")
		_, _ = page.Screenshot(playwright.PageScreenshotOptions{
			Path: playwright.String("captcha_solving.png"),
		})
	} else {
		fmt.Printf("⚠️ Could not find authentication success button: %v\n", err)
	}

	time.Sleep(10 * time.Second)

	_ = session.Browser.UnregisterCallback()
}
