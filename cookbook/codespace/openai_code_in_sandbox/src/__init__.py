"""
Source package for OpenAI Code in Sandbox executables
"""

import sys
from pathlib import Path

# Add parent directory to Python path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

# Import from parent directory
from qwen_code_installer import QwenCodeGenerator

__all__ = ['QwenCodeGenerator']
