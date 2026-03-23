package com.aliyun.agentbay.browser;

import java.util.HashMap;
import java.util.Map;

/**
 * Browser notify message for SDK and sandbox communication, such as call-for-user messages.
 * 
 * <p>Example usage:</p>
 * <pre>{@code
 * BrowserNotifyMessage notifyMsg = new BrowserNotifyMessage(
 *     "call-for-user",
 *     3,
 *     201,
 *     "captcha solving start",
 *     "pause",
 *     Map.of("max_wait_time", 30)
 * );
 * }</pre>
 */
public class BrowserNotifyMessage {
    private String type;
    private Integer id;
    private Integer code;
    private String message;
    private String action;
    private Map<String, Object> extraParams;

    /**
     * Constructs a new BrowserNotifyMessage with all parameters.
     * 
     * @param type Type of the notification (e.g., "call-for-user")
     * @param id ID of the notification
     * @param code Status code of the notification (e.g., 201)
     * @param message Descriptive message (e.g., "captcha solving start")
     * @param action Action to be taken (e.g., "pause", "resume", "takeover", "takeoverdone")
     * @param extraParams Additional parameters as a map (e.g., {"max_wait_time": 30})
     */
    public BrowserNotifyMessage(String type, Integer id, Integer code, String message, String action, Map<String, Object> extraParams) {
        this.type = type;
        this.id = id;
        this.code = code;
        this.message = message;
        this.action = action;
        this.extraParams = extraParams != null ? extraParams : new HashMap<>();
    }

    /**
     * Constructs a new BrowserNotifyMessage with empty extraParams.
     */
    public BrowserNotifyMessage(String type, Integer id, Integer code, String message, String action) {
        this(type, id, code, message, action, new HashMap<>());
    }

    /**
     * Convert BrowserNotifyMessage to a Map for serialization.
     * 
     * @return Map representation of the notify message
     */
    public Map<String, Object> toMap() {
        Map<String, Object> map = new HashMap<>();
        if (type != null) map.put("type", type);
        if (id != null) map.put("id", id);
        if (code != null) map.put("code", code);
        if (message != null) map.put("message", message);
        if (action != null) map.put("action", action);
        if (extraParams != null && !extraParams.isEmpty()) {
            map.put("extra_params", extraParams);
        }
        return map;
    }

    /**
     * Create a BrowserNotifyMessage from a Map.
     * 
     * @param map Map containing the notify message data
     * @return BrowserNotifyMessage instance
     */
    @SuppressWarnings("unchecked")
    public static BrowserNotifyMessage fromMap(Map<String, Object> map) {
        if (map == null) {
            return null;
        }

        // Push callbacks may arrive either as a flat message map or wrapped as:
        // { target: "...", requestId: "...", data: { type, id, code, message, action, extraParams } }
        Map<String, Object> dataMap = map;
        Object nestedData = map.get("data");
        if (nestedData instanceof Map) {
            dataMap = (Map<String, Object>) nestedData;
        }

        String type = dataMap.get("type") instanceof String ? (String) dataMap.get("type") : null;
        Integer id = dataMap.get("id") instanceof Number ? ((Number) dataMap.get("id")).intValue() : null;
        Integer code = dataMap.get("code") instanceof Number ? ((Number) dataMap.get("code")).intValue() : null;
        String message = dataMap.get("message") instanceof String ? (String) dataMap.get("message") : null;
        String action = dataMap.get("action") instanceof String ? (String) dataMap.get("action") : null;

        Map<String, Object> extraParams = new HashMap<>();
        Object snakeCaseExtra = dataMap.get("extra_params");
        Object camelCaseExtra = dataMap.get("extraParams");
        if (snakeCaseExtra instanceof Map) {
            extraParams.putAll((Map<String, Object>) snakeCaseExtra);
        } else if (camelCaseExtra instanceof Map) {
            extraParams.putAll((Map<String, Object>) camelCaseExtra);
        }

        return new BrowserNotifyMessage(type, id, code, message, action, extraParams);
    }

    // Getters and Setters
    public String getType() { return type; }
    public void setType(String type) { this.type = type; }
    
    public Integer getId() { return id; }
    public void setId(Integer id) { this.id = id; }
    
    public Integer getCode() { return code; }
    public void setCode(Integer code) { this.code = code; }
    
    public String getMessage() { return message; }
    public void setMessage(String message) { this.message = message; }
    
    public String getAction() { return action; }
    public void setAction(String action) { this.action = action; }
    
    public Map<String, Object> getExtraParams() { return extraParams; }
    public void setExtraParams(Map<String, Object> extraParams) { this.extraParams = extraParams; }

    @Override
    public String toString() {
        return "BrowserNotifyMessage{" +
                "type='" + type + '\'' +
                ", id=" + id +
                ", code=" + code +
                ", message='" + message + '\'' +
                ", action='" + action + '\'' +
                ", extraParams=" + extraParams +
                '}';
    }
}
