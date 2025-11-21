#!/usr/bin/env python
"""
Script to convert sync examples to async examples.
This script will scan all Python files in the _async directory and convert them to async.
"""

import os
import re
from pathlib import Path

def convert_sync_to_async(content: str) -> str:
    """Convert sync code to async code."""
    
    # 1. Replace imports
    content = content.replace("from agentbay import AgentBay", "from agentbay import AsyncAgentBay")
    content = re.sub(r"agent_bay = AgentBay\(", "agent_bay = AsyncAgentBay(", content)
    
    # 2. Add asyncio import if not present
    if "import asyncio" not in content:
        # Find the first import line after docstring
        lines = content.split("\n")
        import_index = -1
        in_docstring = False
        docstring_char = None
        
        for i, line in enumerate(lines):
            stripped = line.strip()
            
            # Handle docstrings
            if stripped.startswith('"""') or stripped.startswith("'''"):
                if not in_docstring:
                    in_docstring = True
                    docstring_char = stripped[:3]
                    if stripped.endswith(docstring_char) and len(stripped) > 6:
                        in_docstring = False
                elif stripped.endswith(docstring_char):
                    in_docstring = False
                continue
            
            if in_docstring:
                continue
            
            # Find first import line
            if line.startswith("import ") or line.startswith("from "):
                import_index = i
                break
        
        if import_index >= 0:
            lines.insert(import_index, "import asyncio")
            content = "\n".join(lines)
    
    # 3. Convert function definitions to async
    # Convert def main() to async def main()
    content = re.sub(r"\ndef (main|create_\w+|take_\w+)\(\)", r"\nasync def \1()", content)
    
    # 4. Add await to common SDK calls
    patterns = [
        (r"agent_bay\.create\(", "await agent_bay.create("),
        (r"agent_bay\.delete\(", "await agent_bay.delete("),
        (r"agent_bay\.list\(", "await agent_bay.list("),
        (r"agent_bay\.context\.get\(", "await agent_bay.context.get("),
        (r"agent_bay\.context\.list\(", "await agent_bay.context.list("),
        (r"session\.delete\(\)", "await session.delete()"),
        (r"session\.browser\.initialize\(", "await session.browser.initialize("),
        (r"session\.browser\.initialize_async\(", "await session.browser.initialize("),
        (r"session\.browser\.agent\.navigate\(", "await session.browser.agent.navigate("),
        (r"session\.browser\.agent\.navigate_async\(", "await session.browser.agent.navigate("),
        (r"session\.browser\.agent\.screenshot\(", "await session.browser.agent.screenshot("),
        (r"session\.browser\.agent\.screenshot_async\(", "await session.browser.agent.screenshot("),
        (r"session\.browser\.screenshot\(", "await session.browser.screenshot("),
        (r"session\.file_system\.write_file\(", "await session.file_system.write_file("),
        (r"session\.file_system\.read_file\(", "await session.file_system.read_file("),
        (r"session\.file_system\.list_directory\(", "await session.file_system.list_directory("),
        (r"session\.file_system\.create_directory\(", "await session.file_system.create_directory("),
        (r"session\.file_system\.get_file_info\(", "await session.file_system.get_file_info("),
        (r"session\.file_system\.edit_file\(", "await session.file_system.edit_file("),
        (r"session\.file_system\.move_file\(", "await session.file_system.move_file("),
        (r"session\.file_system\.search_files\(", "await session.file_system.search_files("),
        (r"session\.file_system\.read_multiple_files\(", "await session.file_system.read_multiple_files("),
        (r"session\.command\.execute_command\(", "await session.command.execute_command("),
        (r"session\.code\.run_code\(", "await session.code.run_code("),
        (r"session\.get_labels\(\)", "await session.get_labels()"),
        (r"session\.get_link\(", "await session.get_link("),
        (r"fs\.write_file\(", "await fs.write_file("),
        (r"fs\.read_file\(", "await fs.read_file("),
        (r"fs\.list_directory\(", "await fs.list_directory("),
        (r"fs\.create_directory\(", "await fs.create_directory("),
        (r"fs\.get_file_info\(", "await fs.get_file_info("),
        (r"fs\.edit_file\(", "await fs.edit_file("),
        (r"fs\.move_file\(", "await fs.move_file("),
        (r"fs\.search_files\(", "await fs.search_files("),
        (r"fs\.read_multiple_files\(", "await fs.read_multiple_files("),
    ]
    
    for pattern, replacement in patterns:
        content = re.sub(pattern, replacement, content)
    
    # 5. Replace time.sleep with asyncio.sleep
    if "time.sleep(" in content:
        content = content.replace("time.sleep(", "asyncio.sleep(")
        if "import time" in content and "import asyncio" not in content:
            content = content.replace("import time", "import asyncio\nimport time")
    
    # 6. Add asyncio.run(main()) at the end if needed
    if 'if __name__ == "__main__":\n    main()' in content:
        content = content.replace(
            'if __name__ == "__main__":\n    main()',
            'if __name__ == "__main__":\n    asyncio.run(main())'
        )
    
    return content

def should_convert_file(file_path: Path) -> bool:
    """Check if a file should be converted."""
    # Skip if already has async def main
    content = file_path.read_text(encoding="utf-8")
    
    # If already has AsyncAgentBay, skip
    if "AsyncAgentBay" in content:
        return False
    
    # If has AgentBay but not async, convert
    if "AgentBay" in content and "async def main" not in content:
        return True
    
    # If has async def main but AgentBay instead of AsyncAgentBay, convert
    if "async def main" in content and "from agentbay import AgentBay" in content:
        return True
    
    return False

def main():
    root_dir = Path(__file__).parent.parent
    async_dir = root_dir / "docs" / "examples" / "_async"
    
    if not async_dir.exists():
        print(f"Error: {async_dir} does not exist")
        return
    
    converted_count = 0
    skipped_count = 0
    
    for py_file in async_dir.rglob("*.py"):
        if should_convert_file(py_file):
            print(f"Converting: {py_file.relative_to(async_dir)}")
            content = py_file.read_text(encoding="utf-8")
            converted_content = convert_sync_to_async(content)
            py_file.write_text(converted_content, encoding="utf-8")
            converted_count += 1
        else:
            skipped_count += 1
    
    print(f"\nConversion complete!")
    print(f"Converted: {converted_count} files")
    print(f"Skipped: {skipped_count} files")

if __name__ == "__main__":
    main()

