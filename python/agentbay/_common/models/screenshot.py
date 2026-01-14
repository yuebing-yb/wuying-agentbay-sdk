"""
Shared screenshot-related models.
"""

from dataclasses import dataclass

from .response import BaseResult


@dataclass
class ScreenshotResult(BaseResult):
    """Result object containing screenshot data."""

    data: bytes = b""
    format: str = "png"

