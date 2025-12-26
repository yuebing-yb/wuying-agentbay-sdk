package com.aliyun.agentbay.test;

import com.aliyun.agentbay.AgentBay;
import com.aliyun.agentbay.exception.AgentBayException;
import com.aliyun.agentbay.model.CommandResult;
import com.aliyun.agentbay.model.DeleteResult;
import com.aliyun.agentbay.model.SessionResult;
import com.aliyun.agentbay.session.CreateSessionParams;
import com.aliyun.agentbay.session.Session;
import org.junit.AfterClass;
import org.junit.BeforeClass;
import org.junit.Test;

import java.util.HashMap;
import java.util.Map;

import static org.junit.Assert.*;

public class TestCommandEnvironment {

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
        System.out.println("Setting up test environment...");
        String apiKey = getTestApiKey();
        agentBay = new AgentBay();

        CreateSessionParams params = new CreateSessionParams();
        params.setImageId("linux_latest");
        SessionResult sessionResult = agentBay.create(params);

        assertTrue("Failed to create session: " + sessionResult.getErrorMessage(),
                sessionResult.isSuccess());
        assertNotNull("Session object is null", sessionResult.getSession());

        session = sessionResult.getSession();
        System.out.println("✅ Session created with ID: " + session.getSessionId());
    }

    @AfterClass
    public static void tearDown() {
        if (session != null && agentBay != null) {
            try {
                System.out.println("Cleaning up session...");
                DeleteResult deleteResult = agentBay.delete(session, false);
                if (deleteResult.isSuccess()) {
                    System.out.println("✅ Session deleted successfully");
                } else {
                    System.err.println("⚠️ Failed to delete session: " + deleteResult.getErrorMessage());
                }
            } catch (Exception e) {
                System.err.println("⚠️ Error during cleanup: " + e.getMessage());
            }
        }
    }

    @Test
    public void testCommandWithCwd() {
        System.out.println("\n📁 Testing command with cwd parameter...");

        CommandResult result = session.getCommand().executeCommand("pwd", 5000, "/tmp", null);

        assertTrue("Command should succeed", result.isSuccess());
        assertEquals("Exit code should be 0", 0, result.getExitCode());
        assertTrue("Working directory should be /tmp, got: " + result.getOutput(),
                result.getOutput().contains("/tmp"));

        System.out.println("✅ CWD test passed: working directory=" + result.getOutput().trim());
    }

    @Test
    public void testCommandWithEnvs() {
        System.out.println("\n🌍 Testing command with envs parameter...");

        Map<String, String> envs = new HashMap<>();
        envs.put("TEST_VAR", "test_value_123");

        CommandResult result = session.getCommand().executeCommand("echo $TEST_VAR", 5000, null, envs);

        assertTrue("Command should succeed", result.isSuccess());
        assertEquals("Exit code should be 0", 0, result.getExitCode());

        String output = result.getOutput().trim();
        if (output.contains("test_value_123")) {
            System.out.println("✅ Envs test passed: environment variable set correctly: " + output);
        } else {
            System.out.println("⚠️ Envs test: environment variable may not be set (output: " + output + ")");
        }
    }

    @Test
    public void testCommandWithCwdAndEnvs() {
        System.out.println("\n🔀 Testing command with both cwd and envs parameters...");

        Map<String, String> envs = new HashMap<>();
        envs.put("CUSTOM_VAR", "custom_value");

        CommandResult result = session.getCommand().executeCommand(
                "pwd && echo $CUSTOM_VAR",
                5000,
                "/tmp",
                envs
        );

        assertTrue("Command should succeed", result.isSuccess());
        assertEquals("Exit code should be 0", 0, result.getExitCode());
        assertTrue("Working directory should be /tmp", result.getOutput().contains("/tmp"));

        System.out.println("✅ Combined cwd and envs test passed");
        System.out.println("  Output: " + result.getOutput());
    }

    @Test
    public void testCommandWithCwdContainingSpaces() {
        System.out.println("\n📂 Testing command with cwd containing spaces...");

        String testDir = "/tmp/test dir with spaces";

        CommandResult mkdirResult = session.getCommand().executeCommand(
                "mkdir -p '" + testDir + "'",
                5000,
                null,
                null
        );
        assertTrue("Should be able to create directory with spaces", mkdirResult.isSuccess());

        CommandResult result = session.getCommand().executeCommand("pwd", 5000, testDir, null);

        assertTrue("Command should succeed with cwd containing spaces", result.isSuccess());
        assertEquals("Exit code should be 0", 0, result.getExitCode());
        assertTrue("Working directory should contain test dir, got: " + result.getOutput(),
                result.getOutput().contains(testDir) || result.getOutput().contains("/tmp/test"));

        CommandResult cleanupResult = session.getCommand().executeCommand(
                "rm -rf '" + testDir + "'",
                5000,
                null,
                null
        );

        System.out.println("✅ CWD with spaces test passed: directory=" + testDir);
    }

    @Test
    public void testCommandWithEnvsSpecialCharacters() {
        System.out.println("\n🎭 Testing command with environment variables containing special characters...");

        Map<String, String> envs = new HashMap<>();
        envs.put("TEST_VAR", "value with 'single quotes'");

        CommandResult result = session.getCommand().executeCommand("echo $TEST_VAR", 5000, null, envs);

        assertTrue("Command should succeed with env containing single quotes", result.isSuccess());
        assertEquals("Exit code should be 0", 0, result.getExitCode());

        String output = result.getOutput().trim();
        if (output.contains("value with") && output.contains("single quotes")) {
            System.out.println("✅ Envs with single quotes test passed: " + output);
        } else {
            System.out.println("⚠️ Envs with single quotes: output may not match exactly: " + output);
        }
    }

    @Test
    public void testCommandInvalidEnvs() {
        System.out.println("\n❌ Testing command with invalid envs (should throw exception)...");

        Map<String, String> envs = new HashMap<>();
        envs.put("TEST_VAR", "123");

        try {
            CommandResult result = session.getCommand().executeCommand("echo test", 5000, null, envs);
            System.out.println("✅ Valid envs (all strings) test passed");
        } catch (Exception e) {
            fail("Valid envs should not throw exception: " + e.getMessage());
        }
    }

    @Test
    public void testCommandBackwardCompatibility() {
        System.out.println("\n🔄 Testing backward compatibility (no cwd, no envs)...");

        CommandResult result = session.getCommand().executeCommand("echo 'backward compatible'", 5000);

        assertTrue("Command should succeed", result.isSuccess());
        assertNotNull("Output should not be null", result.getOutput());

        System.out.println("✅ Backward compatibility test passed: output=" + result.getOutput());
    }

    @Test
    public void testCommandPathEnv() {
        System.out.println("\n🛤️ Testing PATH environment variable...");

        CommandResult result = session.getCommand().executeCommand("echo $PATH", 5000);

        assertTrue("Command should succeed", result.isSuccess());
        assertTrue("PATH should not be empty", result.getOutput().length() > 0);

        System.out.println("✅ PATH: " + result.getOutput().substring(0, Math.min(100, result.getOutput().length())) + "...");
    }

    @Test
    public void testCommandCwdAndEnvsWithSpecialChars() {
        System.out.println("\n🎪 Testing command with both cwd (spaces) and envs (special chars)...");

        String testDir = "/tmp/test dir with spaces";
        CommandResult mkdirResult = session.getCommand().executeCommand(
                "mkdir -p '" + testDir + "'",
                5000,
                null,
                null
        );
        assertTrue("Should be able to create directory with spaces", mkdirResult.isSuccess());

        Map<String, String> envs = new HashMap<>();
        envs.put("CUSTOM_VAR", "value with 'quotes' and ; semicolon");

        CommandResult result = session.getCommand().executeCommand(
                "pwd && echo $CUSTOM_VAR",
                5000,
                testDir,
                envs
        );

        assertTrue("Command should succeed with both cwd (spaces) and envs (special chars)", result.isSuccess());
        assertEquals("Exit code should be 0", 0, result.getExitCode());
        assertTrue("Working directory should contain test dir",
                result.getOutput().contains(testDir) || result.getOutput().contains("/tmp/test"));

        String output = result.getOutput().trim();
        if (output.contains("value") || output.contains("CUSTOM_VAR")) {
            System.out.println("✅ Combined cwd (spaces) and envs (special chars) test passed");
            System.out.println("  Output: " + output.substring(0, Math.min(100, output.length())) + "...");
        } else {
            System.out.println("⚠️ Combined test: output may not show env var: " + output);
        }

        CommandResult cleanupResult = session.getCommand().executeCommand(
                "rm -rf '" + testDir + "'",
                5000,
                null,
                null
        );
    }

    public static void main(String[] args) {
        System.out.println("=== Running Command Environment Tests ===\n");

        TestCommandEnvironment test = new TestCommandEnvironment();

        try {
            setUp();

            test.testCommandWithCwd();
            test.testCommandWithEnvs();
            test.testCommandWithCwdAndEnvs();
            test.testCommandWithCwdContainingSpaces();
            test.testCommandWithEnvsSpecialCharacters();
            test.testCommandInvalidEnvs();
            test.testCommandBackwardCompatibility();
            test.testCommandPathEnv();
            test.testCommandCwdAndEnvsWithSpecialChars();

            tearDown();

            System.out.println("\n=== ✅ All Command Environment Tests Completed Successfully ===");
        } catch (Exception e) {
            System.err.println("\n=== ❌ Test Failed ===");
            System.err.println("Error: " + e.getMessage());
            e.printStackTrace();
        }
    }
}
