# 💾 Context API Reference

## Overview

The Context module provides specialized functionality for the AgentBay cloud platform. It includes various methods and utilities to interact with cloud services and manage resources.

## 📚 Tutorial

[Data Persistence Guide](../../../../../docs/guides/common-features/basics/data-persistence.md)

Learn about context management and data persistence

## Context

### Constructor

```java
public Context()
```

```java
public Context(String contextId, String name)
```

### Methods

### getDescription

```java
public String getDescription()
```

### setDescription

```java
public void setDescription(String description)
```

### getMetadata

```java
public Map<String, Object> getMetadata()
```

### setMetadata

```java
public void setMetadata(Map<String, Object> metadata)
```

### getCreatedAt

```java
public String getCreatedAt()
```

### setCreatedAt

```java
public void setCreatedAt(String createdAt)
```

### getUpdatedAt

```java
public String getUpdatedAt()
```

### setUpdatedAt

```java
public void setUpdatedAt(String updatedAt)
```

### getState

```java
public String getState()
```

### setState

```java
public void setState(String state)
```

### getOsType

```java
public String getOsType()
```

### setOsType

```java
public void setOsType(String osType)
```



## 🔗 Related Resources

- [Session API Reference](../../../api/common-features/basics/session.md)
- [Context Manager API Reference](../../../api/common-features/basics/context-manager.md)

