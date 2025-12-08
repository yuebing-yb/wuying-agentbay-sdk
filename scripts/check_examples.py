import argparse
import os
import subprocess
import sys
import time
from typing import List, Dict, Any, Optional

# ANSI colors
GREEN = '\033[92m'
RED = '\033[91m'
YELLOW = '\033[93m'
RESET = '\033[0m'

# Report file path
REPORT_FILE = "example_check_report.md"

# List of examples to skip (relative path from project root or filename)
SKIP_EXAMPLES = [
    # Interactive examples requiring user input
    "typescript/docs/examples/browser-use/browser/call_for_user_jd.ts",
    # Long running examples
    "typescript/docs/examples/browser-use/browser/run-2048.ts",
]

def print_success(msg):
    print(f"{GREEN}{msg}{RESET}")

def print_error(msg):
    print(f"{RED}{msg}{RESET}")

def print_warning(msg):
    print(f"{YELLOW}{msg}{RESET}")

# --- AI Analysis Setup ---
try:
    from langchain_openai import ChatOpenAI
    from langchain_core.prompts import ChatPromptTemplate
    AI_AVAILABLE = True
except ImportError as e:
    AI_AVAILABLE = False
    print_warning(f"AI dependencies not found ({e}). AI analysis will be skipped.")

def get_model():
    """Initializes the Qwen model via ChatOpenAI interface compatible with DashScope."""
    if not AI_AVAILABLE:
        return None
        
    api_key = os.environ.get("DASHSCOPE_API_KEY")
    if not api_key:
        print_warning("DASHSCOPE_API_KEY not found. AI analysis will be skipped.")
        return None
    
    return ChatOpenAI(
        model="qwen-max", 
        openai_api_key=api_key,
        openai_api_base="https://dashscope.aliyuncs.com/compatible-mode/v1",
        temperature=0.1
    )

def analyze_failure(file_path: str, output: str, duration: float) -> str:
    """Analyze failure using AI."""
    model = get_model()
    if not model:
        # Check if the failure is due to missing dependencies in sandbox
        if "Connection error" in output or "no such host" in output:
             return "AI分析跳过：环境网络受限，无法连接到 AI 服务进行分析。"
        if not AI_AVAILABLE:
            return "AI分析跳过：缺少 AI 分析所需的 Python 依赖库 (langchain-openai 等)。"
        if not os.environ.get("DASHSCOPE_API_KEY"):
            return "AI分析跳过：环境变量 DASHSCOPE_API_KEY 未设置。"
        return "AI分析跳过：未知原因。"
        
    print(f"🤖 正在分析 {os.path.basename(file_path)} 的失败原因...")
    
    # Read file content
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            code_content = f.read()
    except Exception as e:
        code_content = f"无法读取文件内容: {e}"
        
        # Truncate output if too long
    error_log = output[-5000:] if len(output) > 5000 else output
    
    # Use a simpler prompt to avoid potential encoding issues
    prompt = ChatPromptTemplate.from_template("""
你是一位资深的SDK示例代码审查专家。请用中文进行分析和回答。

### 任务
分析以下SDK示例代码的运行失败原因。
判断这是环境配置问题、代码逻辑问题，还是SDK本身的问题。

### 示例信息
文件: {filename}
耗时: {duration:.2f}s

### 代码内容
```
{code_content}
```

### 运行输出/错误日志
{error_log}

### Output Instructions
请用中文提供简洁的分析报告，使用Markdown格式：
1. **根本原因**: 导致失败的具体原因是什么？
2. **错误分类**: [环境问题 / 代码问题 / SDK缺陷]
3. **修复建议**: 如何修复这个问题（如适用，请提供代码片段或命令）

IMPORTANT: 请务必使用中文回答。
""")

    try:
        chain = prompt | model
        response = chain.invoke({
            "filename": os.path.basename(file_path),
            "duration": duration,
            "code_content": code_content,
            "error_log": error_log
        })
        return response.content
    except Exception as e:
        error_msg = str(e)
        if "Connection error" in error_msg or "Failed to connect" in error_msg:
             return f"AI分析失败：连接 AI 服务超时或失败 (网络问题)。"
        print_error(f"AI analysis failed: {e}")
        return f"AI分析失败: {e}"

# --- Execution Logic ---

def run_command(cmd: List[str], cwd: str, env: Dict[str, str] = None, timeout: int = 600) -> Dict[str, Any]:
    """Run a command with timeout and capture output."""
    start_time = time.time()
    try:
        # Merge environment variables
        cmd_env = os.environ.copy()
        if env:
            cmd_env.update(env)
            
        process = subprocess.Popen(
            cmd, 
            cwd=cwd, 
            stdout=subprocess.PIPE, 
            stderr=subprocess.PIPE, 
            text=True, 
            env=cmd_env
        )
        
        try:
            stdout, stderr = process.communicate(timeout=timeout)
            duration = time.time() - start_time
            return {
                "returncode": process.returncode,
                "stdout": stdout,
                "stderr": stderr,
                "duration": duration,
                "timed_out": False
            }
        except subprocess.TimeoutExpired:
            process.kill()
            stdout, stderr = process.communicate()
            duration = time.time() - start_time
            return {
                "returncode": -1,
                "stdout": stdout,
                "stderr": stderr,
                "duration": duration,
                "timed_out": True
            }
            
    except Exception as e:
        return {
            "returncode": -1,
            "stdout": "",
            "stderr": str(e),
            "duration": time.time() - start_time,
            "timed_out": False
        }

def find_files(root_dir: str, extension: str, exclude_list: List[str] = None) -> List[str]:
    """Find files with specific extension recursively."""
    found_files = []
    if not os.path.exists(root_dir):
        return found_files
        
    for root, dirs, files in os.walk(root_dir):
        # Filter exclusions
        if exclude_list:
            dirs[:] = [d for d in dirs if d not in exclude_list]
            
        for file in files:
            if file.endswith(extension):
                # Check for exclusions in file name
                if exclude_list and any(ex in file for ex in exclude_list):
                    continue
                found_files.append(os.path.join(root, file))
                
    return sorted(found_files)

def process_results(results: List[Dict], language: str):
    """Generate and append report."""
    failed_count = len([r for r in results if not r['success']])
    passed_count = len(results) - failed_count
    
    # Language mapping for better display
    lang_display = {
        "Python": "Python",
        "Golang": "Golang",
        "TypeScript": "TypeScript"
    }
    lang_name = lang_display.get(language, language)
    
    report_content = f"\n## {lang_name} 示例检查报告\n\n"
    report_content += f"**汇总**: 共检测 {len(results)} 个示例 | ✅ {passed_count} 通过 | ❌ {failed_count} 失败\n\n"
    
    if failed_count > 0:
        report_content += "### ❌ 失败示例详情\n\n"
        for res in results:
            if not res['success']:
                rel_path = res['file']
                report_content += f"---\n\n#### 📄 {rel_path}\n"
                report_content += f"**耗时**: {res['duration']:.2f}s\n\n"
                
                # AI Analysis
                report_content += f"**🤖 AI 智能分析**:\n\n{res['analysis']}\n\n"
                
                # Log Snippet
                output = res['output']
                snippet = output[-2000:] if len(output) > 2000 else output
                report_content += f"**日志片段**:\n```\n{snippet}\n```\n\n"
    
    # Write to report file (append mode)
    with open(REPORT_FILE, "a", encoding="utf-8") as f:
        f.write(report_content)

def check_python_examples(project_root: str, limit: int = 0) -> bool:
    print(f"\n{YELLOW}=== Checking Python Examples ==={RESET}")
    examples_dir = os.path.join(project_root, "python", "docs", "examples", "_async")
    python_root = os.path.join(project_root, "python")
    
    exclude_list = ["__init__.py", "__pycache__", "requirements.txt"]
    files = find_files(examples_dir, ".py", exclude_list)
    
    if not files:
        print_warning("No Python examples found.")
        return True
        
    print(f"Found {len(files)} Python examples.")
    if limit > 0 and len(files) > limit:
        print(f"Limiting to first {limit} examples.")
        files = files[:limit]
    
    env = {"PYTHONPATH": python_root}
    results = []
    
    for i, file_path in enumerate(files):
        rel_path = os.path.relpath(file_path, project_root)
        
        if any(skip in rel_path for skip in SKIP_EXAMPLES):
            print(f"Skipping ({i+1}/{len(files)}): {rel_path} (in skip list)")
            continue

        print(f"Running ({i+1}/{len(files)}): {rel_path} ... ", end="", flush=True)
        
        # Set AGENTBAY_LOG_LEVEL to ERROR to reduce noise unless we're debugging a failure
        env_with_log = env.copy()
        env_with_log["AGENTBAY_LOG_LEVEL"] = "ERROR"

        result = run_command([sys.executable, file_path], cwd=python_root, env=env_with_log, timeout=600)
        
        success = result["returncode"] == 0 and not result["timed_out"]
        output = result["stdout"] + "\n" + result["stderr"]
        analysis = ""
        
        if success:
            print(f"\n{GREEN}PASSED ({result['duration']:.2f}s){RESET}")
        else:
            status = "TIMEOUT" if result["timed_out"] else "FAILED"
            print(f"\n{RED}{status} ({result['duration']:.2f}s){RESET}")
            # Print stderr to console for visibility in CI logs
            if result['stderr']:
                print(f"{RED}Stderr:{RESET}")
                print(result['stderr'].strip())
            elif result['stdout']:
                print(f"{YELLOW}Stdout (no stderr):{RESET}")
                print(result['stdout'].strip())
                
            analysis = analyze_failure(file_path, output, result['duration'])
            
        results.append({
            "file": rel_path,
            "success": success,
            "duration": result["duration"],
            "output": output,
            "analysis": analysis
        })
            
    process_results(results, "Python")
    return all(r['success'] for r in results)

def check_golang_examples(project_root: str, limit: int = 0) -> bool:
    print(f"\n{YELLOW}=== Checking Golang Examples ==={RESET}")
    examples_dir = os.path.join(project_root, "golang", "docs", "examples")
    golang_root = os.path.join(project_root, "golang")
    
    example_dirs = set()
    for root, dirs, files in os.walk(examples_dir):
        if "main.go" in files:
            example_dirs.add(root)
            
    sorted_dirs = sorted(list(example_dirs))
    
    if not sorted_dirs:
        print_warning("No Golang examples found.")
        return True
        
    print(f"Found {len(sorted_dirs)} Golang examples.")
    if limit > 0 and len(sorted_dirs) > limit:
        print(f"Limiting to first {limit} examples.")
        sorted_dirs = sorted_dirs[:limit]
    
    results = []
    
    for i, dir_path in enumerate(sorted_dirs):
        rel_path = os.path.relpath(dir_path, project_root)
        
        if any(skip in rel_path for skip in SKIP_EXAMPLES):
            print(f"Skipping ({i+1}/{len(sorted_dirs)}): {rel_path} (in skip list)")
            continue

        print(f"Running ({i+1}/{len(sorted_dirs)}): {rel_path} ... ", end="", flush=True)
        
        result = run_command(["go", "run", "."], cwd=dir_path, timeout=600)
        
        success = result["returncode"] == 0 and not result["timed_out"]
        output = result["stdout"] + "\n" + result["stderr"]
        analysis = ""
        
        if success:
            print(f"\n{GREEN}PASSED ({result['duration']:.2f}s){RESET}")
        else:
            status = "TIMEOUT" if result["timed_out"] else "FAILED"
            print(f"\n{RED}{status} ({result['duration']:.2f}s){RESET}")
            # Print stderr to console for visibility in CI logs
            if result['stderr']:
                print(f"{RED}Stderr:{RESET}")
                print(result['stderr'].strip())
            elif result['stdout']:
                print(f"{YELLOW}Stdout (no stderr):{RESET}")
                print(result['stdout'].strip())
                
            # Identify main.go for analysis
            main_go_path = os.path.join(dir_path, "main.go")
            analysis = analyze_failure(main_go_path, output, result['duration'])
        
        results.append({
            "file": rel_path,
            "success": success,
            "duration": result["duration"],
            "output": output,
            "analysis": analysis
        })

    process_results(results, "Golang")
    return all(r['success'] for r in results)

def check_typescript_examples(project_root: str, limit: int = 0) -> bool:
    print(f"\n{YELLOW}=== Checking TypeScript Examples ==={RESET}")
    examples_dir = os.path.join(project_root, "typescript", "docs", "examples")
    typescript_root = os.path.join(project_root, "typescript")
    
    exclude_list = ["node_modules", "dist"]
    files = find_files(examples_dir, ".ts", exclude_list)
    files = [f for f in files if not f.endswith(".d.ts")]
    
    if not files:
        print_warning("No TypeScript examples found.")
        return True
        
    print(f"Found {len(files)} TypeScript examples.")
    if limit > 0 and len(files) > limit:
        print(f"Limiting to first {limit} examples.")
        files = files[:limit]
    
    # Try npx ts-node
    ts_node_cmd = ["npx", "ts-node"]
    
    # Add NODE_PATH to ensure modules are found
    env = os.environ.copy()
    node_modules_path = os.path.join(typescript_root, "node_modules")
    current_node_path = env.get("NODE_PATH", "")
    env["NODE_PATH"] = f"{node_modules_path}{os.pathsep}{current_node_path}" if current_node_path else node_modules_path
        
    results = []
    
    for i, file_path in enumerate(files):
        rel_path = os.path.relpath(file_path, project_root)
        
        if any(skip in rel_path for skip in SKIP_EXAMPLES):
            print(f"Skipping ({i+1}/{len(files)}): {rel_path} (in skip list)")
            continue

        print(f"Running ({i+1}/{len(files)}): {rel_path} ... ", end="", flush=True)
        
        cmd = ts_node_cmd + [file_path]
        result = run_command(cmd, cwd=typescript_root, env=env, timeout=600)
        
        success = result["returncode"] == 0 and not result["timed_out"]
        output = result["stdout"] + "\n" + result["stderr"]
        analysis = ""
        
        if success:
            print(f"\n{GREEN}PASSED ({result['duration']:.2f}s){RESET}")
        else:
            status = "TIMEOUT" if result["timed_out"] else "FAILED"
            print(f"\n{RED}{status} ({result['duration']:.2f}s){RESET}")
            # Print stderr to console for visibility in CI logs
            if result['stderr']:
                print(f"{RED}Stderr:{RESET}")
                print(result['stderr'].strip())
            elif result['stdout']:
                print(f"{YELLOW}Stdout (no stderr):{RESET}")
                print(result['stdout'].strip())
                
            analysis = analyze_failure(file_path, output, result['duration'])
            
        results.append({
            "file": rel_path,
            "success": success,
            "duration": result["duration"],
            "output": output,
            "analysis": analysis
        })

    process_results(results, "TypeScript")
    return all(r['success'] for r in results)

def main():
    parser = argparse.ArgumentParser(description="Run SDK examples for inspection.")
    parser.add_argument("--lang", choices=["all", "python", "golang", "typescript"], default="all", help="Language to check")
    parser.add_argument("--limit", type=int, default=0, help="Limit number of examples per language (0 for all)")
    args = parser.parse_args()
    
    project_root = os.getcwd()
    if os.path.basename(project_root) == "scripts":
        project_root = os.path.dirname(project_root)
        
    print(f"Project Root: {project_root}")
    
    # Initialize report file
    if not os.path.exists(REPORT_FILE):
        with open(REPORT_FILE, "w", encoding="utf-8") as f:
            f.write("# 示例代码巡检报告\n\n")
            f.write(f"生成时间: {time.strftime('%Y-%m-%d %H:%M:%S')}\n")
    
    success = True
    
    if args.lang in ["all", "python"]:
        if not check_python_examples(project_root, args.limit):
            success = False
            
    if args.lang in ["all", "typescript"]:
        if not check_typescript_examples(project_root, args.limit):
            success = False
            
    if args.lang in ["all", "golang"]:
        if not check_golang_examples(project_root, args.limit):
            success = False
            
    if not success:
        sys.exit(1)
    else:
        print(f"\n{GREEN}All examples passed!{RESET}")
        sys.exit(0)

if __name__ == "__main__":
    main()
