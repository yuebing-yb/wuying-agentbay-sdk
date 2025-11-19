import os
import asyncio
import time
import traceback
from typing import List, Dict, Any
from dotenv import load_dotenv
from pathlib import Path
from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.tools import Tool
from langchain.agents import create_agent
from langgraph.store.memory import InMemoryStore

# Load environment variables
load_dotenv()


def create_real_session():
    """Create a real AgentBay browser session."""
    try:
        from agentbay import AgentBay
        from agentbay.session_params import CreateSessionParams
        
        print("Creating AgentBay browser session...")
        agent_bay = AgentBay()
        session_params = CreateSessionParams(image_id="browser_latest")
     
        result = agent_bay.create(session_params)

        if result.success:
            print(f"Session created successfully with ID: {result.session.session_id}")
            # Store session data in the store
            return agent_bay, result.session
        else:
            raise Exception(f"Failed to create session: {result.error_message}")
    except ImportError:
        raise ImportError("AgentBay SDK not available. Please install agentbay package.")


class BrowserIntegrationToolkit:
    """Toolkit for browser operations in AgentBay sessions.
    
    This toolkit provides tools for interacting with browser environments in AgentBay.
    It requires a browser session created with image_id="browser_latest".
    """
    
    def __init__(self) -> None:
        """Initialize without a browser session.
        
        Session is managed via runtime store.
        """
        self.browser = None
        self.playwright = None
        
    def initialize_browser(self, session):
        """Initialize browser with actual browser connection.
        
        This method must be called before using browser tools.
        
        Args:
            session: AgentBay session object
            
        Returns:
            Browser context object
        """
        try:
            from agentbay.browser.browser import BrowserOption
            
            # Initialize browser
            init_result = session.browser.initialize(BrowserOption())
            if not init_result:
                raise Exception("Failed to initialize browser")
            
            return init_result
        except ImportError:
            raise ImportError(
                "Browser dependencies not available. Please install agentbay package."
            )
        except Exception as e:
            raise Exception(f"Failed to initialize browser: {str(e)}")

    def cleanup_browser(self):
        """Clean up browser resources.
        
        This method should be called when finished using browser tools.
        """
        # 在我们的实现中，清理工作由AgentBay SDK处理
        pass
        
    def get_tools(self) -> List:
        """Get the tools in the toolkit."""
        # Import tools here to avoid circular imports
        try:
            from browser_tools import (
                browser_navigate,
                browser_act,
                browser_screenshot,
                browser_wait
            )
            
            # Create tools with session context
            tools = [
                browser_navigate,
                browser_act,
                browser_screenshot,
                browser_wait
            ]
            
            # Return tools
            return tools
        except ImportError as e:
            print(f"Warning: Could not import browser tools: {e}")
            return []


# Session data class to store session information in the store


def create_form_filling_tools():
    """
    Create LangChain tools for the form filling agent.
    
    Returns:
        List of LangChain tools
    """
    # Create browser integration toolkit and get browser tools
    browser_toolkit = BrowserIntegrationToolkit()
    tools = browser_toolkit.get_tools()
    
    return tools


def create_langchain_form_filling_agent():
    """
    Create a LangChain form filling agent with tools.
    
    Returns:
        dict: Dictionary containing the agent and store
    """
    # Create a real AgentBay browser session
    agent_bay, session = create_real_session()
    
    # Create tools
    tools = create_form_filling_tools()
    
    # Create memory store
    store = InMemoryStore()
    
    # Store session data in the store so tools can access it
    from browser_tools import BrowserSessionData
    session_data = BrowserSessionData(session=session, session_id=session.session_id)
    store.put(("browser_session",), "default", session_data)
    
    # Initialize browser with the session
    toolkit = BrowserIntegrationToolkit()
    toolkit.initialize_browser(session)
    
    # Create the LangChain agent
    llm = ChatOpenAI(
        api_key=os.getenv("DASHSCOPE_API_KEY"),
        base_url="https://dashscope.aliyuncs.com/compatible-mode/v1",
        model=os.getenv("DASHSCOPE_MODEL", "qwen3-max")
    )
    
    # System prompt for the agent
    system_prompt = f"""
    You are an AI assistant that helps interact with websites. You have access to the following tools:
    
    1. browser_navigate - Navigate to a URL in the browser
    2. browser_act - Perform an action on the current web page
    3. browser_screenshot - Take a screenshot of the current browser page
    """
    
    # Create the agent with tools
    langchain_agent = create_agent(
        llm,
        tools=tools,
        store=store,
        system_prompt=system_prompt
    )
    
    return {
        "agent": langchain_agent,
        "store": store,
        "toolkit":toolkit
    }