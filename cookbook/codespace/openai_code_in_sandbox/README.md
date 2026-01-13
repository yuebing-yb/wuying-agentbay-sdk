# Qwen Code Generator

AI code generation tool using Alibaba Cloud Qwen model in AgentBay cloud environment.

## Setup

1. Install dependencies:
```bash
pip install -r requirements.txt
```

2. Set environment variables:
```bash
export AGENTBAY_API_KEY='your-agentbay-api-key'
export DASHSCOPE_API_KEY='your-dashscope-api-key'
```

## Usage

```bash
# Interactive mode
python src/run_qwen_code_generator.py

# With prompt
python src/run_qwen_code_generator.py "Create a login page"
```

## Features

- Cost-effective Qwen model
- Cloud-based execution
- Supports HTML/CSS/JavaScript, Python, and more

## Troubleshooting

- **Import Error**: Run `pip install -r requirements.txt`
- **API Key Error**: Check environment variables
- **Session Failed**: Verify network and API keys
