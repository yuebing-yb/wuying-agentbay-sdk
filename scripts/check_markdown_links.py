#!/usr/bin/env python3
"""
Check internal links in markdown documentation.
Validates both file links and anchor links within markdown files.

This script can be used in CI/CD pipelines to ensure documentation quality.

Usage:
    python scripts/check_markdown_links.py                 # Check current directory
    python scripts/check_markdown_links.py --strict        # Exit with error on broken links
    python scripts/check_markdown_links.py --output report.md  # Save report to file
"""

import os
import re
from pathlib import Path
from typing import Dict, List, Set, Tuple
from urllib.parse import unquote
import sys
import json


class MarkdownLink:
    """Represents a markdown link."""

    def __init__(self, source_file: Path, link_text: str, target: str, line_number: int):
        self.source_file = source_file
        self.link_text = link_text
        self.target = target
        self.line_number = line_number

    def __repr__(self):
        return f"MarkdownLink({self.source_file}:{self.line_number} -> {self.target})"

    def to_dict(self):
        """Convert to dictionary for JSON serialization."""
        return {
            'source_file': str(self.source_file),
            'link_text': self.link_text,
            'target': self.target,
            'line_number': self.line_number
        }


class MarkdownLinkChecker:
    """Check internal links in markdown files."""

    # Patterns to match markdown links
    MARKDOWN_LINK_PATTERN = re.compile(r'\[([^\]]+)\]\(([^\)]+)\)')
    # Pattern to match headings
    HEADING_PATTERN = re.compile(r'^(#{1,6})\s+(.+)$', re.MULTILINE)

    def __init__(self, root_dir: str, exclude_patterns: List[str] = None, check_dir_readme: bool = False):
        self.root_dir = Path(root_dir).resolve()
        self.check_dir_readme = check_dir_readme
        self.exclude_patterns = exclude_patterns or [
            'node_modules',
            'venv',
            'test_venv',
            '.pytest_cache',
            'dist',
            'build',
            '__pycache__',
            '.git',
            '.tox',
            'htmlcov',
            'site-packages',
        ]

        # Cache for markdown files and their headings
        self.markdown_files: Set[Path] = set()
        self.file_headings: Dict[Path, Set[str]] = {}

        # Results
        self.broken_links: List[Tuple[MarkdownLink, str]] = []
        self.valid_links: List[MarkdownLink] = []

    def should_exclude(self, path: Path) -> bool:
        """Check if path should be excluded."""
        parts = path.parts
        for pattern in self.exclude_patterns:
            if pattern in parts:
                return True
        return False

    def scan_markdown_files(self):
        """Scan and cache all markdown files."""
        print(f"🔍 Scanning markdown files in {self.root_dir}...")

        for md_file in self.root_dir.rglob('*.md'):
            if not self.should_exclude(md_file):
                self.markdown_files.add(md_file)
                self._extract_headings(md_file)

        print(f"📚 Found {len(self.markdown_files)} markdown files")

    def _extract_headings(self, file_path: Path):
        """Extract all headings from a markdown file and generate anchor names."""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()

            headings = set()
            for match in self.HEADING_PATTERN.finditer(content):
                heading_text = match.group(2).strip()
                anchor = self._heading_to_anchor(heading_text)
                headings.add(anchor)

            self.file_headings[file_path] = headings

        except Exception as e:
            print(f"⚠️  Warning: Could not read {file_path}: {e}")
            self.file_headings[file_path] = set()

    def _heading_to_anchor(self, heading_text: str) -> str:
        """
        Convert heading text to GitHub-style anchor.

        GitHub's anchor generation:
        1. Remove markdown formatting
        2. Convert to lowercase
        3. Replace spaces with hyphens
        4. Remove special characters except alphanumeric, hyphens, underscores, and Chinese characters
        5. Remove emojis from anchor but not from the original text
        """
        # Remove markdown formatting
        text = re.sub(r'\[([^\]]+)\]\([^\)]+\)', r'\1', heading_text)
        text = re.sub(r'[`*_~]', '', text)

        # Remove emojis (common emoji ranges)
        text = re.sub(r'[\U0001F300-\U0001F9FF]', '', text)
        text = re.sub(r'[\u2600-\u26FF]', '', text)
        text = re.sub(r'[\u2700-\u27BF]', '', text)

        # Convert to lowercase
        text = text.lower()

        # Replace spaces with hyphens
        text = re.sub(r'\s+', '-', text)

        # Remove special characters, keep alphanumeric, hyphens, underscores, and Chinese
        text = re.sub(r'[^\w\u4e00-\u9fff\-]', '', text)

        # Remove leading/trailing hyphens
        text = text.strip('-')

        return text

    def check_links(self):
        """Check all internal links in markdown files."""
        print("🔗 Checking internal links...")

        for md_file in sorted(self.markdown_files):
            self._check_file_links(md_file)

        print(f"\n📊 Results:")
        print(f"  ✅ Valid links: {len(self.valid_links)}")
        print(f"  ❌ Broken links: {len(self.broken_links)}")

    def _check_file_links(self, source_file: Path):
        """Check all links in a single file."""
        try:
            with open(source_file, 'r', encoding='utf-8') as f:
                content = f.read()
        except Exception as e:
            print(f"⚠️  Warning: Could not read {source_file}: {e}")
            return

        lines = content.split('\n')
        in_code_block = False
        code_block_pattern = re.compile(r'^```')

        for line_num, line in enumerate(lines, 1):
            # Track code blocks (fenced code blocks with ```)
            if code_block_pattern.match(line.strip()):
                in_code_block = not in_code_block
                continue

            # Skip links in code blocks
            if in_code_block:
                continue

            # Skip indented code blocks (4 spaces or 1 tab)
            if line.startswith('    ') or line.startswith('\t'):
                continue

            for match in self.MARKDOWN_LINK_PATTERN.finditer(line):
                link_text = match.group(1)
                target = match.group(2)

                # Skip external links
                if target.startswith(('http://', 'https://', 'mailto:', 'ftp://')):
                    continue

                # Skip absolute paths that don't start with the repo root
                if target.startswith('/') and not target.startswith(str(self.root_dir)):
                    continue

                link = MarkdownLink(source_file, link_text, target, line_num)
                self._validate_link(link)

    def _validate_link(self, link: MarkdownLink):
        """Validate a single link."""
        target = unquote(link.target)

        # Split target into file path and anchor
        if '#' in target:
            file_part, anchor = target.split('#', 1)
        else:
            file_part, anchor = target, None

        # Resolve file path
        if file_part == '':
            # Pure anchor link to same file
            target_file = link.source_file
        else:
            # Relative link
            source_dir = link.source_file.parent
            target_file = (source_dir / file_part).resolve()

        # Check if file exists
        if not target_file.exists():
            # Try to make path relative to root_dir, otherwise use absolute path
            try:
                rel_path = target_file.relative_to(self.root_dir)
            except ValueError:
                rel_path = target_file
            self.broken_links.append((link, f"File not found: {rel_path}"))
            return

        # If file is a directory, check for README.md
        if target_file.is_dir():
            readme = target_file / 'README.md'
            if readme.exists():
                target_file = readme
            else:
                # Only report missing README if check_dir_readme is enabled
                if self.check_dir_readme:
                    # Try to make path relative to root_dir, otherwise use absolute path
                    try:
                        rel_path = target_file.relative_to(self.root_dir)
                    except ValueError:
                        rel_path = target_file
                    self.broken_links.append((link, f"Directory has no README.md: {rel_path}"))
                    return
                else:
                    # Treat directory link as valid (directory exists)
                    self.valid_links.append(link)
                    return

        # Check if it's a markdown file
        if target_file.suffix != '.md':
            # Non-markdown files are considered valid if they exist
            self.valid_links.append(link)
            return

        # Check anchor if present
        if anchor:
            if target_file not in self.file_headings:
                self._extract_headings(target_file)

            if anchor not in self.file_headings[target_file]:
                available_anchors = sorted(self.file_headings[target_file])
                similar = self._find_similar_anchor(anchor, available_anchors)

                # Try to make path relative to root_dir, otherwise use absolute path
                try:
                    rel_path = target_file.relative_to(self.root_dir)
                except ValueError:
                    rel_path = target_file

                error_msg = f"Anchor not found: #{anchor} in {rel_path}"
                if similar:
                    error_msg += f" (did you mean #{similar}?)"

                self.broken_links.append((link, error_msg))
                return

        self.valid_links.append(link)

    def _find_similar_anchor(self, target: str, available: List[str]) -> str:
        """Find a similar anchor using simple string similarity."""
        if not available:
            return ""

        # Simple similarity: check if target is substring or vice versa
        for anchor in available:
            if target in anchor or anchor in target:
                return anchor

        return ""

    def check_emoji_anchor_compatibility(self):
        """Check for emoji headings that might have cross-platform issues."""
        # Emoji pattern
        emoji_pattern = re.compile(r'[\U0001F300-\U0001F9FF\u2600-\u26FF\u2700-\u27BF]')

        warnings = []

        for md_file in sorted(self.markdown_files):
            try:
                with open(md_file, 'r', encoding='utf-8') as f:
                    content = f.read()

                # Find emoji headings and their line numbers
                emoji_headings = {}
                for match in self.HEADING_PATTERN.finditer(content):
                    heading_text = match.group(2).strip()
                    if emoji_pattern.search(heading_text):
                        anchor = self._heading_to_anchor(heading_text)
                        line_num = content[:match.start()].count('\n') + 1
                        emoji_headings[anchor] = (heading_text, line_num)

                if not emoji_headings:
                    continue

                # Find links to these emoji headings
                lines = content.split('\n')
                for i, line in enumerate(lines, 1):
                    for match in self.MARKDOWN_LINK_PATTERN.finditer(line):
                        target = match.group(2)
                        if not target.startswith('#'):
                            continue

                        anchor = target.lstrip('#')
                        if anchor in emoji_headings:
                            # Check if HTML anchor exists
                            html_anchor = f'<a id="{anchor}"></a>'
                            if html_anchor not in content:
                                warnings.append({
                                    'file': md_file,
                                    'link_line': i,
                                    'heading_line': emoji_headings[anchor][1],
                                    'anchor': anchor,
                                    'heading': emoji_headings[anchor][0]
                                })
            except Exception:
                pass

        return warnings

    def print_emoji_warnings(self, warnings):
        """Print warnings for emoji anchor compatibility issues."""
        if not warnings:
            return

        print(f"\n⚠️  Found {len(warnings)} emoji anchor(s) without HTML anchor tags:")
        print("   These links may not work in VS Code/Cursor. Add HTML anchors for compatibility.\n")

        # Group by file
        by_file = {}
        for w in warnings:
            if w['file'] not in by_file:
                by_file[w['file']] = []
            by_file[w['file']].append(w)

        for file_path in sorted(by_file.keys()):
            rel_path = file_path.relative_to(self.root_dir)
            print(f"📄 {rel_path}")

            for w in by_file[file_path]:
                print(f"   Line {w['link_line']:4d}: Link to #{w['anchor']}")
                print(f"   Line {w['heading_line']:4d}: {w['heading']}")
                print(f"            💡 Add before heading: <a id=\"{w['anchor']}\"></a>")
                print()

    def print_report(self, verbose: bool = False):
        """Print detailed report of broken links."""
        if not self.broken_links:
            print("\n✅ All internal links are valid!")
            return

        print(f"\n❌ Found {len(self.broken_links)} broken link(s):\n")

        # Group by source file
        by_file: Dict[Path, List[Tuple[MarkdownLink, str]]] = {}
        for link, reason in self.broken_links:
            if link.source_file not in by_file:
                by_file[link.source_file] = []
            by_file[link.source_file].append((link, reason))

        # Print grouped results
        for source_file in sorted(by_file.keys()):
            rel_path = source_file.relative_to(self.root_dir)
            print(f"📄 {rel_path}")

            for link, reason in by_file[source_file]:
                print(f"  Line {link.line_number}: [{link.link_text}]({link.target})")
                print(f"    ⚠️  {reason}")

        if verbose:
            print("\n" + "=" * 80)
            print("Summary by issue type:")

            file_not_found = sum(1 for _, reason in self.broken_links if "File not found" in reason)
            anchor_not_found = sum(1 for _, reason in self.broken_links if "Anchor not found" in reason)
            no_readme = sum(1 for _, reason in self.broken_links if "no README.md" in reason)

            print(f"  - Files not found: {file_not_found}")
            print(f"  - Anchors not found: {anchor_not_found}")
            print(f"  - Directories without README: {no_readme}")

    def save_report(self, output_file: str, format: str = 'markdown'):
        """Save report to a file."""
        if format == 'json':
            self._save_json_report(output_file)
        else:
            self._save_markdown_report(output_file)

    def _save_markdown_report(self, output_file: str):
        """Save report as markdown."""
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write("# Internal Link Check Report\n\n")
            f.write(f"**Repository**: {self.root_dir}\n\n")
            f.write(f"**Statistics**:\n")
            f.write(f"- Total markdown files: {len(self.markdown_files)}\n")
            f.write(f"- Valid links: {len(self.valid_links)}\n")
            f.write(f"- Broken links: {len(self.broken_links)}\n\n")

            if self.broken_links:
                f.write("## Broken Links\n\n")

                by_file: Dict[Path, List[Tuple[MarkdownLink, str]]] = {}
                for link, reason in self.broken_links:
                    if link.source_file not in by_file:
                        by_file[link.source_file] = []
                    by_file[link.source_file].append((link, reason))

                for source_file in sorted(by_file.keys()):
                    rel_path = source_file.relative_to(self.root_dir)
                    f.write(f"\n### {rel_path}\n\n")

                    for link, reason in by_file[source_file]:
                        f.write(f"- **Line {link.line_number}**: `[{link.link_text}]({link.target})`\n")
                        f.write(f"  - 🔴 {reason}\n")
            else:
                f.write("## ✅ All Links Valid\n\n")
                f.write("No broken links found in the documentation.\n")

        print(f"\n📝 Report saved to: {output_file}")

    def _save_json_report(self, output_file: str):
        """Save report as JSON."""
        report = {
            'repository': str(self.root_dir),
            'statistics': {
                'total_markdown_files': len(self.markdown_files),
                'valid_links': len(self.valid_links),
                'broken_links': len(self.broken_links)
            },
            'broken_links': [
                {
                    'link': link.to_dict(),
                    'reason': reason
                }
                for link, reason in self.broken_links
            ]
        }

        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(report, f, indent=2, ensure_ascii=False)

        print(f"\n📝 JSON report saved to: {output_file}")


def main():
    """Main entry point."""
    import argparse

    parser = argparse.ArgumentParser(
        description='Check internal links in markdown documentation',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  %(prog)s                           # Check current directory
  %(prog)s --strict                  # Exit with error on broken links
  %(prog)s --output report.md        # Save report to markdown file
  %(prog)s --output report.json --format json  # Save as JSON
  %(prog)s /path/to/docs             # Check specific directory
        """
    )
    parser.add_argument(
        'root_dir',
        nargs='?',
        default='.',
        help='Root directory to scan (default: current directory)'
    )
    parser.add_argument(
        '--output',
        '-o',
        help='Save report to file'
    )
    parser.add_argument(
        '--format',
        '-f',
        choices=['markdown', 'json'],
        default='markdown',
        help='Output format for report file (default: markdown)'
    )
    parser.add_argument(
        '--exclude',
        '-e',
        action='append',
        help='Additional patterns to exclude (can be used multiple times)'
    )
    parser.add_argument(
        '--strict',
        '-s',
        action='store_true',
        help='Exit with error code if broken links are found'
    )
    parser.add_argument(
        '--verbose',
        '-v',
        action='store_true',
        help='Show verbose output with detailed statistics'
    )
    parser.add_argument(
        '--check-dir-readme',
        action='store_true',
        help='Check if directory links have README.md files (default: disabled)'
    )
    parser.add_argument(
        '--warn-emoji-anchors',
        action='store_true',
        help='Warn about emoji headings without HTML anchors (for VS Code compatibility)'
    )

    args = parser.parse_args()

    # Create checker
    exclude_patterns = None
    if args.exclude:
        exclude_patterns = [
            'node_modules', 'venv', 'test_venv', '.pytest_cache',
            'dist', 'build', '__pycache__', '.git', '.tox', 'htmlcov',
            'site-packages'
        ] + args.exclude

    checker = MarkdownLinkChecker(
        args.root_dir,
        exclude_patterns,
        check_dir_readme=args.check_dir_readme
    )

    # Run checks
    try:
        checker.scan_markdown_files()
        checker.check_links()
        checker.print_report(verbose=args.verbose)

        # Check emoji anchor compatibility if requested
        if args.warn_emoji_anchors:
            emoji_warnings = checker.check_emoji_anchor_compatibility()
            checker.print_emoji_warnings(emoji_warnings)

        # Save report if requested
        if args.output:
            checker.save_report(args.output, format=args.format)

        # Exit with error code if strict mode and broken links found
        if args.strict and checker.broken_links:
            sys.exit(1)

    except KeyboardInterrupt:
        print("\n\n⚠️  Interrupted by user")
        sys.exit(130)
    except Exception as e:
        print(f"\n❌ Error: {e}", file=sys.stderr)
        if args.verbose:
            import traceback
            traceback.print_exc()
        sys.exit(1)


if __name__ == '__main__':
    main()
