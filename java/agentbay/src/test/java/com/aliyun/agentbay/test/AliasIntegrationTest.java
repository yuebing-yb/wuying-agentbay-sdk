package com.aliyun.agentbay.test;

import com.aliyun.agentbay.AgentBay;
import com.aliyun.agentbay.exception.AgentBayException;
import com.aliyun.agentbay.model.*;
import com.aliyun.agentbay.model.code.EnhancedCodeExecutionResult;
import com.aliyun.agentbay.session.CreateSessionParams;
import com.aliyun.agentbay.session.Session;
import org.junit.*;

import static org.junit.Assert.*;

public class AliasIntegrationTest {

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
    public static void setUp() throws AgentBayException, InterruptedException {
        Thread.sleep(3000);

        String apiKey = getTestApiKey();
        agentBay = new AgentBay(apiKey);

        CreateSessionParams params = new CreateSessionParams();
        params.setImageId("code_latest");

        System.out.println("Creating a new session for alias integration testing...");
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
    public void testRealWorldScenarioWithAliases() throws AgentBayException {
        System.out.println("🚀 Test: Real-world scenario using all alias methods");

        String projectDir = "/tmp/alias_integration_test";

        System.out.println("Step 1: Create project directory using fs() alias");
        session.fs().createDirectory(projectDir);

        System.out.println("Step 2: Write project files using fs() alias");
        String readmeContent = "# Alias Integration Test\n\nThis project tests alias methods.";
        session.fs().writeFile(projectDir + "/README.md", readmeContent);

        String scriptContent = "print('Hello from Python script')\nresult = 2 + 2\nprint(f'Result: {result}')";
        session.fs().writeFile(projectDir + "/script.py", scriptContent);

        System.out.println("Step 3: List directory using ls() alias");
        DirectoryListResult lsResult = session.fs().ls(projectDir);
        assertTrue("ls() should succeed", lsResult.isSuccess());
        assertTrue("Should have files", lsResult.getEntries().size() >= 2);
        System.out.println("Files in directory: " + lsResult.getEntries().size());

        System.out.println("Step 4: Execute shell commands using run() and exec() aliases");
        CommandResult cmdResult1 = session.getCommand().run("ls -la " + projectDir, 5000);
        assertTrue("run() should succeed", cmdResult1.isSuccess());
        assertTrue("Output should contain README.md", cmdResult1.getOutput().contains("README.md"));

        CommandResult cmdResult2 = session.getCommand().exec("cat " + projectDir + "/README.md", 5000);
        assertTrue("exec() should succeed", cmdResult2.isSuccess());
        assertTrue("Output should contain title", cmdResult2.getOutput().contains("Alias Integration Test"));

        System.out.println("Step 5: Run Python code using run() alias");
        String pythonCode = String.format(
            "with open('%s/script.py', 'r') as f:\n    content = f.read()\nprint('Script content:')\nprint(content)",
            projectDir
        );
        EnhancedCodeExecutionResult codeResult = session.getCode().run(pythonCode, "python");
        assertTrue("Code run() should succeed", codeResult.isSuccess());

        System.out.println("Step 6: Execute the Python script");
        String executeScript = String.format("exec(open('%s/script.py').read())", projectDir);
        EnhancedCodeExecutionResult execResult = session.getCode().run(executeScript, "python", 10);
        assertTrue("Script execution should succeed", execResult.isSuccess());

        System.out.println("Step 7: Create a log file");
        String logContent = "Test completed successfully\nTimestamp: " + System.currentTimeMillis();
        session.fs().writeFile(projectDir + "/test.log", logContent);

        System.out.println("Step 8: Verify log file with command alias");
        CommandResult catLog = session.getCommand().run("cat " + projectDir + "/test.log", 5000);
        assertTrue("cat should succeed", catLog.isSuccess());
        assertTrue("Log should contain timestamp", catLog.getOutput().contains("Timestamp"));

        System.out.println("Step 9: Clean up using rm() alias");
        session.fs().rm(projectDir + "/README.md");
        session.fs().rm(projectDir + "/script.py");
        session.fs().rm(projectDir + "/test.log");

        System.out.println("Step 10: Verify cleanup");
        DirectoryListResult afterCleanup = session.fs().ls(projectDir);
        assertTrue("Directory should still exist", afterCleanup.isSuccess());

        System.out.println("✅ Real-world scenario test passed");
    }

    @Test
    public void testChainedAliasOperations() throws AgentBayException {
        System.out.println("🚀 Test: Chained alias operations");

        String testDir = "/tmp/chained_test";
        session.fs().createDirectory(testDir);

        for (int i = 1; i <= 5; i++) {
            String filename = testDir + "/file" + i + ".txt";
            String content = "Content for file " + i;
            session.fs().writeFile(filename, content);
        }

        DirectoryListResult listResult = session.fs().ls(testDir);
        assertTrue("ls() should find files", listResult.getEntries().size() >= 5);

        CommandResult countFiles = session.getCommand().run("ls " + testDir + " | wc -l", 5000);
        assertTrue("Command should succeed", countFiles.isSuccess());

        String pythonCode = String.format(
            "import os\nfiles = os.listdir('%s')\nprint(f'Found {len(files)} files')\nfor f in sorted(files):\n    print(f)",
            testDir
        );
        EnhancedCodeExecutionResult codeResult = session.getCode().run(pythonCode, "python");
        assertTrue("Python code should succeed", codeResult.isSuccess());

        for (int i = 1; i <= 5; i++) {
            session.fs().delete(testDir + "/file" + i + ".txt");
        }

        System.out.println("✅ Chained operations test passed");
    }

    @Test
    public void testAliasCompatibilityWithOriginalMethods() throws AgentBayException {
        System.out.println("🚀 Test: Alias compatibility with original methods");

        String testFile = "/tmp/compatibility_test.txt";
        String testContent = "Compatibility test content";

        BoolResult writeOriginal = session.getFileSystem().writeFile(testFile, testContent);
        assertTrue("Original writeFile should succeed", writeOriginal.isSuccess());

        FileContentResult readAlias = session.fs().readFile(testFile);
        assertTrue("Alias read should succeed", readAlias.isSuccess());
        assertEquals("Content should match", testContent, readAlias.getContent());

        BoolResult deleteAlias = session.fs().rm(testFile);
        assertTrue("Alias delete should succeed", deleteAlias.isSuccess());

        CommandResult cmdOriginal = session.getCommand().executeCommand("echo 'original'", 5000);
        assertTrue("Original command should succeed", cmdOriginal.isSuccess());

        CommandResult cmdAlias = session.getCommand().run("echo 'alias'", 5000);
        assertTrue("Alias command should succeed", cmdAlias.isSuccess());

        String code = "print('test')";
        EnhancedCodeExecutionResult codeOriginal = session.getCode().runCode(code, "python");
        assertTrue("Original runCode should succeed", codeOriginal.isSuccess());

        EnhancedCodeExecutionResult codeAlias = session.getCode().run(code, "python");
        assertTrue("Alias run should succeed", codeAlias.isSuccess());

        System.out.println("✅ Compatibility test passed");
    }

    @Test
    public void testMultipleSessionsWithAliases() throws AgentBayException {
        System.out.println("🚀 Test: Multiple sessions using aliases");

        CreateSessionParams params = new CreateSessionParams();
        params.setImageId("code_latest");

        SessionResult result2 = agentBay.create(params);
        assertTrue("Second session creation should succeed", result2.isSuccess());
        Session session2 = result2.getSession();

        try {
            String file1 = "/tmp/session1_test.txt";
            String file2 = "/tmp/session2_test.txt";

            session.fs().writeFile(file1, "Session 1 content");
            session2.fs().writeFile(file2, "Session 2 content");

            FileContentResult read1 = session.fs().readFile(file1);
            assertTrue("Session 1 read should succeed", read1.isSuccess());
            assertEquals("Content should be from session 1", "Session 1 content", read1.getContent());

            FileContentResult read2 = session2.fs().readFile(file2);
            assertTrue("Session 2 read should succeed", read2.isSuccess());
            assertEquals("Content should be from session 2", "Session 2 content", read2.getContent());

            CommandResult cmd1 = session.getCommand().run("echo 'Session 1'", 5000);
            CommandResult cmd2 = session2.getCommand().run("echo 'Session 2'", 5000);
            assertTrue("Both commands should succeed", cmd1.isSuccess() && cmd2.isSuccess());

            session.fs().rm(file1);
            session2.fs().rm(file2);

            System.out.println("✅ Multiple sessions test passed");

        } finally {
            agentBay.delete(session2, false);
        }
    }

    @Test
    public void testAliasesUnderStress() throws AgentBayException {
        System.out.println("🚀 Test: Aliases under stress (rapid operations)");

        String stressDir = "/tmp/stress_test";
        session.fs().createDirectory(stressDir);

        int fileCount = 20;
        for (int i = 0; i < fileCount; i++) {
            String filename = stressDir + "/stress_" + i + ".txt";
            session.fs().writeFile(filename, "Stress test content " + i);
        }

        for (int i = 0; i < fileCount; i++) {
            String filename = stressDir + "/stress_" + i + ".txt";
            FileContentResult result = session.fs().readFile(filename);
            assertTrue("Read should succeed for file " + i, result.isSuccess());
        }

        DirectoryListResult listResult = session.getFilesystem().ls(stressDir);
        assertTrue("ls() should succeed", listResult.isSuccess());
        assertTrue("Should have all files", listResult.getEntries().size() >= fileCount);

        for (int i = 0; i < fileCount; i++) {
            String filename = stressDir + "/stress_" + i + ".txt";
            session.getFiles().delete(filename);
        }

        System.out.println("✅ Stress test passed");
    }

    public static void main(String[] args) {
        System.out.println("=== Running Alias Integration Tests ===\n");

        try {
            setUp();

            AliasIntegrationTest test = new AliasIntegrationTest();
            test.testRealWorldScenarioWithAliases();
            test.testChainedAliasOperations();
            test.testAliasCompatibilityWithOriginalMethods();
            test.testMultipleSessionsWithAliases();
            test.testAliasesUnderStress();

            tearDown();

            System.out.println("\n=== All Alias Integration Tests Completed Successfully ===");
        } catch (Exception e) {
            System.err.println("❌ Test failed: " + e.getMessage());
            e.printStackTrace();
        }
    }
}
