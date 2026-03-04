package com.aliyun.agentbay.browser;

/**
 * Browser data synchronization mode.
 *
 * <p>Controls the scope of browser data synchronized between sessions.
 *
 * <ul>
 *   <li>{@link #MINIMAL} - Only Cookies + Local State. Smallest footprint,
 *       sufficient for basic cookie-based auth.</li>
 *   <li>{@link #STANDARD} - Login state + anti-risk-control data. Includes
 *       Cookies, localStorage, IndexedDB, saved passwords, preferences, HSTS,
 *       GPU cache, etc. Recommended for most scenarios.</li>
 * </ul>
 */
public enum BrowserSyncMode {

    /** Synchronize only essential files (Cookies, Local State). */
    MINIMAL("minimal"),

    /** Synchronize login state and anti-risk-control data (recommended). */
    STANDARD("standard");

    private final String value;

    BrowserSyncMode(String value) {
        this.value = value;
    }

    public String getValue() {
        return value;
    }
}
