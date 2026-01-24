#!/usr/bin/env python3
"""
Qwen Code Generator Execution Entry Point
Execute code generation workflow based on Alibaba Cloud Qwen
"""

import asyncio
import os
import sys

try:
    # Try relative import first (when run as module)
    from . import QwenCodeGenerator
except ImportError:
    try:
        # Fallback to direct import from __init__.py setup
        import sys
        from pathlib import Path
        
        # Add parent directory to Python path
        parent_dir = Path(__file__).parent.parent
        if str(parent_dir) not in sys.path:
            sys.path.insert(0, str(parent_dir))
        
        from qwen_code_installer import QwenCodeGenerator
    except ImportError as e:
        print(f"❌ Error: Cannot import QwenCodeGenerator: {e}")
        print("Please ensure qwen_code_installer.py file is in the parent directory")
        print("Or ensure dependencies are properly installed: pip install -r requirements.txt")
        print()
        print("💡 Alternative: Run as module from parent directory:")
        print("   python -m openai_code_in_sandbox.src.run_qwen_code_generator")
        sys.exit(1)


async def main():
    """Main execution function"""
    print("🌟 Qwen Code Generator")
    print("=" * 60)
    
    # Check environment variables
    agentbay_api_key = os.getenv('AGENTBAY_API_KEY')
    dashscope_api_key = os.getenv('DASHSCOPE_API_KEY')
    
    if not agentbay_api_key:
        print("❌ Error: AGENTBAY_API_KEY environment variable not found")
        print("Please set environment variable: export AGENTBAY_API_KEY='your-api-key'")
        print()
        print("💡 Tip: You can set environment variables as follows:")
        print("   Linux/macOS: export AGENTBAY_API_KEY='your-api-key'")
        print("   Windows:     set AGENTBAY_API_KEY=your-api-key")
        return False
    
    if not dashscope_api_key:
        print("⚠️ Warning: DASHSCOPE_API_KEY environment variable not found")
        print("Will try to read from cloud environment, or please set: export DASHSCOPE_API_KEY='your-api-key'")
        print()
    
    # Get user input for code generation requirements
    if len(sys.argv) > 1:
        prompt = " ".join(sys.argv[1:])
    else:
        print("📝 Please enter your code generation requirements (press Enter to use default example):")
        user_input = input().strip()
        if user_input:
            prompt = user_input
        else:
            prompt = "Create a beautiful hello world HTML page with CSS styling and JavaScript animations"
    
    print(f"🎯 Code generation requirement: {prompt}")
    print()
    
    try:
        # Create generator instance
        generator = QwenCodeGenerator(
            api_key=agentbay_api_key,
            dashscope_api_key=dashscope_api_key
        )
        
        # Run full workflow
        success = await generator.run_full_workflow(prompt)
        
        if success:
            print("🎊 Qwen code generation workflow completed!")
            return True
        else:
            print("💥 Workflow execution failed")
            return False
            
    except Exception as e:
        print(f"❌ Main program exception: {str(e)}")
        return False


def show_usage():
    """Show usage instructions"""
    print("📖 Qwen Code Generator Usage Guide")
    print("=" * 50)
    print()
    print("🔧 Environment Setup:")
    print("1. Install dependencies: pip install wuying-agentbay-sdk>=0.10.0 openai")
    print("2. Set AgentBay API key:")
    print("   export AGENTBAY_API_KEY='your-agentbay-api-key'")
    print("3. Set DashScope API key:")
    print("   export DASHSCOPE_API_KEY='your-dashscope-api-key'")
    print()
    print("🚀 Usage:")
    print("   python run_qwen_code_generator.py")
    print("   python run_qwen_code_generator.py \"Create a responsive login page\"")
    print()
    print("📋 Execution Flow:")
    print("1. Create AgentBay cloud environment session")
    print("2. Set up Python environment and dependencies")
    print("3. Configure DashScope API key")
    print("4. Generate code using Qwen")
    print("5. Save generated code files")
    print("6. Automatically clean up cloud environment")
    print()
    print("💰 Cost Advantages:")
    print("- Qwen is cheaper than Claude")
    print("- Supports Chinese prompts with better understanding")
    print("- More discounts for Alibaba Cloud users")
    print()
    print("🌟 Supported Code Types:")
    print("- HTML/CSS/JavaScript web pages")
    print("- Python scripts and applications")
    print("- Data analysis and visualization")
    print("- API interface development")
    print("- Algorithms and data structures")


def show_examples():
    """Show usage examples"""
    print("💡 Qwen Code Generation Examples")
    print("=" * 40)
    print()
    print("🌐 Web Development:")
    print('   python run_qwen_code_generator.py "Create a modern personal resume webpage"')
    print('   python run_qwen_code_generator.py "Build a responsive product showcase page"')
    print()
    print("🐍 Python Development:")
    print('   python run_qwen_code_generator.py "Write a batch file renaming tool"')
    print('   python run_qwen_code_generator.py "Create a simple todo list manager"')
    print()
    print("📊 Data Analysis:")
    print('   python run_qwen_code_generator.py "Generate sales data visualization charts"')
    print('   python run_qwen_code_generator.py "Write a stock price analysis script"')
    print()
    print("🎮 Fun Projects:")
    print('   python run_qwen_code_generator.py "Create a simple number guessing game"')
    print('   python run_qwen_code_generator.py "Build a colorful clock webpage"')


if __name__ == "__main__":
    # Check command line arguments
    if len(sys.argv) > 1:
        if sys.argv[1] in ['-h', '--help', 'help']:
            show_usage()
            sys.exit(0)
        elif sys.argv[1] in ['-e', '--examples', 'examples']:
            show_examples()
            sys.exit(0)
        elif sys.argv[1] in ['-v', '--version', 'version']:
            print("Qwen Code Generator v1.0.0")
            print("Based on wuying-agentbay-sdk>=0.10.0 and Alibaba Cloud Qwen")
            sys.exit(0)
    
    # Run main program
    print("🎬 Starting Qwen Code Generator...")
    print()
    
    try:
        success = asyncio.run(main())
        sys.exit(0 if success else 1)
    except KeyboardInterrupt:
        print("\n⚠️ User interrupted execution")
        sys.exit(130)
    except Exception as e:
        print(f"\n❌ Program execution exception: {str(e)}")
        sys.exit(1)
