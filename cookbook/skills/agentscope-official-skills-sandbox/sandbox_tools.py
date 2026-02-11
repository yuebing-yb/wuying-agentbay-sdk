"""
Sandbox toolset for the official-skills AgentScope cookbook.

This module keeps tool definitions separate so `main.py` stays small.

Notes:
- Tool functions must never raise exceptions. Any error should be returned as text.
- Tool outputs are truncated to avoid exceeding model input limits.
"""

from __future__ import annotations

import shlex
from dataclasses import dataclass
from dataclasses import field
from typing import Any, Dict, List, Optional, Tuple

from agentscope.message import TextBlock
from agentscope.tool import ToolResponse


def _preview(text: str, limit: int = 500) -> str:
    t = (text or "").strip()
    if len(t) <= limit:
        return t
    return t[: limit - 3] + "..."


@dataclass
class SandboxToolset:
    agent_bay: Any
    create_session_params_cls: Any
    image_id: str
    skills_root: str
    report_path: str
    max_tool_text_chars: int = 8000
    max_shell_calls: int = 24
    max_write_calls: int = 8

    session: Optional[Any] = None
    read_paths: List[str] = field(default_factory=list)
    report_opened: bool = False
    shell_calls: int = 0
    write_calls: int = 0
    completed_outputs: Dict[str, str] = field(default_factory=dict)

    def __post_init__(self) -> None:
        self.skills_root = (self.skills_root or "").rstrip("/") or "/home/wuying/skills"
        self.report_path = (self.report_path or "").strip() or "/tmp/official_skill_report.md"
        self.report_opened = False

    def _truncate(self, text: str) -> str:
        t = text or ""
        if len(t) <= self.max_tool_text_chars:
            return t
        head = t[: self.max_tool_text_chars - 200]
        return (
            head
            + "\n\n[TRUNCATED] Tool output was too large. "
            "Narrow the request (e.g. smaller max_lines / specific file section) and call the tool again."
        )

    def _resp(self, text: str) -> ToolResponse:
        return ToolResponse(content=[TextBlock(type="text", text=self._truncate(text))])

    def _is_allowed_path(self, p: str) -> bool:
        path = (p or "").strip()
        if not path:
            return False
        if path == "/tmp" or path.startswith("/tmp/"):
            return True
        if path == self.skills_root or path.startswith(f"{self.skills_root}/"):
            return True
        return False

    async def _ensure_session(self) -> Any:
        if self.session is not None:
            return self.session
        print("========== [sandbox] creating session ==========", flush=True)
        print(f"- image_id: {self.image_id}", flush=True)
        print("===============================================", flush=True)
        res = await self.agent_bay.create(params=self.create_session_params_cls(image_id=self.image_id))
        if not res.success or not res.session:
            raise RuntimeError(res.error_message or "Failed to create session")
        self.session = res.session
        return self.session

    def _format_with_line_numbers(self, text: str, start_line: int, max_lines: int) -> str:
        lines = (text or "").splitlines()
        start = max(1, int(start_line))
        limit = max(1, min(int(max_lines), 400))
        end = min(len(lines), start + limit - 1)
        out: List[str] = []
        for i in range(start, end + 1):
            out.append(f"{i:>6} | {lines[i - 1]}")
        return "\n".join(out)

    def _split_first_pipe_outside_quotes(self, cmd: str) -> Tuple[str, str]:
        in_single = False
        in_double = False
        escaped = False
        for i, ch in enumerate(cmd or ""):
            if escaped:
                escaped = False
                continue
            if in_double and ch == "\\":
                escaped = True
                continue
            if not in_double and ch == "'":
                in_single = not in_single
                continue
            if not in_single and ch == '"':
                in_double = not in_double
                continue
            if not in_single and not in_double and ch == "|":
                return (cmd[:i], cmd[i + 1 :])
        return (cmd, "")

    def _scan_redirection_outside_quotes(self, cmd: str) -> Optional[str]:
        s = cmd or ""
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
                if j >= len(s):
                    return None
                if s[j] in ("'", '"'):
                    quote = s[j]
                    j += 1
                    start = j
                    esc = False
                    while j < len(s):
                        cj = s[j]
                        if quote == '"' and not esc and cj == "\\":
                            esc = True
                            j += 1
                            continue
                        if esc:
                            esc = False
                            j += 1
                            continue
                        if cj == quote:
                            return s[start:j]
                        j += 1
                    return None
                start = j
                while j < len(s) and not s[j].isspace():
                    j += 1
                return s[start:j]
            i += 1
        return None

    def _detect_curl_output_target(self, cmd: str) -> Optional[str]:
        curl_segment, _rest = self._split_first_pipe_outside_quotes(cmd or "")
        try:
            tokens = shlex.split(curl_segment, posix=True)
        except ValueError:
            return None
        if not tokens:
            return None
        try:
            curl_idx = tokens.index("curl")
        except ValueError:
            return None
        args = tokens[curl_idx + 1 :]
        for i, tok in enumerate(args):
            if tok == "-o" and i + 1 < len(args):
                target = args[i + 1]
                if target != "/dev/null":
                    return target
            if tok == "-D" and i + 1 < len(args):
                return args[i + 1]
        return None

    def _detect_output_target(self, cmd: str) -> Optional[str]:
        target = self._scan_redirection_outside_quotes(cmd or "")
        if target:
            return target
        return self._detect_curl_output_target(cmd or "")

    async def stat_path(self, path: str) -> ToolResponse:
        print("========== [tool] stat_path ==========", flush=True)
        print(f"args: path={path}", flush=True)
        try:
            normalized = (path or "").strip()
            if not self._is_allowed_path(normalized):
                return self._resp(f"Error: Unsupported path. Use {self.skills_root}/... or /tmp/...")
            session = await self._ensure_session()
            res = await session.file_system.get_file_info(normalized)
            if not res.success:
                return self._resp(res.error_message or "get_file_info failed")
            info = res.file_info or {}
            text = (
                "OK\n"
                f"- path: {normalized}\n"
                f"- exists: {bool(info)}\n"
                f"- isDirectory: {info.get('isDirectory')}\n"
                f"- size: {info.get('size')}\n"
                f"- modifiedTime: {info.get('modifiedTime')}\n"
            )
            print(f"result_preview: {_preview(text)}", flush=True)
            print("====================================", flush=True)
            return self._resp(text)
        except Exception as e:
            text = f"Error: stat_path failed: {e}"
            print(f"result: error={_preview(text)}", flush=True)
            print("====================================", flush=True)
            return self._resp(text)

    async def list_dir(self, path: str) -> ToolResponse:
        print("========== [tool] list_dir ==========", flush=True)
        print(f"args: path={path}", flush=True)
        try:
            normalized = (path or "").strip()
            if not self._is_allowed_path(normalized):
                return self._resp(f"Error: Unsupported path. Use {self.skills_root}/... or /tmp/...")
            session = await self._ensure_session()
            res = await session.file_system.list_directory(normalized)
            if not res.success:
                return self._resp(res.error_message or "list_directory failed")
            entries = res.entries or []
            lines = [f"OK ({len(entries)} entries)"]
            for e in entries[:200]:
                if isinstance(e, dict):
                    name = str(e.get("name", ""))
                    is_dir = bool(e.get("isDirectory", False) or e.get("is_directory", False))
                else:
                    name = str(getattr(e, "name", ""))
                    is_dir = bool(
                        getattr(e, "isDirectory", False)
                        or getattr(e, "is_directory", False)
                        or getattr(e, "is_dir", False)
                    )
                lines.append(f"- {'[DIR]' if is_dir else '[FILE]'} {name}")
            if len(entries) > 200:
                lines.append(f"... truncated, total={len(entries)}")
            text = "\n".join(lines) + "\n"
            print(f"result_preview: {_preview(text)}", flush=True)
            print("===================================", flush=True)
            return self._resp(text)
        except Exception as e:
            text = f"Error: list_dir failed: {e}"
            print(f"result: error={_preview(text)}", flush=True)
            print("===================================", flush=True)
            return self._resp(text)

    async def read_text_file(self, file_path: str, start_line: int = 1, max_lines: int = 400) -> ToolResponse:
        print("========== [tool] read_text_file ==========", flush=True)
        print(f"args: file_path={file_path} start_line={start_line} max_lines={max_lines}", flush=True)
        try:
            normalized = (file_path or "").strip()
            if not self._is_allowed_path(normalized):
                return self._resp(f"Error: Unsupported file_path. Use {self.skills_root}/... or /tmp/...")
            if start_line < 1:
                return self._resp("Error: start_line must be >= 1.")
            if max_lines < 1 or max_lines > 400:
                return self._resp("Error: max_lines must be between 1 and 400.")
            session = await self._ensure_session()
            res = await session.file_system.read_file(normalized, format="text")
            if not res.success:
                return self._resp(res.error_message or "read_file failed")
            content = res.content or ""
            numbered = self._format_with_line_numbers(content, start_line=start_line, max_lines=max_lines)
            lines_total = len(content.splitlines())
            end_line = min(lines_total, start_line + max_lines - 1)
            truncated = ""
            if end_line < lines_total:
                truncated = (
                    f"\n\n[TRUNCATED] File has {lines_total} lines. "
                    f"Showing lines {start_line}-{end_line}. "
                    f"Use start_line={start_line + max_lines} to read more."
                )
            text = (
                f"The content of {normalized} (lines {start_line}-{end_line}):\n```\n"
                f"{numbered}\n```{truncated}"
            )
            self.read_paths.append(normalized)
            if normalized == self.report_path:
                self.report_opened = True
            print(f"result_preview: {_preview(text)}", flush=True)
            print("========================================", flush=True)
            return self._resp(text)
        except Exception as e:
            text = f"Error: read_text_file failed: {e}"
            print(f"result: error={_preview(text)}", flush=True)
            print("========================================", flush=True)
            return self._resp(text)

    async def search_text(
        self,
        file_path: str,
        pattern: str,
        max_matches: int = 20,
        case_insensitive: bool = True,
    ) -> ToolResponse:
        print("========== [tool] search_text ==========", flush=True)
        print(
            f"args: file_path={file_path} pattern_len={len(pattern)} max_matches={max_matches} case_insensitive={case_insensitive}",
            flush=True,
        )
        try:
            normalized = (file_path or "").strip()
            if not self._is_allowed_path(normalized):
                return self._resp(f"Error: Unsupported file_path. Use {self.skills_root}/... or /tmp/...")
            if not pattern:
                return self._resp("Error: pattern must be non-empty.")
            if max_matches < 1 or max_matches > 100:
                return self._resp("Error: max_matches must be between 1 and 100.")
            session = await self._ensure_session()
            res = await session.file_system.read_file(normalized, format="text")
            if not res.success:
                return self._resp(res.error_message or "read_file failed")
            content = res.content or ""
            total_lines = len(content.splitlines())
            total_bytes = len(content.encode("utf-8", errors="replace"))
            needle = pattern.lower() if case_insensitive else pattern
            matches: List[str] = []
            for idx, line in enumerate(content.splitlines(), start=1):
                hay = line.lower() if case_insensitive else line
                if needle in hay:
                    matches.append(f"{idx:>6} | {line}")
                    if len(matches) >= max_matches:
                        break
            header = f"OK ({len(matches)} matches in {total_lines} lines, {total_bytes} bytes)\n"
            text = header + "\n".join([f"- {m}" for m in matches]) + ("\n" if matches else "")
            self.read_paths.append(normalized)
            print(f"result_preview: {_preview(text)}", flush=True)
            print("=====================================", flush=True)
            return self._resp(text)
        except Exception as e:
            text = f"Error: search_text failed: {e}"
            print(f"result: error={_preview(text)}", flush=True)
            print("=====================================", flush=True)
            return self._resp(text)

    async def execute_shell_command(
        self,
        command: str,
        timeout: int = 300,
        cwd: Optional[str] = None,
        **_: Any,
    ) -> ToolResponse:
        print("========== [tool] execute_shell_command ==========", flush=True)
        print(f"args: command={command} timeout={timeout} cwd={cwd}", flush=True)
        try:
            output_target = self._detect_output_target(command or "")
            if output_target and self.completed_outputs.get(output_target) == (command or ""):
                text = (
                    f"[BLOCKED] The same command already created '{output_target}' successfully. "
                    f"Do NOT re-run it. Use read_text_file('{output_target}') to view it. "
                    "This call did NOT count against your shell quota."
                )
                print(f"result: blocked_duplicate target={output_target}", flush=True)
                print("===============================================", flush=True)
                return self._resp(text)

            self.shell_calls += 1
            if self.shell_calls > self.max_shell_calls:
                return self._resp(
                    "Error: Too many execute_shell_command calls in this run. "
                    f"Write the report to {self.report_path} and open it with read_text_file."
                )
            session = await self._ensure_session()
            timeout_ms = int(timeout * 1000)
            res = await session.command.execute_command(command, timeout_ms=timeout_ms, cwd=cwd or "/")
            stdout = res.stdout or res.output or ""
            stderr = res.stderr or ""
            text = f"<returncode>{res.exit_code}</returncode><stdout>{stdout}</stdout><stderr>{stderr}</stderr>"

            if res.exit_code == 0 and output_target:
                self.completed_outputs[output_target] = command
                if not stdout.strip():
                    text += (
                        f"\n[NOTE] Command succeeded but stdout is empty because output was saved to {output_target}. "
                        f"Do NOT re-run this command. Use read_text_file('{output_target}') to view the content."
                    )
            print(f"result_preview: {_preview(text)}", flush=True)
            print("===============================================", flush=True)
            return self._resp(text)
        except Exception as e:
            text = f"Error: execute_shell_command failed: {e}"
            print(f"result: error={_preview(text)}", flush=True)
            print("===============================================", flush=True)
            return self._resp(text)

    async def write_text_file(self, file_path: str, content: str, mode: str = "overwrite") -> ToolResponse:
        print("========== [tool] write_text_file ==========", flush=True)
        print(f"args: file_path={file_path} content_len={len(content)} mode={mode}", flush=True)
        try:
            self.write_calls += 1
            if self.write_calls > self.max_write_calls:
                return self._resp(
                    "Error: Too many write_text_file calls in this run. "
                    f"Open the report with read_text_file('{self.report_path}') and finish."
                )
            normalized = (file_path or "").strip()
            if not normalized.startswith("/tmp/"):
                return self._resp("Error: Only sandbox paths under /tmp are supported.")
            if mode not in ("overwrite", "append"):
                return self._resp("Error: mode must be 'overwrite' or 'append'.")
            session = await self._ensure_session()
            res = await session.file_system.write_file(normalized, content, mode=mode)
            if not res.success:
                return self._resp(res.error_message or "write_file failed")
            action = "Appended to" if mode == "append" else "Wrote"
            text = f"{action} {normalized} successfully."
            print(f"result_preview: {_preview(text)}", flush=True)
            print("===========================================", flush=True)
            return self._resp(text)
        except Exception as e:
            text = f"Error: write_text_file failed: {e}"
            print(f"result: error={_preview(text)}", flush=True)
            print("===========================================", flush=True)
            return self._resp(text)


def register_tools(toolkit: Any, toolset: SandboxToolset) -> None:
    async def stat_path(path: str) -> ToolResponse:
        return await toolset.stat_path(path)

    async def list_dir(path: str) -> ToolResponse:
        return await toolset.list_dir(path)

    async def read_text_file(file_path: str, start_line: int = 1, max_lines: int = 400) -> ToolResponse:
        return await toolset.read_text_file(file_path, start_line=start_line, max_lines=max_lines)

    async def search_text(
        file_path: str,
        pattern: str,
        max_matches: int = 20,
        case_insensitive: bool = True,
    ) -> ToolResponse:
        return await toolset.search_text(
            file_path,
            pattern,
            max_matches=max_matches,
            case_insensitive=case_insensitive,
        )

    async def execute_shell_command(command: str, timeout: int = 300, cwd: str = "/") -> ToolResponse:
        return await toolset.execute_shell_command(command, timeout=timeout, cwd=cwd or "/")

    async def write_text_file(file_path: str, content: str, mode: str = "overwrite") -> ToolResponse:
        return await toolset.write_text_file(file_path, content, mode=mode)

    toolkit.register_tool_function(read_text_file, func_name="read_text_file")
    toolkit.register_tool_function(stat_path, func_name="stat_path")
    toolkit.register_tool_function(list_dir, func_name="list_dir")
    toolkit.register_tool_function(search_text, func_name="search_text")
    toolkit.register_tool_function(execute_shell_command, func_name="execute_shell_command")
    toolkit.register_tool_function(write_text_file, func_name="write_text_file")

