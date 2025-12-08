import os
import sys
import argparse
import subprocess
import shutil
import time
import re
from typing import List, Dict, Any, Optional, TypedDict, Literal
import json

# Ensure we can import standard libraries.
print("🔍 正在检查Python环境和依赖...")

# Check each import individually
try:
    from langchain_openai import ChatOpenAI
    print("✅ langchain_openai导入成功")
except ImportError as e:
    print(f"❌ langchain_openai导入失败: {e}")
    sys.exit(1)

try:
    from langgraph.graph import StateGraph, END
    print("✅ langgraph导入成功")
except ImportError as e:
    print(f"❌ langgraph导入失败: {e}")
    sys.exit(1)

try:
    from langchain_core.prompts import ChatPromptTemplate
    print("✅ langchain_core导入成功")
except ImportError as e:
    print(f"❌ langchain_core导入失败: {e}")
    sys.exit(1)

# Configuration
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if os.path.basename(PROJECT_ROOT) == "scripts": 
    PROJECT_ROOT = os.path.dirname(PROJECT_ROOT)

DOCS_DIRS = [
    os.path.join(PROJECT_ROOT, "python", "docs"),
    os.path.join(PROJECT_ROOT, "docs", "guides")
]
TMP_DIR = os.path.join(PROJECT_ROOT, "tmp", "doc_verification")
LLMS_FULL_PATH = os.path.join(PROJECT_ROOT, "llms-full.txt")
REPORT_FILE = os.path.join(PROJECT_ROOT, "tmp", "doc_verification_report.md")

# Ensure tmp dir exists
os.makedirs(TMP_DIR, exist_ok=True)

# State Definition
class Snippet(TypedDict):
    id: str
    file_path: str
    line_number: int
    content: str
    context: str # Surrounding text for context

class VerificationResult(TypedDict):
    snippet_id: str
    file_path: str
    status: str  # 'passed', 'failed_doc_issue', 'failed_gen_issue', 'skipped'
    output: str
    analysis: Optional[str]
    verification_code: Optional[str]

class AgentState(TypedDict):
    # Global
    snippet_queue: List[Snippet]
    current_index: int
    results: List[VerificationResult]
    sdk_context: str
    pattern: Optional[str]
    report_file: str
    
    # Per-snippet loop
    current_snippet: Optional[Snippet]
    verification_script: Optional[str]
    execution_output: Optional[str]
    execution_success: bool
    retry_count: int
    analysis: Optional[str]
    is_doc_issue: bool
    skip_reason: Optional[str]

# --- Helper Functions ---

def get_model():
    """Initializes the Qwen model via ChatOpenAI interface."""
    api_key = os.environ.get("DASHSCOPE_API_KEY")
    if not api_key:
        print("⚠️ 未找到DASHSCOPE_API_KEY，无法使用AI功能。")
        return None
    
    return ChatOpenAI(
        model="qwen-max", 
        openai_api_key=api_key,
        openai_api_base="https://dashscope.aliyuncs.com/compatible-mode/v1",
        temperature=0.1
    )

def load_sdk_context():
    if os.path.exists(LLMS_FULL_PATH):
        try:
            with open(LLMS_FULL_PATH, "r", encoding="utf-8") as f:
                return f.read()
        except Exception as e:
            print(f"⚠️ 读取llms-full.txt失败: {e}")
    return ""

def extract_snippets_from_md(file_path: str) -> List[Snippet]:
    snippets = []
    try:
        with open(file_path, "r", encoding="utf-8") as f:
            lines = f.readlines()
            
        in_code_block = False
        code_lines = []
        start_line = 0
        lang = ""
        
        # Simple parser for ```python blocks
        for i, line in enumerate(lines):
            stripped = line.strip()
            if stripped.startswith("```"):
                if in_code_block:
                    # End of block
                    in_code_block = False
                    if lang in ["python", "py"]:
                        content = "".join(code_lines)
                        if content.strip(): # Ignore empty blocks
                            # Get some context (previous 5 lines)
                            context_start = max(0, start_line - 5)
                            context = "".join(lines[context_start:start_line])
                            
                            snippets.append({
                                "id": f"{os.path.basename(file_path)}:{start_line}",
                                "file_path": os.path.relpath(file_path, PROJECT_ROOT),
                                "line_number": start_line + 1,
                                "content": content,
                                "context": context
                            })
                    code_lines = []
                    lang = ""
                else:
                    # Start of block
                    lang = stripped.lstrip("`").strip().lower()
                    if lang in ["python", "py"]:
                        in_code_block = True
                        start_line = i
            elif in_code_block:
                code_lines.append(line)
                
    except Exception as e:
        print(f"⚠️ 解析文件失败 {file_path}: {e}")
        
    return snippets

# --- Nodes ---

def discover_examples(state: AgentState) -> AgentState:
    """Finds all python code blocks in markdown files."""
    print(f"🔍 正在扫描文档目录...")
    all_snippets = []
    
    for doc_dir in DOCS_DIRS:
        if not os.path.exists(doc_dir):
            continue
            
        for root, _, files in os.walk(doc_dir):
            for file in files:
                if file.endswith(".md"):
                    full_path = os.path.join(root, file)
                    snippets = extract_snippets_from_md(full_path)
                    all_snippets.extend(snippets)
    
    # Filter based on pattern if provided
    if state.get("pattern"):
        pattern = state["pattern"]
        all_snippets = [s for s in all_snippets if pattern in s["file_path"]]
        print(f"🔍 应用过滤模式 '{pattern}': 剩余 {len(all_snippets)} 个代码片段")
    
    print(f"✅ 总共找到 {len(all_snippets)} 个Python代码片段。")
    
    return {
        **state,
        "snippet_queue": all_snippets,
        "current_index": 0,
        "sdk_context": load_sdk_context()
    }

def prepare_snippet(state: AgentState) -> AgentState:
    """Loads the current snippet."""
    idx = state["current_index"]
    if idx >= len(state["snippet_queue"]):
        return state
    
    snippet = state["snippet_queue"][idx]
    print(f"📖 处理片段 ({idx+1}/{len(state['snippet_queue'])}): {snippet['id']}")
    
    return {
        **state,
        "current_snippet": snippet,
        "verification_script": None,
        "execution_output": None,
        "execution_success": False,
        "retry_count": 0,
        "analysis": None,
        "is_doc_issue": False,
        "skip_reason": None
    }

def generate_verification_script(state: AgentState) -> AgentState:
    """Generates a verification script using LLM, or decides to skip."""
    snippet = state["current_snippet"]
    retry_count = state["retry_count"]
    analysis = state["analysis"]
    
    print(f"🤖 正在分析/生成验证脚本 (尝试 {retry_count+1})...")
    
    model = get_model()
    if not model:
        return {**state, "skip_reason": "No AI model available"}

    # Simplify context
    sdk_context_snippet = state["sdk_context"][:20000] + "..." if len(state["sdk_context"]) > 20000 else state["sdk_context"]

    prompt_template = """
你是一个Python SDK专家。你需要验证文档中的Python代码片段。

### SDK Context
{sdk_context}

### 文档文件: {file_path}
### 上下文:
{context}

### 代码片段:
```python
{code_content}
```

### 任务
1. **严格判断**该代码片段是否是**可运行的示例代码** (Usage Example)。
   - **必须跳过**: 函数签名 (如 `def func(...)`)、类定义 (如 `class MyClass`)、API接口描述、仅有变量声明但无上下文的代码。
   - **必须跳过**: 仅包含 `pip install` 或非Python代码。
   - **可以生成**: 包含具体逻辑、函数调用、`print`语句、`await`操作的示例代码。

2. **如果决定验证 (GENERATE)**:
   - 编写一个完整的、可执行的Python脚本。
   - 补全 `import os`, `import asyncio`, `from agentbay import ...` 等。
   - 初始化必要的客户端 (如 `AsyncAgentBay(api_key=os.getenv("AGENTBAY_API_KEY"))`)。
   - 假设 `AGENTBAY_API_KEY` 环境变量已存在。
   - 将逻辑包裹在 `async def main():` 中并运行 `asyncio.run(main())`。
   - 如果示例中使用了未定义的变量 (如 `session_id`)，请**务必**在脚本中先创建相应的资源获取该ID，或者mock它。不要直接使用未定义的变量。

{retry_instruction}

### 输出格式
如果跳过:
SKIP: <跳过原因>

如果生成脚本:
```python
<完整脚本内容>
```
"""
    
    retry_instruction = ""
    if retry_count > 0 and analysis:
        retry_instruction = f"""
        ### 上次验证失败
        上次生成的脚本执行失败。
        错误分析: {analysis}
        
        请根据分析修复验证脚本。
        """

    prompt = ChatPromptTemplate.from_template(prompt_template)
    
    try:
        chain = prompt | model
        response = chain.invoke({
            "sdk_context": sdk_context_snippet,
            "file_path": snippet["file_path"],
            "context": snippet["context"],
            "code_content": snippet["content"],
            "retry_instruction": retry_instruction
        })
        
        text = response.content.strip()
        
        if text.startswith("SKIP:"):
            reason = text.split("SKIP:", 1)[1].strip()
            print(f"   ⏩ 跳过: {reason}")
            return {**state, "skip_reason": reason, "verification_script": None}
            
        if "```python" in text:
            script = text.split("```python")[1].split("```")[0].strip()
        elif "```" in text:
            script = text.split("```")[1].split("```")[0].strip()
        else:
            script = text
            
        # Fallback if model returns code but no SKIP and no ``` block (rare)
        if not script and "SKIP" not in text: 
             script = text

        return {**state, "verification_script": script, "skip_reason": None}
        
    except Exception as e:
        print(f"❌ 生成脚本失败: {e}")
        return {**state, "skip_reason": f"AI Generation Failed: {e}", "verification_script": None}

def execute_script(state: AgentState) -> AgentState:
    """Executes the verification script."""
    if state["skip_reason"]:
        return state
        
    script = state["verification_script"]
    
    # Prepare temp dir
    run_dir = os.path.join(TMP_DIR, f"run_{state['current_index']}")
    if os.path.exists(run_dir):
        shutil.rmtree(run_dir)
    os.makedirs(run_dir)
    
    script_path = os.path.join(run_dir, "verify_snippet.py")
    with open(script_path, "w", encoding="utf-8") as f:
        f.write(script)
        
    print(f"▶️ 执行验证脚本...")
    
    env = os.environ.copy()
    env["PYTHONPATH"] = os.path.join(PROJECT_ROOT, "python") + os.pathsep + env.get("PYTHONPATH", "")
    
    try:
        result = subprocess.run(
            [sys.executable, "verify_snippet.py"],
            cwd=run_dir,
            capture_output=True,
            text=True,
            env=env,
            timeout=120 # 2 mins timeout
        )
        
        success = (result.returncode == 0)
        output = result.stdout + "\n" + result.stderr
        
        print(f"   结果: {'✅ 成功' if success else '❌ 失败'}")
        
        return {
            **state,
            "execution_output": output,
            "execution_success": success
        }
        
    except subprocess.TimeoutExpired:
        print("   结果: ❌ 超时")
        return {
            **state,
            "execution_output": "Execution timed out after 120s",
            "execution_success": False
        }
    except Exception as e:
        print(f"   结果: ❌ 执行异常 {e}")
        return {
            **state,
            "execution_output": str(e),
            "execution_success": False
        }

def analyze_failure(state: AgentState) -> AgentState:
    """Analyzes failure."""
    output = state["execution_output"]
    script = state["verification_script"]
    snippet = state["current_snippet"]
    
    print("🤖 分析失败原因...")
    
    model = get_model()
    if not model:
        return {**state, "analysis": "No AI model", "is_doc_issue": True}
        
    prompt = ChatPromptTemplate.from_template("""
你是一个Python专家。我正在验证文档中的代码片段。

### 原始文档片段:
```python
{code_content}
```

### 生成的验证脚本:
```python
{script}
```

### 执行输出:
{output}

### 任务
分析失败原因。判断是：
1. **生成代码问题**: 验证脚本包装有问题（如mock不对、环境缺失、逻辑错误）。
2. **文档代码问题**: 原始文档片段本身有错（API不存在、参数错误、逻辑不通）。

请返回严格的JSON格式，不要包含Markdown代码块标记（如 ```json），也不要包含任何注释。
{{
    "reason": "简短分析",
    "type": "gen_issue" 或 "doc_issue",
    "suggestion": "修复建议"
}}
""")

    try:
        chain = prompt | model
        response = chain.invoke({
            "code_content": snippet["content"],
            "script": script,
            "output": output[-5000:]
        })
        
        content = response.content.strip()
        # Clean up markdown if present
        if content.startswith("```"):
            content = content.split("\n", 1)[1]
            if content.endswith("```"):
                content = content.rsplit("\n", 1)[0]
        
        # Try to find JSON block
        json_match = re.search(r'\{.*\}', content, re.DOTALL)
        if json_match:
            content = json_match.group(0)
            
        try:
            analysis_json = json.loads(content)
        except json.JSONDecodeError:
            # Try to fix common JSON errors if simple load fails
            # e.g. single quotes to double quotes, though dangerous
            try:
                import ast
                analysis_json = ast.literal_eval(content)
            except:
                raise Exception(f"Failed to parse JSON: {content[:100]}...")
        
        is_doc_issue = (analysis_json.get("type") == "doc_issue")
        analysis_text = f"Type: {analysis_json.get('type')}\nReason: {analysis_json.get('reason')}\nSuggestion: {analysis_json.get('suggestion')}"
        
        print(f"   分析结果: {'📄 文档问题' if is_doc_issue else '🛠️ 生成脚本问题'}")
        
        return {
            **state,
            "analysis": analysis_text,
            "is_doc_issue": is_doc_issue
        }
        
    except Exception as e:
        print(f"❌ 分析失败: {e}")
        return {
            **state,
            "analysis": f"Analysis failed: {e}",
            "is_doc_issue": True 
        }

def record_result(state: AgentState) -> AgentState:
    """Records the result."""
    snippet = state["current_snippet"]
    
    if state["skip_reason"]:
        status = "skipped"
        output = state["skip_reason"]
        analysis = None
    elif state["execution_success"]:
        status = "passed"
        output = state["execution_output"]
        analysis = None
    else:
        status = "failed_doc_issue" if state["is_doc_issue"] else "failed_gen_issue"
        output = state["execution_output"]
        analysis = state["analysis"]
        
    result: VerificationResult = {
        "snippet_id": snippet["id"],
        "file_path": snippet["file_path"],
        "status": status,
        "output": output,
        "analysis": analysis,
        "verification_code": state.get("verification_script")
    }
    
    new_results = state["results"] + [result]
    
    return {
        **state,
        "results": new_results,
        "current_index": state["current_index"] + 1
    }

def generate_final_report(state: AgentState) -> AgentState:
    """Generates the final markdown report."""
    results = state["results"]
    passed = len([r for r in results if r["status"] == "passed"])
    # Only consider doc issues as failures for the final report to user
    failed_doc = len([r for r in results if r["status"] == "failed_doc_issue"])
    failed_gen = len([r for r in results if r["status"] == "failed_gen_issue"])
    skipped = len([r for r in results if r["status"] == "skipped"])
    
    content = f"# Smart Integration Test Report (Doc Verification)\n\n"
    content += f"**Summary**: {len(results)} Snippets | ✅ {passed} Passed | ❌ {failed_doc} Doc Issues | ⚠️ {failed_gen} Script Issues | ⏭️ {skipped} Skipped\n\n"
    
    if failed_doc == 0 and failed_gen == 0:
        content += "🎉 **All verifiable examples passed!**\n\n"
    
    if failed_doc > 0:
        content += f"## 🚨 Documentation Issues ({failed_doc})\n\n"
        content += "这些是文档中实际存在的代码错误，需要修复。\n\n"
        
        for r in results:
            if r["status"] == "failed_doc_issue":
                content += f"---\n\n"
                content += f"### 📄 文件: `{r['file_path']}`\n"
                content += f"**位置**: Line {r['snippet_id'].split(':')[1]}\n\n"
                
                content += "**错误分析**:\n"
                if r.get('analysis'):
                    # Extract reason and suggestion from analysis text
                    analysis_text = r['analysis']
                    reason = ""
                    suggestion = ""
                    for line in analysis_text.split('\n'):
                        if line.startswith("Reason:"):
                            reason = line.replace("Reason:", "").strip()
                        elif line.startswith("Suggestion:"):
                            suggestion = line.replace("Suggestion:", "").strip()
                    
                    if reason:
                        content += f"- 🔴 **原因**: {reason}\n"
                    if suggestion:
                        content += f"- 💡 **建议**: {suggestion}\n"
                    if not reason and not suggestion:
                        content += f"{analysis_text}\n"
                else:
                    content += "未进行AI分析\n"
                content += "\n"
                
                # Show execution output if relevant (e.g. SyntaxError from original code)
                # But filter out the verification script path noise
                output = r['output']
                if output:
                    clean_output = output
                    # Simple heuristic to clean up traceback paths
                    clean_output = re.sub(r'File ".*verify_snippet.py",', 'File "<generated_script>",', clean_output)
                    
                    content += "**执行报错**:\n"
                    content += f"```text\n{clean_output[-1000:]}\n```\n\n"

    if failed_gen > 0:
        content += f"## ⚠️ Script Generation Issues ({failed_gen})\n\n"
        content += "这些是生成验证脚本时的问题（可能是环境、mock或AI生成问题），**不代表文档一定有错**，但建议人工检查。\n\n"
        
        for r in results:
            if r["status"] == "failed_gen_issue":
                content += f"- `{r['file_path']}` (Line {r['snippet_id'].split(':')[1]}) - "
                if r.get('analysis'):
                     for line in r['analysis'].split('\n'):
                        if line.startswith("Reason:"):
                            content += f"{line.replace('Reason:', '').strip()}\n"
                            break
                else:
                     content += "Unknown error\n"

    report_file = state.get("report_file", REPORT_FILE)
    try:
        with open(report_file, "w", encoding="utf-8") as f:
            f.write(content)
        print(f"📝 报告已生成: {report_file}")
    except Exception as e:
        print(f"❌ 写入报告失败: {e}")
        
    return state

def increment_retry(state: AgentState) -> AgentState:
    """Increments the retry count."""
    return {**state, "retry_count": state["retry_count"] + 1}

# --- Routing ---

def check_script_generation(state: AgentState):
    if state["skip_reason"]:
        return "record_result"
    return "execute_script"

def check_execution(state: AgentState):
    if state["execution_success"]:
        return "record_result"
    return "analyze_failure"

def check_retry_condition(state: AgentState):
    if state["is_doc_issue"]:
        return "record_result"
    
    if state["retry_count"] < 2: # Max 2 retries
        return "increment_retry"
    
    return "record_result"

def check_loop(state: AgentState):
    if state["current_index"] < len(state["snippet_queue"]):
        return "prepare_snippet"
    return "generate_final_report"

# --- Graph Construction ---

workflow = StateGraph(AgentState)

workflow.add_node("discover_examples", discover_examples)
workflow.add_node("prepare_snippet", prepare_snippet)
workflow.add_node("generate_verification_script", generate_verification_script)
workflow.add_node("execute_script", execute_script)
workflow.add_node("analyze_failure", analyze_failure)
workflow.add_node("increment_retry", increment_retry)
workflow.add_node("record_result", record_result)
workflow.add_node("generate_final_report", generate_final_report)

workflow.set_entry_point("discover_examples")

workflow.add_edge("discover_examples", "prepare_snippet")
workflow.add_edge("prepare_snippet", "generate_verification_script")
workflow.add_edge("increment_retry", "generate_verification_script")

workflow.add_conditional_edges(
    "generate_verification_script",
    check_script_generation,
    {
        "record_result": "record_result",
        "execute_script": "execute_script"
    }
)

workflow.add_conditional_edges(
    "execute_script",
    check_execution,
    {
        "record_result": "record_result",
        "analyze_failure": "analyze_failure"
    }
)

workflow.add_conditional_edges(
    "analyze_failure",
    check_retry_condition,
    {
        "increment_retry": "increment_retry",
        "record_result": "record_result"
    }
)

workflow.add_conditional_edges(
    "record_result",
    check_loop,
    {
        "prepare_snippet": "prepare_snippet",
        "generate_final_report": "generate_final_report"
    }
)

workflow.add_edge("generate_final_report", END)

app = workflow.compile()

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--limit", type=int, help="Limit number of examples to verify", default=None)
    parser.add_argument("--pattern", type=str, help="Filter files by pattern", default=None)
    parser.add_argument("--report", type=str, help="Report file path", default=REPORT_FILE)
    args = parser.parse_args()
    
    initial_state = {
        "snippet_queue": [],
        "current_index": 0,
        "results": [],
        "sdk_context": "",
        "pattern": args.pattern,
        "report_file": args.report,
        "current_snippet": None,
        "verification_script": None,
        "execution_output": None,
        "execution_success": False,
        "retry_count": 0,
        "analysis": None,
        "is_doc_issue": False,
        "skip_reason": None
    }
    
    try:
        # Increase recursion limit for long loops
        config = {"recursion_limit": 10000}
        app.invoke(initial_state, config=config)
    except Exception as e:
        print(f"💥 执行出错: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()
