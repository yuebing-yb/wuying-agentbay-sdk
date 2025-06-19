package agentbay_test

import (
	"fmt"
	"strings"
	"testing"

	"github.com/aliyun/wuying-agentbay-sdk/golang/pkg/agentbay"
	"github.com/aliyun/wuying-agentbay-sdk/golang/tests/pkg/agentbay/testutil"
)

func TestCommand_ExecuteCommand(t *testing.T) {
	// Create session parameters with ImageId set to code_latest
	params := agentbay.NewCreateSessionParams().WithImageId("code_latest")

	// Setup session with cleanup
	session, cleanup := testutil.SetupAndCleanup(t, params)
	defer cleanup()

	// Test Command execution
	if session.Command != nil {
		// Test with echo command (works on all platforms)
		fmt.Println("Executing echo command...")
		testString := "AgentBay SDK Test"
		echoCmd := fmt.Sprintf("echo '%s'", testString)

		// Test with default timeout
		rawResponse, err := session.Command.ExecuteCommand(echoCmd)
		if err != nil {
			t.Logf("Note: Echo command failed: %v", err)
		} else {
			// Extract text from raw response
			response := extractTextFromContent(rawResponse)
			t.Logf("Echo command result: %s", response)

			// Check if response contains "tool not found"
			if testutil.ContainsToolNotFound(response) {
				t.Errorf("Command.ExecuteCommand returned 'tool not found'")
			}

			// Verify the response contains the test string
			if !strings.Contains(response, testString) {
				t.Errorf("Echo command verification failed: expected '%s' in response, got '%s'", testString, response)
			} else {
				t.Logf("Echo command verified successfully")
			}
		}

		// Test with custom timeout
		fmt.Println("Executing echo command with custom timeout...")
		customTimeout := 2000 // 2 seconds
		rawResponseWithTimeout, err := session.Command.ExecuteCommand(echoCmd, customTimeout)
		if err != nil {
			t.Logf("Note: Echo command with custom timeout failed: %v", err)
		} else {
			// Extract text from raw response
			responseWithTimeout := extractTextFromContent(rawResponseWithTimeout)
			t.Logf("Echo command with custom timeout result: %s", responseWithTimeout)

			// Check if response contains "tool not found"
			if testutil.ContainsToolNotFound(responseWithTimeout) {
				t.Errorf("Command.ExecuteCommand with custom timeout returned 'tool not found'")
			}

			// Verify the response contains the test string
			if !strings.Contains(responseWithTimeout, testString) {
				t.Errorf("Echo command with custom timeout verification failed: expected '%s' in response, got '%s'", testString, responseWithTimeout)
			} else {
				t.Logf("Echo command with custom timeout verified successfully")
			}
		}
	} else {
		t.Logf("Note: Command interface is nil, skipping command test")
	}
}

// Helper function to extract text from content response
func extractTextFromContent(rawContent interface{}) string {
	contentArray, ok := rawContent.([]interface{})
	if !ok {
		return fmt.Sprintf("Failed to convert to []interface{}: %v", rawContent)
	}

	var result strings.Builder
	for _, item := range contentArray {
		contentItem, ok := item.(map[string]interface{})
		if !ok {
			continue
		}

		text, ok := contentItem["text"].(string)
		if !ok {
			continue
		}

		if result.Len() > 0 {
			result.WriteString("\n")
		}
		result.WriteString(text)
	}

	return result.String()
}

func TestCommand_RunCode(t *testing.T) {
	// Create session parameters with ImageId set to code_latest
	params := agentbay.NewCreateSessionParams().WithImageId("code_latest")

	// Setup session with cleanup
	session, cleanup := testutil.SetupAndCleanup(t, params)
	defer cleanup()

	// Test RunCode execution
	if session.Command != nil {
		// Test with Python code
		fmt.Println("Executing Python code...")
		pythonCode := `
print("Hello, world!")
x = 1 + 1
print(x)
`
		// Test with default timeout
		rawResponse, err := session.Command.RunCode(pythonCode, "python")
		if err != nil {
			t.Logf("Note: Python code execution failed: %v", err)
		} else {
			// Extract text from raw response
			response := extractTextFromContent(rawResponse)
			t.Logf("Python code execution result: %s", response)

			// Check if response contains "tool not found"
			if testutil.ContainsToolNotFound(response) {
				t.Errorf("Command.RunCode returned 'tool not found'")
			}

			// Verify the response contains expected output
			if !strings.Contains(response, "Hello, world!") || !strings.Contains(response, "2") {
				t.Errorf("Python code verification failed: expected 'Hello, world!' and '2' in response, got '%s'", response)
			} else {
				t.Logf("Python code execution verified successfully")
			}
		}

		// Test with JavaScript code and custom timeout
		fmt.Println("Executing JavaScript code with custom timeout...")
		jsCode := `
console.log("Hello, world!");
const x = 1 + 1;
console.log(x);
`
		customTimeout := 600 // 10 minutes
		rawResponseJs, err := session.Command.RunCode(jsCode, "javascript", customTimeout)
		if err != nil {
			t.Logf("Note: JavaScript code execution with custom timeout failed: %v", err)
		} else {
			// Extract text from raw response
			responseJs := extractTextFromContent(rawResponseJs)
			t.Logf("JavaScript code execution with custom timeout result: %s", responseJs)

			// Check if response contains "tool not found"
			if testutil.ContainsToolNotFound(responseJs) {
				t.Errorf("Command.RunCode with custom timeout returned 'tool not found'")
			}

			// Verify the response contains expected output
			if !strings.Contains(responseJs, "Hello, world!") || !strings.Contains(responseJs, "2") {
				t.Errorf("JavaScript code verification failed: expected 'Hello, world!' and '2' in response, got '%s'", responseJs)
			} else {
				t.Logf("JavaScript code execution verified successfully")
			}
		}

		// Test with invalid language
		fmt.Println("Testing with invalid language...")
		_, err = session.Command.RunCode("print('test')", "invalid_language")
		if err == nil {
			t.Errorf("Expected error for invalid language, but got nil")
		} else {
			t.Logf("Correctly received error for invalid language: %v", err)
		}
	} else {
		t.Logf("Note: Command interface is nil, skipping run_code test")
	}
}
