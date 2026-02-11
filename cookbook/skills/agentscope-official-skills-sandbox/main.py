"""
AgentScope + AgentBay Official Skills Sandbox Runtime (E2E cookbook, no mocks).

This entrypoint is intentionally small:
- Scenario selection is controlled by an environment variable.
- Tool implementations live in `sandbox_tools.py`.

Required environment variables:
- AGENTBAY_API_KEY
- DASHSCOPE_API_KEY

Optional:
- AGENTBAY_OFFICIAL_SKILLS_SCENARIO: selects a user-facing prompt scenario.
"""

from __future__ import annotations

import asyncio
import os
import warnings
from typing import Any, List, Optional

os.environ.setdefault("AGENTBAY_LOG_LEVEL", "WARNING")

from official_skill_user_scenarios import get_scenario
from sandbox_tools import SandboxToolset, register_tools


DEFAULT_IMAGE_ID = "linux_latest"
SKILLS_ROOT = "/home/wuying/skills"
MODEL_NAME = "qwen3-max"
MAX_SHELL_CALLS = 24
MAX_WRITE_CALLS = 8
MAX_TOOL_TEXT_CHARS = 8000


def _require_env(name: str) -> str:
    value = os.environ.get(name, "").strip()
    if not value:
        raise RuntimeError(f"{name} is required")
    return value


def _silence_deprecation_warnings() -> None:
    warnings.filterwarnings("ignore", category=DeprecationWarning)
    warnings.simplefilter("ignore", DeprecationWarning)
    warnings.showwarning = lambda *args, **kwargs: None


def _preview(text: str, limit: int = 500) -> str:
    t = (text or "").strip()
    if len(t) <= limit:
        return t
    return t[: limit - 3] + "..."


def _print_block(title: str, text: str) -> None:
    print(f"========== {title} ==========", flush=True)
    if text:
        print(text, flush=True)
    print("================================", flush=True)


def _msg_to_text(m: Any) -> str:
    if m is None:
        return ""
    content = getattr(m, "content", None)
    if isinstance(content, list):
        parts: List[str] = []
        for b in content:
            if isinstance(b, dict):
                if b.get("type") == "text" and isinstance(b.get("text"), str):
                    parts.append(b.get("text"))
                continue
            t = getattr(b, "text", None)
            if isinstance(t, str):
                parts.append(t)
        return "".join(parts)
    return str(m)


def _build_skill_dir(skills_root: str, name: str) -> str:
    n = (name or "").strip().lstrip("/")
    root = (skills_root or "").rstrip("/")
    return f"{root}/{n}" if n else root


def _prompt_requires_report(prompt: str, report_path: str) -> bool:
    p = prompt or ""
    r = report_path or ""
    if not r:
        return False
    return (r in p) and ("write_text_file" in p) and ("read_text_file" in p)


async def main() -> None:
    _silence_deprecation_warnings()
    os.environ.setdefault("AGENTSCOPE_DISABLE_CONSOLE_OUTPUT", "true")

    api_key = _require_env("AGENTBAY_API_KEY")
    dashscope_key = _require_env("DASHSCOPE_API_KEY")

    from agentbay import AsyncAgentBay
    from agentbay._common.params.session_params import CreateSessionParams

    from agentscope.agent import ReActAgent
    from agentscope.formatter import DashScopeChatFormatter
    from agentscope.memory import InMemoryMemory
    from agentscope.message import Msg
    from agentscope.model import DashScopeChatModel
    from agentscope.tool import Toolkit

    scenario_key = os.environ.get("AGENTBAY_OFFICIAL_SKILLS_SCENARIO", "").strip() or "generic"
    scenario = get_scenario(scenario_key)

    skills_root = SKILLS_ROOT
    image_id = DEFAULT_IMAGE_ID
    report_path = scenario.default_report_path

    agent_bay = AsyncAgentBay(api_key=api_key)
    skills = await agent_bay.beta.skills.list_metadata()
    if not skills:
        raise RuntimeError("ListSkillMetaData returned empty list")

    toolkit = Toolkit()
    toolset = SandboxToolset(
        agent_bay=agent_bay,
        create_session_params_cls=CreateSessionParams,
        image_id=image_id,
        skills_root=skills_root,
        report_path=report_path,
        max_tool_text_chars=MAX_TOOL_TEXT_CHARS,
        max_shell_calls=MAX_SHELL_CALLS,
        max_write_calls=MAX_WRITE_CALLS,
    )
    register_tools(toolkit, toolset)

    for s in skills:
        name = str(s.get("name") or "").strip()
        if not name:
            continue
        toolkit.skills[name] = {
            "name": name,
            "description": str(s.get("description") or ""),
            "dir": _build_skill_dir(skills_root, name),
        }

    def _build_agent() -> ReActAgent:
        # Build a fresh agent per attempt to keep the message history short and
        # reduce DashScope tool-call chain errors in long multi-tool scenarios.
        return ReActAgent(
            name="Friday",
            max_iters=20,
            sys_prompt=(
                "你是一个可以在云端沙箱中执行任务的 AI 助手。\n"
                "当你决定使用某个 skill 时，请先用 read_text_file 读取该 skill 目录下的 SKILL.md 了解正确用法。\n"
                "重要：不要假设 skill 的挂载根路径。请严格使用 skill list 中提供的 dir 作为起点。\n"
                "当你要进行文件系统操作时，优先使用 stat_path / list_dir / read_text_file / search_text。\n"
                "当你需要分析网页内容时，优先把响应保存到 /tmp 下的文件，再用 read_text_file/search_text 进行提取与引用；避免在 shell 管道里反复 grep。\n"
                "注意：执行 shell 命令有严格超时与配额限制，尽量使用短命令并复用落盘结果。\n"
                "重要分析原则：\n"
                "- 当你已经通过 read_text_file 确认文件有内容，但 search_text 对某个关键词返回 0 matches 时，\n"
                "  说明该关键词在文件中确实不存在——这本身就是一个有价值的分析发现，而不是工具故障。\n"
                "- 请始终基于你实际获取到的数据进行分析，不要因为某些预期内容不存在就放弃分析或退化为通用模板。\n"
                "- 缺失的内容恰恰是最重要的发现，应该作为问题明确指出。\n"
                f"硬性要求：最终必须在沙箱中生成文件 {report_path}，并且在结束前调用 read_text_file 打开它。\n"
            ),
            model=DashScopeChatModel(
                api_key=dashscope_key,
                model_name=MODEL_NAME,
                enable_thinking=False,
                stream=True,
            ),
            formatter=DashScopeChatFormatter(),
            toolkit=toolkit,
            memory=InMemoryMemory(),
        )

    user_prompt = (
        f"{scenario.user_prompt}\n\n"
        "请你自行选择合适的 skills 并完成任务。\n"
        f"最后请在沙箱中写入完整报告到 {report_path}（用 write_text_file），然后用 read_text_file 打开它自检。\n"
        "完成后给出中文摘要，并包含报告的绝对路径。\n"
    )
    _print_block("[llm] input", user_prompt)

    async def _invoke_and_verify(prompt: str) -> List[str]:
        toolset.report_opened = False
        toolset.shell_calls = 0
        toolset.write_calls = 0
        toolset.read_paths = []

        expects_report = _prompt_requires_report(prompt, report_path)

        agent = _build_agent()
        try:
            resp = await agent(Msg("user", prompt, "user"))
        except RuntimeError as e:
            msg = str(e)
            if "tool_calls" in msg and "tool_call_id" in msg and "did not have response messages" in msg:
                print("[llm] DashScope tool-call chain error, retrying with a fresh agent.", flush=True)
                agent = _build_agent()
                resp = await agent(Msg("user", prompt, "user"))
            else:
                raise
        _print_block("[llm] output", _msg_to_text(resp))

        session = toolset.session
        if session is None:
            return ["Session was not created (the model did not call any sandbox tool)."]

        content = ""
        if expects_report:
            try:
                v = await session.file_system.read_file(report_path, format="text")
                content = (v.content or "").strip() if v.success else ""
            except Exception as e:
                print(f"[verify] read report failed: {e}", flush=True)

        missing: List[str] = []
        if expects_report and not content:
            missing.append(f"Report file `{report_path}` is empty or missing.")
        if not any(p.endswith("/SKILL.md") for p in toolset.read_paths):
            missing.append("No SKILL.md was read via tools.")
        if expects_report and not toolset.report_opened:
            missing.append(f"Report was not opened via read_text_file('{report_path}').")
        return missing

    missing = await _invoke_and_verify(user_prompt)
    if missing:
        followup = (
            "你刚才的输出没有通过校验。请严格按要求补齐，必须真实调用工具。\n"
            "请补齐：\n"
            "- 读取你选择的 skill 的 SKILL.md（read_text_file）\n"
            f"- 一次性调用 write_text_file 写入完整的 {report_path}\n"
            f"- 调用 read_text_file 打开 {report_path}\n"
            "- 最后给出中文摘要，并给出报告文件绝对路径\n\n"
            "当前缺失项：\n- "
            + "\n- ".join(missing)
        )
        missing2 = await _invoke_and_verify(followup)
        if missing2:
            raise RuntimeError("Verification failed:\n- " + "\n- ".join(missing2))

    session = toolset.session
    if session is None:
        raise RuntimeError("Session is missing after agent run")
    v = await session.file_system.read_file(report_path, format="text")
    report_content = (v.content or "").strip() if v.success else ""
    if report_content:
        print("========== [Cookbook] Report Preview ==========")
        print(_preview(report_content, limit=1200))
        print("===============================================")
    else:
        raise RuntimeError(v.error_message or f"Report not found: {report_path}")
    await session.delete()


if __name__ == "__main__":
    asyncio.run(main())

