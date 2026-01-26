package com.aliyun.agentbay.browser;

import java.util.HashMap;
import java.util.Map;

/**
 * Browser proxy configuration.
 * Supports three types of proxy:
 * - Custom proxy: User-provided proxy servers
 * - Wuying proxy: Alibaba Cloud proxy service (strategies: restricted, polling)
 * - Managed proxy: Client-provided proxies managed by Wuying platform (strategies: polling, sticky, rotating, matched)
 */
public class BrowserProxy {
    private String type;
    private String server;
    private String username;
    private String password;
    private String strategy;
    private int pollsize;
    private String userId;
    private String isp;
    private String country;
    private String province;
    private String city;

    public BrowserProxy(String type) {
        this.type = type;
        this.pollsize = 10; // default
        validateType();
    }

    public BrowserProxy(String type, String server, String username, String password) {
        this.type = type;
        this.server = server;
        this.username = username;
        this.password = password;
        this.pollsize = 10; // default
        validateType();
        validateCustomProxy();
    }

    public BrowserProxy(String type, String strategy, int pollsize) {
        this.type = type;
        this.strategy = strategy;
        this.pollsize = pollsize;
        validateType();
        validateWuyingProxy();
    }

    public BrowserProxy(String type, String strategy, String userId, String isp, String country, String province, String city) {
        this.type = type;
        this.strategy = strategy;
        this.userId = userId;
        this.isp = isp;
        this.country = country;
        this.province = province;
        this.city = city;
        this.pollsize = 10; // default
        validateType();
        validateManagedProxy();
    }

    private void validateType() {
        if (!"custom".equals(type) && !"wuying".equals(type) && !"managed".equals(type)) {
            throw new IllegalArgumentException("proxy_type must be custom, wuying, or managed");
        }
    }

    private void validateCustomProxy() {
        if ("custom".equals(type) && (server == null || server.trim().isEmpty())) {
            throw new IllegalArgumentException("server is required for custom proxy type");
        }
    }

    private void validateWuyingProxy() {
        if ("wuying".equals(type)) {
            if (strategy == null || strategy.trim().isEmpty()) {
                throw new IllegalArgumentException("strategy is required for wuying proxy type");
            }
            if (!"restricted".equals(strategy) && !"polling".equals(strategy)) {
                throw new IllegalArgumentException("strategy must be restricted or polling for wuying proxy type");
            }
            if ("polling".equals(strategy) && pollsize <= 0) {
                throw new IllegalArgumentException("pollsize must be greater than 0 for polling strategy");
            }
        }
    }

    private void validateManagedProxy() {
        if ("managed".equals(type)) {
            if (strategy == null || strategy.trim().isEmpty()) {
                throw new IllegalArgumentException("strategy is required for managed proxy type");
            }
            if (!"polling".equals(strategy) && !"sticky".equals(strategy) && 
                !"rotating".equals(strategy) && !"matched".equals(strategy)) {
                throw new IllegalArgumentException("strategy must be polling, sticky, rotating, or matched for managed proxy type");
            }
            if (userId == null || userId.trim().isEmpty()) {
                throw new IllegalArgumentException("userId is required for managed proxy type");
            }
            if ("matched".equals(strategy)) {
                boolean hasFilter = (isp != null && !isp.trim().isEmpty()) ||
                                   (country != null && !country.trim().isEmpty()) ||
                                   (province != null && !province.trim().isEmpty()) ||
                                   (city != null && !city.trim().isEmpty());
                if (!hasFilter) {
                    throw new IllegalArgumentException("at least one of isp, country, province, or city is required for matched strategy");
                }
            }
        }
    }

    public Map<String, Object> toMap() {
        Map<String, Object> map = new HashMap<>();
        map.put("type", type);

        if ("custom".equals(type)) {
            if (server != null) map.put("server", server);
            if (username != null) map.put("username", username);
            if (password != null) map.put("password", password);
        } else if ("wuying".equals(type)) {
            if (strategy != null) map.put("strategy", strategy);
            if ("polling".equals(strategy)) {
                map.put("pollsize", pollsize);
            }
        } else if ("managed".equals(type)) {
            if (strategy != null) map.put("strategy", strategy);
            if (userId != null) map.put("userId", userId);
            if (isp != null) map.put("isp", isp);
            if (country != null) map.put("country", country);
            if (province != null) map.put("province", province);
            if (city != null) map.put("city", city);
        }

        return map;
    }

    public static BrowserProxy fromMap(Map<String, Object> map) {
        if (map == null || map.isEmpty()) {
            return null;
        }

        String type = (String) map.get("type");
        if (type == null) {
            throw new IllegalArgumentException("type is required in proxy configuration");
        }

        if ("custom".equals(type)) {
            return new BrowserProxy(
                type,
                (String) map.get("server"),
                (String) map.get("username"),
                (String) map.get("password")
            );
        } else if ("wuying".equals(type)) {
            return new BrowserProxy(
                type,
                (String) map.get("strategy"),
                (Integer) map.getOrDefault("pollsize", 10)
            );
        } else if ("managed".equals(type)) {
            return new BrowserProxy(
                type,
                (String) map.get("strategy"),
                (String) map.get("userId"),
                (String) map.get("isp"),
                (String) map.get("country"),
                (String) map.get("province"),
                (String) map.get("city")
            );
        } else {
            throw new IllegalArgumentException("Unsupported proxy type: " + type);
        }
    }

    // Getters and setters
    public String getType() { return type; }
    public void setType(String type) { this.type = type; }

    public String getServer() { return server; }
    public void setServer(String server) { this.server = server; }

    public String getUsername() { return username; }
    public void setUsername(String username) { this.username = username; }

    public String getPassword() { return password; }
    public void setPassword(String password) { this.password = password; }

    public String getStrategy() { return strategy; }
    public void setStrategy(String strategy) { this.strategy = strategy; }

    public int getPollsize() { return pollsize; }
    public void setPollsize(int pollsize) { this.pollsize = pollsize; }

    public String getUserId() { return userId; }
    public void setUserId(String userId) { this.userId = userId; }

    public String getIsp() { return isp; }
    public void setIsp(String isp) { this.isp = isp; }

    public String getCountry() { return country; }
    public void setCountry(String country) { this.country = country; }

    public String getProvince() { return province; }
    public void setProvince(String province) { this.province = province; }

    public String getCity() { return city; }
    public void setCity(String city) { this.city = city; }
}