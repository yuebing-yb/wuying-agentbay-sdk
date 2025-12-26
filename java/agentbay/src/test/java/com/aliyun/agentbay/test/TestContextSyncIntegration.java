package com.aliyun.agentbay.test;

import com.aliyun.agentbay.AgentBay;
import com.aliyun.agentbay.context.*;
import com.aliyun.agentbay.exception.AgentBayException;
import com.aliyun.agentbay.model.BoolResult;
import com.aliyun.agentbay.model.CommandResult;
import com.aliyun.agentbay.model.DeleteResult;
import com.aliyun.agentbay.model.SessionResult;
import com.aliyun.agentbay.session.CreateSessionParams;
import com.aliyun.agentbay.session.Session;
import org.junit.*;
import java.util.Arrays;

import static org.junit.Assert.*;

/**
 * Integration tests for context synchronization functionality
 * Tests complete context sync workflow across multiple sessions
 * 
 * This test is equivalent to Python's test_context_sync_integration.py
 */
public class TestContextSyncIntegration {
    private static AgentBay agentBay;
    
    @BeforeClass
    public static void setUpClass() throws AgentBayException {
        // Skip if no API key is available or in CI environment
        String apiKey = System.getenv("AGENTBAY_API_KEY");
        String ci = System.getenv("CI");
        if (apiKey == null || apiKey.trim().isEmpty() || "true".equals(ci)) {
            throw new IllegalStateException(
                "Skipping integration test: No API key available or running in CI"
            );
        }
        
        // Initialize AgentBay client
        agentBay = new AgentBay();
    }
    
    /**
     * Test context synchronization persistence with retry
     * 
     * This test verifies the complete context sync workflow:
     * 1. Create a context
     * 2. Create first session with context sync
     * 3. Create a test file in the sync path
     * 4. Trigger context sync
     * 5. Delete first session with sync_context=true
     * 6. Create second session with same context
     * 7. Verify file exists in second session
     */
    @Test
    public void testContextSyncPersistenceWithRetry() throws Exception {
        // 1. Create a unique context name and get its ID
        String contextName = "test-persistence-retry-java-" + System.currentTimeMillis();
        ContextResult contextResult = agentBay.getContext().get(contextName, true);
        assertTrue("Error getting/creating context", contextResult.isSuccess());
        assertNotNull("Context should not be None", contextResult.getContext());
        
        Context context = contextResult.getContext();
        Session session1 = null;
        Session session2 = null;
        
        try {
            // 2. Create a session with context sync, using a timestamped path under /home/wuying/
            long timestamp = System.currentTimeMillis();
            String syncPath = "/home/wuying/test-path-java-" + timestamp;
            
            // Use default policy
            SyncPolicy defaultPolicy = SyncPolicy.defaultPolicy();
            
            // Create session parameters with context sync
            CreateSessionParams sessionParams = new CreateSessionParams();
            ContextSync contextSync = ContextSync.create(context.getId(), syncPath, defaultPolicy);
            sessionParams.setContextSyncs(Arrays.asList(contextSync));
            sessionParams.setImageId("linux_latest");
            
            // Create first session
            SessionResult sessionResult = agentBay.create(sessionParams);
            assertTrue("Error creating first session", sessionResult.isSuccess());
            assertNotNull("Session should not be null", sessionResult.getSession());
            
            session1 = sessionResult.getSession();
            // 3. Wait for session to be ready and retry context info until data is available
            boolean foundData = false;
            ContextInfoResult contextInfo = null;
            
            for (int i = 0; i < 20; i++) {
                contextInfo = session1.getContext().info();
                
                if (!contextInfo.getContextStatusData().isEmpty()) {
                    foundData = true;
                    break;
                }
                Thread.sleep(1000);
            }
            
            assertTrue("Context status data should be available after retries", foundData);
            printContextStatusData(contextInfo.getContextStatusData());
            
            // 4. Create a test file in the context sync path
            String testFilePath = syncPath + "/test-file.txt";
            // Build test content using StringBuilder for Java 8 compatibility
            StringBuilder contentBuilder = new StringBuilder();
            for (int i = 0; i < 100; i++) {
                contentBuilder.append("Test content for context sync persistence\n");
            }
            String testContent = contentBuilder.toString();
            
            // Create directory first
            BoolResult dirResult = session1.getFileSystem().createDirectory(syncPath);
            assertTrue("Error creating directory", dirResult.isSuccess());
            
            // Create test file
            BoolResult fileResult = session1.getFileSystem().writeFile(
                testFilePath, 
                testContent
            );
            assertTrue("Error creating test file", fileResult.isSuccess());
            // 5. Sync to trigger file upload
            ContextSyncResult syncResult = session1.getContext().syncAndWait();
            assertTrue("Context sync should be successful", syncResult.isSuccess());
            // 6. Get context info with retry for upload status
            boolean foundUpload = false;
            for (int i = 0; i < 20; i++) {
                contextInfo = session1.getContext().info();
                
                // Check if we have upload status for our context
                for (ContextStatusData data : contextInfo.getContextStatusData()) {
                    if (data.getContextId().equals(context.getId()) && "upload".equals(data.getTaskType())) {
                        foundUpload = true;
                        break;
                    }
                }
                
                if (foundUpload) {
                    break;
                }
                Thread.sleep(1000);
            }
            
            if (foundUpload) {
                printContextStatusData(contextInfo.getContextStatusData());
            } else {
            }
            
            // 7. Release first session
            DeleteResult deleteResult = agentBay.delete(session1, true);
            assertTrue("Error deleting first session", deleteResult.isSuccess());
            session1 = null;  // Mark as deleted
            
            // 8. Create a second session with the same context
            sessionParams = new CreateSessionParams();
            contextSync = ContextSync.create(context.getId(), syncPath, defaultPolicy);
            sessionParams.setContextSyncs(Arrays.asList(contextSync));
            sessionParams.setImageId("linux_latest");
            
            sessionResult = agentBay.create(sessionParams);
            assertTrue("Error creating second session", sessionResult.isSuccess());
            assertNotNull("Second session should not be null", sessionResult.getSession());
            
            session2 = sessionResult.getSession();
            // 9. Get context info with retry for download status
            boolean foundDownload = false;
            for (int i = 0; i < 20; i++) {
                contextInfo = session2.getContext().info();
                
                // Check if we have download status for our context
                for (ContextStatusData data : contextInfo.getContextStatusData()) {
                    if (data.getContextId().equals(context.getId()) && "download".equals(data.getTaskType())) {
                        foundDownload = true;
                        break;
                    }
                }
                
                if (foundDownload) {
                    break;
                }
                Thread.sleep(1000);
            }
            
            if (foundDownload) {
                printContextStatusData(contextInfo.getContextStatusData());
            } else {
            }
            
            // 10. Verify the test file exists in the second session
            // Check file exists using command
            String checkFileCmd = "test -f " + testFilePath + " && echo 'File exists'";
            CommandResult existsResult = session2.getCommand().executeCommand(checkFileCmd, 5000);
            assertTrue("Error checking if file exists", existsResult.isSuccess());
            assertTrue("Test file should exist in second session", 
                      existsResult.getOutput().contains("File exists"));
            // Read file content to verify it matches
            try {
                String readContent = session2.getFileSystem().read(testFilePath);
                assertEquals("File content should match", testContent, readContent);
            } catch (AgentBayException e) {
                fail("Should be able to read the file");
            }
        } finally {
            // Clean up sessions
            if (session1 != null) {
                try {
                    agentBay.delete(session1, false);
                } catch (Exception e) {
                }
            }
            
            if (session2 != null) {
                try {
                    agentBay.delete(session2, false);
                } catch (Exception e) {
                }
            }
            
            // Clean up context
            try {
                agentBay.getContext().delete(context);
            } catch (Exception e) {
            }
        }
    }
    
    /**
     * Test RecyclePolicy with custom lifecycle
     */
    @Test
    public void testRecyclePolicyWithLifecycle1Day() {
        // Create a custom recycle policy with Lifecycle_1Day
        RecyclePolicy customRecyclePolicy = new RecyclePolicy(
            Lifecycle.LIFECYCLE_1DAY,
            Arrays.asList("/custom/path")
        );
        
        // Create a sync policy with the custom recycle policy
        SyncPolicy syncPolicy = new SyncPolicy(
            UploadPolicy.defaultPolicy(),
            DownloadPolicy.defaultPolicy(),
            DeletePolicy.defaultPolicy(),
            ExtractPolicy.defaultPolicy(),
            customRecyclePolicy,
            new BWList(Arrays.asList(new WhiteList("", Arrays.asList())))
        );
        
        // Verify the recycle policy
        assertNotNull("Recycle policy should not be null", syncPolicy.getRecyclePolicy());
        assertEquals("Lifecycle should be LIFECYCLE_1DAY", 
                    Lifecycle.LIFECYCLE_1DAY, 
                    syncPolicy.getRecyclePolicy().getLifecycle());
        assertNotNull("Paths should not be null", syncPolicy.getRecyclePolicy().getPaths());
        assertEquals("Should have one path", 1, syncPolicy.getRecyclePolicy().getPaths().size());
        assertEquals("Path should match", "/custom/path", syncPolicy.getRecyclePolicy().getPaths().get(0));
        
        // Create ContextSync with the custom policy
        ContextSync contextSync = ContextSync.create(
            "test-recycle-context",
            "/test/recycle/path",
            syncPolicy
        );
        
        // Verify ContextSync properties
        assertEquals("Context ID should match", "test-recycle-context", contextSync.getContextId());
        assertEquals("Path should match", "/test/recycle/path", contextSync.getPath());
        assertEquals("Policy should match", syncPolicy, contextSync.getPolicy());
    }
    
    /**
     * Helper method to print context status data
     */
    private void printContextStatusData(java.util.List<ContextStatusData> data) {
        if (data == null || data.isEmpty()) {
            return;
        }
        
        for (int i = 0; i < data.size(); i++) {
            ContextStatusData item = data.get(i);

            if (item.getErrorMessage() != null && !item.getErrorMessage().isEmpty()) {
            }
        }
    }
}

