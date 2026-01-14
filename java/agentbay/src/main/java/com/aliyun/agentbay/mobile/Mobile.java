package com.aliyun.agentbay.mobile;

import com.aliyun.agentbay.model.*;
import com.aliyun.agentbay.service.BaseService;
import com.aliyun.agentbay.session.Session;
import com.fasterxml.jackson.core.type.TypeReference;
import com.fasterxml.jackson.databind.ObjectMapper;
import java.util.Base64;
import java.util.ArrayList;
import java.util.HashMap;
import java.util.List;
import java.util.Map;

// Explicitly import Process to avoid ambiguity with java.lang.Process
import com.aliyun.agentbay.model.Process;

/**
 * Mobile module for mobile device UI automation and configuration.
 * Handles touch operations, UI element interactions, application management, screenshot capabilities,
 * and mobile environment configuration operations.
 */
public class Mobile extends BaseService {
    private static final ObjectMapper objectMapper = new ObjectMapper();
    private static final byte[] PNG_MAGIC = new byte[] {(byte) 0x89, 0x50, 0x4e, 0x47, 0x0d, 0x0a, 0x1a, 0x0a};
    private static final byte[] JPEG_MAGIC = new byte[] {(byte) 0xff, (byte) 0xd8, (byte) 0xff};
    private static final String SERVER_UI = "wuying_ui";
    private static final String SERVER_APP = "wuying_app";
    private static final String SERVER_CAPTURE = "wuying_capture";
    private static final String SERVER_SYSTEM_SCREENSHOT = "mcp-server";

    public Mobile(Session session) {
        super(session);
    }

    private OperationResult callUiTool(String toolName, Map<String, Object> args) {
        return callMcpTool(toolName, args, SERVER_UI);
    }

    private OperationResult callAppTool(String toolName, Map<String, Object> args) {
        return callMcpTool(toolName, args, SERVER_APP);
    }

    private OperationResult callCaptureTool(String toolName, Map<String, Object> args) {
        return callMcpTool(toolName, args, SERVER_CAPTURE);
    }

    private OperationResult callSystemScreenshotTool() {
        return callMcpTool("system_screenshot", new HashMap<>(), SERVER_SYSTEM_SCREENSHOT);
    }

    // ==================== Touch Operations ====================

    /**
     * Taps on the mobile screen at the specified coordinates.
     *
     * @param x X coordinate in pixels
     * @param y Y coordinate in pixels
     * @return BoolResult containing success status and error message if any
     */
    public BoolResult tap(int x, int y) {
        try {
            Map<String, Object> args = new HashMap<>();
            args.put("x", x);
            args.put("y", y);
            OperationResult result = callUiTool("tap", args);

            if (!result.isSuccess()) {
                return new BoolResult(
                    result.getRequestId(),
                    false,
                    null,
                    result.getErrorMessage()
                );
            }

            return new BoolResult(
                result.getRequestId(),
                true,
                true,
                ""
            );
        } catch (Exception e) {
            return new BoolResult(
                "",
                false,
                null,
                "Failed to tap: " + e.getMessage()
            );
        }
    }

    /**
     * Performs a swipe gesture from one point to another.
     *
     * @param startX Starting X coordinate
     * @param startY Starting Y coordinate
     * @param endX Ending X coordinate
     * @param endY Ending Y coordinate
     * @param durationMs Duration of the swipe in milliseconds. Defaults to 300
     * @return BoolResult containing success status and error message if any
     */
    public BoolResult swipe(int startX, int startY, int endX, int endY, int durationMs) {
        try {
            Map<String, Object> args = new HashMap<>();
            args.put("start_x", startX);
            args.put("start_y", startY);
            args.put("end_x", endX);
            args.put("end_y", endY);
            args.put("duration_ms", durationMs);
            OperationResult result = callUiTool("swipe", args);

            if (!result.isSuccess()) {
                return new BoolResult(
                    result.getRequestId(),
                    false,
                    null,
                    result.getErrorMessage()
                );
            }

            return new BoolResult(
                result.getRequestId(),
                true,
                true,
                ""
            );
        } catch (Exception e) {
            return new BoolResult(
                "",
                false,
                null,
                "Failed to perform swipe: " + e.getMessage()
            );
        }
    }

    /**
     * Performs a swipe gesture with default duration (300ms).
     *
     * @param startX Starting X coordinate
     * @param startY Starting Y coordinate
     * @param endX Ending X coordinate
     * @param endY Ending Y coordinate
     * @return BoolResult containing success status and error message if any
     */
    public BoolResult swipe(int startX, int startY, int endX, int endY) {
        return swipe(startX, startY, endX, endY, 300);
    }

    /**
     * Inputs text into the active field.
     *
     * @param text The text to input
     * @return BoolResult containing success status and error message if any
     */
    public BoolResult inputText(String text) {
        try {
            Map<String, Object> args = new HashMap<>();
            args.put("text", text);
            OperationResult result = callUiTool("input_text", args);

            if (!result.isSuccess()) {
                return new BoolResult(
                    result.getRequestId(),
                    false,
                    null,
                    result.getErrorMessage()
                );
            }

            return new BoolResult(
                result.getRequestId(),
                true,
                true,
                ""
            );
        } catch (Exception e) {
            return new BoolResult(
                "",
                false,
                null,
                "Failed to input text: " + e.getMessage()
            );
        }
    }

    /**
     * Sends a key press event.
     *
     * @param key The key code to send. Supported key codes:
     *            - 3: HOME
     *            - 4: BACK
     *            - 24: VOLUME_UP
     *            - 25: VOLUME_DOWN
     *            - 26: POWER
     *            - 82: MENU
     * @return BoolResult containing success status and error message if any
     */
    public BoolResult sendKey(int key) {
        try {
            Map<String, Object> args = new HashMap<>();
            args.put("key", key);
            OperationResult result = callUiTool("send_key", args);

            if (!result.isSuccess()) {
                return new BoolResult(
                    result.getRequestId(),
                    false,
                    null,
                    result.getErrorMessage()
                );
            }

            return new BoolResult(
                result.getRequestId(),
                true,
                true,
                ""
            );
        } catch (Exception e) {
            return new BoolResult(
                "",
                false,
                null,
                "Failed to send key: " + e.getMessage()
            );
        }
    }

    // ==================== UI Element Operations ====================

    /**
     * Retrieves all clickable UI elements within the specified timeout.
     *
     * @param timeoutMs Timeout in milliseconds. Defaults to 2000
     * @return UIElementListResult containing clickable UI elements and error message if any
     */
    public UIElementListResult getClickableUiElements(int timeoutMs) {
        try {
            Map<String, Object> args = new HashMap<>();
            args.put("timeout_ms", timeoutMs);
            OperationResult result = callUiTool("get_clickable_ui_elements", args);

            if (!result.isSuccess()) {
                return new UIElementListResult(
                    result.getRequestId(),
                    false,
                    new ArrayList<>(),
                    result.getData() == null ? "" : result.getData(),
                    "json",
                    result.getErrorMessage()
                );
            }

            try {
                String data = result.getData();
                if (data == null || data.isEmpty()) {
                    return new UIElementListResult(
                        result.getRequestId(),
                        true,
                        new ArrayList<>(),
                        "",
                        "json",
                        ""
                    );
                }

                List<Map<String, Object>> elements = objectMapper.readValue(
                    data,
                    new TypeReference<List<Map<String, Object>>>() {}
                );

                return new UIElementListResult(
                    result.getRequestId(),
                    true,
                    elements,
                    data,
                    "json",
                    ""
                );
            } catch (Exception e) {
                return new UIElementListResult(
                    result.getRequestId(),
                    false,
                    new ArrayList<>(),
                    result.getData() == null ? "" : result.getData(),
                    "json",
                    "Failed to parse clickable UI elements data: " + e.getMessage()
                );
            }
        } catch (Exception e) {
            return new UIElementListResult(
                "",
                false,
                new ArrayList<>(),
                "",
                "json",
                "Failed to get clickable UI elements: " + e.getMessage()
            );
        }
    }

    /**
     * Retrieves all clickable UI elements with default timeout (2000ms).
     *
     * @return UIElementListResult containing clickable UI elements and error message if any
     */
    public UIElementListResult getClickableUiElements() {
        return getClickableUiElements(2000);
    }

    /**
     * Retrieves all UI elements within the specified timeout.
     *
     * @param timeoutMs Timeout in milliseconds. Defaults to 2000
     * @return UIElementListResult containing UI elements and error message if any
     */
    public UIElementListResult getAllUiElements(int timeoutMs) {
        return getAllUiElements(timeoutMs, "json");
    }

    /**
     * Retrieves all UI elements within the specified timeout.
     *
     * Supported formats:
     * - "json": parse and return elements
     * - "xml": return raw XML and an empty elements list
     *
     * @param timeoutMs Timeout in milliseconds
     * @param format Output format of the underlying MCP tool ("json" or "xml")
     * @return UIElementListResult containing UI elements or raw XML
     */
    public UIElementListResult getAllUiElements(int timeoutMs, String format) {
        try {
            String formatNorm = format == null ? "json" : format.trim().toLowerCase();
            if (formatNorm.isEmpty()) {
                formatNorm = "json";
            }

            Map<String, Object> args = new HashMap<>();
            args.put("timeout_ms", timeoutMs);
            args.put("format", formatNorm);
            OperationResult result = callUiTool("get_all_ui_elements", args);

            if (!result.isSuccess()) {
                return new UIElementListResult(
                    result.getRequestId(),
                    false,
                    new ArrayList<>(),
                    result.getData() == null ? "" : result.getData(),
                    formatNorm,
                    result.getErrorMessage()
                );
            }

            try {
                String data = result.getData();
                if (data == null || data.isEmpty()) {
                    return new UIElementListResult(
                        result.getRequestId(),
                        true,
                        new ArrayList<>(),
                        "",
                        formatNorm,
                        ""
                    );
                }

                if ("xml".equals(formatNorm)) {
                    return new UIElementListResult(
                        result.getRequestId(),
                        true,
                        new ArrayList<>(),
                        data,
                        "xml",
                        ""
                    );
                }

                if (!"json".equals(formatNorm)) {
                    return new UIElementListResult(
                        result.getRequestId(),
                        false,
                        new ArrayList<>(),
                        data,
                        formatNorm,
                        "Unsupported UI elements format: " + format + ". Supported values: 'json', 'xml'."
                    );
                }

                List<Map<String, Object>> elementsJson = objectMapper.readValue(
                    data,
                    new TypeReference<List<Map<String, Object>>>() {}
                );

                List<Map<String, Object>> parsedElements = new ArrayList<>();
                for (Map<String, Object> element : elementsJson) {
                    parsedElements.add(parseElement(element));
                }

                return new UIElementListResult(
                    result.getRequestId(),
                    true,
                    parsedElements,
                    data,
                    "json",
                    ""
                );
            } catch (Exception e) {
                return new UIElementListResult(
                    result.getRequestId(),
                    false,
                    new ArrayList<>(),
                    result.getData() == null ? "" : result.getData(),
                    formatNorm,
                    "Failed to parse UI elements data: " + e.getMessage()
                );
            }
        } catch (Exception e) {
            return new UIElementListResult(
                "",
                false,
                new ArrayList<>(),
                "",
                "json",
                "Failed to get all UI elements: " + e.getMessage()
            );
        }
    }

    /**
     * Retrieves all UI elements with default timeout (2000ms).
     *
     * @return UIElementListResult containing UI elements and error message if any
     */
    public UIElementListResult getAllUiElements() {
        return getAllUiElements(2000);
    }

    /**
     * Helper method to recursively parse a UI element and its children.
     */
    private Map<String, Object> parseElement(Map<String, Object> element) {
        Map<String, Object> parsed = new HashMap<>();
        parsed.put("bounds", element.getOrDefault("bounds", ""));
        parsed.put("className", element.getOrDefault("className", ""));
        parsed.put("text", element.getOrDefault("text", ""));
        parsed.put("type", element.getOrDefault("type", ""));
        parsed.put("resourceId", element.getOrDefault("resourceId", ""));
        parsed.put("index", element.getOrDefault("index", -1));
        parsed.put("isParent", element.getOrDefault("isParent", false));

        Object childrenObj = element.get("children");
        List<Map<String, Object>> children = new ArrayList<>();
        if (childrenObj instanceof List) {
            @SuppressWarnings("unchecked")
            List<Map<String, Object>> childrenList = (List<Map<String, Object>>) childrenObj;
            for (Map<String, Object> child : childrenList) {
                children.add(parseElement(child));
            }
        }
        parsed.put("children", children);

        return parsed;
    }

    // ==================== Application Management Operations ====================

    /**
     * Retrieves a list of installed applications.
     *
     * @param startMenu Whether to include start menu applications
     * @param desktop Whether to include desktop applications
     * @param ignoreSystemApps Whether to ignore system applications
     * @return InstalledAppListResult containing the list of installed applications
     */
    public InstalledAppListResult getInstalledApps(boolean startMenu, boolean desktop, boolean ignoreSystemApps) {
        try {
            Map<String, Object> args = new HashMap<>();
            args.put("start_menu", startMenu);
            args.put("desktop", desktop);
            args.put("ignore_system_apps", ignoreSystemApps);
            OperationResult result = callAppTool("get_installed_apps", args);

            if (!result.isSuccess()) {
                return new InstalledAppListResult(
                    result.getRequestId(),
                    false,
                    new ArrayList<>(),
                    result.getErrorMessage()
                );
            }

            try {
                String data = result.getData();
                if (data == null || data.isEmpty()) {
                    return new InstalledAppListResult(
                        result.getRequestId(),
                        true,
                        new ArrayList<>(),
                        ""
                    );
                }

                List<Map<String, Object>> appsJson = objectMapper.readValue(
                    data,
                    new TypeReference<List<Map<String, Object>>>() {}
                );

                List<InstalledApp> installedApps = new ArrayList<>();
                for (Map<String, Object> appData : appsJson) {
                    InstalledApp app = new InstalledApp();
                    if (appData.containsKey("name")) {
                        app.setName(String.valueOf(appData.get("name")));
                    }
                    if (appData.containsKey("start_cmd")) {
                        app.setStartCmd(String.valueOf(appData.get("start_cmd")));
                    }
                    if (appData.containsKey("stop_cmd")) {
                        Object stopCmdObj = appData.get("stop_cmd");
                        if (stopCmdObj != null) {
                            app.setStopCmd(String.valueOf(stopCmdObj));
                        }
                    }
                    if (appData.containsKey("work_directory")) {
                        Object workDirObj = appData.get("work_directory");
                        if (workDirObj != null) {
                            app.setWorkDirectory(String.valueOf(workDirObj));
                        }
                    }
                    installedApps.add(app);
                }

                return new InstalledAppListResult(
                    result.getRequestId(),
                    true,
                    installedApps,
                    ""
                );
            } catch (Exception e) {
                return new InstalledAppListResult(
                    result.getRequestId(),
                    false,
                    new ArrayList<>(),
                    "Failed to parse installed apps JSON: " + e.getMessage()
                );
            }
        } catch (Exception e) {
            return new InstalledAppListResult(
                "",
                false,
                new ArrayList<>(),
                "Failed to get installed apps: " + e.getMessage()
            );
        }
    }

    /**
     * Retrieves a list of installed applications with default parameters.
     *
     * @return InstalledAppListResult containing the list of installed applications
     */
    public InstalledAppListResult getInstalledApps() {
        return getInstalledApps(true, false, true);
    }

    /**
     * Starts an application with the given command, optional working directory and optional activity.
     *
     * @param startCmd The command to start the application
     * @param workDirectory Optional working directory for the application
     * @param activity Optional activity name to launch (e.g. ".SettingsActivity" or "com.package/.Activity")
     * @return ProcessListResult containing the list of processes started
     */
    public ProcessListResult startApp(String startCmd, String workDirectory, String activity) {
        try {
            Map<String, Object> args = new HashMap<>();
            args.put("start_cmd", startCmd);
            if (workDirectory != null && !workDirectory.isEmpty()) {
                args.put("work_directory", workDirectory);
            }
            if (activity != null && !activity.isEmpty()) {
                args.put("activity", activity);
            }
            OperationResult result = callAppTool("start_app", args);

            if (!result.isSuccess()) {
                return new ProcessListResult(
                    result.getRequestId(),
                    false,
                    new ArrayList<>(),
                    result.getErrorMessage()
                );
            }

            try {
                String data = result.getData();
                if (data == null || data.isEmpty()) {
                    return new ProcessListResult(
                        result.getRequestId(),
                        true,
                        new ArrayList<>(),
                        ""
                    );
                }

                List<Map<String, Object>> processesJson = objectMapper.readValue(
                    data,
                    new TypeReference<List<Map<String, Object>>>() {}
                );

                List<Process> processes = new ArrayList<>();
                for (Map<String, Object> processData : processesJson) {
                    Process process = new Process();
                    if (processData.containsKey("pname")) {
                        process.setPname(String.valueOf(processData.get("pname")));
                    }
                    if (processData.containsKey("pid")) {
                        Object pidObj = processData.get("pid");
                        if (pidObj instanceof Number) {
                            process.setPid(((Number) pidObj).intValue());
                        }
                    }
                    if (processData.containsKey("cmdline")) {
                        process.setCmdline(String.valueOf(processData.get("cmdline")));
                    }
                    processes.add(process);
                }

                return new ProcessListResult(
                    result.getRequestId(),
                    true,
                    processes,
                    ""
                );
            } catch (Exception e) {
                return new ProcessListResult(
                    result.getRequestId(),
                    false,
                    new ArrayList<>(),
                    "Failed to parse processes JSON: " + e.getMessage()
                );
            }
        } catch (Exception e) {
            return new ProcessListResult(
                "",
                false,
                new ArrayList<>(),
                "Failed to start app: " + e.getMessage()
            );
        }
    }

    /**
     * Starts an application with the given command and optional working directory.
     *
     * @param startCmd The command to start the application
     * @param workDirectory Optional working directory for the application
     * @return ProcessListResult containing the list of processes started
     */
    public ProcessListResult startApp(String startCmd, String workDirectory) {
        return startApp(startCmd, workDirectory, "");
    }

    /**
     * Starts an application with the given command.
     *
     * @param startCmd The command to start the application
     * @return ProcessListResult containing the list of processes started
     */
    public ProcessListResult startApp(String startCmd) {
        return startApp(startCmd, "", "");
    }

    /**
     * Stops an application by stop command.
     *
     * @param stopCmd The command to stop the application
     * @return AppOperationResult containing the result of the operation
     */
    public AppOperationResult stopAppByCmd(String stopCmd) {
        try {
            Map<String, Object> args = new HashMap<>();
            args.put("stop_cmd", stopCmd);
            OperationResult result = callAppTool("stop_app_by_cmd", args);

            return new AppOperationResult(
                result.getRequestId(),
                result.isSuccess(),
                result.getErrorMessage()
            );
        } catch (Exception e) {
            return new AppOperationResult(
                "",
                false,
                "Failed to stop app by cmd: " + e.getMessage()
            );
        }
    }

    // ==================== Screenshot Operations ====================

    /**
     * Takes a screenshot of the current screen.
     *
     * @return OperationResult containing the path/URL to the screenshot and error message if any
     */
    public OperationResult screenshot() {
        try {
            OperationResult result = callSystemScreenshotTool();

            if (!result.isSuccess()) {
                return new OperationResult(
                    result.getRequestId(),
                    false,
                    null,
                    result.getErrorMessage()
                );
            }

            return new OperationResult(
                result.getRequestId(),
                true,
                result.getData(),
                ""
            );
        } catch (Exception e) {
            return new OperationResult(
                "",
                false,
                null,
                "Failed to take screenshot: " + e.getMessage()
            );
        }
    }

    /**
     * Captures the current screen as a PNG image and returns raw image bytes.
     *
     * @return ScreenshotBytesResult containing PNG bytes and error message if any
     */
    public ScreenshotBytesResult betaTakeScreenshot() {
        try {
            Map<String, Object> args = new HashMap<>();
            args.put("format", "png");
            OperationResult result = callCaptureTool("screenshot", args);

            if (!result.isSuccess()) {
                return new ScreenshotBytesResult(
                    result.getRequestId(),
                    false,
                    new byte[0],
                    "png",
                    result.getErrorMessage()
                );
            }

            DecodedImage decoded = decodeBase64Image(result.getData(), "png");
            return new ScreenshotBytesResult(
                result.getRequestId(),
                true,
                decoded.bytes,
                decoded.format,
                ""
            );
        } catch (Exception e) {
            return new ScreenshotBytesResult(
                "",
                false,
                new byte[0],
                "png",
                "Failed to take screenshot: " + e.getMessage()
            );
        }
    }

    /**
     * Captures a long screenshot and returns raw image bytes.
     *
     * Supported formats:
     * - "png"
     * - "jpeg" (or "jpg")
     *
     * @param maxScreens Number of screens to stitch (range: [2, 10])
     * @param format Output image format ("png" or "jpeg")
     * @param quality JPEG quality (range: [1, 100]). Only used for jpeg.
     * @return ScreenshotBytesResult containing image bytes and error message if any
     */
    public ScreenshotBytesResult betaTakeLongScreenshot(int maxScreens, String format, Integer quality) {
        try {
            if (maxScreens < 2 || maxScreens > 10) {
                return new ScreenshotBytesResult("", false, new byte[0], "", "Invalid maxScreens: must be in range [2, 10]");
            }

            String formatNorm = normalizeImageFormat(format, "png");
            if (!"png".equals(formatNorm) && !"jpeg".equals(formatNorm)) {
                return new ScreenshotBytesResult(
                    "",
                    false,
                    new byte[0],
                    formatNorm,
                    "Unsupported format: " + format + ". Supported values: 'png', 'jpeg'."
                );
            }
            if (quality != null) {
                if (quality < 1 || quality > 100) {
                    return new ScreenshotBytesResult("", false, new byte[0], formatNorm, "Invalid quality: must be in range [1, 100]");
                }
            }

            Map<String, Object> args = new HashMap<>();
            args.put("max_screens", maxScreens);
            args.put("format", formatNorm);
            if (quality != null) {
                args.put("quality", quality);
            }

            OperationResult result = callCaptureTool("long_screenshot", args);
            if (!result.isSuccess()) {
                return new ScreenshotBytesResult(
                    result.getRequestId(),
                    false,
                    new byte[0],
                    formatNorm,
                    result.getErrorMessage()
                );
            }

            DecodedImage decoded = decodeBase64Image(result.getData(), formatNorm);
            return new ScreenshotBytesResult(
                result.getRequestId(),
                true,
                decoded.bytes,
                decoded.format,
                ""
            );
        } catch (Exception e) {
            return new ScreenshotBytesResult(
                "",
                false,
                new byte[0],
                normalizeImageFormat(format, "png"),
                "Failed to take long screenshot: " + e.getMessage()
            );
        }
    }

    public ScreenshotBytesResult betaTakeLongScreenshot(int maxScreens, String format) {
        return betaTakeLongScreenshot(maxScreens, format, null);
    }

    public ScreenshotBytesResult betaTakeLongScreenshot(int maxScreens) {
        return betaTakeLongScreenshot(maxScreens, "png", null);
    }

    // ==================== Mobile Configuration Operations ====================

    /**
     * Configure mobile settings from MobileExtraConfig.
     * This method is typically called automatically during session creation when
     * MobileExtraConfig is provided in CreateSessionParams.
     *
     * @param mobileConfig Mobile configuration object
     */
    public void configure(MobileExtraConfig mobileConfig) {
        if (mobileConfig == null) {
            return;
        }

        // Configure resolution lock
        if (mobileConfig.getLockResolution() != null) {
            setResolutionLock(mobileConfig.getLockResolution());
        }

        // Configure app management rules
        if (mobileConfig.getAppManagerRule() != null && mobileConfig.getAppManagerRule().getRuleType() != null) {
            AppManagerRule appRule = mobileConfig.getAppManagerRule();
            List<String> packageNames = appRule.getAppPackageNameList();

            if (packageNames != null && !packageNames.isEmpty()) {
                String ruleType = appRule.getRuleType();
                if ("White".equals(ruleType)) {
                    setAppWhitelist(packageNames);
                } else if ("Black".equals(ruleType)) {
                    setAppBlacklist(packageNames);
                }
            } else if (packageNames == null || packageNames.isEmpty()) {
            }
        }

        // Configure navigation bar visibility
        if (mobileConfig.getHideNavigationBar() != null) {
            setNavigationBarVisibility(mobileConfig.getHideNavigationBar());
        }

        // Configure uninstall blacklist
        if (mobileConfig.getUninstallBlacklist() != null && !mobileConfig.getUninstallBlacklist().isEmpty()) {
            setUninstallBlacklist(mobileConfig.getUninstallBlacklist());
        }
    }

    /**
     * Set display resolution lock for mobile devices.
     *
     * @param enable True to enable, False to disable
     */
    public void setResolutionLock(boolean enable) {
        executeTemplateCommand("resolution_lock", enable ? 1 : 0, 
            "Resolution lock " + (enable ? "enable" : "disable"));
    }

    /**
     * Set application whitelist.
     *
     * @param packageNames List of Android package names to whitelist
     */
    public void setAppWhitelist(List<String> packageNames) {
        if (packageNames == null || packageNames.isEmpty()) {
            return;
        }
        executeAppListCommand("app_whitelist", packageNames, 
            "App whitelist configuration (" + packageNames.size() + " packages)");
    }

    /**
     * Set application blacklist.
     *
     * @param packageNames List of Android package names to blacklist
     */
    public void setAppBlacklist(List<String> packageNames) {
        if (packageNames == null || packageNames.isEmpty()) {
            return;
        }
        executeAppListCommand("app_blacklist", packageNames, 
            "App blacklist configuration (" + packageNames.size() + " packages)");
    }

    /**
     * Set navigation bar visibility for mobile devices.
     *
     * @param hide True to hide navigation bar, False to show navigation bar
     */
    public void setNavigationBarVisibility(boolean hide) {
        String templateName = hide ? "hide_navigation_bar" : "show_navigation_bar";
        executeSimpleCommand(templateName, "Navigation bar visibility (hide: " + hide + ")");
    }

    /**
     * Set uninstall protection blacklist for mobile devices.
     *
     * @param packageNames List of Android package names to protect from uninstallation
     */
    public void setUninstallBlacklist(List<String> packageNames) {
        if (packageNames == null || packageNames.isEmpty()) {
            return;
        }
        executeAppListCommand("uninstall_blacklist", packageNames, 
            "Uninstall blacklist configuration (" + packageNames.size() + " packages)");
    }

    /**
     * Retrieves the ADB connection URL for the mobile environment.
     *
     * @param adbkeyPub The ADB public key for connection authentication
     * @return AdbUrlResult containing the ADB connection URL and request ID
     */
    public AdbUrlResult getAdbUrl(String adbkeyPub) {
        try {
            // Call get_adb_link API via ApiClient
            com.aliyun.wuyingai20250506.models.GetAdbLinkResponse response = 
                session.getAgentBay().getApiClient().getAdbLink(
                    session.getSessionId(), 
                    adbkeyPub
                );

            // Check response
            if (response != null && response.getBody() != null) {
                com.aliyun.wuyingai20250506.models.GetAdbLinkResponseBody body = response.getBody();
                
                if (body.getSuccess() != null && body.getSuccess() && body.getData() != null) {
                    String adbUrl = body.getData().getUrl();
                    String requestId = body.getRequestId() != null ? body.getRequestId() : "";
                    return new AdbUrlResult(
                        requestId,
                        true,
                        adbUrl,
                        ""
                    );
                } else {
                    String errorMsg = body.getMessage() != null ? body.getMessage() : "Unknown error";
                    String requestId = body.getRequestId() != null ? body.getRequestId() : "";
                    return new AdbUrlResult(
                        requestId,
                        false,
                        null,
                        errorMsg
                    );
                }
            } else {
                return new AdbUrlResult(
                    "",
                    false,
                    null,
                    "No response from server"
                );
            }

        } catch (Exception e) {
            String errorMsg = "Failed to get ADB URL: " + e.getMessage();
            return new AdbUrlResult(
                "",
                false,
                null,
                errorMsg
            );
        }
    }

    // ==================== Helper Methods ====================

    /**
     * Execute a template command for resolution lock.
     */
    private void executeTemplateCommand(String templateName, int lockSwitch, String operationName) {
        try {
            String command = String.format("setprop sys.wuying.lockres %d", lockSwitch);
            // Execute via command service if available
            if (session.getCommand() != null) {
                CommandResult result = session.getCommand().executeCommand(command, 5000);
                if (result.isSuccess()) {
                } else {
                }
            }
        } catch (Exception e) {
        }
    }

    /**
     * Execute an app list command (whitelist/blacklist/uninstall blacklist).
     */
    private void executeAppListCommand(String templateName, List<String> packageNames, String operationName) {
        try {
            String packageList = String.join("\n", packageNames);
            String command = buildAppListCommand(templateName, packageList);
            // Execute via command service if available
            if (session.getCommand() != null) {
                CommandResult result = session.getCommand().executeCommand(command, 5000);
                if (result.isSuccess()) {
                } else {
                }
            }
        } catch (Exception e) {
        }
    }

    /**
     * Build command for app list operations (whitelist/blacklist) based on Python implementation.
     */
    private String buildAppListCommand(String templateName, String packageList) {
        if ("app_whitelist".equals(templateName)) {
            return String.format(
                "cat > /data/system/pm_whitelist.txt << 'EOF'\n%s\nEOF\n" +
                "chmod 644 /data/system/pm_whitelist.txt\n" +
                "setprop rw.wy.pm_whitelist.refresh 1\n" +
                "setprop persist.wy.pm_blacklist.switch 2",
                packageList
            );
        } else if ("app_blacklist".equals(templateName)) {
            return String.format(
                "cat > /data/system/pm_blacklist.txt << 'EOF'\n%s\nEOF\n" +
                "chmod 644 /data/system/pm_blacklist.txt\n" +
                "setprop rw.wy.pm_blacklist.refresh 1\n" +
                "setprop persist.wy.pm_blacklist.switch 1",
                packageList
            );
        } else if ("uninstall_blacklist".equals(templateName)) {
            long timestamp = System.currentTimeMillis() / 1000;
            return String.format(
                "cat > /data/system/pm_lock.conf << 'EOF'\n%s\nEOF\n" +
                "chmod 644 /data/system/pm_lock.conf\n" +
                "setprop persist.wy.pm_lock.trigger %d",
                packageList, timestamp
            );
        }
        throw new IllegalArgumentException("Unknown template: " + templateName);
    }

    /**
     * Execute a simple command template (navigation bar visibility).
     */
    private void executeSimpleCommand(String templateName, String operationName) {
        try {
            String command;
            if ("hide_navigation_bar".equals(templateName)) {
                command = "setprop persist.wy.hasnavibar false; killall com.android.systemui";
            } else {
                command = "setprop persist.wy.hasnavibar true; killall com.android.systemui";
            }
            // Execute via command service if available
            if (session.getCommand() != null) {
                CommandResult result = session.getCommand().executeCommand(command, 5000);
                if (result.isSuccess()) {
                } else {
                }
            }
        } catch (Exception e) {
        }
    }

    private static class DecodedImage {
        final byte[] bytes;
        final String format;

        DecodedImage(byte[] bytes, String format) {
            this.bytes = bytes;
            this.format = format;
        }
    }

    private static String normalizeImageFormat(String format, String defaultValue) {
        String f = format == null ? "" : format.trim().toLowerCase();
        if (f.isEmpty()) {
            return defaultValue;
        }
        if ("jpg".equals(f)) {
            return "jpeg";
        }
        return f;
    }

    private static DecodedImage decodeBase64Image(String data, String expectedFormat) {
        if (data == null) {
            throw new IllegalArgumentException("Empty image data");
        }

        String s = data.trim();
        if (s.isEmpty()) {
            throw new IllegalArgumentException("Empty image data");
        }
        // The screenshot tool returns a base64 string (or a data URL). We do not
        // attempt to parse arbitrary JSON payloads here.
        if (s.startsWith("{") || s.startsWith("[")) {
            throw new IllegalArgumentException("Unexpected JSON image data");
        }

        String lower = s.toLowerCase();
        String formatHint = "";
        if (lower.startsWith("data:image/")) {
            int base64Idx = lower.indexOf("base64,");
            if (base64Idx < 0) {
                throw new IllegalArgumentException("Invalid data URL: missing base64 marker");
            }
            String header = lower.substring("data:image/".length(), base64Idx);
            int semi = header.indexOf(";");
            String mime = (semi >= 0 ? header.substring(0, semi) : header).trim();
            if ("png".equals(mime)) {
                formatHint = "png";
            } else if ("jpeg".equals(mime) || "jpg".equals(mime)) {
                formatHint = "jpeg";
            }
        }

        int idx = lower.indexOf("base64,");
        if (idx >= 0) {
            s = s.substring(idx + "base64,".length()).trim();
        }
        s = s.replace("\n", "").replace("\r", "").replace("\t", "").replace(" ", "");
        int mod = s.length() % 4;
        if (mod != 0) {
            s = s + "====".substring(mod);
        }

        byte[] decoded = Base64.getDecoder().decode(s);

        String fmt = expectedFormat;
        if (startsWith(decoded, PNG_MAGIC)) {
            fmt = "png";
        } else if (startsWith(decoded, JPEG_MAGIC)) {
            fmt = "jpeg";
        } else if (!formatHint.isEmpty()) {
            fmt = formatHint;
        }
        return new DecodedImage(decoded, fmt);
    }

    private static boolean startsWith(byte[] data, byte[] prefix) {
        if (data == null || prefix == null || data.length < prefix.length) {
            return false;
        }
        for (int i = 0; i < prefix.length; i++) {
            if (data[i] != prefix[i]) {
                return false;
            }
        }
        return true;
    }
}
