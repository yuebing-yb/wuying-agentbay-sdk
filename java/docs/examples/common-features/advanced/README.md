# Common Features - Advanced Examples

This directory contains Java examples demonstrating advanced features of the AgentBay SDK.

## Examples

### 1. SessionMetricsExample.java
**Source**: [`../../../../agentbay/src/main/java/com/aliyun/agentbay/examples/SessionMetricsExample.java`](../../../../agentbay/src/main/java/com/aliyun/agentbay/examples/SessionMetricsExample.java)

Monitor session performance and usage metrics:
- Retrieving session metrics
- Analyzing resource usage
- Performance monitoring

**Key features demonstrated:**
```java
// Get session metrics
SessionMetrics metrics = session.getMetrics();
System.out.println("CPU Usage: " + metrics.getCpuUsage());
System.out.println("Memory Usage: " + metrics.getMemoryUsage());
System.out.println("Network I/O: " + metrics.getNetworkIO());
```

### 2. NetworkExample.java
**Source**: [`../../../../agentbay/src/main/java/com/aliyun/agentbay/examples/NetworkExample.java`](../../../../agentbay/src/main/java/com/aliyun/agentbay/examples/NetworkExample.java)

Network configuration and VPC integration:
- VPC session creation
- Network configuration
- Custom network settings

**Key features demonstrated:**
```java
CreateSessionParams params = new CreateSessionParams();
params.setIsVpc(true);
params.setPolicyId("vpc-policy-id");

SessionResult result = agentBay.create(params);
```

### 3. OSSManagementExample.java
**Source**: [`../../../../agentbay/src/main/java/com/aliyun/agentbay/examples/OSSManagementExample.java`](../../../../agentbay/src/main/java/com/aliyun/agentbay/examples/OSSManagementExample.java)

Alibaba Cloud OSS integration:
- Initializing OSS in session
- Uploading files to OSS
- Downloading files from OSS
- OSS bucket operations

**Key features demonstrated:**
```java
// Initialize OSS
session.getOss().init();

// Upload to OSS
session.getOss().upload("/local/path/file.txt", "bucket-name", "remote/key");

// Download from OSS
session.getOss().download("bucket-name", "remote/key", "/local/path/file.txt");
```

### 4. AgentExample.java
**Source**: [`../../../../agentbay/src/main/java/com/aliyun/agentbay/examples/AgentExample.java`](../../../../agentbay/src/main/java/com/aliyun/agentbay/examples/AgentExample.java)

Advanced agent automation patterns:
- Multi-step agent workflows
- Complex automation scenarios
- Agent orchestration

### 5. AliasMethodsExample.java
**Source**: [`../../../../agentbay/src/main/java/com/aliyun/agentbay/examples/AliasMethodsExample.java`](../../../../agentbay/src/main/java/com/aliyun/agentbay/examples/AliasMethodsExample.java)

Convenience methods and aliases:
- Shorthand method usage
- Alternative API patterns
- Simplified workflows

## Running the Examples

### Prerequisites

Set your API key:
```bash
export AGENTBAY_API_KEY=your_api_key_here
```

### Running from Maven

```bash
cd java/agentbay
mvn compile exec:java -Dexec.mainClass="com.aliyun.agentbay.examples.SessionMetricsExample"
mvn compile exec:java -Dexec.mainClass="com.aliyun.agentbay.examples.NetworkExample"
mvn compile exec:java -Dexec.mainClass="com.aliyun.agentbay.examples.OSSManagementExample"
```

## Advanced Patterns

### VPC Sessions
```java
CreateSessionParams params = new CreateSessionParams();
params.setIsVpc(true);
params.setPolicyId("your-vpc-policy-id");

SessionResult result = agentBay.create(params);
Session session = result.getSession();
```

### OSS Integration
```java
// Initialize OSS capability
session.getOss().init();

// Upload file
OssUploadResult uploadResult = session.getOss().upload(
    localPath,
    bucketName,
    objectKey
);

// Download file
OssDownloadResult downloadResult = session.getOss().download(
    bucketName,
    objectKey,
    localPath
);
```

### Session Metrics Monitoring
```java
// Get real-time metrics
SessionMetrics metrics = session.getMetrics();

// Monitor resource usage
System.out.println("CPU: " + metrics.getCpuUsage() + "%");
System.out.println("Memory: " + metrics.getMemoryUsage() + "MB");
System.out.println("Disk I/O: " + metrics.getDiskIO());
System.out.println("Network I/O: " + metrics.getNetworkIO());
```

## Related Documentation

- [OSS API](../../../api/common-features/advanced/oss.md)
- [Network API](../../../api/common-features/advanced/network.md)
- [Agent API](../../../api/common-features/advanced/agent.md)

## Troubleshooting

**VPC session creation fails:**
- Verify policy ID is correct
- Check VPC configuration
- Ensure VPC permissions are set

**OSS operations fail:**
- Initialize OSS with `session.getOss().init()` first
- Verify bucket permissions
- Check file paths and bucket names

**Metrics not available:**
- Ensure session is active
- Some metrics require time to populate
- Check session type supports metrics
