"""
Unit tests for AsyncGit module.

This module contains comprehensive unit tests for:
- Private helper methods (_shell_escape, _build_git_command, _get_stdout, _get_stderr)
- URL derivation (_derive_repo_dir_from_url)
- Status derivation (_derive_status)
- Parsing methods (_parse_git_status, _parse_git_log, _parse_git_branches)
- Error classification (_classify_error)
- Git availability check (_ensure_git_available)
- All public API methods (clone, init, add, commit, status, log, etc.)
"""

import unittest

import pytest
from unittest.mock import MagicMock, MagicMock

from agentbay._sync.git.git import SyncGit
from agentbay._common.exceptions import (
    GitAuthError,
    GitConflictError,
    GitError,
    GitNotARepoError,
    GitNotFoundError,
)
from agentbay._common.models.command import CommandResult
from agentbay._common.models.git import (
    GitBranchListResult,
    GitCloneResult,
    GitCommitResult,
    GitInitResult,
    GitLogResult,
    GitStatusResult,
)


# ---------------------------------------------------------------------------
# Test infrastructure
# ---------------------------------------------------------------------------


class DummySession:
    """Minimal mock session for AsyncGit unit tests."""

    def __init__(self):
        self.command = MagicMock()
        self.command.execute_command = MagicMock()


def _ok(stdout="", stderr="", output="", exit_code=0):
    """Build a successful CommandResult."""
    return CommandResult(
        success=True,
        stdout=stdout,
        stderr=stderr,
        output=output,
        exit_code=exit_code,
    )


def _fail(stderr="", exit_code=1, output="", error_message=""):
    """Build a failed CommandResult."""
    return CommandResult(
        success=False,
        stderr=stderr,
        exit_code=exit_code,
        output=output,
        error_message=error_message,
    )


# =========================================================================
# 1.2 Private helper tests
# =========================================================================


class TestAsyncGitHelpers(unittest.TestCase):
    """Tests for static / instance helper methods."""

    # -- _shell_escape -----------------------------------------------------

    def test_shell_escape_plain(self):
        assert SyncGit._shell_escape("hello") == "'hello'"

    def test_shell_escape_single_quote(self):
        assert SyncGit._shell_escape("it's") == "'it'\\''s'"

    def test_shell_escape_spaces(self):
        assert SyncGit._shell_escape("hello world") == "'hello world'"

    def test_shell_escape_empty(self):
        assert SyncGit._shell_escape("") == "''"

    # -- _build_git_command ------------------------------------------------

    def test_build_git_command_no_repo_path(self):
        session = DummySession()
        git = SyncGit(session)
        cmd = git._build_git_command(["status", "--porcelain"])
        assert cmd == "git 'status' '--porcelain'"

    def test_build_git_command_with_repo_path(self):
        session = DummySession()
        git = SyncGit(session)
        cmd = git._build_git_command(["log"], "/tmp/repo")
        assert cmd == "git -C '/tmp/repo' 'log'"

    def test_build_git_command_multiple_args(self):
        session = DummySession()
        git = SyncGit(session)
        cmd = git._build_git_command(["commit", "-m", "init"], "/repo")
        assert cmd == "git -C '/repo' 'commit' '-m' 'init'"

    # -- _get_stdout / _get_stderr -----------------------------------------

    def test_get_stdout_prefers_stdout(self):
        r = CommandResult(stdout="from-stdout", output="from-output")
        assert SyncGit._get_stdout(r) == "from-stdout"

    def test_get_stdout_fallback_to_output(self):
        r = CommandResult(stdout="", output="from-output")
        assert SyncGit._get_stdout(r) == "from-output"

    def test_get_stdout_all_empty(self):
        r = CommandResult(stdout="", output="")
        assert SyncGit._get_stdout(r) == ""

    def test_get_stderr_prefers_stderr(self):
        r = CommandResult(stderr="from-stderr", error_message="from-err")
        assert SyncGit._get_stderr(r) == "from-stderr"

    def test_get_stderr_fallback_to_error_message(self):
        r = CommandResult(stderr="", error_message="from-err")
        assert SyncGit._get_stderr(r) == "from-err"

    def test_get_stderr_all_empty(self):
        r = CommandResult(stderr="", error_message="")
        assert SyncGit._get_stderr(r) == ""

    # -- _derive_repo_dir_from_url -----------------------------------------

    def test_derive_repo_https(self):
        url = "https://github.com/user/my-repo.git"
        assert SyncGit._derive_repo_dir_from_url(url) == "my-repo"

    def test_derive_repo_ssh(self):
        url = "git@github.com:user/my-repo.git"
        assert SyncGit._derive_repo_dir_from_url(url) == "my-repo"

    def test_derive_repo_no_git_suffix(self):
        url = "https://github.com/user/my-repo"
        assert SyncGit._derive_repo_dir_from_url(url) == "my-repo"

    def test_derive_repo_trailing_slash(self):
        url = "https://github.com/user/my-repo.git/"
        assert SyncGit._derive_repo_dir_from_url(url) == "my-repo"

    def test_derive_repo_plain_name(self):
        assert SyncGit._derive_repo_dir_from_url("repo") == "repo"

    def test_derive_repo_url_encoded(self):
        assert SyncGit._derive_repo_dir_from_url(
            "https://github.com/user/my%20repo.git"
        ) == "my repo"

    # -- _derive_status ----------------------------------------------------

    def test_derive_status_conflict(self):
        assert SyncGit._derive_status("U", " ") == "conflict"

    def test_derive_status_renamed(self):
        assert SyncGit._derive_status("R", " ") == "renamed"

    def test_derive_status_copied(self):
        assert SyncGit._derive_status("C", " ") == "copied"

    def test_derive_status_deleted(self):
        assert SyncGit._derive_status("D", " ") == "deleted"

    def test_derive_status_added(self):
        assert SyncGit._derive_status("A", " ") == "added"

    def test_derive_status_modified(self):
        assert SyncGit._derive_status(" ", "M") == "modified"

    def test_derive_status_typechange(self):
        assert SyncGit._derive_status("T", " ") == "typechange"

    def test_derive_status_untracked(self):
        assert SyncGit._derive_status("?", "?") == "untracked"

    def test_derive_status_unknown(self):
        assert SyncGit._derive_status(" ", " ") == "unknown"


# =========================================================================
# 1.3 Parser tests
# =========================================================================


class TestAsyncGitParsers(unittest.TestCase):
    """Tests for _parse_git_status, _parse_git_log, _parse_git_branches."""

    # -- _parse_git_status -------------------------------------------------

    def test_parse_status_empty(self):
        result = SyncGit._parse_git_status("")
        assert result.is_clean
        assert result.current_branch is None

    def test_parse_status_branch_only(self):
        result = SyncGit._parse_git_status("## main")
        assert result.current_branch == "main"
        assert result.is_clean

    def test_parse_status_with_upstream(self):
        result = SyncGit._parse_git_status("## main...origin/main")
        assert result.current_branch == "main"
        assert result.upstream == "origin/main"

    def test_parse_status_ahead_behind(self):
        result = SyncGit._parse_git_status("## main...origin/main [ahead 2, behind 3]")
        assert result.ahead == 2
        assert result.behind == 3

    def test_parse_status_untracked(self):
        output = "## main\n?? new-file.txt"
        result = SyncGit._parse_git_status(output)
        assert len(result.files) == 1
        f = result.files[0]
        assert f.path == "new-file.txt"
        assert f.status == "untracked"
        assert not f.staged

    def test_parse_status_added(self):
        output = "## main\nA  staged.txt"
        result = SyncGit._parse_git_status(output)
        assert len(result.files) == 1
        f = result.files[0]
        assert f.path == "staged.txt"
        assert f.status == "added"
        assert f.staged

    def test_parse_status_modified_worktree(self):
        output = "## main\n M modified.txt"
        result = SyncGit._parse_git_status(output)
        f = result.files[0]
        assert f.status == "modified"
        assert not f.staged

    def test_parse_status_deleted(self):
        output = "## main\nD  deleted.txt"
        result = SyncGit._parse_git_status(output)
        f = result.files[0]
        assert f.status == "deleted"
        assert f.staged

    def test_parse_status_renamed(self):
        output = "## main\nR  old.txt -> new.txt"
        result = SyncGit._parse_git_status(output)
        f = result.files[0]
        assert f.status == "renamed"
        assert f.path == "new.txt"
        assert f.renamed_from == "old.txt"

    def test_parse_status_conflict(self):
        output = "## main\nUU conflicted.txt"
        result = SyncGit._parse_git_status(output)
        f = result.files[0]
        assert f.status == "conflict"
        assert result.has_conflicts

    def test_parse_status_detached_head(self):
        result = SyncGit._parse_git_status("## HEAD (detached at abc1234)")
        assert result.detached
        assert result.current_branch is None

    def test_parse_status_no_commits_yet(self):
        result = SyncGit._parse_git_status("## No commits yet on main")
        assert result.current_branch == "main"

    def test_parse_status_mixed(self):
        output = (
            "## main...origin/main [ahead 1]\n"
            "A  added.txt\n"
            " M modified.txt\n"
            "?? untracked.txt"
        )
        result = SyncGit._parse_git_status(output)
        assert result.current_branch == "main"
        assert result.ahead == 1
        assert len(result.files) == 3
        assert result.has_staged
        assert result.has_untracked
        assert result.staged_count == 1
        assert result.untracked_count == 1

    def test_parse_status_properties(self):
        output = "## main\nA  a.txt\n M b.txt\n?? c.txt\nUU d.txt"
        result = SyncGit._parse_git_status(output)
        assert result.has_changes
        assert result.total_count == 4
        assert result.staged_count == 2  # A and UU both have staged index
        assert result.conflict_count == 1

    # -- _parse_git_log ----------------------------------------------------

    def test_parse_log_empty(self):
        result = SyncGit._parse_git_log("")
        assert len(result.entries) == 0

    def test_parse_log_single(self):
        record = (
            "abc123\x01abc1\x01Alice\x01alice@x.com\x012024-01-01\x01init commit\x00"
        )
        result = SyncGit._parse_git_log(record)
        assert len(result.entries) == 1
        e = result.entries[0]
        assert e.hash == "abc123"
        assert e.short_hash == "abc1"
        assert e.author_name == "Alice"
        assert e.author_email == "alice@x.com"
        assert e.message == "init commit"

    def test_parse_log_multiple(self):
        records = (
            "aaa\x01a1\x01A\x01a@x\x01d1\x01msg1\x00"
            "bbb\x01b1\x01B\x01b@x\x01d2\x01msg2\x00"
        )
        result = SyncGit._parse_git_log(records)
        assert len(result.entries) == 2

    def test_parse_log_special_chars(self):
        record = "abc\x01ab\x01A\x01a@x\x01d\x01feat: add 'quotes' & <angle>\x00"
        result = SyncGit._parse_git_log(record)
        assert "quotes" in result.entries[0].message

    # -- _parse_git_branches -----------------------------------------------

    def test_parse_branches_empty(self):
        result = SyncGit._parse_git_branches("")
        assert len(result.branches) == 0
        assert result.current == ""

    def test_parse_branches_single_current(self):
        output = "main\t*"
        result = SyncGit._parse_git_branches(output)
        assert len(result.branches) == 1
        assert result.branches[0].name == "main"
        assert result.branches[0].is_current
        assert result.current == "main"

    def test_parse_branches_multiple(self):
        output = "main\t*\ndev\t \nfeature/x\t "
        result = SyncGit._parse_git_branches(output)
        assert len(result.branches) == 3
        assert result.current == "main"
        assert not result.branches[1].is_current

    def test_parse_branches_skip_detached(self):
        output = "(HEAD detached at abc1234)\t*\nmain\t "
        result = SyncGit._parse_git_branches(output)
        assert len(result.branches) == 1
        assert result.branches[0].name == "main"


# =========================================================================
# 1.4 Error classification tests
# =========================================================================


class TestAsyncGitClassifyError(unittest.TestCase):
    """Tests for _classify_error method."""

    def setUp(self):
        self.session = DummySession()
        self.git = SyncGit(self.session)

    def test_auth_error_authentication_failed(self):
        r = _fail(stderr="fatal: Authentication failed for 'url'")
        err = self.git._classify_error("clone", r)
        assert isinstance(err, GitAuthError)
        assert err.exit_code == 1

    def test_auth_error_could_not_read_username(self):
        r = _fail(stderr="fatal: could not read Username")
        err = self.git._classify_error("push", r)
        assert isinstance(err, GitAuthError)

    def test_auth_error_invalid_credentials(self):
        r = _fail(stderr="remote: Invalid credentials")
        err = self.git._classify_error("fetch", r)
        assert isinstance(err, GitAuthError)

    def test_auth_error_access_denied(self):
        r = _fail(stderr="access denied")
        err = self.git._classify_error("clone", r)
        assert isinstance(err, GitAuthError)

    def test_auth_error_permission_denied(self):
        r = _fail(stderr="Permission denied (publickey)")
        err = self.git._classify_error("clone", r)
        assert isinstance(err, GitAuthError)

    def test_auth_error_403(self):
        r = _fail(stderr="The requested URL returned error: 403")
        err = self.git._classify_error("clone", r)
        assert isinstance(err, GitAuthError)

    def test_not_a_repo_error(self):
        r = _fail(stderr="fatal: not a git repository", exit_code=128)
        err = self.git._classify_error("status", r)
        assert isinstance(err, GitNotARepoError)
        assert err.exit_code == 128

    def test_not_a_repo_does_not_appear(self):
        r = _fail(stderr="does not appear to be a git repository")
        err = self.git._classify_error("clone", r)
        assert isinstance(err, GitNotARepoError)

    def test_conflict_error(self):
        r = _fail(stderr="CONFLICT (content): Merge conflict in file.txt")
        err = self.git._classify_error("pull", r)
        assert isinstance(err, GitConflictError)

    def test_not_found_command_not_found(self):
        r = _fail(stderr="bash: git: command not found", exit_code=127)
        err = self.git._classify_error("clone", r)
        assert isinstance(err, GitNotFoundError)

    def test_not_found_git_not_found(self):
        r = _fail(stderr="git: not found", exit_code=127)
        err = self.git._classify_error("clone", r)
        assert isinstance(err, GitNotFoundError)

    def test_not_found_exit_127(self):
        r = _fail(stderr="some error", exit_code=127)
        err = self.git._classify_error("clone", r)
        assert isinstance(err, GitNotFoundError)

    def test_generic_error(self):
        r = _fail(stderr="fatal: something unexpected", exit_code=1)
        err = self.git._classify_error("commit", r)
        assert isinstance(err, GitError)
        assert not isinstance(err, GitAuthError)
        assert not isinstance(err, GitNotARepoError)
        assert "exit code 1" in str(err)

    def test_classify_preserves_stderr(self):
        r = _fail(stderr="original stderr text", exit_code=42)
        err = self.git._classify_error("test_op", r)
        assert err.stderr == "original stderr text"
        assert err.exit_code == 42


# =========================================================================
# 1.5 _ensure_git_available tests
# =========================================================================


class TestAsyncGitAvailability(unittest.TestCase):
    """Tests for _ensure_git_available."""

    @pytest.mark.sync
    def test_git_available_success(self):
        session = DummySession()
        git = SyncGit(session)
        session.command.execute_command.return_value = _ok(stdout="git version 2.39.0")
        git._ensure_git_available()
        assert git._git_available is True

    @pytest.mark.sync
    def test_git_available_cached(self):
        session = DummySession()
        git = SyncGit(session)
        git._git_available = True
        git._ensure_git_available()
        # Should not call execute_command when cached
        session.command.execute_command.assert_not_called()

    @pytest.mark.sync
    def test_git_not_available(self):
        session = DummySession()
        git = SyncGit(session)
        session.command.execute_command.return_value = _fail(
            stderr="git: not found", exit_code=127
        )
        with pytest.raises(GitNotFoundError):
            git._ensure_git_available()
        assert git._git_available is False


# =========================================================================
# 1.6 Public API tests
# =========================================================================


class TestAsyncGitClone(unittest.TestCase):
    """Tests for clone()."""

    def setUp(self):
        self.session = DummySession()
        self.git = SyncGit(self.session)
        self.git._git_available = True  # skip availability check

    @pytest.mark.sync
    def test_clone_basic(self):
        self.session.command.execute_command.return_value = _ok()
        result = self.git.clone("https://github.com/user/repo.git")
        assert isinstance(result, GitCloneResult)
        assert result.path == "repo"
        cmd = self.session.command.execute_command.call_args[0][0]
        assert "clone" in cmd
        assert "'https://github.com/user/repo.git'" in cmd

    @pytest.mark.sync
    def test_clone_with_path(self):
        self.session.command.execute_command.return_value = _ok()
        result = self.git.clone(
            "https://github.com/user/repo.git", path="/tmp/my-repo"
        )
        assert result.path == "/tmp/my-repo"

    @pytest.mark.sync
    def test_clone_with_branch_and_depth(self):
        self.session.command.execute_command.return_value = _ok()
        self.git.clone("https://github.com/user/repo.git", branch="main", depth=1)
        cmd = self.session.command.execute_command.call_args[0][0]
        assert "'--branch'" in cmd
        assert "'main'" in cmd
        assert "'--single-branch'" in cmd
        assert "'--depth'" in cmd
        assert "'1'" in cmd

    @pytest.mark.sync
    def test_clone_default_timeout(self):
        self.session.command.execute_command.return_value = _ok()
        self.git.clone("https://github.com/user/repo.git")
        kwargs = self.session.command.execute_command.call_args[1]
        assert kwargs["timeout_ms"] == 300000

    @pytest.mark.sync
    def test_clone_custom_timeout(self):
        self.session.command.execute_command.return_value = _ok()
        self.git.clone("https://github.com/user/repo.git", timeout_ms=600000)
        kwargs = self.session.command.execute_command.call_args[1]
        assert kwargs["timeout_ms"] == 600000

    @pytest.mark.sync
    def test_clone_env(self):
        self.session.command.execute_command.return_value = _ok()
        self.git.clone("https://github.com/user/repo.git")
        kwargs = self.session.command.execute_command.call_args[1]
        assert kwargs["envs"] == {"GIT_TERMINAL_PROMPT": "0", "LC_ALL": "C"}

    @pytest.mark.sync
    def test_clone_auth_error(self):
        self.session.command.execute_command.return_value = _fail(
            stderr="fatal: Authentication failed"
        )
        with pytest.raises(GitAuthError):
            self.git.clone("https://github.com/user/private.git")
    @pytest.mark.sync
    def test_clone_depth_zero(self):
        """depth=0 is falsy, should NOT add --depth flag."""
        self.session.command.execute_command.return_value = _ok()
        self.git.clone("https://github.com/user/repo.git", depth=0)
        cmd = self.session.command.execute_command.call_args[0][0]
        assert "'--depth'" not in cmd

    @pytest.mark.sync
    def test_clone_depth_negative(self):
        """Negative depth is truthy, will be passed to git."""
        self.session.command.execute_command.return_value = _ok()
        self.git.clone("https://github.com/user/repo.git", depth=-1)
        cmd = self.session.command.execute_command.call_args[0][0]
        assert "'--depth'" in cmd
        assert "'-1'" in cmd

    @pytest.mark.sync
    def test_clone_generic_error(self):
        self.session.command.execute_command.return_value = _fail(
            stderr="fatal: some error"
        )
        with pytest.raises(GitError):
            self.git.clone("https://github.com/user/repo.git")

class TestAsyncGitInit(unittest.TestCase):
    """Tests for init()."""

    def setUp(self):
        self.session = DummySession()
        self.git = SyncGit(self.session)
        self.git._git_available = True

    @pytest.mark.sync
    def test_init_basic(self):
        self.session.command.execute_command.return_value = _ok()
        result = self.git.init("/tmp/repo")
        assert isinstance(result, GitInitResult)
        assert result.path == "/tmp/repo"
        cmd = self.session.command.execute_command.call_args[0][0]
        assert "'init'" in cmd
        assert "'/tmp/repo'" in cmd

    @pytest.mark.sync
    def test_init_with_initial_branch(self):
        self.session.command.execute_command.return_value = _ok()
        self.git.init("/tmp/repo", initial_branch="main")
        cmd = self.session.command.execute_command.call_args[0][0]
        assert "'--initial-branch'" in cmd
        assert "'main'" in cmd

    @pytest.mark.sync
    def test_init_bare(self):
        self.session.command.execute_command.return_value = _ok()
        self.git.init("/tmp/repo", bare=True)
        cmd = self.session.command.execute_command.call_args[0][0]
        assert "'--bare'" in cmd

    @pytest.mark.sync
    def test_init_failure(self):
        self.session.command.execute_command.return_value = _fail(stderr="fatal: error")
        with pytest.raises(GitError):
            self.git.init("/tmp/repo")


class TestAsyncGitAdd(unittest.TestCase):
    """Tests for add()."""

    def setUp(self):
        self.session = DummySession()
        self.git = SyncGit(self.session)
        self.git._git_available = True

    @pytest.mark.sync
    def test_add_stage_all_default(self):
        self.session.command.execute_command.return_value = _ok()
        self.git.add("/repo")
        cmd = self.session.command.execute_command.call_args[0][0]
        assert "'-A'" in cmd

    @pytest.mark.sync
    def test_add_specific_files(self):
        self.session.command.execute_command.return_value = _ok()
        self.git.add("/repo", files=["a.txt", "b.txt"])
        cmd = self.session.command.execute_command.call_args[0][0]
        assert "'--'" in cmd
        assert "'a.txt'" in cmd
        assert "'b.txt'" in cmd

    @pytest.mark.sync
    def test_add_stage_all_false(self):
        self.session.command.execute_command.return_value = _ok()
        self.git.add("/repo", stage_all=False)
        cmd = self.session.command.execute_command.call_args[0][0]
        assert "'.'" in cmd
        assert "'-A'" not in cmd

    @pytest.mark.sync
    def test_add_not_a_repo(self):
        self.session.command.execute_command.return_value = _fail(
            stderr="fatal: not a git repository", exit_code=128
        )
        with pytest.raises(GitNotARepoError):
            self.git.add("/not-a-repo")


class TestAsyncGitCommit(unittest.TestCase):
    """Tests for commit()."""

    def setUp(self):
        self.session = DummySession()
        self.git = SyncGit(self.session)
        self.git._git_available = True

    @pytest.mark.sync
    def test_commit_basic(self):
        self.session.command.execute_command.return_value = _ok(
            stdout="[main abc1234] initial commit"
        )
        result = self.git.commit("/repo", "initial commit")
        assert isinstance(result, GitCommitResult)
        assert result.commit_hash == "abc1234"

    @pytest.mark.sync
    def test_commit_with_author(self):
        self.session.command.execute_command.return_value = _ok(
            stdout="[main def5678] test"
        )
        self.git.commit(
            "/repo",
            "test",
            author_name="Bot",
            author_email="bot@test.com",
        )
        cmd = self.session.command.execute_command.call_args[0][0]
        assert "'-c'" in cmd
        assert "'user.name=Bot'" in cmd
        assert "'user.email=bot@test.com'" in cmd

    @pytest.mark.sync
    def test_commit_allow_empty(self):
        self.session.command.execute_command.return_value = _ok(
            stdout="[main 111aaaa] empty"
        )
        self.git.commit("/repo", "empty", allow_empty=True)
        cmd = self.session.command.execute_command.call_args[0][0]
        assert "'--allow-empty'" in cmd
    @pytest.mark.sync
    def test_commit_message_with_single_quotes(self):
        """Verify single quotes in commit message are properly escaped."""
        self.session.command.execute_command.return_value = _ok(
            stdout="[main aaa1111] fix: handle 'quoted' case"
        )
        self.git.commit("/repo", "fix: handle 'quoted' case")
        cmd = self.session.command.execute_command.call_args[0][0]
        assert "'fix: handle '\\''quoted'\\'' case'" in cmd

    @pytest.mark.sync
    def test_commit_failure(self):
        self.session.command.execute_command.return_value = _fail(
            stderr="nothing to commit"
        )
        with pytest.raises(GitError):
            self.git.commit("/repo", "msg")

class TestAsyncGitStatus(unittest.TestCase):
    """Tests for status()."""

    def setUp(self):
        self.session = DummySession()
        self.git = SyncGit(self.session)
        self.git._git_available = True

    @pytest.mark.sync
    def test_status_clean(self):
        self.session.command.execute_command.return_value = _ok(stdout="## main")
        result = self.git.status("/repo")
        assert isinstance(result, GitStatusResult)
        assert result.current_branch == "main"
        assert result.is_clean

    @pytest.mark.sync
    def test_status_with_changes(self):
        self.session.command.execute_command.return_value = _ok(
            stdout="## main\n?? new.txt\nA  added.txt"
        )
        result = self.git.status("/repo")
        assert len(result.files) == 2
        assert result.has_untracked
        assert result.has_staged

    @pytest.mark.sync
    def test_status_not_a_repo(self):
        self.session.command.execute_command.return_value = _fail(
            stderr="fatal: not a git repository", exit_code=128
        )
        with pytest.raises(GitNotARepoError):
            self.git.status("/not-a-repo")


class TestAsyncGitLog(unittest.TestCase):
    """Tests for log()."""

    def setUp(self):
        self.session = DummySession()
        self.git = SyncGit(self.session)
        self.git._git_available = True

    @pytest.mark.sync
    def test_log_default(self):
        record = "abc\x01ab\x01A\x01a@x\x01d\x01msg\x00"
        self.session.command.execute_command.return_value = _ok(stdout=record)
        result = self.git.log("/repo")
        assert isinstance(result, GitLogResult)
        assert len(result.entries) == 1

    @pytest.mark.sync
    def test_log_max_count(self):
        self.session.command.execute_command.return_value = _ok(stdout="")
        self.git.log("/repo", max_count=5)
        cmd = self.session.command.execute_command.call_args[0][0]
        assert "'--max-count'" in cmd
        assert "'5'" in cmd

    @pytest.mark.sync
    def test_log_failure(self):
        self.session.command.execute_command.return_value = _fail(
            stderr="fatal: not a git repository"
        )
        with pytest.raises(GitError):
            self.git.log("/repo")


class TestAsyncGitBranches(unittest.TestCase):
    """Tests for list_branches, create_branch, checkout_branch, delete_branch."""

    def setUp(self):
        self.session = DummySession()
        self.git = SyncGit(self.session)
        self.git._git_available = True

    @pytest.mark.sync
    def test_list_branches(self):
        self.session.command.execute_command.return_value = _ok(
            stdout="main\t*\ndev\t "
        )
        result = self.git.list_branches("/repo")
        assert isinstance(result, GitBranchListResult)
        assert result.current == "main"
        assert len(result.branches) == 2

    @pytest.mark.sync
    def test_list_branches_failure(self):
        self.session.command.execute_command.return_value = _fail(
            stderr="fatal: not a git repository"
        )
        with pytest.raises(GitError):
            self.git.list_branches("/repo")

    @pytest.mark.sync
    def test_create_branch_checkout(self):
        self.session.command.execute_command.return_value = _ok()
        self.git.create_branch("/repo", "feature/x")
        cmd = self.session.command.execute_command.call_args[0][0]
        assert "'checkout'" in cmd
        assert "'-b'" in cmd
        assert "'feature/x'" in cmd

    @pytest.mark.sync
    def test_create_branch_no_checkout(self):
        self.session.command.execute_command.return_value = _ok()
        self.git.create_branch("/repo", "feature/x", checkout=False)
        cmd = self.session.command.execute_command.call_args[0][0]
        assert "'branch'" in cmd
        assert "'feature/x'" in cmd
        assert "'-b'" not in cmd

    @pytest.mark.sync
    def test_create_branch_failure(self):
        self.session.command.execute_command.return_value = _fail(
            stderr="fatal: a branch named 'x' already exists"
        )
        with pytest.raises(GitError):
            self.git.create_branch("/repo", "x")

    @pytest.mark.sync
    def test_checkout_branch(self):
        self.session.command.execute_command.return_value = _ok()
        self.git.checkout_branch("/repo", "main")
        cmd = self.session.command.execute_command.call_args[0][0]
        assert "'checkout'" in cmd
        assert "'main'" in cmd

    @pytest.mark.sync
    def test_checkout_branch_failure(self):
        self.session.command.execute_command.return_value = _fail(
            stderr="error: pathspec 'nonexistent' did not match"
        )
        with pytest.raises(GitError):
            self.git.checkout_branch("/repo", "nonexistent")

    @pytest.mark.sync
    def test_delete_branch_default(self):
        self.session.command.execute_command.return_value = _ok()
        self.git.delete_branch("/repo", "old-branch")
        cmd = self.session.command.execute_command.call_args[0][0]
        assert "'-d'" in cmd
        assert "'old-branch'" in cmd

    @pytest.mark.sync
    def test_delete_branch_force(self):
        self.session.command.execute_command.return_value = _ok()
        self.git.delete_branch("/repo", "old-branch", force=True)
        cmd = self.session.command.execute_command.call_args[0][0]
        assert "'-D'" in cmd

    @pytest.mark.sync
    def test_delete_branch_failure(self):
        self.session.command.execute_command.return_value = _fail(
            stderr="error: cannot delete branch"
        )
        with pytest.raises(GitError):
            self.git.delete_branch("/repo", "main")


class TestAsyncGitRemote(unittest.TestCase):
    """Tests for remote_add and remote_get."""

    def setUp(self):
        self.session = DummySession()
        self.git = SyncGit(self.session)
        self.git._git_available = True

    @pytest.mark.sync
    def test_remote_add_basic(self):
        self.session.command.execute_command.return_value = _ok()
        self.git.remote_add("/repo", "origin", "https://github.com/user/repo.git")
        cmd = self.session.command.execute_command.call_args[0][0]
        assert "'remote'" in cmd
        assert "'add'" in cmd
        assert "'origin'" in cmd

    @pytest.mark.sync
    def test_remote_add_with_fetch(self):
        self.session.command.execute_command.return_value = _ok()
        self.git.remote_add(
            "/repo", "origin", "https://github.com/user/repo.git", fetch=True
        )
        cmd = self.session.command.execute_command.call_args[0][0]
        assert "'-f'" in cmd

    @pytest.mark.sync
    def test_remote_add_overwrite(self):
        self.session.command.execute_command.return_value = _ok()
        self.git.remote_add(
            "/repo",
            "origin",
            "https://github.com/user/repo.git",
            overwrite=True,
        )
        cmd = self.session.command.execute_command.call_args[0][0]
        # overwrite mode uses shell fallback: add || set-url
        assert "||" in cmd

    @pytest.mark.sync
    def test_remote_add_overwrite_with_fetch(self):
        self.session.command.execute_command.return_value = _ok()
        self.git.remote_add(
            "/repo",
            "origin",
            "https://github.com/user/repo.git",
            overwrite=True,
            fetch=True,
        )
        cmd = self.session.command.execute_command.call_args[0][0]
        assert "||" in cmd
        assert "'fetch'" in cmd

    @pytest.mark.sync
    def test_remote_add_failure(self):
        self.session.command.execute_command.return_value = _fail(
            stderr="fatal: remote origin already exists"
        )
        with pytest.raises(GitError):
            self.git.remote_add("/repo", "origin", "url")

    @pytest.mark.sync
    def test_remote_get_success(self):
        self.session.command.execute_command.return_value = _ok(
            stdout="https://github.com/user/repo.git\n"
        )
        url = self.git.remote_get("/repo", "origin")
        assert url == "https://github.com/user/repo.git"

    @pytest.mark.sync
    def test_remote_get_not_exist(self):
        self.session.command.execute_command.return_value = _fail(
            stderr="fatal: No such remote 'nonexistent'"
        )
        result = self.git.remote_get("/repo", "nonexistent")
        assert result is None

    @pytest.mark.sync
    def test_remote_get_other_error(self):
        self.session.command.execute_command.return_value = _fail(
            stderr="fatal: not a git repository"
        )
        with pytest.raises(GitError):
            self.git.remote_get("/repo", "origin")

    @pytest.mark.sync
    def test_reset_invalid_mode(self):
        """Verify invalid reset mode raises ValueError before any git call."""
        with pytest.raises(ValueError, match="Invalid reset mode"):
            self.git.reset("/repo", mode="invalid")
        # Ensure no git command was executed
        self.session.command.execute_command.assert_not_called()

    @pytest.mark.sync
    def test_reset_failure(self):
        self.session.command.execute_command.return_value = _fail(stderr="fatal: error")
        with pytest.raises(GitError):
            self.git.reset("/repo")

    @pytest.mark.sync
    def test_reset_modes(self):
        for mode in ("soft", "mixed", "hard", "merge", "keep"):
            self.session.command.execute_command.return_value = _ok()
            self.git.reset("/repo", mode=mode)
            cmd = self.session.command.execute_command.call_args[0][0]
            assert f"'--{mode}'" in cmd

    @pytest.mark.sync
    def test_reset_with_target(self):
        self.session.command.execute_command.return_value = _ok()
        self.git.reset("/repo", mode="hard", target="HEAD~2")
        cmd = self.session.command.execute_command.call_args[0][0]
        assert "'--hard'" in cmd
        assert "'HEAD~2'" in cmd

class TestAsyncGitRestore(unittest.TestCase):
    """Tests for restore()."""

    def setUp(self):
        self.session = DummySession()
        self.git = SyncGit(self.session)
        self.git._git_available = True

    @pytest.mark.sync
    def test_restore_worktree_default(self):
        self.session.command.execute_command.return_value = _ok()
        self.git.restore("/repo", ["file.txt"])
        cmd = self.session.command.execute_command.call_args[0][0]
        assert "'restore'" in cmd
        assert "'--worktree'" in cmd
        assert "'file.txt'" in cmd

    @pytest.mark.sync
    def test_restore_staged(self):
        self.session.command.execute_command.return_value = _ok()
        self.git.restore("/repo", ["file.txt"], staged=True)
        cmd = self.session.command.execute_command.call_args[0][0]
        assert "'--staged'" in cmd
        # worktree should not be set when staged=True and worktree=None
        assert "'--worktree'" not in cmd

    @pytest.mark.sync
    def test_restore_staged_and_worktree(self):
        self.session.command.execute_command.return_value = _ok()
        self.git.restore("/repo", ["file.txt"], staged=True, worktree=True)
        cmd = self.session.command.execute_command.call_args[0][0]
        assert "'--staged'" in cmd
        assert "'--worktree'" in cmd

    @pytest.mark.sync
    def test_restore_with_source(self):
        self.session.command.execute_command.return_value = _ok()
        self.git.restore("/repo", ["file.txt"], source="HEAD~1")
        cmd = self.session.command.execute_command.call_args[0][0]
        assert "'--source'" in cmd
        assert "'HEAD~1'" in cmd

    @pytest.mark.sync
    def test_restore_failure(self):
        self.session.command.execute_command.return_value = _fail(stderr="fatal: error")
        with pytest.raises(GitError):
            self.git.restore("/repo", ["file.txt"])


class TestAsyncGitPull(unittest.TestCase):
    """Tests for pull()."""

    def setUp(self):
        self.session = DummySession()
        self.git = SyncGit(self.session)
        self.git._git_available = True

    @pytest.mark.sync
    def test_pull_default(self):
        self.session.command.execute_command.return_value = _ok()
        self.git.pull("/repo")
        cmd = self.session.command.execute_command.call_args[0][0]
        assert "'pull'" in cmd

    @pytest.mark.sync
    def test_pull_with_remote_and_branch(self):
        self.session.command.execute_command.return_value = _ok()
        self.git.pull("/repo", remote="origin", branch="main")
        cmd = self.session.command.execute_command.call_args[0][0]
        assert "'origin'" in cmd
        assert "'main'" in cmd

    @pytest.mark.sync
    def test_pull_conflict(self):
        self.session.command.execute_command.return_value = _fail(
            stderr="CONFLICT (content): Merge conflict in file.txt"
        )
        with pytest.raises(GitConflictError):
            self.git.pull("/repo")

    @pytest.mark.sync
    def test_pull_default_timeout(self):
        self.session.command.execute_command.return_value = _ok()
        self.git.pull("/repo")
        kwargs = self.session.command.execute_command.call_args[1]
        assert kwargs["timeout_ms"] == 120000


class TestAsyncGitConfig(unittest.TestCase):
    """Tests for configure_user, set_config, get_config."""

    def setUp(self):
        self.session = DummySession()
        self.git = SyncGit(self.session)
        self.git._git_available = True

    @pytest.mark.sync
    def test_configure_user_global(self):
        self.session.command.execute_command.return_value = _ok()
        self.git.configure_user("/repo", "Alice", "alice@x.com")
        calls = self.session.command.execute_command.call_args_list
        assert len(calls) == 2
        name_cmd = calls[0][0][0]
        email_cmd = calls[1][0][0]
        assert "'--global'" in name_cmd
        assert "'user.name'" in name_cmd
        assert "'Alice'" in name_cmd
        assert "'user.email'" in email_cmd
        assert "'alice@x.com'" in email_cmd

    @pytest.mark.sync
    def test_configure_user_local(self):
        self.session.command.execute_command.return_value = _ok()
        self.git.configure_user("/repo", "Alice", "alice@x.com", scope="local")
        cmd = self.session.command.execute_command.call_args_list[0][0][0]
        assert "'--local'" in cmd

    @pytest.mark.sync
    def test_configure_user_name_failure(self):
        self.session.command.execute_command.return_value = _fail(stderr="error")
        with pytest.raises(GitError):
            self.git.configure_user("/repo", "Alice", "alice@x.com")

    @pytest.mark.sync
    def test_configure_user_email_failure(self):
        self.session.command.execute_command.side_effect = [
            _ok(),
            _fail(stderr="error setting email"),
        ]
        with pytest.raises(GitError):
            self.git.configure_user("/repo", "Alice", "alice@x.com")

    @pytest.mark.sync
    def test_set_config_global(self):
        self.session.command.execute_command.return_value = _ok()
        self.git.set_config("/repo", "core.autocrlf", "false")
        cmd = self.session.command.execute_command.call_args[0][0]
        assert "'--global'" in cmd
        assert "'core.autocrlf'" in cmd
        assert "'false'" in cmd

    @pytest.mark.sync
    def test_set_config_local(self):
        self.session.command.execute_command.return_value = _ok()
        self.git.set_config("/repo", "core.autocrlf", "false", scope="local")
        cmd = self.session.command.execute_command.call_args[0][0]
        assert "'--local'" in cmd

    @pytest.mark.sync
    def test_set_config_failure(self):
        self.session.command.execute_command.return_value = _fail(stderr="error")
        with pytest.raises(GitError):
            self.git.set_config("/repo", "k", "v")

    @pytest.mark.sync
    def test_get_config_success(self):
        self.session.command.execute_command.return_value = _ok(stdout="false\n")
        val = self.git.get_config("/repo", "core.autocrlf")
        assert val == "false"

    @pytest.mark.sync
    def test_get_config_not_found_exit1_no_stderr(self):
        self.session.command.execute_command.return_value = _fail(
            stderr="", exit_code=1
        )
        val = self.git.get_config("/repo", "nonexistent.key")
        assert val is None

    @pytest.mark.sync
    def test_get_config_not_found_key_does_not_contain(self):
        self.session.command.execute_command.return_value = _fail(
            stderr="key does not contain a section", exit_code=1
        )
        val = self.git.get_config("/repo", "bad-key")
        assert val is None

    @pytest.mark.sync
    def test_get_config_other_error(self):
        self.session.command.execute_command.return_value = _fail(
            stderr="fatal: not in a git directory", exit_code=128
        )
        with pytest.raises(GitError):
            self.git.get_config("/repo", "user.name")
