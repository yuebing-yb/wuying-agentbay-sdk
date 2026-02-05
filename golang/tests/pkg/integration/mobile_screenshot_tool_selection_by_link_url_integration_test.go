package integration_test

import (
	"strings"
	"testing"

	"github.com/aliyun/wuying-agentbay-sdk/golang/pkg/agentbay"
	"github.com/aliyun/wuying-agentbay-sdk/golang/tests/pkg/agentbay/testutil"
)

const (
	mobileLinkUrlEndpoint = "agentbay-pre.cn-hangzhou.aliyuncs.com"
	mobileLinkUrlImageID  = "mobile-use-android-12-gw"

	mobileNoLinkUrlEndpoint = "wuyingai-pre.cn-hangzhou.aliyuncs.com"
	mobileNoLinkUrlImageID  = "mobile_latest"
)

func TestMobileLinkUrlPresentRequiresBetaTakeScreenshot(t *testing.T) {
	apiKey := testutil.GetTestAPIKey(t)
	client := newAgentBayWithEndpoint(t, apiKey, mobileLinkUrlEndpoint)

	params := agentbay.NewCreateSessionParams().WithImageId(mobileLinkUrlImageID)
	createResult, err := client.Create(params)
	if err != nil {
		t.Fatalf("Error creating session: %v", err)
	}
	session := createResult.Session
	defer func() {
		_, _ = client.Delete(session)
	}()

	if session.GetLinkUrl() == "" {
		t.Fatalf("Expected session.LinkUrl to be non-empty for this endpoint/image")
	}

	r := session.Mobile.Screenshot()
	if r == nil {
		t.Fatalf("Mobile.Screenshot returned nil")
	}
	if r.ErrorMessage == "" {
		t.Fatalf("Expected screenshot() to fail when LinkUrl is present")
	}
	if !strings.Contains(r.ErrorMessage, "does not support `screenshot()`") || !strings.Contains(r.ErrorMessage, "beta_take_screenshot") {
		t.Fatalf("Unexpected screenshot() error message: %q", r.ErrorMessage)
	}

	beta := session.Mobile.BetaTakeScreenshot()
	if beta == nil {
		t.Fatalf("Mobile.BetaTakeScreenshot returned nil")
	}
	if !beta.Success {
		t.Fatalf("beta_take_screenshot failed: %s", beta.ErrorMessage)
	}
	if beta.Type != "image" {
		t.Fatalf("Unexpected type: %q", beta.Type)
	}
	if beta.MimeType != "image/png" {
		t.Fatalf("Unexpected mime_type: %q", beta.MimeType)
	}
	if beta.Width == nil || beta.Height == nil || *beta.Width <= 0 || *beta.Height <= 0 {
		t.Fatalf("Unexpected dimensions: width=%v height=%v", beta.Width, beta.Height)
	}
	if len(beta.Data) == 0 {
		t.Fatalf("Expected non-empty screenshot bytes")
	}
	pngMagic := []byte{0x89, 0x50, 0x4e, 0x47, 0x0d, 0x0a, 0x1a, 0x0a}
	if len(beta.Data) < len(pngMagic) {
		t.Fatalf("Screenshot bytes too short: %d", len(beta.Data))
	}
	ok := true
	for i := 0; i < len(pngMagic); i++ {
		if beta.Data[i] != pngMagic[i] {
			ok = false
			break
		}
	}
	if !ok {
		t.Fatalf("Screenshot bytes do not look like PNG")
	}
}

func TestMobileLinkUrlAbsentRequiresScreenshot(t *testing.T) {
	apiKey := testutil.GetTestAPIKey(t)
	client := newAgentBayWithEndpoint(t, apiKey, mobileNoLinkUrlEndpoint)

	params := agentbay.NewCreateSessionParams().WithImageId(mobileNoLinkUrlImageID)
	createResult, err := client.Create(params)
	if err != nil {
		t.Fatalf("Error creating session: %v", err)
	}
	session := createResult.Session
	defer func() {
		_, _ = client.Delete(session)
	}()

	if session.GetLinkUrl() != "" {
		t.Fatalf("Expected session.LinkUrl to be empty for this endpoint/image, got: %q", session.GetLinkUrl())
	}

	r := session.Mobile.Screenshot()
	if r == nil {
		t.Fatalf("Mobile.Screenshot returned nil")
	}
	if r.ErrorMessage != "" {
		t.Fatalf("Screenshot failed: %s", r.ErrorMessage)
	}
	if strings.TrimSpace(r.Data) == "" {
		t.Fatalf("Expected non-empty screenshot URL")
	}

	beta := session.Mobile.BetaTakeScreenshot()
	if beta == nil {
		t.Fatalf("Mobile.BetaTakeScreenshot returned nil")
	}
	if beta.Success {
		t.Fatalf("Expected beta_take_screenshot to fail when LinkUrl is absent")
	}
	if !strings.Contains(beta.ErrorMessage, "does not support `beta_take_screenshot()`") {
		t.Fatalf("Unexpected beta_take_screenshot error message: %q", beta.ErrorMessage)
	}
}
