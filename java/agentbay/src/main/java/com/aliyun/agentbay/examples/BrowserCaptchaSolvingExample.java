package com.aliyun.agentbay.examples;

import com.aliyun.agentbay.AgentBay;
import com.aliyun.agentbay.browser.BrowserCallback;
import com.aliyun.agentbay.browser.BrowserNotifyMessage;
import com.aliyun.agentbay.browser.BrowserOption;
import com.aliyun.agentbay.model.SessionResult;
import com.aliyun.agentbay.session.CreateSessionParams;
import com.aliyun.agentbay.session.Session;
import com.microsoft.playwright.Browser;
import com.microsoft.playwright.BrowserContext;
import com.microsoft.playwright.Page;
import com.microsoft.playwright.Playwright;

import java.util.concurrent.CountDownLatch;
import java.util.concurrent.TimeUnit;
import java.util.concurrent.atomic.AtomicBoolean;
import java.util.concurrent.atomic.AtomicInteger;
import java.util.concurrent.atomic.AtomicReference;

/**
 * Example demonstrating how to handle captcha automatically solving
 * using browser notification callback from sandbox browser.
 * 
 * 1. Create a new browser session with AgentBay SDK
 * 2. Use playwright to connect to AIBrowser instance through CDP protocol
 * 3. Set solve_captchas to be True and goto jd.com website
 * 4. We will encounter a captcha and we will solve it automatically.
 */
public class BrowserCaptchaSolvingExample {
    private static final AtomicBoolean shouldTakeover = new AtomicBoolean(false);
    private static final AtomicInteger takeoverNotifyId = new AtomicInteger(-1);
    private static final double MAX_CAPTCHA_DETECT_TIMEOUT = 5.0;
    private static final AtomicReference<Double> maxCaptchaSolvingTimeout = new AtomicReference<>(60.0);
    private static final AtomicReference<Double> maxTakeoverTimeout = new AtomicReference<>(180.0);
    
    private static final CountDownLatch captchaPauseEvent = new CountDownLatch(1);
    private static final CountDownLatch captchaResumeOrTakeoverEvent = new CountDownLatch(1);

    public static void main(String[] args) {
        String apiKey = System.getenv("AGENTBAY_API_KEY");
        if (apiKey == null || apiKey.isEmpty()) {
            System.err.println("Error: AGENTBAY_API_KEY environment variable is required");
            return;
        }

        try {
            AgentBay agentBay = new AgentBay();
            CreateSessionParams params = new CreateSessionParams();
            params.setImageId("browser_latest");
            
            SessionResult result = agentBay.create(params);
            
            if (!result.isSuccess() || result.getSession() == null) {
                System.err.println("Failed to create session");
                return;
            }

            Session session = result.getSession();
            String takeoverUrl = session.getResourceUrl();
            System.out.println("🌐 Takeover URL: " + takeoverUrl);

            // Register browser callback
            BrowserCallback callback = (notifyMsg) -> {
                System.out.printf("🔔 Received browser callback: %s, %s, %s, %s, %s, %s%n",
                    notifyMsg.getType(), notifyMsg.getId(), notifyMsg.getCode(),
                    notifyMsg.getMessage(), notifyMsg.getAction(), notifyMsg.getExtraParams());

                try {
                    if ("call-for-user".equals(notifyMsg.getType())) {
                        String action = notifyMsg.getAction();
                        
                        if ("pause".equals(action)) {
                            Object maxWaitTime = notifyMsg.getExtraParams().get("max_wait_time");
                            if (maxWaitTime instanceof Number) {
                                maxCaptchaSolvingTimeout.set(((Number) maxWaitTime).doubleValue());
                            }
                            System.out.printf("Captcha pause notification received, max wait time: %.1fs%n",
                                maxCaptchaSolvingTimeout.get());
                            captchaPauseEvent.countDown();
                        } else if ("resume".equals(action)) {
                            System.out.println("Captcha resume notification received");
                            captchaResumeOrTakeoverEvent.countDown();
                        } else if ("takeover".equals(action)) {
                            shouldTakeover.set(true);
                            if (notifyMsg.getId() != null) {
                                takeoverNotifyId.set(notifyMsg.getId());
                            }
                            Object maxWaitTime = notifyMsg.getExtraParams().get("max_wait_time");
                            if (maxWaitTime instanceof Number) {
                                maxTakeoverTimeout.set(((Number) maxWaitTime).doubleValue());
                            }
                            System.out.printf("Captcha takeover notification received, notify_id: %d, max wait time: %.1fs%n",
                                takeoverNotifyId.get(), maxTakeoverTimeout.get());
                            captchaResumeOrTakeoverEvent.countDown();
                        }
                    }
                } catch (Exception e) {
                    System.err.println("Error handling browser callback: " + e.getMessage());
                }
            };
            
            session.getBrowser().registerCallback(callback);

            try {
                // Initialize browser with captcha solving enabled
                BrowserOption browserOption = new BrowserOption();
                browserOption.setUseStealth(true);
                browserOption.setSolveCaptchas(true);
                browserOption.setCallForUser(true);
                
                boolean initialized = session.getBrowser().initialize(browserOption);
                if (!initialized) {
                    System.err.println("Failed to initialize browser");
                    return;
                }

                String endpointUrl = session.getBrowser().getEndpointUrl();
                System.out.println("🌐 Browser endpoint URL: " + endpointUrl);

                Thread.sleep(2000);

                try (Playwright playwright = Playwright.create()) {
                    Browser browser = playwright.chromium().connectOverCDP(endpointUrl);
                    BrowserContext context = browser.contexts().get(0);
                    Page page = context.newPage();

                    System.out.println("🚀 Navigating to jd.com...");
                    page.navigate("https://aq.jd.com/process/findPwd?s=1");

                    System.out.println("📱 fill phone number...");
                    page.fill("input.field[placeholder=\"请输入账号名/邮箱/已验证手机号\"]", "13000000000");
                    Thread.sleep(2000);

                    System.out.println("🖱️ click next step button...");
                    page.click("button.btn-check-defaut.btn-xl");
                    System.out.println("🔑 Captcha triggered, waiting for solving...");

                    // Wait for captcha solving
                    boolean captchaSolved = waitForCaptchaSolving();

                    if (!captchaSolved) {
                        System.out.println("⏰ Captcha solving timeout or should takeover...");
                        System.out.println("🌍 Opening browser with takeover URL...");
                        
                        // Open browser with takeover URL
                        openBrowser(takeoverUrl);

                        System.out.printf("Waiting for user task over completed or timeout, timeout: %.1fs%n",
                            maxTakeoverTimeout.get());
                        Thread.sleep((long) (maxTakeoverTimeout.get() * 1000));

                        // Send takeoverdone notify message
                        int notifyId = takeoverNotifyId.get();
                        if (notifyId != -1) {
                            session.getBrowser().sendTakeoverDone(notifyId);
                        }
                        System.out.println("✅ User task over completed...");
                    } else {
                        System.out.println("✅ Captcha solved successfully...");
                    }

                    // Check for authentication success button
                    System.out.println("🔍 Checking for authentication success...");
                    try {
                        com.microsoft.playwright.ElementHandle successButton = page.waitForSelector(
                            "button.btn-check-succ:has-text(\"认证成功\")",
                            new Page.WaitForSelectorOptions().setTimeout(5000)
                        );
                        if (successButton != null) {
                            System.out.println("✅ Authentication successful - '认证成功' button found!");
                            page.screenshot(new Page.ScreenshotOptions().setPath(java.nio.file.Paths.get("captcha_solving.png")));
                        } else {
                            System.out.println("⚠️ Authentication success button not found");
                        }
                    } catch (Exception e) {
                        System.out.println("⚠️ Could not find authentication success button: " + e.getMessage());
                    }

                    Thread.sleep(10000);

                    session.getBrowser().unregisterCallback();
                }
            } catch (Exception e) {
                System.err.println("❌ error: " + e.getMessage());
                e.printStackTrace();
            } finally {
                System.out.println("🗑️ Deleting session");
                session.delete();
            }
        } catch (Exception e) {
            e.printStackTrace();
        }
    }

    private static boolean waitForCaptchaSolving() throws InterruptedException {
        System.out.printf("Waiting for captcha pause event, timeout: %.1fs%n", MAX_CAPTCHA_DETECT_TIMEOUT);
        boolean pauseDetected = captchaPauseEvent.await((long) (MAX_CAPTCHA_DETECT_TIMEOUT * 1000), TimeUnit.MILLISECONDS);

        if (!pauseDetected) {
            System.out.println("No captcha pause event detected within timeout, proceeding next step");
            return true;
        }

        System.out.printf("Waiting for captcha resume event, timeout: %.1fs%n", maxCaptchaSolvingTimeout.get());
        boolean resumeDetected = captchaResumeOrTakeoverEvent.await(
            (long) (maxCaptchaSolvingTimeout.get() * 1000), TimeUnit.MILLISECONDS
        );

        if (!resumeDetected) {
            System.out.println("No captcha resume event detected within timeout, should takeover");
            return false;
        }

        if (shouldTakeover.get()) {
            System.out.println("Captcha solving failed, takeover event detected");
            return false;
        }
        return true;
    }

    private static void openBrowser(String url) {
        try {
            String os = System.getProperty("os.name").toLowerCase();
            Runtime runtime = Runtime.getRuntime();
            
            if (os.contains("win")) {
                runtime.exec("rundll32 url.dll,FileProtocolHandler " + url);
            } else if (os.contains("mac")) {
                runtime.exec("open " + url);
            } else if (os.contains("nix") || os.contains("nux")) {
                runtime.exec("xdg-open " + url);
            }
        } catch (Exception e) {
            System.err.println("Failed to open browser: " + e.getMessage());
        }
    }
}
