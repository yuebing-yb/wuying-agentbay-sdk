# 🚀 Agentbay API Reference

## Overview

The AgentBay class is the main entry point for the AgentBay Java SDK. It provides methods to create and manage cloud sessions, configure authentication, and access various cloud services.

## 📚 Tutorial

[First Session Tutorial](../../../../../docs/quickstart/first-session.md)

Get started with creating your first AgentBay session

## AgentBay

### Constructor

```java
public AgentBay() throws AgentBayException
```

```java
public AgentBay(String apiKey) throws AgentBayException
```

```java
public AgentBay(String apiKey, com.aliyun.agentbay.Config config) throws AgentBayException
```

### Methods

### get

```java
public SessionResult get(String sessionId) throws AgentBayException
```

Get a session by its ID from remote server.
This method calls the GetSession API to retrieve session information and creates a Session object.
This method fetches from the remote server, enabling session recovery scenarios.

**Parameters:**
- `sessionId` (String): The ID of the session to retrieve. Must be a non-empty string.

**Returns:**
- `SessionResult`: SessionResult containing the Session instance, request ID, and success status.

**Throws:**
- `AgentBayException`: if the API request fails

### getClient

```java
public Client getClient()
```

Get the underlying OpenAPI client

**Returns:**
- `Client`: Client instance

### getApiClient

```java
public ApiClient getApiClient()
```

Get the API client (internal use)

**Returns:**
- `ApiClient`: ApiClient instance

### getMobileSimulate

```java
public MobileSimulate getMobileSimulate()
```

Get mobile simulate service for this AgentBay instance

**Returns:**
- `MobileSimulate`: MobileSimulate instance

### getBetaNetwork

```java
public BetaNetworkService getBetaNetwork()
```

Get beta network service (trial feature).

**Returns:**
- `BetaNetworkService`: BetaNetworkService instance

### getBetaSkills

```java
public BetaSkillsService getBetaSkills()
```

Get beta skills service (trial feature).

**Returns:**
- `BetaSkillsService`: BetaSkillsService instance

### getApiKey

```java
public String getApiKey()
```

Get the API key

**Returns:**
- `String`: The API key

### getRegionId

```java
public String getRegionId()
```

Get the region ID

**Returns:**
- `String`: The region ID

### create

```java
public SessionResult create(CreateSessionParams params) throws AgentBayException
```

Create a new session with CreateSessionParams

**Parameters:**
- `params` (CreateSessionParams): Parameters for creating the session

**Returns:**
- `SessionResult`: SessionResult containing the created session information

**Throws:**
- `AgentBayException`: if the session creation fails

### getContextService

```java
public ContextService getContextService()
```

Get context service for this AgentBay instance

**Returns:**
- `ContextService`: ContextService instance

### getContext

```java
public ContextService getContext()
```

Get context service for this AgentBay instance (alias for getContextService)

**Returns:**
- `ContextService`: ContextService instance

### list

```java
public SessionListResult list(java.util.Map<String, String> labels, Integer page, Integer limit, String status)
```

```java
public SessionListResult list()
```

```java
public SessionListResult list(String status)
```

Returns paginated list of sessions filtered by labels.

**Parameters:**
- `labels` (java.util.Map<String,String>): Labels to filter sessions (optional)
- `page` (Integer): Page number for pagination starting from 1 (optional)
- `limit` (Integer): Maximum number of items per page (default: 10)
- `status` (String): Status to filter sessions: RUNNING, PAUSING, PAUSED, RESUMING, DELETING, DELETED (optional)

**Returns:**
- `SessionListResult`: SessionListResult containing paginated list of session information

### delete

```java
public DeleteResult delete(Session session, boolean syncContext)
```

Delete a session

**Parameters:**
- `session` (Session): The session to delete
- `syncContext` (boolean): Whether to sync context before deletion

**Returns:**
- `DeleteResult`: DeleteResult

### betaPause

```java
public SessionPauseResult betaPause(Session session, int timeout, double pollInterval) throws AgentBayException
```

```java
public SessionPauseResult betaPause(Session session) throws AgentBayException
```

Pause a session (beta feature), putting it into a dormant state.

This is a convenience method that delegates to the session's betaPause method.

**Parameters:**
- `session` (Session): The session to pause
- `timeout` (int): Maximum time to wait for pause completion in seconds (default: 600)
- `pollInterval` (double): Interval between status checks in seconds (default: 2.0)

**Returns:**
- `SessionPauseResult`: SessionPauseResult containing the pause operation result

**Throws:**
- `AgentBayException`: if the API call fails

### betaResume

```java
public SessionResumeResult betaResume(Session session, int timeout, double pollInterval) throws AgentBayException
```

```java
public SessionResumeResult betaResume(Session session) throws AgentBayException
```

Resume a paused session and wait until it enters RUNNING state (beta feature).

This is a convenience method that delegates to the session's betaResume method.

**Parameters:**
- `session` (Session): The session to resume
- `timeout` (int): Maximum time to wait for resume completion in seconds (default: 600)
- `pollInterval` (double): Interval between status checks in seconds (default: 2.0)

**Returns:**
- `SessionResumeResult`: SessionResumeResult containing the resume operation result

**Throws:**
- `AgentBayException`: if the API call fails



## Config

### Constructor

```java
public Config(String regionId, String endpoint, int timeoutMs)
```

```java
public Config(String regionId)
```

```java
public Config()
```

### Methods

### getRegionId

```java
public String getRegionId()
```

### setRegionId

```java
public void setRegionId(String regionId)
```

### getEndpoint

```java
public String getEndpoint()
```

### setEndpoint

```java
public void setEndpoint(String endpoint)
```

### getTimeoutMs

```java
public int getTimeoutMs()
```

### setTimeoutMs

```java
public void setTimeoutMs(int timeoutMs)
```



## 🔗 Related Resources

- [Session API Reference](../../../api/common-features/basics/session.md)
- [Context API Reference](../../../api/common-features/basics/context.md)

