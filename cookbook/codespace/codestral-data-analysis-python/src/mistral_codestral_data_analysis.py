#!/usr/bin/env python3
"""
AgentBay + Mistral Codestral Integration: E-commerce Sales Analysis

This example demonstrates how to integrate AgentBay with Mistral's Codestral model
to perform automated data analysis on e-commerce sales data.

Features:
1. Creating an AgentBay CodeSpace environment
2. Uploading a sales dataset to the session
3. Using Mistral Codestral to generate Python code for data analysis
4. Executing the code in the AgentBay CodeSpace
5. Retrieving and saving visualization results

Key differences from OpenAI version:
- Uses Mistral AI's Codestral model (codestral-latest)
- Direct code generation without function calling (Codestral doesn't support tools yet)
- Optimized prompts for Codestral's code generation capabilities
"""

import os
import json
import base64
import re
from typing import Dict, Any, Optional
from mistralai import Mistral
from agentbay import AgentBay, CreateSessionParams

# Configuration
MODEL_NAME = "codestral-latest"

SYSTEM_PROMPT = """You are an expert Python data analyst specializing in e-commerce analytics. Your task is to analyze sales data and generate Python code for comprehensive data analysis.

## Dataset Information
The sales dataset is located at `/tmp/user/ecommerce_sales.csv` with the following structure:
- Delimiter: `,` (comma)
- Columns:
  * Date: Order date in YYYY-MM-DD format
  * OrderID: Unique order identifier
  * ProductID, ProductName: Product identifiers
  * Category: Product category (Electronics, Clothing, Home & Garden, Books, Sports, Toys)
  * Brand: Brand name
  * UnitPrice: Price per unit in USD
  * Quantity: Number of units purchased
  * TotalAmount: Total order value (UnitPrice × Quantity)
  * CustomerID: Unique customer identifier
  * CustomerSegment: Customer tier (Premium, Regular, New)
  * Region: Geographic region (North America, Europe, Asia Pacific, Latin America)
  * City: City name
  * PaymentMethod: Payment type (Credit Card, PayPal, Bank Transfer, Digital Wallet)
  * ShippingMethod: Delivery method (Standard, Express, Next Day)

## Execution Environment
- Code runs in a secure AgentBay CodeSpace environment
- Pre-installed packages: pandas, numpy, matplotlib, seaborn, scikit-learn
- Use matplotlib for visualizations (they will be captured automatically)
- You have full filesystem access and can install additional packages via pip if needed

## Code Generation Guidelines
- Generate ONLY Python code, no explanations
- Write clean, well-commented code
- Handle missing or invalid data appropriately
- Use appropriate visualization techniques for different data types
- Create matplotlib figures that will be automatically saved
- Always use plt.tight_layout() and plt.show() for visualizations
- Include print statements for key insights and metrics

## Response Format
Respond with ONLY Python code wrapped in ```python code blocks. Do not include any explanations outside the code block.
"""

class MistralCodestralAnalyzer:
    """Mistral Codestral-powered data analyzer with AgentBay integration."""
    
    def __init__(self, api_key: Optional[str] = None):
        """Initialize the analyzer with Mistral client."""
        print("🚀 Initializing AgentBay client...")
        self.mistral_client = Mistral(api_key=os.environ.get("MISTRAL_API_KEY"))
        print(f"get api_key={os.environ.get('AGENTBAY_API_KEY')}")
        self.agentbay = AgentBay(api_key=os.environ.get("AGENTBAY_API_KEY"))
        self.session = None
        
    def create_agentbay_session(self) -> bool:
        """Create an AgentBay session with code_latest image."""
        print("🚀 Creating AgentBay CodeSpace session...")
        
        try:
            result = self.agentbay.create(CreateSessionParams(image_id="code_latest"))
            if result.success:
                self.session = result.session
                print("✅ AgentBay session created successfully")
                return True
            else:
                print(f"❌ Failed to create AgentBay session: {result}")
                return False
        except Exception as e:
            print(f"❌ Error creating AgentBay session: {e}")
            return False
    
    def upload_dataset(self, local_path: str, remote_path: str = '/tmp/user/ecommerce_sales.csv') -> bool:
        """Upload a dataset file to the AgentBay session."""
        print(f'📤 Uploading dataset to AgentBay session...')

        if not os.path.exists(local_path):
            print(f'❌ Dataset file not found: {local_path}')
            return False

        try:
            # Read local file
            with open(local_path, 'r', encoding='utf-8') as f:
                content = f.read()

            # Ensure directory exists
            remote_dir = os.path.dirname(remote_path)
            self.session.file_system.create_directory(remote_dir)
            
            # Upload file
            result = self.session.file_system.write_file(remote_path, content)

            if result.success:
                print(f'✅ Dataset uploaded to {remote_path}')
                return True
            else:
                print(f'❌ Failed to upload dataset: {result.error_message}')
                return False
                
        except Exception as e:
            print(f'❌ Error uploading dataset: {e}')
            return False
    
    def generate_code_with_codestral(self, user_request: str) -> Optional[str]:
        """Generate Python code using Mistral Codestral."""
        print('🧠 Generating Python code with Mistral Codestral...')
        
        try:
            messages = [
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": user_request}
            ]
            
            response = self.mistral_client.chat.complete(
                model=MODEL_NAME,
                messages=messages,
                temperature=0.1,
                max_tokens=2000
            )
            
            response_content = response.choices[0].message.content
            
            # Extract Python code from response
            code_blocks = re.findall(r'```python\n(.*?)\n```', response_content, re.DOTALL)
            
            if code_blocks:
                code = code_blocks[0].strip()
                print("✅ Code generated successfully")
                return code
            else:
                # If no code blocks found, try to extract code directly
                # Codestral sometimes returns code without markdown formatting
                lines = response_content.strip().split('\n')
                if any(line.strip().startswith(('import ', 'from ', 'df = ', 'plt.')) for line in lines):
                    print("✅ Code generated successfully (direct format)")
                    return response_content.strip()
                else:
                    print("❌ No Python code found in Codestral response")
                    print(f"Response: {response_content}")
                    return None
                    
        except Exception as e:
            print(f"❌ Error generating code with Codestral: {e}")
            return None
    
    def execute_python_code(self, code: str) -> Dict[str, Any]:
        """Execute Python code in the AgentBay session."""
        print("🔧 Executing Python code in AgentBay session...")

        try:
            result = self.session.code.run_code(code, "python", timeout_s=120)

            execution_result = {
                'success': result.success,
                'result': '',
                'error': None,
                'png_path': None
            }

            if not result.success:
                execution_result['error'] = result.error_message
                print(f"❌ Code execution failed: {result.error_message}")
                return execution_result

            # Store the execution result
            execution_result['result'] = result.result
            print(f"✅ Code executed successfully")
            if result.result:
                print(f"📊 Execution output:\n{result.result}")

            # Check for image results
            for res in result.results:
                if res.png:
                    print("📈 Visualization detected in execution results...")
                    local_path = 'codestral_analysis.png'
                    try:
                        with open(local_path, "wb") as f:
                            f.write(base64.b64decode(res.png))
                        execution_result['png_path'] = local_path
                        print(f"✅ Visualization saved to {local_path}")
                    except Exception as e:
                        print(f"⚠️  Failed to save visualization: {e}")
                    break
                elif res.jpeg:
                    print("📈 Visualization (JPEG) detected in execution results...")
                    local_path = 'codestral_analysis.jpg'
                    try:
                        with open(local_path, "wb") as f:
                            f.write(base64.b64decode(res.jpeg))
                        execution_result['png_path'] = local_path
                        print(f"✅ Visualization saved to {local_path}")
                    except Exception as e:
                        print(f"⚠️  Failed to save visualization: {e}")
                    break

            return execution_result
            
        except Exception as e:
            print(f"❌ Error executing code: {e}")
            return {
                'success': False,
                'result': '',
                'error': str(e),
                'png_path': None
            }
    
    def validate_dataset(self, remote_path: str = '/tmp/user/ecommerce_sales.csv') -> bool:
        """Validate the uploaded dataset structure."""
        print(f'🔍 Validating dataset...')

        validation_code = f"""
import pandas as pd
import numpy as np

try:
    df = pd.read_csv('{remote_path}')
    print(f"✅ Dataset loaded successfully")
    print(f"📊 Total rows: {{len(df)}}")
    print(f"📊 Total columns: {{len(df.columns)}}")
    print(f"📅 Date range: {{df['Date'].min()}} to {{df['Date'].max()}}")
    print(f"💰 Total revenue: ${{df['TotalAmount'].sum():,.2f}}")
    print(f"🏷️  Categories: {{', '.join(df['Category'].unique())}}")
    print(f"👥 Customer segments: {{', '.join(df['CustomerSegment'].unique())}}")
    print(f"🌍 Regions: {{', '.join(df['Region'].unique())}}")
except Exception as e:
    print(f"❌ Error loading dataset: {{e}}")
"""

        result = self.execute_python_code(validation_code)
        return result['success']
    
    def analyze_data(self, analysis_request: str) -> Dict[str, Any]:
        """Perform data analysis using Codestral-generated code."""
        print('\n' + '=' * 80)
        print(f'📋 Analysis Request: {analysis_request}')
        print('=' * 80)

        # Generate code using Codestral
        code = self.generate_code_with_codestral(analysis_request)
        
        if not code:
            return {
                'success': False,
                'error': 'Failed to generate code with Codestral',
                'result': None
            }

        print(f'\n📝 Generated Code:')
        print('-' * 80)
        # Show first 30 lines of code
        code_lines = code.split('\n')
        for i, line in enumerate(code_lines[:30]):
            print(f"{i+1:2d}: {line}")
        if len(code_lines) > 30:
            print(f"... ({len(code_lines) - 30} more lines)")
        print('-' * 80)

        # Execute the generated code
        execution_result = self.execute_python_code(code)
        
        return {
            'success': execution_result['success'],
            'generated_code': code,
            'execution_result': execution_result['result'],
            'error': execution_result['error'],
            'visualization_path': execution_result['png_path']
        }
    
    def cleanup(self):
        """Clean up AgentBay session."""
        if self.session:
            print("🧹 Cleaning up AgentBay session...")
            try:
                self.agentbay.delete(self.session)
                print("✅ Session cleaned up successfully")
            except Exception as e:
                print(f"⚠️  Error during cleanup: {e}")


def generate_sample_dataset(filename: str = "sample_ecommerce_data.csv") -> bool:
    """Generate a sample e-commerce dataset for testing."""
    print("📊 Generating sample e-commerce dataset...")
    
    try:
        import csv
        import random
        from datetime import datetime, timedelta

        # Sample data configuration
        categories = ["Electronics", "Clothing", "Home & Garden", "Books", "Sports", "Toys"]
        segments = ["Premium", "Regular", "New"]
        regions = ["North America", "Europe", "Asia Pacific", "Latin America"]
        cities = {
            "North America": ["New York", "Los Angeles", "Chicago", "Toronto"],
            "Europe": ["London", "Paris", "Berlin", "Amsterdam"],
            "Asia Pacific": ["Singapore", "Tokyo", "Sydney", "Hong Kong"],
            "Latin America": ["Mexico City", "São Paulo", "Buenos Aires", "Santiago"]
        }
        
        records = []
        start_date = datetime(2023, 1, 1)
        end_date = datetime(2024, 12, 31)
        
        for i in range(1000):  # Generate 1000 sample records
            # Random date
            delta = end_date - start_date
            random_days = random.randint(0, delta.days)
            order_date = start_date + timedelta(days=random_days)
            
            # Random data
            category = random.choice(categories)
            region = random.choice(regions)
            city = random.choice(cities[region])
            segment = random.choice(segments)
            
            unit_price = round(random.uniform(10, 500), 2)
            quantity = random.randint(1, 5)
            total_amount = round(unit_price * quantity, 2)
            
            record = {
                "Date": order_date.strftime("%Y-%m-%d"),
                "OrderID": f"ORD{order_date.strftime('%Y%m%d')}{i:04d}",
                "ProductID": f"PROD{category[:4].upper()}{i%100:03d}",
                "ProductName": f"{category} Product {i%10 + 1}",
                "Category": category,
                "Brand": f"Brand{i%5 + 1}",
                "UnitPrice": unit_price,
                "Quantity": quantity,
                "TotalAmount": total_amount,
                "CustomerID": f"CUST{i%200 + 1:04d}",
                "CustomerSegment": segment,
                "Region": region,
                "City": city,
                "PaymentMethod": random.choice(["Credit Card", "PayPal", "Bank Transfer", "Digital Wallet"]),
                "ShippingMethod": random.choice(["Standard", "Express", "Next Day"])
            }
            records.append(record)
        
        # Sort by date
        records.sort(key=lambda x: x["Date"])
        
        # Save to CSV
        with open(filename, 'w', newline='', encoding='utf-8') as csvfile:
            fieldnames = list(records[0].keys())
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(records)
        
        print(f"✅ Generated {len(records)} sample records in {filename}")
        return True
        
    except Exception as e:
        print(f"❌ Error generating sample dataset: {e}")
        return False


def main():
    """Main function to run the Mistral Codestral data analysis demo."""
    print("=" * 80)
    print("AgentBay + Mistral Codestral Integration: E-commerce Sales Analysis")
    print("=" * 80)

    # Check environment variables
    if not os.environ.get("AGENTBAY_API_KEY"):
        print("❌ Please set AGENTBAY_API_KEY environment variable")
        return

    if not os.environ.get("MISTRAL_API_KEY"):
        print("❌ Please set MISTRAL_API_KEY environment variable")
        print("💡 Get your API key from: https://console.mistral.ai/api-keys/")
        return

    # Initialize analyzer
    analyzer = MistralCodestralAnalyzer()

    try:
        # Create AgentBay session
        if not analyzer.create_agentbay_session():
            return

        # Check if dataset exists, if not generate sample data
        dataset_file = "sample_ecommerce_data.csv"
        if not os.path.exists(dataset_file):
            print(f"📊 Dataset {dataset_file} not found, generating sample data...")
            if not generate_sample_dataset(dataset_file):
                return

        # Upload dataset
        if not analyzer.upload_dataset(dataset_file):
            return

        # Validate dataset
        if not analyzer.validate_dataset():
            return

        # Perform various analyses
        analyses = [
            "Create a comprehensive sales overview with total revenue, number of orders, and average order value. Show the top 5 product categories by revenue with a bar chart.",
            
            "Analyze sales trends over time. Create a line chart showing monthly revenue trends and identify any seasonal patterns.",
            
            "Perform customer segment analysis. Compare the three customer segments (Premium, Regular, New) in terms of revenue contribution, average order value, and order frequency. Create visualizations to show the differences.",
            
            "Analyze geographic performance. Show revenue distribution across regions and identify the top performing cities. Create appropriate visualizations.",
            
            "Create a comprehensive dashboard with multiple subplots showing: 1) Revenue by category, 2) Monthly trends, 3) Customer segment comparison, 4) Regional performance."
        ]

        for i, analysis_request in enumerate(analyses, 1):
            print(f"\n🔍 Running Analysis {i}/{len(analyses)}")
            result = analyzer.analyze_data(analysis_request)
            
            if result['success']:
                print(f"✅ Analysis {i} completed successfully")
                if result['visualization_path']:
                    print(f"📈 Visualization saved: {result['visualization_path']}")
            else:
                print(f"❌ Analysis {i} failed: {result['error']}")
            
            # Add a small delay between analyses
            import time
            time.sleep(2)

        print("\n" + "=" * 80)
        print("🎉 All analyses completed!")
        print("📊 Check the generated visualization files for results")
        print("=" * 80)

    except KeyboardInterrupt:
        print("\n⚠️  Analysis interrupted by user")
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
    finally:
        # Cleanup
        analyzer.cleanup()


if __name__ == "__main__":
    main()
