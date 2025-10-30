#!/usr/bin/env python3
"""
build_llms_txt.py – Generate llms.txt and llms-full.txt for AgentBay SDK

This script creates two files for AI coding assistants:
- llms.txt: A concise index with links to documentation
- llms-full.txt: Complete documentation content for full context

Usage:
  python scripts/build_llms_txt.py
"""
from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path
from typing import List, Tuple

# Regex patterns
RE_SNIPPET = re.compile(r"^(\s*)--8<--\s+\"([^\"]+?)(?::([^\"]+))?\"$", re.M)


def first_heading(md: str) -> str | None:
  """Extract the first heading from markdown content."""
  for line in md.splitlines():
    if line.startswith("#"):
      return line.lstrip("#").strip()
  return None


def md_to_text(md: str) -> str:
  """Convert markdown to plain text."""
  try:
    import bs4
    import markdown

    html = markdown.markdown(
      md, extensions=["fenced_code", "tables", "attr_list"]
    )
    return bs4.BeautifulSoup(html, "html.parser").get_text("\n")
  except ImportError:
    print("Warning: markdown and bs4 not installed, returning raw markdown")
    return md


def count_tokens(text: str, model: str = "cl100k_base") -> int:
  """Estimate token count using tiktoken or word count."""
  try:
    import tiktoken
    return len(tiktoken.get_encoding(model).encode(text))
  except Exception:
    return len(text.split())


def expand_code_snippets(content: str, project_root: Path) -> str:
  """
  Expand code snippets marked with --8<-- "path/to/file" syntax.
  This allows embedding code examples directly in documentation.
  """
  def replace_snippet(match):
    indent = match.group(1)
    snippet_path_str = match.group(2)
    section_name = match.group(3)
    snippet_full_path = project_root / snippet_path_str

    if snippet_full_path.exists():
      try:
        file_content = snippet_full_path.read_text(encoding="utf-8")
        if section_name:
          # Extract section between markers
          start_marker_patterns = [
            f"# --8<-- [start:{section_name.strip()}]",
            f"## --8<-- [start:{section_name.strip()}]",
          ]
          end_marker_patterns = [
            f"# --8<-- [end:{section_name.strip()}]",
            f"## --8<-- [end:{section_name.strip()}]",
          ]

          start_index = -1
          end_index = -1

          for pattern in start_marker_patterns:
            start_index = file_content.find(pattern)
            if start_index != -1:
              start_marker = pattern
              break

          for pattern in end_marker_patterns:
            end_index = file_content.find(pattern)
            if end_index != -1:
              break

          if start_index != -1 and end_index != -1 and start_index < end_index:
            start_of_code = start_index + len(start_marker)
            temp_content = file_content[start_of_code:end_index]
            lines = temp_content.splitlines(keepends=True)
            extracted_lines = []
            for line in lines:
              if (
                not line.strip().startswith("# --8<--")
                and not line.strip().startswith("## --8<--")
                and line.strip() != ""
              ):
                extracted_lines.append(line)
            extracted_content = "".join(extracted_lines).strip("\n")
            return "\n".join(indent + line for line in extracted_content.splitlines())
          else:
            print(
              f"Warning: Section '{section_name}' not found in {snippet_full_path}"
            )
            return match.group(0)
        else:
          # Read entire file
          return "\n".join(indent + line for line in file_content.splitlines())
      except Exception as e:
        print(f"Warning: Could not read snippet file {snippet_full_path}: {e}")
        return match.group(0)
    else:
      print(f"Warning: Snippet file not found: {snippet_full_path}")
      return match.group(0)

  return RE_SNIPPET.sub(replace_snippet, content)


def build_index(project_root: Path) -> str:
  """Build the concise index (llms.txt) with documentation links."""
  readme = project_root / "README.md"
  if not readme.exists():
    sys.exit("README.md not found in project root")

  readme_content = readme.read_text(encoding="utf-8")
  title = first_heading(readme_content) or "AgentBay SDK"
  summary = md_to_text(readme_content).split("\n\n")[0]

  lines = [
    f"# {title}",
    "",
    f"> {summary}",
    "",
  ]

  # Add main README content
  lines.append("## AgentBay SDK Repository")
  lines.append("")
  readme_text = md_to_text(readme_content)
  lines.append(readme_text)
  lines.append("")
  lines.append(
    "**Source:** [wuying-agentbay-sdk repository]"
    "(https://github.com/aliyun/wuying-agentbay-sdk)"
  )
  lines.append("")

  # Collect documentation files
  primary: List[Tuple[str, str]] = []
  secondary: List[Tuple[str, str]] = []

  # Main documentation
  docs_dir = project_root / "docs"
  if docs_dir.exists():
    for md in sorted(docs_dir.rglob("*.md")):
      # Skip node_modules and other irrelevant directories
      if any(part in ["node_modules", "__pycache__", ".git", "venv", "test_venv"] for part in md.parts):
        continue

      rel = md.relative_to(docs_dir)
      url = (
        f"https://github.com/aliyun/wuying-agentbay-sdk/blob/main/docs/{rel}"
        .replace(" ", "%20")
      )
      h = first_heading(md.read_text(encoding="utf-8")) or rel.stem
      if "cookbook" in rel.parts or "example" in rel.parts:
        secondary.append((h, url))
      else:
        primary.append((h, url))

  # Language-specific documentation
  for lang in ["python", "typescript", "golang"]:
    lang_dir = project_root / lang
    if lang_dir.exists():
      # Main README
      lang_readme = lang_dir / "README.md"
      if lang_readme.exists():
        primary.append((
          f"{lang.capitalize()} SDK",
          f"https://github.com/aliyun/wuying-agentbay-sdk/blob/main/{lang}/README.md"
        ))

      # API docs
      api_docs = lang_dir / "docs" / "api"
      if api_docs.exists():
        primary.append((
          f"{lang.capitalize()} API Reference",
          f"https://github.com/aliyun/wuying-agentbay-sdk/blob/main/{lang}/docs/api/"
        ))

  # Cookbook examples
  cookbook_dir = project_root / "cookbook"
  if cookbook_dir.exists():
    cookbook_readme = cookbook_dir / "README.md"
    if cookbook_readme.exists():
      secondary.append((
        "Cookbook Examples",
        "https://github.com/aliyun/wuying-agentbay-sdk/blob/main/cookbook/README.md"
      ))

  def emit(name: str, items: List[Tuple[str, str]]):
    nonlocal lines
    if items:
      lines.append(f"## {name}")
      lines += [f"- [{h}]({u})" for h, u in items]
      lines.append("")

  emit("Documentation", primary)
  emit("Examples & Cookbook", secondary)

  return "\n".join(lines)


def build_full(project_root: Path) -> str:
  """Build the full documentation corpus (llms-full.txt)."""
  out = []

  # Add main README
  readme = project_root / "README.md"
  if readme.exists():
    readme_content = readme.read_text(encoding="utf-8")
    expanded_readme = expand_code_snippets(readme_content, project_root)
    out.append("# AgentBay SDK Repository")
    out.append("")
    out.append(expanded_readme)
    out.append("")
    out.append("---")
    out.append("")

  # Process main documentation
  docs_dir = project_root / "docs"
  if docs_dir.exists():
    print(f"Processing main documentation from: {docs_dir}")
    for md in sorted(docs_dir.rglob("*.md")):
      # Skip node_modules and other irrelevant directories
      if any(part in ["node_modules", "__pycache__", ".git", "venv", "test_venv"] for part in md.parts):
        continue

      print(f"  Processing: {md.relative_to(project_root)}")
      md_content = md.read_text(encoding="utf-8")
      expanded_content = expand_code_snippets(md_content, project_root)
      out.append(expanded_content)
      out.append("")

  # Process language-specific documentation
  for lang in ["python", "typescript", "golang"]:
    lang_dir = project_root / lang
    if not lang_dir.exists():
      continue

    out.append(f"\n# {lang.capitalize()} SDK Documentation\n")

    # Main README
    lang_readme = lang_dir / "README.md"
    if lang_readme.exists():
      print(f"Processing {lang} README")
      content = lang_readme.read_text(encoding="utf-8")
      expanded_content = expand_code_snippets(content, project_root)
      out.append(expanded_content)
      out.append("")

    # API documentation
    lang_docs = lang_dir / "docs"
    if lang_docs.exists():
      print(f"Processing {lang} documentation from: {lang_docs}")
      for md in sorted(lang_docs.rglob("*.md")):
        # Skip node_modules and other irrelevant directories
        if any(part in ["node_modules", "__pycache__", ".git", "venv", "test_venv"] for part in md.parts):
          continue

        print(f"  Processing: {md.relative_to(project_root)}")
        md_content = md.read_text(encoding="utf-8")
        expanded_content = expand_code_snippets(md_content, project_root)
        out.append(expanded_content)
        out.append("")

  # Process cookbook examples
  cookbook_dir = project_root / "cookbook"
  if cookbook_dir.exists():
    out.append("\n# Cookbook Examples\n")
    print(f"Processing cookbook from: {cookbook_dir}")
    for md in sorted(cookbook_dir.rglob("*.md")):
      # Skip node_modules and other irrelevant directories
      if any(part in ["node_modules", "__pycache__", ".git", "venv", "test_venv"] for part in md.parts):
        continue

      print(f"  Processing: {md.relative_to(project_root)}")
      md_content = md.read_text(encoding="utf-8")
      expanded_content = expand_code_snippets(md_content, project_root)
      out.append(expanded_content)
      out.append("")

  return "\n\n".join(out)


def main() -> None:
  """Main entry point for the script."""
  ap = argparse.ArgumentParser(
    description="Generate llms.txt and llms-full.txt for AgentBay SDK",
    formatter_class=argparse.RawDescriptionHelpFormatter,
  )
  ap.add_argument(
    "--project-root",
    type=Path,
    default=Path(__file__).parent.parent,
    help="Project root directory (default: parent of scripts/)"
  )
  ap.add_argument(
    "--out-root",
    type=Path,
    default=None,
    help="Output directory (default: project root)"
  )
  ap.add_argument(
    "--index-limit",
    type=int,
    default=50_000,
    help="Maximum tokens for llms.txt (default: 50,000)"
  )
  ap.add_argument(
    "--full-limit",
    type=int,
    default=500_000,
    help="Maximum tokens for llms-full.txt (default: 500,000)"
  )
  args = ap.parse_args()

  project_root = args.project_root.resolve()
  out_root = args.out_root.resolve() if args.out_root else project_root

  print(f"Project root: {project_root}")
  print(f"Output directory: {out_root}")
  print("")

  # Build index and full documentation
  print("Building llms.txt (index)...")
  idx = build_index(project_root)

  print("\nBuilding llms-full.txt (full documentation)...")
  full = build_full(project_root)

  # Check token limits
  idx_tokens = count_tokens(idx)
  full_tokens = count_tokens(full)

  print(f"\nToken counts:")
  print(f"  llms.txt: {idx_tokens:,} tokens")
  print(f"  llms-full.txt: {full_tokens:,} tokens")

  if idx_tokens > args.index_limit:
    print(f"\n⚠️  Warning: llms.txt exceeds limit ({idx_tokens:,} > {args.index_limit:,})")

  if full_tokens > args.full_limit:
    print(f"\n⚠️  Warning: llms-full.txt exceeds limit ({full_tokens:,} > {args.full_limit:,})")

  # Write output files
  (out_root / "llms.txt").write_text(idx, encoding="utf-8")
  (out_root / "llms-full.txt").write_text(full, encoding="utf-8")

  print("\n✅ Generated llms.txt and llms-full.txt successfully")
  print(f"   Output location: {out_root}")


if __name__ == "__main__":
  main()

