"""
LangChain DeepAgents + AgentBay Official Skills Sandbox Runtime (E2E cookbook, no mocks).

This entrypoint is intentionally small:
- Scenario selection is controlled by an environment variable.
- DeepAgents backend implementation lives in `deepagents_agentbay_backend.py`.

Required environment variables:
- AGENTBAY_API_KEY
- DASHSCOPE_API_KEY

Optional:
- AGENTBAY_OFFICIAL_SKILLS_SCENARIO: selects a user-facing prompt scenario.
"""

from __future__ import annotations

import os
import sys
import warnings
from typing import Any, Dict, List

os.environ.setdefault("AGENTBAY_LOG_LEVEL", "WARNING")

from deepagents_agentbay_backend import AgentBayDeepagentsBackend
from official_skill_user_scenarios import get_scenario


DEFAULT_IMAGE_ID = "imgc-0ab5ta4n50mtv1sut"
SKILLS_ROOT = "/home/wuying/skills"
MODEL_NAME = "qwen3-max"


def _require_env(name: str) -> str:
    value = os.environ.get(name, "").strip()
    if not value:
        raise RuntimeError(f"{name} is required")
    return value


def _silence_deprecation_warnings() -> None:
    warnings.filterwarnings("ignore", category=DeprecationWarning)
    warnings.simplefilter("ignore", DeprecationWarning)
    warnings.showwarning = lambda *args, **kwargs: None


def _print_block(title: str, text: str) -> None:
    print(f"========== {title} ==========", flush=True)
    if text:
        print(text, flush=True)
    print("================================", flush=True)


def _ensure_deepagents_importable() -> None:
    try:
        import deepagents  # type: ignore[import-not-found]  # noqa: F401
        return
    except Exception:
        pass

    repo = os.getenv("DEEPAGENTS_PATH", "").strip()
    if not repo:
        raise RuntimeError(
            "deepagents is not installed and DEEPAGENTS_PATH is not set. "
            "Please install deepagents or set DEEPAGENTS_PATH to the local checkout path."
        )
    if os.path.isdir(repo) and repo not in sys.path:
        sys.path.insert(0, repo)


def _msg_to_text(result: Dict[str, Any]) -> str:
    msgs = result.get("messages", [])
    if not isinstance(msgs, list):
        return ""
    parts: List[str] = []
    for m in msgs:
        mtype = getattr(m, "type", None) or getattr(m, "__class__", type("x", (), {})).__name__
        if isinstance(mtype, str) and mtype != "ai":
            continue
        content = getattr(m, "content", None)
        if isinstance(content, str) and content.strip():
            parts.append(content.strip())
    return "\n\n".join(parts)


def _build_skills_catalog_text(items: List[Dict[str, str]]) -> str:
    def _build_skill_dir(skills_root: str, name: str) -> str:
        n = (name or "").strip().lstrip("/")
        root = (skills_root or "").rstrip("/")
        return f"{root}/{n}" if n else root

    lines = ["Available skills (from backend metadata):"]
    for it in items:
        name = str((it or {}).get("name") or "").strip()
        if not name:
            continue
        desc = str((it or {}).get("description") or "").strip()
        dir_path = _build_skill_dir(SKILLS_ROOT, name)
        if desc:
            lines.append(f"- {name}")
            lines.append(f"  - description: {desc}")
            lines.append(f"  - dir: {dir_path}")
        else:
            lines.append(f"- {name}")
            lines.append(f"  - dir: {dir_path}")
    return "\n".join(lines).strip() + "\n"


def _build_system_prompt(skills_catalog_text: str, report_path: str) -> str:
    return (
        "你是一个可以在云端沙箱中执行任务的 AI 助手。\n"
        "你可以使用 sandbox 工具读取文件、写文件、执行命令。\n"
        "当你决定使用某个 skill 时，请先读取该 skill 目录下的 SKILL.md 了解正确用法。\n"
        "重要：不要假设 skill 的挂载根路径。请严格使用 skills list 中提供的 dir 作为起点。\n"
        "当你需要运行脚本/命令时，请使用 execute 工具。\n"
        "当你需要读取文件时，请使用 read_file 工具。\n"
        "当你需要写入报告时，请使用 write_file 工具，将报告写入指定路径。\n"
        f"硬性要求：最终必须在沙箱中生成文件 {report_path}，并且在结束前读取它自检。\n"
        "\n"
        + (skills_catalog_text or "")
    )


def main() -> None:
    _silence_deprecation_warnings()
    _ensure_deepagents_importable()

    api_key = _require_env("AGENTBAY_API_KEY")
    dashscope_key = _require_env("DASHSCOPE_API_KEY")

    from deepagents.graph import create_deep_agent  # type: ignore[import-not-found]
    from langchain_community.chat_models import ChatTongyi
    from langchain_core.messages import HumanMessage

    from agentbay import AgentBay

    scenario_key = os.environ.get("AGENTBAY_OFFICIAL_SKILLS_SCENARIO", "").strip() or "generic"
    scenario = get_scenario(scenario_key)

    image_id = DEFAULT_IMAGE_ID
    skills_root = SKILLS_ROOT
    report_path = scenario.default_report_path

    agent_bay = AgentBay(api_key=api_key)
    skills = agent_bay.beta.skills.list_metadata()
    if not skills:
        raise RuntimeError("ListSkillMetaData returned empty list")

    skills_catalog_text = _build_skills_catalog_text(skills)

    backend = AgentBayDeepagentsBackend(
        agent_bay=agent_bay,
        skills_metadata=skills,
        image_id=image_id,
        skills_root=skills_root,
        report_path=report_path,
        trace=True,
    )

    model = ChatTongyi(model=MODEL_NAME, api_key=dashscope_key)
    system_prompt = _build_system_prompt(skills_catalog_text, report_path=report_path)

    agent = create_deep_agent(
        model=model,
        backend=backend,
        skills=[skills_root],
        system_prompt=system_prompt,
        debug=False,
    )

    user_prompt = (
        f"{scenario.user_prompt}\n\n"
        "请你自行选择合适的 skills 并完成任务。\n"
        f"最后请在沙箱中写入完整报告到 {report_path}，然后读取该文件自检。\n"
        "完成后给出中文摘要，并包含报告文件的绝对路径。\n"
    )
    _print_block("[llm] input", user_prompt)

    def _prompt_requires_report(prompt: str, path: str) -> bool:
        p = prompt or ""
        r = path or ""
        if not r:
            return False
        return r in p

    def _invoke_and_verify(prompt: str) -> List[str]:
        backend.read_paths = []
        backend.report_opened = False

        expects_report = _prompt_requires_report(prompt, report_path)
        result = agent.invoke(
            {"messages": [HumanMessage(content=prompt)]},
            config={"configurable": {"thread_id": "agentbay-deepagents-official-skills-cookbook"}},
        )
        _print_block("[llm] output", _msg_to_text(result))

        session = backend.session
        if session is None:
            return ["Session was not created (the model did not call any sandbox tool)."]

        content = ""
        if expects_report:
            try:
                v = session.file_system.read_file(report_path, format="text")
                content = (v.content or "").strip() if v.success else ""
            except Exception as e:
                print(f"[verify] read report failed: {e}", flush=True)

        missing: List[str] = []
        if expects_report and not content:
            missing.append(f"Report file `{report_path}` is empty or missing.")
        if not any(p.endswith("/SKILL.md") for p in backend.read_paths):
            missing.append("No SKILL.md was read via tools.")
        if expects_report and not backend.report_opened:
            missing.append(f"Report was not opened via read_file('{report_path}').")
        return missing

    missing = _invoke_and_verify(user_prompt)
    if missing:
        followup = (
            "你刚才的输出没有通过校验。请严格按要求补齐，必须真实调用工具。\n"
            "请补齐：\n"
            "- 读取你选择的 skill 的 SKILL.md（read_file）\n"
            f"- 一次性写入完整报告到 {report_path}（write_file）\n"
            f"- 读取 {report_path} 自检（read_file）\n"
            "- 最后给出中文摘要，并给出报告文件绝对路径\n\n"
            "当前缺失项：\n- "
            + "\n- ".join(missing)
        )
        missing2 = _invoke_and_verify(followup)
        if missing2:
            raise RuntimeError("Verification failed:\n- " + "\n- ".join(missing2))

    session = backend.session
    if session is None:
        raise RuntimeError("Session is missing after agent run")
    try:
        v = session.file_system.read_file(report_path, format="text")
        report_content = (v.content or "").strip() if v.success else ""
        if not report_content:
            raise RuntimeError(v.error_message or f"Report not found: {report_path}")
        _print_block(
            "[Cookbook] Report Preview",
            report_content[:1200] + ("..." if len(report_content) > 1200 else ""),
        )
    finally:
        backend.close()


if __name__ == "__main__":
    main()

