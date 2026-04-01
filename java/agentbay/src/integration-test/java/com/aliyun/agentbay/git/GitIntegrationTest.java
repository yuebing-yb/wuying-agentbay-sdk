package com.aliyun.agentbay.git;

import com.aliyun.agentbay.AgentBay;
import com.aliyun.agentbay.exception.AgentBayException;
import com.aliyun.agentbay.model.CommandResult;
import com.aliyun.agentbay.model.SessionResult;
import com.aliyun.agentbay.session.CreateSessionParams;
import com.aliyun.agentbay.session.Session;
import org.junit.AfterClass;
import org.junit.Assume;
import org.junit.BeforeClass;
import org.junit.FixMethodOrder;
import org.junit.Test;
import org.junit.runners.MethodSorters;

import static org.junit.Assert.*;

/**
 * Integration tests for the Git class.
 * Requires a real AgentBay session to execute git commands.
 * Tests are ordered to build on each other (init -> add -> commit -> status -> log -> branch).
 */
@FixMethodOrder(MethodSorters.NAME_ASCENDING)
public class GitIntegrationTest {
    private static AgentBay agentBay;
    private static Session session;
    private static Git git;
    private static final String TEST_REPO_PATH = "/tmp/test-git-repo";

    @BeforeClass
    public static void setUp() throws AgentBayException {
        String apiKey = System.getenv("AGENTBAY_API_KEY");
        Assume.assumeTrue("AGENTBAY_API_KEY not set, skipping Git integration tests",
                apiKey != null && !apiKey.isEmpty());

        agentBay = new AgentBay(apiKey);
        System.out.println("Creating a new session for Git integration testing...");
        CreateSessionParams params = new CreateSessionParams();
        params.setImageId("linux_latest");
        SessionResult result = agentBay.create(params);

        if (!result.isSuccess()) {
            fail("Session creation failed: " + result.getErrorMessage());
        }
        if (result.getSession() == null) {
            fail("Session object is null");
        }

        session = result.getSession();
        git = session.getGit();
        System.out.println("Session created with ID: " + session.getSessionId());

        // Clean up any previous test repo
        session.getCommand().executeCommand("rm -rf " + TEST_REPO_PATH, 5000);
    }

    @AfterClass
    public static void tearDown() {
        System.out.println("Cleaning up: Deleting the session...");
        try {
            // Clean up test repo
            session.getCommand().executeCommand("rm -rf " + TEST_REPO_PATH, 5000);
            agentBay.delete(session, false);
        } catch (Exception e) {
            System.out.println("Warning: Error during cleanup: " + e.getMessage());
        }
    }

    @Test
    public void test01_InitRepo() throws GitError {
        // Test git init
        GitInitResult result = git.init(TEST_REPO_PATH, "main", false, null);
        assertNotNull(result);
        assertEquals(TEST_REPO_PATH, result.getPath());
        System.out.println("test01_InitRepo passed");
    }

    @Test
    public void test02_ConfigureUser() throws GitError {
        // Test configureUser
        git.configureUser(TEST_REPO_PATH, "Test User", "test@example.com");

        // Verify config was set
        String name = git.getConfig(TEST_REPO_PATH, "user.name");
        String email = git.getConfig(TEST_REPO_PATH, "user.email");
        assertEquals("Test User", name);
        assertEquals("test@example.com", email);
        System.out.println("test02_ConfigureUser passed");
    }

    @Test
    public void test03_SetAndGetConfig() throws GitError {
        // Test setConfig and getConfig
        git.setConfig(TEST_REPO_PATH, "core.autocrlf", "false");
        String value = git.getConfig(TEST_REPO_PATH, "core.autocrlf");
        assertEquals("false", value);
        System.out.println("test03_SetAndGetConfig passed");
    }

    @Test
    public void test04_StatusCleanRepo() throws GitError {
        // Test status on a clean repo (no commits yet, but no files either)
        GitStatusResult status = git.status(TEST_REPO_PATH);
        assertNotNull(status);
        // On a fresh init, branch should be main
        assertEquals("main", status.getCurrentBranch());
        System.out.println("test04_StatusCleanRepo passed");
    }

    @Test
    public void test05_AddAndCommit() throws GitError {
        // Create a test file
        session.getCommand().executeCommand(
                "echo 'Hello World' > " + TEST_REPO_PATH + "/test.txt", 5000);

        // Test add
        git.add(TEST_REPO_PATH);

        // Verify file is staged
        GitStatusResult statusBeforeCommit = git.status(TEST_REPO_PATH);
        assertTrue("Should have staged files", statusBeforeCommit.hasStaged());

        // Test commit
        GitCommitResult commitResult = git.commit(TEST_REPO_PATH, "Initial commit");
        assertNotNull(commitResult);
        // Commit hash may or may not be parsed depending on git output format
        System.out.println("Commit hash: " + commitResult.getCommitHash());

        // Verify repo is clean after commit
        GitStatusResult statusAfterCommit = git.status(TEST_REPO_PATH);
        assertTrue("Repo should be clean after commit", statusAfterCommit.isClean());
        System.out.println("test05_AddAndCommit passed");
    }

    @Test
    public void test06_Log() throws GitError {
        // Test log
        GitLogResult logResult = git.log(TEST_REPO_PATH);
        assertNotNull(logResult);
        assertFalse("Log should have at least one entry", logResult.getEntries().isEmpty());

        GitLogEntry firstEntry = logResult.getEntries().get(0);
        assertEquals("Initial commit", firstEntry.getMessage());
        assertEquals("Test User", firstEntry.getAuthorName());
        assertEquals("test@example.com", firstEntry.getAuthorEmail());
        assertNotNull(firstEntry.getHash());
        assertNotNull(firstEntry.getShortHash());
        assertNotNull(firstEntry.getDate());
        System.out.println("test06_Log passed");
    }

    @Test
    public void test07_LogWithMaxCount() throws GitError {
        // Add another commit
        session.getCommand().executeCommand(
                "echo 'Second file' > " + TEST_REPO_PATH + "/test2.txt", 5000);
        git.add(TEST_REPO_PATH);
        git.commit(TEST_REPO_PATH, "Second commit");

        // Test log with maxCount
        GitLogResult logAll = git.log(TEST_REPO_PATH);
        assertEquals(2, logAll.getEntries().size());

        GitLogResult logOne = git.log(TEST_REPO_PATH, 1, null);
        assertEquals(1, logOne.getEntries().size());
        assertEquals("Second commit", logOne.getEntries().get(0).getMessage());
        System.out.println("test07_LogWithMaxCount passed");
    }

    @Test
    public void test08_StatusWithChanges() throws GitError {
        // Create untracked file
        session.getCommand().executeCommand(
                "echo 'untracked' > " + TEST_REPO_PATH + "/untracked.txt", 5000);

        // Modify existing file
        session.getCommand().executeCommand(
                "echo 'modified' >> " + TEST_REPO_PATH + "/test.txt", 5000);

        GitStatusResult status = git.status(TEST_REPO_PATH);
        assertTrue("Should have changes", status.hasChanges());
        assertFalse("Should not be clean", status.isClean());
        assertTrue("Should have untracked files", status.hasUntracked());
        assertTrue("Total count should be > 0", status.getTotalCount() > 0);

        // Clean up: add and commit changes
        git.add(TEST_REPO_PATH);
        git.commit(TEST_REPO_PATH, "Add more files");
        System.out.println("test08_StatusWithChanges passed");
    }

    @Test
    public void test09_BranchOperations() throws GitError {
        // Test create branch (default checkout=true, creates and switches)
        git.createBranch(TEST_REPO_PATH, "feature-branch");

        // Verify current branch changed to feature-branch
        GitStatusResult statusOnFeature = git.status(TEST_REPO_PATH);
        assertEquals("Should be on feature-branch after create", "feature-branch", statusOnFeature.getCurrentBranch());

        // Switch back to main
        git.checkoutBranch(TEST_REPO_PATH, "main");

        // Test list branches
        GitBranchListResult branches = git.listBranches(TEST_REPO_PATH);
        assertNotNull(branches);
        assertTrue("Should have at least 2 branches",
                branches.getBranches().size() >= 2);
        assertEquals("Current branch should be main", "main", branches.getCurrent());

        // Verify feature-branch exists
        boolean featureBranchFound = branches.getBranches().stream()
                .anyMatch(b -> b.getName().equals("feature-branch"));
        assertTrue("feature-branch should exist", featureBranchFound);

        // Test create branch without checkout
        git.createBranch(TEST_REPO_PATH, "no-checkout-branch", false, null);

        // Verify we're still on main
        GitStatusResult statusStillMain = git.status(TEST_REPO_PATH);
        assertEquals("Should still be on main", "main", statusStillMain.getCurrentBranch());

        // Test delete branches
        git.deleteBranch(TEST_REPO_PATH, "feature-branch");
        git.deleteBranch(TEST_REPO_PATH, "no-checkout-branch");

        // Verify branches were deleted
        GitBranchListResult branchesAfterDelete = git.listBranches(TEST_REPO_PATH);
        boolean featureBranchStillExists = branchesAfterDelete.getBranches().stream()
                .anyMatch(b -> b.getName().equals("feature-branch"));
        assertFalse("feature-branch should be deleted", featureBranchStillExists);
        boolean noCheckoutBranchStillExists = branchesAfterDelete.getBranches().stream()
                .anyMatch(b -> b.getName().equals("no-checkout-branch"));
        assertFalse("no-checkout-branch should be deleted", noCheckoutBranchStillExists);
        System.out.println("test09_BranchOperations passed");
    }

    @Test
    public void test10_RemoteOperations() throws GitError {
        // Test remote add
        git.remoteAdd(TEST_REPO_PATH, "origin",
                "https://github.com/example/test-repo.git");

        // Test remote get
        String url = git.remoteGet(TEST_REPO_PATH, "origin");
        assertEquals("https://github.com/example/test-repo.git", url);
        System.out.println("test10_RemoteOperations passed");
    }

    @Test
    public void test11_ResetOperation() throws GitError {
        // Create a file and stage it
        session.getCommand().executeCommand(
                "echo 'reset test' > " + TEST_REPO_PATH + "/reset-test.txt", 5000);
        git.add(TEST_REPO_PATH);

        // Verify file is staged
        GitStatusResult statusBefore = git.status(TEST_REPO_PATH);
        assertTrue("Should have staged files", statusBefore.hasStaged());

        // Test reset (unstage)
        git.reset(TEST_REPO_PATH);

        // Verify file is no longer staged (but still untracked)
        GitStatusResult statusAfter = git.status(TEST_REPO_PATH);
        assertTrue("Should have untracked files", statusAfter.hasUntracked());

        // Clean up
        session.getCommand().executeCommand(
                "rm -f " + TEST_REPO_PATH + "/reset-test.txt", 5000);
        System.out.println("test11_ResetOperation passed");
    }

    @Test
    public void test12_ClonePublicRepo() throws GitError {
        String clonePath = "/tmp/test-clone-repo";
        // Clean up any previous clone
        session.getCommand().executeCommand("rm -rf " + clonePath, 5000);

        try {
            // Clone a small public repo with depth 1
            GitCloneResult result = git.clone(
                    "https://github.com/octocat/Hello-World.git",
                    clonePath, null, 1, null);
            assertNotNull(result);
            assertEquals(clonePath, result.getPath());

            // Verify the clone by checking status
            GitStatusResult status = git.status(clonePath);
            assertNotNull(status);
            assertNotNull(status.getCurrentBranch());
            System.out.println("test12_ClonePublicRepo passed");
        } finally {
            // Clean up
            session.getCommand().executeCommand("rm -rf " + clonePath, 10000);
        }
    }

    @Test
    public void test13_CommitWithAuthor() throws GitError {
        // Create a file
        session.getCommand().executeCommand(
                "echo 'author test' > " + TEST_REPO_PATH + "/author-test.txt", 5000);
        git.add(TEST_REPO_PATH);

        // Commit with custom author
        GitCommitResult result = git.commit(TEST_REPO_PATH, "Commit with author",
                "Custom Author", "custom@example.com", false, null);
        assertNotNull(result);

        // Verify author in log
        GitLogResult log = git.log(TEST_REPO_PATH, 1, null);
        assertEquals("Custom Author", log.getEntries().get(0).getAuthorName());
        assertEquals("custom@example.com", log.getEntries().get(0).getAuthorEmail());
        System.out.println("test13_CommitWithAuthor passed");
    }

    @Test
    public void test14_AllowEmptyCommit() throws GitError {
        // Test allow-empty commit
        GitCommitResult result = git.commit(TEST_REPO_PATH, "Empty commit",
                null, null, true, null);
        assertNotNull(result);

        // Verify in log
        GitLogResult log = git.log(TEST_REPO_PATH, 1, null);
        assertEquals("Empty commit", log.getEntries().get(0).getMessage());
        System.out.println("test14_AllowEmptyCommit passed");
    }

    @Test
    public void test15_RestoreOperation() throws GitError {
        // Create and stage a file
        session.getCommand().executeCommand(
                "echo 'restore test' > " + TEST_REPO_PATH + "/restore-test.txt", 5000);
        git.add(TEST_REPO_PATH);
        git.commit(TEST_REPO_PATH, "Add restore test file");

        // Modify the file
        session.getCommand().executeCommand(
                "echo 'modified content' > " + TEST_REPO_PATH + "/restore-test.txt", 5000);

        // Verify file is modified
        GitStatusResult statusBefore = git.status(TEST_REPO_PATH);
        assertTrue("Should have changes", statusBefore.hasChanges());

        // Test restore (discard worktree changes)
        git.restore(TEST_REPO_PATH, java.util.Arrays.asList("restore-test.txt"));

        // Verify file is restored
        GitStatusResult statusAfter = git.status(TEST_REPO_PATH);
        assertTrue("Repo should be clean after restore", statusAfter.isClean());
        System.out.println("test15_RestoreOperation passed");
    }

    @Test
    public void test16_ErrorHandlingNotARepo() {
        // Test status on a non-git directory
        try {
            git.status("/tmp");
            fail("Expected GitNotARepoError");
        } catch (GitNotARepoError e) {
            // Expected
            assertNotNull(e.getMessage());
            assertTrue(e.getMessage().contains("not a git repository"));
            System.out.println("test16_ErrorHandlingNotARepo passed");
        } catch (GitError e) {
            // Some environments may return generic GitError
            assertNotNull(e.getMessage());
            System.out.println("test16_ErrorHandlingNotARepo passed (generic GitError)");
        }
    }

    @Test
    public void test17_RestoreEmptyPathsValidation() {
        // Test restore with empty paths - should fail with validation error
        try {
            git.restore(TEST_REPO_PATH, java.util.Collections.emptyList());
            fail("Expected GitError for empty paths");
        } catch (GitError e) {
            assertTrue(e.getMessage().contains("requires at least one path"));
            System.out.println("test17_RestoreEmptyPathsValidation passed");
        }
    }
}
