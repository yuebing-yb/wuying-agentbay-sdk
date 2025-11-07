#!/usr/bin/env python3
"""Generate API reference documentation for the Python SDK using pydoc-markdown APIs."""

from __future__ import annotations

import shutil
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Iterable, Sequence

import docspec
import yaml
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
METADATA_PATH = PROJECT_ROOT.parent / "scripts" / "doc-metadata.yaml"

DOC_MAPPINGS: Sequence[DocMapping] = (
    DocMapping("common-features/basics/agentbay.md", "AgentBay", ("agentbay.agentbay",)),
    DocMapping("common-features/basics/session.md", "Session", ("agentbay.session",)),
    DocMapping("common-features/basics/command.md", "Command", ("agentbay.command.command",)),
    DocMapping("common-features/basics/context.md", "Context", ("agentbay.context",)),
    DocMapping("common-features/basics/context-manager.md", "Context Manager", ("agentbay.context_manager",)),
    DocMapping("common-features/basics/filesystem.md", "File System", ("agentbay.filesystem.filesystem",)),
    DocMapping("common-features/basics/logging.md", "Logging", ("agentbay.logger",)),
    DocMapping("common-features/advanced/agent.md", "Agent", ("agentbay.agent",)),
    DocMapping("common-features/advanced/oss.md", "OSS", ("agentbay.oss",)),
    DocMapping("browser-use/browser.md", "Browser", ("agentbay.browser.browser", "agentbay.browser.browser_agent")),
    DocMapping("browser-use/extension.md", "Extension", ("agentbay.extension",)),
    DocMapping("codespace/code.md", "Code", ("agentbay.code",)),
    DocMapping("computer-use/computer.md", "Computer", ("agentbay.computer.computer",)),
    DocMapping("mobile-use/mobile.md", "Mobile", ("agentbay.mobile.mobile",)),
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


def load_metadata() -> dict[str, Any]:
    """Load metadata from the configuration file."""
    if not METADATA_PATH.exists():
        return {}
    with open(METADATA_PATH, 'r', encoding='utf-8') as f:
        return yaml.safe_load(f) or {}


def get_module_name_from_path(module_path: str) -> str:
    """Extract module name from Python module path (e.g., agentbay.session -> session)."""
    return module_path.split('.')[-1]


def get_tutorial_section(module_name: str, metadata: dict[str, Any]) -> str:
    """Generate tutorial section markdown."""
    module_config = metadata.get('modules', {}).get(module_name, {})
    tutorial = module_config.get('tutorial')
    if not tutorial:
        return ""

    emoji = module_config.get('emoji', '📖')

    # Calculate correct relative path based on category depth
    # From: python/docs/api-preview/latest/{category}/{file}.md
    # To: project_root/docs/guides/...
    # Need to go up: {category_depth} + 3 (latest, api-preview, docs) + 1 (python) = category_depth + 4
    category = module_config.get('category', 'common-features/basics')
    category_depth = len(category.split('/'))
    depth = category_depth + 4  # +4 for latest/api-preview/docs/python
    up_levels = '../' * depth

    # Replace the hardcoded path with dynamically calculated one
    tutorial_url = tutorial['url']
    # Extract the part after 'docs/' from the URL
    import re
    docs_match = re.search(r'docs/(.+)$', tutorial_url)
    if docs_match:
        tutorial_url = f"{up_levels}docs/{docs_match.group(1)}"

    return f"""## {emoji} Related Tutorial

- [{tutorial['text']}]({tutorial_url}) - {tutorial['description']}

"""


def get_overview_section(module_name: str, metadata: dict[str, Any]) -> str:
    """Generate overview section markdown."""
    module_config = metadata.get('modules', {}).get(module_name, {})
    overview = module_config.get('overview')
    if not overview:
        return ""

    return f"""## Overview

{overview}

"""


def get_requirements_section(module_name: str, metadata: dict[str, Any]) -> str:
    """Generate requirements section markdown."""
    module_config = metadata.get('modules', {}).get(module_name, {})
    requirements = module_config.get('requirements', [])
    if not requirements:
        return ""

    lines = ["## Requirements\n"]
    for req in requirements:
        lines.append(f"- {req}")
    lines.append("\n")

    return "\n".join(lines)


def get_data_types_section(module_name: str, metadata: dict[str, Any]) -> str:
    """Generate data types section markdown."""
    module_config = metadata.get('modules', {}).get(module_name, {})
    data_types = module_config.get('data_types', [])
    if not data_types:
        return ""

    lines = ["## Data Types\n"]
    for data_type in data_types:
        lines.append(f"### {data_type['name']}\n")
        lines.append(f"{data_type['description']}\n")
    lines.append("")

    return "\n".join(lines)


def get_important_notes_section(module_name: str, metadata: dict[str, Any]) -> str:
    """Generate important notes section markdown."""
    module_config = metadata.get('modules', {}).get(module_name, {})
    important_notes = module_config.get('important_notes', [])
    if not important_notes:
        return ""

    lines = ["## Important Notes\n"]
    for note in important_notes:
        lines.append(f"- {note}")
    lines.append("\n")

    return "\n".join(lines)


def get_best_practices_section(module_name: str, metadata: dict[str, Any]) -> str:
    """Generate best practices section markdown."""
    module_config = metadata.get('modules', {}).get(module_name, {})
    best_practices = module_config.get('best_practices', [])
    if not best_practices:
        return ""

    lines = ["## Best Practices\n"]
    for i, practice in enumerate(best_practices, 1):
        lines.append(f"{i}. {practice}")
    lines.append("\n")

    return "\n".join(lines)


def calculate_resource_path(resource: dict[str, Any], module_config: dict[str, Any]) -> str:
    """Calculate relative path for a related resource."""
    target_category = resource.get('category', 'common-features/basics')
    current_category = module_config.get('category', 'common-features/basics')
    module = resource['module']

    # If same category, just use module name
    if target_category == current_category:
        return f"{module}.md"

    # Calculate relative path from current category to target category
    current_parts = current_category.split('/')
    target_parts = target_category.split('/')

    # Go up from current directory
    relative_path = '../' * len(current_parts)

    # Go down to target directory
    relative_path += '/'.join(target_parts) + '/' + module + '.md'

    return relative_path


def get_related_resources_section(module_name: str, metadata: dict[str, Any]) -> str:
    """Generate related resources section markdown."""
    module_config = metadata.get('modules', {}).get(module_name, {})
    resources = module_config.get('related_resources', [])
    if not resources:
        return ""

    lines = ["## Related Resources\n"]
    for resource in resources:
        path = calculate_resource_path(resource, module_config)
        lines.append(f"- [{resource['name']}]({path})")

    return "\n".join(lines) + "\n\n"


def fix_code_block_indentation(content: str) -> str:
    """
    Fix code block indentation in Example sections.
    pydoc-markdown adds indentation before code fences in examples, which breaks rendering.
    This function removes that extra indentation.

    Handles two patterns:
    1. **Example**:\n\n    ```python (4 spaces)
    2. **Example**:\n\n        ```python (8 spaces)
    """
    import re

    # Pattern 1: 4-space indentation (most common)
    # Matches: "**Example**:\n\n    ```python"
    pattern1 = r'(\*\*Example\*\*:)\n\n(    ```python\n(?:.*\n)*?    ```)'

    # Pattern 2: 8-space indentation (when source has blank line after Example:)
    # Matches: "**Example**:\n\n  \n        ```python" (with an extra line containing 2 spaces)
    pattern2 = r'(\*\*Example\*\*:)\n\n  \n(        ```python\n(?:.*\n)*?        ```)'

    def fix_block_4_spaces(match):
        header = match.group(1)  # "**Example**:"
        code_block = match.group(2)  # The indented code block

        # Remove 4 spaces from each line that has them
        fixed_lines = []
        for line in code_block.split('\n'):
            if line.startswith('    '):  # 4 spaces
                fixed_lines.append(line[4:])  # Remove the 4 spaces
            else:
                fixed_lines.append(line)

        return header + '\n\n' + '\n'.join(fixed_lines)

    def fix_block_8_spaces(match):
        header = match.group(1)  # "**Example**:"
        code_block = match.group(2)  # The indented code block

        # Remove 8 spaces from each line that has them
        fixed_lines = []
        for line in code_block.split('\n'):
            if line.startswith('        '):  # 8 spaces
                fixed_lines.append(line[8:])  # Remove the 8 spaces
            else:
                fixed_lines.append(line)

        return header + '\n\n' + '\n'.join(fixed_lines)

    # Apply both patterns
    content = re.sub(pattern2, fix_block_8_spaces, content, flags=re.MULTILINE)
    content = re.sub(pattern1, fix_block_4_spaces, content, flags=re.MULTILINE)

    return content


def format_markdown(raw_content: str, title: str, module_name: str, metadata: dict[str, Any]) -> str:
    """Enhanced markdown formatting with metadata injection."""
    content = raw_content.lstrip()

    # Fix code block indentation in Example sections
    content = fix_code_block_indentation(content)

    # 1. Add title
    if content.startswith("#"):
        lines = content.splitlines()
        lines[0] = f"# {title} API Reference"
        content = "\n".join(lines)
    else:
        content = f"# {title} API Reference\n\n{content}"

    # 2. Collect all sections to insert after title
    sections_after_title = []

    # Tutorial section
    tutorial_section = get_tutorial_section(module_name, metadata)
    if tutorial_section:
        sections_after_title.append(tutorial_section)

    # Overview section
    overview_section = get_overview_section(module_name, metadata)
    if overview_section:
        sections_after_title.append(overview_section)

    # Requirements section
    requirements_section = get_requirements_section(module_name, metadata)
    if requirements_section:
        sections_after_title.append(requirements_section)

    # Data types section
    data_types_section = get_data_types_section(module_name, metadata)
    if data_types_section:
        sections_after_title.append(data_types_section)

    # Important notes section
    important_notes_section = get_important_notes_section(module_name, metadata)
    if important_notes_section:
        sections_after_title.append(important_notes_section)

    # Insert all sections after title at once
    if sections_after_title:
        lines = content.split('\n', 1)
        if len(lines) >= 2:
            title_line = lines[0]
            rest_content = lines[1]
            combined_sections = ''.join(sections_after_title)
            content = f"{title_line}\n\n{combined_sections}\n{rest_content}"

    # Add best practices before related resources
    best_practices_section = get_best_practices_section(module_name, metadata)
    if best_practices_section:
        content = content.rstrip() + "\n\n" + best_practices_section

    # Add related resources before footer
    resources_section = get_related_resources_section(module_name, metadata)
    if resources_section:
        content = content.rstrip() + "\n\n" + resources_section

    # Add footer
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
    metadata = load_metadata()
    ensure_clean_docs_root()
    for mapping in DOC_MAPPINGS:
        markdown = render_markdown(mapping.modules)
        module_name = get_module_name_from_path(mapping.modules[0])
        formatted = format_markdown(markdown, mapping.title, module_name, metadata)
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
