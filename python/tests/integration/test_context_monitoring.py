import asyncio
import sys
import os
import pytest
import importlib.util
from pathlib import Path

# Add project root to path
PROJECT_ROOT = Path(__file__).resolve().parents[3]
sys.path.append(str(PROJECT_ROOT))

from agentbay._common.exceptions import AgentBayError

@pytest.mark.asyncio
async def test_context_sync_monitoring_example():
    """
    Integration test for context_sync_monitoring_example.py
    This test executes the main function of the example script.
    """
    # Path to the example file
    example_path = PROJECT_ROOT / "python/docs/examples/_async/common-features/basics/data_persistence/context_sync_monitoring_example.py"
    
    assert example_path.exists(), f"Example file not found at {example_path}"
    
    # Load the module dynamically
    spec = importlib.util.spec_from_file_location("context_sync_monitoring_example", example_path)
    module = importlib.util.module_from_spec(spec)
    sys.modules["context_sync_monitoring_example"] = module
    spec.loader.exec_module(module)
    
    # Run the main function
    try:
        await module.main()
    except Exception as e:
        pytest.fail(f"Example execution failed: {e}")

