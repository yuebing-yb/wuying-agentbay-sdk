#!/usr/bin/env python3
"""
build_llms_txt.py - Generate llms.txt and llms-full.txt for AI coding assistants.

Tiered knowledge construction approach:
- Tier 1: Core SDK public API source (~30 files per language, async-only for Python)
- Tier 2: API Reference documentation summaries
- Tier 3: Key examples and guides
- Tier 4: READMEs and project configuration

Truncated source files include a method/function signature index so LLMs
can discover the full API surface even when file bodies are cut short.

Usage:
  python scripts/build_llms_txt.py
  python scripts/build_llms_txt.py --out-root /path/to/output
"""
from __future__ import annotations

import argparse
import re
import sys
import time
from pathlib import Path
from typing import Dict, List, Optional, Set, Tuple

SEPARATOR = "=" * 48

TIER_1_LIMIT = 20_000  # Core SDK source
TIER_2_LIMIT = 12_000  # API reference docs
TIER_3_LIMIT = 8_000   # Examples and guides
TIER_4_LIMIT = 5_000   # READMEs and config

SIGNATURE_PATTERNS = {
    ".py": re.compile(r"^( *)(?:async )?def (\w+)\(.*$", re.MULTILINE),
    ".ts": re.compile(
        r"^( *)(?:async |static )?(?:public |private |protected )?(\w+)\s*[<(].*$",
        re.MULTILINE,
    ),
    ".go": re.compile(r"^func (?:\(.*?\) )?(\w+)\(.*$", re.MULTILINE),
}

EXCLUDE_DIRS = {
    "node_modules", ".git", "__pycache__", ".pytest_cache", ".mypy_cache",
    ".cache", ".venv", "venv", "test_env", "agentbay_example_env",
    ".github", ".aoneci", ".cursor", ".idea", ".vscode",
    "dist", "build", "tmp", "downloads", "logs", ".next",
    "_sync", "tests", "test", "scripts", "cookbook", "assets",
    "resource", "signatures", ".claude", ".aone_copilot",
}


def _extract_signatures(content: str, ext: str) -> List[str]:
    """Extract method/function signatures from source code."""
    pattern = SIGNATURE_PATTERNS.get(ext)
    if not pattern:
        return []
    sigs = []
    for m in pattern.finditer(content):
        line = m.group(0).rstrip()
        if len(line) > 120:
            line = line[:117] + "..."
        sigs.append(line)
    return sigs


def truncate_content(content: str, max_chars: int, filepath: str = "") -> str:
    """Truncate content preserving line boundaries and appending a signature index."""
    if len(content) <= max_chars:
        return content
    lines = content.split("\n")
    result: List[str] = []
    chars = 0
    for line in lines:
        if chars + len(line) + 1 > max_chars:
            break
        result.append(line)
        chars += len(line) + 1

    ext = Path(filepath).suffix if filepath else ""
    remaining = content[chars:]
    sigs = _extract_signatures(remaining, ext)

    result.append(f"\n... [truncated, {len(content) - chars:,} chars remaining] ...")
    if sigs:
        result.append("\n# Remaining method/function signatures (truncated bodies):")
        for sig in sigs:
            result.append(sig)

    return "\n".join(result)


def read_file_safe(path: Path) -> Optional[str]:
    """Read a file, skipping files that are too large or unreadable."""
    try:
        if path.stat().st_size > 200_000:
            return None
        return path.read_text(encoding="utf-8", errors="replace")
    except (OSError, UnicodeDecodeError):
        return None


def collect_tier(
    root: Path,
    patterns: List[str],
    exclude_dirs: Set[str],
) -> List[Tuple[str, str]]:
    """Collect files matching glob patterns relative to root."""
    results: List[Tuple[str, str]] = []
    seen: Set[str] = set()
    for pattern in patterns:
        for path in sorted(root.glob(pattern)):
            if not path.is_file():
                continue
            rel = str(path.relative_to(root))
            if rel in seen:
                continue
            parts = Path(rel).parts
            if any(p in exclude_dirs for p in parts):
                continue
            content = read_file_safe(path)
            if content is not None:
                seen.add(rel)
                results.append((rel, content))
    return results


def format_output(files: List[Tuple[str, str]]) -> str:
    """Format collected files into a single text document with directory tree."""
    tree_lines = ["Directory structure:", "└── wuying-agentbay-sdk/"]
    dirs_seen: Set[str] = set()
    for rel, _ in files:
        parts = Path(rel).parts
        for i in range(len(parts) - 1):
            d = "/".join(parts[: i + 1])
            if d not in dirs_seen:
                dirs_seen.add(d)
                indent = "    " + "│   " * i
                tree_lines.append(f"{indent}├── {parts[i]}/")
        indent = "    " + "│   " * (len(parts) - 1)
        tree_lines.append(f"{indent}├── {parts[-1]}")

    sections = ["\n".join(tree_lines), ""]
    for rel, content in files:
        sections.append(SEPARATOR)
        sections.append(f"FILE: {rel}")
        sections.append(SEPARATOR)
        sections.append(content)
        sections.append("")
    return "\n".join(sections)


# ---------------------------------------------------------------------------
# llms-full.txt builder
# ---------------------------------------------------------------------------

def build_llms_full(root: Path) -> str:
    """Build llms-full.txt with tiered knowledge construction."""
    all_files: List[Tuple[str, str, int]] = []

    # === Tier 1: Core SDK public API source files ===
    py_core = collect_tier(root, [
        "python/agentbay/_async/agentbay.py",
        "python/agentbay/_async/session.py",
        "python/agentbay/_async/command.py",
        "python/agentbay/_async/filesystem.py",
        "python/agentbay/_async/computer.py",
        "python/agentbay/_async/context.py",
        "python/agentbay/_async/mobile.py",
        "python/agentbay/_async/browser.py",
        "python/agentbay/_async/browser_operator.py",
        "python/agentbay/_async/agent.py",
        "python/agentbay/_async/code.py",
        "python/agentbay/_async/beta.py",
        "python/agentbay/__init__.py",
        "python/agentbay/_async/__init__.py",
    ], EXCLUDE_DIRS)

    ts_core = collect_tier(root, [
        "typescript/src/agent-bay.ts",
        "typescript/src/session.ts",
        "typescript/src/command/command.ts",
        "typescript/src/filesystem/filesystem.ts",
        "typescript/src/computer/computer.ts",
        "typescript/src/context.ts",
        "typescript/src/mobile/mobile.ts",
        "typescript/src/browser/browser.ts",
        "typescript/src/agent/agent.ts",
        "typescript/src/code/code.ts",
        "typescript/src/index.ts",
    ], EXCLUDE_DIRS)

    go_core = collect_tier(root, [
        "golang/pkg/agentbay/agentbay.go",
        "golang/pkg/agentbay/session.go",
        "golang/pkg/agentbay/command/command.go",
        "golang/pkg/agentbay/filesystem/filesystem.go",
        "golang/pkg/agentbay/computer/computer.go",
        "golang/pkg/agentbay/context.go",
        "golang/pkg/agentbay/mobile/mobile.go",
        "golang/pkg/agentbay/browser/browser.go",
        "golang/pkg/agentbay/agent/agent.go",
    ], EXCLUDE_DIRS)

    for f, c in py_core + ts_core + go_core:
        all_files.append((f, c, TIER_1_LIMIT))

    # === Tier 2: API Reference docs (top-level summaries only) ===
    api_docs = collect_tier(root, [
        "python/docs/api/README.md",
        "python/docs/api/*/README.md",
        "typescript/docs/api/README.md",
        "typescript/docs/api/*/README.md",
        "golang/docs/api/README.md",
        "golang/docs/api/*/README.md",
        "java/docs/api/README.md",
        "java/docs/api/*/README.md",
    ], EXCLUDE_DIRS)
    for f, c in api_docs:
        all_files.append((f, c, TIER_2_LIMIT))

    # === Tier 3: Key examples and guides ===
    examples = collect_tier(root, [
        "python/docs/examples/README.md",
        "python/docs/examples/_async/common-features/basics/*/README.md",
        "python/docs/examples/_async/browser-use/*/README.md",
        "typescript/docs/examples/README.md",
        "typescript/docs/examples/common-features/basics/*/README.md",
        "typescript/docs/examples/browser-use/*/README.md",
        "golang/docs/examples/README.md",
        "golang/docs/examples/common-features/basics/*/README.md",
    ], EXCLUDE_DIRS)
    guides = collect_tier(root, [
        "docs/guides/README.md",
        "docs/guides/*/README.md",
        "docs/quickstart/README.md",
    ], EXCLUDE_DIRS)
    for f, c in examples + guides:
        all_files.append((f, c, TIER_3_LIMIT))

    # === Tier 4: READMEs, config, meta ===
    meta = collect_tier(root, [
        "README.md",
        "python/README.md",
        "typescript/README.md",
        "golang/README.md",
        "java/README.md",
        "python/pyproject.toml",
        "typescript/package.json",
        "golang/go.mod",
        "docs/README.md",
    ], EXCLUDE_DIRS)
    for f, c in meta:
        all_files.append((f, c, TIER_4_LIMIT))

    # Deduplicate: keep first occurrence (higher-tier limit wins)
    seen_paths: Set[str] = set()
    deduped: List[Tuple[str, str, int]] = []
    for f, c, limit in all_files:
        if f not in seen_paths:
            seen_paths.add(f)
            deduped.append((f, c, limit))
    all_files = deduped

    truncated = [(f, truncate_content(c, limit, f)) for f, c, limit in all_files]
    truncated.sort(key=lambda x: x[0])
    return format_output(truncated)


# ---------------------------------------------------------------------------
# llms.txt builder (concise)
# ---------------------------------------------------------------------------

def build_llms_concise(root: Path) -> str:
    """Build llms.txt: READMEs + config + top-level guides only."""
    all_files: List[Tuple[str, str]] = []

    meta = collect_tier(root, [
        "README.md",
        "python/README.md",
        "typescript/README.md",
        "golang/README.md",
        "java/README.md",
        "python/pyproject.toml",
        "typescript/package.json",
        "golang/go.mod",
        "docs/README.md",
        "docs/quickstart/README.md",
        "docs/guides/README.md",
        "docs/guides/*/README.md",
    ], EXCLUDE_DIRS)

    for f, c in meta:
        all_files.append((f, truncate_content(c, TIER_4_LIMIT, f)))

    all_files.sort(key=lambda x: x[0])
    return format_output(all_files)


def count_tokens_estimate(text: str) -> int:
    """Rough token estimate: ~4 chars per token for mixed code/prose."""
    return len(text) // 4


def main() -> None:
    ap = argparse.ArgumentParser(
        description="Generate llms.txt and llms-full.txt for AI coding assistants",
    )
    ap.add_argument(
        "--project-root",
        type=Path,
        default=Path(__file__).parent.parent,
        help="Project root directory (default: parent of scripts/)",
    )
    ap.add_argument(
        "--out-root",
        type=Path,
        default=None,
        help="Output directory (default: project root)",
    )
    args = ap.parse_args()

    root = args.project_root.resolve()
    out = args.out_root.resolve() if args.out_root else root

    if not (root / "README.md").exists():
        print(f"Error: {root} does not look like the project root")
        sys.exit(1)

    t0 = time.time()

    print("Building llms.txt (concise)...")
    llms = build_llms_concise(root)
    t1 = time.time()
    tokens_llms = count_tokens_estimate(llms)
    print(f"  {len(llms):,} chars, ~{tokens_llms:,} tokens ({t1-t0:.2f}s)")

    print("Building llms-full.txt (comprehensive)...")
    llms_full = build_llms_full(root)
    t2 = time.time()
    tokens_full = count_tokens_estimate(llms_full)
    print(f"  {len(llms_full):,} chars, ~{tokens_full:,} tokens ({t2-t1:.2f}s)")

    (out / "llms.txt").write_text(llms, encoding="utf-8")
    (out / "llms-full.txt").write_text(llms_full, encoding="utf-8")

    full_files = re.findall(r"^FILE: (.+)$", llms_full, re.MULTILINE)
    dir_counts: Dict[str, int] = {}
    for f in full_files:
        top = f.split("/")[0] if "/" in f else "root"
        dir_counts[top] = dir_counts.get(top, 0) + 1
    print(f"\nllms-full.txt: {len(full_files)} files")
    for d in sorted(dir_counts, key=lambda x: dir_counts[x], reverse=True):
        print(f"  {d}: {dir_counts[d]} files")

    print(f"\nTotal time: {t2-t0:.2f}s")
    print(f"Output: {out}")


if __name__ == "__main__":
    main()
