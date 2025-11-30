#!/usr/bin/env python3
"""
Langchain Example for Auto Testing Agent (Async)
Demonstrates how to use the testing agent with Langchain asynchronously.
"""

import os
import sys
import asyncio
import traceback
from typing import List
from dotenv import load_dotenv

# Add the current and common directories to sys.path to enable imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__)))
sys.path.insert(1, os.path.join(os.path.dirname(__file__), '..', '..', 'common', 'src'))

from auto_testing_agent import create_langchain_agent


# Load environment variables
load_dotenv()


async def main():
    """Main function demonstrating the Langchain integration."""
    # Get API keys from environment variables
    agentbay_api_key = os.getenv("AGENTBAY_API_KEY")
    dashscope_api_key = os.getenv("DASHSCOPE_API_KEY")
    
    if not agentbay_api_key:
        print("Error: AGENTBAY_API_KEY environment variable must be set")
        return
    
    if not dashscope_api_key:
        print("Error: DASHSCOPE_API_KEY environment variable must be set")
        return

    try:
        # Create Langchain agent
        agent_dict = create_langchain_agent(api_key=agentbay_api_key)
        agent = agent_dict["agent"]
        
        # Get current script path and construct sample project path
        current_script_dir = os.path.dirname(os.path.abspath(__file__))
        sample_project_path = os.path.join(current_script_dir, "..", "..", "common", "sample_project")
        
        # Run agent on sample project
        project_path = os.getenv("PROJECT_PATH", sample_project_path)
        
        # Execute the agent with context
        result = await agent.ainvoke(
            {"messages": [{"role": "user", "content": f"Test the Python project at {project_path}. First scan the project structure, then generate tests, and finally execute them."}]},
            {"recursion_limit": 500}
        )
        
        # Extract and print the final output
        if "messages" in result and len(result["messages"]) > 0:
            final_message = result["messages"][-1]
            if hasattr(final_message, 'content') and final_message.content:
                print("Final result:", final_message.content)
            else:
                print("Final result:", final_message)
        else:
            print("Final result:", result)
    except Exception as e:
        print(f"Error running auto tests: {e}")
        traceback.print_exc()


if __name__ == "__main__":
    asyncio.run(main())
