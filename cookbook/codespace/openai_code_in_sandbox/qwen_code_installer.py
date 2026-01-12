#!/usr/bin/env python3
"""
Qwen Code Generator
Generate code using Alibaba Cloud Qwen model in AgentBay cloud environment
"""

import asyncio
import os
import sys
import json
from typing import Optional

try:
    from agentbay import AsyncAgentBay, CreateSessionParams
    from openai import OpenAI
except ImportError as e:
    print(f"Error: Cannot import dependencies: {e}")
    print("Please ensure the following dependencies are installed:")
    print("pip install wuying-agentbay-sdk>=0.10.0 openai")
    sys.exit(1)

class QwenCodeGenerator:
    """Qwen Code Generator"""
    
    def __init__(self, api_key: Optional[str] = None, dashscope_api_key: Optional[str] = None):
        """
        Initialize the generator
        
        Args:
            api_key: AgentBay API key
            dashscope_api_key: Alibaba Cloud DashScope API key
        """
        self.api_key = api_key or os.getenv('AGENTBAY_API_KEY')
        self.dashscope_api_key = dashscope_api_key or os.getenv('DASHSCOPE_API_KEY')
        self.agent_bay = None
        self.session = None
        self.llm_client = None
        
        if not self.api_key:
            raise ValueError("AgentBay API key is required")
        
        if not self.dashscope_api_key:
            print("Warning: DashScope API key not provided, will try to read from cloud environment")
    
    async def create_session(self) -> bool:
        """Create cloud environment session"""
        try:
            print("🚀 Creating AgentBay cloud environment session...")
            
            self.agent_bay = AsyncAgentBay(api_key=self.api_key)
            
            # Create session parameters
            session_params = CreateSessionParams(
                image_id='code_latest',  # Use latest code environment
            )
            
            # Create session
            result = await self.agent_bay.create(session_params)
            
            if not result.success:
                print(f"❌ Failed to create session: {result.error_message}")
                return False
            
            self.session = result.session
            print(f"✅ Session created successfully, session ID: {self.session.session_id}")
            return True
            
        except Exception as e:
            print(f"❌ Session creation exception: {str(e)}")
            return False
    
    async def setup_python_environment(self) -> bool:
        """Set up Python environment and dependencies"""
        try:
            print("🔧 Setting up Python environment...")
            
            # Install necessary Python packages
            # Only install core packages: openai (required)
            install_result = await self.session.command.execute_command(
                "pip install openai"
            )
            
            if not install_result.success or install_result.exit_code != 0:
                print(f"⚠️ Package installation warning: {install_result.output}")
            else:
                print("✅ Python dependencies installed successfully")
            
            return True
            
        except Exception as e:
            print(f"❌ Python environment setup exception: {str(e)}")
            return False
    
    
    async def generate_code_with_qwen(self, prompt: str) -> bool:
        """Generate code using Qwen"""
        try:
            print("🎯 Generating code using Qwen...")
            
            # Create working directory
            mkdir_result = await self.session.command.execute_command("mkdir -p /workspace/qwen-output")
            print(f"Create working directory: {mkdir_result.success}")
            
            # Verify API key availability
            print("🔑 Verifying API key...")
            if not self.dashscope_api_key:
                print("❌ DashScope API key not found")
                return False
            
            # Create code generation script in cloud environment
            code_generator_script = f'''
import os
from openai import OpenAI

# Create OpenAI client using DashScope compatible interface
# API key is passed through environment variables, error if environment variable is empty
dashscope_key = os.environ.get("DASHSCOPE_API_KEY")
if not dashscope_key:
    print("❌ Error: DASHSCOPE_API_KEY environment variable not found")
    print("Please ensure environment variables are set correctly when executing the script")
    exit(1)

client = OpenAI(
    api_key=dashscope_key,
    base_url="https://dashscope.aliyuncs.com/compatible-mode/v1",
)
# System prompt
system_prompt = """You are a professional code generation assistant. Please generate high-quality code based on user requirements.
Requirements:
1. Code should be concise and readable
2. Include necessary comments
3. Handle possible exceptions
4. If it's web-related code, generate complete HTML structure
"""

try:
    print("🤖 Calling Qwen to generate code...")
    
    completion = client.chat.completions.create(
        model="qwen3-max",
        messages=[
            {{"role": "system", "content": system_prompt}},
            {{"role": "user", "content": "{prompt}"}}
        ],
        temperature=0.7,
        max_tokens=2000
    )
    
    generated_code = completion.choices[0].message.content
    print("✅ Code generation successful!")
    print("=" * 60)
    print("Generated code:")
    print("=" * 60)
    print(generated_code)
    print("=" * 60)
    
    # Save generated code to file
    if "html" in "{prompt}".lower():
        filename = "generated_page.html"
    elif "python" in "{prompt}".lower():
        filename = "generated_code.py"
    else:
        filename = "generated_code.txt"
    
    with open(f"/workspace/qwen-output/{{filename}}", "w", encoding="utf-8") as f:
        f.write(generated_code)
    
    print(f"📁 Code saved to: /workspace/qwen-output/{{filename}}")
    
except Exception as e:
    print(f"❌ Code generation failed: {{str(e)}}")
'''
            
            # Write script to cloud environment
            script_result = await self.session.file_system.write_file(
                path="/workspace/qwen-output/generate_code.py",
                content=code_generator_script,
                mode="overwrite"
            )
            
            if not script_result.success:
                print(f"❌ Script write failed: {script_result.error_message}")
                return False
            
            # Execute code generation script
            print("🔄 Executing code generation...")
            
            # Check if python3 exists, use python if not
            print("🔍 Checking Python command...")
            python_check = await self.session.command.execute_command("which python3")
            
            if python_check.success and python_check.exit_code == 0:
                python_cmd = "python3"
                print("✅ Using python3 command")
            else:
                print("⚠️ python3 not found, trying python")
                python_fallback_check = await self.session.command.execute_command("which python")
                if python_fallback_check.success and python_fallback_check.exit_code == 0:
                    python_cmd = "python"
                    print("✅ Using python command")
                else:
                    print("❌ No available Python command found")
                    return False
            
            # Execute script with detected Python command, set environment variables and execute in same command
            print(f"🚀 Executing Python script (with environment variables)...")
            result = await self.session.command.execute_command(
                f"cd /workspace/qwen-output && DASHSCOPE_API_KEY='{self.dashscope_api_key}' {python_cmd} generate_code.py"
            )
            
            print(f"Code generation execution result:")
            print(f"  success: {result.success}")
            print(f"  exit_code: {result.exit_code}")
            print(f"  output: {result.output}")
            
            if result.success and result.exit_code == 0:
                print("✅ Qwen code generation successful")
                
                # Check generated files
                ls_result = await self.session.command.execute_command("ls -la /workspace/qwen-output/")
                if ls_result.success:
                    print(f"📁 Generated files:\n{ls_result.output}")
                
                # Try to read generated file content
                for filename in ["generated_page.html", "generated_code.py", "generated_code.txt"]:
                    file_result = await self.session.file_system.read_file(f"/workspace/qwen-output/{filename}")
                    if file_result.success:
                        print(f"📝 Generated {filename} content:\n{file_result.content}")
                        break
                
                return True
            else:
                print(f"❌ Code generation execution failed")
                print(f"   Error output: {result.output}")
                print(f"   stderr: {result.stderr}")
                return False
                
        except Exception as e:
            print(f"❌ Code generation exception: {str(e)}")
            return False
    
    async def cleanup_and_delete(self) -> bool:
        """Clean up and delete cloud environment"""
        try:
            print("🧹 Cleaning up and deleting cloud environment...")
            
            if self.session:
                try:
                    await self.session.delete()
                    print("✅ Cloud environment deleted successfully")
                    return True
                except Exception as e:
                    print(f"❌ Cloud environment deletion failed: {str(e)}")
                    return False
            else:
                print("⚠️ No active session to delete")
                return True
                
        except Exception as e:
            print(f"❌ Cleanup exception: {str(e)}")
            return False
    
    async def run_full_workflow(self, prompt: str = "Create a beautiful hello world HTML page with CSS styling") -> bool:
        """Run complete workflow"""
        try:
            print("🎬 Starting Qwen code generation workflow...")
            print("=" * 60)
            
            # 1. Create cloud environment session
            if not await self.create_session():
                return False
            
            # 2. Set up Python environment
            if not await self.setup_python_environment():
                return False
            
            # 3. Generate code using Qwen
            if not await self.generate_code_with_qwen(prompt):
                return False
            
            print("=" * 60)
            print("🎉 All tasks completed successfully!")
            
            # Wait for user to view results
            print("⏳ Waiting 10 seconds before automatic environment cleanup...")
            await asyncio.sleep(10)
            
            return True
            
        except Exception as e:
            print(f"❌ Workflow exception: {str(e)}")
            return False
        finally:
            # Ensure resource cleanup
            if self.session:
                try:
                    await self.session.delete()
                except:
                    pass

# If running this file directly, prompt user to use dedicated execution file
if __name__ == "__main__":
    print("⚠️  Please use the dedicated execution file to run Qwen code generator:")
    print("   python run_qwen_code_generator.py")
    print()
    print("Or import this module for use in your code:")
    print("   from qwen_code_installer import QwenCodeGenerator")
    sys.exit(1)
