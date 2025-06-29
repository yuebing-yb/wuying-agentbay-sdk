import os
from setuptools import setup, find_packages

# 读取 README.md 文件内容作为 long_description
with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

# 获取版本号，如果环境变量中没有设置，则使用默认值
version = os.getenv("RELEASE_VERSION", "0.3.0")

setup(
    name="wuying_agentbay_sdk",
    version=version,
    author="Alibaba Cloud",
    author_email="wuying@alibaba-inc.com",
    description="Python SDK for AgentBay service",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/aliyun/wuying-agentbay-sdk",
    packages=find_packages(exclude=["tests*"]),
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: Apache Software License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Topic :: Software Development :: Libraries :: Python Modules",
    ],
    python_requires=">=3.7",
    install_requires=[
        "requests>=2.25.0",
        "urllib3>=1.26.0",
        "typing-extensions>=4.0.0",
        "pydantic>=1.8.0",
    ],
    extras_require={
        "dev": [
            "pytest>=6.0.0",
            "pytest-cov>=2.10.0",
            "black>=22.0.0",
            "isort>=5.0.0",
            "mypy>=0.900",
            "flake8>=3.9.0",
        ],
        "test": [
            "pytest>=6.0.0",
            "pytest-cov>=2.10.0",
        ],
    },
    project_urls={
        "Bug Tracker": "https://github.com/aliyun/wuying-agentbay-sdk/issues",
        "Documentation": "https://github.com/aliyun/wuying-agentbay-sdk/blob/main/README.md",
        "Source Code": "https://github.com/aliyun/wuying-agentbay-sdk",
    },
    keywords=[
        "alibaba",
        "aliyun",
        "wuying",
        "agentbay",
        "sdk",
        "cloud",
        "api"
    ],
)