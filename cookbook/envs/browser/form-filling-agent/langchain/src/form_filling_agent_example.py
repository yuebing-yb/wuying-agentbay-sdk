import os
import sys
import traceback

# Add the project root to the path so we can import from common
project_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
common_path = os.path.join(project_root, "common", "src")
sys.path.insert(0, common_path)

def main():
    """
    Main function to demonstrate LangChain orchestration of form filling agent.
    """
    print("Creating LangChain form filling agent...")
    
    # Import the agent creator function
    from form_filling_agent import create_langchain_form_filling_agent
    
    try:
        # Create the LangChain agent
        agent_dict = create_langchain_form_filling_agent()
        agent = agent_dict["agent"]
        
        # URL to navigate to
        url = "https://data.stats.gov.cn/easyquery.htm?cn=C01"
        
        print(f"Website URL: {url}")
        
        # Example Using the agent with custom instructions
        print("\n=== Example: Using agent with custom instructions ===")
        # Execute the agent with context
        content = f"""
            First navigate to the website at {url}, 
            then open the time selector, select 最近10年，wait for 3 seconds,
            then click Line chart icon，wait for 3 seconds, 
            save the snapshot to ./data/filled_page_screenshot.png
        """
        result = agent.invoke(
            {"messages": [{"role": "user", "content": content}]},
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
        print(f"Error: {e}")
        traceback.print_exc()


if __name__ == "__main__":
    main()