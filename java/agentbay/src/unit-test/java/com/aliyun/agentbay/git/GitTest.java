package com.aliyun.agentbay.git;

import com.aliyun.agentbay.command.Command;
import com.aliyun.agentbay.model.CommandResult;
import com.aliyun.agentbay.session.Session;
import org.junit.Before;
import org.junit.Test;

import java.lang.reflect.Field;
import java.lang.reflect.Method;
import java.util.Arrays;
import java.util.Collections;
import java.util.List;

import static org.junit.Assert.*;
import static org.mockito.Mockito.*;
import static org.mockito.ArgumentMatchers.*;

/**
 * Unit tests for the Git class.
 * Tests private helper/parsing methods via reflection.
 */
public class GitTest {
    private Git git;
    private Session mockSession;

    @Before
    public void setUp() {
        mockSession = mock(Session.class);
        git = new Git(mockSession);
    }

    // ==================== Helper: invoke private methods via reflection ====================

    private Object invokePrivate(String methodName, Class<?>[] paramTypes, Object... args) throws Exception {
        Method method = Git.class.getDeclaredMethod(methodName, paramTypes);
        method.setAccessible(true);
        return method.invoke(git, args);
    }

    // ==================== shellEscape Tests ====================

    @Test
    public void testShellEscapeNormal() throws Exception {
        String result = (String) invokePrivate("shellEscape",
                new Class[]{String.class}, "hello");
        assertEquals("'hello'", result);
    }

    @Test
    public void testShellEscapeWithSingleQuote() throws Exception {
        String result = (String) invokePrivate("shellEscape",
                new Class[]{String.class}, "it's");
        assertEquals("'it'\\''s'", result);
    }

    @Test
    public void testShellEscapeNull() throws Exception {
        String result = (String) invokePrivate("shellEscape",
                new Class[]{String.class}, (Object) null);
        assertEquals("''", result);
    }

    @Test
    public void testShellEscapeEmpty() throws Exception {
        String result = (String) invokePrivate("shellEscape",
                new Class[]{String.class}, "");
        assertEquals("''", result);
    }

    // ==================== buildGitCommand Tests ====================

    @Test
    public void testBuildGitCommandWithoutRepoPath() throws Exception {
        List<String> args = Arrays.asList("status", "--porcelain");
        String result = (String) invokePrivate("buildGitCommand",
                new Class[]{List.class, String.class}, args, null);
        assertEquals("git 'status' '--porcelain'", result);
    }

    @Test
    public void testBuildGitCommandWithRepoPath() throws Exception {
        List<String> args = Arrays.asList("status", "--porcelain");
        String result = (String) invokePrivate("buildGitCommand",
                new Class[]{List.class, String.class}, args, "/tmp/repo");
        assertEquals("git -C '/tmp/repo' 'status' '--porcelain'", result);
    }

    @Test
    public void testBuildGitCommandWithEmptyRepoPath() throws Exception {
        List<String> args = Arrays.asList("log");
        String result = (String) invokePrivate("buildGitCommand",
                new Class[]{List.class, String.class}, args, "");
        assertEquals("git 'log'", result);
    }

    @Test
    public void testBuildGitCommandWithSpecialCharsInRepoPath() throws Exception {
        List<String> args = Arrays.asList("status");
        String result = (String) invokePrivate("buildGitCommand",
                new Class[]{List.class, String.class}, args, "/tmp/my repo");
        assertEquals("git -C '/tmp/my repo' 'status'", result);
    }

    // ==================== deriveRepoDirFromUrl Tests ====================

    @Test
    public void testDeriveRepoDirFromUrlWithGitSuffix() throws Exception {
        String result = (String) invokePrivate("deriveRepoDirFromUrl",
                new Class[]{String.class}, "https://github.com/user/repo.git");
        assertEquals("repo", result);
    }

    @Test
    public void testDeriveRepoDirFromUrlWithoutGitSuffix() throws Exception {
        String result = (String) invokePrivate("deriveRepoDirFromUrl",
                new Class[]{String.class}, "https://github.com/user/repo");
        assertEquals("repo", result);
    }

    @Test
    public void testDeriveRepoDirFromUrlSimpleName() throws Exception {
        String result = (String) invokePrivate("deriveRepoDirFromUrl",
                new Class[]{String.class}, "my-project.git");
        assertEquals("my-project", result);
    }

    @Test
    public void testDeriveRepoDirFromUrlDeepPath() throws Exception {
        String result = (String) invokePrivate("deriveRepoDirFromUrl",
                new Class[]{String.class}, "https://gitlab.com/org/sub/deep/repo.git");
        assertEquals("repo", result);
    }

    // ==================== deriveStatus Tests ====================

    @Test
    public void testDeriveStatusConflict() throws Exception {
        String result = (String) invokePrivate("deriveStatus",
                new Class[]{String.class, String.class}, "U", "U");
        assertEquals("conflict", result);
    }

    @Test
    public void testDeriveStatusRenamed() throws Exception {
        String result = (String) invokePrivate("deriveStatus",
                new Class[]{String.class, String.class}, "R", " ");
        assertEquals("renamed", result);
    }

    @Test
    public void testDeriveStatusCopied() throws Exception {
        String result = (String) invokePrivate("deriveStatus",
                new Class[]{String.class, String.class}, "C", " ");
        assertEquals("copied", result);
    }

    @Test
    public void testDeriveStatusDeleted() throws Exception {
        String result = (String) invokePrivate("deriveStatus",
                new Class[]{String.class, String.class}, "D", " ");
        assertEquals("deleted", result);
    }

    @Test
    public void testDeriveStatusAdded() throws Exception {
        String result = (String) invokePrivate("deriveStatus",
                new Class[]{String.class, String.class}, "A", " ");
        assertEquals("added", result);
    }

    @Test
    public void testDeriveStatusModified() throws Exception {
        String result = (String) invokePrivate("deriveStatus",
                new Class[]{String.class, String.class}, "M", " ");
        assertEquals("modified", result);
    }

    @Test
    public void testDeriveStatusModifiedWorkTree() throws Exception {
        String result = (String) invokePrivate("deriveStatus",
                new Class[]{String.class, String.class}, " ", "M");
        assertEquals("modified", result);
    }

    @Test
    public void testDeriveStatusTypechange() throws Exception {
        String result = (String) invokePrivate("deriveStatus",
                new Class[]{String.class, String.class}, "T", " ");
        assertEquals("typechange", result);
    }

    @Test
    public void testDeriveStatusUntracked() throws Exception {
        String result = (String) invokePrivate("deriveStatus",
                new Class[]{String.class, String.class}, "?", "?");
        assertEquals("untracked", result);
    }

    @Test
    public void testDeriveStatusUnknown() throws Exception {
        String result = (String) invokePrivate("deriveStatus",
                new Class[]{String.class, String.class}, " ", " ");
        assertEquals("unknown", result);
    }

    @Test
    public void testDeriveStatusNullInputs() throws Exception {
        String result = (String) invokePrivate("deriveStatus",
                new Class[]{String.class, String.class}, null, null);
        assertEquals("unknown", result);
    }

    @Test
    public void testDeriveStatusConflictPriority() throws Exception {
        // U should take priority over other statuses
        String result = (String) invokePrivate("deriveStatus",
                new Class[]{String.class, String.class}, "U", "M");
        assertEquals("conflict", result);
    }

    // ==================== parseGitStatus Tests ====================

    @Test
    public void testParseGitStatusSimpleBranch() throws Exception {
        String output = "## main\n";
        GitStatusResult result = (GitStatusResult) invokePrivate("parseGitStatus",
                new Class[]{String.class}, output);
        assertEquals("main", result.getCurrentBranch());
        assertNull(result.getUpstream());
        assertEquals(0, result.getAhead());
        assertEquals(0, result.getBehind());
        assertFalse(result.isDetached());
        assertTrue(result.getFiles().isEmpty());
        assertTrue(result.isClean());
    }

    @Test
    public void testParseGitStatusWithUpstream() throws Exception {
        String output = "## main...origin/main\n";
        GitStatusResult result = (GitStatusResult) invokePrivate("parseGitStatus",
                new Class[]{String.class}, output);
        assertEquals("main", result.getCurrentBranch());
        assertEquals("origin/main", result.getUpstream());
        assertEquals(0, result.getAhead());
        assertEquals(0, result.getBehind());
    }

    @Test
    public void testParseGitStatusWithAheadBehind() throws Exception {
        String output = "## main...origin/main [ahead 3, behind 2]\n";
        GitStatusResult result = (GitStatusResult) invokePrivate("parseGitStatus",
                new Class[]{String.class}, output);
        assertEquals("main", result.getCurrentBranch());
        assertEquals("origin/main", result.getUpstream());
        assertEquals(3, result.getAhead());
        assertEquals(2, result.getBehind());
    }

    @Test
    public void testParseGitStatusAheadOnly() throws Exception {
        String output = "## feature...origin/feature [ahead 5]\n";
        GitStatusResult result = (GitStatusResult) invokePrivate("parseGitStatus",
                new Class[]{String.class}, output);
        assertEquals("feature", result.getCurrentBranch());
        assertEquals(5, result.getAhead());
        assertEquals(0, result.getBehind());
    }

    @Test
    public void testParseGitStatusBehindOnly() throws Exception {
        String output = "## feature...origin/feature [behind 7]\n";
        GitStatusResult result = (GitStatusResult) invokePrivate("parseGitStatus",
                new Class[]{String.class}, output);
        assertEquals("feature", result.getCurrentBranch());
        assertEquals(0, result.getAhead());
        assertEquals(7, result.getBehind());
    }

    @Test
    public void testParseGitStatusDetachedHead() throws Exception {
        String output = "## HEAD (no branch)\n";
        GitStatusResult result = (GitStatusResult) invokePrivate("parseGitStatus",
                new Class[]{String.class}, output);
        assertTrue(result.isDetached());
    }

    @Test
    public void testParseGitStatusWithFiles() throws Exception {
        // Porcelain format preserves positional XY status indicators
        String output = "## main\nMM file1.txt\nA  file2.txt\n?? file3.txt\n M file4.txt\n";
        GitStatusResult result = (GitStatusResult) invokePrivate("parseGitStatus",
                new Class[]{String.class}, output);
        assertEquals("main", result.getCurrentBranch());
        assertEquals(4, result.getFiles().size());

        // file1.txt: modified in both index and work tree
        GitFileStatus f1 = result.getFiles().get(0);
        assertEquals("file1.txt", f1.getPath());
        assertEquals("modified", f1.getStatus());
        assertEquals("M", f1.getIndexStatus());
        assertEquals("M", f1.getWorkTreeStatus());
        assertTrue("MM should be staged", f1.isStaged());

        // file2.txt: added to index
        GitFileStatus f2 = result.getFiles().get(1);
        assertEquals("file2.txt", f2.getPath());
        assertEquals("added", f2.getStatus());
        assertTrue(f2.isStaged());

        // file3.txt: untracked
        GitFileStatus f3 = result.getFiles().get(2);
        assertEquals("file3.txt", f3.getPath());
        assertEquals("untracked", f3.getStatus());
        assertFalse(f3.isStaged());

        // file4.txt: modified only in worktree (not staged)
        GitFileStatus f4 = result.getFiles().get(3);
        assertEquals("file4.txt", f4.getPath());
        assertEquals("modified", f4.getStatus());
        assertEquals(" ", f4.getIndexStatus());
        assertEquals("M", f4.getWorkTreeStatus());
        assertFalse("Worktree-only modification should NOT be staged", f4.isStaged());
    }

    @Test
    public void testParseGitStatusWithRenamedFile() throws Exception {
        String output = "## main\nR  old.txt -> new.txt\n";
        GitStatusResult result = (GitStatusResult) invokePrivate("parseGitStatus",
                new Class[]{String.class}, output);
        assertEquals(1, result.getFiles().size());
        GitFileStatus f = result.getFiles().get(0);
        assertEquals("new.txt", f.getPath());
        assertEquals("renamed", f.getStatus());
        assertEquals("old.txt", f.getRenamedFrom());
        assertTrue(f.isStaged());
    }

    @Test
    public void testParseGitStatusComputedProperties() throws Exception {
        // Full porcelain format test with all file status types
        String output = "## main\nA  staged.txt\n M unstaged.txt\n?? untracked.txt\nUU conflict.txt\n";
        GitStatusResult result = (GitStatusResult) invokePrivate("parseGitStatus",
                new Class[]{String.class}, output);
        assertTrue(result.hasChanges());
        assertFalse(result.isClean());
        assertTrue(result.hasStaged());
        assertTrue(result.hasUntracked());
        assertTrue(result.hasConflicts());
        assertEquals(4, result.getTotalCount());
        // A (staged), UU (staged because U != ' ') = 2 staged; ' M' is NOT staged
        assertEquals(2, result.getStagedCount());
        assertEquals(1, result.getUntrackedCount());
        assertEquals(1, result.getConflictCount());
    }

    @Test
    public void testParseGitStatusNoCommitsYet() throws Exception {
        String output = "## No commits yet on main\n";
        GitStatusResult result = (GitStatusResult) invokePrivate("parseGitStatus",
                new Class[]{String.class}, output);
        assertEquals("main", result.getCurrentBranch());
        assertFalse(result.isDetached());
        assertTrue(result.isClean());
    }

    @Test
    public void testParseGitStatusNoCommitsYetWithFiles() throws Exception {
        String output = "## No commits yet on develop\nA  newfile.txt\n";
        GitStatusResult result = (GitStatusResult) invokePrivate("parseGitStatus",
                new Class[]{String.class}, output);
        assertEquals("develop", result.getCurrentBranch());
        assertEquals(1, result.getFiles().size());
        assertTrue(result.hasStaged());
    }

    @Test
    public void testParseGitStatusInitialCommitOn() throws Exception {
        // Older git versions use "Initial commit on" instead of "No commits yet on"
        String output = "## Initial commit on main\n";
        GitStatusResult result = (GitStatusResult) invokePrivate("parseGitStatus",
                new Class[]{String.class}, output);
        assertEquals("main", result.getCurrentBranch());
    }

    @Test
    public void testParseGitStatusWorktreeOnlyDeletion() throws Exception {
        // " D file.txt" = deleted in worktree but not staged
        String output = "## main\n D deleted.txt\n";
        GitStatusResult result = (GitStatusResult) invokePrivate("parseGitStatus",
                new Class[]{String.class}, output);
        assertEquals(1, result.getFiles().size());
        GitFileStatus f = result.getFiles().get(0);
        assertEquals("deleted", f.getStatus());
        assertEquals(" ", f.getIndexStatus());
        assertEquals("D", f.getWorkTreeStatus());
        assertFalse("Worktree-only deletion should NOT be staged", f.isStaged());
    }

    // ==================== parseGitLog Tests ====================

    @Test
    public void testParseGitLogSingleEntry() throws Exception {
        String output = "abc123def456\u0001abc123d\u0001John Doe\u0001john@example.com\u00012024-01-15T10:30:00+08:00\u0001Initial commit\u0000";
        GitLogResult result = (GitLogResult) invokePrivate("parseGitLog",
                new Class[]{String.class}, output);
        assertEquals(1, result.getEntries().size());
        GitLogEntry entry = result.getEntries().get(0);
        assertEquals("abc123def456", entry.getHash());
        assertEquals("abc123d", entry.getShortHash());
        assertEquals("John Doe", entry.getAuthorName());
        assertEquals("john@example.com", entry.getAuthorEmail());
        assertEquals("2024-01-15T10:30:00+08:00", entry.getDate());
        assertEquals("Initial commit", entry.getMessage());
    }

    @Test
    public void testParseGitLogMultipleEntries() throws Exception {
        String output = "hash1\u0001h1\u0001Alice\u0001alice@test.com\u00012024-01-15\u0001First\u0000"
                + "hash2\u0001h2\u0001Bob\u0001bob@test.com\u00012024-01-16\u0001Second\u0000";
        GitLogResult result = (GitLogResult) invokePrivate("parseGitLog",
                new Class[]{String.class}, output);
        assertEquals(2, result.getEntries().size());
        assertEquals("Alice", result.getEntries().get(0).getAuthorName());
        assertEquals("Bob", result.getEntries().get(1).getAuthorName());
    }

    @Test
    public void testParseGitLogEmptyOutput() throws Exception {
        String output = "";
        GitLogResult result = (GitLogResult) invokePrivate("parseGitLog",
                new Class[]{String.class}, output);
        assertTrue(result.getEntries().isEmpty());
    }

    @Test
    public void testParseGitLogMalformedEntry() throws Exception {
        // Less than 6 fields - should be skipped
        String output = "hash1\u0001h1\u0001Alice\u0000";
        GitLogResult result = (GitLogResult) invokePrivate("parseGitLog",
                new Class[]{String.class}, output);
        assertTrue(result.getEntries().isEmpty());
    }

    // ==================== parseGitBranches Tests ====================

    @Test
    public void testParseGitBranchesFormatOutput() throws Exception {
        // --format=%(refname:short)\t%(HEAD) output format
        String output = "main\t*\ndevelop\t \nfeature/login\t \n";
        GitBranchListResult result = (GitBranchListResult) invokePrivate("parseGitBranches",
                new Class[]{String.class}, output);
        assertEquals(3, result.getBranches().size());
        assertEquals("main", result.getCurrent());

        assertTrue(result.getBranches().get(0).isCurrent());
        assertEquals("main", result.getBranches().get(0).getName());
        assertFalse(result.getBranches().get(1).isCurrent());
        assertEquals("develop", result.getBranches().get(1).getName());
        assertFalse(result.getBranches().get(2).isCurrent());
        assertEquals("feature/login", result.getBranches().get(2).getName());
    }

    @Test
    public void testParseGitBranchesFormatNoCurrent() throws Exception {
        // All branches have space (not current)
        String output = "main\t \ndevelop\t \n";
        GitBranchListResult result = (GitBranchListResult) invokePrivate("parseGitBranches",
                new Class[]{String.class}, output);
        assertEquals(2, result.getBranches().size());
        assertNull(result.getCurrent());
    }

    @Test
    public void testParseGitBranchesFallbackLegacyFormat() throws Exception {
        // Fallback: legacy format without tab separator
        String output = "* main\n  develop\n  feature/login\n";
        GitBranchListResult result = (GitBranchListResult) invokePrivate("parseGitBranches",
                new Class[]{String.class}, output);
        assertEquals(3, result.getBranches().size());
        assertEquals("main", result.getCurrent());
    }

    @Test
    public void testParseGitBranchesDetachedHead() throws Exception {
        // Legacy fallback format with detached HEAD
        String output = "* (HEAD detached at abc1234)\n  main\n  develop\n";
        GitBranchListResult result = (GitBranchListResult) invokePrivate("parseGitBranches",
                new Class[]{String.class}, output);
        assertEquals(2, result.getBranches().size());
        assertNull(result.getCurrent());
        assertEquals("main", result.getBranches().get(0).getName());
        assertEquals("develop", result.getBranches().get(1).getName());
    }

    @Test
    public void testParseGitBranchesNoBranch() throws Exception {
        String output = "* (no branch)\n  main\n";
        GitBranchListResult result = (GitBranchListResult) invokePrivate("parseGitBranches",
                new Class[]{String.class}, output);
        assertEquals(1, result.getBranches().size());
        assertNull(result.getCurrent());
        assertEquals("main", result.getBranches().get(0).getName());
    }

    @Test
    public void testParseGitBranchesEmptyOutput() throws Exception {
        String output = "";
        GitBranchListResult result = (GitBranchListResult) invokePrivate("parseGitBranches",
                new Class[]{String.class}, output);
        assertTrue(result.getBranches().isEmpty());
        assertNull(result.getCurrent());
    }

    // ==================== classifyError Tests ====================
    // classifyError reads result.getStdout() and result.getStderr(), so we use the 8-arg constructor
    // CommandResult(requestId, success, output, errorMessage, exitCode, stdout, stderr, traceId)

    @Test
    public void testClassifyErrorAuthentication() throws Exception {
        CommandResult cmdResult = new CommandResult("", false, "", "", 1, "", "authentication failed", "");
        GitError error = (GitError) invokePrivate("classifyError",
                new Class[]{String.class, CommandResult.class}, "clone", cmdResult);
        assertTrue(error instanceof GitAuthError);
        assertTrue(error.getMessage().contains("authentication error"));
    }

    @Test
    public void testClassifyErrorPermissionDenied() throws Exception {
        CommandResult cmdResult = new CommandResult("", false, "", "", 1, "", "Permission denied (publickey)", "");
        GitError error = (GitError) invokePrivate("classifyError",
                new Class[]{String.class, CommandResult.class}, "push", cmdResult);
        assertTrue(error instanceof GitAuthError);
    }

    @Test
    public void testClassifyErrorNotARepo() throws Exception {
        CommandResult cmdResult = new CommandResult("", false, "", "", 128, "", "fatal: not a git repository", "");
        GitError error = (GitError) invokePrivate("classifyError",
                new Class[]{String.class, CommandResult.class}, "status", cmdResult);
        assertTrue(error instanceof GitNotARepoError);
    }

    @Test
    public void testClassifyErrorDoesNotAppearToBeRepo() throws Exception {
        CommandResult cmdResult = new CommandResult("", false, "", "", 128, "", "does not appear to be a git repository", "");
        GitError error = (GitError) invokePrivate("classifyError",
                new Class[]{String.class, CommandResult.class}, "push", cmdResult);
        assertTrue(error instanceof GitNotARepoError);
    }

    @Test
    public void testClassifyErrorConflict() throws Exception {
        // conflict in stdout
        CommandResult cmdResult = new CommandResult("", false, "", "", 1, "conflict detected", "", "");
        GitError error = (GitError) invokePrivate("classifyError",
                new Class[]{String.class, CommandResult.class}, "merge", cmdResult);
        assertTrue(error instanceof GitConflictError);
    }

    @Test
    public void testClassifyErrorCommandNotFound() throws Exception {
        CommandResult cmdResult = new CommandResult("", false, "", "", 127, "", "git: command not found", "");
        GitError error = (GitError) invokePrivate("classifyError",
                new Class[]{String.class, CommandResult.class}, "status", cmdResult);
        assertTrue(error instanceof GitNotFoundError);
    }

    @Test
    public void testClassifyErrorGeneric() throws Exception {
        CommandResult cmdResult = new CommandResult("", false, "", "", 1, "", "some unknown error", "");
        GitError error = (GitError) invokePrivate("classifyError",
                new Class[]{String.class, CommandResult.class}, "push", cmdResult);
        assertTrue(error instanceof GitError);
        assertFalse(error instanceof GitAuthError);
        assertFalse(error instanceof GitNotARepoError);
        assertFalse(error instanceof GitConflictError);
        assertFalse(error instanceof GitNotFoundError);
    }

    @Test
    public void testClassifyErrorNullStderr() throws Exception {
        // classifyError should handle null stdout/stderr gracefully
        CommandResult cmdResult = new CommandResult("", false, "", "", 1, null, null, "");
        GitError error = (GitError) invokePrivate("classifyError",
                new Class[]{String.class, CommandResult.class}, "push", cmdResult);
        assertNotNull(error);
        assertTrue(error instanceof GitError);
    }

    // ==================== ensureGitAvailable Tests ====================

    private void resetGitAvailable() throws Exception {
        Field field = Git.class.getDeclaredField("gitAvailable");
        field.setAccessible(true);
        field.set(git, null);
    }

    @Test
    public void testEnsureGitAvailableSuccess() throws Exception {
        Command mockCommand = mock(Command.class);
        when(mockSession.getCommand()).thenReturn(mockCommand);
        when(mockCommand.executeCommand(anyString(), anyInt(), any(), anyMap()))
                .thenReturn(new CommandResult("", true, "", "", 0, "git version 2.40.0", "", ""));

        resetGitAvailable();
        // Should not throw
        Method method = Git.class.getDeclaredMethod("ensureGitAvailable");
        method.setAccessible(true);
        method.invoke(git);

        // Verify gitAvailable is cached as true
        Field field = Git.class.getDeclaredField("gitAvailable");
        field.setAccessible(true);
        assertEquals(Boolean.TRUE, field.get(git));
    }

    @Test
    public void testEnsureGitAvailableDeterministicFailure() throws Exception {
        Command mockCommand = mock(Command.class);
        when(mockSession.getCommand()).thenReturn(mockCommand);
        when(mockCommand.executeCommand(anyString(), anyInt(), any(), anyMap()))
                .thenReturn(new CommandResult("", false, "", "", 127, "", "git: command not found", ""));

        resetGitAvailable();
        Method method = Git.class.getDeclaredMethod("ensureGitAvailable");
        method.setAccessible(true);
        try {
            method.invoke(git);
            fail("Expected GitNotFoundError");
        } catch (java.lang.reflect.InvocationTargetException e) {
            assertTrue(e.getCause() instanceof GitNotFoundError);
        }

        // gitAvailable should be cached as false
        Field field = Git.class.getDeclaredField("gitAvailable");
        field.setAccessible(true);
        assertEquals(Boolean.FALSE, field.get(git));
    }

    @Test
    public void testEnsureGitAvailableCachesSuccess() throws Exception {
        Command mockCommand = mock(Command.class);
        when(mockSession.getCommand()).thenReturn(mockCommand);
        when(mockCommand.executeCommand(anyString(), anyInt(), any(), anyMap()))
                .thenReturn(new CommandResult("", true, "", "", 0, "git version 2.40.0", "", ""));

        resetGitAvailable();
        Method method = Git.class.getDeclaredMethod("ensureGitAvailable");
        method.setAccessible(true);

        // First call
        method.invoke(git);
        // Second call should use cached value (no second executeCommand call)
        method.invoke(git);

        // executeCommand should have been called only once
        verify(mockCommand, times(1)).executeCommand(anyString(), anyInt(), any(), anyMap());
    }

    // ==================== restore validation Tests ====================

    @Test(expected = GitError.class)
    public void testRestoreEmptyPathsThrows() throws Throwable {
        try {
            git.restore("/tmp/repo", Collections.emptyList());
        } catch (Exception e) {
            if (e instanceof GitError) throw e;
            throw e;
        }
    }

    @Test(expected = GitError.class)
    public void testRestoreNullPathsThrows() throws Throwable {
        try {
            git.restore("/tmp/repo", null);
        } catch (Exception e) {
            if (e instanceof GitError) throw e;
            throw e;
        }
    }

    // ==================== Public API Mock Tests ====================

    private Git createGitWithVersionCheck() throws Exception {
        Command mockCommand = mock(Command.class);
        when(mockSession.getCommand()).thenReturn(mockCommand);

        // Git version check succeeds
        CommandResult versionResult = new CommandResult("", true, "", "", 0, "git version 2.40.0", "", "");
        when(mockCommand.executeCommand(eq("git --version"), anyInt(), any(), anyMap()))
                .thenReturn(versionResult);

        Git testGit = new Git(mockSession);
        return testGit;
    }

    @Test
    public void testInitSuccess() throws Exception {
        Git testGit = createGitWithVersionCheck();
        Command mockCommand = mockSession.getCommand();

        CommandResult initResult = new CommandResult("", true, "", "", 0,
                "Initialized empty Git repository in /tmp/repo/.git/", "", "");
        when(mockCommand.executeCommand(contains("'init'"), anyInt(), any(), anyMap()))
                .thenReturn(initResult);

        GitInitResult result = testGit.init("/tmp/repo");
        assertNotNull(result);
        assertEquals("/tmp/repo", result.getPath());
    }

    @Test
    public void testInitFailure() throws Exception {
        Git testGit = createGitWithVersionCheck();
        Command mockCommand = mockSession.getCommand();

        CommandResult failResult = new CommandResult("", false, "", "", 128, "",
                "fatal: not a git repository", "");
        when(mockCommand.executeCommand(contains("'init'"), anyInt(), any(), anyMap()))
                .thenReturn(failResult);

        try {
            testGit.init("/tmp/repo");
            fail("Expected GitError");
        } catch (GitError e) {
            assertTrue(e instanceof GitNotARepoError);
        }
    }

    @Test
    public void testCommitSuccess() throws Exception {
        Git testGit = createGitWithVersionCheck();
        Command mockCommand = mockSession.getCommand();

        CommandResult commitResult = new CommandResult("", true, "", "", 0,
                "[main abc1234] Test commit", "", "");
        when(mockCommand.executeCommand(contains("'commit'"), anyInt(), any(), anyMap()))
                .thenReturn(commitResult);

        GitCommitResult result = testGit.commit("/tmp/repo", "Test commit");
        assertNotNull(result);
        assertEquals("abc1234", result.getCommitHash());
    }

    @Test
    public void testStatusSuccess() throws Exception {
        Git testGit = createGitWithVersionCheck();
        Command mockCommand = mockSession.getCommand();

        CommandResult statusResult = new CommandResult("", true, "", "", 0,
                "## main\n M file.txt\n", "", "");
        when(mockCommand.executeCommand(contains("'status'"), anyInt(), any(), anyMap()))
                .thenReturn(statusResult);

        GitStatusResult result = testGit.status("/tmp/repo");
        assertNotNull(result);
        assertEquals("main", result.getCurrentBranch());
        assertEquals(1, result.getFiles().size());
        assertFalse("Worktree-only change should not be staged", result.getFiles().get(0).isStaged());
    }

    @Test
    public void testCloneSuccess() throws Exception {
        Git testGit = createGitWithVersionCheck();
        Command mockCommand = mockSession.getCommand();

        CommandResult cloneResult = new CommandResult("", true, "", "", 0,
                "Cloning into '/tmp/my-repo'...", "", "");
        when(mockCommand.executeCommand(contains("'clone'"), anyInt(), any(), anyMap()))
                .thenReturn(cloneResult);

        GitCloneResult result = testGit.clone("https://github.com/user/repo.git", "/tmp/my-repo", null, null, null);
        assertNotNull(result);
        assertEquals("/tmp/my-repo", result.getPath());
    }

    @Test
    public void testCloneAuthError() throws Exception {
        Git testGit = createGitWithVersionCheck();
        Command mockCommand = mockSession.getCommand();

        CommandResult failResult = new CommandResult("", false, "", "", 128, "",
                "fatal: Authentication failed for 'https://github.com/user/repo.git'", "");
        when(mockCommand.executeCommand(contains("'clone'"), anyInt(), any(), anyMap()))
                .thenReturn(failResult);

        try {
            testGit.clone("https://github.com/user/repo.git");
            fail("Expected GitAuthError");
        } catch (GitError e) {
            assertTrue(e instanceof GitAuthError);
        }
    }
}
