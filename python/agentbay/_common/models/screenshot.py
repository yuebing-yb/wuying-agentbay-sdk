"""
Shared screenshot-related models.
"""

from dataclasses import dataclass
from typing import Optional

from .response import BaseResult


@dataclass
class ScreenshotResult(BaseResult):
    """
    Result object containing screenshot data and metadata.

    Cloud (MCP tool) screenshot payload is expected to include:
    - type
    - data
    - mime_type
    - width
    - height
    """

    type: str = ""
    data: bytes = b""
    mime_type: str = ""
    width: Optional[int] = None
    height: Optional[int] = None

