package agentbay_test

import (
	"fmt"
	"strings"
	"testing"

	"github.com/aliyun/wuying-agentbay-sdk/golang/pkg/agentbay"
)

func TestCommand_ExecuteCommand(t *testing.T) {
	// Initialize AgentBay client
	apiKey := getTestAPIKey(t)
	agentBay, err := agentbay.NewAgentBay(apiKey)
	if err != nil {
		t.Fatalf("Error initializing AgentBay client: %v", err)
	}

	// Create a session
	fmt.Println("Creating a new session for command testing...")
	session, err := agentBay.Create(nil)
	if err != nil {
		t.Fatalf("Error creating session: %v", err)
	}
	t.Logf("Session created with ID: %s", session.SessionID)

	// IMPORTANT: Ensure cleanup of the session after test
	defer func() {
		fmt.Println("Cleaning up: Deleting the session...")
		err := agentBay.Delete(session)
		if err != nil {
			t.Logf("Warning: Error deleting session: %v", err)
		} else {
			t.Log("Session successfully deleted")
		}
	}()

	// Test Command execution
	if session.Command != nil {
		// Test with echo command (works on all platforms)
		fmt.Println("Executing echo command...")
		testString := "AgentBay SDK Test"
		echoCmd := fmt.Sprintf("echo '%s'", testString)

		// Test with default timeout
		response, err := session.Command.ExecuteCommand(echoCmd)
		if err != nil {
			t.Logf("Note: Echo command failed: %v", err)
		} else {
			t.Logf("Echo command result: %s", response)

			// Check if response contains "tool not found"
			if containsToolNotFound(response) {
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
		responseWithTimeout, err := session.Command.ExecuteCommand(echoCmd, customTimeout)
		if err != nil {
			t.Logf("Note: Echo command with custom timeout failed: %v", err)
		} else {
			t.Logf("Echo command with custom timeout result: %s", responseWithTimeout)

			// Check if response contains "tool not found"
			if containsToolNotFound(responseWithTimeout) {
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

func TestCommand_RunCode(t *testing.T) {
	// Initialize AgentBay client
	apiKey := getTestAPIKey(t)
	agentBay, err := agentbay.NewAgentBay(apiKey)
	if err != nil {
		t.Fatalf("Error initializing AgentBay client: %v", err)
	}

	// Create a session
	fmt.Println("Creating a new session for run_code testing...")
	session, err := agentBay.Create(nil)
	if err != nil {
		t.Fatalf("Error creating session: %v", err)
	}
	t.Logf("Session created with ID: %s", session.SessionID)

	// IMPORTANT: Ensure cleanup of the session after test
	defer func() {
		fmt.Println("Cleaning up: Deleting the session...")
		err := agentBay.Delete(session)
		if err != nil {
			t.Logf("Warning: Error deleting session: %v", err)
		} else {
			t.Log("Session successfully deleted")
		}
	}()

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
		response, err := session.Command.RunCode(pythonCode, "python")
		if err != nil {
			t.Logf("Note: Python code execution failed: %v", err)
		} else {
			t.Logf("Python code execution result: %s", response)

			// Check if response contains "tool not found"
			if containsToolNotFound(response) {
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
		responseJs, err := session.Command.RunCode(jsCode, "javascript", customTimeout)
		if err != nil {
			t.Logf("Note: JavaScript code execution with custom timeout failed: %v", err)
		} else {
			t.Logf("JavaScript code execution with custom timeout result: %s", responseJs)

			// Check if response contains "tool not found"
			if containsToolNotFound(responseJs) {
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
