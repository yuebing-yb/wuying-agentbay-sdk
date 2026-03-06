"""
Web Scraping Pipeline with AgentBay Browser Operator

This example demonstrates how to build a complete web scraping pipeline
using a cloud browser:

  1. Initialize a cloud browser with stealth mode
  2. Navigate to a target website
  3. Extract structured data using AI-powered extraction
  4. Save results to the cloud file system
  5. Process data with command-line tools
  6. (Bonus) Perform search + extraction from a search engine

Target: quotes.toscrape.com (a practice site designed for web scraping)

Prerequisites:
  - pip install wuying-agentbay-sdk pydantic
  - export AGENTBAY_API_KEY=your_api_key_here
"""

import os
import sys
import asyncio
import json
import base64

from pydantic import BaseModel
from typing import List

from agentbay import AsyncAgentBay, CreateSessionParams
from agentbay._common.models.browser_operator import ExtractOptions, ActOptions
from agentbay._common.models.browser import BrowserOption


IMAGES_DIR = os.path.join(os.path.dirname(__file__), "..", "images")
os.makedirs(IMAGES_DIR, exist_ok=True)


class Quote(BaseModel):
    """A single quote with its author."""
    text: str
    author: str


class QuoteList(BaseModel):
    """Collection of quotes extracted from a page."""
    quotes: List[Quote]


class SearchResult(BaseModel):
    """A search engine result."""
    title: str
    url: str


class SearchResultList(BaseModel):
    """Collection of search results."""
    results: List[SearchResult]


async def save_browser_screenshot(session, name: str):
    """Capture and save a browser screenshot."""
    try:
        data_url = await session.browser.operator.screenshot()
        if data_url and "," in data_url:
            img_data = base64.b64decode(data_url.split(",", 1)[1])
            path = os.path.join(IMAGES_DIR, f"{name}.png")
            with open(path, "wb") as f:
                f.write(img_data)
            print(f"  Screenshot saved: {name}.png ({len(img_data):,} bytes)")
    except Exception as e:
        print(f"  Screenshot failed: {e}")


async def main():
    api_key = os.getenv("AGENTBAY_API_KEY")
    if not api_key:
        print("Error: Please set the AGENTBAY_API_KEY environment variable")
        sys.exit(1)

    agent_bay = AsyncAgentBay(api_key=api_key)
    session = None

    try:
        # Step 1: Create session and initialize browser
        print("Step 1: Creating session and initializing browser...")
        result = await agent_bay.create(
            CreateSessionParams(image_id="linux_latest")
        )
        if not result.success:
            print(f"  Failed: {result.error_message}")
            return
        session = result.session
        print(f"  Session: {session.session_id}")

        option = BrowserOption(use_stealth=True)
        await session.browser.initialize(option)
        print("  Browser initialized with stealth mode")

        # Step 2: Navigate to target website
        print("\nStep 2: Navigating to quotes.toscrape.com...")
        await session.browser.operator.navigate("https://quotes.toscrape.com")
        await asyncio.sleep(3)
        await save_browser_screenshot(session, "01_quotes_page")

        # Step 3: Extract structured data
        print("\nStep 3: Extracting quotes with AI-powered extraction...")
        extract_options = ExtractOptions(
            instruction="Extract all quotes and their authors from this page. "
                        "Each quote has a text and an author name.",
            schema=QuoteList,
            use_text_extract=True,
        )

        success, data = await session.browser.operator.extract(extract_options)
        if success and data and data.quotes:
            print(f"  Extracted {len(data.quotes)} quotes:")
            for i, q in enumerate(data.quotes[:5], 1):
                print(f"    {i}. \"{q.text[:60]}...\" — {q.author}")
            if len(data.quotes) > 5:
                print(f"    ... and {len(data.quotes) - 5} more")
        else:
            print("  No quotes extracted")
            return

        # Step 4: Save to cloud file system
        print("\nStep 4: Saving data to cloud file system...")
        json_data = json.dumps(
            [q.model_dump() for q in data.quotes],
            ensure_ascii=False,
            indent=2,
        )
        write_result = await session.file_system.write_file(
            "/tmp/quotes.json", json_data
        )
        print(f"  Write: success={write_result.success}")

        read_result = await session.file_system.read_file("/tmp/quotes.json")
        if read_result.success:
            print(f"  Verified: {len(read_result.content)} chars written")

        # Step 5: Process data with command-line tools
        print("\nStep 5: Processing data with command-line tools...")
        analysis_script = (
            "import json\n"
            "data = json.load(open('/tmp/quotes.json'))\n"
            "authors = {}\n"
            "for q in data:\n"
            "    a = q['author']\n"
            "    authors[a] = authors.get(a, 0) + 1\n"
            "print(f'Total quotes: {len(data)}')\n"
            "print(f'Unique authors: {len(authors)}')\n"
            "print('Top authors:')\n"
            "for a, c in sorted(authors.items(), key=lambda x: -x[1])[:5]:\n"
            "    print(f'  {a}: {c} quote(s)')\n"
        )
        cmd = await session.command.execute_command(
            f"python3 << 'PYEOF'\n{analysis_script}PYEOF",
            timeout_ms=10000,
        )
        if cmd.success and cmd.output:
            print(f"  Analysis results:")
            for line in cmd.output.strip().split("\n"):
                print(f"    {line}")
        else:
            print(f"  Analysis failed: {cmd.error_message}")

        # Step 6 (Bonus): Search engine scraping
        print("\nStep 6: Bonus — Search engine scraping...")
        await session.browser.operator.navigate("https://www.baidu.com")
        await asyncio.sleep(3)
        await save_browser_screenshot(session, "02_baidu_home")

        print("  Searching for 'Python web scraping'...")
        await session.browser.operator.act(
            ActOptions(action="在搜索框中输入 'Python web scraping' 然后点击搜索按钮")
        )
        await asyncio.sleep(5)
        await save_browser_screenshot(session, "03_search_results")

        print("  Extracting search results...")
        search_options = ExtractOptions(
            instruction="Extract all search result titles and their links "
                        "from this Baidu search results page.",
            schema=SearchResultList,
            use_text_extract=True,
        )
        s_ok, s_data = await session.browser.operator.extract(search_options)
        if s_ok and s_data and s_data.results:
            print(f"  Found {len(s_data.results)} search results:")
            for i, r in enumerate(s_data.results[:5], 1):
                print(f"    {i}. {r.title}")
        else:
            print("  No search results extracted")

        # Close browser
        print("\nClosing browser...")
        await session.browser.destroy()
        print("Browser closed.")

        # Summary
        print("\n" + "=" * 50)
        print("Pipeline completed successfully!")
        print("=" * 50)
        print(f"  Quotes extracted: {len(data.quotes)}")
        print(f"  Data saved to: /tmp/quotes.json")
        if s_ok and s_data:
            print(f"  Search results: {len(s_data.results)}")
        print(f"  Screenshots saved to: {IMAGES_DIR}")

    except Exception as e:
        print(f"\nError: {e}")
        import traceback
        traceback.print_exc()

    finally:
        if session:
            print("\nCleaning up session...")
            await agent_bay.delete(session)
            print("Session deleted.")


if __name__ == "__main__":
    asyncio.run(main())
