# Qwen Code Generator - AI Code Generation Tool Based on Alibaba Cloud Qwen

## 📖 Project Overview

Qwen Code Generator is an intelligent code generation tool based on Alibaba Cloud's Qwen (Tongyi Qianwen) model, providing secure and efficient code generation services through the AgentBay cloud environment. Compared to other AI code generation tools, it offers advantages such as lower cost, better Chinese language understanding, and more discounts for Alibaba Cloud users.

## 🌟 Key Features

- **💰 Cost Advantage**: Qwen model is cheaper than Claude and other models
- **🇨🇳 Chinese Friendly**: More accurate understanding of Chinese prompts
- **☁️ Cloud Execution**: Based on AgentBay cloud environment, no need for complex local configuration
- **🔒 Security Isolation**: Code generation executes in an isolated cloud environment
- **🎯 Multi-language Support**: Supports generating HTML/CSS/JavaScript, Python, and other code types
- **🚀 One-click Run**: Simple command-line interface for quick code generation

## 📁 Project Structure

```
openai_code_in_sandbox/
├── README.md                    # Project documentation (this file)
├── requirements.txt             # Python dependencies
├── qwen_code_installer.py       # Qwen code generator core class
├── __init__.py                  # Python package initialization file
└── src/
    ├── __init__.py              # Source package initialization file
    └── run_qwen_code_generator.py  # Main execution entry point
```

## 🛠️ Environment Setup

### 1. Install Dependencies

```bash
# Install Python dependencies
pip install -r requirements.txt

# Or install manually
pip install wuying-agentbay-sdk==0.14.0 openai
```

### 2. Configure API Keys

You need to prepare two API keys:

#### AgentBay API Key (Required)
```bash
# Linux/macOS
export AGENTBAY_API_KEY='your-agentbay-api-key'

# Windows
set AGENTBAY_API_KEY=your-agentbay-api-key
```

#### Alibaba Cloud DashScope API Key (Required)
```bash
# Linux/macOS  
export DASHSCOPE_API_KEY='your-dashscope-api-key'

# Windows
set DASHSCOPE_API_KEY=your-dashscope-api-key
```

> **💡 Tip**: How to get API keys?
> - **AgentBay API Key**: Visit AgentBay console to obtain
> - **DashScope API Key**: Visit [Alibaba Cloud DashScope Console](https://dashscope.console.aliyun.com/) to obtain

## 🚀 Usage

### Basic Usage

#### 1. Interactive Mode
```bash
python src/run_qwen_code_generator.py
```
After running, you will be prompted to enter code generation requirements. Press Enter to use the default example.

#### 2. Command Line Arguments
```bash
# Generate a responsive login page
python src/run_qwen_code_generator.py "Create a modern responsive login page"

# Generate Python script
python src/run_qwen_code_generator.py "Write a batch file renaming tool"

# Generate data visualization code
python src/run_qwen_code_generator.py "Generate sales data visualization charts"
```

### Help Commands

```bash
# View usage help
python src/run_qwen_code_generator.py --help

# View usage examples
python src/run_qwen_code_generator.py --examples

# View version information
python src/run_qwen_code_generator.py --version
```

## 💡 Usage Examples

### Web Development Examples

```bash
# Create personal resume webpage
python src/run_qwen_code_generator.py "Create a modern personal resume webpage"

# Build product showcase page
python src/run_qwen_code_generator.py "Build a responsive product showcase page"

# Create colorful clock webpage
python src/run_qwen_code_generator.py "Create a colorful clock webpage"
```

### Python Development Examples

```bash
# Batch file renaming tool
python src/run_qwen_code_generator.py "Write a batch file renaming tool"

# Simple todo list manager
python src/run_qwen_code_generator.py "Create a simple todo list manager"

# Number guessing game
python src/run_qwen_code_generator.py "Create a simple number guessing game"
```

### Data Analysis Examples

```bash
# Sales data visualization
python src/run_qwen_code_generator.py "Generate sales data visualization charts"

# Stock price analysis script
python src/run_qwen_code_generator.py "Write a stock price analysis script"
```

## 🔄 Execution Flow

1. **🚀 Create Cloud Environment**: Create an independent code execution environment in AgentBay
2. **🔧 Environment Configuration**: Install necessary Python dependencies
3. **🔑 Key Configuration**: Configure DashScope API key
4. **🤖 Code Generation**: Call Qwen model to generate code
5. **💾 Save Files**: Save generated code to files
6. **🧹 Environment Cleanup**: Automatically clean up and delete cloud environment

## 🎯 Supported Code Types

- **🌐 Web Development**: HTML/CSS/JavaScript webpages
- **🐍 Python Development**: Scripts and applications
- **📊 Data Analysis**: Data visualization and analysis scripts
- **🔌 API Development**: Interface development
- **🧮 Algorithm Implementation**: Algorithms and data structures

## ⚠️ Important Notes

1. **API Key Security**: Please keep your API keys safe and do not hardcode them in your code
2. **Network Connection**: Ensure stable network connection as code generation requires access to cloud services
3. **Cost Control**: Although Qwen has lower costs, it's still recommended to use it reasonably and avoid unnecessary calls
4. **Generation Quality**: AI-generated code is for reference only, please adjust and test according to actual needs

## 🔧 Troubleshooting

### Common Issues

#### 1. Import Error
```
❌ Error: Cannot import QwenCodeGenerator
```
**Solution**:
- Ensure dependencies are installed: `pip install -r requirements.txt`
- Try running from parent directory: `python -m openai_code_in_sandbox.src.run_qwen_code_generator`

#### 2. API Key Error
```
❌ Error: AGENTBAY_API_KEY environment variable not found
```
**Solution**:
- Check if environment variables are correctly set
- Reset API keys

#### 3. Cloud Environment Creation Failed
```
❌ Failed to create session
```
**Solution**:
- Check network connection
- Verify if AgentBay API key is valid
- Confirm if account balance is sufficient

## 📞 Technical Support

If you encounter problems during usage, you can:

1. Check detailed error information in console output
2. Verify if API key configuration is correct
3. Confirm if network connection is normal
4. Refer to the troubleshooting section in this document

## 📄 License

This project follows the corresponding open source license. Please check the LICENSE file in the project root directory for details.

---

**🎉 Start using Qwen Code Generator and experience the convenience of intelligent code generation!**
