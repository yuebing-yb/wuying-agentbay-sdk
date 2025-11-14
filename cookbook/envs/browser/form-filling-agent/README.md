# Form-Filling Agent

This project demonstrates how to create a form-filling agent using the Agent-Bay SDK. The agent can automatically fill HTML forms with data based on natural language instructions.

## Features

- Uploads an HTML form to Agent-Bay environment
- Opens the form in a browser using Agent-Bay's browser capabilities
- Uses natural language instructions to fill form fields
- Submits the form automatically

## Framework Integration Guides

This project is structured to support multiple agent frameworks. Please refer to the specific framework integration guide for detailed setup and usage instructions:

- [LangChain Integration Guide](./langchain/README.md) - Complete setup and usage instructions for LangChain framework

## Project Structure

This project follows a modular structure that separates core functionality from framework-specific integrations:

```
├── README.md            # Documentation
├── common/              # Public core functionality
│   └── src/             # Framework-agnostic code
│       └── __init__.py  # Python package initializer
└── langchain/           # LangChain integration
    ├── README.md        # LangChain integration documentation
    ├── requirements.txt # Python dependencies
    └── src/             # LangChain-specific code
        ├── __init__.py                # Python package initializer
        ├── browser_tools.py           # Browser automation tools
        ├── form_filling_agent.py      # Main form filling agent implementation
        └── form_filling_agent_example.py # Example usage script
```

### Common Module

The [common](./common/) directory is intended for all the core functionality that can be used across different agent frameworks.

### Framework Integration Modules

Framework-specific directories (like [langchain](./langchain/)) contain the integration code that implements form filling functionality using specific agent frameworks.

## Customization

You can customize the form filling behavior by modifying the implementation in the framework-specific directories and providing your own forms and instructions.

## Agent-Bay SDK Features Used

- Session management
- File system operations (uploading files)
- Browser initialization and control
- BrowserAgent for natural language web automation