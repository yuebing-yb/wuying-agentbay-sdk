package com.aliyun.agentbay.git;

import com.aliyun.agentbay.model.CommandResult;
import com.aliyun.agentbay.service.BaseService;
import com.aliyun.agentbay.session.Session;

import java.util.*;
import java.util.regex.Matcher;
import java.util.regex.Pattern;

/**
 * Manage git operations in the AgentBay cloud environment.
 *
 * <p>Provides a high-level interface for common git workflows (clone, commit,
 * branch, config, etc.) by executing git commands on the remote session via
 * the Command module. All commands run with {@code GIT_TERMINAL_PROMPT=0} to
 * prevent interactive credential prompts.
 *
 * <p><b>Example:</b>
 * <pre>{@code
 * AgentBay agentBay = new AgentBay(apiKey);
 * Session session = agentBay.createSession();
 *
 * GitCloneResult result = session.getGit().clone(
 *     "https://github.com/user/repo.git", null, "main", 1, null);
 * System.out.println("Cloned to: " + result.getPath());
 *
 * session.close();
 * }</pre>
 */
public class Git extends BaseService {
    private volatile Boolean gitAvailable = null;
    private static final Map<String, String> DEFAULT_GIT_ENV;
    static {
        Map<String, String> env = new HashMap<>();
        env.put("GIT_TERMINAL_PROMPT", "0");
        env.put("LC_ALL", "C");
        DEFAULT_GIT_ENV = Collections.unmodifiableMap(env);
    }
    // Default timeout for git operations (30 seconds)
    private static final int DEFAULT_GIT_TIMEOUT_MS = 30000;
    // Default timeout for clone operations (5 minutes, as clone may download large repos)
    private static final int DEFAULT_CLONE_TIMEOUT_MS = 300000;
    // Default timeout for pull/push operations (2 minutes, as network operations may be slow)
    private static final int DEFAULT_PULL_TIMEOUT_MS = 120000;

    // Pre-compiled patterns for parsing git output
    private static final Pattern AHEAD_PATTERN = Pattern.compile("ahead\\s+(\\d+)");
    private static final Pattern BEHIND_PATTERN = Pattern.compile("behind\\s+(\\d+)");
    private static final Pattern COMMIT_HASH_PATTERN = Pattern.compile("\\[\\w+(?:\\s+\\([^)]+\\))?\\s+([a-f0-9]+)\\]");

    /**
     * Constructs a new {@code Git} service bound to the given session.
     *
     * @param session the session to execute git commands on
     */
    public Git(Session session) {
        super(session);
    }

    // ==================== Private Helper Methods ====================

    /**
     * Escape a string for safe use in a shell command.
     *
     * <p>Wraps the argument in single quotes and escapes any embedded
     * single quotes.
     *
     * @param arg the argument to escape
     * @return the shell-escaped argument string
     */
    private String shellEscape(String arg) {
        if (arg == null) return "''";
        return "'" + arg.replace("'", "'\\''") + "'";
    }

    /**
     * Build a complete git command string with optional {@code -C} directory flag.
     *
     * @param args     list of git sub-command arguments
     * @param repoPath working directory for git, or {@code null} to use the default
     * @return the fully constructed shell command string
     */
    private String buildGitCommand(List<String> args, String repoPath) {
        StringBuilder cmd = new StringBuilder("git");
        if (repoPath != null && !repoPath.isEmpty()) {
            cmd.append(" -C ").append(shellEscape(repoPath));
        }
        for (String arg : args) {
            cmd.append(" ").append(shellEscape(arg));
        }
        return cmd.toString();
    }

    /**
     * Execute a git command in the remote session.
     *
     * <p>Ensures git is available before running the command.
     *
     * @param args      list of git sub-command arguments
     * @param repoPath  working directory for git, or {@code null}
     * @param timeoutMs timeout in milliseconds, or {@code null} for the default
     * @return the command execution result
     * @throws GitError if git is not available
     */
    private CommandResult runGit(List<String> args, String repoPath, Integer timeoutMs) throws GitError {
        ensureGitAvailable();
        String cmd = buildGitCommand(args, repoPath);
        int timeout = timeoutMs != null ? timeoutMs : DEFAULT_GIT_TIMEOUT_MS;
        return session.getCommand().executeCommand(cmd, timeout, null, DEFAULT_GIT_ENV);
    }

    /**
     * Verify that git is installed and available in the remote session.
     *
     * <p>The result is cached after the first successful check so subsequent
     * calls are no-ops.
     *
     * @throws GitNotFoundError if git is not installed
     */
    private synchronized void ensureGitAvailable() throws GitError {
        if (gitAvailable != null && gitAvailable) {
            return;
        }
        CommandResult result = session.getCommand().executeCommand("git --version", 5000, null, DEFAULT_GIT_ENV);
        if (result.isSuccess() && result.getExitCode() == 0) {
            gitAvailable = true;
        } else {
            gitAvailable = false;
            throw new GitNotFoundError("Git is not available or not installed", result.getExitCode(),
                    result.getStderr() != null ? result.getStderr() : "");
        }
    }

    /**
     * Classify a failed git command result into a specific exception type.
     *
     * <p>Inspects the stderr output to determine whether the failure is
     * an authentication error, a "not a repo" error, a conflict, etc.
     *
     * @param operation human-readable operation name for the error message
     * @param result    the failed command result
     * @return an appropriate {@link GitError} subclass
     */
    private GitError classifyError(String operation, CommandResult result) {
        String rawStderr = result.getStderr() != null ? result.getStderr() : "";
        String stderr = rawStderr.toLowerCase();
        int exitCode = result.getExitCode();

        // Git not found (check first, as other errors are meaningless if git is missing)
        if (exitCode == 127 ||
            stderr.contains("command not found") ||
            stderr.contains("git: not found")) {
            return new GitNotFoundError(
                operation + " failed: git not found. " + rawStderr, exitCode, rawStderr);
        }

        // Authentication errors
        if (stderr.contains("authentication failed") ||
            stderr.contains("could not read username") ||
            stderr.contains("invalid credentials") ||
            stderr.contains("authorization failed") ||
            stderr.contains("access denied") ||
            stderr.contains("permission denied") ||
            stderr.contains("403")) {
            return new GitAuthError(
                operation + " failed: authentication error. " + rawStderr, exitCode, rawStderr);
        }

        // Not a git repository
        if (stderr.contains("not a git repository") ||
            stderr.contains("does not appear to be a git repository")) {
            return new GitNotARepoError(
                operation + " failed: not a git repository. " + rawStderr, exitCode, rawStderr);
        }

        // Merge/rebase conflicts (use raw stderr for case-sensitive CONFLICT)
        if (rawStderr.contains("CONFLICT") ||
            stderr.contains("merge conflict") ||
            stderr.contains("automatic merge failed")) {
            return new GitConflictError(
                operation + " failed: merge conflict. " + rawStderr, exitCode, rawStderr);
        }

        return new GitError(
            operation + " failed (exit code " + exitCode + "): " + rawStderr, exitCode, rawStderr);
    }

    /**
     * Derive a repository directory name from a clone URL.
     *
     * <p>Strips trailing slashes, the {@code .git} suffix, URL-decodes,
     * and extracts the last path segment.
     *
     * @param url the repository URL
     * @return the derived directory name
     */
    private String deriveRepoDirFromUrl(String url) {
        String cleaned = url;
        while (cleaned.endsWith("/")) {
            cleaned = cleaned.substring(0, cleaned.length() - 1);
        }
        if (cleaned.endsWith(".git")) {
            cleaned = cleaned.substring(0, cleaned.length() - 4);
        }
        try {
            cleaned = java.net.URLDecoder.decode(cleaned, "UTF-8");
        } catch (Exception e) {
            // ignore decoding errors
        }
        int lastSlash = cleaned.lastIndexOf('/');
        int lastColon = cleaned.lastIndexOf(':');
        int separatorIndex = Math.max(lastSlash, lastColon);
        if (separatorIndex >= 0 && separatorIndex < cleaned.length() - 1) {
            return cleaned.substring(separatorIndex + 1);
        }
        return cleaned;
    }

    /**
     * Derive a normalized file status string from porcelain status codes.
     *
     * @param indexStatus    the index status character
     * @param workTreeStatus the working-tree status character
     * @return normalized status such as {@code "modified"}, {@code "added"}, etc.
     */
    private String deriveStatus(String indexStatus, String workTreeStatus) {
        String combined = (indexStatus != null ? indexStatus : "") + (workTreeStatus != null ? workTreeStatus : "");
        if (combined.contains("U") || "AA".equals(combined)) return "conflict";
        if (combined.contains("R")) return "renamed";
        if (combined.contains("C")) return "copied";
        if (combined.contains("D")) return "deleted";
        if (combined.contains("A")) return "added";
        if (combined.contains("M")) return "modified";
        if (combined.contains("T")) return "typechange";
        if (combined.contains("?")) return "untracked";
        return "unknown";
    }

    /**
     * Parse the output of {@code git status --porcelain=1 -b}.
     *
     * <p>Extracts the current branch, upstream tracking information,
     * ahead/behind counts, and per-file status entries.
     *
     * @param output raw stdout from the git status command
     * @return parsed {@link GitStatusResult}
     */
    private GitStatusResult parseGitStatus(String output) {
        String currentBranch = null;
        String upstream = null;
        int ahead = 0;
        int behind = 0;
        boolean detached = false;
        List<GitFileStatus> files = new ArrayList<>();
        
        String[] lines = output.split("\n");
        for (String line : lines) {
            if (line.isEmpty()) continue;
            
            // Branch line: only trim the branch info line
            if (line.trim().startsWith("## ")) {
                String branchInfo = line.trim().substring(3);
                
                // Handle "No commits yet on <branch>" format
                if (branchInfo.startsWith("No commits yet on ")) {
                    currentBranch = branchInfo.substring("No commits yet on ".length()).split("\\.{3}")[0].trim();
                    continue;
                }
                
                // Handle "Initial commit on <branch>" format
                if (branchInfo.startsWith("Initial commit on ")) {
                    currentBranch = branchInfo.substring("Initial commit on ".length()).split("\\.{3}")[0].trim();
                    continue;
                }
                
                String[] parts = branchInfo.split("\\.{3}");
                if (parts.length > 0) {
                    currentBranch = parts[0].trim();
                }
                
                if (currentBranch != null && currentBranch.contains("HEAD")) {
                    detached = true;
                    String[] detachedParts = currentBranch.split("\\s+");
                    if (detachedParts.length > 1) {
                        currentBranch = detachedParts[1].replaceAll("[()]", "").trim();
                    }
                }
                
                if (parts.length > 1) {
                    String trackingInfo = parts[1];
                    // Extract upstream (first token before any space/bracket)
                    String[] tracking = trackingInfo.trim().split("\\s+");
                    if (tracking.length > 0) {
                        upstream = tracking[0].trim();
                    }
                    // Search ahead/behind in the entire tracking info string
                    Matcher aheadMatcher = AHEAD_PATTERN.matcher(trackingInfo);
                    if (aheadMatcher.find()) {
                        ahead = Integer.parseInt(aheadMatcher.group(1));
                    }
                    Matcher behindMatcher = BEHIND_PATTERN.matcher(trackingInfo);
                    if (behindMatcher.find()) {
                        behind = Integer.parseInt(behindMatcher.group(1));
                    }
                }
            } else if (line.length() >= 3) {
                // File status lines: DO NOT trim - porcelain format is positional
                // Format: XY filename (X=index status at pos 0, Y=worktree status at pos 1)
                String indexStatus = line.substring(0, 1);
                String workTreeStatus = line.substring(1, 2);
                String path = line.substring(3).trim();
                
                String renamedFrom = null;
                if (indexStatus.equals("R") || workTreeStatus.equals("R")) {
                    String[] pathParts = path.split(" -> ");
                    if (pathParts.length == 2) {
                        renamedFrom = pathParts[0].trim();
                        path = pathParts[1].trim();
                    }
                }
                
                String status = deriveStatus(indexStatus, workTreeStatus);
                boolean staged = !indexStatus.equals(" ") && !indexStatus.equals("?");
                
                files.add(new GitFileStatus(path, status, indexStatus, workTreeStatus, staged, renamedFrom));
            }
        }
        
        return new GitStatusResult(currentBranch, upstream, ahead, behind, detached, files);
    }

    /**
     * Parse the output of {@code git log} with NUL/SOH separators.
     *
     * @param output raw stdout from the git log command
     * @return parsed {@link GitLogResult}
     */
    private GitLogResult parseGitLog(String output) {
        List<GitLogEntry> entries = new ArrayList<>();
        // Split by NUL character (record separator)
        String[] records = output.split("\0");
        for (String record : records) {
            record = record.trim();
            if (record.isEmpty()) continue;
            // Split by SOH character (field separator)
            String[] fields = record.split("\1");
            if (fields.length >= 6) {
                entries.add(new GitLogEntry(
                    fields[0].trim(),  // hash
                    fields[1],          // shortHash
                    fields[2],          // authorName
                    fields[3],          // authorEmail
                    fields[4],          // date
                    fields[5].trim()    // message
                ));
            }
        }
        return new GitLogResult(entries);
    }

    /**
     * Parse the output of {@code git branch --format}.
     *
     * @param output raw stdout from the git branch command
     * @return parsed {@link GitBranchListResult}
     */
    private GitBranchListResult parseGitBranches(String output) {
        List<GitBranchInfo> branches = new ArrayList<>();
        String current = null;
        
        String[] lines = output.split("\n");
        for (String line : lines) {
            line = line.trim();
            if (line.isEmpty()) continue;
            
            // --format=%(refname:short)\t%(HEAD) produces: branch_name\t* or branch_name\t 
            String[] parts = line.split("\t");
            if (parts.length >= 2) {
                String name = parts[0].trim();
                boolean isCurrent = "*".equals(parts[1].trim());
                if (isCurrent) {
                    current = name;
                }
                branches.add(new GitBranchInfo(name, isCurrent));
            } else {
                // Fallback: handle legacy format (e.g., "* main" or "  develop")
                if (line.startsWith("* ")) {
                    String name = line.substring(2).trim();
                    // Skip detached HEAD state
                    if (name.startsWith("(HEAD detached") || name.startsWith("(no branch)")) {
                        continue;
                    }
                    current = name;
                    branches.add(new GitBranchInfo(name, true));
                } else {
                    String name = line.trim();
                    branches.add(new GitBranchInfo(name, false));
                }
            }
        }
        
        return new GitBranchListResult(branches, current);
    }

    // ==================== Public API Methods ====================

    /**
     * Clone a git repository with default settings.
     *
     * @param url the repository URL to clone (HTTPS or SSH)
     * @return clone result containing the local repository path
     * @throws GitError if the clone operation fails
     * @see #clone(String, String, String, Integer, Integer)
     */
    public GitCloneResult clone(String url) throws GitError {
        return clone(url, null, null, null, null);
    }

    /**
     * Clone a git repository into the remote session environment.
     *
     * <p>Supports public repositories. When {@code branch} is specified,
     * {@code --single-branch} is automatically added.
     *
     * <p><b>Example:</b>
     * <pre>{@code
     * GitCloneResult result = session.getGit().clone(
     *     "https://github.com/user/repo.git",
     *     null, "main", 1, null);
     * System.out.println("Cloned to: " + result.getPath());
     * }</pre>
     *
     * @param url       the repository URL to clone (HTTPS or SSH)
     * @param path      target directory path; if {@code null}, derived from the URL
     * @param branch    branch to clone (adds {@code --single-branch}); may be {@code null}
     * @param depth     create a shallow clone with the given number of commits; may be {@code null}
     * @param timeoutMs timeout in milliseconds; defaults to 300 000 (5 min)
     * @return clone result containing the local repository path
     * @throws GitNotFoundError if git is not installed
     * @throws GitAuthError     if authentication fails
     * @throws GitError         for other git errors
     */
    public GitCloneResult clone(String url, String path, String branch, Integer depth, Integer timeoutMs) throws GitError {
        List<String> args = new ArrayList<>();
        args.add("clone");
        
        if (branch != null) {
            args.add("-b");
            args.add(branch);
            args.add("--single-branch");
        }
        
        if (depth != null && depth > 0) {
            args.add("--depth");
            args.add(depth.toString());
        }
        
        args.add(url);
        
        if (path == null) {
            path = deriveRepoDirFromUrl(url);
        }
        args.add(path);
        
        int timeout = timeoutMs != null ? timeoutMs : DEFAULT_CLONE_TIMEOUT_MS;
        CommandResult result = runGit(args, null, timeout);
        
        if (!result.isSuccess()) {
            throw classifyError("clone", result);
        }
        
        return new GitCloneResult(path);
    }

    /**
     * Initialize a new git repository at the given path with default settings.
     *
     * @param path the directory path to initialize
     * @return init result containing the repository path
     * @throws GitError if the init operation fails
     * @see #init(String, String, boolean, Integer)
     */
    public GitInitResult init(String path) throws GitError {
        return init(path, null, false, null);
    }

    /**
     * Initialize a new git repository.
     *
     * <p>The directory does not need to exist beforehand; git will create it.
     *
     * <p><b>Example:</b>
     * <pre>{@code
     * GitInitResult result = session.getGit().init(
     *     "/home/user/my-project", "main", false, null);
     * System.out.println("Initialized at: " + result.getPath());
     * }</pre>
     *
     * @param path          the directory path to initialize
     * @param initialBranch name of the initial branch; may be {@code null} for git default
     * @param bare          {@code true} to create a bare repository
     * @param timeoutMs     timeout in milliseconds; defaults to 30 000
     * @return init result containing the repository path
     * @throws GitNotFoundError if git is not installed
     * @throws GitError         for other git errors
     */
    public GitInitResult init(String path, String initialBranch, boolean bare, Integer timeoutMs) throws GitError {
        List<String> args = new ArrayList<>();
        args.add("init");
        
        if (initialBranch != null) {
            args.add("--initial-branch=" + initialBranch);
        }
        
        if (bare) {
            args.add("--bare");
        }
        
        // Pass path as argument to 'git init <path>' instead of using '-C'
        // because the directory may not exist yet and '-C' requires it to exist
        args.add(path);
        
        CommandResult result = runGit(args, null, timeoutMs);
        
        if (!result.isSuccess()) {
            throw classifyError("init", result);
        }
        
        return new GitInitResult(path);
    }

    /**
     * Stage all files in the repository for the next commit.
     *
     * @param repoPath the repository working directory
     * @throws GitError if the add operation fails
     * @see #add(String, List, boolean, Integer)
     */
    public void add(String repoPath) throws GitError {
        add(repoPath, null, true, null);
    }

    /**
     * Stage files for the next commit.
     *
     * <p><b>Example:</b>
     * <pre>{@code
     * // Stage specific files
     * session.getGit().add(repoPath,
     *     Arrays.asList("src/Main.java", "README.md"), false, null);
     *
     * // Stage all changes
     * session.getGit().add(repoPath, null, true, null);
     * }</pre>
     *
     * @param files     list of specific file paths to stage; may be {@code null}
     * @param repoPath  the repository working directory
     * @param all       {@code true} to stage all changes (equivalent to {@code git add -A})
     * @param timeoutMs timeout in milliseconds; defaults to 30 000
     * @throws GitNotFoundError  if git is not installed
     * @throws GitNotARepoError  if the path is not a git repository
     * @throws GitError          for other git errors
     */
    public void add(String repoPath, List<String> files, boolean all, Integer timeoutMs) throws GitError {
        List<String> args = new ArrayList<>();
        args.add("add");
        
        if (files != null && !files.isEmpty()) {
            // Use -- separator to prevent filenames from being interpreted as options
            args.add("--");
            args.addAll(files);
        } else if (all) {
            args.add("-A");
        } else {
            args.add(".");
        }
        
        CommandResult result = runGit(args, repoPath, timeoutMs);
        
        if (!result.isSuccess()) {
            throw classifyError("add", result);
        }
    }

    /**
     * Commit staged changes with the given message.
     *
     * @param repoPath the repository working directory
     * @param message  the commit message
     * @return commit result containing the commit hash
     * @throws GitError if the commit operation fails
     * @see #commit(String, String, String, String, boolean, Integer)
     */
    public GitCommitResult commit(String repoPath, String message) throws GitError {
        return commit(repoPath, message, null, null, false, null);
    }

    /**
     * Commit staged changes with full options.
     *
     * <p><b>Example:</b>
     * <pre>{@code
     * session.getGit().add(repoPath);
     * GitCommitResult result = session.getGit().commit(
     *     repoPath, "feat: add new feature",
     *     "John Doe", "john@example.com", false, null);
     * System.out.println("Commit: " + result.getCommitHash());
     * }</pre>
     *
     * @param repoPath    the repository working directory
     * @param message     the commit message
     * @param authorName  custom author name; may be {@code null} to use git config
     * @param authorEmail custom author email; may be {@code null} to use git config
     * @param allowEmpty  {@code true} to allow creating a commit with no changes
     * @param timeoutMs   timeout in milliseconds; defaults to 30 000
     * @return commit result containing the commit hash
     * @throws GitNotFoundError  if git is not installed
     * @throws GitNotARepoError  if the path is not a git repository
     * @throws GitError          for other git errors
     */
    public GitCommitResult commit(String repoPath, String message, String authorName, String authorEmail, boolean allowEmpty, Integer timeoutMs) throws GitError {
        List<String> args = new ArrayList<>();
        // -c parameters must come BEFORE the 'commit' subcommand
        if (authorName != null) {
            args.add("-c");
            args.add("user.name=" + authorName);
        }
        if (authorEmail != null) {
            args.add("-c");
            args.add("user.email=" + authorEmail);
        }
        args.add("commit");
        args.add("-m");
        args.add(message);
        
        if (allowEmpty) {
            args.add("--allow-empty");
        }
        
        CommandResult result = runGit(args, repoPath, timeoutMs);
        
        if (!result.isSuccess()) {
            throw classifyError("commit", result);
        }
        
        String commitHash = null;
        String stdout = result.getStdout();
        if (stdout != null && stdout.contains("[")) {
            Matcher matcher = COMMIT_HASH_PATTERN.matcher(stdout);
            if (matcher.find()) {
                commitHash = matcher.group(1);
            }
        }
        
        return new GitCommitResult(commitHash);
    }

    /**
     * Get the status of the repository with default timeout.
     *
     * @param repoPath the repository working directory
     * @return parsed status result
     * @throws GitError if the status operation fails
     * @see #status(String, Integer)
     */
    public GitStatusResult status(String repoPath) throws GitError {
        return status(repoPath, null);
    }

    /**
     * Get the current status of a git repository.
     *
     * <p>Returns branch information, tracking status, and per-file change
     * details parsed from {@code git status --porcelain=1 -b}.
     *
     * <p><b>Example:</b>
     * <pre>{@code
     * GitStatusResult status = session.getGit().status(repoPath, null);
     * System.out.println("Branch: " + status.getCurrentBranch());
     * System.out.println("Clean: " + status.isClean());
     * for (GitFileStatus f : status.getFiles()) {
     *     System.out.println(f.getStatus() + " " + f.getPath());
     * }
     * }</pre>
     *
     * @param repoPath  the repository working directory
     * @param timeoutMs timeout in milliseconds; defaults to 30 000
     * @return parsed status result
     * @throws GitNotFoundError  if git is not installed
     * @throws GitNotARepoError  if the path is not a git repository
     * @throws GitError          for other git errors
     */
    public GitStatusResult status(String repoPath, Integer timeoutMs) throws GitError {
        List<String> args = new ArrayList<>();
        args.add("status");
        args.add("--porcelain=1");
        args.add("-b");
        
        CommandResult result = runGit(args, repoPath, timeoutMs);
        
        if (!result.isSuccess()) {
            throw classifyError("status", result);
        }
        
        return parseGitStatus(result.getStdout());
    }

    /**
     * Get the commit log with default settings.
     *
     * @param repoPath the repository working directory
     * @return log result containing commit entries
     * @throws GitError if the log operation fails
     * @see #log(String, Integer, Integer)
     */
    public GitLogResult log(String repoPath) throws GitError {
        return log(repoPath, null, null);
    }

    /**
     * Get the commit log of a repository.
     *
     * <p><b>Example:</b>
     * <pre>{@code
     * GitLogResult log = session.getGit().log(repoPath, 10, null);
     * for (GitLogEntry entry : log.getEntries()) {
     *     System.out.println(entry.getShortHash() + " " + entry.getMessage());
     * }
     * }</pre>
     *
     * @param repoPath  the repository working directory
     * @param maxCount  maximum number of commits to return; may be {@code null} for all
     * @param timeoutMs timeout in milliseconds; defaults to 30 000
     * @return log result containing commit entries
     * @throws GitNotFoundError  if git is not installed
     * @throws GitNotARepoError  if the path is not a git repository
     * @throws GitError          for other git errors
     */
    public GitLogResult log(String repoPath, Integer maxCount, Integer timeoutMs) throws GitError {
        List<String> args = new ArrayList<>();
        args.add("log");
        args.add("--format=%H%x01%h%x01%an%x01%ae%x01%aI%x01%s%x00");
        
        if (maxCount != null && maxCount > 0) {
            args.add("-n");
            args.add(maxCount.toString());
        }
        
        CommandResult result = runGit(args, repoPath, timeoutMs);
        
        if (!result.isSuccess()) {
            throw classifyError("log", result);
        }
        
        return parseGitLog(result.getStdout());
    }

    /**
     * List all branches in the repository with default timeout.
     *
     * @param repoPath the repository working directory
     * @return branch list result
     * @throws GitError if the operation fails
     * @see #listBranches(String, Integer)
     */
    public GitBranchListResult listBranches(String repoPath) throws GitError {
        return listBranches(repoPath, null);
    }

    /**
     * List all branches in a repository.
     *
     * <p><b>Example:</b>
     * <pre>{@code
     * GitBranchListResult branches = session.getGit().listBranches(repoPath, null);
     * System.out.println("Current: " + branches.getCurrent());
     * for (GitBranchInfo b : branches.getBranches()) {
     *     System.out.println((b.isCurrent() ? "* " : "  ") + b.getName());
     * }
     * }</pre>
     *
     * @param repoPath  the repository working directory
     * @param timeoutMs timeout in milliseconds; defaults to 30 000
     * @return branch list result containing all branches and current branch
     * @throws GitNotFoundError  if git is not installed
     * @throws GitNotARepoError  if the path is not a git repository
     * @throws GitError          for other git errors
     */
    public GitBranchListResult listBranches(String repoPath, Integer timeoutMs) throws GitError {
        List<String> args = new ArrayList<>();
        args.add("branch");
        args.add("--format=%(refname:short)\t%(HEAD)");
        
        CommandResult result = runGit(args, repoPath, timeoutMs);
        
        if (!result.isSuccess()) {
            throw classifyError("list branches", result);
        }
        
        return parseGitBranches(result.getStdout());
    }

    /**
     * Create a new branch and check it out.
     *
     * @param repoPath the repository working directory
     * @param branch   the new branch name
     * @throws GitError if the operation fails
     * @see #createBranch(String, String, boolean, Integer)
     */
    public void createBranch(String repoPath, String branch) throws GitError {
        createBranch(repoPath, branch, true, null);
    }

    /**
     * Create a new branch, optionally checking it out immediately.
     *
     * <p><b>Example:</b>
     * <pre>{@code
     * // Create and switch to the new branch
     * session.getGit().createBranch(repoPath, "feature/login", true, null);
     *
     * // Create without switching
     * session.getGit().createBranch(repoPath, "release/v1.0", false, null);
     * }</pre>
     *
     * @param repoPath  the repository working directory
     * @param branch    the new branch name
     * @param checkout  {@code true} to switch to the new branch after creation
     * @param timeoutMs timeout in milliseconds; defaults to 30 000
     * @throws GitNotFoundError  if git is not installed
     * @throws GitNotARepoError  if the path is not a git repository
     * @throws GitError          for other git errors
     */
    public void createBranch(String repoPath, String branch, boolean checkout, Integer timeoutMs) throws GitError {
        List<String> args = new ArrayList<>();
        if (checkout) {
            args.add("checkout");
            args.add("-b");
        } else {
            args.add("branch");
        }
        args.add(branch);
        
        CommandResult result = runGit(args, repoPath, timeoutMs);
        
        if (!result.isSuccess()) {
            throw classifyError("create branch", result);
        }
    }

    /**
     * Switch to an existing branch with default timeout.
     *
     * @param repoPath the repository working directory
     * @param branch   the branch name to check out
     * @throws GitError if the operation fails
     * @see #checkoutBranch(String, String, Integer)
     */
    public void checkoutBranch(String repoPath, String branch) throws GitError {
        checkoutBranch(repoPath, branch, null);
    }

    /**
     * Switch to an existing branch.
     *
     * <p><b>Example:</b>
     * <pre>{@code
     * session.getGit().checkoutBranch(repoPath, "main", null);
     * }</pre>
     *
     * @param repoPath  the repository working directory
     * @param branch    the branch name to check out
     * @param timeoutMs timeout in milliseconds; defaults to 30 000
     * @throws GitNotFoundError  if git is not installed
     * @throws GitNotARepoError  if the path is not a git repository
     * @throws GitError          for other git errors
     */
    public void checkoutBranch(String repoPath, String branch, Integer timeoutMs) throws GitError {
        List<String> args = new ArrayList<>();
        args.add("checkout");
        args.add(branch);
        
        CommandResult result = runGit(args, repoPath, timeoutMs);
        
        if (!result.isSuccess()) {
            throw classifyError("checkout", result);
        }
    }

    /**
     * Delete a branch (safe delete, branch must be fully merged).
     *
     * @param repoPath the repository working directory
     * @param branch   the branch name to delete
     * @throws GitError if the operation fails
     * @see #deleteBranch(String, String, boolean, Integer)
     */
    public void deleteBranch(String repoPath, String branch) throws GitError {
        deleteBranch(repoPath, branch, false, null);
    }

    /**
     * Delete a branch.
     *
     * <p><b>Example:</b>
     * <pre>{@code
     * // Safe delete (must be fully merged)
     * session.getGit().deleteBranch(repoPath, "feature/old", false, null);
     *
     * // Force delete
     * session.getGit().deleteBranch(repoPath, "feature/abandoned", true, null);
     * }</pre>
     *
     * @param repoPath  the repository working directory
     * @param branch    the branch name to delete
     * @param force     {@code true} to force delete (uses {@code -D}) even if not fully merged
     * @param timeoutMs timeout in milliseconds; defaults to 30 000
     * @throws GitNotFoundError  if git is not installed
     * @throws GitNotARepoError  if the path is not a git repository
     * @throws GitError          for other git errors
     */
    public void deleteBranch(String repoPath, String branch, boolean force, Integer timeoutMs) throws GitError {
        List<String> args = new ArrayList<>();
        args.add("branch");
        if (force) {
            args.add("-D");
        } else {
            args.add("-d");
        }
        args.add(branch);
        
        CommandResult result = runGit(args, repoPath, timeoutMs);
        
        if (!result.isSuccess()) {
            throw classifyError("delete branch", result);
        }
    }

    /**
     * Add a remote repository with default settings.
     *
     * @param repoPath the repository working directory
     * @param name     the remote name (e.g., {@code "origin"})
     * @param url      the remote URL
     * @throws GitError if the operation fails
     * @see #remoteAdd(String, String, String, boolean, boolean, Integer)
     */
    public void remoteAdd(String repoPath, String name, String url) throws GitError {
        remoteAdd(repoPath, name, url, false, false, null);
    }

    /**
     * Add a remote repository with full options.
     *
     * <p><b>Example:</b>
     * <pre>{@code
     * // Add and immediately fetch
     * session.getGit().remoteAdd(repoPath,
     *     "origin", "https://github.com/user/repo.git",
     *     true, false, null);
     *
     * // Overwrite an existing remote
     * session.getGit().remoteAdd(repoPath,
     *     "origin", "https://github.com/user/new-repo.git",
     *     false, true, null);
     * }</pre>
     *
     * @param repoPath  the repository working directory
     * @param name      the remote name (e.g., {@code "origin"})
     * @param url       the remote URL
     * @param fetch     {@code true} to fetch immediately after adding
     * @param overwrite {@code true} to remove and re-add if the remote already exists
     * @param timeoutMs timeout in milliseconds; defaults to 30 000
     * @throws GitNotFoundError  if git is not installed
     * @throws GitNotARepoError  if the path is not a git repository
     * @throws GitAuthError      if authentication fails during fetch
     * @throws GitError          for other git errors
     */
    public void remoteAdd(String repoPath, String name, String url, boolean fetch, boolean overwrite, Integer timeoutMs) throws GitError {
        if (overwrite) {
            // Remove existing remote first (ignore errors if it doesn't exist)
            List<String> removeArgs = new ArrayList<>();
            removeArgs.add("remote");
            removeArgs.add("remove");
            removeArgs.add(name);
            runGit(removeArgs, repoPath, timeoutMs); // ignore result
        }
        
        List<String> args = new ArrayList<>();
        args.add("remote");
        args.add("add");
        args.add(name);
        args.add(url);
        
        CommandResult result = runGit(args, repoPath, timeoutMs);
        
        if (!result.isSuccess()) {
            throw classifyError("remote add", result);
        }
        
        if (fetch) {
            List<String> fetchArgs = new ArrayList<>();
            fetchArgs.add("fetch");
            fetchArgs.add(name);
            CommandResult fetchResult = runGit(fetchArgs, repoPath, timeoutMs);
            if (!fetchResult.isSuccess()) {
                throw classifyError("fetch", fetchResult);
            }
        }
    }

    /**
     * Get the URL of a named remote with default timeout.
     *
     * @param repoPath the repository working directory
     * @param name     the remote name
     * @return the remote URL, or {@code null} if the remote does not exist
     * @throws GitError if the operation fails
     * @see #remoteGet(String, String, Integer)
     */
    public String remoteGet(String repoPath, String name) throws GitError {
        return remoteGet(repoPath, name, null);
    }

    /**
     * Get the URL of a named remote.
     *
     * <p><b>Example:</b>
     * <pre>{@code
     * String url = session.getGit().remoteGet(repoPath, "origin", null);
     * if (url != null) {
     *     System.out.println("Origin URL: " + url);
     * }
     * }</pre>
     *
     * @param repoPath  the repository working directory
     * @param name      the remote name
     * @param timeoutMs timeout in milliseconds; defaults to 30 000
     * @return the remote URL, or {@code null} if the remote does not exist
     * @throws GitNotFoundError  if git is not installed
     * @throws GitNotARepoError  if the path is not a git repository
     * @throws GitError          for other git errors
     */
    public String remoteGet(String repoPath, String name, Integer timeoutMs) throws GitError {
        ensureGitAvailable();
        CommandResult result = runGit(Arrays.asList("remote", "get-url", name), repoPath, timeoutMs);
        if (!result.isSuccess()) {
            String stderr = result.getStderr() != null ? result.getStderr().toLowerCase() : "";
            if (stderr.contains("no such remote")) {
                return null;
            }
            throw classifyError("remote get", result);
        }
        String trimmed = result.getStdout() != null ? result.getStdout().trim() : "";
        return trimmed.isEmpty() ? null : trimmed;
    }

    /**
     * Reset the repository to the default state.
     *
     * @param repoPath the repository working directory
     * @throws GitError if the operation fails
     * @see #reset(String, String, String, List, Integer)
     */
    public void reset(String repoPath) throws GitError {
        reset(repoPath, null, null, null, null);
    }

    /**
     * Reset the current HEAD to a specified state.
     *
     * <p><b>Example:</b>
     * <pre>{@code
     * // Soft reset to the previous commit
     * session.getGit().reset(repoPath, "soft", "HEAD~1", null, null);
     *
     * // Unstage specific files
     * session.getGit().reset(repoPath, null, null,
     *     Arrays.asList("file1.txt", "file2.txt"), null);
     * }</pre>
     *
     * @param repoPath  the repository working directory
     * @param mode      reset mode ({@code "soft"}, {@code "mixed"}, or {@code "hard"}); may be {@code null}
     * @param target    the commit reference to reset to; may be {@code null}
     * @param paths     specific paths to reset; may be {@code null}
     * @param timeoutMs timeout in milliseconds; defaults to 30 000
     * @throws GitNotFoundError  if git is not installed
     * @throws GitNotARepoError  if the path is not a git repository
     * @throws GitError          for other git errors
     */
    public void reset(String repoPath, String mode, String target, List<String> paths, Integer timeoutMs) throws GitError {
        List<String> args = new ArrayList<>();
        args.add("reset");
        
        if (mode != null) {
            args.add("--" + mode);
        }
        
        if (target != null) {
            args.add(target);
        }
        
        if (paths != null && !paths.isEmpty()) {
            args.add("--");
            args.addAll(paths);
        }
        
        CommandResult result = runGit(args, repoPath, timeoutMs);
        
        if (!result.isSuccess()) {
            throw classifyError("reset", result);
        }
    }

    /**
     * Restore working tree files with default settings.
     *
     * @param repoPath the repository working directory
     * @param paths    list of file paths to restore
     * @throws GitError if the operation fails
     * @see #restore(String, List, boolean, Boolean, String, Integer)
     */
    public void restore(String repoPath, List<String> paths) throws GitError {
        restore(repoPath, paths, false, null, null, null);
    }

    /**
     * Restore working tree and/or staged files.
     *
     * <p>At least one path must be specified. When {@code staged} is {@code true}
     * and {@code worktree} is not explicitly set, only staged changes are restored.
     *
     * <p><b>Example:</b>
     * <pre>{@code
     * // Discard working tree changes
     * session.getGit().restore(repoPath,
     *     Arrays.asList("src/Main.java"), false, null, null, null);
     *
     * // Unstage a file
     * session.getGit().restore(repoPath,
     *     Arrays.asList("src/Main.java"), true, null, null, null);
     * }</pre>
     *
     * @param repoPath  the repository working directory
     * @param paths     list of file paths to restore (must not be empty)
     * @param staged    {@code true} to restore staged changes
     * @param worktree  explicitly control worktree restore; defaults to {@code !staged}
     * @param source    source commit to restore from; may be {@code null}
     * @param timeoutMs timeout in milliseconds; defaults to 30 000
     * @throws GitError if paths is empty or the operation fails
     */
    public void restore(String repoPath, List<String> paths, boolean staged, Boolean worktree, String source, Integer timeoutMs) throws GitError {
        // Validate: at least one path must be specified
        if (paths == null || paths.isEmpty()) {
            throw new GitError("git restore requires at least one path", -1, "");
        }
        
        boolean resolvedWorktree = worktree != null ? worktree : !staged;
        
        List<String> args = new ArrayList<>();
        args.add("restore");
        
        if (staged) {
            args.add("--staged");
        }
        
        if (resolvedWorktree) {
            args.add("--worktree");
        }
        
        if (source != null) {
            args.add("--source");
            args.add(source);
        }
        
        args.add("--");
        args.addAll(paths);
        
        CommandResult result = runGit(args, repoPath, timeoutMs);
        
        if (!result.isSuccess()) {
            throw classifyError("restore", result);
        }
    }

    /**
     * Pull changes from the default remote with default timeout.
     *
     * @param repoPath the repository working directory
     * @throws GitError if the operation fails
     * @see #pull(String, String, String, Integer)
     */
    public void pull(String repoPath) throws GitError {
        pull(repoPath, null, null, null);
    }

    /**
     * Pull changes from a remote repository.
     *
     * <p><b>Example:</b>
     * <pre>{@code
     * session.getGit().pull(repoPath, "origin", "main", null);
     * }</pre>
     *
     * @param repoPath  the repository working directory
     * @param remote    the remote name (e.g., {@code "origin"}); may be {@code null}
     * @param branch    the branch to pull; may be {@code null}
     * @param timeoutMs timeout in milliseconds; defaults to 120 000 (2 min)
     * @throws GitNotFoundError   if git is not installed
     * @throws GitNotARepoError   if the path is not a git repository
     * @throws GitAuthError       if authentication fails
     * @throws GitConflictError   if there are merge conflicts
     * @throws GitError           for other git errors
     */
    public void pull(String repoPath, String remote, String branch, Integer timeoutMs) throws GitError {
        List<String> args = new ArrayList<>();
        args.add("pull");
        
        if (remote != null) {
            args.add(remote);
            if (branch != null) {
                args.add(branch);
            }
        }
        
        int timeout = timeoutMs != null ? timeoutMs : DEFAULT_PULL_TIMEOUT_MS;
        CommandResult result = runGit(args, repoPath, timeout);
        
        if (!result.isSuccess()) {
            throw classifyError("pull", result);
        }
    }

    /**
     * Configure git user name and email with default scope.
     *
     * @param repoPath the repository working directory
     * @param name     the user name
     * @param email    the user email
     * @throws GitError if the operation fails
     * @see #configureUser(String, String, String, String, Integer)
     */
    public void configureUser(String repoPath, String name, String email) throws GitError {
        configureUser(repoPath, name, email, null, null);
    }

    /**
     * Configure git user name and email.
     *
     * <p><b>Example:</b>
     * <pre>{@code
     * session.getGit().configureUser(repoPath,
     *     "John Doe", "john@example.com", "local", null);
     * }</pre>
     *
     * @param repoPath  the repository working directory
     * @param name      the user name
     * @param email     the user email
     * @param scope     config scope ({@code "local"}, {@code "global"}); may be {@code null}
     * @param timeoutMs timeout in milliseconds; defaults to 30 000
     * @throws GitNotFoundError  if git is not installed
     * @throws GitNotARepoError  if the path is not a git repository
     * @throws GitError          for other git errors
     */
    public void configureUser(String repoPath, String name, String email, String scope, Integer timeoutMs) throws GitError {
        setConfig(repoPath, "user.name", name, scope, timeoutMs);
        setConfig(repoPath, "user.email", email, scope, timeoutMs);
    }

    /**
     * Set a git configuration value with default scope.
     *
     * @param repoPath the repository working directory
     * @param key      the config key (e.g., {@code "user.name"})
     * @param value    the config value
     * @throws GitError if the operation fails
     * @see #setConfig(String, String, String, String, Integer)
     */
    public void setConfig(String repoPath, String key, String value) throws GitError {
        setConfig(repoPath, key, value, null, null);
    }

    /**
     * Set a git configuration value.
     *
     * <p><b>Example:</b>
     * <pre>{@code
     * session.getGit().setConfig(repoPath,
     *     "core.autocrlf", "input", "local", null);
     * }</pre>
     *
     * @param repoPath  the repository working directory
     * @param key       the config key (e.g., {@code "user.name"})
     * @param value     the config value
     * @param scope     config scope ({@code "local"}, {@code "global"}); may be {@code null}
     * @param timeoutMs timeout in milliseconds; defaults to 30 000
     * @throws GitNotFoundError  if git is not installed
     * @throws GitNotARepoError  if the path is not a git repository
     * @throws GitError          for other git errors
     */
    public void setConfig(String repoPath, String key, String value, String scope, Integer timeoutMs) throws GitError {
        List<String> args = new ArrayList<>();
        args.add("config");
        
        if (scope != null) {
            args.add("--" + scope);
        }
        
        args.add(key);
        args.add(value);
        
        CommandResult result = runGit(args, repoPath, timeoutMs);
        
        if (!result.isSuccess()) {
            throw classifyError("set config", result);
        }
    }

    /**
     * Get a git configuration value with default scope.
     *
     * @param repoPath the repository working directory
     * @param key      the config key
     * @return the config value, or {@code null} if the key is not set
     * @throws GitError if the operation fails
     * @see #getConfig(String, String, String, Integer)
     */
    public String getConfig(String repoPath, String key) throws GitError {
        return getConfig(repoPath, key, null, null);
    }

    /**
     * Get a git configuration value.
     *
     * <p>Returns {@code null} if the key is not found rather than throwing
     * an exception.
     *
     * <p><b>Example:</b>
     * <pre>{@code
     * String userName = session.getGit().getConfig(repoPath,
     *     "user.name", "local", null);
     * System.out.println("User: " + userName);
     * }</pre>
     *
     * @param repoPath  the repository working directory
     * @param key       the config key
     * @param scope     config scope ({@code "local"}, {@code "global"}); may be {@code null}
     * @param timeoutMs timeout in milliseconds; defaults to 30 000
     * @return the config value, or {@code null} if the key is not set
     * @throws GitNotFoundError  if git is not installed
     * @throws GitNotARepoError  if the path is not a git repository
     * @throws GitError          for other git errors
     */
    public String getConfig(String repoPath, String key, String scope, Integer timeoutMs) throws GitError {
        List<String> args = new ArrayList<>();
        args.add("config");
        
        if (scope != null) {
            args.add("--" + scope);
        }
        
        args.add("--get");
        args.add(key);
        
        CommandResult result = runGit(args, repoPath, timeoutMs);
        
        if (!result.isSuccess()) {
            // git config --get exits with code 1 when the key is not found
            String rawStderr = result.getStderr() != null ? result.getStderr().trim().toLowerCase() : "";
            if (result.getExitCode() == 1 && (rawStderr.isEmpty() || rawStderr.contains("key does not contain"))) {
                return null;
            }
            throw classifyError("get config", result);
        }
        
        String value = result.getStdout() != null ? result.getStdout().trim() : "";
        return value.isEmpty() ? null : value;
    }
}
