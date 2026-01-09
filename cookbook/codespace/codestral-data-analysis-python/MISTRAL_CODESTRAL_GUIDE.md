# Mistral Codestral + AgentBay Data Analysis Integration Guide

This guide demonstrates how to use Mistral's Codestral model with AgentBay for AI-driven data analysis.

## 🎯 Features

- **AI Code Generation**: Use Mistral Codestral model to generate professional Python data analysis code
- **Secure Execution Environment**: Safely execute AI-generated code in AgentBay cloud sandbox
- **Automatic Visualization**: Automatically capture and save matplotlib-generated charts
- **Complete Data Pipeline**: Full workflow from data upload to analysis results
- **Multiple Analysis Types**: Support for sales analysis, trend analysis, customer segmentation, and other analysis scenarios

## 📋 Prerequisites

### 1. API Keys
- **AgentBay API Key**: Get from [AgentBay Console](https://agentbay.console.aliyun.com/)
- **Mistral API Key**: Get from [Mistral AI Console](https://console.mistral.ai/api-keys/)

### 2. Python Environment
- Python 3.8+
- Virtual environment recommended

## 🚀 Quick Start

### 1. Install Dependencies

```bash
pip install -r mistral_requirements.txt
```

### 2. Configure Environment Variables

Set operating system environment variables:

**Windows (PowerShell):**
```powershell
# Set environment variables
$env:AGENTBAY_API_KEY = "your_agentbay_api_key_here"
$env:MISTRAL_API_KEY = "your_mistral_api_key_here"

# Permanent setting (optional)
setx AGENTBAY_API_KEY "your_agentbay_api_key_here"
setx MISTRAL_API_KEY "your_mistral_api_key_here"
```

**Linux/MacOS (Bash):**
```bash
# Temporary setting
export AGENTBAY_API_KEY="your_agentbay_api_key_here"
export MISTRAL_API_KEY="your_mistral_api_key_here"

# Permanent setting (add to ~/.bashrc or ~/.zshrc)
echo 'export AGENTBAY_API_KEY="your_agentbay_api_key_here"' >> ~/.bashrc
echo 'export MISTRAL_API_KEY="your_mistral_api_key_here"' >> ~/.bashrc
source ~/.bashrc
```

### 3. Verify Environment Variables

Verify that environment variables are correctly set:

**Windows (PowerShell):**
```powershell
# Check environment variables
echo $env:AGENTBAY_API_KEY
echo $env:MISTRAL_API_KEY

# Or verify using Python
python -c "import os; print('AGENTBAY_API_KEY:', 'SET' if os.environ.get('AGENTBAY_API_KEY') else 'NOT SET'); print('MISTRAL_API_KEY:', 'SET' if os.environ.get('MISTRAL_API_KEY') else 'NOT SET')"
```

**Linux/MacOS (Bash):**
```bash
# Check environment variables
echo $AGENTBAY_API_KEY
echo $MISTRAL_API_KEY

# Or verify using Python
python -c "import os; print('AGENTBAY_API_KEY:', 'SET' if os.environ.get('AGENTBAY_API_KEY') else 'NOT SET'); print('MISTRAL_API_KEY:', 'SET' if os.environ.get('MISTRAL_API_KEY') else 'NOT SET')"
```

### 4. Run Quick Analysis

```bash
python run_mistral_analysis.py --quick
```

### 5. Run Custom Analysis

```bash
python run_mistral_analysis.py --custom "Analyze regional sales performance and create map visualization"
```

## 📋 Command Details

### Basic Commands

```bash
# Quick analysis (using predefined analysis templates)
python run_mistral_analysis.py --quick

# Custom analysis
python run_mistral_analysis.py --custom "Your analysis requirements"

# Generate sample dataset only
python run_mistral_analysis.py --generate-data

# Show help information
python run_mistral_analysis.py --help
```

### Specific Usage Examples

#### 1. Sales Overview Analysis
```bash
python run_mistral_analysis.py --custom "Create sales overview including total revenue, order count, and average order value, with bar chart showing top 5 product categories by revenue"
```

#### 2. Trend Analysis
```bash
python run_mistral_analysis.py --custom "Analyze sales trends, create monthly revenue trend line chart and identify seasonal patterns"
```

#### 3. Customer Segmentation Analysis
```bash
python run_mistral_analysis.py --custom "Analyze customer segments (Premium, Regular, New), compare revenue contribution, average order value and order frequency, display with pie chart"
```

#### 4. Geographic Analysis
```bash
python run_mistral_analysis.py --custom "Analyze geographic performance, show regional revenue distribution and identify best performing cities, create bar chart"
```

#### 5. Comprehensive Dashboard
```bash
python run_mistral_analysis.py --custom "Create comprehensive dashboard with multiple subplots: 1) Category revenue 2) Monthly trends 3) Customer segment comparison 4) Regional performance"
```

### Complete Workflow Example

```bash
# 1. Enter project directory
cd cookbook/codespace/api-testing-suite

# 2. Set environment variables (Windows PowerShell)
$env:AGENTBAY_API_KEY = "your_agentbay_api_key_here"
$env:MISTRAL_API_KEY = "your_mistral_api_key_here"

# 3. Verify environment variables
python -c "import os; print('AGENTBAY_API_KEY:', 'SET' if os.environ.get('AGENTBAY_API_KEY') else 'NOT SET'); print('MISTRAL_API_KEY:', 'SET' if os.environ.get('MISTRAL_API_KEY') else 'NOT SET')"

# 4. Install dependencies (if not already installed)
pip install -r mistral_requirements.txt

# 5. Run quick analysis
python run_mistral_analysis.py --quick
```

### Direct Python Script Usage

If you want to use the main script directly instead of the runner:

```bash
# Run main analysis script directly
python mistral_codestral_data_analysis.py
```

### Usage in Python Code

```python
# Use in your own Python script
from mistral_codestral_data_analysis import MistralCodestralAnalyzer

# Create analyzer instance
analyzer = MistralCodestralAnalyzer()

# Create session
analyzer.create_agentbay_session()

# Upload dataset (if you have your own data)
analyzer.upload_dataset("your_data.csv")

# Run analysis
result = analyzer.analyze_data("Your analysis requirements")

# Clean up resources
analyzer.cleanup()
```

## 📁 File Structure

```
cookbook/codespace/api-testing-suite/
├── mistral_codestral_data_analysis.py  # Main implementation file
├── run_mistral_analysis.py             # Quick run script
├── mistral_requirements.txt            # Dependency list
└── MISTRAL_CODESTRAL_GUIDE.md         # This guide document
```

## 🔧 Core Components

### MistralCodestralAnalyzer Class

Main analyzer class providing the following functionality:

- `create_agentbay_session()`: Create AgentBay session
- `upload_dataset()`: Upload dataset to cloud environment
- `generate_code_with_codestral()`: Generate code using Codestral
- `execute_python_code()`: Execute code in cloud environment
- `analyze_data()`: Complete data analysis workflow

### Key Features

1. **Intelligent Code Generation**: Codestral is specifically optimized for code generation, producing high-quality data analysis code
2. **Secure Execution**: All code executes in AgentBay sandbox, ensuring security
3. **Automatic Visualization Capture**: Automatically save matplotlib-generated charts
4. **Error Handling**: Comprehensive error handling and logging

## 📊 Supported Analysis Types

### 1. Sales Overview Analysis
```python
analyzer.analyze_data("Create sales overview including total revenue, order count, and average order value, with bar chart showing top 5 product categories by revenue")
```

### 2. Trend Analysis
```python
analyzer.analyze_data("Analyze sales trends, create monthly revenue trend line chart and identify seasonal patterns")
```

### 3. Customer Segmentation Analysis
```python
analyzer.analyze_data("Analyze customer segments (Premium, Regular, New), compare revenue contribution, average order value and order frequency")
```

### 4. Geographic Analysis
```python
analyzer.analyze_data("Analyze geographic performance, show regional revenue distribution and identify best performing cities")
```

### 5. Comprehensive Dashboard
```python
analyzer.analyze_data("Create comprehensive dashboard with multiple subplots: 1) Category revenue 2) Monthly trends 3) Customer segment comparison 4) Regional performance")
```

## 🛠️ Advanced Usage

### Custom Dataset

If you have your own dataset, you can use it directly:

```python
from mistral_codestral_data_analysis import MistralCodestralAnalyzer

analyzer = MistralCodestralAnalyzer()
analyzer.create_agentbay_session()
analyzer.upload_dataset("your_dataset.csv", "/tmp/user/your_data.csv")
result = analyzer.analyze_data("Your analysis requirements")
```

### Batch Analysis

```python
analyses = [
    "Sales overview analysis",
    "Trend analysis", 
    "Customer segmentation analysis"
]

for analysis in analyses:
    result = analyzer.analyze_data(analysis)
    if result['success']:
        print(f"✅ {analysis} completed")
```

## 🔍 Differences from OpenAI Version

| Feature | OpenAI Version | Mistral Codestral Version |
|---------|----------------|---------------------------|
| **Model** | GPT-3.5/4 | Codestral-latest |
| **Tool Calling** | Supports Function Calling | Direct code generation |
| **Code Quality** | General AI model | Professional code generation model |
| **Response Format** | JSON tool calls | Markdown code blocks |
| **Specialization** | General intelligence | Code generation focused |

## 🎨 Codestral Model Features

### Advantages
- **Professional Code Generation**: Specifically optimized for code generation tasks
- **High-Quality Output**: Generated code is well-structured with comprehensive comments
- **Multi-Language Support**: Supports Python, JavaScript, Java, and other languages
- **Fast Response**: Inference speed optimized for code generation

### Use Cases
- Data analysis script generation
- Visualization code creation
- Algorithm implementation
- Code refactoring and optimization

## 🚨 Important Notes

1. **API Limits**: Pay attention to Mistral API rate limits
2. **Code Security**: Although executed in sandbox, still need to consider generated code security
3. **Data Privacy**: Ensure uploaded data complies with privacy requirements
4. **Resource Management**: Clean up AgentBay sessions promptly to avoid resource waste

## 🔧 Troubleshooting

### Common Issues

1. **API Key Error**
   ```
   ❌ MISTRAL_API_KEY not set in environment variables
   ```
   Solution: Check if environment variables are correctly set
   ```powershell
   # Windows PowerShell check
   echo $env:MISTRAL_API_KEY
   echo $env:AGENTBAY_API_KEY
   
   # If empty, reset
   $env:MISTRAL_API_KEY = "your_mistral_api_key"
   $env:AGENTBAY_API_KEY = "your_agentbay_api_key"
   ```

2. **AgentBay Session Creation Failed**
   ```
   ❌ Failed to create AgentBay session
   ```
   Solution: Check AGENTBAY_API_KEY and network connection

3. **Code Generation Failed**
   ```
   ❌ No Python code found in Codestral response
   ```
   Solution: Try simplifying analysis request or rephrasing requirements

4. **Missing Dependencies**
   ```
   ❌ Missing required packages: mistralai
   ```
   Solution: Run `pip install -r mistral_requirements.txt`

### Debug Mode

Enable verbose logging in code:

```python
import logging
logging.basicConfig(level=logging.DEBUG)

analyzer = MistralCodestralAnalyzer()
# ... other code
```

## 📈 Performance Optimization

1. **Batch Processing**: For multiple analysis tasks, reuse the same AgentBay session
2. **Result Caching**: Cache results for identical analysis requests
3. **Concurrency Control**: Avoid creating too many AgentBay sessions simultaneously

## 🤝 Contributing

Welcome to submit Issues and Pull Requests to improve this integration example.

## 📄 License

This project follows the MIT License.
