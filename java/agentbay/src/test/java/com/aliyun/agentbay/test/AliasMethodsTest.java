package com.aliyun.agentbay.test;

import com.aliyun.agentbay.AgentBay;
import com.aliyun.agentbay.exception.AgentBayException;
import com.aliyun.agentbay.model.*;
import com.aliyun.agentbay.model.code.EnhancedCodeExecutionResult;
import com.aliyun.agentbay.session.CreateSessionParams;
import com.aliyun.agentbay.session.Session;
import org.junit.*;

import static org.junit.Assert.*;

public class AliasMethodsTest {

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
        params.setImageId("code_latest");

        System.out.println("Creating a new session for alias testing...");
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
            agentBay.delete(session, false);
        } catch (Exception e) {
            System.out.println("Warning: Error deleting session: " + e.getMessage());
        }
    }

    @Test
    public void testSessionFsAlias() {
        System.out.println("Testing session.fs() alias...");
        assertNotNull("fs() should not return null", session.fs());
        assertSame("fs() should return the same FileSystem instance",
            session.getFileSystem(), session.fs());
        System.out.println("✅ testSessionFsAlias passed");
    }

    @Test
    public void testSessionFilesystemAlias() {
        System.out.println("Testing session.getFilesystem() alias...");
        assertNotNull("getFilesystem() should not return null", session.getFilesystem());
        assertSame("getFilesystem() should return the same FileSystem instance",
            session.getFileSystem(), session.getFilesystem());
        System.out.println("✅ testSessionFilesystemAlias passed");
    }

    @Test
    public void testSessionFilesAlias() {
        System.out.println("Testing session.getFiles() alias...");
        assertNotNull("getFiles() should not return null", session.getFiles());
        assertSame("getFiles() should return the same FileSystem instance",
            session.getFileSystem(), session.getFiles());
        System.out.println("✅ testSessionFilesAlias passed");
    }

    @Test
    public void testCommandRunAlias() {
        System.out.println("Testing command.run() alias...");
        CommandResult result1 = session.getCommand().executeCommand("echo 'Hello AgentBay'", 5000);
        CommandResult result2 = session.getCommand().run("echo 'Hello AgentBay'", 5000);

        assertTrue("run() should succeed", result2.isSuccess());
        assertNotNull("run() output should not be null", result2.getOutput());
        assertTrue("run() output should contain expected text",
            result2.getOutput().contains("Hello AgentBay"));
        System.out.println("✅ testCommandRunAlias passed");
    }

    @Test
    public void testCommandExecAlias() {
        System.out.println("Testing command.exec() alias...");
        CommandResult result = session.getCommand().exec("echo 'Test exec'", 5000);

        assertTrue("exec() should succeed", result.isSuccess());
        assertNotNull("exec() output should not be null", result.getOutput());
        assertTrue("exec() output should contain expected text",
            result.getOutput().contains("Test exec"));
        System.out.println("✅ testCommandExecAlias passed");
    }

    @Test
    public void testFileSystemWriteReadDeleteAliases() throws AgentBayException {
        System.out.println("Testing FileSystem write/read/delete aliases...");

        String testPath = "/tmp/alias_test_file.txt";
        String testContent = "Test content for alias methods";

        BoolResult writeResult = session.fs().writeFile(testPath, testContent);
        assertTrue("write() should succeed", writeResult.isSuccess());

        FileContentResult readResult = session.fs().readFile(testPath);
        assertTrue("read() should succeed", readResult.isSuccess());
        assertEquals("read() content should match written content", testContent, readResult.getContent());

        BoolResult deleteResult = session.fs().delete(testPath);
        assertTrue("delete() should succeed", deleteResult.isSuccess());

        System.out.println("✅ testFileSystemWriteReadDeleteAliases passed");
    }

    @Test
    public void testFileSystemRmAlias() throws AgentBayException {
        System.out.println("Testing FileSystem rm() alias...");

        String testPath = "/tmp/alias_test_rm.txt";
        String testContent = "Test content for rm";

        BoolResult writeResult = session.fs().writeFile(testPath, testContent);
        assertTrue("write() should succeed", writeResult.isSuccess());

        BoolResult rmResult = session.fs().rm(testPath);
        assertTrue("rm() should succeed", rmResult.isSuccess());

        System.out.println("✅ testFileSystemRmAlias passed");
    }

    @Test
    public void testFileSystemLsAlias() throws AgentBayException {
        System.out.println("Testing FileSystem ls() alias...");

        session.fs().createDirectory("/tmp/alias_test_dir");
        session.fs().writeFile("/tmp/alias_test_dir/test_file.txt", "test");

        DirectoryListResult lsResult = session.fs().ls("/tmp/alias_test_dir");
        assertTrue("ls() should succeed", lsResult.isSuccess());
        assertNotNull("ls() entries should not be null", lsResult.getEntries());
        assertTrue("ls() should return entries", lsResult.getEntries().size() > 0);

        session.fs().rm("/tmp/alias_test_dir/test_file.txt");

        System.out.println("✅ testFileSystemLsAlias passed");
    }

    @Test
    public void testCodeRunAlias() {
        System.out.println("Testing Code.run() alias...");

        String pythonCode = "print('Hello from run alias')";
        EnhancedCodeExecutionResult result = session.getCode().run(pythonCode, "python");

        assertTrue("run() should succeed", result.isSuccess());
        assertNotNull("run() results should not be null", result.getResults());

        System.out.println("✅ testCodeRunAlias passed");
    }

    @Test
    public void testCodeRunWithTimeoutAlias() {
        System.out.println("Testing Code.run() with timeout alias...");

        String pythonCode = "import time\nprint('Start')\ntime.sleep(0.5)\nprint('End')";
        EnhancedCodeExecutionResult result = session.getCode().run(pythonCode, "python", 10);

        assertTrue("run() with timeout should succeed", result.isSuccess());

        System.out.println("✅ testCodeRunWithTimeoutAlias passed");
    }

    @Test
    public void testAllAliasesWorkTogether() throws AgentBayException {
        System.out.println("Testing all aliases work together...");

        String testPath = "/tmp/integrated_alias_test.txt";
        String testContent = "Integrated test for all aliases";

        session.fs().writeFile(testPath, testContent);

        CommandResult cmdResult = session.getCommand().run("cat " + testPath, 5000);
        assertTrue("Command run() should succeed", cmdResult.isSuccess());
        assertTrue("Command output should contain expected content",
            cmdResult.getOutput().contains(testContent));

        String pythonCode = String.format(
            "with open('%s', 'r') as f:\n    print(f.read())",
            testPath
        );
        EnhancedCodeExecutionResult codeResult = session.getCode().run(pythonCode, "python");
        assertTrue("Code run() should succeed", codeResult.isSuccess());

        DirectoryListResult lsResult = session.fs().ls("/tmp");
        assertTrue("ls() should succeed", lsResult.isSuccess());

        session.fs().rm(testPath);

        System.out.println("✅ testAllAliasesWorkTogether passed");
    }

    public static void main(String[] args) {
        System.out.println("=== Running Alias Methods Tests ===\n");

        try {
            setUp();

            AliasMethodsTest test = new AliasMethodsTest();
            test.testSessionFsAlias();
            test.testSessionFilesystemAlias();
            test.testSessionFilesAlias();
            test.testCommandRunAlias();
            test.testCommandExecAlias();
            test.testFileSystemWriteReadDeleteAliases();
            test.testFileSystemRmAlias();
            test.testFileSystemLsAlias();
            test.testCodeRunAlias();
            test.testCodeRunWithTimeoutAlias();
            test.testAllAliasesWorkTogether();

            tearDown();

            System.out.println("\n=== All Alias Tests Completed Successfully ===");
        } catch (Exception e) {
            System.err.println("❌ Test failed: " + e.getMessage());
            e.printStackTrace();
        }
    }
}
