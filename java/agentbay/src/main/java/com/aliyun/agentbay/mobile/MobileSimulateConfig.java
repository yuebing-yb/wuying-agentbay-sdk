package com.aliyun.agentbay.mobile;

import com.fasterxml.jackson.annotation.JsonInclude;
import com.fasterxml.jackson.annotation.JsonProperty;

import java.util.HashMap;
import java.util.Map;

/**
 * Configuration for mobile device simulation.
 * 
 * <p>This configuration enables simulating real device properties in the cloud
 * mobile environment, including device model, manufacturer, sensors, and more.</p>
 * 
 * @see MobileSimulateMode
 */
@JsonInclude(JsonInclude.Include.NON_NULL)
public class MobileSimulateConfig {
    
    @JsonProperty("Simulate")
    private boolean simulate;
    
    @JsonProperty("SimulatePath")
    private String simulatePath;
    
    @JsonProperty("SimulateMode")
    private MobileSimulateMode simulateMode;
    
    @JsonProperty("SimulatedContextId")
    private String simulatedContextId;

    /**
     * Default constructor with simulation disabled.
     */
    public MobileSimulateConfig() {
        this.simulate = false;
        this.simulateMode = MobileSimulateMode.PROPERTIES_ONLY;
    }

    /**
     * Constructor with all parameters.
     *
     * @param simulate Whether to enable device simulation
     * @param simulatePath Path to the device info file
     * @param simulateMode Simulation mode (what to simulate)
     * @param simulatedContextId Context ID containing device info
     */
    public MobileSimulateConfig(boolean simulate, String simulatePath, 
                               MobileSimulateMode simulateMode, String simulatedContextId) {
        this.simulate = simulate;
        this.simulatePath = simulatePath;
        this.simulateMode = simulateMode;
        this.simulatedContextId = simulatedContextId;
    }

    public boolean isSimulate() {
        return simulate;
    }

    public void setSimulate(boolean simulate) {
        this.simulate = simulate;
    }

    public String getSimulatePath() {
        return simulatePath;
    }

    public void setSimulatePath(String simulatePath) {
        this.simulatePath = simulatePath;
    }

    public MobileSimulateMode getSimulateMode() {
        return simulateMode;
    }

    public void setSimulateMode(MobileSimulateMode simulateMode) {
        this.simulateMode = simulateMode;
    }

    public String getSimulatedContextId() {
        return simulatedContextId;
    }

    public void setSimulatedContextId(String simulatedContextId) {
        this.simulatedContextId = simulatedContextId;
    }

    /**
     * Validate the configuration.
     * 
     * @throws IllegalArgumentException if configuration is invalid
     */
    public void validate() {
        if (simulate && (simulatePath == null || simulatePath.trim().isEmpty())) {
            throw new IllegalArgumentException("simulate_path is required when simulate is enabled");
        }
    }

    /**
     * Convert to Map for API request.
     *
     * @return Map representation
     */
    public Map<String, Object> toMap() {
        Map<String, Object> result = new HashMap<>();
        result.put("Simulate", simulate);
        
        if (simulatePath != null) {
            result.put("SimulatePath", simulatePath);
        }
        
        if (simulateMode != null) {
            result.put("SimulateMode", simulateMode.getValue());
        }
        
        if (simulatedContextId != null) {
            result.put("SimulatedContextId", simulatedContextId);
        }
        
        return result;
    }

    /**
     * Create from Map.
     *
     * @param map Map representation
     * @return MobileSimulateConfig instance
     */
    public static MobileSimulateConfig fromMap(Map<String, Object> map) {
        if (map == null) {
            return null;
        }
        
        MobileSimulateConfig config = new MobileSimulateConfig();
        
        if (map.containsKey("Simulate")) {
            config.setSimulate((Boolean) map.get("Simulate"));
        }
        
        if (map.containsKey("SimulatePath")) {
            config.setSimulatePath((String) map.get("SimulatePath"));
        }
        
        if (map.containsKey("SimulateMode")) {
            String modeValue = (String) map.get("SimulateMode");
            config.setSimulateMode(MobileSimulateMode.fromValue(modeValue));
        }
        
        if (map.containsKey("SimulatedContextId")) {
            config.setSimulatedContextId((String) map.get("SimulatedContextId"));
        }
        
        return config;
    }

    @Override
    public String toString() {
        return "MobileSimulateConfig{" +
                "simulate=" + simulate +
                ", simulatePath='" + simulatePath + '\'' +
                ", simulateMode=" + simulateMode +
                ", simulatedContextId='" + simulatedContextId + '\'' +
                '}';
    }
}
