package com.aliyun.agentbay.test;

import com.aliyun.agentbay.AgentBay;
import com.aliyun.agentbay.exception.AgentBayException;
import com.aliyun.agentbay.model.BoolResult;
import com.aliyun.agentbay.model.FileInfoResult;
import com.aliyun.agentbay.model.SessionResult;
import com.aliyun.agentbay.session.CreateSessionParams;
import com.aliyun.agentbay.session.Session;
import org.junit.*;

import static org.junit.Assert.*;

/**
 * Test cases for FileSystem.deleteFile method
 */
public class FileSystemDeleteTest {

    private static AgentBay agentBay;
    private static Session session;

    private static String getTestApiKey() {
        String apiKey = System.getenv("AGENTBAY_API_KEY");
        if (apiKey == null || apiKey.trim().isEmpty()) {
            apiKey = "akm-xxx";
            System.out.println("Warning: Using default API key. Set AGENTBAY_API_KEY environment variable for testing.");
        }
        return apiKey;
    }

    @BeforeClass
    public static void setUp() throws AgentBayException {
        String apiKey = getTestApiKey();
        agentBay = new AgentBay(apiKey);

        CreateSessionParams params = new CreateSessionParams();
        params.setImageId("linux_latest");

        System.out.println("Creating a new session for delete file testing...");
        SessionResult result = agentBay.create(params);

        if (!result.isSuccess()) {
            fail("Session creation failed in setUp: " + result.getErrorMessage());
        }
        if (result.getSession() == null) {
            fail("Session object is null in setUp");
        }

        session = result.getSession();
        System.out.println("Session created with ID: " + session.getSessionId());
    }

    @AfterClass
    public static void tearDown() {
        System.out.println("Cleaning up: Deleting the session...");
        try {
            if (session != null) {
                agentBay.delete(session, false);
            }
        } catch (Exception e) {
            System.out.println("Warning: Error deleting session: " + e.getMessage());
        }
    }

    @Test
    public void testDeleteFile() {
        if (session.getFileSystem() == null) {
            System.out.println("Note: FileSystem interface is null, skipping delete file test");
            return;
        }

        String testFilePath = "/tmp/test_delete_" + System.currentTimeMillis() + ".txt";
        String testContent = "This is a test file content for deleteFile test.";

        System.out.println("Creating test file: " + testFilePath);
        BoolResult writeResult = session.getFileSystem().writeFile(testFilePath, testContent);
        assertTrue("File creation should succeed", writeResult.isSuccess());

        System.out.println("Deleting test file: " + testFilePath);
        BoolResult deleteResult = session.getFileSystem().deleteFile(testFilePath);
        assertTrue("deleteFile should succeed", deleteResult.isSuccess());
        assertNotNull("deleteResult should have requestId", deleteResult.getRequestId());

        System.out.println("Verifying file is deleted");
        FileInfoResult infoResult = session.getFileSystem().getFileInfo(testFilePath);
        assertFalse("getFileInfo should fail after deletion", infoResult.isSuccess());

        System.out.println("✅ testDeleteFile passed");
    }

    @Test
    public void testDeleteNonExistentFile() {
        if (session.getFileSystem() == null) {
            System.out.println("Note: FileSystem interface is null, skipping delete file test");
            return;
        }

        String nonExistentPath = "/tmp/non_existent_file_" + System.currentTimeMillis() + ".txt";

        System.out.println("Attempting to delete non-existent file: " + nonExistentPath);
        BoolResult deleteResult = session.getFileSystem().deleteFile(nonExistentPath);
        assertFalse("deleteFile should fail for non-existent file", deleteResult.isSuccess());
        assertNotNull("deleteResult should have error message", deleteResult.getErrorMessage());

        System.out.println("✅ testDeleteNonExistentFile passed");
    }

    @Test
    public void testDeleteUsingAlias() {
        if (session.getFileSystem() == null) {
            System.out.println("Note: FileSystem interface is null, skipping delete alias test");
            return;
        }

        String testFilePath = "/tmp/test_delete_alias_" + System.currentTimeMillis() + ".txt";
        String testContent = "Test file for alias deletion";

        System.out.println("Creating test file: " + testFilePath);
        session.getFileSystem().writeFile(testFilePath, testContent);

        System.out.println("Deleting using rm() alias: " + testFilePath);
        BoolResult deleteResult = session.getFileSystem().rm(testFilePath);
        assertTrue("rm() alias should succeed", deleteResult.isSuccess());

        System.out.println("Verifying file is deleted");
        FileInfoResult infoResult = session.getFileSystem().getFileInfo(testFilePath);
        assertFalse("getFileInfo should fail after deletion", infoResult.isSuccess());

        System.out.println("✅ testDeleteUsingAlias passed");
    }

    @Test
    public void testDeleteUsingRemoveAlias() {
        if (session.getFileSystem() == null) {
            System.out.println("Note: FileSystem interface is null, skipping delete alias test");
            return;
        }

        String testFilePath = "/tmp/test_delete_remove_alias_" + System.currentTimeMillis() + ".txt";
        String testContent = "Test file for remove() alias deletion";

        System.out.println("Creating test file: " + testFilePath);
        session.getFileSystem().writeFile(testFilePath, testContent);

        System.out.println("Deleting using remove() alias: " + testFilePath);
        BoolResult deleteResult = session.getFileSystem().remove(testFilePath);
        assertTrue("remove() alias should succeed", deleteResult.isSuccess());

        System.out.println("Verifying file is deleted");
        FileInfoResult infoResult = session.getFileSystem().getFileInfo(testFilePath);
        assertFalse("getFileInfo should fail after deletion", infoResult.isSuccess());

        System.out.println("✅ testDeleteUsingRemoveAlias passed");
    }
}
