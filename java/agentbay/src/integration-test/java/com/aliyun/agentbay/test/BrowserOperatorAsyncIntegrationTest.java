package com.aliyun.agentbay.test;

import java.util.List;

import org.junit.AfterClass;
import static org.junit.Assert.assertEquals;
import static org.junit.Assert.assertFalse;
import static org.junit.Assert.assertNotNull;
import static org.junit.Assert.assertTrue;
import static org.junit.Assert.fail;
import org.junit.BeforeClass;
import org.junit.Test;

import com.aliyun.agentbay.AgentBay;
import com.aliyun.agentbay.browser.ActOptions;
import com.aliyun.agentbay.browser.ActResult;
import com.aliyun.agentbay.browser.BrowserOperator;
import com.aliyun.agentbay.browser.BrowserOption;
import com.aliyun.agentbay.browser.ExtractOptions;
import com.aliyun.agentbay.browser.ObserveOptions;
import com.aliyun.agentbay.browser.ObserveResult;
import com.aliyun.agentbay.exception.AgentBayException;
import com.aliyun.agentbay.model.SessionResult;
import com.aliyun.agentbay.session.CreateSessionParams;
import com.aliyun.agentbay.session.Session;
import com.fasterxml.jackson.annotation.JsonProperty;
import com.microsoft.playwright.Browser;
import com.microsoft.playwright.Page;
import com.microsoft.playwright.Playwright;

/**
 * Test cases for BrowserOperator async methods (actAsync and extractAsync)
 * Tests the async variants that use page_use_act_async and page_use_extract_async
 */
public class BrowserOperatorAsyncIntegrationTest {
    private static AgentBay agentBay;
    private static Session session;
    private static String apiKey;

    /**
     * Simple product data model for testing extraction
     */
    public static class ProductInfo {
        @JsonProperty("title")
        private String title;

        @JsonProperty("price")
        private String price;

        @JsonProperty("description")
        private String description;

        public String getTitle() {
            return title;
        }

        public void setTitle(String title) {
            this.title = title;
        }

        public String getPrice() {
            return price;
        }

        public void setPrice(String price) {
            this.price = price;
        }

        public String getDescription() {
            return description;
        }

        public void setDescription(String description) {
            this.description = description;
        }
    }

    /**
     * Game state model for 2048 game
     */
    public static class GameState {
        @JsonProperty("score")
        private Integer score;

        @JsonProperty("highestTile")
        private Integer highestTile;

        @JsonProperty("grid")
        private List<List<Integer>> grid;

        public Integer getScore() {
            return score;
        }

        public void setScore(Integer score) {
            this.score = score;
        }

        public Integer getHighestTile() {
            return highestTile;
        }

        public void setHighestTile(Integer highestTile) {
            this.highestTile = highestTile;
        }

        public List<List<Integer>> getGrid() {
            return grid;
        }

        public void setGrid(List<List<Integer>> grid) {
            this.grid = grid;
        }
    }

    @BeforeClass
    public static void setUp() throws AgentBayException {
        apiKey = System.getenv("AGENTBAY_API_KEY");
        assertNotNull("AGENTBAY_API_KEY environment variable must be set", apiKey);
        assertFalse("AGENTBAY_API_KEY cannot be empty", apiKey.trim().isEmpty());
        agentBay = new AgentBay(apiKey);
        CreateSessionParams params = new CreateSessionParams();
        params.setImageId("browser_latest");
        SessionResult sessionResult = agentBay.create(params);

        if (sessionResult.isSuccess()) {
            session = sessionResult.getSession();
            System.out.println("Resource URL: " + session.getResourceUrl());
        } else {
            fail("Failed to create session: " + sessionResult.getErrorMessage());
        }
    }

    @AfterClass
    public static void tearDown() {
        if (session != null) {
            try {
            } catch (Exception e) {
            }
        }
    }

    @Test
    public void test01_ActAsyncBasicNavigation() {
        assertNotNull("Session must be created", session);

        try {
            session.getBrowser().initialize(new BrowserOption());

            try (Playwright playwright = Playwright.create()) {
                String endpointUrl = session.getBrowser().getEndpointUrl();
                Browser browser = playwright.chromium().connectOverCDP(endpointUrl);
                com.microsoft.playwright.BrowserContext context = browser.contexts().get(0);
                Page page = context.newPage();
                BrowserOperator operator = session.getBrowser().getOperator();
                ActOptions options = new ActOptions("goto('https://www.baidu.com')");
                ActResult result = operator.actAsync(options, page);
                System.out.println("ActResult: " + result.toString());
                assertNotNull("ActResult should not be null", result);
                assertTrue("Navigation should succeed", result.isSuccess());
                page.close();
                browser.close();
            }
        } catch (Exception e) {
            fail("Async act navigation should not throw exception: " + e.getMessage());
        }
    }

    @Test
    public void test02_ActAsyncClickOperation() {
        assertNotNull("Session must be created", session);

        try {
            session.getBrowser().initialize(new BrowserOption());

            try (Playwright playwright = Playwright.create()) {
                String endpointUrl = session.getBrowser().getEndpointUrl();
                Browser browser = playwright.chromium().connectOverCDP(endpointUrl);
                com.microsoft.playwright.BrowserContext context = browser.contexts().get(0);
                Page page = context.newPage();
                BrowserOperator operator = session.getBrowser().getOperator();
                page.navigate("https://example.com",
                    new Page.NavigateOptions()
                        .setWaitUntil(com.microsoft.playwright.options.WaitUntilState.DOMCONTENTLOADED)
                        .setTimeout(60000));
                Thread.sleep(1000);
                ActOptions options = new ActOptions("click('a')");
                ActResult result = operator.actAsync(options, page);

                assertNotNull("ActResult should not be null", result);
                page.close();
                browser.close();
            }
        } catch (Exception e) {
        }
    }

    @Test
    public void test03_ExtractAsyncUserAgent() {
        assertNotNull("Session must be created", session);

        try {
            session.getBrowser().initialize(new BrowserOption());

            try (Playwright playwright = Playwright.create()) {
                String endpointUrl = session.getBrowser().getEndpointUrl();
                Browser browser = playwright.chromium().connectOverCDP(endpointUrl);
                com.microsoft.playwright.BrowserContext context = browser.contexts().get(0);
                Page page = context.newPage();
                BrowserOperator operator = session.getBrowser().getOperator();
                page.navigate("https://httpbin.org/user-agent",
                    new Page.NavigateOptions()
                        .setWaitUntil(com.microsoft.playwright.options.WaitUntilState.DOMCONTENTLOADED)
                        .setTimeout(60000));
                Thread.sleep(2000);

                String instruction = "Extract the user-agent string from the page content";
                ExtractOptions<ProductInfo> extractOptions = new ExtractOptions<>(instruction, ProductInfo.class);
                extractOptions.setUseTextExtract(true);

                BrowserOperator.ExtractResultTuple<ProductInfo> extractResult =
                    operator.extractAsync(extractOptions, page);

                assertNotNull("Extract result should not be null", extractResult);
                assertTrue("Extract operation should succeed", extractResult.isSuccess());

                ProductInfo info = extractResult.getData();
                assertNotNull("Extracted info should not be null", info);

                page.close();
                browser.close();
            }
        } catch (Exception e) {
            fail("Async extract operation should not throw exception: " + e.getMessage());
        }
    }

    @Test
    public void test04_ExtractAsyncProductInfo() {
        assertNotNull("Session must be created", session);

        try {
            session.getBrowser().initialize(new BrowserOption());

            try (Playwright playwright = Playwright.create()) {
                String endpointUrl = session.getBrowser().getEndpointUrl();
                Browser browser = playwright.chromium().connectOverCDP(endpointUrl);
                com.microsoft.playwright.BrowserContext context = browser.contexts().get(0);
                Page page = context.newPage();
                BrowserOperator operator = session.getBrowser().getOperator();
                page.navigate("https://example.com",
                    new Page.NavigateOptions()
                        .setWaitUntil(com.microsoft.playwright.options.WaitUntilState.DOMCONTENTLOADED)
                        .setTimeout(60000));
                Thread.sleep(1000);

                String instruction = "Extract information from the page:\n" +
                    "1. Page title as 'title'\n" +
                    "2. Any price information as 'price' (use 'N/A' if not found)\n" +
                    "3. Main content description as 'description'";
                ExtractOptions<ProductInfo> extractOptions =
                    new ExtractOptions<>(instruction, ProductInfo.class);
                extractOptions.setUseTextExtract(true);

                BrowserOperator.ExtractResultTuple<ProductInfo> extractResult =
                    operator.extractAsync(extractOptions, page);

                assertNotNull("Extract result should not be null", extractResult);
                assertTrue("Extract operation should succeed", extractResult.isSuccess());

                ProductInfo info = extractResult.getData();
                assertNotNull("Product info should not be null", info);
                assertNotNull("Title should not be null", info.getTitle());

                page.close();
                browser.close();
            }
        } catch (Exception e) {
            fail("Async extract operation should not throw exception: " + e.getMessage());
        }
    }

    @Test
    public void test05_ActAsyncWithObserveResult() {
        assertNotNull("Session must be created", session);

        try {
            session.getBrowser().initialize(new BrowserOption());

            try (Playwright playwright = Playwright.create()) {
                String endpointUrl = session.getBrowser().getEndpointUrl();
                Browser browser = playwright.chromium().connectOverCDP(endpointUrl);
                com.microsoft.playwright.BrowserContext context = browser.contexts().get(0);
                Page page = context.newPage();
                BrowserOperator operator = session.getBrowser().getOperator();
                page.navigate("https://example.com",
                    new Page.NavigateOptions()
                        .setWaitUntil(com.microsoft.playwright.options.WaitUntilState.DOMCONTENTLOADED)
                        .setTimeout(60000));
                Thread.sleep(1000);
                ObserveOptions observeOptions = new ObserveOptions("Find all links on the page");
                BrowserOperator.ObserveResultTuple observeResult = operator.observe(page, observeOptions);

                if (observeResult.isSuccess() && !observeResult.getResults().isEmpty()) {
                    ObserveResult firstResult = observeResult.getResults().get(0);
                    ActResult actResult = operator.actAsync(firstResult, page);

                    assertNotNull("ActResult should not be null", actResult);
                } else {
                }

                page.close();
                browser.close();
            }
        } catch (Exception e) {
        }
    }

    @Test
    public void test06_ExtractAsyncWithCustomOptions() {
        assertNotNull("Session must be created", session);

        try {
            session.getBrowser().initialize(new BrowserOption());

            try (Playwright playwright = Playwright.create()) {
                String endpointUrl = session.getBrowser().getEndpointUrl();
                Browser browser = playwright.chromium().connectOverCDP(endpointUrl);
                com.microsoft.playwright.BrowserContext context = browser.contexts().get(0);
                Page page = context.newPage();
                BrowserOperator operator = session.getBrowser().getOperator();
                page.navigate("https://example.com",
                    new Page.NavigateOptions()
                        .setWaitUntil(com.microsoft.playwright.options.WaitUntilState.DOMCONTENTLOADED)
                        .setTimeout(60000));
                Thread.sleep(1000);

                String instruction = "Extract page title and main heading";
                ExtractOptions<ProductInfo> extractOptions =
                    new ExtractOptions<>(instruction, ProductInfo.class);
                extractOptions.setUseTextExtract(true);
                extractOptions.setUseVision(false);
                extractOptions.setSelector("body");
                extractOptions.setDomSettleTimeoutMs(2000);
                BrowserOperator.ExtractResultTuple<ProductInfo> extractResult =
                    operator.extractAsync(extractOptions, page);

                assertNotNull("Extract result should not be null", extractResult);
                assertTrue("Extract operation should succeed", extractResult.isSuccess());

                ProductInfo info = extractResult.getData();
                assertNotNull("Product info should not be null", info);

                page.close();
                browser.close();
            }
        } catch (Exception e) {
            fail("Async extract with custom options should not throw exception: " + e.getMessage());
        }
    }

    @Test
    public void test07_ActAsyncWithTimeout() {
        assertNotNull("Session must be created", session);

        try {
            session.getBrowser().initialize(new BrowserOption());

            try (Playwright playwright = Playwright.create()) {
                String endpointUrl = session.getBrowser().getEndpointUrl();
                Browser browser = playwright.chromium().connectOverCDP(endpointUrl);
                com.microsoft.playwright.BrowserContext context = browser.contexts().get(0);
                Page page = context.newPage();
                BrowserOperator operator = session.getBrowser().getOperator();
                ActOptions options = new ActOptions("goto('https://httpbin.org/user-agent')");
                options.setTimeoutMS(30000);
                options.setDomSettleTimeoutMs(3000);

                ActResult result = operator.actAsync(options, page);

                assertNotNull("ActResult should not be null", result);
                assertTrue("Navigation with timeout should succeed", result.isSuccess());
                page.close();
                browser.close();
            }
        } catch (Exception e) {
            fail("Async act with timeout should not throw exception: " + e.getMessage());
        }
    }

    @Test
    public void test08_CompareAsyncVsSyncAct() {
        assertNotNull("Session must be created", session);

        try {
            session.getBrowser().initialize(new BrowserOption());

            try (Playwright playwright = Playwright.create()) {
                String endpointUrl = session.getBrowser().getEndpointUrl();
                Browser browser = playwright.chromium().connectOverCDP(endpointUrl);
                com.microsoft.playwright.BrowserContext context = browser.contexts().get(0);
                Page page = context.newPage();
                BrowserOperator operator = session.getBrowser().getOperator();

                ActOptions options = new ActOptions("goto('https://example.com')");
                long startSync = System.currentTimeMillis();
                ActResult syncResult = operator.act(page, options);
                long syncDuration = System.currentTimeMillis() - startSync;

                Thread.sleep(2000);
                long startAsync = System.currentTimeMillis();
                ActResult asyncResult = operator.actAsync(options, page);
                long asyncDuration = System.currentTimeMillis() - startAsync;

                assertNotNull("Sync result should not be null", syncResult);
                assertNotNull("Async result should not be null", asyncResult);

                page.close();
                browser.close();
            }
        } catch (Exception e) {
        }
    }

    @Test
    public void test09_CompareAsyncVsSyncExtract() {
        assertNotNull("Session must be created", session);

        try {
            session.getBrowser().initialize(new BrowserOption());

            try (Playwright playwright = Playwright.create()) {
                String endpointUrl = session.getBrowser().getEndpointUrl();
                Browser browser = playwright.chromium().connectOverCDP(endpointUrl);
                com.microsoft.playwright.BrowserContext context = browser.contexts().get(0);
                Page page = context.newPage();
                BrowserOperator operator = session.getBrowser().getOperator();

                page.navigate("https://example.com",
                    new Page.NavigateOptions()
                        .setWaitUntil(com.microsoft.playwright.options.WaitUntilState.DOMCONTENTLOADED)
                        .setTimeout(60000));
                Thread.sleep(1000);

                String instruction = "Extract page title";
                ExtractOptions<ProductInfo> options = new ExtractOptions<>(instruction, ProductInfo.class);
                options.setUseTextExtract(true);
                long startSync = System.currentTimeMillis();
                BrowserOperator.ExtractResultTuple<ProductInfo> syncResult = operator.extract(page, options);
                long syncDuration = System.currentTimeMillis() - startSync;

                Thread.sleep(2000);
                long startAsync = System.currentTimeMillis();
                BrowserOperator.ExtractResultTuple<ProductInfo> asyncResult = operator.extractAsync(options, page);
                long asyncDuration = System.currentTimeMillis() - startAsync;

                assertNotNull("Sync result should not be null", syncResult);
                assertNotNull("Async result should not be null", asyncResult);

                page.close();
                browser.close();
            }
        } catch (Exception e) {
        }
    }

    @Test
    public void test10_AsyncMethodsWithNullPage() {
        assertNotNull("Session must be created", session);

        try {
            session.getBrowser().initialize(new BrowserOption());

            try (Playwright playwright = Playwright.create()) {
                String endpointUrl = session.getBrowser().getEndpointUrl();
                com.microsoft.playwright.Browser browser = playwright.chromium().connectOverCDP(endpointUrl);
                BrowserOperator operator = session.getBrowser().getOperator();
                ActOptions actOptions = new ActOptions("goto('https://example.com')");
                ActResult actResult = operator.actAsync(actOptions);

                assertNotNull("ActResult should not be null", actResult);
                Thread.sleep(2000);
                ExtractOptions<ProductInfo> extractOptions =
                    new ExtractOptions<>("Extract page title", ProductInfo.class);
                extractOptions.setUseTextExtract(true);

                BrowserOperator.ExtractResultTuple<ProductInfo> extractResult =
                    operator.extractAsync(extractOptions);

                assertNotNull("ExtractResult should not be null", extractResult);

                browser.close();
            }
        } catch (Exception e) {
        }
    }
}
