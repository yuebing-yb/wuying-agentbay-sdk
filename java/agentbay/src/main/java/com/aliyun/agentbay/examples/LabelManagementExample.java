package com.aliyun.agentbay.examples;

import com.aliyun.agentbay.AgentBay;
import com.aliyun.agentbay.exception.AgentBayException;
import com.aliyun.agentbay.model.OperationResult;
import com.aliyun.agentbay.session.CreateSessionParams;
import com.aliyun.agentbay.session.Session;
import com.fasterxml.jackson.databind.ObjectMapper;

import java.util.HashMap;
import java.util.Map;

/**
 * Example demonstrating Session label management functionality
 *
 * This example shows how to:
 * 1. Set labels on a session
 * 2. Retrieve labels from a session
 * 3. Update existing labels
 * 4. Use labels for session organization
 *
 * Labels are key-value pairs that help organize and filter sessions.
 * Use cases include:
 * - Organizing sessions by environment (dev, staging, production)
 * - Tracking sessions by team or project
 * - Adding version or release tags
 * - Filtering sessions in monitoring dashboards
 */
public class LabelManagementExample {

    public static void main(String[] args) {
        String apiKey = System.getenv("AGENTBAY_API_KEY");
        if (apiKey == null || apiKey.isEmpty()) {
            System.err.println("Error: AGENTBAY_API_KEY environment variable is not set");
            System.err.println("Please set it with: export AGENTBAY_API_KEY=your_api_key");
            System.exit(1);
        }

        try {
            // Initialize AgentBay client
            AgentBay agentBay = new AgentBay(apiKey);
            System.out.println("✓ AgentBay client initialized");

            // Create a new session
            CreateSessionParams params = new CreateSessionParams();
            params.setImageId("linux_latest");
            Session session = agentBay.create(params).getSession();
            System.out.println("✓ Session created: " + session.getSessionId());
            System.out.println();

            try {
                // ========================================
                // Example 1: Set initial labels
                // ========================================
                System.out.println("=== Example 1: Setting Initial Labels ===");

                Map<String, String> initialLabels = new HashMap<>();
                initialLabels.put("environment", "development");
                initialLabels.put("team", "backend");
                initialLabels.put("project", "agentbay-demo");
                initialLabels.put("version", "v1.0.0");

                OperationResult setResult = session.setLabels(initialLabels);
                if (setResult.isSuccess()) {
                    System.out.println("✓ Labels set successfully");
                    ObjectMapper mapper = new ObjectMapper();
                    @SuppressWarnings("unchecked")
                    Map<String, String> returnedLabels = mapper.readValue(setResult.getData(),
                        mapper.getTypeFactory().constructMapType(Map.class, String.class, String.class));
                    System.out.println("  Set " + returnedLabels.size() + " labels:");
                    returnedLabels.forEach((key, value) ->
                        System.out.println("    " + key + " = " + value)
                    );
                } else {
                    System.out.println("✗ Failed to set labels: " + setResult.getErrorMessage());
                }
                System.out.println();

                // ========================================
                // Example 2: Retrieve labels
                // ========================================
                System.out.println("=== Example 2: Retrieving Labels ===");

                OperationResult getResult = session.getLabels();
                if (getResult.isSuccess()) {
                    ObjectMapper mapper = new ObjectMapper();
                    @SuppressWarnings("unchecked")
                    Map<String, String> retrievedLabels = mapper.readValue(getResult.getData(),
                        mapper.getTypeFactory().constructMapType(Map.class, String.class, String.class));
                    System.out.println("✓ Retrieved " + retrievedLabels.size() + " labels:");
                    retrievedLabels.forEach((key, value) ->
                        System.out.println("    " + key + " = " + value)
                    );
                } else {
                    System.out.println("✗ Failed to get labels: " + getResult.getErrorMessage());
                }
                System.out.println();

                // ========================================
                // Example 3: Update existing labels
                // ========================================
                System.out.println("=== Example 3: Updating Labels ===");

                Map<String, String> updateLabels = new HashMap<>();
                updateLabels.put("environment", "staging");  // Update existing
                updateLabels.put("version", "v1.1.0");       // Update existing
                updateLabels.put("release-date", "2025-12-25"); // Add new

                setResult = session.setLabels(updateLabels);
                if (setResult.isSuccess()) {
                    System.out.println("✓ Labels updated successfully");
                } else {
                    System.out.println("✗ Failed to update labels: " + setResult.getErrorMessage());
                }

                // Verify updates
                getResult = session.getLabels();
                if (getResult.isSuccess()) {
                    ObjectMapper mapper = new ObjectMapper();
                    @SuppressWarnings("unchecked")
                    Map<String, String> updatedLabels = mapper.readValue(getResult.getData(),
                        mapper.getTypeFactory().constructMapType(Map.class, String.class, String.class));
                    System.out.println("  Updated labels:");
                    updatedLabels.forEach((key, value) ->
                        System.out.println("    " + key + " = " + value)
                    );
                }
                System.out.println();

                // ========================================
                // Example 4: Label validation examples
                // ========================================
                System.out.println("=== Example 4: Label Validation ===");

                // Try setting too many labels (max 20)
                try {
                    Map<String, String> tooManyLabels = new HashMap<>();
                    for (int i = 0; i < 21; i++) {
                        tooManyLabels.put("key" + i, "value" + i);
                    }
                    session.setLabels(tooManyLabels);
                    System.out.println("✗ Should have thrown exception for too many labels");
                } catch (AgentBayException e) {
                    System.out.println("✓ Correctly rejected too many labels (>20)");
                    System.out.println("  Error: " + e.getMessage());
                }

                // Try setting null labels
                try {
                    session.setLabels(null);
                    System.out.println("✗ Should have thrown exception for null labels");
                } catch (AgentBayException e) {
                    System.out.println("✓ Correctly rejected null labels");
                    System.out.println("  Error: " + e.getMessage());
                }

                // Try setting empty key
                try {
                    Map<String, String> emptyKeyLabels = new HashMap<>();
                    emptyKeyLabels.put("", "value");
                    session.setLabels(emptyKeyLabels);
                    System.out.println("✗ Should have thrown exception for empty key");
                } catch (AgentBayException e) {
                    System.out.println("✓ Correctly rejected empty label key");
                    System.out.println("  Error: " + e.getMessage());
                }
                System.out.println();

                // ========================================
                // Example 5: Common use case patterns
                // ========================================
                System.out.println("=== Example 5: Common Use Case Patterns ===");

                // Pattern 1: Environment-based labeling
                System.out.println("Pattern 1: Environment-based labeling");
                Map<String, String> envLabels = new HashMap<>();
                envLabels.put("environment", "production");
                envLabels.put("region", "us-west-2");
                envLabels.put("availability-zone", "us-west-2a");
                session.setLabels(envLabels);
                System.out.println("  ✓ Set environment labels");

                // Pattern 2: Team and project tracking
                System.out.println("Pattern 2: Team and project tracking");
                Map<String, String> teamLabels = new HashMap<>();
                teamLabels.put("team", "platform-engineering");
                teamLabels.put("project", "agentbay-sdk");
                teamLabels.put("owner", "john.doe@example.com");
                session.setLabels(teamLabels);
                System.out.println("  ✓ Set team and project labels");

                // Pattern 3: Version and release tracking
                System.out.println("Pattern 3: Version and release tracking");
                Map<String, String> versionLabels = new HashMap<>();
                versionLabels.put("version", "v2.0.0");
                versionLabels.put("release-type", "major");
                versionLabels.put("build-number", "1234");
                session.setLabels(versionLabels);
                System.out.println("  ✓ Set version and release labels");

                // Pattern 4: Cost allocation
                System.out.println("Pattern 4: Cost allocation");
                Map<String, String> costLabels = new HashMap<>();
                costLabels.put("cost-center", "engineering");
                costLabels.put("billing-project", "agentbay");
                costLabels.put("budget-category", "development");
                session.setLabels(costLabels);
                System.out.println("  ✓ Set cost allocation labels");

                // Final label state
                System.out.println();
                System.out.println("Final session label state:");
                getResult = session.getLabels();
                if (getResult.isSuccess()) {
                    ObjectMapper mapper = new ObjectMapper();
                    @SuppressWarnings("unchecked")
                    Map<String, String> finalLabels = mapper.readValue(getResult.getData(),
                        mapper.getTypeFactory().constructMapType(Map.class, String.class, String.class));
                    System.out.println("  Total labels: " + finalLabels.size());
                    finalLabels.forEach((key, value) ->
                        System.out.println("    " + key + " = " + value)
                    );
                }

            } finally {
                // Clean up - delete the session
                System.out.println();
                System.out.println("=== Cleanup ===");
                session.delete();
                System.out.println("✓ Session deleted");
            }

            System.out.println();
            System.out.println("=== Label Management Example Complete ===");

        } catch (Exception e) {
            System.err.println("Error: " + e.getMessage());
            e.printStackTrace();
            System.exit(1);
        }
    }
}
