package com.aliyun.agentbay.browser;

/**
 * Callback interface for handling browser-related push notifications from sandbox.
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
 * session.getBrowser().registerCallback(callback);
 * }</pre>
 */
@FunctionalInterface
public interface BrowserCallback {
    /**
     * Called when a browser notification is received.
     * 
     * @param notifyMsg The notification message containing type, code, message, action, and extra parameters
     */
    void onNotify(BrowserNotifyMessage notifyMsg);
}
