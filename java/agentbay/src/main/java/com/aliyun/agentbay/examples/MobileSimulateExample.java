package com.aliyun.agentbay.examples;

import com.aliyun.agentbay.AgentBay;
import com.aliyun.agentbay.context.Context;
import com.aliyun.agentbay.context.ContextResult;
import com.aliyun.agentbay.mobile.MobileExtraConfig;
import com.aliyun.agentbay.mobile.MobileSimulate;
import com.aliyun.agentbay.mobile.MobileSimulateConfig;
import com.aliyun.agentbay.mobile.MobileSimulateMode;
import com.aliyun.agentbay.mobile.MobileSimulateUploadResult;
import com.aliyun.agentbay.model.CommandResult;
import com.aliyun.agentbay.model.ExtraConfigs;
import com.aliyun.agentbay.model.SessionResult;
import com.aliyun.agentbay.session.CreateSessionParams;
import com.aliyun.agentbay.session.Session;

import java.nio.file.Files;
import java.nio.file.Paths;
import java.util.HashMap;
import java.util.Map;

/**
 * Example demonstrating mobile device simulation using MobileSimulateConfig.
 * 
 * This example shows:
 * 1. Uploading device info to a context
 * 2. Creating a session with device simulation enabled
 * 3. Verifying the simulated device properties
 * 
 * Prerequisites:
 * - A mobile device info JSON file (dev_info.json)
 * - File can be obtained from a real device or generated
 */
public class MobileSimulateExample {

    public static void main(String[] args) {
        String apiKey = System.getenv("AGENTBAY_API_KEY");
        if (apiKey == null || apiKey.isEmpty()) {
            System.err.println("Please set AGENTBAY_API_KEY environment variable");
            return;
        }

        try {
            // Initialize AgentBay client
            AgentBay agentBay = new AgentBay(apiKey);
            System.out.println("AgentBay client initialized successfully");

            // Example: Mobile device simulation
            mobileDeviceSimulation(agentBay);

        } catch (Exception e) {
            System.err.println("Error: " + e.getMessage());
            e.printStackTrace();
        }
    }

    /**
     * Example: Complete mobile device simulation workflow.
     */
    private static void mobileDeviceSimulation(AgentBay agentBay) {
        System.out.println("\n=== Mobile Device Simulation Example ===");
        
        Session session = null;
        String contextId = null;
        
        try {
            // Step 1: Create or get a context for storing device info
            System.out.println("\n1. Creating context for device info...");
            String contextName = "mobile-device-xiaomi13-" + System.currentTimeMillis();
            ContextResult contextResult = agentBay.getContext().create(contextName);
            
            if (!contextResult.isSuccess() || contextResult.getContext() == null) {
                System.err.println("❌ Failed to create context: " + contextResult.getErrorMessage());
                return;
            }
            
            Context context = contextResult.getContext();
            contextId = context.getContextId();
            System.out.println("✅ Context created: " + contextId);

            // Step 2: Upload mobile device info file
            System.out.println("\n2. Uploading device info file...");
            
            // Path to your device info JSON file
            // You can use the example file from resource directory
            String projectRoot = System.getProperty("user.dir");
            String deviceInfoPath = Paths.get(projectRoot, "..", "..", "resource", "mobile_info_model_a.json")
                                        .normalize().toString();
            
            if (!Files.exists(Paths.get(deviceInfoPath))) {
                System.err.println("❌ Device info file not found: " + deviceInfoPath);
                System.err.println("   Please provide a valid mobile device info JSON file");
                return;
            }
            
            // Read device info content
            String deviceInfoContent = new String(Files.readAllBytes(Paths.get(deviceInfoPath)));
            
            // Upload using MobileSimulate service
            MobileSimulate mobileSimulate = agentBay.getMobileSimulate();
            mobileSimulate.setSimulateEnable(true);
            mobileSimulate.setSimulateMode(MobileSimulateMode.ALL);  // Simulate all properties
            mobileSimulate.setSimulateContextId(contextId);
            
            MobileSimulateUploadResult uploadResult = 
                mobileSimulate.uploadMobileInfo(deviceInfoContent);
            
            if (!uploadResult.isSuccess()) {
                System.err.println("❌ Failed to upload device info: " + uploadResult.getErrorMessage());
                return;
            }
            
            System.out.println("✅ Device info uploaded successfully");
            System.out.println("   Context ID: " + uploadResult.getMobileSimulateContextId());

            // Step 3: Create session with device simulation
            System.out.println("\n3. Creating session with device simulation...");
            
            // Get simulate config from MobileSimulate service
            MobileSimulateConfig simulateConfig = mobileSimulate.getSimulateConfig();
            
            // Create mobile extra config with simulate config
            MobileExtraConfig mobileConfig = new MobileExtraConfig();
            mobileConfig.setLockResolution(true);
            mobileConfig.setHideNavigationBar(true);
            mobileConfig.setSimulateConfig(simulateConfig);

            // Create ExtraConfigs
            ExtraConfigs extraConfigs = new ExtraConfigs(mobileConfig);

            // Create session parameters
            CreateSessionParams params = new CreateSessionParams();
            params.setImageId("mobile_latest");
            params.setExtraConfigs(extraConfigs);
            
            Map<String, String> labels = new HashMap<>();
            labels.put("example", "mobile-simulate");
            labels.put("device", "xiaomi13");
            params.setLabels(labels);

            SessionResult sessionResult = agentBay.create(params);

            if (!sessionResult.isSuccess() || sessionResult.getSession() == null) {
                System.err.println("❌ Failed to create session: " + sessionResult.getErrorMessage());
                return;
            }

            session = sessionResult.getSession();
            System.out.println("✅ Session created with device simulation!");
            System.out.println("   Session ID: " + session.getSessionId());

            // Step 4: Wait for simulation to complete
            System.out.println("\n4. Waiting for device simulation to complete...");
            Thread.sleep(8000);  // Wait for wya apply command to complete

            // Step 5: Verify simulated device properties
            System.out.println("\n5. Verifying simulated device properties...");
            
            // Check device model
            CommandResult modelResult = session.getCommand().executeCommand("getprop ro.product.model", 5000);
            if (modelResult.isSuccess() && modelResult.getOutput() != null) {
                System.out.println("✅ Device model: " + modelResult.getOutput().trim());
            }
            
            // Check device manufacturer
            CommandResult manufacturerResult = session.getCommand().executeCommand("getprop ro.product.manufacturer", 5000);
            if (manufacturerResult.isSuccess() && manufacturerResult.getOutput() != null) {
                System.out.println("✅ Manufacturer: " + manufacturerResult.getOutput().trim());
            }
            
            // Check Android version
            CommandResult versionResult = session.getCommand().executeCommand("getprop ro.build.version.release", 5000);
            if (versionResult.isSuccess() && versionResult.getOutput() != null) {
                System.out.println("✅ Android version: " + versionResult.getOutput().trim());
            }

            System.out.println("\n✅ Mobile device simulation completed successfully!");

        } catch (Exception e) {
            System.err.println("❌ Error in mobileDeviceSimulation: " + e.getMessage());
            e.printStackTrace();
        } finally {
            // Clean up
            if (session != null) {
                try {
                    agentBay.delete(session, false);
                    System.out.println("\n✅ Session cleaned up");
                } catch (Exception e) {
                    System.err.println("❌ Error cleaning up session: " + e.getMessage());
                }
            }
            
            // Note: Context cleanup is optional and can be done manually if needed
        }
    }
}

