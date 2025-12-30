# Codespace Examples

This directory contains Java examples demonstrating code execution capabilities in AgentBay sessions.

## Examples

### 1. CodeExecutionExample.java
**Source**: [`../../../agentbay/src/main/java/com/aliyun/agentbay/examples/CodeExecutionExample.java`](../../../agentbay/src/main/java/com/aliyun/agentbay/examples/CodeExecutionExample.java)

Execute code in multiple programming languages:
- Python code execution
- JavaScript/Node.js execution
- Java code execution
- R code execution
- Shell script execution

**Key features demonstrated:**
```java
// Execute Python code
CodeResult result = session.getCode().runCode(
    "print('Hello from Python')\nresult = 2 + 2\nprint(result)",
    "python"
);
System.out.println(result.getOutput());

// Execute JavaScript
CodeResult jsResult = session.getCode().runCode(
    "console.log('Hello from Node.js');\nlet sum = 2 + 2;\nconsole.log(sum);",
    "javascript"
);

// Execute Java
String javaCode = """
    public class Main {
        public static void main(String[] args) {
            System.out.println("Hello from Java");
        }
    }
    """;
CodeResult javaResult = session.getCode().runCode(javaCode, "java");

// Execute R
CodeResult rResult = session.getCode().runCode(
    "print('Hello from R')\nresult <- 2 + 2\nprint(result)",
    "r"
);
```

## Running the Examples

### Prerequisites

1. Set your API key:
```bash
export AGENTBAY_API_KEY=your_api_key_here
```

2. Use an appropriate image (linux_latest supports most languages):
```java
CreateSessionParams params = new CreateSessionParams();
params.setImageId("linux_latest");
```

### Running from Maven

```bash
cd java/agentbay
mvn compile exec:java -Dexec.mainClass="com.aliyun.agentbay.examples.CodeExecutionExample"
```

## Supported Languages

| Language | Code Type | Example |
|----------|-----------|---------|
| Python | `"python"` | `session.getCode().runCode("print('Hello')", "python")` |
| JavaScript/Node.js | `"javascript"` or `"node"` | `session.getCode().runCode("console.log('Hello')", "javascript")` |
| Java | `"java"` | `session.getCode().runCode(javaCode, "java")` |
| R | `"r"` | `session.getCode().runCode("print('Hello')", "r")` |
| Shell/Bash | `"shell"` or `"bash"` | `session.getCode().runCode("echo 'Hello'", "shell")` |

## Common Patterns

### Basic Code Execution
```java
// Execute code with default timeout
CodeResult result = session.getCode().runCode(code, language);

if (result.isSuccess()) {
    System.out.println("Output: " + result.getOutput());
} else {
    System.err.println("Error: " + result.getError());
}
```

### Code Execution with Timeout
```java
// Execute with custom timeout (in seconds)
CodeResult result = session.getCode().runCode(
    code,
    language,
    30  // 30 second timeout
);
```

### Python with File I/O
```java
String pythonCode = """
    # Write to file
    with open('/tmp/data.txt', 'w') as f:
        f.write('Hello from Python')

    # Read from file
    with open('/tmp/data.txt', 'r') as f:
        content = f.read()
        print(content)
    """;

CodeResult result = session.getCode().runCode(pythonCode, "python");
```

### JavaScript with NPM Packages
```java
// First install package via command
session.getCommand().executeCommand("npm install lodash");

// Then use it in code
String jsCode = """
    const _ = require('lodash');
    const array = [1, 2, 3, 4, 5];
    const sum = _.sum(array);
    console.log('Sum:', sum);
    """;

CodeResult result = session.getCode().runCode(jsCode, "javascript");
```

### Multi-step Data Processing
```java
// Step 1: Generate data with Python
String pythonCode = """
    import json
    data = {'numbers': [1, 2, 3, 4, 5]}
    with open('/tmp/data.json', 'w') as f:
        json.dump(data, f)
    print('Data generated')
    """;
session.getCode().runCode(pythonCode, "python");

// Step 2: Process with JavaScript
String jsCode = """
    const fs = require('fs');
    const data = JSON.parse(fs.readFileSync('/tmp/data.json'));
    const sum = data.numbers.reduce((a, b) => a + b, 0);
    console.log('Sum:', sum);
    """;
session.getCode().runCode(jsCode, "javascript");
```

### Execute Method (Alternative API)
```java
// Alternative method with similar functionality
ExecuteResult result = session.getCode().execute(code, language);
System.out.println(result.getStdout());
System.err.println(result.getStderr());
```

## Error Handling

```java
try {
    CodeResult result = session.getCode().runCode(code, language, timeout);

    if (result.isSuccess()) {
        System.out.println("Success: " + result.getOutput());
    } else {
        System.err.println("Execution failed: " + result.getError());
        System.err.println("Exit code: " + result.getExitCode());
    }
} catch (AgentBayException e) {
    System.err.println("Exception: " + e.getMessage());
}
```

## Best Practices

1. **Always set timeout** for long-running code:
   ```java
   session.getCode().runCode(code, language, 60); // 60 second timeout
   ```

2. **Use file system** for data exchange between executions:
   ```java
   // Write results to /tmp/ for persistence
   session.getCode().runCode("with open('/tmp/result.txt', 'w') as f: f.write(str(result))", "python");
   ```

3. **Check execution result**:
   ```java
   if (result.isSuccess()) {
       // Process output
   } else {
       // Handle error
   }
   ```

4. **Install dependencies** first:
   ```java
   // Install Python packages
   session.getCommand().executeCommand("pip install pandas numpy");

   // Then use them
   session.getCode().runCode("import pandas as pd; print(pd.__version__)", "python");
   ```

## Related Documentation

- [Code API](../api/codespace/code.md)
- [Command API](../api/common-features/basics/command.md)
- [Code Execution Guide](../../../docs/guides/codespace/code-execution.md)

## Troubleshooting

**Code execution timeout:**
- Increase timeout parameter
- Optimize code for better performance
- Split into smaller chunks

**Module not found errors:**
- Install required packages first using Command API
- Check package is available in the image
- Use virtual environments if needed

**Permission errors:**
- Use /tmp/ directory for file operations
- Check file paths are correct
- Ensure sufficient permissions

**Out of memory:**
- Reduce data size
- Process data in chunks
- Use more efficient algorithms
