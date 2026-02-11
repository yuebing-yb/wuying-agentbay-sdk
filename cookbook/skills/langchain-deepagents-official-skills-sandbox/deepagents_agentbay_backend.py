from __future__ import annotations

import time
from dataclasses import dataclass
from typing import Any, Dict, List, Optional, Tuple

try:
    from deepagents.backends.protocol import SandboxBackendProtocol  # type: ignore[import-not-found]
except Exception:  # pragma: no cover
    SandboxBackendProtocol = object  # type: ignore[misc,assignment]


@dataclass
class PocEvent:
    ts_ms: int
    kind: str
    detail: str


def _now_ms() -> int:
    return int(time.time() * 1000)


def _preview(text: str, n: int = 160) -> str:
    t = (text or "").replace("\n", "\\n")
    if len(t) <= n:
        return t
    return t[: n - 3] + "..."


def _normalize_posix_path(path: str) -> str:
    p = (path or "").strip().replace("\\", "/")
    if not p:
        return "/"
    if not p.startswith("/"):
        p = "/" + p.lstrip("./")
    if p != "/" and p.endswith("/"):
        p = p.rstrip("/")
    return p or "/"


def _preview_text(text: str, limit: int = 500) -> str:
    t = (text or "").strip()
    if len(t) <= limit:
        return t
    return t[: limit - 3] + "..."


def _format_with_line_numbers(text: str, start_line: int, max_lines: int) -> str:
    lines = (text or "").splitlines()
    start = max(1, int(start_line))
    limit = max(1, min(int(max_lines), 400))
    end = min(len(lines), start + limit - 1)
    out: List[str] = []
    for i in range(start, end + 1):
        out.append(f"{i:>6} | {lines[i - 1]}")
    return "\n".join(out)


def _detect_redirect_target(command: str) -> Optional[str]:
    """
    Best-effort output redirection detection for "cmd > /tmp/file".
    (Used only to mimic the cookbook log note.)
    """
    s = command or ""
    in_single = False
    in_double = False
    escaped = False
    i = 0
    while i < len(s):
        ch = s[i]
        if escaped:
            escaped = False
            i += 1
            continue
        if in_double and ch == "\\":
            escaped = True
            i += 1
            continue
        if not in_double and ch == "'":
            in_single = not in_single
            i += 1
            continue
        if not in_single and ch == '"':
            in_double = not in_double
            i += 1
            continue
        if not in_single and not in_double and ch == ">":
            j = i + 1
            if j < len(s) and s[j] == ">":
                j += 1
            while j < len(s) and s[j].isspace():
                j += 1
            start = j
            while j < len(s) and not s[j].isspace():
                j += 1
            target = s[start:j].strip()
            return target or None
        i += 1
    return None


class AgentBayDeepagentsBackend(SandboxBackendProtocol):
    """
    DeepAgents backend backed by AgentBay official skills sandbox image.

    Design:
    - Virtual skill paths are exposed as `/skills/<name>/...` to the agent.
    - Official skills are mounted in the sandbox at `${skills_root}/<name>/...`.
    - Session is lazily created on first sandbox access.
    """

    def __init__(
        self,
        *,
        agent_bay: Any,
        skills_metadata: List[Dict[str, str]],
        image_id: str,
        skills_root: str,
        report_path: str,
        trace: bool = True,
    ) -> None:
        self._agent_bay = agent_bay
        self._skills_metadata = list(skills_metadata or [])
        self._image_id = (image_id or "").strip()
        self._skills_root = (skills_root or "").rstrip("/") or "/home/wuying/skills"
        self._report_path = (report_path or "").strip() or "/tmp/official_skill_report.md"
        self._trace = trace

        self._session: Optional[Any] = None
        self._events: List[PocEvent] = []

        self.read_paths: List[str] = []
        self.report_opened: bool = False
        self._created_session_logged: bool = False

    @property
    def id(self) -> str:
        return "agentbay-deepagents-official-skills-backend"

    @property
    def session(self) -> Optional[Any]:
        return self._session

    def events(self) -> List[PocEvent]:
        return list(self._events)

    def _emit(self, kind: str, detail: str) -> None:
        e = PocEvent(ts_ms=_now_ms(), kind=kind, detail=detail)
        self._events.append(e)

    def _print(self, text: str) -> None:
        if not self._trace:
            return
        print(text, flush=True)

    def _print_tool_header(self, name: str) -> None:
        self._print(f"========== [tool] {name} ==========")

    def _print_tool_footer(self) -> None:
        self._print("=====================================")

    def _print_result_preview(self, text: str) -> None:
        self._print(f"result_preview: {_preview_text(text)}")

    def _ensure_session(self) -> Any:
        if self._session is not None:
            return self._session
        if not self._created_session_logged:
            self._print("========== [sandbox] creating session ==========")
            self._print(f"- image_id: {self._image_id}")
            self._print("===============================================")
            self._created_session_logged = True
        from agentbay._common.params.session_params import CreateSessionParams

        params = CreateSessionParams(image_id=self._image_id)
        res = self._agent_bay.create(params=params)
        if not getattr(res, "success", False) or not getattr(res, "session", None):
            raise RuntimeError(getattr(res, "error_message", "") or "Failed to create AgentBay session")
        self._session = res.session
        return self._session

    def close(self) -> None:
        if self._session is None:
            return
        try:
            self._session.delete()
        finally:
            self._session = None

    def _virtual_to_sandbox_path(self, p: str) -> str:
        path = _normalize_posix_path(p)
        if path == "/skills" or path.startswith("/skills/"):
            rest = path[len("/skills") :]
            return f"{self._skills_root}{rest}"
        return path

    def _is_allowed_path(self, p: str) -> bool:
        path = _normalize_posix_path(p)
        if path == "/tmp" or path.startswith("/tmp/"):
            return True
        root = _normalize_posix_path(self._skills_root)
        if path == root or path.startswith(root + "/"):
            return True
        if path == "/skills" or path.startswith("/skills/"):
            return True
        return False

    def ls_info(self, path: str):
        p = _normalize_posix_path(path)
        skills_root = _normalize_posix_path(self._skills_root)
        if p == skills_root:
            out = []
            for s in self._skills_metadata:
                name = str((s or {}).get("name") or "").strip()
                if not name:
                    continue
                out.append({"path": f"{skills_root}/{name}", "is_dir": True})
            return out
        if p == "/skills":
            out = []
            for s in self._skills_metadata:
                name = str((s or {}).get("name") or "").strip()
                if not name:
                    continue
                out.append({"path": f"/skills/{name}", "is_dir": True})
            return out

        sp = self._virtual_to_sandbox_path(p)
        s = self._ensure_session()
        res = s.file_system.list_directory(sp)
        if not getattr(res, "success", False):
            return []

        out = []
        base_virtual = p.rstrip("/")
        for item in getattr(res, "entries", []) or []:
            if isinstance(item, dict):
                name = str(item.get("name", "") or "")
                is_dir = bool(item.get("isDirectory", False) or item.get("is_directory", False))
            else:
                name = str(getattr(item, "name", "") or getattr(item, "Name", "") or "")
                is_dir = bool(
                    getattr(item, "isDirectory", False)
                    or getattr(item, "is_directory", False)
                    or getattr(item, "is_dir", False)
                )
            if not name:
                continue
            out.append({"path": f"{base_virtual}/{name}".rstrip("/"), "is_dir": is_dir})
        return out

    def read(self, file_path: str, offset: int = 0, limit: int = 2000) -> str:
        p = _normalize_posix_path(file_path)
        self._print_tool_header("read_file")
        start_line = max(1, int(offset) + 1)
        max_lines = max(1, min(int(limit), 400))
        self._print(f"args: file_path={p} start_line={start_line} max_lines={max_lines}")
        if not self._is_allowed_path(p):
            text = f"Error: Unsupported file_path. Use {self._skills_root}/... or /tmp/..."
            self._print_result_preview(text)
            self._print_tool_footer()
            return text
        sp = self._virtual_to_sandbox_path(p)
        s = self._ensure_session()
        r = s.file_system.read_file(sp, format="text")
        if not getattr(r, "success", False):
            text = f"Error: File '{p}' not found"
            self._print_result_preview(text)
            self._print_tool_footer()
            return text
        content = getattr(r, "content", "") or ""
        self.read_paths.append(p)
        if p == self._report_path:
            self.report_opened = True
        numbered = _format_with_line_numbers(content, start_line=start_line, max_lines=max_lines)
        total_lines = len(content.splitlines())
        end_line = min(total_lines, start_line + max_lines - 1)
        truncated = ""
        if end_line < total_lines:
            truncated = (
                f"\n\n[TRUNCATED] File has {total_lines} lines. "
                f"Showing lines {start_line}-{end_line}. "
                f"Use start_line={start_line + max_lines} to read more."
            )
        text = (
            f"The content of {p} (lines {start_line}-{end_line}):\n```\n"
            f"{numbered}\n```{truncated}"
        )
        self._print_result_preview(text)
        self._print_tool_footer()
        return text

    def write(self, file_path: str, content: str):
        from deepagents.backends.protocol import WriteResult  # type: ignore[import-not-found]

        p = _normalize_posix_path(file_path)
        self._print_tool_header("write_file")
        self._print(f"args: file_path={p} content_len={len(content)} mode=overwrite")
        if not p.startswith("/tmp/"):
            text = "Error: Only sandbox paths under /tmp are supported."
            self._print_result_preview(text)
            self._print_tool_footer()
            return WriteResult(error=text)
        sp = self._virtual_to_sandbox_path(p)
        s = self._ensure_session()
        r = s.file_system.write_file(sp, content, mode="overwrite")
        if not getattr(r, "success", False):
            text = getattr(r, "error_message", "") or "write failed"
            self._print_result_preview(text)
            self._print_tool_footer()
            return WriteResult(error=text)
        text = f"Wrote {p} successfully."
        self._print_result_preview(text)
        self._print_tool_footer()
        return WriteResult(path=p, files_update=None)

    def execute(self, command: str):
        from deepagents.backends.protocol import ExecuteResponse  # type: ignore[import-not-found]

        cmd = (command or "").strip()
        self._print_tool_header("execute")
        self._print(f"args: command={cmd} timeout=300 cwd=/")
        if not cmd:
            text = "Error: command must be non-empty."
            self._print_result_preview(text)
            self._print_tool_footer()
            return ExecuteResponse(output=text, exit_code=2, truncated=False)
        s = self._ensure_session()
        r = s.command.execute_command(cmd, timeout_ms=50000, cwd="/")
        out = getattr(r, "stdout", "") or getattr(r, "output", "") or ""
        err = getattr(r, "stderr", "") or ""
        combined = out + (("\n" + err) if err else "")
        text = (
            f"<returncode>{getattr(r, 'exit_code', None)}</returncode>"
            f"<stdout>{out}</stdout><stderr>{err}</stderr>"
        )
        target = _detect_redirect_target(cmd)
        if getattr(r, "exit_code", None) == 0 and target and not out.strip():
            text += (
                f"\n[NOTE] Command succeeded but stdout is empty because output was saved to {target}. "
                f"Do NOT re-run this command. Use read_file('{target}') to view the content."
            )
        self._print_result_preview(text)
        self._print_tool_footer()
        return ExecuteResponse(output=combined, exit_code=getattr(r, "exit_code", None), truncated=False)

    def edit(self, file_path: str, old_string: str, new_string: str, replace_all: bool = False):
        from deepagents.backends.protocol import EditResult  # type: ignore[import-not-found]

        p = _normalize_posix_path(file_path)
        sp = self._virtual_to_sandbox_path(p)
        s = self._ensure_session()
        r = s.file_system.read_file(sp, format="text")
        if not getattr(r, "success", False):
            return EditResult(error="Error: File not found")
        original = getattr(r, "content", "") or ""
        if old_string not in original:
            return EditResult(error="Error: String not found")
        if (not replace_all) and original.count(old_string) != 1:
            return EditResult(error="Error: Multiple occurrences found")
        updated = original.replace(old_string, new_string) if replace_all else original.replace(old_string, new_string, 1)
        w = s.file_system.write_file(sp, updated, mode="overwrite")
        if not getattr(w, "success", False):
            return EditResult(error=getattr(w, "error_message", "") or "edit failed")
        occurrences = original.count(old_string)
        return EditResult(path=p, files_update=None, occurrences=occurrences)

    def download_files(self, paths: List[str]):
        from deepagents.backends.protocol import FileDownloadResponse  # type: ignore[import-not-found]

        out: List[FileDownloadResponse] = []
        for raw in paths:
            p = _normalize_posix_path(raw)
            sp = self._virtual_to_sandbox_path(p)
            s = self._ensure_session()
            r = s.file_system.read_file(sp, format="text")
            if not getattr(r, "success", False):
                out.append(FileDownloadResponse(path=p, content=None, error="file_not_found"))
                continue
            content = (getattr(r, "content", "") or "").encode("utf-8", errors="replace")
            out.append(FileDownloadResponse(path=p, content=content, error=None))
            self.read_paths.append(p)
        return out

    def upload_files(self, files: List[Tuple[str, bytes]]):
        from deepagents.backends.protocol import FileUploadResponse  # type: ignore[import-not-found]

        out: List[FileUploadResponse] = []
        s = self._ensure_session()
        for path, content in files:
            p = _normalize_posix_path(path)
            if not p.startswith("/tmp/"):
                out.append(FileUploadResponse(path=p, error="permission_denied"))
                continue
            sp = self._virtual_to_sandbox_path(p)
            text = content.decode("utf-8", errors="replace")
            r = s.file_system.write_file(sp, text, mode="overwrite")
            if getattr(r, "success", False):
                out.append(FileUploadResponse(path=p, error=None))
            else:
                out.append(FileUploadResponse(path=p, error="write_failed"))
        return out

