import os
import re

def process_file(file_path):
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    original_content = content
    
    # 1. Fix Eval Modules (python/agentbay/_sync/eval/*.py and python/agentbay/_async/eval/*.py)
    # These should use public API: from agentbay import ...
    if '/eval/' in file_path:
        # Replace from agentbay._common... import ... with from agentbay import ...
        content = re.sub(r'from\s+agentbay\._common[a-zA-Z0-9_.]*\s+import', 'from agentbay import', content)
        # Replace from agentbay._sync... import ... with from agentbay import ...
        content = re.sub(r'from\s+agentbay\._sync[a-zA-Z0-9_.]*\s+import', 'from agentbay import', content)
        # Replace from agentbay._async... import ... with from agentbay import ...
        content = re.sub(r'from\s+agentbay\._async[a-zA-Z0-9_.]*\s+import', 'from agentbay import', content)
        
    # 2. Fix Core Modules (python/agentbay/_sync/*.py and python/agentbay/_async/*.py)
    # These should use relative imports: from .._common...
    elif '/_sync/' in file_path or '/_async/' in file_path:
        # Replace from agentbay._common... import ... with from .._common... import ...
        content = re.sub(r'from\s+agentbay\._common', 'from .._common', content)
        
        # Replace from agentbay.api... import ... with from ..api... import ...
        content = re.sub(r'from\s+agentbay\.api', 'from ..api', content)

    # 3. Fix API Module (python/agentbay/api/*.py)
    elif '/agentbay/api/' in file_path:
        # Replace from agentbay._common... import ... with from .._common... import ...
        content = re.sub(r'from\s+agentbay\._common', 'from .._common', content)
        # Replace from agentbay.api... import ... with from . import ... (if referencing sibling)
        content = re.sub(r'from\s+agentbay\.api\.', 'from .', content)

    # 4. Fix Common Module (python/agentbay/_common/*.py)
    elif '/agentbay/_common/' in file_path:
        # Replace from agentbay._common... import ... with from . import ... or from .._common
        # Case 1: from agentbay._common.logger import -> from .logger import
        content = re.sub(r'from\s+agentbay\._common\.([a-zA-Z0-9_]+)', r'from .\1', content)
        # Case 2: from agentbay._common import -> from . import
        content = re.sub(r'from\s+agentbay\._common\s+import', 'from . import', content)

    if content != original_content:
        print(f"Updating {file_path}")
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(content)

def main():
    target_dirs = [
        "python/agentbay"
    ]
    
    root_dir = "/Users/liyuebing/Projects/wuying-agentbay-sdk"
    
    for d in target_dirs:
        full_path = os.path.join(root_dir, d)
        for root, _, files in os.walk(full_path):
            for file in files:
                if file.endswith(".py"):
                    # Skip __init__.py to avoid messing up exports (though usually fine)
                    # if file == "__init__.py": continue
                    process_file(os.path.join(root, file))

if __name__ == "__main__":
    main()

