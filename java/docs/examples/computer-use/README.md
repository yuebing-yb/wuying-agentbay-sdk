# Computer Use Examples

This directory contains Java examples demonstrating Windows desktop automation capabilities of the AgentBay SDK.

## Examples

### 1. ComputerStartAppExample.java
**Source**: [`../../../agentbay/src/main/java/com/aliyun/agentbay/examples/ComputerStartAppExample.java`](../../../agentbay/src/main/java/com/aliyun/agentbay/examples/ComputerStartAppExample.java)

Windows desktop application management:
- Starting desktop applications
- Stopping applications by PID
- Stopping applications by process name
- Listing visible applications
- Getting installed applications

**Key features demonstrated:**
```java
// Start an application
session.getComputer().startApp("notepad.exe");

// List visible applications
ListResult visibleApps = session.getComputer().listVisibleApps();
for (App app : visibleApps.getApps()) {
    System.out.println("App: " + app.getName() + " (PID: " + app.getPid() + ")");
}

// Stop by PID
session.getComputer().stopAppByPID(12345);

// Stop by process name
session.getComputer().stopAppByPName("notepad.exe");

// Get all installed apps
List<InstalledApp> installedApps = session.getComputer().getInstalledApps();
```

## Running the Examples

### Prerequisites

1. Set your API key:
```bash
export AGENTBAY_API_KEY=your_api_key_here
```

2. Use Windows image for session:
```java
CreateSessionParams params = new CreateSessionParams();
params.setImageId("windows_latest");  // Or specific Windows image
```

### Running from Maven

```bash
cd java/agentbay
mvn compile exec:java -Dexec.mainClass="com.aliyun.agentbay.examples.ComputerStartAppExample"
```

## Common Patterns

### Basic Computer Session
```java
// Create Windows session
CreateSessionParams params = new CreateSessionParams();
params.setImageId("windows_latest");

Session session = agentBay.create(params).getSession();

// Start application
session.getComputer().startApp("notepad.exe");
```

### Application Lifecycle Management
```java
// Start application
StartAppResult result = session.getComputer().startApp("calculator.exe");
if (result.isSuccess()) {
    int pid = result.getPid();
    System.out.println("Started app with PID: " + pid);

    // Do some work...

    // Stop by PID
    session.getComputer().stopAppByPID(pid);
}
```

### Listing Applications
```java
// Get visible (running) applications
ListResult visibleApps = session.getComputer().listVisibleApps();
System.out.println("Running applications:");
for (App app : visibleApps.getApps()) {
    System.out.println("  - " + app.getName() + " (PID: " + app.getPid() + ")");
}

// Get all installed applications
List<InstalledApp> installedApps = session.getComputer().getInstalledApps();
System.out.println("Installed applications:");
for (InstalledApp app : installedApps) {
    System.out.println("  - " + app.getName() + " (" + app.getVersion() + ")");
}
```

### Process Management
```java
// Stop application by process name
StopResult result = session.getComputer().stopAppByPName("notepad.exe");
if (result.isSuccess()) {
    System.out.println("Successfully stopped notepad.exe");
} else {
    System.err.println("Failed to stop: " + result.getMessage());
}

// Stop specific instance by PID
session.getComputer().stopAppByPID(12345);
```

### Application Discovery
```java
// Check if specific app is installed
List<InstalledApp> apps = session.getComputer().getInstalledApps();
boolean hasChrome = apps.stream()
    .anyMatch(app -> app.getName().contains("Chrome"));

if (hasChrome) {
    session.getComputer().startApp("chrome.exe");
}
```

## Supported Applications

The Computer API works with standard Windows applications:

- **Built-in Apps**: notepad.exe, calc.exe, mspaint.exe, etc.
- **Installed Apps**: chrome.exe, firefox.exe, vscode.exe, etc.
- **Custom Apps**: Any installed Windows application

## Error Handling

```java
try {
    StartAppResult result = session.getComputer().startApp("myapp.exe");

    if (result.isSuccess()) {
        System.out.println("App started with PID: " + result.getPid());
    } else {
        System.err.println("Failed to start app: " + result.getMessage());
    }
} catch (AgentBayException e) {
    System.err.println("Exception: " + e.getMessage());
}
```

## Best Practices

1. **Check application existence** before starting:
   ```java
   List<InstalledApp> apps = session.getComputer().getInstalledApps();
   boolean exists = apps.stream()
       .anyMatch(app -> app.getName().equalsIgnoreCase("myapp.exe"));

   if (exists) {
       session.getComputer().startApp("myapp.exe");
   }
   ```

2. **Clean up applications**:
   ```java
   try {
       StartAppResult result = session.getComputer().startApp("app.exe");
       int pid = result.getPid();

       // Use application...

   } finally {
       session.getComputer().stopAppByPID(pid);
   }
   ```

3. **Handle process names carefully**:
   ```java
   // Use exact process name with extension
   session.getComputer().stopAppByPName("notepad.exe");  // Correct
   // Not: stopAppByPName("notepad")  // May not work
   ```

4. **Wait for application startup**:
   ```java
   session.getComputer().startApp("slowapp.exe");
   Thread.sleep(2000);  // Wait for app to fully start
   // Then interact with the app
   ```

## Related Documentation

- [Computer API](../api/computer-use/computer.md)
- [Desktop Automation Guide](../../../docs/guides/computer-use/desktop-automation.md)
- [Windows Session Guide](../../../docs/guides/computer-use/windows-sessions.md)

## Troubleshooting

**Application fails to start:**
- Verify application is installed
- Check application path and name are correct
- Ensure Windows image is being used
- Check for permission issues

**Cannot stop application:**
- Verify PID is correct and process exists
- Check process name includes .exe extension
- Ensure process is not protected by system

**List operations fail:**
- Check session is active and Windows-based
- Verify Computer API is available in image
- Ensure sufficient permissions

**Application not found:**
- Use `getInstalledApps()` to verify installation
- Check application name spelling
- Ensure application is in system PATH or use full path
