import os
import subprocess
import sys
import argparse
from typing import List, Dict, Any, Optional, TypedDict
import json

# Ensure we can import standard libraries. Langchain/Langgraph availability depends on environment.
print("🔍 正在检查Python环境和依赖...")
print(f"Python可执行文件: {sys.executable}")
print(f"Python版本: {sys.version}")
print(f"Python路径: {sys.path}")

    # Check each import individually for better error reporting
try:
    print("📦 正在导入langchain_openai...")
    from langchain_openai import ChatOpenAI
    print("✅ langchain_openai导入成功")
except ImportError as e:
    print(f"❌ langchain_openai导入失败: {e}")
    print("🔍 尝试替代导入方法...")
    try:
        import langchain_openai
        print("✅ 替代导入成功: import langchain_openai")
    except ImportError as e2:
        print(f"❌ 替代导入也失败了: {e2}")
        
        # List available packages
        import pkgutil
        print("📋 包含'langchain'的可用包:")
        for _, name, _ in pkgutil.iter_modules():
            if 'langchain' in name.lower():
                print(f"  - {name}")
        sys.exit(1)

try:
    print("📦 正在导入langgraph...")
    from langgraph.graph import StateGraph, END
    print("✅ langgraph导入成功")
except ImportError as e:
    print(f"❌ langgraph导入失败: {e}")
    sys.exit(1)

try:
    print("📦 正在导入langchain_core...")
    from langchain_core.prompts import ChatPromptTemplate
    print("✅ langchain_core导入成功")
except ImportError as e:
    print(f"❌ langchain_core导入失败: {e}")
    sys.exit(1)

print("✅ 所有必需的库都导入成功!")

print("🔍 正在检查环境变量...")
agentbay_key = os.environ.get("AGENTBAY_API_KEY")
dashscope_key = os.environ.get("DASHSCOPE_API_KEY")
print(f"AGENTBAY_API_KEY: {'✅ 已设置' if agentbay_key else '❌ 缺失'}")
print(f"DASHSCOPE_API_KEY: {'✅ 已设置' if dashscope_key else '❌ 缺失'}")

# Configuration
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
# Ideally we want to run this from project root, but we'll be robust
if os.path.basename(PROJECT_ROOT) == "scripts": 
    PROJECT_ROOT = os.path.dirname(PROJECT_ROOT)

TEST_DIR = os.path.join(PROJECT_ROOT, "python", "tests", "integration")
LLMS_FULL_PATH = os.path.join(PROJECT_ROOT, "llms-full.txt")
REPORT_FILE = os.path.join(PROJECT_ROOT, "test_report.md")

# State Definition
class TestResult(TypedDict):
    test_id: str
    status: str  # 'passed', 'failed', 'error'
    output: str
    error_analysis: Optional[str]

class AgentState(TypedDict):
    test_queue: List[str]
    current_test_index: int
    results: List[TestResult]
    sdk_context: str
    is_finished: bool
    specific_test_pattern: Optional[str]

# --- Helper Functions ---

def get_model():
    """Initializes the Qwen model via ChatOpenAI interface compatible with DashScope."""
    api_key = os.environ.get("DASHSCOPE_API_KEY")
    if not api_key:
        print("警告: 未找到DASHSCOPE_API_KEY，将跳过AI分析。")
        return None
    
    # Using qwen-max for better reasoning capabilities on complex error logs
    return ChatOpenAI(
        model="qwen-max", 
        openai_api_key=api_key,
        openai_api_base="https://dashscope.aliyuncs.com/compatible-mode/v1",
        temperature=0.1
    )

# --- Nodes ---

def discover_tests(state: AgentState) -> AgentState:
    """Discover integration tests using pytest --collect-only."""
    print("🔍 正在发现测试...")
    pattern = state.get("specific_test_pattern")
    
    try:
        cwd = os.path.join(PROJECT_ROOT, "python")
        env = os.environ.copy()
        env["PYTHONPATH"] = cwd
        
        print(f"📂 项目根目录: {PROJECT_ROOT}")
        print(f"📂 工作目录: {cwd}")
        print(f"📂 PYTHONPATH: {env.get('PYTHONPATH')}")
        print(f"🔍 目录存在: {os.path.exists(cwd)}")
        if os.path.exists(cwd):
            print(f"📋 内容: {os.listdir(cwd)}") 
        
        # Base command
        cmd = [sys.executable, "-m", "pytest", "tests/integration", "--collect-only", "-q", "-c", "/dev/null"]
        
        # Add specific test pattern if provided (passed to pytest directly for filtering)
        if pattern:
            print(f"   使用模式过滤测试: {pattern}")
            cmd.append("-k")
            cmd.append(pattern)
            
        print(f"执行命令: {' '.join(cmd)} 在目录 {cwd}")
        print("⏳ 正在运行pytest命令...")
        result = subprocess.run(cmd, cwd=cwd, capture_output=True, text=True, env=env)
        print(f"✅ 命令完成，返回码: {result.returncode}")
        if result.stderr:
            print(f"⚠️ 标准错误: {result.stderr}")
        print(f"📄 标准输出长度: {len(result.stdout)} 字符")
        
        test_ids = []
        for line in result.stdout.splitlines():
            line = line.strip()
            # Standard pytest -q output: tests/integration/path/to/test.py::test_name
            if line and not line.startswith("no tests ran") and not line.startswith("===") and "::" in line:
                test_id = line.split(" ")[0]
                # Fix path if it's missing tests/integration prefix
                if not test_id.startswith("tests/integration") and (test_id.startswith("_async") or test_id.startswith("_sync")):
                    test_id = os.path.join("tests", "integration", test_id)
                test_ids.append(test_id)
        
        print(f"✅ 找到 {len(test_ids)} 个测试。")
        if len(test_ids) == 0 and result.stderr:
             print(f"调试输出:\n{result.stderr}")
        
        # Load SDK Context
        context = ""
        if os.path.exists(LLMS_FULL_PATH):
            try:
                with open(LLMS_FULL_PATH, "r", encoding="utf-8") as f:
                    context = f.read()
                print(f"📚 已加载SDK上下文 ({len(context)} 字符)")
            except Exception as e:
                print(f"⚠️ 读取llms-full.txt失败: {e}")
        else:
            print(f"⚠️ 在 {LLMS_FULL_PATH} 未找到llms-full.txt")

        return {
            "test_queue": test_ids,
            "current_test_index": 0,
            "results": [],
            "sdk_context": context,
            "is_finished": False,
            "specific_test_pattern": pattern
        }
    except Exception as e:
        print(f"❌ 发现测试时出错: {e}")
        return {"test_queue": [], "current_test_index": 0, "results": [], "sdk_context": "", "is_finished": True, "specific_test_pattern": pattern}

def execute_next_test(state: AgentState) -> AgentState:
    """Executes the next test in the queue."""
    idx = state["current_test_index"]
    queue = state["test_queue"]
    
    if idx >= len(queue):
        return state 

    test_id = queue[idx]
    print(f"▶️ 正在运行测试 ({idx+1}/{len(queue)}): {test_id}")
    
    cwd = os.path.join(PROJECT_ROOT, "python")
    env = os.environ.copy()
    env["PYTHONPATH"] = cwd
    
    # Ensure AGENTBAY_API_KEY is present (it should be injected by CI/Aone)
    if "AGENTBAY_API_KEY" not in env:
        print("⚠️ 警告: 环境变量中未找到AGENTBAY_API_KEY。")

    # Run specific test
    cmd = [sys.executable, "-m", "pytest", test_id, "-vv"]
    result = subprocess.run(cmd, cwd=cwd, capture_output=True, text=True, env=env)
    
    status = "passed" if result.returncode == 0 else "failed"
    output = result.stdout + "\n" + result.stderr
    
    print(f"   结果: {status.upper()}")
    
    new_result: TestResult = {
        "test_id": test_id,
        "status": status,
        "output": output,
        "error_analysis": None
    }
    
    return {
        "results": state["results"] + [new_result],
        "current_test_index": state["current_test_index"], # Keep current index, will be incremented later
        "test_queue": state["test_queue"],
        "sdk_context": state["sdk_context"],
        "is_finished": state["is_finished"],
        "specific_test_pattern": state["specific_test_pattern"]
    }

def analyze_failure(state: AgentState) -> AgentState:
    """Analyzes the last failed test."""
    last_result = state["results"][-1]
    if last_result["status"] == "passed":
        return state 
        
    print(f"🤖 正在分析失败测试 {last_result['test_id']}...")
    
    model = get_model()
    if not model:
        last_result["error_analysis"] = "跳过分析 (无DASHSCOPE_API_KEY)。"
        return {"results": state["results"][:-1] + [last_result], **{k:v for k,v in state.items() if k != "results"}}

    # Prepare context
    # Limit context to avoid super long prompts if not needed, 
    # but allow enough for the model to understand the SDK.
    sdk_context_snippet = state["sdk_context"][:50000] + "...(truncated)" if len(state["sdk_context"]) > 50000 else state["sdk_context"]
    
    # Get test code
    test_file_path = os.path.join(PROJECT_ROOT, "python", last_result["test_id"].split("::")[0])
    test_code = ""
    if os.path.exists(test_file_path):
        try:
            with open(test_file_path, "r") as f:
                test_code = f.read()
        except:
            test_code = "Could not read test file."

    error_log = last_result["output"][-5000:] # Last 5000 chars of log

    prompt = ChatPromptTemplate.from_template("""
你是一位资深的Python SDK测试专家。请用中文进行分析和回答。

### SDK Context (Documentation/Codebase)
{sdk_context}

### 任务
分析以下集成测试的失败原因。
判断这是测试问题、环境问题，还是SDK缺陷。

### 测试信息
测试ID: {test_id}

测试代码:
```python
{test_code}
```

错误日志片段:
{error_log}

### Output Instructions
请用中文提供简洁的分析报告，使用Markdown格式：
1. **根本原因**: 导致失败的具体原因是什么？
2. **错误分类**: [测试问题 / 环境问题 / SDK缺陷]
3. **修复建议**: 如何修复这个问题（如适用，请提供代码片段）

IMPORTANT: 请务必使用中文回答，不要使用英文。
""")

    try:
        chain = prompt | model
        response = chain.invoke({
            "sdk_context": sdk_context_snippet,
            "test_id": last_result["test_id"],
            "test_code": test_code,
            "error_log": error_log
        })
        
        last_result["error_analysis"] = response.content
        print("   ✅ 分析完成。")
        
    except Exception as e:
        print(f"   ❌ 分析失败: {e}")
        last_result["error_analysis"] = f"分析失败: {e}"

    return {
        "results": state["results"][:-1] + [last_result],
        "test_queue": state["test_queue"],
        "current_test_index": state["current_test_index"],
        "sdk_context": state["sdk_context"],
        "is_finished": state["is_finished"],
        "specific_test_pattern": state["specific_test_pattern"]
    }

def increment_index(state: AgentState) -> AgentState:
    """Increments the test index."""
    new_index = state["current_test_index"] + 1
    print(f"🔢 增加索引: {state['current_test_index']} -> {new_index}")
    return {
        "current_test_index": new_index,
        "results": state["results"],
        "test_queue": state["test_queue"],
        "sdk_context": state["sdk_context"],
        "is_finished": state["is_finished"],
        "specific_test_pattern": state["specific_test_pattern"]
    }

def generate_report(state: AgentState) -> AgentState:
    """Generates a Markdown report."""
    print("📝 Generating report...")
    results = state["results"]
    
    passed = len([r for r in results if r["status"] == "passed"])
    failed = len([r for r in results if r["status"] == "failed"])
    
    content = f"# Smart Integration Test Report\n\n"
    content += f"**Summary**: {len(results)} Tests | ✅ {passed} Passed | ❌ {failed} Failed\n\n"
    
    for res in results:
        icon = "✅" if res["status"] == "passed" else "❌"
        content += f"## {icon} {res['test_id']}\n\n"
        
        if res["status"] == "failed":
            content += "### 🤖 AI Analysis\n"
            content += f"{res['error_analysis']}\n\n"
            
            content += "### 📄 Output (Snippet)\n"
            content += f"```\n{res['output'][-2000:]}\n```\n\n"
            
    try:
        # Save report to project root or specified artifacts dir
        report_path = os.environ.get("TEST_REPORT_PATH", REPORT_FILE)
        with open(report_path, "w", encoding="utf-8") as f:
            f.write(content)
        print(f"Report saved to {report_path}")
    except Exception as e:
        print(f"Failed to write report: {e}")
        
    return {
        "is_finished": True,
        "results": state["results"],
        "test_queue": state["test_queue"],
        "current_test_index": state["current_test_index"],
        "sdk_context": state["sdk_context"],
        "specific_test_pattern": state["specific_test_pattern"]
    }

# --- Graph Construction ---

workflow = StateGraph(AgentState)

workflow.add_node("discover_tests", discover_tests)
workflow.add_node("execute_test", execute_next_test)
workflow.add_node("analyze_failure", analyze_failure)
workflow.add_node("increment_index", increment_index)
workflow.add_node("generate_report", generate_report)

workflow.set_entry_point("discover_tests")

def check_completion(state: AgentState):
    current_idx = state["current_test_index"]
    total_tests = len(state["test_queue"])
    print(f"🔍 检查完成状态: {current_idx}/{total_tests}")
    
    if current_idx >= total_tests:
        print("✅ 所有测试已完成，正在生成报告...")
        return "generate_report"
    
    print(f"➡️ 继续下一个测试 ({current_idx + 1}/{total_tests})")
    return "execute_test"

workflow.add_conditional_edges(
    "discover_tests",
    check_completion,
    {
        "generate_report": "generate_report",
        "execute_test": "execute_test"
    }
)

def check_test_result(state: AgentState):
    last_result = state["results"][-1]
    print(f"🔍 检查测试结果: {last_result['test_id']} -> {last_result['status']}")
    if last_result["status"] == "failed":
        print("❌ 测试失败，进行AI分析...")
        return "analyze_failure"
    print("✅ 测试通过，增加索引...")
    return "increment_index"

workflow.add_conditional_edges(
    "execute_test",
    check_test_result,
    {
        "analyze_failure": "analyze_failure",
        "increment_index": "increment_index"
    }
)

workflow.add_edge("analyze_failure", "increment_index")

workflow.add_conditional_edges(
    "increment_index",
    check_completion,
    {
        "generate_report": "generate_report",
        "execute_test": "execute_test"
    }
)

workflow.add_edge("generate_report", END)

app = workflow.compile()

def main():
    global REPORT_FILE
    
    parser = argparse.ArgumentParser(description="Smart Integration Test Runner with AI Analysis")
    parser.add_argument("-k", "--keyword", help="Run tests which match the given substring expression (same as pytest -k)", type=str)
    parser.add_argument("--test-type", help="Test type to run (all, python, typescript, golang)", type=str, default="all")
    parser.add_argument("--report", help="Path to save the report", default=REPORT_FILE)
    
    args = parser.parse_args()
    
    print("🚀 Starting Smart Test Runner...")
    if args.keyword:
        print(f"🎯 Target Pattern: {args.keyword}")
    
    if args.test_type:
        print(f"🎯 Test Type: {args.test_type}")
    
    if args.report:
        REPORT_FILE = args.report

    print("📋 Initializing state...")
    initial_state = {
        "test_queue": [], 
        "current_test_index": 0, 
        "results": [], 
        "sdk_context": "",
        "is_finished": False,
        "specific_test_pattern": args.keyword
    }
    
    print("🔧 Starting workflow execution...")
    try:
        print("📍 About to invoke app...")
        # Set recursion limit to prevent infinite loops
        config = {"recursion_limit": 100}
        result = app.invoke(initial_state, config=config)
        print(f"✅ Workflow completed: {result}")
    except Exception as e:
        print(f"\n💥 执行失败: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

if __name__ == "__main__":
    main()

