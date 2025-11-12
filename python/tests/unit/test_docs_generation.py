import shutil
import subprocess
import sys
from pathlib import Path


def test_generate_python_api_docs():
    project_root = Path(__file__).resolve().parents[2]
    docs_dir = project_root / "docs" / "api"

    if docs_dir.exists():
        shutil.rmtree(docs_dir)

    result = subprocess.run(
        [sys.executable, "scripts/generate_api_docs.py"],
        cwd=project_root,
        capture_output=True,
        text=True,
    )

    assert result.returncode == 0, result.stderr or result.stdout

    target_file = docs_dir / "common-features" / "basics" / "session.md"
    assert target_file.exists(), "Session documentation was not generated"
    contents = target_file.read_text(encoding="utf-8")
    assert "# Session API Reference" in contents
    assert "Documentation generated automatically" in contents
