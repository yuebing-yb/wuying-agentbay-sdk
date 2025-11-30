"""
Example script demonstrating the E-commerce Inspector Agent.
This script shows how to use the agent to inspect e-commerce websites and extract product information.
"""

import os
from langchain_community.chat_models import ChatTongyi


def main():
    # Get API keys from environment variables
    agentbay_api_key = os.getenv("AGENTBAY_API_KEY")
    dashscope_api_key = os.getenv("DASHSCOPE_API_KEY")

    if not agentbay_api_key:
        print("Error: AGENTBAY_API_KEY environment variable not set")
        return

    if not dashscope_api_key:
        print("Error: DASHSCOPE_API_KEY environment variable not set")
        return

    # Initialize LLM
    print("Initializing LLM...")
    llm = ChatTongyi(
        model="qwen-plus",
        dashscope_api_key=dashscope_api_key,
        temperature=0
    )

    # Import the inspector
    from e_commerce_inspector import ECommerceInspector

    # Create and use the inspector
    with ECommerceInspector(
        llm=llm,
        agentbay_api_key=agentbay_api_key,
        output_dir="./data"
    ) as inspector:
        print("\n" + "="*80)
        print("E-commerce Inspector Agent Ready!")
        print("="*80 + "\n")

        # Example 1: Inspect a single website
        print("\n--- Example 1: Inspect a single e-commerce website ---\n")
        task1 = "Please inspect the website https://waydoo.com/collections/all and extract all product information"
        result1 = inspector.run(task1)
        print(f"\nResult:\n{result1}\n")

        # Example 2: Inspect multiple websites
        # Uncomment to test with multiple sites
        # print("\n--- Example 2: Inspect multiple e-commerce websites ---\n")
        # task2 = "Please inspect these websites: https://example1.com, https://example2.com"
        # result2 = inspector.run(task2)
        # print(f"\nResult:\n{result2}\n")

        print("\n" + "="*80)
        print("Inspection completed! Check the ./data directory for results.")
        print("="*80 + "\n")


if __name__ == "__main__":
    main()

