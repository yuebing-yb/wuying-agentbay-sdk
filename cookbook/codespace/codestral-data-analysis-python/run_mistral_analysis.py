#!/usr/bin/env python3
"""
Quick runner script for Mistral Codestral data analysis demo.

This script provides a simple interface to run the Mistral Codestral data analysis
with different analysis types and configurations.
"""

import os
import sys
import argparse
from pathlib import Path

# Add the current directory to Python path for imports
sys.path.insert(0, str(Path(__file__).parent))

from mistral_codestral_data_analysis import MistralCodestralAnalyzer, generate_sample_dataset


# Note: load_env_file function removed - now using OS environment variables directly
# Set environment variables using:
# PowerShell: $env:AGENTBAY_API_KEY = "your_api_key"
# PowerShell: $env:MISTRAL_API_KEY = "your_api_key"


def check_requirements():
    """Check if required packages are installed."""
    required_packages = ['mistralai', 'agentbay']
    missing_packages = []
    
    for package in required_packages:
        try:
            __import__(package)
        except ImportError:
            missing_packages.append(package)
    
    if missing_packages:
        print(f"❌ Missing required packages: {', '.join(missing_packages)}")
        print("💡 Install with: pip install -r mistral_requirements.txt")
        return False
    
    return True


def run_quick_analysis():
    """Run a quick analysis with predefined requests."""
    print("🚀 Running Quick Mistral Codestral Analysis")
    print("=" * 60)
    
    # Check requirements
    if not check_requirements():
        return False
    
    # Check API keys from OS environment variables
    if not os.environ.get("AGENTBAY_API_KEY"):
        print("❌ AGENTBAY_API_KEY not set in environment variables")
        print("💡 Set with: $env:AGENTBAY_API_KEY = 'your_api_key' (PowerShell)")
        return False
    
    if not os.environ.get("MISTRAL_API_KEY"):
        print("❌ MISTRAL_API_KEY not set in environment variables")
        print("💡 Set with: $env:MISTRAL_API_KEY = 'your_api_key' (PowerShell)")
        return False
    
    # Initialize analyzer
    analyzer = MistralCodestralAnalyzer()
    
    try:
        # Create session
        if not analyzer.create_agentbay_session():
            return False
        
        # Generate or use existing dataset
        dataset_file = "sample_ecommerce_data.csv"
        if not os.path.exists(dataset_file):
            print("📊 Generating sample dataset...")
            if not generate_sample_dataset(dataset_file):
                return False
        
        # Upload dataset
        if not analyzer.upload_dataset(dataset_file):
            return False
        
        # Validate dataset
        if not analyzer.validate_dataset():
            return False
        
        # Run a simple analysis
        analysis_request = """
        Create a comprehensive sales analysis including:
        1. Total revenue, number of orders, and average order value
        2. Top 5 product categories by revenue with a bar chart
        3. Monthly revenue trends with a line chart
        4. Customer segment analysis (Premium, Regular, New) with pie chart
        
        Use matplotlib to create a 2x2 subplot layout with all visualizations.
        """
        
        print("\n🔍 Running comprehensive sales analysis...")
        result = analyzer.analyze_data(analysis_request)
        
        if result['success']:
            print("✅ Analysis completed successfully!")
            if result['visualization_path']:
                print(f"📈 Visualization saved: {result['visualization_path']}")
            print("\n📊 Analysis Results:")
            print("-" * 40)
            print(result['execution_result'])
        else:
            print(f"❌ Analysis failed: {result['error']}")
            return False
        
        return True
        
    except Exception as e:
        print(f"❌ Error during analysis: {e}")
        return False
    finally:
        analyzer.cleanup()


def run_custom_analysis(analysis_request: str):
    """Run analysis with custom request."""
    print(f"🚀 Running Custom Mistral Codestral Analysis")
    print("=" * 60)
    
    # Check requirements
    if not check_requirements():
        return False
    
    # Check API keys from OS environment variables
    if not os.environ.get("AGENTBAY_API_KEY"):
        print("❌ AGENTBAY_API_KEY not set in environment variables")
        print("💡 Set with: $env:AGENTBAY_API_KEY = 'your_api_key' (PowerShell)")
        return False
    
    if not os.environ.get("MISTRAL_API_KEY"):
        print("❌ MISTRAL_API_KEY not set in environment variables")
        print("💡 Set with: $env:MISTRAL_API_KEY = 'your_api_key' (PowerShell)")
        return False
    
    # Initialize analyzer
    analyzer = MistralCodestralAnalyzer()
    
    try:
        # Create session
        if not analyzer.create_agentbay_session():
            return False
        
        # Generate or use existing dataset
        dataset_file = "sample_ecommerce_data.csv"
        if not os.path.exists(dataset_file):
            print("📊 Generating sample dataset...")
            if not generate_sample_dataset(dataset_file):
                return False
        
        # Upload dataset
        if not analyzer.upload_dataset(dataset_file):
            return False
        
        # Validate dataset
        if not analyzer.validate_dataset():
            return False
        
        # Run custom analysis
        print(f"\n🔍 Running custom analysis: {analysis_request}")
        result = analyzer.analyze_data(analysis_request)
        
        if result['success']:
            print("✅ Analysis completed successfully!")
            if result['visualization_path']:
                print(f"📈 Visualization saved: {result['visualization_path']}")
            print("\n📊 Analysis Results:")
            print("-" * 40)
            print(result['execution_result'])
        else:
            print(f"❌ Analysis failed: {result['error']}")
            return False
        
        return True
        
    except Exception as e:
        print(f"❌ Error during analysis: {e}")
        return False
    finally:
        analyzer.cleanup()


def main():
    """Main function with command line interface."""
    parser = argparse.ArgumentParser(
        description="Run Mistral Codestral data analysis with AgentBay",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python run_mistral_analysis.py --quick
  python run_mistral_analysis.py --custom "Analyze sales by region and create a map visualization"
  python run_mistral_analysis.py --generate-data

Note: Set environment variables before running:
  PowerShell: $env:AGENTBAY_API_KEY = "your_api_key"
  PowerShell: $env:MISTRAL_API_KEY = "your_api_key"
        """
    )
    
    parser.add_argument(
        '--quick', 
        action='store_true',
        help='Run quick analysis with predefined requests'
    )
    
    parser.add_argument(
        '--custom',
        type=str,
        help='Run custom analysis with specified request'
    )
    
    # Note: --env argument removed - now using OS environment variables directly
    
    parser.add_argument(
        '--generate-data',
        action='store_true',
        help='Only generate sample dataset and exit'
    )
    
    args = parser.parse_args()
    
    # Handle generate data only
    if args.generate_data:
        print("📊 Generating sample dataset...")
        if generate_sample_dataset():
            print("✅ Sample dataset generated successfully")
            return 0
        else:
            print("❌ Failed to generate sample dataset")
            return 1
    
    # Handle analysis modes
    if args.quick:
        success = run_quick_analysis()
    elif args.custom:
        success = run_custom_analysis(args.custom)
    else:
        print("❌ Please specify either --quick or --custom analysis mode")
        parser.print_help()
        return 1
    
    return 0 if success else 1


if __name__ == "__main__":
    sys.exit(main())
