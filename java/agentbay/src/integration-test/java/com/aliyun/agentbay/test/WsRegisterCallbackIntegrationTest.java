package com.aliyun.agentbay.test;

import com.aliyun.agentbay.AgentBay;
import com.aliyun.agentbay._internal.WsClient;
import com.aliyun.agentbay.browser.BrowserOption;
import com.aliyun.agentbay.model.SessionResult;
import com.aliyun.agentbay.session.CreateSessionParams;
import com.aliyun.agentbay.session.Session;
import com.microsoft.playwright.Browser;
import com.microsoft.playwright.Page;
import com.microsoft.playwright.Playwright;
import org.junit.AfterClass;
import org.junit.Assume;
import org.junit.BeforeClass;
import org.junit.Test;

import java.util.ArrayList;
import java.util.List;
import java.util.Map;
import java.util.concurrent.CountDownLatch;
import java.util.concurrent.TimeUnit;

import static org.junit.Assert.*;

public class WsRegisterCallbackIntegrationTest {
    private static AgentBay agentBay;
    private static Session session;

    @BeforeClass
    public static void setUp() throws Exception {
        String apiKey = System.getenv("AGENTBAY_API_KEY");
        Assume.assumeTrue(apiKey != null && !apiKey.isEmpty());

        agentBay = new AgentBay(apiKey);

        CreateSessionParams params = new CreateSessionParams();
        SessionResult created = agentBay.create(params);
        assertTrue("Failed to create session: " + created.getErrorMessage(), created.isSuccess());
        session = created.getSession();
        assertNotNull(session);
        assertNotNull("wsUrl should not be empty", session.getWsUrl());
        assertTrue("wsUrl should not be empty", !session.getWsUrl().isEmpty());
    }

    @AfterClass
    public static void tearDown() {
        if (session != null && agentBay != null) {
            try {
                agentBay.delete(session, false);
            } catch (Exception e) {
                System.err.println("Cleanup error: " + e.getMessage());
            }
        }
    }

    @Test
    public void testWsRegisterCallbackShouldReceiveCaptchaPushE2E() throws Exception {
        WsClient wsClient = session.getWsClient();
        assertNotNull(wsClient);

        CountDownLatch latch = new CountDownLatch(1);
        List<Map<String, Object>> received = new ArrayList<>();
        wsClient.registerCallback("wuying_cdp_mcp_server", payload -> {
            received.add(payload);
            latch.countDown();
        });

        BrowserOption option = new BrowserOption();
        option.setUseStealth(true);
        option.setSolveCaptchas(true);
        boolean ok = session.getBrowser().initialize(option);
        assertTrue("Failed to initialize browser", ok);

        String endpointUrl = session.getBrowser().getEndpointUrl();
        assertNotNull(endpointUrl);
        assertTrue(endpointUrl.startsWith("ws://") || endpointUrl.startsWith("wss://"));

        try (Playwright playwright = Playwright.create()) {
            Browser browser = playwright.chromium().connectOverCDP(endpointUrl);
            Page page = browser.contexts().get(0).newPage();
            page.navigate("https://passport.ly.com/Passport/GetPassword");
            page.waitForSelector("#name_in").fill("13000000000");
            page.waitForTimeout(1000);
            page.click("#next_step1");

            boolean got = latch.await(180, TimeUnit.SECONDS);
            assertTrue("Timeout waiting for WS push callback", got);
        }

        assertFalse("Expected at least one push message", received.isEmpty());
        Map<String, Object> first = received.get(0);
        assertEquals("wuying_cdp_mcp_server", first.get("target"));
        assertNotNull(first.get("requestId"));
        Object dataObj = first.get("data");
        assertTrue("payload.data should be an object", dataObj instanceof Map);
        Map<?, ?> data = (Map<?, ?>) dataObj;
        Object code = data.get("code");
        assertTrue("unexpected data.code: " + code, code != null && (Integer.valueOf(201).equals(code) || Integer.valueOf(202).equals(code)));
    }
}

