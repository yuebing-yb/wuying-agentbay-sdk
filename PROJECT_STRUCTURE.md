# Wuying AgentBay SDK Project Structure

This document provides an overview of the Wuying AgentBay SDK project structure.

## Overview

The Wuying AgentBay SDK is a multi-language SDK that provides APIs for interacting with the Wuying AgentBay cloud runtime environment. The SDK is available in Python, TypeScript, and Golang.

## Directory Structure

```
wuying-agentbay-sdk/
├── LICENSE                 # Apache License 2.0
├── README.md               # Project overview and documentation
├── PROJECT_STRUCTURE.md    # This file
├── .gitignore              # Git ignore file
│
├── python/                 # Python SDK
│   ├── agentbay/           # Python package
│   │   ├── __init__.py     # Package initialization
│   │   ├── agent_bay.py    # AgentBay class implementation
│   │   ├── session.py      # Session class implementation
│   │   └── exceptions.py   # Exception classes
│   ├── examples/           # Example usage
│   │   └── basic_usage.py  # Basic usage example
│   ├── tests/              # Unit tests
│   │   ├── test_agent_bay.py  # Tests for AgentBay class
│   │   └── test_session.py    # Tests for Session class
│   └── setup.py            # Package setup script
│
├── typescript/             # TypeScript SDK
│   ├── src/                # Source code
│   │   ├── index.ts        # Main entry point
│   │   ├── agent-bay.ts    # AgentBay class implementation
│   │   ├── session.ts      # Session class implementation
│   │   └── exceptions.ts   # Exception classes
│   ├── examples/           # Example usage
│   │   └── basic-usage.ts  # Basic usage example
│   ├── tests/              # Unit tests
│   │   ├── agent-bay.test.ts  # Tests for AgentBay class
│   │   └── session.test.ts    # Tests for Session class
│   ├── package.json        # Package configuration
│   ├── tsconfig.json       # TypeScript configuration
│   └── README.md           # TypeScript SDK documentation
│
└── golang/                 # Golang SDK
    ├── pkg/                # Package code
    │   └── agentbay/       # AgentBay package
    │       ├── agentbay.go        # AgentBay implementation
    │       ├── agentbay_test.go   # Tests for AgentBay
    │       ├── session.go         # Session implementation
    │       └── session_test.go    # Tests for Session
    ├── cmd/                # Command-line tools
    │   └── agentbay/       # AgentBay CLI
    │       └── main.go     # CLI entry point
    ├── examples/           # Example usage
    │   └── basic_usage.go  # Basic usage example
    ├── go.mod              # Go module file
    └── README.md           # Golang SDK documentation
```

## Core Concepts

- **AgentBay**: The main client class for interacting with the Wuying AgentBay cloud runtime environment.
- **Session**: Represents a session in the Wuying AgentBay cloud environment.

## API Functionality

### Session Management
- Create a new session
- Get information about a session
- List all sessions
- Delete a session

### File Management
- Read a file
- Write a file

### Command Execution
- Execute a command

## Authentication

Authentication is done using an API key, which can be provided in several ways:
1. As a parameter when initializing the SDK
2. Through environment variables (`AGENTBAY_API_KEY`)

## Implementation Status

- **Python SDK**: Fully implemented
- **TypeScript SDK**: Fully implemented
- **Golang SDK**: Fully implemented
