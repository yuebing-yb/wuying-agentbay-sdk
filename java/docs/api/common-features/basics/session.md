# 🔧 Session API Reference

## Overview

The Session class represents an active cloud environment instance in AgentBay. It provides access to all service modules (filesystem, command, browser, code, etc.) and manages the lifecycle of the cloud environment.


## 📚 Tutorial

[Session Management Guide](../../../../../docs/guides/common-features/basics/session-management.md)

Detailed tutorial on session lifecycle and management

## Session

Represents a session in the AgentBay cloud environment

### Constructor

```java
public Session(String sessionId, AgentBay agentBay, SessionParams params)
```

```java
public Session(AgentBay agentBay, String sessionId)
```

Constructor compatible with Python SDK style (AgentBay, sessionId)

### Methods

### getSessionId

```java
public String getSessionId()
```

Get the session ID

**Returns:**
- `String`: Session ID

### getAgentBay

```java
public AgentBay getAgentBay()
```

Get the AgentBay client

**Returns:**
- `AgentBay`: AgentBay instance

### getParams

```java
public SessionParams getParams()
```

Get session parameters

**Returns:**
- `SessionParams`: SessionParams

### getAgent

```java
public Agent getAgent()
```

Get the agent for this session

**Returns:**
- `Agent`: Agent instance

### getFileSystem

```java
public FileSystem getFileSystem()
```

Get the file system for this session

**Returns:**
- `FileSystem`: FileSystem instance

### fs

```java
public FileSystem fs()
```

### getFilesystem

```java
public FileSystem getFilesystem()
```

### getFiles

```java
public FileSystem getFiles()
```

### callMcpTool

```java
public OperationResult callMcpTool(String toolName, Object args)
```

Call an MCP tool and return structured OperationResult (similar to Python's call_mcp_tool).
This is the preferred method for calling MCP tools as it provides unified routing logic
(LinkUrl, VPC, API) and consistent error handling.

**Parameters:**
- `toolName` (String): Tool name
- `args` (Object): Tool arguments

**Returns:**
- `OperationResult`: OperationResult containing parsed response with request ID, success status, and data

### listTools

```java
public List<Object> listTools() throws AgentBayException
```

List available tools

**Returns:**
- `List<Object>`: List of available tools

**Throws:**
- `AgentBayException`: if the call fails

### getMetrics

```java
public SessionMetricsResult getMetrics()
```

Get runtime metrics for this session via the MCP get_metrics tool.

The underlying MCP tool returns a JSON string. This method parses it and returns structured metrics.

**Returns:**
- `SessionMetricsResult`: SessionMetricsResult containing structured metrics data

### info

```java
public SessionInfoResult info() throws AgentBayException
```

Gets information about this session

**Returns:**
- `SessionInfoResult`: SessionInfoResult containing SessionInfo and request ID

**Throws:**
- `AgentBayException`: if the operation fails

### getOss

```java
public OSS getOss()
```

Get the OSS service for this session

**Returns:**
- `OSS`: OSS instance

### getCode

```java
public Code getCode()
```

Get the Code service for this session

**Returns:**
- `Code`: Code instance

### getCommand

```java
public Command getCommand()
```

Get the Command service for this session

**Returns:**
- `Command`: Command instance

### getContext

```java
public ContextManager getContext()
```

Get the context manager for this session

**Returns:**
- `ContextManager`: ContextManager instance

### getBrowser

```java
public Browser getBrowser()
```

Get the browser service for this session

**Returns:**
- `Browser`: Browser instance

### getComputer

```java
public Computer getComputer()
```

Get the computer service for this session

**Returns:**
- `Computer`: Computer instance

### getMobile

```java
public Mobile getMobile()
```

Get the mobile service for this session

**Returns:**
- `Mobile`: Mobile instance

### getFileTransferContextId

```java
public String getFileTransferContextId()
```

Get the file transfer context ID for this session

**Returns:**
- `String`: File transfer context ID

### setFileTransferContextId

```java
public void setFileTransferContextId(String fileTransferContextId)
```

Set the file transfer context ID for this session

**Parameters:**
- `fileTransferContextId` (String): File transfer context ID

### initializeBrowser

```java
public OperationResult initializeBrowser(BrowserOption option) throws AgentBayException
```

Initialize browser instance with the given options
This calls the AgentBay cloud service to create a browser instance

### getApiKey

```java
public String getApiKey()
```

Get the API key for this session

**Returns:**
- `String`: API key

### listMcpTools

```java
public McpToolsResult listMcpTools()
```

List MCP tools for this session

**Returns:**
- `McpToolsResult`: McpToolsResult

### setImageId

```java
public void setImageId(String imageId)
```

Set image ID for this session (placeholder method)

### getImageId

```java
public String getImageId()
```

### getEnableBrowserReplay

```java
public Boolean getEnableBrowserReplay()
```

Get enableBrowserReplay flag

### setEnableBrowserReplay

```java
public void setEnableBrowserReplay(Boolean enableBrowserReplay)
```

Set enableBrowserReplay flag

### getResourceUrl

```java
public String getResourceUrl()
```

Get the resource URL for accessing the session

**Returns:**
- `String`: Resource URL

### setResourceUrl

```java
public void setResourceUrl(String resourceUrl)
```

Set the resource URL for accessing the session

**Parameters:**
- `resourceUrl` (String): Resource URL

### getToken

```java
public String getToken()
```

Get the token for LinkUrl tool calls.

### setToken

```java
public void setToken(String token)
```

Set the token for LinkUrl tool calls.

### getLinkUrl

```java
public String getLinkUrl()
```

Get the LinkUrl for direct tool calls.

### setLinkUrl

```java
public void setLinkUrl(String linkUrl)
```

Set the LinkUrl for direct tool calls.

### updateMcpTools

```java
public void updateMcpTools(String dataJson)
```

Update MCP tools for this session

### getMcpTools

```java
public List<McpTool> getMcpTools()
```

### setMcpTools

```java
public void setMcpTools(List<McpTool> mcpTools)
```

### getMcpServerForTool

```java
public String getMcpServerForTool(String toolName)
```

### getLink

```java
public OperationResult getLink(String protocolType, Integer port) throws AgentBayException
```

```java
public OperationResult getLink() throws AgentBayException
```

Get a link associated with the current session

**Parameters:**
- `protocolType` (String): The protocol type to use for the link (optional)
- `port` (Integer): The port to use for the link (optional)

**Returns:**
- `OperationResult`: OperationResult containing the link URL

**Throws:**
- `AgentBayException`: if the request fails

### dumpState

```java
public String dumpState() throws AgentBayException
```

Dump session state to a JSON string for persistence

**Returns:**
- `String`: JSON string containing session state

**Throws:**
- `AgentBayException`: if serialization fails

### restoreState

```java
public static Session restoreState(AgentBay agentBay, String stateJson) throws AgentBayException
```

Restore session from a JSON state string

**Parameters:**
- `agentBay` (AgentBay): AgentBay client instance
- `stateJson` (String): JSON string containing session state

**Returns:**
- `Session`: Restored Session object

**Throws:**
- `AgentBayException`: if deserialization or restoration fails

### delete

```java
public com.aliyun.agentbay.model.DeleteResult delete()
```

```java
public com.aliyun.agentbay.model.DeleteResult delete(boolean syncContext)
```

Delete this session with optional sync context

**Parameters:**
- `syncContext` (boolean): Whether to sync context before deletion

**Returns:**
- `com.aliyun.agentbay.model.DeleteResult`: DeleteResult

### setLabels

```java
public OperationResult setLabels(Map<String, String> labels) throws AgentBayException
```

Set labels for this session

**Parameters:**
- `labels` (Map<String,String>): Map of label key-value pairs to set

**Returns:**
- `OperationResult`: OperationResult indicating success or failure

**Throws:**
- `AgentBayException`: if the API call fails

### getLabels

```java
public OperationResult getLabels() throws AgentBayException
```

Get labels for this session

**Returns:**
- `OperationResult`: OperationResult containing the labels map in the data field

**Throws:**
- `AgentBayException`: if the API call fails



## 🔗 Related Resources

- [FileSystem API Reference](/Users/liyuebing/Projects/wuying-agentbay-sdk/java/docs/api/common-features/basics/filesystem.md)
- [Command API Reference](/Users/liyuebing/Projects/wuying-agentbay-sdk/java/docs/api/common-features/basics/command.md)
- [Context API Reference](/Users/liyuebing/Projects/wuying-agentbay-sdk/java/docs/api/common-features/basics/context.md)
- [Context Manager API Reference](/Users/liyuebing/Projects/wuying-agentbay-sdk/java/docs/api/common-features/basics/context-manager.md)
- [OSS API Reference](/Users/liyuebing/Projects/wuying-agentbay-sdk/java/docs/api/common-features/advanced/oss.md)

