package com.aliyun.agentbay.test;

import com.aliyun.agentbay.AgentBay;
import com.aliyun.agentbay.agent.Agent;
import com.aliyun.agentbay.exception.AgentBayException;
import com.aliyun.agentbay.model.ExecutionResult;
import com.aliyun.agentbay.model.QueryResult;
import com.aliyun.agentbay.model.SessionResult;
import com.aliyun.agentbay.session.CreateSessionParams;
import com.aliyun.agentbay.session.Session;
import org.junit.AfterClass;
import org.junit.BeforeClass;
import org.junit.Test;

import static org.junit.Assert.*;

/**
 * Integration tests for Mobile Agent functionality in AgentBay Java SDK.
 * This test class is equivalent to test_mobile_agent_integration.py in Python SDK.
 */
public class TestMobileAgentIntegration {
    private static AgentBay agentBay;
    private static Session session;
    private static Agent agent;

    /**
     * Get API key for testing
     */
    private static String getTestApiKey() {
        String apiKey = System.getenv("AGENTBAY_API_KEY");
        if (apiKey == null || apiKey.trim().isEmpty()) {
            apiKey = "akm-xxx"; // Replace with your actual API key for testing
            System.out.println("Warning: Using default API key. Set AGENTBAY_API_KEY environment variable for production use.");
        }
        return apiKey;
    }

    /**
     * Set up the test environment by creating a session and initializing agent.
     */
    @BeforeClass
    public static void setUp() throws AgentBayException, InterruptedException {
        // Ensure a delay to avoid session creation conflicts
        Thread.sleep(3000);
        
        String apiKey = getTestApiKey();
        agentBay = new AgentBay(apiKey);
        
        // Create a session with mobile_latest image
        CreateSessionParams params = new CreateSessionParams();
        params.setImageId("imgc-0aae4rgien5oudgb6"); // mobile_latest image ID
        
        System.out.println("Creating a new session for mobile agent testing...");
        SessionResult sessionResult = agentBay.create(params);
        
        if (!sessionResult.isSuccess() || sessionResult.getSession() == null) {
            throw new AgentBayException("Failed to create session: " + sessionResult.getErrorMessage());
        }
        
        session = sessionResult.getSession();
        agent = session.getAgent();

        System.out.println("Session created with ID: " + session.getSessionId());
    }

    /**
     * Clean up resources after all tests.
     */
    @AfterClass
    public static void tearDown() {
        System.out.println("Cleaning up: Deleting the session...");
        try {
            if (session != null) {
                agentBay.delete(session, false);
            }
        } catch (Exception e) {
            System.err.println("Warning: Error deleting session: " + e.getMessage());
        }
    }

    @Test
    public void testMobileExecuteTaskSuccess() throws InterruptedException {
        System.out.println("🚀 Test: Mobile execute_task - non-blocking execution");

        String task = "Open WeChat app";
        String taskId = null;
        
        try {
            ExecutionResult result = agent.getMobile().executeTask(task, 1);

            if (!result.isSuccess()) {
                System.out.println("ExecutionResult details:");
                System.out.println("  Success: " + result.isSuccess());
                System.out.println("  Error Message: " + result.getErrorMessage());
                System.out.println("  Request ID: " + result.getRequestId());
                System.out.println("  Task ID: " + result.getTaskId());
                System.out.println("  Task Status: " + result.getTaskStatus());
            }
            assertTrue("Task execution should succeed. Error: " + result.getErrorMessage(), result.isSuccess());
            assertNotNull("Request ID should not be null", result.getRequestId());
            assertFalse("Request ID should not be empty", result.getRequestId().isEmpty());
            assertEquals("Error message should be empty", "", result.getErrorMessage());
            assertNotNull("Task ID should not be null", result.getTaskId());
            assertFalse("Task ID should not be empty", result.getTaskId().isEmpty());
            assertEquals("Initial status should be running", "running", result.getTaskStatus());

            taskId = result.getTaskId();
            System.out.println("✅ Task ID: " + taskId);

            // Poll until task completes to avoid blocking subsequent tests
            String timeoutEnv = System.getenv("AGENT_TASK_TIMEOUT");
            int timeout = (timeoutEnv != null && !timeoutEnv.isEmpty())
                ? Integer.parseInt(timeoutEnv)
                : 300;
            int pollInterval = 3;
            int maxPollAttempts = timeout / pollInterval;
            int retryTimes = 0;
            QueryResult queryResult = null;

            while (retryTimes < maxPollAttempts) {
                queryResult = agent.getMobile().getTaskStatus(taskId);

                assertTrue("Query should succeed", queryResult.isSuccess());
                System.out.println("⏳ Task " + queryResult.getTaskId() + " status: " + queryResult.getTaskStatus());

                String taskStatus = queryResult.getTaskStatus();
                if ("completed".equals(taskStatus) || "failed".equals(taskStatus) || 
                    "cancelled".equals(taskStatus) || "unsupported".equals(taskStatus)) {
                    break;
                }

                retryTimes++;
                Thread.sleep(pollInterval * 1000);
            }

            // Verify the final task status
            assertNotNull("Query result should not be null", queryResult);
            assertTrue("Task should finish within timeout", retryTimes < maxPollAttempts);
            System.out.println("✅ Task completed with status: " + queryResult.getTaskStatus());
        } finally {
            // Clean up: terminate task if still running
            if (taskId != null && !taskId.isEmpty()) {
                try {
                    QueryResult status = agent.getMobile().getTaskStatus(taskId);
                    if (status.isSuccess() && "running".equals(status.getTaskStatus())) {
                        System.out.println("Cleaning up: terminating task " + taskId);
                        ExecutionResult terminateResult = agent.getMobile().terminateTask(taskId);
                        if (terminateResult.isSuccess()) {
                            System.out.println("✅ Task " + taskId + " terminated successfully");
                            Thread.sleep(1000);
                        }
                    }
                } catch (Exception e) {
                    System.out.println("Could not terminate task " + taskId + ": " + e.getMessage());
                }
            }
        }
    }

    @Test
    public void testMobileExecuteTaskAndWaitSuccess() throws InterruptedException {
        System.out.println("🚀 Test: Mobile execute_task_and_wait - blocking execution");

        String task = "Open WeChat app";
        String taskId = null;
        
        try {
            String timeoutEnv = System.getenv("AGENT_TASK_TIMEOUT");
            int timeout = (timeoutEnv != null && !timeoutEnv.isEmpty())
                ? Integer.parseInt(timeoutEnv)
                : 300;

            ExecutionResult result = agent.getMobile().executeTaskAndWait(task, 10, timeout);
            taskId = result.getTaskId();

            if (!result.isSuccess()) {
                System.out.println("ExecutionResult details:");
                System.out.println("  Success: " + result.isSuccess());
                System.out.println("  Error Message: " + result.getErrorMessage());
                System.out.println("  Request ID: " + result.getRequestId());
                System.out.println("  Task ID: " + result.getTaskId());
                System.out.println("  Task Status: " + result.getTaskStatus());
                System.out.println("  Task Result: " + result.getTaskResult());
            }
            assertTrue("Task execution should succeed. Error: " + result.getErrorMessage(), result.isSuccess());
            assertNotNull("Request ID should not be null", result.getRequestId());
            assertFalse("Request ID should not be empty", result.getRequestId().isEmpty());
            assertEquals("Error message should be empty", "", result.getErrorMessage());
            assertNotNull("Task ID should not be null", result.getTaskId());
            assertFalse("Task ID should not be empty", result.getTaskId().isEmpty());
            assertEquals("Task status should be completed", "completed", result.getTaskStatus());

            System.out.println("✅ Task result: " + result.getTaskResult());
        } finally {
            // Clean up: terminate task if still running
            if (taskId != null && !taskId.isEmpty()) {
                try {
                    QueryResult status = agent.getMobile().getTaskStatus(taskId);
                    if (status.isSuccess() && "running".equals(status.getTaskStatus())) {
                        System.out.println("Cleaning up: terminating task " + taskId);
                        ExecutionResult terminateResult = agent.getMobile().terminateTask(taskId);
                        if (terminateResult.isSuccess()) {
                            System.out.println("✅ Task " + taskId + " terminated successfully");
                            Thread.sleep(1000);
                        }
                    }
                } catch (Exception e) {
                    System.out.println("Could not terminate task " + taskId + ": " + e.getMessage());
                }
            }
        }
    }

    @Test
    public void testMobileGetTaskStatusSuccess() throws InterruptedException {
        System.out.println("🚀 Test: Mobile get_task_status");

        String task = "Open WeChat app";
        String taskId = null;
        
        try {
            ExecutionResult executeResult = agent.getMobile().executeTask(task, 1);

            if (!executeResult.isSuccess()) {
                System.out.println("ExecutionResult details:");
                System.out.println("  Success: " + executeResult.isSuccess());
                System.out.println("  Error Message: " + executeResult.getErrorMessage());
                System.out.println("  Request ID: " + executeResult.getRequestId());
                System.out.println("  Task ID: " + executeResult.getTaskId());
                System.out.println("  Task Status: " + executeResult.getTaskStatus());
            }
            assertTrue("Task execution should succeed. Error: " + executeResult.getErrorMessage(), executeResult.isSuccess());
            taskId = executeResult.getTaskId();
            assertNotNull("Task ID should not be null", taskId);
            assertFalse("Task ID should not be empty", taskId.isEmpty());

            // Poll until task completes to avoid blocking subsequent tests
            String timeoutEnv = System.getenv("AGENT_TASK_TIMEOUT");
            int timeout = (timeoutEnv != null && !timeoutEnv.isEmpty())
                ? Integer.parseInt(timeoutEnv)
                : 300;
            int pollInterval = 3;
            int maxPollAttempts = timeout / pollInterval;
            int retryTimes = 0;
            QueryResult queryResult = null;

            while (retryTimes < maxPollAttempts) {
                queryResult = agent.getMobile().getTaskStatus(taskId);

                assertTrue("Query should succeed", queryResult.isSuccess());
                assertNotNull("Request ID should not be null", queryResult.getRequestId());
                assertEquals("Task ID should match", taskId, queryResult.getTaskId());
                assertNotNull("Task status should not be null", queryResult.getTaskStatus());
                assertFalse("Task status should not be empty", queryResult.getTaskStatus().isEmpty());

                System.out.println("⏳ Query #" + (retryTimes + 1) + ": Task status: " + queryResult.getTaskStatus());
                System.out.println("✅ Task action: " + queryResult.getTaskAction());

                String taskStatus = queryResult.getTaskStatus();
                if ("completed".equals(taskStatus) || "failed".equals(taskStatus) || 
                    "cancelled".equals(taskStatus) || "unsupported".equals(taskStatus)) {
                    System.out.println("✅ Task reached final status: " + taskStatus);
                    break;
                }

                retryTimes++;
                Thread.sleep(pollInterval * 1000);
            }

            // Verify task completed
            assertNotNull("Query result should not be null", queryResult);
            assertTrue("Task should finish within timeout", retryTimes < maxPollAttempts);
            System.out.println("✅ Task completed with status: " + queryResult.getTaskStatus());
        } finally {
            // Clean up: terminate task if still running
            if (taskId != null && !taskId.isEmpty()) {
                try {
                    QueryResult status = agent.getMobile().getTaskStatus(taskId);
                    if (status.isSuccess() && "running".equals(status.getTaskStatus())) {
                        System.out.println("Cleaning up: terminating task " + taskId);
                        ExecutionResult terminateResult = agent.getMobile().terminateTask(taskId);
                        if (terminateResult.isSuccess()) {
                            System.out.println("✅ Task " + taskId + " terminated successfully");
                            Thread.sleep(1000);
                        }
                    }
                } catch (Exception e) {
                    System.out.println("Could not terminate task " + taskId + ": " + e.getMessage());
                }
            }
        }
    }

    @Test
    public void testMobileTerminateTaskSuccess() throws InterruptedException {
        System.out.println("🚀 Test: Mobile terminate_task");

        String task = "Open WeChat app";
        String taskId = null;
        
        try {
            ExecutionResult executeResult = agent.getMobile().executeTask(task, 100);

            if (!executeResult.isSuccess()) {
                System.out.println("ExecutionResult details:");
                System.out.println("  Success: " + executeResult.isSuccess());
                System.out.println("  Error Message: " + executeResult.getErrorMessage());
                System.out.println("  Request ID: " + executeResult.getRequestId());
                System.out.println("  Task ID: " + executeResult.getTaskId());
                System.out.println("  Task Status: " + executeResult.getTaskStatus());
            }
            assertTrue("Task execution should succeed. Error: " + executeResult.getErrorMessage(), executeResult.isSuccess());
            taskId = executeResult.getTaskId();
            assertNotNull("Task ID should not be null", taskId);
            assertFalse("Task ID should not be empty", taskId.isEmpty());

            // Wait a bit for task to start
            Thread.sleep(2000);

            ExecutionResult terminateResult = agent.getMobile().terminateTask(taskId);

            assertTrue("Terminate should succeed", terminateResult.isSuccess());
            assertEquals("Task ID should match", taskId, terminateResult.getTaskId());
            assertEquals("Task status should be cancelling", "cancelling", terminateResult.getTaskStatus());

            System.out.println("✅ Task terminated successfully");

            // Verify task is actually terminated by checking status
            String timeoutEnv = System.getenv("AGENT_TASK_TIMEOUT");
            int timeout = (timeoutEnv != null && !timeoutEnv.isEmpty())
                ? Integer.parseInt(timeoutEnv)
                : 300;
            int pollInterval = 3;
            int maxPollAttempts = Math.min(5, timeout / pollInterval); // Limit to 5 attempts for cleanup
            int retryTimes = 0;

            while (retryTimes < maxPollAttempts) {
                QueryResult queryResult = agent.getMobile().getTaskStatus(taskId);
                if (queryResult.isSuccess()) {
                    String taskStatus = queryResult.getTaskStatus();
                    if ("cancelled".equals(taskStatus) || "completed".equals(taskStatus) || 
                        "failed".equals(taskStatus)) {
                        break;
                    }
                }
                retryTimes++;
                Thread.sleep(pollInterval * 1000);
            }
        } finally {
            // Final cleanup: terminate task if still running
            if (taskId != null && !taskId.isEmpty()) {
                try {
                    QueryResult status = agent.getMobile().getTaskStatus(taskId);
                    if (status.isSuccess() && "running".equals(status.getTaskStatus())) {
                        System.out.println("Final cleanup: attempting to terminate task " + taskId);
                        ExecutionResult terminateResult = agent.getMobile().terminateTask(taskId);
                        if (terminateResult.isSuccess()) {
                            System.out.println("✅ Task " + taskId + " terminated in cleanup");
                            Thread.sleep(1000);
                        } else {
                            // Poll until task completes naturally, but with shorter timeout
                            int maxTryTimes = 5;
                            int retryTimes = 0;
                            while (retryTimes < maxTryTimes) {
                                QueryResult queryStatus = agent.getMobile().getTaskStatus(taskId);
                                if (!queryStatus.isSuccess()) {
                                    break;
                                }
                                if ("completed".equals(queryStatus.getTaskStatus()) || 
                                    "failed".equals(queryStatus.getTaskStatus()) || 
                                    "cancelled".equals(queryStatus.getTaskStatus())) {
                                    System.out.println("✅ Task completed in cleanup: " + queryStatus.getTaskStatus());
                                    break;
                                }
                                retryTimes++;
                                Thread.sleep(1000);
                            }
                        }
                    }
                } catch (Exception e) {
                    System.out.println("Final cleanup failed for task " + taskId + ": " + e.getMessage());
                }
            }
        }
    }

    /**
     * Main method to run tests manually (for debugging purposes).
     * In production, use Maven or IDE test runners.
     */
    public static void main(String[] args) {
        System.out.println("=== Running Mobile Agent Integration Tests ===\n");
        
        TestMobileAgentIntegration test = new TestMobileAgentIntegration();
        
        try {
            TestMobileAgentIntegration.setUp();
            
            System.out.println("\n--- Test 1: Execute Task Success ---");
            test.testMobileExecuteTaskSuccess();
            
            System.out.println("\n--- Test 2: Execute Task And Wait Success ---");
            test.testMobileExecuteTaskAndWaitSuccess();
            
            System.out.println("\n--- Test 3: Get Task Status Success ---");
            test.testMobileGetTaskStatusSuccess();
            
            System.out.println("\n--- Test 4: Terminate Task Success ---");
            test.testMobileTerminateTaskSuccess();
            
            TestMobileAgentIntegration.tearDown();
            
            System.out.println("\n=== All Tests Completed ===");
            
        } catch (Exception e) {
            System.err.println("❌ Test failed: " + e.getMessage());
            e.printStackTrace();
        }
    }
}

