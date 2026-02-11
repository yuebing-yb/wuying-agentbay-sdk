# 🤖 Agent API Reference

## Overview

The Agent module provides specialized functionality for the AgentBay cloud platform. It includes various methods and utilities to interact with cloud services and manage resources.

## 📚 Tutorial

[Agent Modules Guide](../../../../../docs/guides/common-features/advanced/agent-modules.md)

Learn about agent modules and custom agents

## Agent

An Agent to manipulate applications to complete specific tasks.

<p><strong>⚠️ Note</strong>: Currently, for agent services (including ComputerUseAgent, BrowserUseAgent, and MobileUseAgent), 
we do not provide services for overseas users registered with <strong>alibabacloud.com</strong>.</p>

### Constructor

```java
public Agent(Session session)
```

### Methods

### getComputer

```java
public Computer getComputer()
```

Get the Computer agent for desktop task execution.

**Returns:**
- `Computer`: Computer agent instance

### getBrowser

```java
public Browser getBrowser()
```

Get the Browser agent for browser task execution.

**Returns:**
- `Browser`: Browser agent instance

### getMobile

```java
public Mobile getMobile()
```

Get the Mobile agent for mobile device task execution.

**Returns:**
- `Mobile`: Mobile agent instance



## 🔗 Related Resources

- [Session API Reference](../../../api/common-features/basics/session.md)

