package com.aliyun.agentbay.git;

import com.aliyun.agentbay.model.CommandResult;
import com.aliyun.agentbay.service.BaseService;
import com.aliyun.agentbay.session.Session;

import java.util.*;
import java.util.regex.Matcher;
import java.util.regex.Pattern;

public class Git extends BaseService {
    private volatile Boolean gitAvailable = null;
    private static final Map<String, String> DEFAULT_GIT_ENV;
    static {
        Map<String, String> env = new HashMap<>();
        env.put("GIT_TERMINAL_PROMPT", "0");
        DEFAULT_GIT_ENV = Collections.unmodifiableMap(env);
    }
    // Default timeout for git operations (30 seconds)
    private static final int DEFAULT_GIT_TIMEOUT_MS = 30000;
    // Default timeout for clone operations (5 minutes, as clone may download large repos)
    private static final int DEFAULT_CLONE_TIMEOUT_MS = 300000;

    // Pre-compiled patterns for parsing git output
    private static final Pattern AHEAD_PATTERN = Pattern.compile("ahead\\s+(\\d+)");
    private static final Pattern BEHIND_PATTERN = Pattern.compile("behind\\s+(\\d+)");
    private static final Pattern COMMIT_HASH_PATTERN = Pattern.compile("\\[\\w+(?:\\s+\\([^)]+\\))?\\s+([a-f0-9]+)\\]");

    public Git(Session session) {
        super(session);
    }

    // ==================== Private Helper Methods ====================

    private String shellEscape(String arg) {
        if (arg == null) return "''";
        return "'" + arg.replace("'", "'\\''") + "'";
    }

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

    private CommandResult runGit(List<String> args, String repoPath, Integer timeoutMs) throws GitError {
        ensureGitAvailable();
        String cmd = buildGitCommand(args, repoPath);
        int timeout = timeoutMs != null ? timeoutMs : DEFAULT_GIT_TIMEOUT_MS;
        return session.getCommand().executeCommand(cmd, timeout, null, DEFAULT_GIT_ENV);
    }

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

    private GitError classifyError(String operation, CommandResult result) {
        String stderr = result.getStderr() != null ? result.getStderr().toLowerCase() : "";
        String stdout = result.getStdout() != null ? result.getStdout().toLowerCase() : "";
        
        if (stderr.contains("authentication") || stderr.contains("permission denied") || 
            stderr.contains("invalid credentials") || stderr.contains("could not read username")) {
            return new GitAuthError(operation + " failed: authentication error", result.getExitCode(), result.getStderr());
        }
        
        if (stderr.contains("not a git repository") || stderr.contains("does not appear to be a git repository") ||
            stdout.contains("not a git repository")) {
            return new GitNotARepoError(operation + " failed: not a git repository", result.getExitCode(), result.getStderr());
        }
        
        if (stderr.contains("conflict") || stdout.contains("conflict") ||
            stderr.contains("failed to merge") || stdout.contains("failed to merge")) {
            return new GitConflictError(operation + " failed: merge conflict", result.getExitCode(), result.getStderr());
        }
        
        if (result.getExitCode() == 127) {
            return new GitNotFoundError(operation + " failed: command not found", result.getExitCode(), result.getStderr());
        }
        
        return new GitError(operation + " failed", result.getExitCode(), result.getStderr());
    }

    private String deriveRepoDirFromUrl(String url) {
        String name = url;
        if (name.endsWith(".git")) {
            name = name.substring(0, name.length() - 4);
        }
        int lastSlash = name.lastIndexOf('/');
        if (lastSlash >= 0) {
            name = name.substring(lastSlash + 1);
        }
        return name;
    }

    private String deriveStatus(String indexStatus, String workTreeStatus) {
        String combined = (indexStatus != null ? indexStatus : "") + (workTreeStatus != null ? workTreeStatus : "");
        if (combined.contains("U")) return "conflict";
        if (combined.contains("R")) return "renamed";
        if (combined.contains("C")) return "copied";
        if (combined.contains("D")) return "deleted";
        if (combined.contains("A")) return "added";
        if (combined.contains("M")) return "modified";
        if (combined.contains("T")) return "typechange";
        if (combined.contains("?")) return "untracked";
        return "unknown";
    }

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

    public GitCloneResult clone(String url) throws GitError {
        return clone(url, null, null, null, null);
    }

    public GitCloneResult clone(String url, String path, String branch, Integer depth, Integer timeoutMs) throws GitError {
        List<String> args = new ArrayList<>();
        args.add("clone");
        
        if (branch != null) {
            args.add("-b");
            args.add(branch);
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

    public GitInitResult init(String path) throws GitError {
        return init(path, null, false, null);
    }

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

    public void add(String repoPath) throws GitError {
        add(repoPath, null, true, null);
    }

    public void add(String repoPath, List<String> files, boolean all, Integer timeoutMs) throws GitError {
        List<String> args = new ArrayList<>();
        args.add("add");
        
        if (all) {
            args.add("--all");
        }
        
        if (files != null && !files.isEmpty()) {
            // Use -- separator to prevent filenames from being interpreted as options
            args.add("--");
            args.addAll(files);
        }
        
        CommandResult result = runGit(args, repoPath, timeoutMs);
        
        if (!result.isSuccess()) {
            throw classifyError("add", result);
        }
    }

    public GitCommitResult commit(String repoPath, String message) throws GitError {
        return commit(repoPath, message, null, null, false, null);
    }

    public GitCommitResult commit(String repoPath, String message, String authorName, String authorEmail, boolean allowEmpty, Integer timeoutMs) throws GitError {
        List<String> args = new ArrayList<>();
        args.add("commit");
        args.add("-m");
        args.add(message);
        
        if (authorName != null && authorEmail != null) {
            args.add("--author=" + authorName + " <" + authorEmail + ">");
        }
        
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

    public GitStatusResult status(String repoPath) throws GitError {
        return status(repoPath, null);
    }

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

    public GitLogResult log(String repoPath) throws GitError {
        return log(repoPath, null, null);
    }

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

    public GitBranchListResult listBranches(String repoPath) throws GitError {
        return listBranches(repoPath, null);
    }

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

    public void createBranch(String repoPath, String branch) throws GitError {
        createBranch(repoPath, branch, true, null);
    }

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

    public void checkoutBranch(String repoPath, String branch) throws GitError {
        checkoutBranch(repoPath, branch, null);
    }

    public void checkoutBranch(String repoPath, String branch, Integer timeoutMs) throws GitError {
        List<String> args = new ArrayList<>();
        args.add("checkout");
        args.add(branch);
        
        CommandResult result = runGit(args, repoPath, timeoutMs);
        
        if (!result.isSuccess()) {
            throw classifyError("checkout", result);
        }
    }

    public void deleteBranch(String repoPath, String branch) throws GitError {
        deleteBranch(repoPath, branch, false, null);
    }

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

    public void remoteAdd(String repoPath, String name, String url) throws GitError {
        remoteAdd(repoPath, name, url, false, false, null);
    }

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

    public String remoteGet(String repoPath, String name) throws GitError {
        return remoteGet(repoPath, name, null);
    }

    public String remoteGet(String repoPath, String name, Integer timeoutMs) throws GitError {
        List<String> args = new ArrayList<>();
        args.add("remote");
        args.add("get-url");
        args.add(name);
        
        CommandResult result = runGit(args, repoPath, timeoutMs);
        
        if (!result.isSuccess()) {
            throw classifyError("remote get-url", result);
        }
        
        return result.getStdout().trim();
    }

    public void reset(String repoPath) throws GitError {
        reset(repoPath, null, null, null, null);
    }

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

    public void restore(String repoPath, List<String> paths) throws GitError {
        restore(repoPath, paths, false, null, null, null);
    }

    public void restore(String repoPath, List<String> paths, boolean staged, Boolean worktree, String source, Integer timeoutMs) throws GitError {
        // Validate: at least one path must be specified
        if (paths == null || paths.isEmpty()) {
            throw new GitError("git restore requires at least one path", -1, "");
        }
        
        List<String> args = new ArrayList<>();
        args.add("restore");
        
        if (staged) {
            args.add("--staged");
        }
        
        if (worktree != null && worktree) {
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

    public void pull(String repoPath) throws GitError {
        pull(repoPath, null, null, null);
    }

    public void pull(String repoPath, String remote, String branch, Integer timeoutMs) throws GitError {
        List<String> args = new ArrayList<>();
        args.add("pull");
        
        if (remote != null) {
            args.add(remote);
            if (branch != null) {
                args.add(branch);
            }
        }
        
        CommandResult result = runGit(args, repoPath, timeoutMs);
        
        if (!result.isSuccess()) {
            throw classifyError("pull", result);
        }
    }

    public void configureUser(String repoPath, String name, String email) throws GitError {
        configureUser(repoPath, name, email, null, null);
    }

    public void configureUser(String repoPath, String name, String email, String scope, Integer timeoutMs) throws GitError {
        setConfig(repoPath, "user.name", name, scope, timeoutMs);
        setConfig(repoPath, "user.email", email, scope, timeoutMs);
    }

    public void setConfig(String repoPath, String key, String value) throws GitError {
        setConfig(repoPath, key, value, null, null);
    }

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

    public String getConfig(String repoPath, String key) throws GitError {
        return getConfig(repoPath, key, null, null);
    }

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
            throw classifyError("get config", result);
        }
        
        return result.getStdout().trim();
    }
}
