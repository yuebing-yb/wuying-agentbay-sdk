package com.aliyun.agentbay.browser;

import java.util.HashMap;
import java.util.Map;

import com.aliyun.agentbay.Config;
import com.aliyun.agentbay.exception.BrowserException;
import com.aliyun.agentbay.model.OperationResult;
import com.aliyun.agentbay.service.BaseService;
import com.aliyun.agentbay.session.Session;
import com.aliyun.agentbay.util.ResponseUtil;
import com.aliyun.wuyingai20250506.models.InitBrowserRequest;
import com.aliyun.wuyingai20250506.models.InitBrowserResponse;
import com.aliyun.wuyingai20250506.models.InitBrowserResponseBody;
import com.fasterxml.jackson.databind.ObjectMapper;

/**
 * Browser provides browser-related operations for the session.
 */
public class Browser extends BaseService {
    private static final ObjectMapper objectMapper = new ObjectMapper();
    private static final String SERVER_BROWSER_USE = "wuying_browseruse";
    private static final String SERVER_CDP = "wuying_cdp_mcp_server";

    private String endpointUrl;
    private boolean initialized;
    private BrowserOption option;
    
    /**
     * The browser operator instance (recommended).
     */
    private BrowserOperator operator;
    /**
     * The browser agent instance (deprecated).
     */
    @Deprecated
    private BrowserAgent agent;
    
    private Integer endpointRouterPort;
    private volatile boolean agentDeprecationWarned = false;
    
    // Callback-related fields
    private BrowserCallback userCallback;
    private volatile boolean wsCallbackRegistered = false;
    private com.aliyun.agentbay._internal.WsClient.PushCallback internalWsCallback;

    public Browser(Session session) {
        super(session);
        this.initialized = false;
        
        this.operator = new BrowserOperator(session, this);
        this.agent = new BrowserAgent(session, this);
    }

    /**
     * Initialize the browser instance with the given options asynchronously.
     * Returns true if successful, false otherwise.
     * 
     * @param option Browser configuration options. If null, default options are used
     * @return true if initialization was successful, false otherwise
     */
    public boolean initialize(BrowserOption option) {
        if (isInitialized()) {
            return true;
        }

        try {
            InitBrowserRequest request = new InitBrowserRequest();
            request.setAuthorization("Bearer " + session.getApiKey());
            request.setSessionId(session.getSessionId());
            request.setPersistentPath(Config.BROWSER_DATA_PATH);

            Map<String, Object> browserOptionMap = option.toMap();

            // Set enableRecord based on session.enableBrowserReplay
            if (session.getEnableBrowserReplay() != null) {
                browserOptionMap.put("enableRecord", session.getEnableBrowserReplay());
            }

            // Convert BrowserOption to JSON string
            String browserOptionJson = objectMapper.writeValueAsString(browserOptionMap);
            request.setBrowserOption(browserOptionJson);

            InitBrowserResponse response = session.getAgentBay().getClient().initBrowser(request);
            String requestId = ResponseUtil.extractRequestId(response);

            if (response != null && response.getBody() != null && response.getBody().getData() != null) {
                // Extract port from response using the correct data type
                InitBrowserResponseBody.InitBrowserResponseBodyData data = response.getBody().getData();
                Integer port = data.getPort();
                if (port != null) {
                    this.endpointRouterPort = port;
                    this.initialized = true;
                    this.option = option;
                    return true;
                } else {
                }
            }
            return false;

        } catch (Exception e) {
            this.initialized = false;
            this.endpointUrl = null;
            this.option = null;
            return false;
        }
    }

    /**
     * Alias for initialize method.
     *
     * @param option Browser initialization options
     * @return true if successful, false otherwise
     */
    public boolean init(BrowserOption option) {
        return initialize(option);
    }

    /**
     * Destroy the browser instance manually.
     */
    public void destroy() {
        if (isInitialized()) {
            try {
                stopBrowser();
                // Reset browser state
                this.initialized = false;
                this.endpointUrl = null;
                this.option = null;
                this.endpointRouterPort = null;
            } catch (BrowserException e) {
            }
        }
    }

    /**
     * Takes a screenshot of the specified page with enhanced options and error handling.
     *
     * @param page The Playwright Page object to take a screenshot of. This is a required parameter.
     * @param fullPage Whether to capture the full scrollable page
     * @param options Additional screenshot options that will override defaults.
     *                Common options include:
     *                - type (ScreenshotType): Image type, either PNG or JPEG (default: PNG)
     *                - timeout (Double): Maximum time in milliseconds (default: 60000)
     *                - animations (String): How to handle animations (default: "disabled")
     *                - caret (String): How to handle the caret (default: "hide")
     *                - scale (String): Scale setting (default: "css")
     * @return Screenshot data as bytes
     * @throws BrowserException if browser is not initialized or page is null
     * @throws IllegalArgumentException if page is null
     */
    public byte[] screenshot(com.microsoft.playwright.Page page, boolean fullPage, Map<String, Object> options) throws BrowserException {
        if (!isInitialized()) {
            throw new BrowserException("Browser must be initialized before calling screenshot.");
        }
        if (page == null) {
            throw new IllegalArgumentException("Page cannot be null");
        }

        Map<String, Object> enhancedOptions = new HashMap<>();
        enhancedOptions.put("animations", "disabled");
        enhancedOptions.put("caret", "hide");
        enhancedOptions.put("scale", "css");
        enhancedOptions.put("timeout", options != null && options.containsKey("timeout") ? options.get("timeout") : 60000);
        enhancedOptions.put("fullPage", fullPage);
        enhancedOptions.put("type", options != null && options.containsKey("type") ? options.get("type") : com.microsoft.playwright.options.ScreenshotType.PNG);

        if (options != null) {
            enhancedOptions.putAll(options);
        }

        try {
            page.evaluate("window.scrollTo(0, document.body.scrollHeight)");
            page.waitForLoadState(com.microsoft.playwright.options.LoadState.DOMCONTENTLOADED,
                new com.microsoft.playwright.Page.WaitForLoadStateOptions().setTimeout(30000));

            scrollToLoadAllContent(page, 8, 1200);

            page.evaluate(
                "() => {\n" +
                "    document.querySelectorAll('img[data-src]').forEach(img => {\n" +
                "        if (!img.src && img.dataset.src) {\n" +
                "            img.src = img.dataset.src;\n" +
                "        }\n" +
                "    });\n" +
                "    document.querySelectorAll('[data-bg]').forEach(el => {\n" +
                "        if (!el.style.backgroundImage) {\n" +
                "            el.style.backgroundImage = `url(${el.dataset.bg})`;\n" +
                "        }\n" +
                "    });\n" +
                "}"
            );

            page.waitForTimeout(1500);

            int finalHeight = (int) page.evaluate("document.body.scrollHeight");
            page.setViewportSize(1920, Math.min(finalHeight, 10000));

            com.microsoft.playwright.Page.ScreenshotOptions screenshotOptions = new com.microsoft.playwright.Page.ScreenshotOptions();
            screenshotOptions.setFullPage((Boolean) enhancedOptions.get("fullPage"));
            screenshotOptions.setType((com.microsoft.playwright.options.ScreenshotType) enhancedOptions.get("type"));
            screenshotOptions.setTimeout((Double) enhancedOptions.getOrDefault("timeout", 60000.0));

            byte[] screenshotBytes = page.screenshot(screenshotOptions);
            return screenshotBytes;

        } catch (Exception e) {
            String errorMsg = "Failed to capture screenshot: " + e.getMessage();
            throw new BrowserException(errorMsg);
        }
    }

    /**
     * Scroll to load all content on the page.
     * 
     * @param page The Playwright Page object
     * @param maxScrolls Maximum number of scroll attempts (default: 8)
     * @param delayMs Delay between scrolls in milliseconds (default: 1200)
     */
    private void scrollToLoadAllContent(com.microsoft.playwright.Page page, int maxScrolls, int delayMs) {
        int lastHeight = 0;
        for (int i = 0; i < maxScrolls; i++) {
            page.evaluate("window.scrollTo(0, document.body.scrollHeight)");
            page.waitForTimeout(delayMs);
            int newHeight = (int) page.evaluate("Math.max(document.body.scrollHeight, document.documentElement.scrollHeight)");
            if (newHeight == lastHeight) {
                break;
            }
            lastHeight = newHeight;
        }
    }

    /**
     * Stop the browser instance (internal use only).
     * 
     * @throws BrowserException if browser is not initialized or stop operation fails
     */
    private void stopBrowser() throws BrowserException {
        if (!isInitialized()) {
            throw new BrowserException("Browser is not initialized. Cannot stop browser.");
        }

        try {
            OperationResult result = callMcpTool("stopChrome", new HashMap<>());
            if (!result.isSuccess()) {
            }
        } catch (Exception e) {
            throw new BrowserException("Failed to stop browser: " + e.getMessage());
        }
    }

    /**
     * Returns the endpoint URL if the browser is initialized, otherwise raises an exception.
     * When initialized, always fetches the latest CDP url from getCdpLink API.
     *
     * @return Browser endpoint URL
     * @throws BrowserException if browser is not initialized or endpoint URL cannot be retrieved
     * 
     */
    public String getEndpointUrl() throws BrowserException {
        if (!isInitialized()) {
            throw new BrowserException("Browser is not initialized. Cannot access endpoint URL.");
        }

        try {
            com.aliyun.wuyingai20250506.models.GetCdpLinkRequest request =
                new com.aliyun.wuyingai20250506.models.GetCdpLinkRequest();
            request.setAuthorization("Bearer " + session.getAgentBay().getApiKey());
            request.setSessionId(session.getSessionId());

            com.aliyun.wuyingai20250506.models.GetCdpLinkResponse response =
                session.getAgentBay().getClient().getCdpLink(request);

            if (response != null && response.getBody() != null &&
                response.getBody().getSuccess() && response.getBody().getData() != null) {
                this.endpointUrl = response.getBody().getData().getUrl();
            } else {
                String errorMsg = response != null && response.getBody() != null ?
                    response.getBody().getMessage() : "Unknown error";
                throw new BrowserException("Failed to get CDP link: " + errorMsg);
            }

            return this.endpointUrl;

        } catch (Exception e) {
            throw new BrowserException("Failed to get endpoint URL from session: " + e.getMessage());
        }
    }

    /**
     * Get the current BrowserOption used to initialize the browser.
     *
     * @return BrowserOption or null if not set
     * 
     */
    public BrowserOption getOption() {
        return option;
    }

    /**
     * Check if the browser is initialized.
     *
     * @return true if initialized, false otherwise
     * 
     */
    public boolean isInitialized() {
        return initialized;
    }

    /**
     * Get the browser operator for browser operations (recommended).
     * 
     * <p>The operator provides AI-powered browser automation capabilities including
     * navigation, screenshots, actions, observations, and data extraction.</p>
     * 
     * @return BrowserOperator instance
     */
    public BrowserOperator getOperator() {
        return operator;
    }

    /**
     * Get the browser agent for advanced browser operations.
     * 
     * <p><strong>⚠️ Deprecated</strong>: Use getOperator instead. This method will be removed in a future version.</p>
     * 
     * @return BrowserAgent instance
     * @deprecated Use getOperator instead
     */
    @Deprecated
    public BrowserAgent getAgent() {
        if (!agentDeprecationWarned) {
            synchronized (this) {
                if (!agentDeprecationWarned) {
                    System.err.println(
                        "[⚠️ DeprecationWarning] browser.agent is deprecated and will be removed in a future version. "
                        + "Please use browser.operator instead."
                    );
                    agentDeprecationWarned = true;
                }
            }
        }
        return agent;
    }

    /**
     * Get the endpoint router port.
     *
     * @return Port number or null if not set
     */
    public Integer getEndpointRouterPort() {
        return endpointRouterPort;
    }
    
    /**
     * Register a callback function to handle browser-related push notifications from sandbox.
     * 
     * <p>Example usage:</p>
     * <pre>{@code
     * BrowserCallback callback = (notifyMsg) -> {
     *     System.out.println("Type: " + notifyMsg.getType());
     *     System.out.println("Code: " + notifyMsg.getCode());
     *     System.out.println("Message: " + notifyMsg.getMessage());
     *     System.out.println("Action: " + notifyMsg.getAction());
     *     System.out.println("Extra params: " + notifyMsg.getExtraParams());
     * };
     * 
     * CreateResult createResult = agentBay.create();
     * Session session = createResult.getSession();
     * session.getBrowser().initialize(new BrowserOption());
     * boolean success = session.getBrowser().registerCallback(callback);
     * // ... do work ...
     * session.getBrowser().unregisterCallback();
     * session.delete();
     * }</pre>
     * 
     * @param callback Callback function that receives a BrowserNotifyMessage
     * @return true if the callback was successfully registered
     */
    public boolean registerCallback(BrowserCallback callback) {
        try {
            // Store user callback
            this.userCallback = callback;
            
            // Register internal callback to ws_client only once
            if (!wsCallbackRegistered) {
                com.aliyun.agentbay._internal.WsClient wsClient = session.getWsClient();
                if (wsClient == null) {
                    throw new BrowserException("WebSocket client is not available");
                }
                
                // Create internal callback wrapper
                internalWsCallback = (payload) -> {
                    try {
                        if (userCallback != null) {
                            BrowserNotifyMessage notifyMsg = BrowserNotifyMessage.fromMap(payload);
                            userCallback.onNotify(notifyMsg);
                        }
                    } catch (Exception e) {
                        System.err.println("Error in internal ws_callback: " + e.getMessage());
                    }
                };
                
                wsClient.registerCallback(SERVER_CDP, internalWsCallback);
                wsCallbackRegistered = true;
            }
            
            return true;
        } catch (Exception e) {
            System.err.println("Failed to register callback: " + e.getMessage());
            return false;
        }
    }
    
    /**
     * Unregister the previously registered callback function.
     * 
     * <p>Example usage:</p>
     * <pre>{@code
     * session.getBrowser().registerCallback(callback);
     * // ... do work ...
     * session.getBrowser().unregisterCallback();
     * }</pre>
     */
    public void unregisterCallback() {
        try {
            // Clear user callback
            userCallback = null;
            
            // Unregister from ws_client
            if (wsCallbackRegistered) {
                com.aliyun.agentbay._internal.WsClient wsClient = session.getWsClient();
                if (wsClient != null && internalWsCallback != null) {
                    wsClient.unregisterCallback(SERVER_CDP, internalWsCallback);
                    wsClient.close();
                }
                wsCallbackRegistered = false;
                internalWsCallback = null;
            }
        } catch (Exception e) {
            System.err.println("Failed to unregister callback: " + e.getMessage());
        }
    }
    
    /**
     * Send a notify message to sandbox through WebSocket.
     * 
     * <p>Example usage:</p>
     * <pre>{@code
     * BrowserNotifyMessage notifyMsg = new BrowserNotifyMessage(
     *     "call-for-user",
     *     1,
     *     199,
     *     "user handle done",
     *     "takeoverdone",
     *     new HashMap<>()
     * );
     * boolean success = session.getBrowser().sendNotifyMessage(notifyMsg);
     * }</pre>
     * 
     * @param notifyMessage The notification message to send
     * @return true if the message was successfully sent, false otherwise
     */
    public boolean sendNotifyMessage(BrowserNotifyMessage notifyMessage) {
        try {
            com.aliyun.agentbay._internal.WsClient wsClient = session.getWsClient();
            if (wsClient == null) {
                throw new BrowserException("WebSocket client is not available");
            }
            
            // Send notify message through ws_client
            wsClient.sendMessage(SERVER_CDP, notifyMessage.toMap());
            return true;
        } catch (Exception e) {
            System.err.println("Failed to send notify message: " + e.getMessage());
            return false;
        }
    }
    
    /**
     * Send a takeoverdone notify message to sandbox.
     * 
     * <p>Example usage:</p>
     * <pre>{@code
     * BrowserCallback callback = (notifyMsg) -> {
     *     if ("takeover".equals(notifyMsg.getAction())) {
     *         int takeoverNotifyId = notifyMsg.getId();
     *         // ... do work in other thread...
     *         session.getBrowser().sendTakeoverDone(takeoverNotifyId);
     *     }
     * };
     * 
     * CreateResult createResult = agentBay.create();
     * Session session = createResult.getSession();
     * session.getBrowser().initialize(new BrowserOption());
     * session.getBrowser().registerCallback(callback);
     * // ... do work ...
     * session.getBrowser().unregisterCallback();
     * session.delete();
     * }</pre>
     * 
     * @param notifyId The notification ID associated with the takeover request message
     * @return true if the takeoverdone notify message was successfully sent, false otherwise
     */
    public boolean sendTakeoverDone(int notifyId) {
        try {
            // Get ws_client
            com.aliyun.agentbay._internal.WsClient wsClient = session.getWsClient();
            if (wsClient == null) {
                throw new BrowserException("WebSocket client is not available");
            }
            
            // Build takeoverdone notify message
            BrowserNotifyMessage notifyMessage = new BrowserNotifyMessage(
                "call-for-user",
                notifyId,
                199,
                "user handle done",
                "takeoverdone",
                new HashMap<>()
            );
            
            // Send message through ws_client
            wsClient.sendMessage(SERVER_CDP, notifyMessage.toMap());
            return true;
        } catch (Exception e) {
            System.err.println("Failed to send browser notify message: " + e.getMessage());
            return false;
        }
    }
}