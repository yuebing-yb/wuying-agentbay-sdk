package com.aliyun.agentbay.examples;

import com.aliyun.agentbay.AgentBay;
import com.aliyun.agentbay._internal.WsClient;
import com.aliyun.agentbay.browser.BrowserOption;
import com.aliyun.agentbay.model.SessionResult;
import com.aliyun.agentbay.session.CreateSessionParams;
import com.aliyun.agentbay.session.Session;
import com.microsoft.playwright.Browser;
import com.microsoft.playwright.Page;
import com.microsoft.playwright.Playwright;

import java.util.Map;
import java.util.concurrent.CountDownLatch;
import java.util.concurrent.TimeUnit;

/**
 * Example demonstrating how to receive backend push notifications via Session WS.
 *
 * It will:
 * - Create a browser session
 * - Connect to the session WS client
 * - Register a callback for target wuying_cdp_mcp_server
 * - Trigger a captcha flow on Tongcheng and wait for a backend push message
 */
public class WsPushCallbackCaptchaTongchengExample {
    public static void main(String[] args) throws Exception {
        String apiKey = System.getenv("AGENTBAY_API_KEY");
        if (apiKey == null || apiKey.isEmpty()) {
            throw new RuntimeException("AGENTBAY_API_KEY environment variable not set");
        }

        String imageId = System.getenv("AGENTBAY_WS_IMAGE_ID");
        if (imageId == null || imageId.isEmpty()) {
            imageId = "imgc-0ab5ta4kuo0x3pa70";
        }

        AgentBay agentBay = new AgentBay(apiKey);
        Session session = null;
        try {
            CreateSessionParams params = new CreateSessionParams();
            params.setImageId(imageId);
            SessionResult created = agentBay.create(params);
            if (!created.isSuccess() || created.getSession() == null) {
                throw new RuntimeException("Failed to create session: " + created.getErrorMessage());
            }
            session = created.getSession();

            WsClient wsClient = session.getWsClient();
            CountDownLatch latch = new CountDownLatch(1);
            wsClient.registerCallback("wuying_cdp_mcp_server", (Map<String, Object> payload) -> {
                System.out.println("WS PUSH: " + payload);
                latch.countDown();
            });

            BrowserOption option = new BrowserOption();
            option.setUseStealth(true);
            option.setSolveCaptchas(true);
            boolean ok = session.getBrowser().initialize(option);
            if (!ok) {
                throw new RuntimeException("Failed to initialize browser");
            }

            String endpointUrl = session.getBrowser().getEndpointUrl();
            try (Playwright playwright = Playwright.create()) {
                Browser browser = playwright.chromium().connectOverCDP(endpointUrl);
                Page page = browser.contexts().get(0).newPage();
                page.navigate("https://passport.ly.com/Passport/GetPassword");
                page.waitForSelector("#name_in").fill("13000000000");
                page.waitForTimeout(1000);
                page.click("#next_step1");

                System.out.println("Waiting for backend push...");
                boolean got = latch.await(180, TimeUnit.SECONDS);
                if (!got) {
                    throw new RuntimeException("Timeout waiting for WS push callback");
                }
                System.out.println("Received backend push.");
            }
        } finally {
            if (session != null) {
                agentBay.delete(session, false);
            }
        }
    }
}

