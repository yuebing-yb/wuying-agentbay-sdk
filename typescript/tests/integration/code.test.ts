import { AgentBay, Session } from "../../src";
import { getTestApiKey } from "../utils/test-helpers";
import { log, logError } from "../../src/utils/logger";

describe("Code Integration Test", () => {
  describe("runCode", () => {
    let agentBay: AgentBay;
    let session: Session;

    beforeEach(async () => {
      const apiKey = getTestApiKey();
      agentBay = new AgentBay({ apiKey });

      log("Creating a new session for code testing...");
      
      // Create session with code_latest image for code execution tests
      const createResponse = await agentBay.create({ imageId: "code_latest" });
      session = createResponse.session!;
      log(`Session created with ID: ${session.sessionId}`);
    });

    afterEach(async () => {
      if (session) {
        log(`Cleaning up session: ${session.sessionId}`);
        try {
          await session.delete();
        } catch (error) {
          logError("Failed to delete session:", error);
        }
      }
    });

    test("should execute Python code successfully", async () => {
      if (!session || !session.code) {
        log("Note: Code interface is nil, skipping code test");
        return;
      }

      const pythonCode = `
print("Hello, world!")
x = 1 + 1
print(x)
`;

      log("Executing Python code...");

      const runCodeResponse = await session.code.runCode(pythonCode, "python");

      log(`Python code execution output:`, runCodeResponse.result);
      log(`Run Code RequestId: ${runCodeResponse.requestId || "undefined"}`);

      expect(runCodeResponse.success).toBe(true);
      expect(runCodeResponse.requestId).toBeDefined();
      expect(typeof runCodeResponse.requestId).toBe("string");

      expect(runCodeResponse.result).toBeDefined();
      expect(runCodeResponse.result.includes("Hello, world!")).toBe(true);
      expect(runCodeResponse.result.includes("2")).toBe(true);
    }, 60000);

    test("should support code.run/code.execute aliases", async () => {
      if (!session || !session.code) {
        log("Note: Code interface is nil, skipping code alias test");
        return;
      }

      const pythonCode = `
print("Hello from alias")
`;

      const runRes = await session.code.run(pythonCode, "python");
      expect(runRes.success).toBe(true);
      expect(runRes.result).toContain("Hello from alias");

      const execRes = await session.code.execute(pythonCode, "python");
      expect(execRes.success).toBe(true);
      expect(execRes.result).toContain("Hello from alias");
    }, 60000);

    test("should execute JavaScript code successfully", async () => {
      if (!session || !session.code) {
        log("Note: Code interface is nil, skipping code test");
        return;
      }

      const jsCode = `
console.log("Hello, world!");
const x = 1 + 1;
console.log(x);
`;

      log("Executing JavaScript code...");

      const runCodeResponse = await session.code.runCode(jsCode, "javascript");

      log(`JavaScript code execution output:`, runCodeResponse.result);
      log(`Run Code RequestId: ${runCodeResponse.requestId || "undefined"}`);

      expect(runCodeResponse.success).toBe(true);
      expect(runCodeResponse.requestId).toBeDefined();
      expect(typeof runCodeResponse.requestId).toBe("string");

      expect(runCodeResponse.result).toBeDefined();
      expect(runCodeResponse.result.includes("Hello, world!")).toBe(true);
      expect(runCodeResponse.result.includes("2")).toBe(true);
    }, 60000);

    test("should support case-insensitive language input", async () => {
      if (!session || !session.code) {
        log("Note: Code interface is nil, skipping code test");
        return;
      }

      const pythonCode = `print("CASE_INSENSITIVE_OK")\n`;
      const runCodeResponse = await session.code.runCode(pythonCode, "PyThOn");

      expect(runCodeResponse.success).toBe(true);
      expect(runCodeResponse.result).toBeDefined();
      expect(runCodeResponse.result.includes("CASE_INSENSITIVE_OK")).toBe(true);
    }, 60000);

    test("should execute R code successfully", async () => {
      if (!session || !session.code) {
        log("Note: Code interface is nil, skipping code test");
        return;
      }

      const rCode = `
cat("Hello, R!\\n")
x <- 1 + 1
cat(x, "\\n")
`;

      const runCodeResponse = await session.code.runCode(rCode, "r");
      expect(runCodeResponse.success).toBe(true);
      expect(runCodeResponse.result).toBeDefined();
      expect(runCodeResponse.result.includes("Hello, R!")).toBe(true);
      expect(runCodeResponse.result.includes("2")).toBe(true);
    }, 60000);

    test("should execute Java code successfully", async () => {
      if (!session || !session.code) {
        log("Note: Code interface is nil, skipping code test");
        return;
      }

      const javaCode = `
System.out.println("Hello, Java!");
int x = 1 + 1;
System.out.println(x);
`;

      const runCodeResponse = await session.code.runCode(javaCode, "java");
      expect(runCodeResponse.success).toBe(true);
      expect(runCodeResponse.result).toBeDefined();
      expect(runCodeResponse.result.includes("Hello, Java!")).toBe(true);
      expect(runCodeResponse.result.includes("2")).toBe(true);
    }, 60000);

    test("should support R Jupyter-like context persistence", async () => {
      if (!session || !session.code) {
        log("Note: Code interface is nil, skipping code test");
        return;
      }

      const setup = `
x <- 41
cat("R_CONTEXT_SETUP_DONE\\n")
`;
      const setupRes = await session.code.runCode(setup, "R");
      expect(setupRes.success).toBe(true);
      expect(setupRes.result.includes("R_CONTEXT_SETUP_DONE")).toBe(true);

      const use = `cat(paste0("R_CONTEXT_VALUE:", x + 1, "\\n"))\n`;
      const useRes = await session.code.runCode(use, "r");
      expect(useRes.success).toBe(true);
      expect(useRes.result.includes("R_CONTEXT_VALUE:42")).toBe(true);
    }, 60000);

    test("should support Java Jupyter-like context persistence", async () => {
      if (!session || !session.code) {
        log("Note: Code interface is nil, skipping code test");
        return;
      }

      const setup = `
int x = 41;
System.out.println("JAVA_CONTEXT_SETUP_DONE");
`;
      const setupRes = await session.code.runCode(setup, "JAVA");
      expect(setupRes.success).toBe(true);
      expect(setupRes.result.includes("JAVA_CONTEXT_SETUP_DONE")).toBe(true);

      const use = `System.out.println("JAVA_CONTEXT_VALUE:" + (x + 1));\n`;
      const useRes = await session.code.runCode(use, "java");
      expect(useRes.success).toBe(true);
      expect(useRes.result.includes("JAVA_CONTEXT_VALUE:42")).toBe(true);
    }, 60000);

    test("should handle unsupported language", async () => {
      if (!session || !session.code) {
        log("Note: Code interface is nil, skipping code test");
        return;
      }

      log("Testing with unsupported language...");

      const response = await session.code.runCode('print("test")', "ruby");

      expect(response.success).toBe(false);
      expect(response.errorMessage).toBeDefined();
      expect(response.errorMessage).toContain("Unsupported language");
    }, 30000);

    test("should execute Python code with custom timeout", async () => {
      if (!session || !session.code) {
        log("Note: Code interface is nil, skipping code test");
        return;
      }

      const pythonCode = `
import time
print("Starting...")
time.sleep(2)
print("Completed after 2 seconds")
`;

      log("Executing Python code with timeout...");

      const runCodeResponse = await session.code.runCode(pythonCode, "python", 10);

      log(`Python code with timeout execution output:`, runCodeResponse.result);

      expect(runCodeResponse.success).toBe(true);
      expect(runCodeResponse.result).toBeDefined();
      expect(runCodeResponse.result.includes("Starting...")).toBe(true);
      expect(runCodeResponse.result.includes("Completed after 2 seconds")).toBe(true);
    }, 60000);

    test("should execute JavaScript code with custom timeout", async () => {
      if (!session || !session.code) {
        log("Note: Code interface is nil, skipping code test");
        return;
      }

      const jsCode = `
console.log("Starting...");
setTimeout(() => {
    console.log("This should not appear");
}, 5000);
console.log("Immediate output");
`;

      log("Executing JavaScript code with timeout...");

      const runCodeResponse = await session.code.runCode(jsCode, "javascript", 10);

      log(`JavaScript code with timeout execution output:`, runCodeResponse.result);

      expect(runCodeResponse.success).toBe(true);
      expect(runCodeResponse.result).toBeDefined();
      expect(runCodeResponse.result.includes("Starting...")).toBe(true);
      expect(runCodeResponse.result.includes("Immediate output")).toBe(true);
    }, 60000);

    test("should execute Python code with file operations", async () => {
      if (!session || !session.code) {
        log("Note: Code interface is nil, skipping code test");
        return;
      }

      const pythonCode = `
import os
# Create a test file
with open('/tmp/test_code_integration.txt', 'w') as f:
    f.write('Test content from Python code execution')

# Read it back
with open('/tmp/test_code_integration.txt', 'r') as f:
    content = f.read()
    print(f"File content: {content}")

# Clean up
os.remove('/tmp/test_code_integration.txt')
print("File operations completed successfully")
`;

      log("Executing Python code with file operations...");

      const runCodeResponse = await session.code.runCode(pythonCode, "python");

      log(`Python file operations output:`, runCodeResponse.result);

      expect(runCodeResponse.success).toBe(true);
      expect(runCodeResponse.result).toBeDefined();
      expect(runCodeResponse.result.includes("Test content from Python code execution")).toBe(true);
      expect(runCodeResponse.result.includes("File operations completed successfully")).toBe(true);
    }, 60000);

    test("should handle Python code with error handling", async () => {
      if (!session || !session.code) {
        log("Note: Code interface is nil, skipping code test");
        return;
      }

      const pythonCode = `
try:
    result = 10 / 0
except ZeroDivisionError as e:
    print(f"Caught error: {e}")
    print("Error handled successfully")
`;

      log("Executing Python code with error handling...");

      const runCodeResponse = await session.code.runCode(pythonCode, "python");

      log(`Python error handling output:`, runCodeResponse.result);

      expect(runCodeResponse.success).toBe(true);
      expect(runCodeResponse.result).toBeDefined();
      expect(runCodeResponse.result.includes("Caught error")).toBe(true);
      expect(runCodeResponse.result.includes("Error handled successfully")).toBe(true);
    }, 60000);

    test("should execute Python code with imports", async () => {
      if (!session || !session.code) {
        log("Note: Code interface is nil, skipping code test");
        return;
      }

      const pythonCode = `
import json
import datetime

data = {
    "message": "Hello from Python",
    "timestamp": str(datetime.datetime.now()),
    "numbers": [1, 2, 3, 4, 5]
}

json_str = json.dumps(data, indent=2)
print(json_str)

# Parse it back
parsed = json.loads(json_str)
print(f"Message: {parsed['message']}")
print(f"Numbers sum: {sum(parsed['numbers'])}")
`;

      log("Executing Python code with imports...");

      const runCodeResponse = await session.code.runCode(pythonCode, "python");

      log(`Python with imports output:`, runCodeResponse.result);

      expect(runCodeResponse.success).toBe(true);
      expect(runCodeResponse.result).toBeDefined();
      expect(runCodeResponse.result.includes("Hello from Python")).toBe(true);
      expect(runCodeResponse.result.includes("Numbers sum: 15")).toBe(true);
    }, 60000);

    test("should support cross-language interoperability", async () => {
      if (!session || !session.code) {
        log("Note: Code interface is nil, skipping code test");
        return;
      }

      // Step 1: Create a file with Python
      const pythonCode = `
import json
data = {"language": "python", "value": 42}
with open('/tmp/interop_test.json', 'w') as f:
    json.dump(data, f)
print("Python wrote data to file")
`;

      log("Step 1: Creating file with Python...");
      let runCodeResponse = await session.code.runCode(pythonCode, "python");
      expect(runCodeResponse.success).toBe(true);
      expect(runCodeResponse.result.includes("Python wrote data to file")).toBe(true);

      // Wait a bit
      await new Promise(resolve => setTimeout(resolve, 1000));

      // Step 2: Read and modify with JavaScript
      const jsCode = `
const fs = require('fs');
const data = JSON.parse(fs.readFileSync('/tmp/interop_test.json', 'utf8'));
console.log('JavaScript read data:', JSON.stringify(data));
data.language = 'javascript';
data.value = data.value * 2;
fs.writeFileSync('/tmp/interop_test.json', JSON.stringify(data));
console.log('JavaScript updated data in file');
`;

      log("Step 2: Modifying file with JavaScript...");
      runCodeResponse = await session.code.runCode(jsCode, "javascript");
      expect(runCodeResponse.success).toBe(true);
      expect(runCodeResponse.result.includes("JavaScript read data")).toBe(true);
      expect(runCodeResponse.result.includes("JavaScript updated data in file")).toBe(true);

      // Wait a bit
      await new Promise(resolve => setTimeout(resolve, 1000));

      // Step 3: Verify with Python
      const pythonVerifyCode = `
import json
with open('/tmp/interop_test.json', 'r') as f:
    data = json.load(f)
print(f"Final data: {data}")
print(f"Language: {data['language']}")
print(f"Value: {data['value']}")
import os
os.remove('/tmp/interop_test.json')
print("Cleanup completed")
`;

      log("Step 3: Verifying with Python...");
      runCodeResponse = await session.code.runCode(pythonVerifyCode, "python");
      expect(runCodeResponse.success).toBe(true);
      expect(runCodeResponse.result.includes("javascript")).toBe(true);
      expect(runCodeResponse.result.includes("84")).toBe(true);
      expect(runCodeResponse.result.includes("Cleanup completed")).toBe(true);
    }, 120000);
  });
}); 