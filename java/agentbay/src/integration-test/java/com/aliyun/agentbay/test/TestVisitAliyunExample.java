package com.aliyun.agentbay.test;

import com.aliyun.agentbay.AgentBay;
import com.aliyun.agentbay.browser.BrowserOption;
import com.aliyun.agentbay.exception.AgentBayException;
import com.aliyun.agentbay.exception.BrowserException;
import com.aliyun.agentbay.model.SessionResult;
import com.aliyun.agentbay.session.CreateSessionParams;
import com.aliyun.agentbay.session.Session;
import com.microsoft.playwright.*;
import org.junit.*;
import static org.junit.Assert.*;

/**
 * JUnit 4 test cases for VisitAliyunExample functionality
 * Tests the integration of AgentBay SDK with Playwright to visit aliyun.com
 */
public class TestVisitAliyunExample {
    private AgentBay agentBay;
    private Session session;
    private String apiKey;

    @BeforeClass
    public static void setUpClass() {
    }

    @Before
    public void setUp() {
        // Get API key from environment variable
        apiKey = System.getenv("AGENTBAY_API_KEY");
        assertNotNull("AGENTBAY_API_KEY environment variable must be set", apiKey);
        assertFalse("AGENTBAY_API_KEY must not be empty", apiKey.trim().isEmpty());
    }

    @After
    public void tearDown() {
        // Clean up session if it was created
        if (agentBay != null && session != null) {
            try {
                agentBay.delete(session, false);
            } catch (Exception e) {
            }
        }
    }

    @AfterClass
    public static void tearDownClass() {
    }

    /**
     * Test successful AgentBay client initialization
     */
    @Test
    public void testAgentBayInitialization() throws AgentBayException {
        agentBay = new AgentBay();
        assertNotNull("AgentBay instance should not be null", agentBay);
    }

    /**
     * Test successful session creation with browser_latest image
     */
    @Test
    public void testSessionCreation() throws AgentBayException {
        agentBay = new AgentBay();
        
        CreateSessionParams params = new CreateSessionParams();
        params.setImageId("browser_latest");
        
        SessionResult sessionResult = agentBay.create(params);
        
        assertTrue("Session creation should be successful", sessionResult.isSuccess());
        assertNotNull("Session should not be null", sessionResult.getSession());
        
        session = sessionResult.getSession();
        assertNotNull("Session ID should not be null", session.getSessionId());
        assertFalse("Session ID should not be empty", session.getSessionId().isEmpty());
    }

    /**
     * Test browser initialization
     */
    @Test
    public void testBrowserInitialization() throws AgentBayException, BrowserException {
        agentBay = new AgentBay();
        
        CreateSessionParams params = new CreateSessionParams();
        params.setImageId("browser_latest");
        
        SessionResult sessionResult = agentBay.create(params);
        assertTrue("Session creation should be successful", sessionResult.isSuccess());
        
        session = sessionResult.getSession();
        
        boolean browserInitialized = session.getBrowser().initialize(new BrowserOption());
        assertTrue("Browser should be initialized successfully", browserInitialized);
        
        String endpointUrl = session.getBrowser().getEndpointUrl();
        assertNotNull("Endpoint URL should not be null", endpointUrl);
        assertFalse("Endpoint URL should not be empty", endpointUrl.isEmpty());
//        assertTrue("Endpoint URL should start with ws://", endpointUrl.startsWith("ws://"));
    }

    /**
     * Test visiting aliyun.com using Playwright
     */
    @Test
    public void testVisitAliyun() throws AgentBayException, BrowserException {
        agentBay = new AgentBay();
        
        CreateSessionParams params = new CreateSessionParams();
        params.setImageId("browser_latest");
        
        SessionResult sessionResult = agentBay.create(params);
        assertTrue("Session creation should be successful", sessionResult.isSuccess());
        
        session = sessionResult.getSession();
        
        boolean browserInitialized = session.getBrowser().initialize(new BrowserOption());
        assertTrue("Browser should be initialized successfully", browserInitialized);
        
        String endpointUrl = session.getBrowser().getEndpointUrl();
        
        try (Playwright playwright = Playwright.create()) {
            Browser browser = playwright.chromium().connectOverCDP(endpointUrl);
            assertNotNull("Browser should not be null", browser);
            
            BrowserContext context = browser.contexts().get(0);
            assertNotNull("Browser context should not be null", context);
            
            Page page = context.newPage();
            assertNotNull("Page should not be null", page);
            
            page.navigate("https://www.aliyun.com",
                new Page.NavigateOptions()
                    .setWaitUntil(com.microsoft.playwright.options.WaitUntilState.DOMCONTENTLOADED)
                    .setTimeout(60000));
            
            String pageTitle = page.title();
            assertNotNull("Page title should not be null", pageTitle);
            assertFalse("Page title should not be empty", pageTitle.isEmpty());
            page.waitForTimeout(5000);
            
            browser.close();
        }
    }

    /**
     * Test page manipulation with font family change
     */
    @Test
    public void testPageFontManipulation() throws AgentBayException, BrowserException {
        agentBay = new AgentBay();
        
        CreateSessionParams params = new CreateSessionParams();
        params.setImageId("browser_latest");
        
        SessionResult sessionResult = agentBay.create(params);
        assertTrue("Session creation should be successful", sessionResult.isSuccess());
        
        session = sessionResult.getSession();
        
        boolean browserInitialized = session.getBrowser().initialize(new BrowserOption());
        assertTrue("Browser should be initialized successfully", browserInitialized);
        
        String endpointUrl = session.getBrowser().getEndpointUrl();
        
        try (Playwright playwright = Playwright.create()) {
            Browser browser = playwright.chromium().connectOverCDP(endpointUrl);
            BrowserContext context = browser.contexts().get(0);
            Page page = context.newPage();
            
            page.navigate("https://www.aliyun.com",
                new Page.NavigateOptions()
                    .setWaitUntil(com.microsoft.playwright.options.WaitUntilState.DOMCONTENTLOADED)
                    .setTimeout(60000));
            page.waitForTimeout(5000);
            
            // Change font family
            Object result = page.evaluate("document.body.style.fontFamily = 'Microsoft YaHei';");
            page.waitForTimeout(5000);
            
            browser.close();
        }
    }

    /**
     * Test page transformation with scaling
     */
    @Test
    public void testPageTransformation() throws AgentBayException, BrowserException {
        agentBay = new AgentBay();
        
        CreateSessionParams params = new CreateSessionParams();
        params.setImageId("browser_latest");
        
        SessionResult sessionResult = agentBay.create(params);
        assertTrue("Session creation should be successful", sessionResult.isSuccess());
        
        session = sessionResult.getSession();
        
        boolean browserInitialized = session.getBrowser().initialize(new BrowserOption());
        assertTrue("Browser should be initialized successfully", browserInitialized);
        
        String endpointUrl = session.getBrowser().getEndpointUrl();
        
        try (Playwright playwright = Playwright.create()) {
            Browser browser = playwright.chromium().connectOverCDP(endpointUrl);
            BrowserContext context = browser.contexts().get(0);
            Page page = context.newPage();
            
            page.navigate("https://www.aliyun.com",
                new Page.NavigateOptions()
                    .setWaitUntil(com.microsoft.playwright.options.WaitUntilState.DOMCONTENTLOADED)
                    .setTimeout(60000));
            page.waitForTimeout(5000);
            
            // Change font family
            page.evaluate("document.body.style.fontFamily = 'Microsoft YaHei';");
            page.waitForTimeout(5000);
            
            // Apply transformation
            page.evaluate(
                "document.body.style.transform = 'scale(2)';" +
                "document.body.style.transformOrigin = 'top left';"
            );
            page.waitForTimeout(10000);
            
            browser.close();
        }
    }

    /**
     * Test complete workflow from session creation to deletion
     */
    @Test
    public void testCompleteWorkflow() throws AgentBayException, BrowserException {
        agentBay = new AgentBay();
        assertNotNull("AgentBay instance should not be null", agentBay);
        
        CreateSessionParams params = new CreateSessionParams();
        params.setImageId("browser_latest");
        
        SessionResult sessionResult = agentBay.create(params);
        assertTrue("Session creation should be successful", sessionResult.isSuccess());
        
        session = sessionResult.getSession();
        String sessionId = session.getSessionId();
        assertNotNull("Session ID should not be null", sessionId);
        boolean browserInitialized = session.getBrowser().initialize(new BrowserOption());
        assertTrue("Browser should be initialized successfully", browserInitialized);
        
        String endpointUrl = session.getBrowser().getEndpointUrl();
        assertNotNull("Endpoint URL should not be null", endpointUrl);
        try (Playwright playwright = Playwright.create()) {
            Browser browser = playwright.chromium().connectOverCDP(endpointUrl);
            BrowserContext context = browser.contexts().get(0);
            Page page = context.newPage();
            
            page.navigate("https://www.aliyun.com",
                new Page.NavigateOptions()
                    .setWaitUntil(com.microsoft.playwright.options.WaitUntilState.DOMCONTENTLOADED)
                    .setTimeout(60000));
            String pageTitle = page.title();
            page.waitForTimeout(5000);
            
            page.evaluate("document.body.style.fontFamily = 'Microsoft YaHei';");
            page.waitForTimeout(5000);
            
            page.evaluate(
                "document.body.style.transform = 'scale(2)';" +
                "document.body.style.transformOrigin = 'top left';"
            );
            
            page.waitForTimeout(10000);
            browser.close();
        }
        
        agentBay.delete(session, false);
        // Prevent duplicate cleanup in tearDown
        session = null;
    }

    /**
     * Test session creation failure with invalid session result
     */
    @Test
    public void testSessionCreationFailureHandling() throws AgentBayException {
        agentBay = new AgentBay();
        
        CreateSessionParams params = new CreateSessionParams();
        params.setImageId("browser_latest");
        
        SessionResult sessionResult = agentBay.create(params);
        
        if (!sessionResult.isSuccess()) {
            assertNotNull("Error message should be provided", sessionResult.getErrorMessage());
            assertFalse("Error message should not be empty", sessionResult.getErrorMessage().isEmpty());
        } else {
            session = sessionResult.getSession();
        }
    }

    /**
     * Test browser initialization failure handling
     */
    @Test
    public void testBrowserInitializationFailureHandling() throws AgentBayException, BrowserException {
        agentBay = new AgentBay();
        
        CreateSessionParams params = new CreateSessionParams();
        params.setImageId("browser_latest");
        
        SessionResult sessionResult = agentBay.create(params);
        assertTrue("Session creation should be successful", sessionResult.isSuccess());
        
        session = sessionResult.getSession();
        
        boolean browserInitialized = session.getBrowser().initialize(new BrowserOption());
        
        if (!browserInitialized) {
        } else {
        }
    }
}

