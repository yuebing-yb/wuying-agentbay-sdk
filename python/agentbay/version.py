# -*- coding: utf-8 -*-
"""Version information for the AgentBay SDK."""

import os
from pathlib import Path


def _get_version_from_pyproject() -> str:
    """Read version from pyproject.toml file."""
    try:
        # Get the path to pyproject.toml (relative to this file)
        current_dir = Path(__file__).parent
        pyproject_path = current_dir.parent / "pyproject.toml"
        
        if pyproject_path.exists():
            with open(pyproject_path, "r", encoding="utf-8") as f:
                for line in f:
                    if line.strip().startswith("version = "):
                        # Extract version from: version = "0.9.3"
                        version = line.split("=")[1].strip().strip('"')
                        return version
    except Exception:
        pass
    
    # Fallback version if pyproject.toml cannot be read
    return "0.9.3"


def _is_release_build() -> bool:
    """
    Check if this is a release build.
    Returns True only if built by official release workflows:
    - manual_publish_prod.yml
    """
    # Check if running in GitHub Actions
    if os.environ.get("GITHUB_ACTIONS") != "true":
        return False
    
    # Check if triggered by manual_publish_prod workflow
    workflow = os.environ.get("GITHUB_WORKFLOW", "")
    if "Manual Publish to PyPI" in workflow:
        return True
    
    # Check for AGENTBAY_RELEASE_BUILD environment variable
    # This can be set in CI/CD for release builds
    if os.environ.get("AGENTBAY_RELEASE_BUILD") == "true":
        return True
    
    return False


__version__ = _get_version_from_pyproject()
__is_release__ = _is_release_build()

