import os
import sys
import time
import pytest
from typing import Any, Dict

# Add the parent directory to the Python path to find agentbay module
current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(os.path.dirname(current_dir))
if parent_dir not in sys.path:
    sys.path.insert(0, parent_dir)

from agentbay import AsyncAgentBay
from agentbay import CreateSessionParams


def get_api_key():
    """Get API key for testing"""
    api_key = os.getenv("AGENTBAY_API_KEY")
    if not api_key:
        pytest.skip("AGENTBAY_API_KEY environment variable not set")
    return api_key


@pytest.mark.asyncio
async def test_vpc_session_basic_tools():
    """Test VPC session creation and filesystem write/read functionality"""
    # Skip VPC tests as they require special environment setup
    # VPC mode requires specific images and network configuration
    pytest.skip("VPC session tests require special environment setup and VPC-compatible images")
