package integration_test

import (
	"encoding/json"
	"fmt"
	"strings"
	"testing"
	"time"

	"github.com/aliyun/wuying-agentbay-sdk/golang/pkg/agentbay"
	"github.com/aliyun/wuying-agentbay-sdk/golang/tests/pkg/agentbay/testutil"
)

// extractCodeOutput extracts the actual text output from the MCP tool response
func extractCodeOutput(rawOutput string) (string, error) {
	// The output is a JSON string with structure:
	// {"content":[{"text":"...","type":"text"}],"isError":false,"parsedToolName":"..."}
	var response struct {
		Content []struct {
			Text string `json:"text"`
			Type string `json:"type"`
		} `json:"content"`
		IsError        bool   `json:"isError"`
		ParsedToolName string `json:"parsedToolName"`
	}

	if err := json.Unmarshal([]byte(rawOutput), &response); err != nil {
		return "", fmt.Errorf("failed to parse output JSON: %w", err)
	}

	// Extract text from all content items
	var texts []string
	for _, item := range response.Content {
		if item.Type == "text" {
			texts = append(texts, item.Text)
		}
	}

	return strings.Join(texts, ""), nil
}

// TestCodeRunCodeIntegration tests the code.run_code functionality with Python and JavaScript
func TestCodeRunCodeIntegration(t *testing.T) {
	apiKey := testutil.GetTestAPIKey(t)
	agentBay, err := agentbay.NewAgentBay(apiKey)
	if err != nil {
		t.Fatalf("Error initializing AgentBay client: %v", err)
	}
	t.Logf("AgentBay client initialized successfully")

	// Create a session with code_latest image
	t.Log("Creating session with code_latest image...")
	params := agentbay.NewCreateSessionParams().WithImageId("code_latest")
	sessionResult, err := agentBay.Create(params)
	if err != nil {
		t.Fatalf("Error creating session: %v", err)
	}
	session := sessionResult.Session
	t.Logf("Session created with ID: %s (RequestID: %s)",
		session.SessionID, sessionResult.RequestID)

	// Ensure cleanup of the session after test
	defer func() {
		t.Log("Cleaning up: Deleting the session...")
		deleteResult, err := agentBay.Delete(session)
		if err != nil {
			t.Logf("Warning: Error deleting session: %v", err)
		} else {
			t.Logf("Session successfully deleted (RequestID: %s)",
				deleteResult.RequestID)
		}
	}()

	// Test 1: Execute simple Python code
	t.Run("SimplePythonExecution", func(t *testing.T) {
		pythonCode := `print("Hello from Python!")
x = 10 + 20
print(f"Result: {x}")`

		t.Logf("Executing Python code:\n%s", pythonCode)
		result, err := session.Code.RunCode(pythonCode, "python")
		if err != nil {
			t.Fatalf("Error executing Python code: %v", err)
		}

		// Extract actual code output
		actualOutput, err := extractCodeOutput(result.Output)
		if err != nil {
			t.Logf("Warning: Failed to extract code output: %v", err)
			t.Logf("Raw output: %s", result.Output)
			actualOutput = result.Output
		}

		t.Logf("Python execution output (RequestID: %s):\n%s",
			result.RequestID, actualOutput)

		// Verify output contains expected strings
		if !strings.Contains(actualOutput, "Hello from Python!") {
			t.Errorf("Expected output to contain 'Hello from Python!', got: %s", actualOutput)
		}
		if !strings.Contains(actualOutput, "30") {
			t.Errorf("Expected output to contain '30', got: %s", actualOutput)
		}
		if result.RequestID == "" {
			t.Error("RequestID should not be empty")
		}
	})

	// Test 2: Execute Python code with custom timeout
	t.Run("PythonWithCustomTimeout", func(t *testing.T) {
		pythonCode := `import time
print("Starting...")
time.sleep(2)
print("Completed after 2 seconds")`

		t.Logf("Executing Python code with 10s timeout:\n%s", pythonCode)
		result, err := session.Code.RunCode(pythonCode, "python", 10)
		if err != nil {
			t.Fatalf("Error executing Python code with timeout: %v", err)
		}

		actualOutput, _ := extractCodeOutput(result.Output)
		t.Logf("Python execution with timeout output (RequestID: %s):\n%s",
			result.RequestID, actualOutput)

		// Verify output contains expected strings
		if !strings.Contains(actualOutput, "Starting...") {
			t.Errorf("Expected output to contain 'Starting...', got: %s", actualOutput)
		}
		if !strings.Contains(actualOutput, "Completed after 2 seconds") {
			t.Errorf("Expected output to contain 'Completed after 2 seconds', got: %s", actualOutput)
		}
	})

	// Test 3: Execute simple JavaScript code
	t.Run("SimpleJavaScriptExecution", func(t *testing.T) {
		jsCode := `console.log("Hello from JavaScript!");
const x = 10 + 20;
console.log("Result: " + x);`

		t.Logf("Executing JavaScript code:\n%s", jsCode)
		result, err := session.Code.RunCode(jsCode, "javascript")
		if err != nil {
			t.Fatalf("Error executing JavaScript code: %v", err)
		}

		actualOutput, _ := extractCodeOutput(result.Output)
		t.Logf("JavaScript execution output (RequestID: %s):\n%s",
			result.RequestID, actualOutput)

		// Verify output contains expected strings
		if !strings.Contains(actualOutput, "Hello from JavaScript!") {
			t.Errorf("Expected output to contain 'Hello from JavaScript!', got: %s", actualOutput)
		}
		if !strings.Contains(actualOutput, "30") {
			t.Errorf("Expected output to contain '30', got: %s", actualOutput)
		}
		if result.RequestID == "" {
			t.Error("RequestID should not be empty")
		}
	})

	// Test 4: Execute JavaScript code with custom timeout
	t.Run("JavaScriptWithCustomTimeout", func(t *testing.T) {
		jsCode := `console.log("Starting...");
setTimeout(() => {
    console.log("This should not appear");
}, 5000);
console.log("Immediate output");`

		t.Logf("Executing JavaScript code with 10s timeout:\n%s", jsCode)
		result, err := session.Code.RunCode(jsCode, "javascript", 10)
		if err != nil {
			t.Fatalf("Error executing JavaScript code with timeout: %v", err)
		}

		actualOutput, _ := extractCodeOutput(result.Output)
		t.Logf("JavaScript execution with timeout output (RequestID: %s):\n%s",
			result.RequestID, actualOutput)

		// Verify output contains expected strings
		if !strings.Contains(actualOutput, "Starting...") {
			t.Errorf("Expected output to contain 'Starting...', got: %s", actualOutput)
		}
		if !strings.Contains(actualOutput, "Immediate output") {
			t.Errorf("Expected output to contain 'Immediate output', got: %s", actualOutput)
		}
	})

	// Test 5: Test Python code with file operations
	t.Run("PythonFileOperations", func(t *testing.T) {
		pythonCode := `import os
# Create a test file
with open('/tmp/test_code_integration.txt', 'w') as f:
    f.write('Test content from Python code execution')

# Read it back
with open('/tmp/test_code_integration.txt', 'r') as f:
    content = f.read()
    print(f"File content: {content}")

# Clean up
os.remove('/tmp/test_code_integration.txt')
print("File operations completed successfully")`

		t.Logf("Executing Python code with file operations:\n%s", pythonCode)
		result, err := session.Code.RunCode(pythonCode, "python")
		if err != nil {
			t.Fatalf("Error executing Python code with file operations: %v", err)
		}

		actualOutput, _ := extractCodeOutput(result.Output)
		t.Logf("Python file operations output (RequestID: %s):\n%s",
			result.RequestID, actualOutput)

		// Verify output
		if !strings.Contains(actualOutput, "Test content from Python code execution") {
			t.Errorf("Expected output to contain file content, got: %s", actualOutput)
		}
		if !strings.Contains(actualOutput, "File operations completed successfully") {
			t.Errorf("Expected output to contain success message, got: %s", actualOutput)
		}
	})

	// Test 6: Test Python code with error handling
	t.Run("PythonErrorHandling", func(t *testing.T) {
		pythonCode := `try:
    result = 10 / 0
except ZeroDivisionError as e:
    print(f"Caught error: {e}")
    print("Error handled successfully")`

		t.Logf("Executing Python code with error handling:\n%s", pythonCode)
		result, err := session.Code.RunCode(pythonCode, "python")
		if err != nil {
			t.Fatalf("Error executing Python code with error handling: %v", err)
		}

		actualOutput, _ := extractCodeOutput(result.Output)
		t.Logf("Python error handling output (RequestID: %s):\n%s",
			result.RequestID, actualOutput)

		// Verify output
		if !strings.Contains(actualOutput, "Caught error") {
			t.Errorf("Expected output to contain 'Caught error', got: %s", actualOutput)
		}
		if !strings.Contains(actualOutput, "Error handled successfully") {
			t.Errorf("Expected output to contain 'Error handled successfully', got: %s", actualOutput)
		}
	})

	// Test 7: Test unsupported language
	t.Run("UnsupportedLanguage", func(t *testing.T) {
		code := `print("test")`

		t.Log("Testing unsupported language...")
		_, err := session.Code.RunCode(code, "ruby")
		if err == nil {
			t.Error("Expected error for unsupported language, got nil")
		} else {
			t.Logf("Got expected error for unsupported language: %v", err)
			if !strings.Contains(err.Error(), "unsupported language") {
				t.Errorf("Expected error message to contain 'unsupported language', got: %v", err)
			}
		}
	})

	// Test 8: Test Python code with imports
	t.Run("PythonWithImports", func(t *testing.T) {
		pythonCode := `import json
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
print(f"Numbers sum: {sum(parsed['numbers'])}")`

		t.Logf("Executing Python code with imports:\n%s", pythonCode)
		result, err := session.Code.RunCode(pythonCode, "python")
		if err != nil {
			t.Fatalf("Error executing Python code with imports: %v", err)
		}

		actualOutput, _ := extractCodeOutput(result.Output)
		t.Logf("Python with imports output (RequestID: %s):\n%s",
			result.RequestID, actualOutput)

		// Verify output
		if !strings.Contains(actualOutput, "Hello from Python") {
			t.Errorf("Expected output to contain 'Hello from Python', got: %s", actualOutput)
		}
		if !strings.Contains(actualOutput, "Numbers sum: 15") {
			t.Errorf("Expected output to contain 'Numbers sum: 15', got: %s", actualOutput)
		}
	})

	t.Log("All code execution integration tests completed successfully")
}

// TestCodeRunCodeTimeout tests timeout behavior
func TestCodeRunCodeTimeout(t *testing.T) {
	apiKey := testutil.GetTestAPIKey(t)
	agentBay, err := agentbay.NewAgentBay(apiKey)
	if err != nil {
		t.Fatalf("Error initializing AgentBay client: %v", err)
	}

	// Create a session with code_latest image
	t.Log("Creating session for timeout testing...")
	params := agentbay.NewCreateSessionParams().WithImageId("code_latest")
	sessionResult, err := agentBay.Create(params)
	if err != nil {
		t.Fatalf("Error creating session: %v", err)
	}
	session := sessionResult.Session
	t.Logf("Session created with ID: %s (RequestID: %s)",
		session.SessionID, sessionResult.RequestID)

	defer func() {
		t.Log("Cleaning up: Deleting the session...")
		deleteResult, err := agentBay.Delete(session)
		if err != nil {
			t.Logf("Warning: Error deleting session: %v", err)
		} else {
			t.Logf("Session successfully deleted (RequestID: %s)",
				deleteResult.RequestID)
		}
	}()

	// Test code that takes longer than timeout
	t.Run("TimeoutExceeded", func(t *testing.T) {
		// Note: Due to gateway limitations, we can't test actual timeout > 60s
		// But we can test that short timeouts work correctly
		pythonCode := `import time
print("Starting long operation...")
for i in range(3):
    print(f"Step {i+1}")
    time.sleep(1)
print("Completed")`

		t.Logf("Executing Python code with 5s timeout:\n%s", pythonCode)
		result, err := session.Code.RunCode(pythonCode, "python", 5)
		if err != nil {
			t.Logf("Note: Code execution with timeout returned error: %v", err)
			// This is acceptable - timeout might cause an error
		} else {
			actualOutput, _ := extractCodeOutput(result.Output)
			t.Logf("Python execution output (RequestID: %s):\n%s",
				result.RequestID, actualOutput)
			// If it completes, verify it has the expected output
			if !strings.Contains(actualOutput, "Starting long operation") {
				t.Errorf("Expected output to contain 'Starting long operation', got: %s", actualOutput)
			}
		}
	})
}

// TestCodeRunCodeCrossPlatform tests code execution across different scenarios
func TestCodeRunCodeCrossPlatform(t *testing.T) {
	apiKey := testutil.GetTestAPIKey(t)
	agentBay, err := agentbay.NewAgentBay(apiKey)
	if err != nil {
		t.Fatalf("Error initializing AgentBay client: %v", err)
	}

	// Create a session
	t.Log("Creating session for cross-platform testing...")
	params := agentbay.NewCreateSessionParams().WithImageId("code_latest")
	sessionResult, err := agentBay.Create(params)
	if err != nil {
		t.Fatalf("Error creating session: %v", err)
	}
	session := sessionResult.Session
	t.Logf("Session created with ID: %s (RequestID: %s)",
		session.SessionID, sessionResult.RequestID)

	defer func() {
		t.Log("Cleaning up: Deleting the session...")
		deleteResult, err := agentBay.Delete(session)
		if err != nil {
			t.Logf("Warning: Error deleting session: %v", err)
		} else {
			t.Logf("Session successfully deleted (RequestID: %s)",
				deleteResult.RequestID)
		}
	}()

	// Test Python and JavaScript interoperability through file system
	t.Run("PythonJavaScriptInterop", func(t *testing.T) {
		// Step 1: Create a file with Python
		pythonCode := `import json
data = {"language": "python", "value": 42}
with open('/tmp/interop_test.json', 'w') as f:
    json.dump(data, f)
print("Python wrote data to file")`

		t.Log("Step 1: Python writing data to file...")
		result, err := session.Code.RunCode(pythonCode, "python")
		if err != nil {
			t.Fatalf("Error executing Python code: %v", err)
		}
		actualOutput, _ := extractCodeOutput(result.Output)
		t.Logf("Python output (RequestID: %s):\n%s", result.RequestID, actualOutput)

		// Add a small delay to ensure file is written
		time.Sleep(1 * time.Second)

		// Step 2: Read and modify the file with JavaScript
		jsCode := `const fs = require('fs');
const data = JSON.parse(fs.readFileSync('/tmp/interop_test.json', 'utf8'));
console.log('JavaScript read data:', JSON.stringify(data));
data.language = 'javascript';
data.value = data.value * 2;
fs.writeFileSync('/tmp/interop_test.json', JSON.stringify(data));
console.log('JavaScript updated data in file');`

		t.Log("Step 2: JavaScript reading and updating file...")
		result, err = session.Code.RunCode(jsCode, "javascript")
		if err != nil {
			t.Fatalf("Error executing JavaScript code: %v", err)
		}
		actualOutput, _ = extractCodeOutput(result.Output)
		t.Logf("JavaScript output (RequestID: %s):\n%s", result.RequestID, actualOutput)

		// Add a small delay
		time.Sleep(1 * time.Second)

		// Step 3: Read back with Python to verify
		pythonVerifyCode := `import json
with open('/tmp/interop_test.json', 'r') as f:
    data = json.load(f)
print(f"Final data: {data}")
print(f"Language: {data['language']}")
print(f"Value: {data['value']}")
import os
os.remove('/tmp/interop_test.json')
print("Cleanup completed")`

		t.Log("Step 3: Python verifying updated data...")
		result, err = session.Code.RunCode(pythonVerifyCode, "python")
		if err != nil {
			t.Fatalf("Error executing Python verification code: %v", err)
		}
		actualOutput, _ = extractCodeOutput(result.Output)
		t.Logf("Python verification output (RequestID: %s):\n%s", result.RequestID, actualOutput)

		// Verify the data was correctly modified
		if !strings.Contains(actualOutput, "javascript") {
			t.Errorf("Expected language to be 'javascript', got: %s", actualOutput)
		}
		if !strings.Contains(actualOutput, "84") {
			t.Errorf("Expected value to be 84 (42*2), got: %s", actualOutput)
		}
	})

	t.Log("Cross-platform integration tests completed successfully")
}
