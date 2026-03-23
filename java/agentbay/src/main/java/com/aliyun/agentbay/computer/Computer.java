package com.aliyun.agentbay.computer;

import com.aliyun.agentbay.model.AppOperationResult;
import com.aliyun.agentbay.model.BoolResult;
import com.aliyun.agentbay.model.InstalledApp;
import com.aliyun.agentbay.model.InstalledAppListResult;
import com.aliyun.agentbay.model.OperationResult;
import com.aliyun.agentbay.model.Process;
import com.aliyun.agentbay.model.ProcessListResult;
import com.aliyun.agentbay.model.ScreenshotBytesResult;
import com.aliyun.agentbay.model.Window;
import com.aliyun.agentbay.model.WindowInfoResult;
import com.aliyun.agentbay.model.WindowListResult;
import com.aliyun.agentbay.service.BaseService;
import com.aliyun.agentbay.session.Session;
import com.fasterxml.jackson.core.type.TypeReference;
import com.fasterxml.jackson.databind.ObjectMapper;

import java.util.ArrayList;
import java.util.Arrays;
import java.util.HashMap;
import java.util.List;
import java.util.Map;
import java.util.Base64;

/**
 * Computer module for desktop UI automation.
 * Provides comprehensive desktop automation capabilities including mouse, keyboard,window management, application management, and screen operations.
 */
public class Computer extends BaseService {
    private static final ObjectMapper objectMapper = new ObjectMapper();
    private static final String SERVER_UI = "wuying_ui";
    private static final String SERVER_APP = "wuying_app";
    private static final String SERVER_CAPTURE = "wuying_capture";
    private static final String SERVER_SYSTEM_SCREENSHOT = "mcp-server";
    private static final byte[] PNG_MAGIC = new byte[] {(byte) 0x89, 0x50, 0x4e, 0x47, 0x0d, 0x0a, 0x1a, 0x0a};
    private static final byte[] JPEG_MAGIC = new byte[] {(byte) 0xff, (byte) 0xd8, (byte) 0xff};

    public Computer(Session session) {
        super(session);
    }

    private OperationResult callUiTool(String toolName, Map<String, Object> args) {
        return callMcpTool(toolName, args);
    }

    private OperationResult callAppTool(String toolName, Map<String, Object> args) {
        return callMcpTool(toolName, args);
    }

    private OperationResult callCaptureTool(String toolName, Map<String, Object> args) {
        return callMcpTool(toolName, args);
    }

    private OperationResult callSystemScreenshotTool() {
        return callMcpTool("system_screenshot", new HashMap<>());
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

    /**
     * Starts an application with the given command, optional working directory and optional activity.
     *
     * @param startCmd The command to start the application
     * @param workDirectory working directory for the application
     * @param activity activity name to launch (for mobile apps). Defaults to empty string.
     * @return ProcessListResult containing the list of processes started and error message if any.
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
                // Parse the JSON response to get list of processes
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
     * @param workDirectory working directory for the application
     * @return ProcessListResult containing the list of processes started and error message if any.
     */
    public ProcessListResult startApp(String startCmd, String workDirectory) {
        return startApp(startCmd, workDirectory, "");
    }

    /**
     * Starts an application with the given command.
     *
     * @param startCmd The command to start the application
     * @return ProcessListResult containing the list of processes started and error message if any.
     */
    public ProcessListResult startApp(String startCmd) {
        return startApp(startCmd, "", "");
    }

    /**
     * Stops an application by process name.
     *
     * @param pname The process name of the application to stop
     * @return AppOperationResult containing success status and error message if any
     */
    public AppOperationResult stopAppByPName(String pname) {
        try {
            Map<String, Object> args = new HashMap<>();
            args.put("pname", pname);

            OperationResult result = callAppTool("stop_app_by_pname", args);

            return new AppOperationResult(
                result.getRequestId(),
                result.isSuccess(),
                result.getErrorMessage()
            );
        } catch (Exception e) {
            return new AppOperationResult(
                "",
                false,
                "Failed to stop app by pname: " + e.getMessage()
            );
        }
    }

    /**
     * Stops an application by process ID.
     *
     * @param pid The process ID of the application to stop
     * @return AppOperationResult containing success status and error message if any
     */
    public AppOperationResult stopAppByPID(int pid) {
        try {
            Map<String, Object> args = new HashMap<>();
            args.put("pid", pid);

            OperationResult result = callAppTool("stop_app_by_pid", args);

            return new AppOperationResult(
                result.getRequestId(),
                result.isSuccess(),
                result.getErrorMessage()
            );
        } catch (Exception e) {
            return new AppOperationResult(
                "",
                false,
                "Failed to stop app by pid: " + e.getMessage()
            );
        }
    }

    /**
     * Stops an application by stop command.
     *
     * @param stopCmd The command to stop the application
     * @return AppOperationResult containing success status and error message if any
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

    /**
     * Lists all applications with visible windows.
     * Returns detailed process information for applications that have visible windows,including process ID, name, command line, and other system information.
     * This is useful for system monitoring and process management tasks.
     *
     * @return ProcessListResult containing list of visible applications with detailed process information
     * 
     * @see #startApp(String)
     * @see #stopAppByPName(String)
     * @see #getInstalledApps()
     */
    public ProcessListResult listVisibleApps() {
        try {

            OperationResult result = callAppTool("list_visible_apps", new HashMap<>());

            if (!result.isSuccess()) {
                return new ProcessListResult(
                    result.getRequestId(),
                    false,
                    new ArrayList<>(),
                    result.getErrorMessage()
                );
            }

            try {
                // Parse the JSON response to get list of processes
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
                "Failed to list visible apps: " + e.getMessage()
            );
        }
    }

    /**
     * Gets the list of installed applications.
     *
     * @param startMenu Whether to include start menu applications. Defaults to true.
     * @param desktop Whether to include desktop applications. Defaults to false.
     * @param ignoreSystemApps Whether to ignore system applications. Defaults to true.
     * @return InstalledAppListResult containing list of installed apps and error message if any
     */
    public InstalledAppListResult getInstalledApps(boolean startMenu, boolean desktop, boolean ignoreSystemApps) {
        try {
            Map<String, Object> args = new HashMap<>();
            args.put("start_menu", startMenu);
            args.put("desktop", desktop);
            args.put("ignore_system_app", ignoreSystemApps);

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
                // Parse the JSON response to get list of installed apps
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
     * Gets the list of installed applications with default parameters.
     * Defaults: startMenu=true, desktop=false, ignoreSystemApps=true
     *
     * @return InstalledAppListResult containing list of installed apps and error message if any
     */
    public InstalledAppListResult getInstalledApps() {
        return getInstalledApps(true, false, true);
    }

    // ==================== Mouse Operations ====================

    /**
     * Clicks the mouse at the specified screen coordinates.
     *
     * @param x X coordinate in pixels (0 is left edge of screen)
     * @param y Y coordinate in pixels (0 is top edge of screen)
     * @param button Mouse button to click. Options:
     *               - MouseButton.LEFT: Single left click
     *               - MouseButton.RIGHT: Right click (context menu)
     *               - MouseButton.MIDDLE: Middle click (scroll wheel)
     *               - MouseButton.DOUBLE_LEFT: Double left click
     *               Defaults to MouseButton.LEFT
     * @return BoolResult Object containing:
     *         - success (boolean): Whether the click succeeded
     *         - data (Boolean): True if successful, null otherwise
     *         - errorMessage (String): Error description if failed
     * @throws IllegalArgumentException If button is not one of the valid options
     * 
     * <p>Behavior:
     * <ul>
     *   <li>Clicks at the exact pixel coordinates provided</li>
     *   <li>Does not move the mouse cursor before clicking</li>
     *   <li>For double-click, use MouseButton.DOUBLE_LEFT</li>
     *   <li>Right-click typically opens context menus</li>
     * </ul>
     * 
     * 
     * <p>Note:
     * <ul>
     *   <li>Coordinates are absolute screen positions, not relative to windows</li>
     *   <li>Use getScreenSize() to determine valid coordinate ranges</li>
     *   <li>Consider using moveMouse() first if you need to see cursor movement</li>
     * </ul>
     * 
     */
    public BoolResult clickMouse(int x, int y, MouseButton button) {
        return clickMouse(x, y, button.getValue());
    }

    /**
     * Clicks the mouse at the specified screen coordinates with LEFT button.
     *
     * @param x X coordinate in pixels
     * @param y Y coordinate in pixels
     * @return BoolResult containing success status and error message if any
     */
    public BoolResult clickMouse(int x, int y) {
        return clickMouse(x, y, MouseButton.LEFT);
    }

    /**
     * Clicks the mouse at the specified screen coordinates.
     *
     * @param x X coordinate in pixels
     * @param y Y coordinate in pixels
     * @param button Mouse button as string ("left", "right", "middle", "double_left")
     * @return BoolResult containing success status and error message if any
     */
    public BoolResult clickMouse(int x, int y, String button) {
        try {
            List<String> validButtons = Arrays.asList("left", "right", "middle", "double_left");
            if (!validButtons.contains(button)) {
                throw new IllegalArgumentException(
                    "Invalid button '" + button + "'. Must be one of " + validButtons
                );
            }

            Map<String, Object> args = new HashMap<>();
            args.put("x", x);
            args.put("y", y);
            args.put("button", button);

            OperationResult result = callUiTool("click_mouse", args);

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
                "Failed to click mouse: " + e.getMessage()
            );
        }
    }

    /**
     * Moves the mouse to the specified coordinates.
     *
     * @param x X coordinate
     * @param y Y coordinate
     * @return BoolResult Result object containing success status and error message if any
     * 
     * 
     * <p>Note:
     * <ul>
     *   <li>Moves the cursor smoothly to the target position</li>
     *   <li>Does not click after moving</li>
     *   <li>Use getCursorPosition() to verify the new position</li>
     * </ul>
     * 
     * @see #clickMouse(int, int, MouseButton)
     * @see #dragMouse(int, int, int, int, MouseButton)
     * @see #getCursorPosition()
     */
    public BoolResult moveMouse(int x, int y) {
        try {
            Map<String, Object> args = new HashMap<>();
            args.put("x", x);
            args.put("y", y);

            OperationResult result = callUiTool("move_mouse", args);

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
                "Failed to move mouse: " + e.getMessage()
            );
        }
    }

    /**
     * Drags the mouse from one point to another.
     *
     * @param fromX Starting X coordinate
     * @param fromY Starting Y coordinate
     * @param toX Ending X coordinate
     * @param toY Ending Y coordinate
     * @param button Mouse button to use. Defaults to LEFT
     * @return BoolResult containing success status and error message if any
     */
    public BoolResult dragMouse(int fromX, int fromY, int toX, int toY, MouseButton button) {
        return dragMouse(fromX, fromY, toX, toY, button.getValue());
    }

    /**
     * Drags the mouse from one point to another with LEFT button.
     *
     * @param fromX Starting X coordinate
     * @param fromY Starting Y coordinate
     * @param toX Ending X coordinate
     * @param toY Ending Y coordinate
     * @return BoolResult containing success status and error message if any
     */
    public BoolResult dragMouse(int fromX, int fromY, int toX, int toY) {
        return dragMouse(fromX, fromY, toX, toY, MouseButton.LEFT);
    }

    /**
     * Drags the mouse from one point to another.
     *
     * @param fromX Starting X coordinate
     * @param fromY Starting Y coordinate
     * @param toX Ending X coordinate
     * @param toY Ending Y coordinate
     * @param button Mouse button as string. Valid values: "left", "right", "middle"
     *               Note: "double_left" is not supported for drag operations
     * @return BoolResult Result object containing success status and error message if any
     * @throws IllegalArgumentException If button is not a valid option
     * 
     * <p>Note:
     * <ul>
     *   <li>Performs a click-and-drag operation from start to end coordinates</li>
     *   <li>Useful for selecting text, moving windows, or drawing</li>
     *   <li>DOUBLE_LEFT button is not supported for drag operations</li>
     *   <li>Use LEFT, RIGHT, or MIDDLE button only</li>
     * </ul>
     * 
     */
    public BoolResult dragMouse(int fromX, int fromY, int toX, int toY, String button) {
        try {
            List<String> validButtons = Arrays.asList("left", "right", "middle");
            if (!validButtons.contains(button)) {
                throw new IllegalArgumentException(
                    "Invalid button '" + button + "'. Must be one of " + validButtons
                );
            }

            Map<String, Object> args = new HashMap<>();
            args.put("from_x", fromX);
            args.put("from_y", fromY);
            args.put("to_x", toX);
            args.put("to_y", toY);
            args.put("button", button);
            OperationResult result = callUiTool("drag_mouse", args);

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
                "Failed to drag mouse: " + e.getMessage()
            );
        }
    }

    /**
     * Scrolls the mouse wheel at the specified coordinates.
     *
     * @param x X coordinate
     * @param y Y coordinate
     * @param direction Scroll direction. Defaults to UP
     * @param amount Scroll amount. Defaults to 1
     * @return BoolResult containing success status and error message if any
     */
    public BoolResult scroll(int x, int y, ScrollDirection direction, int amount) {
        return scroll(x, y, direction.getValue(), amount);
    }

    /**
     * Scrolls the mouse wheel at the specified coordinates with default direction (UP) and amount (1).
     *
     * @param x X coordinate
     * @param y Y coordinate
     * @return BoolResult containing success status and error message if any
     */
    public BoolResult scroll(int x, int y) {
        return scroll(x, y, ScrollDirection.UP, 1);
    }

    /**
     * Scrolls the mouse wheel at the specified coordinates.
     *
     * @param x X coordinate
     * @param y Y coordinate
     * @param direction Scroll direction as string. Valid values: "up", "down", "left", "right"
     * @param amount Scroll amount. Defaults to 1
     * @return BoolResult Result object containing success status and error message if any
     * @throws IllegalArgumentException If direction is not a valid option
     * 
     * <p>Note:
     * <ul>
     *   <li>Scroll operations are performed at the specified coordinates</li>
     *   <li>The amount parameter controls how many scroll units to move</li>
     *   <li>Larger amounts result in faster scrolling</li>
     *   <li>Useful for navigating long documents or web pages</li>
     * </ul>
     * 
     */
    public BoolResult scroll(int x, int y, String direction, int amount) {
        try {
            List<String> validDirections = Arrays.asList("up", "down", "left", "right");
            if (!validDirections.contains(direction)) {
                throw new IllegalArgumentException(
                    "Invalid direction '" + direction + "'. Must be one of " + validDirections
                );
            }

            Map<String, Object> args = new HashMap<>();
            args.put("x", x);
            args.put("y", y);
            args.put("direction", direction);
            args.put("amount", amount);
            OperationResult result = callUiTool("scroll", args);

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
                "Failed to scroll: " + e.getMessage()
            );
        }
    }

    /**
     * Gets the current cursor position.
     *
     * @return OperationResult Result object containing cursor position data with keys 'x' and 'y', and error message if any
     * 
     * <p>Note:
     * <ul>
     *   <li>Returns the absolute screen coordinates</li>
     *   <li>Useful for verifying mouse movements</li>
     *   <li>Position is in pixels from top-left corner (0, 0)</li>
     * </ul>
     * 
     * @see #moveMouse(int, int)
     * @see #clickMouse(int, int, MouseButton)
     * @see #getScreenSize()
     */
    public OperationResult getCursorPosition() {
        try {
            OperationResult result = callUiTool("get_cursor_position", new HashMap<>());

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
                "Failed to get cursor position: " + e.getMessage()
            );
        }
    }

    // ==================== Keyboard Operations ====================

    /**
     * Types text into the currently focused input field.
     *
     * @param text The text to input. Supports Unicode characters
     * @return BoolResult Object with success status and error message if any
     * 
     * <p>Note:
     * <ul>
     *   <li>Requires an input field to be focused first</li>
     *   <li>Use clickMouse() or UI automation to focus the field</li>
     *   <li>Supports special characters and Unicode</li>
     * </ul>
     * 
     * @see #pressKeys(List, boolean)
     * @see #clickMouse(int, int, MouseButton)
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
     * Presses the specified keys.
     *
     * @param keys List of keys to press (e.g., Arrays.asList("Ctrl", "a"))
     * @param hold Whether to hold the keys. Defaults to false
     * @return BoolResult Result object containing success status and error message if any
     * 
     * <p>Note:
     * <ul>
     *   <li>Key names are case-sensitive</li>
     *   <li>When hold=true, remember to call releaseKeys() afterwards</li>
     *   <li>Supports modifier keys like Ctrl, Alt, Shift</li>
     *   <li>Can press multiple keys simultaneously for shortcuts</li>
     * </ul>
     * 
     * @see #releaseKeys(List)
     * @see #inputText(String)
     */
    public BoolResult pressKeys(List<String> keys, boolean hold) {
        try {
            Map<String, Object> args = new HashMap<>();
            args.put("keys", keys);
            args.put("hold", hold);
            OperationResult result = callUiTool("press_keys", args);

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
                "Failed to press keys: " + e.getMessage()
            );
        }
    }

    /**
     * Presses the specified keys without holding.
     *
     * @param keys List of keys to press
     * @return BoolResult containing success status and error message if any
     */
    public BoolResult pressKeys(List<String> keys) {
        return pressKeys(keys, false);
    }

    /**
     * Releases the specified keys.
     *
     * @param keys List of keys to release (e.g., Arrays.asList("Ctrl", "a"))
     * @return BoolResult Result object containing success status and error message if any
     * 
     * <p>Note:
     * <ul>
     *   <li>Should be used after pressKeys() with hold=true</li>
     *   <li>Key names are case-sensitive</li>
     *   <li>Releases all keys specified in the list</li>
     * </ul>
     * 
     * @see #pressKeys(List, boolean)
     * @see #inputText(String)
     */
    public BoolResult releaseKeys(List<String> keys) {
        try {
            Map<String, Object> args = new HashMap<>();
            args.put("keys", keys);
            OperationResult result = callUiTool("release_keys", args);

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
                "Failed to release keys: " + e.getMessage()
            );
        }
    }

    // ==================== Screen Operations ====================

    /**
     * Gets the screen size and DPI scaling factor.
     *
     * @return OperationResult Result object containing screen size data with keys 'width', 'height', and 'dpiScalingFactor', and error message if any
     * 
     * <p>Note:
     * <ul>
     *   <li>Returns the full screen dimensions in pixels</li>
     *   <li>DPI scaling factor affects coordinate calculations on high-DPI displays</li>
     *   <li>Use this to determine valid coordinate ranges for mouse operations</li>
     * </ul>
     * 
     * @see #clickMouse(int, int, MouseButton)
     * @see #moveMouse(int, int)
     * @see #screenshot()
     */
    public OperationResult getScreenSize() {
        try {
            OperationResult result = callUiTool("get_screen_size", new HashMap<>());

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
                "Failed to get screen size: " + e.getMessage()
            );
        }
    }

    /**
     * Takes a screenshot of the current screen.
     *
     * @return OperationResult Result object containing the path to the screenshot and error message if any
     * 
     * <p>Note:
     * <ul>
     *   <li>Returns an OSS URL to the screenshot image</li>
     *   <li>Screenshot captures the entire screen</li>
     *   <li>Useful for debugging and verification</li>
     *   <li>Image format is typically PNG</li>
     * </ul>
     * 
     * @see #getScreenSize()
     */
    @SuppressWarnings("deprecation")
    public OperationResult screenshot() {
        if (session.getLinkUrl() != null && !session.getLinkUrl().isEmpty()) {
            return new OperationResult(
                "",
                false,
                null,
                "This cloud environment does not support `screenshot()`. Please use `beta_take_screenshot()` instead."
            );
        }
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
     * Takes a screenshot of the Computer and returns raw binary image data (beta).
     *
     * <p>This API uses the MCP tool `screenshot` (wuying_capture) and returns raw
     * binary image data. The backend also returns the captured image dimensions
     * (width/height in pixels), which are exposed on ScreenshotBytesResult.width
     * and ScreenshotBytesResult.height. The backend metadata fields `type` and
     * `mime_type` are exposed on ScreenshotBytesResult.type and ScreenshotBytesResult.mimeType.
     *
     * @param format The desired image format (default: "png"). Supported: "png", "jpeg", "jpg"
     * @return ScreenshotBytesResult Object containing the screenshot image data (bytes) and metadata
     *         including `type`, `mimeType`, `width`, and `height` when provided by the backend
     * @throws IllegalArgumentException If format is invalid
     * 
     * <p>Supported formats:
     * <ul>
     *   <li>"png"</li>
     *   <li>"jpeg" (or "jpg")</li>
     * </ul>
     */
    @SuppressWarnings("deprecation")
    public ScreenshotBytesResult betaTakeScreenshot(String format) {
        String fmt = normalizeImageFormat(format, "png");
        if (session.getLinkUrl() == null || session.getLinkUrl().isEmpty()) {
            return new ScreenshotBytesResult(
                "",
                false,
                "",
                "",
                new byte[0],
                "This cloud environment does not support `beta_take_screenshot()`. Please use `screenshot()` instead."
            );
        }
        if (!"png".equals(fmt) && !"jpeg".equals(fmt)) {
            return new ScreenshotBytesResult("", false, "", "", new byte[0], null, null, "Unsupported format: " + format);
        }

        try {
            Map<String, Object> args = new HashMap<>();
            args.put("format", fmt);
            OperationResult result = callCaptureTool("screenshot", args);
            if (!result.isSuccess()) {
                return new ScreenshotBytesResult(
                    result.getRequestId(),
                    false,
                    "",
                    "",
                    new byte[0],
                    result.getErrorMessage()
                );
            }

            String s = result.getData() == null ? "" : result.getData().trim();
            if (!s.startsWith("{")) {
                return new ScreenshotBytesResult(
                    result.getRequestId(),
                    false,
                    "",
                    "",
                    new byte[0],
                    "Screenshot tool returned non-JSON data"
                );
            }

            @SuppressWarnings("unchecked")
            Map<String, Object> obj = objectMapper.readValue(s, Map.class);
            Object typeObj = obj.get("type");
            Object mimeTypeObj = obj.get("mime_type");
            Object b64Obj = obj.get("data");
            if (!(typeObj instanceof String) || ((String) typeObj).trim().isEmpty()) {
                return new ScreenshotBytesResult(
                    result.getRequestId(),
                    false,
                    "",
                    "",
                    new byte[0],
                    "Invalid screenshot JSON: expected non-empty string 'type'"
                );
            }
            if (!(mimeTypeObj instanceof String) || ((String) mimeTypeObj).trim().isEmpty()) {
                return new ScreenshotBytesResult(
                    result.getRequestId(),
                    false,
                    "",
                    "",
                    new byte[0],
                    "Invalid screenshot JSON: expected non-empty string 'mime_type'"
                );
            }
            if (!(b64Obj instanceof String) || ((String) b64Obj).trim().isEmpty()) {
                return new ScreenshotBytesResult(
                    result.getRequestId(),
                    false,
                    "",
                    "",
                    new byte[0],
                    "Screenshot JSON missing base64 field"
                );
            }
            Object widthObj = obj.get("width");
            Object heightObj = obj.get("height");
            Integer width = null;
            Integer height = null;
            if (widthObj != null) {
                if (!(widthObj instanceof Number)) {
                    return new ScreenshotBytesResult(
                        result.getRequestId(),
                        false,
                        "",
                        "",
                        new byte[0],
                        "Invalid screenshot JSON: expected integer 'width'"
                    );
                }
                width = ((Number) widthObj).intValue();
            }
            if (heightObj != null) {
                if (!(heightObj instanceof Number)) {
                    return new ScreenshotBytesResult(
                        result.getRequestId(),
                        false,
                        "",
                        "",
                        new byte[0],
                        "Invalid screenshot JSON: expected integer 'height'"
                    );
                }
                height = ((Number) heightObj).intValue();
            }

            byte[] decoded = Base64.getDecoder().decode(((String) b64Obj).trim());
            if ("png".equals(fmt) && !startsWith(decoded, PNG_MAGIC)) {
                return new ScreenshotBytesResult(
                    result.getRequestId(),
                    false,
                    "",
                    "",
                    new byte[0],
                    "Screenshot data does not match expected format 'png'"
                );
            }
            if ("jpeg".equals(fmt) && !startsWith(decoded, JPEG_MAGIC)) {
                return new ScreenshotBytesResult(
                    result.getRequestId(),
                    false,
                    "",
                    "",
                    new byte[0],
                    "Screenshot data does not match expected format 'jpeg'"
                );
            }

            String expectedMimeType = "png".equals(fmt) ? "image/png" : "jpeg".equals(fmt) ? "image/jpeg" : "";
            String mimeType = ((String) mimeTypeObj).trim();
            if (!expectedMimeType.isEmpty() && !expectedMimeType.equalsIgnoreCase(mimeType)) {
                return new ScreenshotBytesResult(
                    result.getRequestId(),
                    false,
                    "",
                    "",
                    new byte[0],
                    "Screenshot JSON mime_type does not match expected format: expected " + expectedMimeType + ", got " + mimeType
                );
            }

            return new ScreenshotBytesResult(
                result.getRequestId(),
                true,
                ((String) typeObj).trim(),
                mimeType,
                decoded,
                width,
                height,
                ""
            );
        } catch (Exception e) {
            return new ScreenshotBytesResult(
                "",
                false,
                "",
                "",
                new byte[0],
                "Failed to take screenshot: " + e.getMessage()
            );
        }
    }

    public ScreenshotBytesResult betaTakeScreenshot() {
        return betaTakeScreenshot("png");
    }

    // ==================== Window Management Operations ====================

    /**
     * Lists all root windows.
     *
     * @param timeoutMs Timeout in milliseconds. Defaults to 3000
     * @return WindowListResult Result object containing list of windows and error message if any
     * 
     */
    public WindowListResult listRootWindows(int timeoutMs) {
        try {
            Map<String, Object> args = new HashMap<>();
            args.put("timeout_ms", timeoutMs);
            OperationResult result = callUiTool("list_root_windows", args);

            if (!result.isSuccess()) {
                return new WindowListResult(
                    result.getRequestId(),
                    false,
                    new ArrayList<>(),
                    result.getErrorMessage()
                );
            }

            try {
                String data = result.getData();
                if (data == null || data.isEmpty()) {
                    return new WindowListResult(
                        result.getRequestId(),
                        true,
                        new ArrayList<>(),
                        ""
                    );
                }

                List<Map<String, Object>> windowsJson = objectMapper.readValue(
                    data,
                    new TypeReference<List<Map<String, Object>>>() {}
                );

                List<Window> windows = new ArrayList<>();
                for (Map<String, Object> windowData : windowsJson) {
                    windows.add(parseWindow(windowData));
                }

                return new WindowListResult(
                    result.getRequestId(),
                    true,
                    windows,
                    ""
                );
            } catch (Exception e) {
                return new WindowListResult(
                    result.getRequestId(),
                    false,
                    new ArrayList<>(),
                    "Failed to parse windows JSON: " + e.getMessage()
                );
            }
        } catch (Exception e) {
            return new WindowListResult(
                "",
                false,
                new ArrayList<>(),
                "Failed to list root windows: " + e.getMessage()
            );
        }
    }

    /**
     * Lists all root windows with default timeout (3000ms).
     *
     * @return WindowListResult containing list of windows and error message if any
     */
    public WindowListResult listRootWindows() {
        return listRootWindows(3000);
    }

    /**
     * Gets the currently active window.
     *
     * @param timeoutMs Timeout in milliseconds. Defaults to 3000
     * @return WindowInfoResult Result object containing active window info and error message if any
     * 
     * <p><strong>Note</strong>: Java version requires timeoutMs parameter, while Python version does not.
     * 
     * @see #listRootWindows()
     * @see #activateWindow(int)
     */
    public WindowInfoResult getActiveWindow(int timeoutMs) {
        try {
            Map<String, Object> args = new HashMap<>();
            args.put("timeout_ms", timeoutMs);
            OperationResult result = callUiTool("get_active_window", args);

            if (!result.isSuccess()) {
                return new WindowInfoResult(
                    result.getRequestId(),
                    false,
                    null,
                    result.getErrorMessage()
                );
            }

            try {
                String data = result.getData();
                if (data == null || data.isEmpty()) {
                    return new WindowInfoResult(
                        result.getRequestId(),
                        true,
                        null,
                        ""
                    );
                }

                Map<String, Object> windowData = objectMapper.readValue(
                    data,
                    new TypeReference<Map<String, Object>>() {}
                );

                Window window = parseWindow(windowData);

                return new WindowInfoResult(
                    result.getRequestId(),
                    true,
                    window,
                    ""
                );
            } catch (Exception e) {
                return new WindowInfoResult(
                    result.getRequestId(),
                    false,
                    null,
                    "Failed to parse window JSON: " + e.getMessage()
                );
            }
        } catch (Exception e) {
            return new WindowInfoResult(
                "",
                false,
                null,
                "Failed to get active window: " + e.getMessage()
            );
        }
    }

    /**
     * Gets the currently active window with default timeout (3000ms).
     *
     * @return WindowInfoResult containing active window info and error message if any
     */
    public WindowInfoResult getActiveWindow() {
        return getActiveWindow(3000);
    }

    /**
     * Activates the specified window.
     *
     * @param windowId The ID of the window to activate
     * @return BoolResult Result object containing success status and error message if any
     * 
     * <p>Note:
     * <ul>
     *   <li>The window must exist in the system</li>
     *   <li>Use listRootWindows() to get available window IDs</li>
     *   <li>Activating a window brings it to the foreground</li>
     * </ul>
     * 
     * @see #listRootWindows()
     * @see #getActiveWindow()
     * @see #closeWindow(int)
     */
    public BoolResult activateWindow(int windowId) {
        return windowOperation("activate_window", windowId);
    }

    /**
     * Closes the specified window.
     *
     * @param windowId The ID of the window to close
     * @return BoolResult Result object containing success status and error message if any
     * 
     * <p>Note:
     * <ul>
     *   <li>The window must exist in the system</li>
     *   <li>Use listRootWindows() to get available window IDs</li>
     *   <li>Closing a window terminates it permanently</li>
     * </ul>
     * 
     * @see #listRootWindows()
     * @see #activateWindow(int)
     * @see #minimizeWindow(int)
     */
    public BoolResult closeWindow(int windowId) {
        return windowOperation("close_window", windowId);
    }

    /**
     * Maximizes the specified window.
     *
     * @param windowId The ID of the window to maximize
     * @return BoolResult Result object containing success status and error message if any
     * 
     * <p>Note:
     * <ul>
     *   <li>The window must exist in the system</li>
     *   <li>Maximizing expands the window to fill the screen</li>
     *   <li>Use restoreWindow() to return to previous size</li>
     * </ul>
     * 
     * @see #minimizeWindow(int)
     * @see #restoreWindow(int)
     * @see #fullscreenWindow(int)
     * @see #resizeWindow(int, int, int)
     */
    public BoolResult maximizeWindow(int windowId) {
        return windowOperation("maximize_window", windowId);
    }

    /**
     * Minimizes the specified window.
     *
     * @param windowId The ID of the window to minimize
     * @return BoolResult Result object containing success status and error message if any
     * 
     * <p>Note:
     * <ul>
     *   <li>The window must exist in the system</li>
     *   <li>Minimizing hides the window in the taskbar</li>
     *   <li>Use restoreWindow() or activateWindow() to bring it back</li>
     * </ul>
     * 
     * @see #maximizeWindow(int)
     * @see #restoreWindow(int)
     * @see #activateWindow(int)
     */
    public BoolResult minimizeWindow(int windowId) {
        return windowOperation("minimize_window", windowId);
    }

    /**
     * Restores the specified window.
     *
     * @param windowId The ID of the window to restore
     * @return BoolResult Result object containing success status and error message if any
     * 
     * <p>Note:
     * <ul>
     *   <li>The window must exist in the system</li>
     *   <li>Restoring returns a minimized or maximized window to its normal state</li>
     *   <li>Works for windows that were previously minimized or maximized</li>
     * </ul>
     * 
     * @see #minimizeWindow(int)
     * @see #maximizeWindow(int)
     * @see #activateWindow(int)
     */
    public BoolResult restoreWindow(int windowId) {
        return windowOperation("restore_window", windowId);
    }

    /**
     * Resizes the specified window.
     *
     * @param windowId The ID of the window to resize
     * @param width New width of the window
     * @param height New height of the window
     * @return BoolResult Result object containing success status and error message if any
     * 
     * <p>Note:
     * <ul>
     *   <li>The window must exist in the system</li>
     *   <li>Width and height are in pixels</li>
     *   <li>Some windows may have minimum or maximum size constraints</li>
     * </ul>
     * 
     * @see #maximizeWindow(int)
     * @see #restoreWindow(int)
     * @see #getScreenSize()
     */
    public BoolResult resizeWindow(int windowId, int width, int height) {
        try {
            Map<String, Object> args = new HashMap<>();
            args.put("window_id", windowId);
            args.put("width", width);
            args.put("height", height);
            OperationResult result = callUiTool("resize_window", args);

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
                "Failed to resize window: " + e.getMessage()
            );
        }
    }

    /**
     * Makes the specified window fullscreen.
     *
     * @param windowId The ID of the window to make fullscreen
     * @return BoolResult containing success status and error message if any
     * 
     * <p>Note:
     * <ul>
     *   <li>The window must exist in the system</li>
     *   <li>Fullscreen mode hides window borders and taskbar</li>
     *   <li>Different from maximizeWindow() which keeps window borders</li>
     *   <li>Press F11 or ESC to exit fullscreen in most applications</li>
     * </ul>
     * 
     * @see #maximizeWindow(int)
     * @see #restoreWindow(int)
     */
    public BoolResult fullscreenWindow(int windowId) {
        return windowOperation("fullscreen_window", windowId);
    }

    /**
     * Toggles focus mode on or off.
     *
     * @param on True to enable focus mode, False to disable it
     * @return BoolResult containing success status and error message if any
     * 
     * <p>Note:
     * <ul>
     *   <li>Focus mode helps reduce distractions by managing window focus</li>
     *   <li>When enabled, may prevent background windows from stealing focus</li>
     *   <li>Behavior depends on the window manager and OS settings</li>
     * </ul>
     * 
     * @see #activateWindow(int)
     * @see #getActiveWindow()
     */
    public BoolResult focusMode(boolean on) {
        try {
            Map<String, Object> args = new HashMap<>();
            args.put("on", on);
            OperationResult result = callUiTool("focus_mode", args);

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
                "Failed to toggle focus mode: " + e.getMessage()
            );
        }
    }

    // ==================== Helper Methods ====================

    /**
     * Helper method for window operations that only require window_id.
     */
    private BoolResult windowOperation(String toolName, int windowId) {
        try {
            Map<String, Object> args = new HashMap<>();
            args.put("window_id", windowId);
            OperationResult result = callMcpTool(toolName, args);

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
                "Failed to " + toolName + ": " + e.getMessage()
            );
        }
    }

    /**
     * Helper method to parse Window object from JSON data.
     */
    private Window parseWindow(Map<String, Object> windowData) {
        Window window = new Window();
        if (windowData.containsKey("window_id")) {
            Object windowIdObj = windowData.get("window_id");
            if (windowIdObj instanceof Number) {
                window.setWindowId(((Number) windowIdObj).intValue());
            }
        }
        if (windowData.containsKey("window_title")) {
            window.setTitle(String.valueOf(windowData.get("window_title")));
        }
        if (windowData.containsKey("absolute_upper_left_x")) {
            Object xObj = windowData.get("absolute_upper_left_x");
            if (xObj instanceof Number) {
                window.setAbsoluteUpperLeftX(((Number) xObj).intValue());
            }
        }
        if (windowData.containsKey("absolute_upper_left_y")) {
            Object yObj = windowData.get("absolute_upper_left_y");
            if (yObj instanceof Number) {
                window.setAbsoluteUpperLeftY(((Number) yObj).intValue());
            }
        }
        if (windowData.containsKey("width")) {
            Object widthObj = windowData.get("width");
            if (widthObj instanceof Number) {
                window.setWidth(((Number) widthObj).intValue());
            }
        }
        if (windowData.containsKey("height")) {
            Object heightObj = windowData.get("height");
            if (heightObj instanceof Number) {
                window.setHeight(((Number) heightObj).intValue());
            }
        }
        if (windowData.containsKey("pid")) {
            Object pidObj = windowData.get("pid");
            if (pidObj instanceof Number) {
                window.setPid(((Number) pidObj).intValue());
            }
        }
        if (windowData.containsKey("pname")) {
            window.setPname(String.valueOf(windowData.get("pname")));
        }
        if (windowData.containsKey("child_windows")) {
            Object childWindowsObj = windowData.get("child_windows");
            if (childWindowsObj instanceof List) {
                @SuppressWarnings("unchecked")
                List<Map<String, Object>> childWindowsList = (List<Map<String, Object>>) childWindowsObj;
                List<Window> childWindows = new ArrayList<>();
                for (Map<String, Object> childData : childWindowsList) {
                    childWindows.add(parseWindow(childData));
                }
                window.setChildWindows(childWindows);
            }
        }
        return window;
    }
}

