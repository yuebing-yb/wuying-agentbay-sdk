package com.aliyun.agentbay.test;

import com.aliyun.agentbay.AgentBay;
import com.aliyun.agentbay.context.Context;
import com.aliyun.agentbay.context.ContextListResult;
import com.aliyun.agentbay.context.ContextResult;
import com.aliyun.agentbay.context.ContextSync;
import com.aliyun.agentbay.context.SyncPolicy;
import com.aliyun.agentbay.exception.AgentBayException;
import com.aliyun.agentbay.model.CommandResult;
import com.aliyun.agentbay.model.DeleteResult;
import com.aliyun.agentbay.model.SessionResult;
import com.aliyun.agentbay.session.CreateSessionParams;
import com.aliyun.agentbay.session.Session;
import org.junit.AfterClass;
import org.junit.BeforeClass;
import org.junit.Test;
import java.util.Arrays;

import static org.junit.Assert.*;

/**
 * JUnit 4 test cases for SessionContextExample functionality
 * Tests context management operations including list, get, create, update and cleanup
 */
public class TestSessionContextExample {
    private static AgentBay agentBay;
    private static Session session;
    private static Context context;
    private static String apiKey;
    private static String contextName;

    @BeforeClass
    public static void setUpClass() {
    }

    @BeforeClass
    public static void setUp() throws AgentBayException {
        // Get API key from environment variable
        apiKey = System.getenv("AGENTBAY_API_KEY");
        assertNotNull("AGENTBAY_API_KEY environment variable must be set", apiKey);
        assertFalse("AGENTBAY_API_KEY must not be empty", apiKey.trim().isEmpty());
        
        // Initialize AgentBay client
        agentBay = new AgentBay();
        assertNotNull("AgentBay client should be initialized", agentBay);
        
        // Generate unique context name for this test run
        contextName = "test-context-java-" + System.currentTimeMillis();
    }

    @AfterClass
    public static void tearDown() {
        // Clean up session if it was created
        if (agentBay != null && session != null) {
            try {
                DeleteResult deleteResult = agentBay.delete(session, true);
                assertTrue("Session should be deleted successfully", deleteResult.isSuccess());
                assertNotNull("Delete result should have request ID", deleteResult.getRequestId());
            } catch (Exception e) {
            }
        }
    }

    @AfterClass
    public static void tearDownClass() {
    }

    /**
     * Test 1: List all contexts
     */
    @Test
    public void testListContexts() {
        try {
            ContextListResult result = agentBay.getContext().list();
            
            // Verify result
            assertNotNull("Context list result should not be null", result);
            assertNotNull("Request ID should not be null", result.getRequestId());
            assertTrue("List contexts should be successful", result.isSuccess());
            assertNotNull("Contexts list should not be null", result.getContexts());
            // Log context details
            for (Context ctx : result.getContexts()) {
            }
            
        } catch (Exception e) {
            fail("Should not throw exception when listing contexts: " + e.getMessage());
        }
    }

    /**
     * Test 2: Get a context (create if it doesn't exist)
     */
    @Test
    public void testGetOrCreateContext() {
        try {
            ContextResult result = agentBay.getContext().get(contextName, true);
            
            // Verify result
            assertNotNull("Context result should not be null", result);
            assertNotNull("Request ID should not be null", result.getRequestId());
            assertTrue("Get context should be successful", result.isSuccess());
            assertNotNull("Context should not be null", result.getContext());
            
            context = result.getContext();
            assertNotNull("Context ID should not be null", context.getId());
            assertEquals("Context name should match", contextName, context.getName());
        } catch (Exception e) {
            fail("Should not throw exception when getting or creating context: " + e.getMessage());
        }
    }

    /**
     * Test 3: Create a session with context
     */
    @Test
    public void testCreateSessionWithContext() {
        try {
            // First get or create context
            ContextResult contextResult = agentBay.getContext().get(contextName, true);
            assertTrue("Get context should be successful", contextResult.isSuccess());
            assertNotNull("Context should not be null", contextResult.getContext());
            context = contextResult.getContext();
            // Create session with context
            CreateSessionParams params = new CreateSessionParams();
            
            SyncPolicy syncPolicy = SyncPolicy.defaultPolicy();
            ContextSync contextSync = ContextSync.create(
                context.getId(),
                "/tmp/shared",
                syncPolicy
            );
            params.setContextSyncs(Arrays.asList(contextSync));
            params.setImageId("linux_latest");
            
            SessionResult sessionResult = agentBay.create(params);
            
            // Verify result
            assertNotNull("Session result should not be null", sessionResult);
            assertNotNull("Request ID should not be null", sessionResult.getRequestId());
            assertNotNull("Session should not be null", sessionResult.getSession());
            
            session = sessionResult.getSession();
            assertNotNull("Session ID should not be null", session.getSessionId());
        } catch (AgentBayException e) {
            fail("Should not throw exception when creating session: " + e.getMessage());
        }
    }

    /**
     * Test 4: Execute commands in session with context
     */
    @Test
    public void testExecuteCommandsInContextSession() {
        try {
            // First get or create context
            ContextResult contextResult = agentBay.getContext().get(contextName, true);
            assertTrue("Get context should be successful", contextResult.isSuccess());
            context = contextResult.getContext();
            
            // Create session with context
            CreateSessionParams params = new CreateSessionParams();
            SyncPolicy syncPolicy = SyncPolicy.defaultPolicy();
            ContextSync contextSync = ContextSync.create(
                context.getId(),
                "/tmp/shared",
                syncPolicy
            );
            params.setContextSyncs(Arrays.asList(contextSync));
            params.setImageId("linux_latest");
            
            SessionResult sessionResult = agentBay.create(params);
            session = sessionResult.getSession();
            // Execute first command: create directory and file
            String createCommand = "mkdir -p /tmp/shared/ && touch /tmp/shared/" + session.getSessionId();
            CommandResult commandResult = session.getCommand().executeCommand(createCommand, 1000);
            
            assertNotNull("Command result should not be null", commandResult);
            assertTrue("Command should execute successfully: " + commandResult.getErrorMessage(), 
                      commandResult.isSuccess());
            assertNotNull("Command result should have request ID", commandResult.getRequestId());

            // Execute second command: list directory contents
            CommandResult listResult = session.getCommand().executeCommand("ls -al /tmp/shared", 1000);
            
            assertNotNull("List command result should not be null", listResult);
            assertTrue("List command should execute successfully: " + listResult.getErrorMessage(), 
                      listResult.isSuccess());
            assertNotNull("List command result should have request ID", listResult.getRequestId());
            assertNotNull("List command should have output", listResult.getOutput());

            // Verify the file was created (should be in the output)
            assertTrue("Output should contain the created file", 
                      listResult.getOutput().contains(session.getSessionId()));
            
        } catch (Exception e) {
            fail("Should not throw exception when executing commands: " + e.getMessage());
        }
    }

    /**
     * Test 5: Complete workflow - list, get, create session, execute commands, and cleanup
     */
    @Test
    public void testCompleteContextWorkflow() {
        try {
            // Step 1: List all contexts
            ContextListResult listResult = agentBay.getContext().list();
            assertTrue("List contexts should be successful", listResult.isSuccess());
            int initialContextCount = listResult.getContexts().size();
            // Step 2: Get or create context
            ContextResult contextResult = agentBay.getContext().get(contextName, true);
            assertTrue("Get context should be successful", contextResult.isSuccess());
            assertNotNull("Context should not be null", contextResult.getContext());
            context = contextResult.getContext();
            // Step 3: Create session with context
            CreateSessionParams params = new CreateSessionParams();
            SyncPolicy syncPolicy = SyncPolicy.defaultPolicy();
            ContextSync contextSync = ContextSync.create(
                context.getId(),
                "/tmp/shared",
                syncPolicy
            );
            params.setContextSyncs(Arrays.asList(contextSync));
            params.setImageId("linux_latest");
            
            SessionResult sessionResult = agentBay.create(params);
            session = sessionResult.getSession();
            assertNotNull("Session should be created", session);
            // Step 4: Execute commands
            String createCommand = "mkdir -p /tmp/shared/ && touch /tmp/shared/" + session.getSessionId();
            CommandResult createResult = session.getCommand().executeCommand(createCommand, 1000);
            assertTrue("Create command should succeed", createResult.isSuccess());
            
            CommandResult listCommandResult = session.getCommand().executeCommand("ls -al /tmp/shared", 1000);
            assertTrue("List command should succeed", listCommandResult.isSuccess());
            assertTrue("Created file should exist in output", 
                      listCommandResult.getOutput().contains(session.getSessionId()));
            // Step 5: Delete session with context synchronization
            DeleteResult deleteResult = agentBay.delete(session, true);
            assertTrue("Session deletion should be successful", deleteResult.isSuccess());
            assertNotNull("Delete result should have request ID", deleteResult.getRequestId());
            // Clear session reference to prevent duplicate cleanup
            session = null;
        } catch (Exception e) {
            fail("Should not throw exception in complete workflow: " + e.getMessage());
        }
    }

    /**
     * Test 6: Get non-existent context without auto-create
     */
    @Test
    public void testGetNonExistentContextWithoutCreate() {
        String nonExistentContextName = "non-existent-context-" + System.currentTimeMillis();
        
        try {
            // Try to get context without creating it (second parameter = false)
            ContextResult result = agentBay.getContext().get(nonExistentContextName, false);
            
            assertNotNull("Context result should not be null", result);
            assertNotNull("Request ID should not be null", result.getRequestId());
            
            // Context should be null when it doesn't exist and auto-create is false
            if (!result.isSuccess() || result.getContext() == null) {
            } else {
            }
            
        } catch (Exception e) {
            // This is acceptable behavior
        }
    }

    /**
     * Test 7: Create session with invalid context should fail gracefully
     */
    @Test
    public void testCreateSessionWithInvalidContext() {
        try {
            CreateSessionParams params = new CreateSessionParams();
            
            // Use an invalid context ID
            String invalidContextId = "invalid-context-id-12345";
            SyncPolicy syncPolicy = SyncPolicy.defaultPolicy();
            ContextSync contextSync = ContextSync.create(
                invalidContextId,
                "/tmp/shared",
                syncPolicy
            );
            params.setContextSyncs(Arrays.asList(contextSync));
            params.setImageId("linux_latest");
            
            try {
                SessionResult sessionResult = agentBay.create(params);
                // If it succeeds, that's unexpected but we should handle it
                session = sessionResult.getSession();
            } catch (AgentBayException e) {
                // This is the expected behavior
            }
            
        } catch (Exception e) {
            // This is acceptable behavior
        }
    }
}

