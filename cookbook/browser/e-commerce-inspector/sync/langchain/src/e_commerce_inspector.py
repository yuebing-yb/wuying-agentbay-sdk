"""
E-commerce Inspector Agent using LangChain and AgentBay SDK.
This agent can automatically inspect e-commerce websites and extract product information.
"""

import json
import time
from typing import List, Optional
from langgraph.prebuilt import create_react_agent
from langchain_core.tools import StructuredTool
from langchain_core.language_models import BaseChatModel

from agentbay import AgentBay, CreateSessionParams, BrowserOption, BrowserScreen, Session

from inspector_tools import process_site


class ECommerceInspector:
    """E-commerce inspector agent that can extract product information from websites."""

    def __init__(
        self,
        llm: BaseChatModel,
        agentbay_api_key: str,
        output_dir: str = "./data"
    ):
        """
        Initialize the e-commerce inspector agent.

        Args:
            llm: Language model for the agent
            agentbay_api_key: AgentBay API key
            output_dir: Directory to save inspection results
        """
        self.llm = llm
        self.agentbay_api_key = agentbay_api_key
        self.output_dir = output_dir
        self.session: Optional[Session] = None
        self.agent_executor = None

    def initialize(self):
        """Initialize the AgentBay session and browser."""
        print("Initializing AgentBay session...")
        agent_bay = AgentBay(api_key=self.agentbay_api_key)

        params = CreateSessionParams(image_id="browser_latest")
        session_result = agent_bay.create(params)

        if not session_result.success:
            raise RuntimeError(f"Failed to create session: {session_result.error_message}")

        self.session = session_result.session
        print(f"Session created with ID: {self.session.session_id}")

        # Initialize browser
        screen_option = BrowserScreen(width=1920, height=1080)
        browser_init_options = BrowserOption(
            screen=screen_option,
            solve_captchas=True,
        )

        ok = self.session.browser.initialize(browser_init_options)
        if not ok:
            raise RuntimeError("Failed to initialize browser")

        print("Browser initialized successfully")

        # Create LangChain tools
        self._create_tools()

    def _create_tools(self):
        """Create LangChain tools for the agent."""

        def inspect_website(url: str) -> str:
            """
            Inspect an e-commerce website and extract product information.

            Args:
                url: The URL of the e-commerce website to inspect

            Returns:
                A summary of the inspection results
            """
            if not self.session:
                return "Error: Session not initialized"

            try:
                result = process_site(
                    self.session.browser.agent,
                    url,
                    out_dir=self.output_dir
                )

                if result["success"]:
                    return (
                        f"Successfully inspected {result['host']}. "
                        f"Found {result['product_count']} products. "
                        f"Results saved to: {result['output_file']}"
                    )
                else:
                    error_msg = result.get("error", "Unknown error")
                    return f"Failed to inspect {result['host']}: {error_msg}"

            except Exception as e:
                return f"Error inspecting {url}: {str(e)}"

        def inspect_multiple_websites(urls: str) -> str:
            """
            Inspect multiple e-commerce websites and extract product information.

            Args:
                urls: Comma-separated list of URLs to inspect

            Returns:
                A summary of all inspection results
            """
            if not self.session:
                return "Error: Session not initialized"

            url_list = [u.strip() for u in urls.split(",")]
            results = []

            for url in url_list:
                try:
                    result = process_site(
                        self.session.browser.agent,
                        url,
                        out_dir=self.output_dir
                    )
                    results.append(result)
                except Exception as e:
                    results.append({
                        "url": url,
                        "success": False,
                        "error": str(e)
                    })

            # Create summary
            total = len(results)
            successful = sum(1 for r in results if r["success"])
            total_products = sum(r.get("product_count", 0) for r in results)

            summary = f"Inspected {total} websites. {successful} successful. Total products found: {total_products}\n\n"
            for r in results:
                if r["success"]:
                    summary += f"✓ {r['host']}: {r['product_count']} products\n"
                else:
                    summary += f"✗ {r.get('host', r['url'])}: {r.get('error', 'Failed')}\n"

            return summary

        # Create tools
        self.tools = [
            StructuredTool.from_function(
                func=inspect_website,
                name="inspect_website",
                description="Inspect a single e-commerce website and extract product information including names, prices, and links"
            ),
            StructuredTool.from_function(
                func=inspect_multiple_websites,
                name="inspect_multiple_websites",
                description="Inspect multiple e-commerce websites at once. Provide URLs as comma-separated list"
            )
        ]

        # Create agent using langgraph
        system_message = """You are an e-commerce inspector agent. You can inspect e-commerce websites and extract product information.

Your capabilities:
- Extract product names, prices, and links from e-commerce websites
- Handle multiple websites in batch
- Navigate to product listing pages automatically
- Save results to JSON files with screenshots

When inspecting websites:
1. Use the inspect_website tool for single sites
2. Use the inspect_multiple_websites tool for multiple sites
3. Provide clear summaries of what was found

Always be helpful and provide detailed information about the inspection results."""

        self.agent_executor = create_react_agent(
            self.llm,
            self.tools,
            prompt=system_message
        )

    def run(self, task: str) -> str:
        """
        Run the inspector agent with a given task.

        Args:
            task: The task description (e.g., "Inspect https://example.com")

        Returns:
            The agent's response
        """
        if not self.agent_executor:
            raise RuntimeError("Agent not initialized. Call initialize() first.")

        result = self.agent_executor.invoke({"messages": [("user", task)]})
        # Extract the last message from the agent
        messages = result.get("messages", [])
        if messages:
            last_message = messages[-1]
            return last_message.content if hasattr(last_message, 'content') else str(last_message)
        return "No response from agent"

    def cleanup(self):
        """Clean up resources."""
        if self.session:
            try:
                self.session.browser.agent.close()
            except Exception:
                pass

            try:
                agent_bay = AgentBay(api_key=self.agentbay_api_key)
                agent_bay.delete(self.session)
                print(f"Session {self.session.session_id} deleted")
            except Exception as e:
                print(f"Warning: Failed to delete session: {e}")

    def __enter__(self):
        """Context manager entry."""
        self.initialize()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit."""
        self.cleanup()

