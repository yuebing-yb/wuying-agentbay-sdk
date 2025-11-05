#!/usr/bin/env python3
"""Generate API reference documentation for the Python SDK using pydoc-markdown APIs."""

from __future__ import annotations

import shutil
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Iterable, Sequence

import docspec
from pydoc_markdown import PydocMarkdown
from pydoc_markdown.contrib.loaders.python import PythonLoader
from pydoc_markdown.contrib.processors.crossref import CrossrefProcessor
from pydoc_markdown.contrib.processors.filter import FilterProcessor
from pydoc_markdown.contrib.processors.smart import SmartProcessor
from pydoc_markdown.contrib.renderers.markdown import MarkdownRenderer


@dataclass(frozen=True)
class DocMapping:
    target: str
    title: str
    modules: Sequence[str]


PROJECT_ROOT = Path(__file__).resolve().parent.parent
DOCS_ROOT = PROJECT_ROOT / "docs" / "api-preview" / "latest"

DOC_MAPPINGS: Sequence[DocMapping] = (
    DocMapping("common-features/basics/agentbay.md", "AgentBay", ("agentbay.agentbay",)),
    DocMapping("common-features/basics/session.md", "Session", ("agentbay.session",)),
    DocMapping("common-features/basics/command.md", "Command", ("agentbay.command",)),
    DocMapping("common-features/basics/context.md", "Context", ("agentbay.context",)),
    DocMapping("common-features/basics/context-manager.md", "Context Manager", ("agentbay.context_manager",)),
    DocMapping("common-features/basics/filesystem.md", "File System", ("agentbay.filesystem",)),
    DocMapping("common-features/basics/logging.md", "Logging", ("agentbay.logger",)),
    DocMapping("common-features/advanced/agent.md", "Agent", ("agentbay.agent",)),
    DocMapping("common-features/advanced/oss.md", "OSS", ("agentbay.oss",)),
    DocMapping("browser-use/browser.md", "Browser", ("agentbay.browser",)),
    DocMapping("browser-use/extension.md", "Extension", ("agentbay.extension",)),
    DocMapping("codespace/code.md", "Code", ("agentbay.code",)),
    DocMapping("computer-use/application.md", "Application", ("agentbay.application",)),
    DocMapping("computer-use/computer.md", "Computer", ("agentbay.computer",)),
    DocMapping("computer-use/ui.md", "UI", ("agentbay.ui",)),
    DocMapping("computer-use/window.md", "Window Manager", ("agentbay.window",)),
    DocMapping("mobile-use/mobile.md", "Mobile", ("agentbay.mobile",)),
)


def ensure_clean_docs_root() -> None:
    if DOCS_ROOT.exists():
        shutil.rmtree(DOCS_ROOT)
    DOCS_ROOT.mkdir(parents=True, exist_ok=True)


def prune_members(container, module_name: str) -> None:
    members = getattr(container, "members", None)
    if not members:
        return

    filtered = []
    for member in members:
        if isinstance(member, docspec.Indirection):
            continue

        prune_members(member, module_name)
        filtered.append(member)

    members[:] = filtered


def render_markdown(module_names: Iterable[str]) -> str:
    loader = PythonLoader(search_path=[str(PROJECT_ROOT)], modules=list(module_names))
    pydoc = PydocMarkdown(
        loaders=[loader],
        processors=[
            FilterProcessor(expression="not name.startswith('_')"),
            SmartProcessor(),
            CrossrefProcessor(),
        ],
        renderer=MarkdownRenderer(
            render_module_header=False,
            render_typehint_in_data_header=True,
            data_code_block=True,
            insert_header_anchors=False,
        ),
    )

    modules = pydoc.load_modules()
    for module in modules:
        prune_members(module, module.name)

    pydoc.process(modules)
    markdown = pydoc.renderer.render_to_string(modules)
    if markdown is None:
        raise RuntimeError("Markdown renderer returned no content")
    return markdown.strip()


def format_markdown(raw_content: str, title: str) -> str:
    content = raw_content.lstrip()
    if content.startswith("#"):
        lines = content.splitlines()
        lines[0] = f"# {title} API Reference"
        content = "\n".join(lines)
    else:
        content = f"# {title} API Reference\n\n{content}"

    content = content.rstrip() + "\n\n---\n\n*Documentation generated automatically from source code using pydoc-markdown.*\n"
    return content


def write_readme() -> None:
    lines = [
        "# AgentBay Python SDK API Reference (Preview)",
        "",
        "This directory is generated. Run `python scripts/generate_api_docs.py` to refresh it.",
        "",
    ]

    sections: dict[str, list[DocMapping]] = {}
    for mapping in DOC_MAPPINGS:
        section = mapping.target.split("/")[0]
        sections.setdefault(section, []).append(mapping)

    for section_name in sorted(sections):
        lines.append(f"## {section_name.replace('-', ' ').title()}")
        lines.append("")
        for mapping in sections[section_name]:
            lines.append(f"- `{mapping.target}` – {mapping.title}")
        lines.append("")

    README = DOCS_ROOT / "README.md"
    README.write_text("\n".join(lines), encoding="utf-8")


def main() -> None:
    ensure_clean_docs_root()
    for mapping in DOC_MAPPINGS:
        markdown = render_markdown(mapping.modules)
        formatted = format_markdown(markdown, mapping.title)
        output_path = DOCS_ROOT / mapping.target
        output_path.parent.mkdir(parents=True, exist_ok=True)
        output_path.write_text(formatted, encoding="utf-8")
    write_readme()


if __name__ == "__main__":
    try:
        main()
    except RuntimeError as error:
        print(error, file=sys.stderr)
        sys.exit(1)
